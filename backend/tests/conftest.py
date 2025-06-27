"""
Configuração de fixtures e setup para testes do MedAI
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import redis
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Importações do projeto
from app.main import app
from app.database import Base, get_db, get_async_db
from app.models import User, Patient, ECGRecord, Diagnosis, Medication
from app.config import settings
from app.utils.security import create_access_token, hash_password

# Configurações de teste
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/medai_test"
TEST_ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/medai_test"
TEST_REDIS_URL = "redis://localhost:6379/1"

# Configuração pytest
pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def engine():
    """Cria engine do banco de dados para testes"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
async def async_engine():
    """Cria engine assíncrono do banco de dados"""
    engine = create_async_engine(TEST_ASYNC_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Cria sessão do banco de dados para cada teste"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
async def async_db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Cria sessão assíncrona do banco de dados"""
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="function")
def redis_client():
    """Cliente Redis para testes"""
    client = redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    client.flushdb()
    client.close()

@pytest.fixture(scope="function")
def client(db_session) -> TestClient:
    """Cliente de teste FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def async_client(async_db_session) -> AsyncGenerator[AsyncClient, None]:
    """Cliente assíncrono de teste"""
    async def override_get_async_db():
        yield async_db_session
    
    app.dependency_overrides[get_async_db] = override_get_async_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

# Fixtures de dados de teste

@pytest.fixture
def test_user(db_session) -> User:
    """Cria usuário de teste"""
    user = User(
        email="doctor@medai.com",
        username="dr_test",
        hashed_password=hash_password("Test@123"),
        full_name="Dr. Test User",
        role="doctor",
        specialty="cardiology",
        crm="12345-SP",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_patient(db_session, test_user) -> Patient:
    """Cria paciente de teste"""
    patient = Patient(
        name="João Silva",
        birth_date=datetime(1980, 5, 15),
        gender="M",
        cpf="12345678901",
        phone="11987654321",
        email="joao@email.com",
        address="Rua Teste, 123",
        blood_type="O+",
        allergies=["Penicilina"],
        medical_history={
            "conditions": ["Hipertensão"],
            "surgeries": [],
            "family_history": ["Diabetes"]
        },
        created_by_id=test_user.id
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient

@pytest.fixture
def test_ecg_data():
    """Dados de ECG de teste"""
    return {
        "data": [0.1, 0.2, 0.15, -0.1, -0.2, 0.0] * 1000,  # 6000 pontos
        "sampling_rate": 500,
        "leads": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        "duration": 12,  # segundos
        "metadata": {
            "device": "ECG-TEST-001",
            "recorded_at": datetime.utcnow().isoformat()
        }
    }

@pytest.fixture
def test_ecg_record(db_session, test_patient, test_user, test_ecg_data) -> ECGRecord:
    """Cria registro de ECG de teste"""
    ecg = ECGRecord(
        patient_id=test_patient.id,
        recorded_by_id=test_user.id,
        ecg_data=test_ecg_data,
        heart_rate=72,
        pr_interval=160,
        qrs_duration=90,
        qt_interval=400,
        qtc_interval=420,
        rhythm="Sinusal",
        interpretation="Normal",
        ai_analysis={
            "arrhythmia_detected": False,
            "confidence": 0.95,
            "features": {
                "p_wave": "normal",
                "qrs_complex": "normal",
                "t_wave": "normal"
            }
        }
    )
    db_session.add(ecg)
    db_session.commit()
    db_session.refresh(ecg)
    return ecg

@pytest.fixture
def auth_headers(test_user):
    """Headers de autenticação para testes"""
    token = create_access_token(
        data={"sub": test_user.email, "user_id": test_user.id}
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_ai_service():
    """Mock do serviço de IA"""
    mock = Mock()
    mock.analyze_ecg = AsyncMock(return_value={
        "arrhythmia_detected": False,
        "confidence": 0.95,
        "classification": "Normal Sinus Rhythm",
        "features": {
            "heart_rate_variability": "normal",
            "p_wave_morphology": "normal",
            "qrs_morphology": "normal",
            "st_segment": "normal",
            "t_wave": "normal"
        },
        "recommendations": []
    })
    
    mock.diagnose_symptoms = AsyncMock(return_value={
        "possible_conditions": [
            {"name": "Common Cold", "probability": 0.7, "icd10": "J00"},
            {"name": "Allergic Rhinitis", "probability": 0.2, "icd10": "J30.4"}
        ],
        "recommended_exams": ["Hemograma completo"],
        "urgency": "low",
        "confidence": 0.85
    })
    
    return mock

@pytest.fixture
def mock_medication_service():
    """Mock do serviço de medicamentos"""
    mock = Mock()
    mock.check_interactions = AsyncMock(return_value={
        "interactions": [],
        "warnings": [],
        "safe": True
    })
    
    mock.get_medication_info = AsyncMock(return_value={
        "name": "Paracetamol",
        "active_ingredient": "Acetaminophen",
        "dosage_forms": ["500mg", "750mg"],
        "contraindications": ["Hepatic impairment"],
        "side_effects": ["Nausea", "Rash"]
    })
    
    return mock

@pytest.fixture
def sample_lab_results():
    """Resultados de laboratório de exemplo"""
    return {
        "hemograma": {
            "hemoglobin": {"value": 14.5, "unit": "g/dL", "reference": "13.5-17.5"},
            "hematocrit": {"value": 42, "unit": "%", "reference": "41-53"},
            "leukocytes": {"value": 7500, "unit": "/mm³", "reference": "4500-11000"},
            "platelets": {"value": 250000, "unit": "/mm³", "reference": "150000-400000"}
        },
        "biochemistry": {
            "glucose": {"value": 95, "unit": "mg/dL", "reference": "70-100"},
            "creatinine": {"value": 1.0, "unit": "mg/dL", "reference": "0.7-1.3"},
            "urea": {"value": 35, "unit": "mg/dL", "reference": "15-40"}
        }
    }

@pytest.fixture
def load_test_data():
    """Carrega dados de teste de arquivos JSON"""
    def _load(filename: str):
        test_data_dir = Path(__file__).parent / "test_data"
        with open(test_data_dir / filename, 'r') as f:
            return json.load(f)
    return _load