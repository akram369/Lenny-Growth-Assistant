"""
Session Management API Routes.
Provides CRUD endpoints for chat sessions, conversation history, and linked artifacts.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import SessionModel, MessageModel, ArtifactModel

router = APIRouter(prefix="/sessions", tags=["Sessions"])


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Growth Session"


class ArtifactResponse(BaseModel):
    id: str
    message_id: Optional[str] = None
    session_id: str
    artifact_type: str
    title: str
    identifier: str
    content: str
    created_at: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[list] = []
    created_at: str

    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[MessageResponse] = []
    artifacts: List[ArtifactResponse] = []

    class Config:
        from_attributes = True


class SessionSummaryResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

    class Config:
        from_attributes = True


@router.post("", response_model=SessionSummaryResponse)
async def create_session(
    payload: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Creates a fresh chat session."""
    session = SessionModel(title=payload.title or "New Growth Session")
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return SessionSummaryResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        message_count=0,
    )


@router.get("", response_model=List[SessionSummaryResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """Lists all chat sessions ordered by latest activity."""
    stmt = (
        select(SessionModel)
        .options(selectinload(SessionModel.messages))
        .order_by(desc(SessionModel.updated_at))
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    summaries = []
    for s in sessions:
        summaries.append(
            SessionSummaryResponse(
                id=s.id,
                title=s.title,
                created_at=s.created_at.isoformat(),
                updated_at=s.updated_at.isoformat(),
                message_count=len(s.messages),
            )
        )
    return summaries


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full conversation history and artifacts for a session."""
    stmt = (
        select(SessionModel)
        .options(
            selectinload(SessionModel.messages),
            selectinload(SessionModel.artifacts),
        )
        .where(SessionModel.id == session_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                sources=m.sources or [],
                created_at=m.created_at.isoformat(),
            )
            for m in session.messages
        ],
        artifacts=[
            ArtifactResponse(
                id=a.id,
                message_id=a.message_id,
                session_id=a.session_id,
                artifact_type=a.artifact_type,
                title=a.title,
                identifier=a.identifier,
                content=a.content,
                created_at=a.created_at.isoformat(),
            )
            for a in session.artifacts
        ],
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Deletes a chat session and all associated messages/artifacts."""
    stmt = select(SessionModel).where(SessionModel.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()
    return {"status": "success", "message": f"Session {session_id} deleted"}
