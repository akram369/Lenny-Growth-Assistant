"""
Database Engine, Session Factory, and Initialization.
Handles PostgreSQL connection with pgvector extension initialization and SQLite fallback.
"""

from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.logging_config import logger
from app.db.models import Base

# Engine and sessionmaker singletons
_engine = None
_session_factory = None
_is_sqlite = False


_current_db_url = None

def get_engine():
    global _engine, _session_factory, _is_sqlite, _current_db_url
    db_url = settings.DATABASE_URL
    if _engine is None or _current_db_url != db_url:
        _current_db_url = db_url
        if "sqlite" in db_url:
            _is_sqlite = True
            _engine = create_async_engine(db_url, echo=False)
        else:
            _is_sqlite = False
            _engine = create_async_engine(
                db_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                connect_args={"timeout": 2.0},
            )
        _session_factory = None
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> bool:
    """Initializes the database schema and pgvector extension."""
    global _engine, _session_factory, _is_sqlite
    engine = get_engine()

    try:
        async with engine.begin() as conn:
            if not _is_sqlite:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    logger.info("Successfully ensured pgvector extension is enabled.")
                except Exception as ext_err:
                    logger.warning(f"Could not enable pgvector extension (might already exist or permission issue): {ext_err}")

            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema initialized successfully.")
            return True
    except Exception as e:
        logger.error(f"Failed to connect or initialize primary database: {e}")
        # If PostgreSQL failed and we're not yet using SQLite, try SQLite fallback
        if not _is_sqlite and settings.SQLITE_FALLBACK_URL:
            logger.warning(f"Attempting fallback to SQLite: {settings.SQLITE_FALLBACK_URL}")
            _engine = create_async_engine(settings.SQLITE_FALLBACK_URL, echo=False)
            _session_factory = async_sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)
            _is_sqlite = True
            async with _engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Fallback SQLite database initialized.")
            return True
        return False
