"""
Pytest Test Fixtures and Test Environment Configuration.
Provides isolated test database, seed chunks, and async HTTP test client.
"""

import asyncio
import os
import sys
from pathlib import Path
import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure backend root is on sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

TEST_DB_URL = "sqlite+aiosqlite:///./test_lenny.db"

# Force test database URL into settings before loading app
from app.config import settings
settings.DATABASE_URL = TEST_DB_URL
settings.DEFAULT_LLM_PROVIDER = "ollama"

from app.main import app
from app.db.models import Base, TranscriptChunkModel
from app.db.session import get_db
from app.rag.embeddings import embed_text


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Seed sample chunks for retrieval tests
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        chunk1 = TranscriptChunkModel(
            episode_id="will-larson",
            guest="Will Larson",
            title="The engineering mindset",
            youtube_url="https://youtube.com/watch?v=will-larson",
            timestamp="00:00:00",
            chunk_index=0,
            content="I think that we often treat engineers a little bit like children instead of giving them the responsibilities and ability to actually thrive as adults. Leaders must treat engineers as adult peers.",
            embedding=embed_text("treat engineers like adult peers avoid coddling engineering mindset"),
        )
        chunk2 = TranscriptChunkModel(
            episode_id="elena-verna",
            guest="Elena Verna",
            title="B2B product-led sales",
            youtube_url="https://youtube.com/watch?v=elena-verna",
            timestamp="00:04:00",
            chunk_index=0,
            content="A Product-Qualified Lead (PQL) is someone who has reached the core aha moment in your product and demonstrated repeatable usage. PQLs convert at 3x to 5x the rate of MQLs.",
            embedding=embed_text("product qualified lead PQL convert aha moment freemium growth loop"),
        )
        session.add_all([chunk1, chunk2])
        await session.commit()

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if os.path.exists("./test_lenny.db"):
        try:
            os.remove("./test_lenny.db")
        except Exception:
            pass


@pytest_asyncio.fixture
async def db_session(test_engine):
    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(test_engine):
    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
