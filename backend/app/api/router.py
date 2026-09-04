"""
Root API Router.
Assembles all sub-routers under the /api prefix.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import TranscriptChunkModel
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.chat import router as chat_router
from app.api.skills import router as skills_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(sessions_router)
api_router.include_router(chat_router)
api_router.include_router(skills_router)


@api_router.get("/transcripts/stats", tags=["Transcripts"])
async def get_transcript_stats(db: AsyncSession = Depends(get_db)):
    """Returns total indexed episodes and chunk counts."""
    chunk_count_stmt = select(func.count(TranscriptChunkModel.id))
    episode_count_stmt = select(func.count(func.distinct(TranscriptChunkModel.episode_id)))

    chunks_res = await db.execute(chunk_count_stmt)
    episodes_res = await db.execute(episode_count_stmt)

    total_chunks = chunks_res.scalar_one_or_none() or 0
    total_episodes = episodes_res.scalar_one_or_none() or 0

    return {
        "total_episodes": total_episodes,
        "total_chunks": total_chunks,
        "status": "ready" if total_chunks > 0 else "unindexed",
    }
