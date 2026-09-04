"""
Unit Tests for Session Management and Persistence.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_session_lifecycle(async_client: AsyncClient):
    # 1. Create session
    create_res = await async_client.post("/api/sessions", json={"title": "Q3 Growth Planning"})
    assert create_res.status_code == 200
    created = create_res.json()
    session_id = created["id"]
    assert created["title"] == "Q3 Growth Planning"

    # 2. List sessions
    list_res = await async_client.get("/api/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert any(s["id"] == session_id for s in sessions)

    # 3. Get session details
    detail_res = await async_client.get(f"/api/sessions/{session_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == session_id
    assert isinstance(detail["messages"], list)
    assert isinstance(detail["artifacts"], list)

    # 4. Delete session
    del_res = await async_client.delete(f"/api/sessions/{session_id}")
    assert del_res.status_code == 200

    # Verify deletion
    verify_res = await async_client.get(f"/api/sessions/{session_id}")
    assert verify_res.status_code == 404
