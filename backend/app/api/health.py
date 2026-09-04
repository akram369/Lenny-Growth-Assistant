"""
Health Probe Endpoint.
Reports status of Database, pgvector, Ollama daemon, and model availability.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.db.models import TranscriptChunkModel, HAS_PGVECTOR
from app.providers.factory import get_all_providers_status, get_provider

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive system diagnostic probe."""
    db_status = "healthy"
    chunks_count = 0
    pgvector_active = False

    try:
        count_res = await db.execute(select(func.count(TranscriptChunkModel.id)))
        chunks_count = count_res.scalar_one_or_none() or 0

        bind = db.bind
        is_postgres = bind and "postgresql" in str(bind.url)
        if is_postgres and HAS_PGVECTOR:
            ext_res = await db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
            pgvector_active = ext_res.scalar_one_or_none() is not None
    except Exception as e:
        db_status = f"degraded ({str(e)})"

    # Check providers status
    providers = await get_all_providers_status()
    active_provider = get_provider()

    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database": {
            "status": db_status,
            "pgvector_enabled": pgvector_active,
            "indexed_chunks": chunks_count,
        },
        "llm": {
            "default_provider": settings.DEFAULT_LLM_PROVIDER,
            "active_model": active_provider.model_name,
            "providers": providers,
        },
        "embeddings": {
            "model": settings.EMBEDDING_MODEL_NAME,
            "dimension": settings.EMBEDDING_DIMENSION,
        },
    }
