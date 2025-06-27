"""
Configuração simplificada para testes
"""
import pytest
import asyncio
import os

# Marcar como ambiente de teste
os.environ["TESTING"] = "1"

# Configuração básica do pytest
pytest_plugins = ['pytest_asyncio']

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Fixture básica para testes
@pytest.fixture
def test_client():
    """Create test client"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    return TestClient(app)
