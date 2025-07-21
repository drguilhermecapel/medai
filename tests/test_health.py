"""
Health check endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from medai.api.main import app

client = TestClient(app)


def test_health_check_sync():
    """Test health check endpoint synchronously."""
    response = client.get("/healthz")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "database" in data
    assert data["service"] == "MEDAI"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "version" in data
    assert "docs_url" in data
    assert "health_url" in data
    assert "MEDAI" in data["message"]


@pytest.mark.asyncio
async def test_health_check_async():
    """Test health check endpoint asynchronously."""
    from httpx import ASGITransport
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        response = await ac.get("/healthz")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "MEDAI"
    assert "status" in data