"""
Configuração avançada do pytest para MedAI
Inclui fixtures, mocks e configurações especiais
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.database.session import Base
from app.models import User, Patient, MedicalRecord, Prescription
from app.services import AIDiagnosticService, MLModelService, ValidationService
from tests.smart_mocks import SmartAIMock, SmartMLMock, SmartValidationMock

# Configurações de teste
settings = get_settings()
settings.TESTING = True
settings.DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/medai_test"

# Engine de teste
test_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
)

# Session maker de teste
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para toda a sessão de testes"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Cria uma sessão de banco de dados para testes"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
        
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Cria um usuário de teste"""
    user = User(
        email="test@medai.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_patient(db_session: AsyncSession, test_user: User) -> Patient:
    """Cria um paciente de teste"""
    patient = Patient(
        name="João Silva",
        birth_date=datetime(1980, 1, 1),
        gender="M",
        cpf="12345678900",
        phone="11999999999",
        email="joao@example.com",
        medical_record_number="MED001",
        created_by_id=test_user.id,
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


@pytest.fixture
def sample_medical_data() -> dict:
    """Gera dados médicos de exemplo"""
    return {
        "symptoms": ["febre", "tosse", "dor de cabeça"],
        "duration_days": 3,
        "vital_signs": {
            "temperature": 38.5,
            "blood_pressure": "120/80",
            "heart_rate": 90,
            "respiratory_rate": 18,
            "oxygen_saturation": 96
        },
        "medical_history": ["hipertensão", "diabetes tipo 2"],
        "medications": ["metformina", "losartana"],
        "allergies": ["penicilina"],
        "lab_results": {
            "hemoglobin": 14.5,
            "leukocytes": 12000,
            "platelets": 250000,
            "glucose": 120,
            "creatinine": 1.1
        }
    }


@pytest.fixture
def ai_diagnostic_service(db_session: AsyncSession) -> AIDiagnosticService:
    """Cria instância do serviço AI com mocks inteligentes"""
    service = AIDiagnosticService(db_session)
    service._ai_engine = SmartAIMock()
    return service


@pytest.fixture
def ml_model_service(db_session: AsyncSession) -> MLModelService:
    """Cria instância do serviço ML com mocks inteligentes"""
    service = MLModelService(db_session)
    service._model_registry = SmartMLMock()
    return service


@pytest.fixture
def validation_service(db_session: AsyncSession) -> ValidationService:
    """Cria instância do serviço de validação com mocks inteligentes"""
    service = ValidationService(db_session)
    service._validator = SmartValidationMock()
    return service


@pytest.fixture
def mock_redis():
    """Mock do Redis para testes"""
    with patch("app.core.cache.redis_client") as mock:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=None)
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.delete = AsyncMock(return_value=True)
        mock_instance.exists = AsyncMock(return_value=False)
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_storage():
    """Mock do storage para testes"""
    with patch("app.core.storage.storage_client") as mock:
        mock_instance = Mock()
        mock_instance.upload_file = Mock(return_value="https://storage.medai.com/test.pdf")
        mock_instance.download_file = Mock(return_value=b"file_content")
        mock_instance.delete_file = Mock(return_value=True)
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Headers de autenticação para testes"""
    from app.core.security import create_access_token
    
    token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=None
    )
    return {"Authorization": f"Bearer {token}"}


# Marcadores personalizados
pytest.mark.critical = pytest.mark.critical
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow
pytest.mark.smoke = pytest.mark.smoke