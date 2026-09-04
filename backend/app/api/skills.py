"""
Dedicated Skills API Endpoint.
Exposes specialized agent skills including the 'Ship 30 for 30' content engine.
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
from app.rag.retriever import retrieve_relevant_chunks
from app.skills.ship30 import build_ship30_prompt
from app.artifacts.parser import extract_artifacts
from app.providers.factory import get_provider
from app.logging_config import logger

router = APIRouter(prefix="/skills", tags=["Skills"])


class Ship30Request(BaseModel):
    topic: str
    session_id: Optional[str] = None
    provider: Optional[str] = None


@router.post("/ship30")
async def ship30_endpoint(
    payload: Ship30Request,
    request: Request,
    x_llm_provider: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes the Ship 30 for 30 content engine skill.
    Retrieves grounded context, generates a 1,250-word atomic essay,
    and returns it as a rendered side-by-side artifact.
    """
    topic = payload.topic.strip()
    session_id = payload.session_id
    chosen_provider = payload.provider or x_llm_provider or settings.DEFAULT_LLM_PROVIDER

    # Ensure session
    session = None
    if session_id:
        res = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session = res.scalar_one_or_none()

    if not session:
        session = SessionModel(title=f"Ship 30: {topic[:30]}")
        db.add(session)
        await db.commit()
        await db.refresh(session)
        session_id = session.id

    # Retrieve relevant knowledge
    retrieved_chunks = await retrieve_relevant_chunks(
        db,
        topic,
        top_k=6,
        threshold=0.25,  # Lower threshold slightly for rich essay synthesis
    )

    provider = get_provider(chosen_provider)

    async def event_generator():
        sources_payload = [
            {
                "episode_id": c["episode_id"],
                "guest": c["guest"],
                "title": c["title"],
                "timestamp": c["timestamp"],
                "score": c["score"],
                "snippet": c["content"][:200] + "...",
            }
            for c in retrieved_chunks
        ]

        yield {
            "event": "metadata",
            "data": json.dumps({
                "session_id": session_id,
                "skill": "ship30_content_engine",
                "provider": provider.provider_name,
                "sources_count": len(retrieved_chunks),
                "sources": sources_payload,
            }),
        }

        system_prompt = build_ship30_prompt(topic, retrieved_chunks)
        messages = [{"role": "user", "content": f"Write a complete Ship 30 for 30 essay on: {topic}"}]

        full_tokens = []
        try:
            async for token in provider.stream(messages, system_prompt=system_prompt, temperature=0.4):
                if await request.is_disconnected():
                    break
                full_tokens.append(token)
                yield {
                    "event": "token",
                    "data": json.dumps({"token": token}),
                }
        except Exception as e:
            logger.error(f"Error streaming Ship 30 essay: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

        complete_response = "".join(full_tokens)
        artifacts = extract_artifacts(complete_response)

        # If LLM didn't wrap in <artifact>, wrap whole essay automatically
        if not artifacts and len(complete_response) > 100:
            artifacts = [{
                "title": f"Ship 30 Essay: {topic[:40]}",
                "artifact_type": "markdown",
                "identifier": "ship30-essay",
                "content": complete_response,
            }]

        for art in artifacts:
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
                "artifacts_count": len(artifacts),
                "done": True,
            }),
        }

        # Persist
        factory = get_session_factory()
        async with factory() as save_db:
            u_msg = MessageModel(
                session_id=session_id,
                role="user",
                content=f"Generate Ship 30 for 30 essay: {topic}",
                sources=[],
            )
            a_msg = MessageModel(
                session_id=session_id,
                role="assistant",
                content=f"I have crafted a grounded Ship 30 for 30 atomic essay for you on **{topic}**. You can review, copy, or export it in the side-by-side artifact viewer.",
                sources=sources_payload,
            )
            save_db.add_all([u_msg, a_msg])
            await save_db.flush()

            for art in artifacts:
                art_model = ArtifactModel(
                    session_id=session_id,
                    message_id=a_msg.id,
                    artifact_type=art["artifact_type"],
                    title=art["title"],
                    identifier=art["identifier"],
                    content=art["content"],
                )
                save_db.add(art_model)
            await save_db.commit()

    return EventSourceResponse(event_generator())
