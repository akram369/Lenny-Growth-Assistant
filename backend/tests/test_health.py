"""
Unit Tests for Health Probe Endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "online"
    assert "database" in data
    assert "llm" in data
    assert "embeddings" in data
    assert data["database"]["indexed_chunks"] >= 2


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "The Lenny Growth Assistant" in data["app"]
