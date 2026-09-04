"""
Conversational Chat Streaming API.
Handles RAG retrieval, dynamic LLM streaming, artifact extraction, and persistence over SSE.
"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.db.session import get_db, get_session_factory
from app.db.models import SessionModel, MessageModel, ArtifactModel
from app.rag.retriever import retrieve_relevant_chunks, format_context_for_prompt, REFUSAL_MESSAGE
from app.skills.grounded_qa import build_grounded_qa_prompt
from app.artifacts.parser import extract_artifacts, clean_text_for_chat
from app.providers.factory import get_provider
from app.logging_config import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    provider: Optional[str] = None


@router.post("")
async def chat_endpoint(
    payload: ChatRequest,
    request: Request,
    x_llm_provider: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Primary conversational endpoint.
    Performs vector similarity search against Lenny's transcripts,
    streams answers with citations, detects artifacts, and saves conversation turns.
    """
    user_query = payload.message.strip()
    session_id = payload.session_id
    chosen_provider_name = payload.provider or x_llm_provider or settings.DEFAULT_LLM_PROVIDER

    # Ensure session exists or create a new one
    session = None
    if session_id:
        stmt = select(SessionModel).where(SessionModel.id == session_id)
        res = await db.execute(stmt)
        session = res.scalar_one_or_none()

    if not session:
        # Generate initial title from first query
        first_title = (user_query[:40] + "...") if len(user_query) > 40 else user_query
        session = SessionModel(title=first_title)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        session_id = session.id

    # 1. Retrieve relevant transcript chunks
    retrieved_chunks = await retrieve_relevant_chunks(
        db,
        user_query,
        top_k=settings.RETRIEVAL_TOP_K,
        threshold=settings.RETRIEVAL_SIMILARITY_THRESHOLD,
    )

    # 2. Fetch recent conversation history for session
    history_stmt = (
        select(MessageModel)
        .where(MessageModel.session_id == session_id)
        .order_by(MessageModel.created_at.asc())
        .limit(10)
    )
    history_res = await db.execute(history_stmt)
    prev_messages = history_res.scalars().all()

    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in prev_messages
    ]
    conversation_history.append({"role": "user", "content": user_query})

    # Prepare provider instance
    provider = get_provider(chosen_provider_name)

    async def event_generator():
        # Step A: Send metadata event with sources and provider info
        sources_payload = [
            {
                "episode_id": c["episode_id"],
                "guest": c["guest"],
                "title": c["title"],
                "youtube_url": c["youtube_url"],
                "timestamp": c["timestamp"],
                "score": c["score"],
                "snippet": (c["content"][:220] + "...") if len(c["content"]) > 220 else c["content"],
            }
            for c in retrieved_chunks
        ]

        meta_data = {
            "session_id": session_id,
            "provider": provider.provider_name,
            "model": provider.model_name,
            "sources_count": len(retrieved_chunks),
            "sources": sources_payload,
        }
        yield {
            "event": "metadata",
            "data": json.dumps(meta_data),
        }

        # Step B: Check for out-of-domain refusal condition
        if not retrieved_chunks:
            refusal_response = REFUSAL_MESSAGE
            yield {
                "event": "token",
                "data": json.dumps({"token": refusal_response}),
            }
            yield {
                "event": "done",
                "data": json.dumps({"session_id": session_id, "done": True}),
            }

            # Persist turns in background session
            factory = get_session_factory()
            async with factory() as save_db:
                u_msg = MessageModel(session_id=session_id, role="user", content=user_query, sources=[])
                a_msg = MessageModel(session_id=session_id, role="assistant", content=refusal_response, sources=[])
                save_db.add_all([u_msg, a_msg])
                await save_db.commit()
            return

        # Step C: Formulate Grounded QA System Prompt
        context_str = format_context_for_prompt(retrieved_chunks)
        system_prompt = build_grounded_qa_prompt(context_str)

        # Step D: Stream tokens from active provider
        full_tokens = []
        try:
            async for token in provider.stream(conversation_history, system_prompt=system_prompt):
                if await request.is_disconnected():
                    logger.info("Client disconnected during chat stream.")
                    break
                full_tokens.append(token)
                yield {
                    "event": "token",
                    "data": json.dumps({"token": token}),
                }
        except Exception as stream_err:
            logger.error(f"Error during LLM token streaming: {stream_err}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(stream_err)}),
            }

        complete_response = "".join(full_tokens)

        # Step E: Parse artifacts if any were emitted
        detected_artifacts = extract_artifacts(complete_response)
        for art in detected_artifacts:
            yield {
                "event": "artifact",
                "data": json.dumps({
                    "session_id": session_id,
                    "title": art["title"],
                    "artifact_type": art["artifact_type"],
                    "identifier": art["identifier"],
                    "content": art["content"],
                }),
            }

        yield {
            "event": "done",
            "data": json.dumps({
                "session_id": session_id,
                "artifacts_count": len(detected_artifacts),
                "done": True,
            }),
        }

        # Step F: Persist messages and artifacts to database
        factory = get_session_factory()
        async with factory() as save_db:
            user_msg = MessageModel(
                session_id=session_id,
                role="user",
                content=user_query,
                sources=[],
            )
            assistant_msg = MessageModel(
                session_id=session_id,
                role="assistant",
                content=complete_response,
                sources=sources_payload,
            )
            save_db.add_all([user_msg, assistant_msg])
            await save_db.flush()

            for art in detected_artifacts:
                art_model = ArtifactModel(
                    session_id=session_id,
                    message_id=assistant_msg.id,
                    artifact_type=art["artifact_type"],
                    title=art["title"],
                    identifier=art["identifier"],
                    content=art["content"],
                )
                save_db.add(art_model)

            await save_db.commit()

    return EventSourceResponse(event_generator())
