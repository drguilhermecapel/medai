# tests/conftest.py
"""
Configuração global do pytest para o projeto MedAI.
Este arquivo contém fixtures e configurações que serão compartilhadas
entre todos os testes do sistema.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import asyncio

# Adiciona o diretório raiz ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.database import Base, get_db
from app.models import User, Patient, Exam, Diagnostic
from app.security import create_access_token, get_password_hash
from app.config import settings

# Configuração do banco de dados de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Cria uma sessão de banco de dados isolada para cada teste.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Cria um cliente de teste FastAPI com banco de dados isolado.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """
    Cria um usuário de teste padrão.
    """
    user = User(
        email="test@medai.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        role="doctor"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    """
    Gera headers de autenticação para requisições de teste.
    """
    access_token = create_access_token(
        data={"sub": test_user.email, "user_id": test_user.id}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_patient(db_session: Session, test_user: User) -> Patient:
    """
    Cria um paciente de teste com dados médicos realistas.
    """
    patient = Patient(
        name="João Silva",
        birth_date=datetime(1980, 5, 15),
        gender="M",
        cpf="12345678901",
        phone="11999999999",
        email="joao.silva@email.com",
        address="Rua Teste, 123",
        city="São Paulo",
        state="SP",
        medical_history={
            "chronic_conditions": ["Hipertensão", "Diabetes Tipo 2"],
            "allergies": ["Penicilina"],
            "medications": ["Metformina 850mg", "Losartana 50mg"],
            "family_history": {
                "diabetes": True,
                "heart_disease": True,
                "cancer": False
            }
        },
        created_by_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def test_exam(db_session: Session, test_patient: Patient, test_user: User) -> Exam:
    """
    Cria um exame de teste com resultados médicos.
    """
    exam = Exam(
        patient_id=test_patient.id,
        exam_type="blood_test",
        exam_date=datetime.utcnow(),
        results={
            "hemoglobin": 14.5,
            "hematocrit": 42.3,
            "glucose": 126,
            "cholesterol_total": 210,
            "cholesterol_hdl": 45,
            "cholesterol_ldl": 140,
            "triglycerides": 180,
            "creatinine": 1.1,
            "urea": 35,
            "ast": 28,
            "alt": 32
        },
        reference_values={
            "hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
            "glucose": {"min": 70, "max": 100, "unit": "mg/dL"},
            "cholesterol_total": {"max": 200, "unit": "mg/dL"}
        },
        status="completed",
        created_by_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(exam)
    db_session.commit()
    db_session.refresh(exam)
    return exam


@pytest.fixture
def test_diagnostic(db_session: Session, test_patient: Patient, test_exam: Exam, test_user: User) -> Diagnostic:
    """
    Cria um diagnóstico de teste com análise de IA.
    """
    diagnostic = Diagnostic(
        patient_id=test_patient.id,
        exam_id=test_exam.id,
        diagnostic_text="Paciente apresenta quadro de diabetes mellitus tipo 2 descompensada com dislipidemia mista.",
        ai_analysis={
            "confidence": 0.89,
            "risk_factors": [
                {"factor": "Glicemia elevada", "severity": "high", "value": 126},
                {"factor": "Colesterol LDL elevado", "severity": "medium", "value": 140},
                {"factor": "Triglicerídeos elevados", "severity": "medium", "value": 180}
            ],
            "recommendations": [
                "Ajuste da medicação antidiabética",
                "Introdução de estatina",
                "Orientação nutricional",
                "Atividade física regular"
            ],
            "icd10_codes": ["E11.9", "E78.5"],
            "follow_up": "30 dias"
        },
        severity="moderate",
        created_by_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(diagnostic)
    db_session.commit()
    db_session.refresh(diagnostic)
    return diagnostic


@pytest.fixture
def mock_ml_model():
    """
    Mock do modelo de ML para testes.
    """
    class MockMLModel:
        def predict(self, data):
            return {
                "prediction": "diabetes_risk_high",
                "confidence": 0.85,
                "risk_factors": ["glucose", "bmi", "family_history"],
                "recommendations": ["lifestyle_changes", "medical_followup"]
            }
        
        def analyze_exam(self, exam_data):
            return {
                "abnormal_values": ["glucose", "cholesterol_ldl"],
                "risk_assessment": "moderate",
                "suggested_actions": ["repeat_test", "specialist_consultation"]
            }
    
    return MockMLModel()


@pytest.fixture(scope="session")
def event_loop():
    """
    Cria um event loop para testes assíncronos.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Marcadores personalizados para categorizar testes
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes que demoram mais tempo"
    )
    config.addinivalue_line(
        "markers", "critical: marca testes de componentes críticos"
    )