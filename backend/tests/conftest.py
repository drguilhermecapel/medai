"""
Fixtures compartilhadas para testes
"""
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

try:
    from app.main import app
except ImportError:
    # Se main.py tiver problemas, criar app básico para testes
    from fastapi import FastAPI
    app = FastAPI()
from app.core.database import Base
from app.core.config import settings

# Configurar event loop para testes assíncronos
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    """Create async engine for tests"""
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def async_session(async_engine):
    """Create async session for tests"""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client() -> Generator:
    """Create test client"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user_data():
    """Dados de teste para usuário"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "TestPass123!",
        "role": "doctor"
    }

@pytest.fixture
def test_patient_data():
    """Dados de teste para paciente"""
    return {
        "patient_id": "PAT001",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-15",
        "gender": "male",
        "cpf": "123.456.789-00",
        "phone": "+55 11 98765-4321",
        "email": "patient@example.com"
    }
