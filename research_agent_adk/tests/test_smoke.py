import os
import asyncio
import pytest
from httpx import AsyncClient
from research_agent_adk.server import app


@pytest.mark.asyncio
async def test_health_ok():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_query_missing_env():
    # Ensure required env vars are not set for this test (simulate misconfig)
    os.environ.pop("PROJECT_ID", None)
    os.environ.pop("GOOGLE_API_KEY", None)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/query", json={"question": "test?", "max_sources": 3})
        # Should return 500 with helpful error when env missing
        assert resp.status_code == 500
        assert "required" in resp.json()["detail"]