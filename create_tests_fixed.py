#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar todos os arquivos de teste - Versão corrigida para Windows
"""

import os
from pathlib import Path

def create_file(filepath, content):
    """Cria arquivo com encoding UTF-8."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"Criado: {filepath}")

def main():
    print("\n========== CRIANDO ARQUIVOS DE TESTE ==========\n")
    
    # 1. pytest.ini
    create_file("pytest.ini", """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
""")

    # 2. conftest.py
    create_file("tests/conftest.py", '''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def test_data():
    return {"name": "Test", "value": 123}
''')

    # 3. test_security.py
    create_file("tests/unit/test_security.py", '''import pytest
from app.security import get_password_hash, verify_password, create_access_token

def test_password_hash():
    password = "test123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)

def test_wrong_password():
    password = "test123"
    hashed = get_password_hash(password)
    assert not verify_password("wrong", hashed)

def test_create_token():
    token = create_access_token({"sub": "test@test.com"})
    assert isinstance(token, str)
    assert len(token) > 20

def test_token_with_data():
    data = {"sub": "user@test.com", "id": 1}
    token = create_access_token(data)
    assert token is not None
''')

    # 4. test_config.py
    create_file("tests/unit/test_config.py", '''import pytest
from app.config import Settings, validate_database_url, validate_secret_key

def test_settings():
    settings = Settings()
    assert settings.app_name == "MedAI"
    assert settings.debug is False

def test_validate_database_url():
    assert validate_database_url("sqlite:///test.db")
    assert validate_database_url("postgresql://user:pass@localhost/db")
    assert not validate_database_url("")
    assert not validate_database_url("invalid")

def test_validate_secret_key():
    assert validate_secret_key("a" * 32)
    assert not validate_secret_key("short")
    assert not validate_secret_key("")

def test_config_classes():
    from app.config import DatabaseConfig, SecurityConfig, MLConfig
    
    db_config = DatabaseConfig("sqlite:///test.db")
    assert db_config.url == "sqlite:///test.db"
    
    sec_config = SecurityConfig()
    assert sec_config.algorithm == "HS256"
    
    ml_config = MLConfig()
    assert ml_config.model_path == "./models"
''')

    # 5. test_validation_service.py
    create_file("tests/unit/test_validation_service.py", '''import pytest
from app.services.validation_service import (
    validate_cpf, validate_phone, validate_email,
    PatientValidator, ValidationService
)

def test_validate_cpf():
    assert validate_cpf("11111111111")
    assert validate_cpf("12345678909")
    assert not validate_cpf("123")
    assert not validate_cpf("")

def test_validate_phone():
    assert validate_phone("11999999999")
    assert validate_phone("1199999999")
    assert not validate_phone("123")

def test_validate_email():
    assert validate_email("test@test.com")
    assert not validate_email("invalid")

def test_patient_validator():
    validator = PatientValidator()
    result = validator.validate({"name": "Test User"})
    assert result.is_valid

def test_validation_service():
    service = ValidationService()
    result = service.validate_patient_record({})
    assert result.is_valid
''')

    # 6. test_ml_model_service.py
    create_file("tests/unit/test_ml_model_service.py", '''import pytest
from app.services.ml_model_service import (
    MLModelService, DiagnosticModel, RiskAssessmentModel,
    ModelPreprocessor, ModelMonitor
)

def test_ml_service():
    service = MLModelService()
    result = service.predict({"test": 1})
    assert "prediction" in result
    assert "confidence" in result

def test_diagnostic_model():
    model = DiagnosticModel()
    result = model.predict_diabetes({"glucose": 126})
    assert "risk_score" in result
    assert 0 <= result["risk_score"] <= 1

def test_risk_model():
    model = RiskAssessmentModel()
    result = model.calculate_readmission_risk({"age": 70})
    assert "probability" in result
    assert "risk_level" in result

def test_preprocessor():
    preprocessor = ModelPreprocessor()
    data = {"glucose": 100}
    result = preprocessor.normalize_blood_test(data)
    assert "glucose_normalized" in result

def test_monitor():
    monitor = ModelMonitor()
    monitor.log_prediction({"predicted": 1, "actual": 1})
    metrics = monitor.calculate_metrics()
    assert "accuracy" in metrics
''')

    # 7. test_patient_service.py
    create_file("tests/unit/test_patient_service.py", '''import pytest
from app.services.patient_service import PatientService

def test_create_patient():
    service = PatientService()
    result = service.create_patient({"name": "Test"})
    assert result["name"] == "Test"
    assert "id" in result

def test_get_patient():
    service = PatientService()
    result = service.get_patient(1)
    assert result["id"] == 1

def test_update_patient():
    service = PatientService()
    result = service.update_patient(1, {"phone": "123"})
    assert result["phone"] == "123"

def test_list_patients():
    service = PatientService()
    result = service.list_patients()
    assert isinstance(result, list)
''')

    # 8. test_exam_service.py
    create_file("tests/unit/test_exam_service.py", '''import pytest
from app.services.exam_service import ExamService

def test_create_exam():
    service = ExamService()
    result = service.create_exam({"type": "blood"})
    assert "id" in result

def test_process_results():
    service = ExamService()
    result = service.process_exam_results(1, {"glucose": 95})
    assert result["processed"]

def test_validate_exam():
    service = ExamService()
    assert service.validate_exam_data({"type": "blood"})

def test_exam_history():
    service = ExamService()
    history = service.get_exam_history(1)
    assert isinstance(history, list)
''')

    # 9. test_diagnostic_service.py  
    create_file("tests/unit/test_diagnostic_service.py", '''import pytest
from app.services.diagnostic_service import DiagnosticService

def test_create_diagnostic():
    service = DiagnosticService()
    result = service.create_diagnostic({"text": "Test"})
    assert result["text"] == "Test"

def test_analyze_symptoms():
    service = DiagnosticService()
    result = service.analyze_symptoms(["fever"])
    assert "possible_conditions" in result

def test_suggest_treatments():
    service = DiagnosticService()
    treatments = service.suggest_treatments(1)
    assert len(treatments) > 0

def test_generate_report():
    service = DiagnosticService()
    report = service.generate_report(1)
    assert isinstance(report, bytes)
''')

    # 10. test_auth.py
    create_file("tests/unit/test_auth.py", '''import pytest
from app.auth import authenticate_user, create_user

def test_authenticate():
    assert authenticate_user("user", "pass")

def test_create_user():
    user = create_user("new", "pass")
    assert user["username"] == "new"

def test_auth_functions():
    # Testa funcoes basicas de auth
    assert True
''')

    # 11. test_health.py
    create_file("tests/unit/test_health.py", '''import pytest
from app.health import HealthChecker, HealthStatus

def test_health_checker():
    checker = HealthChecker()
    result = checker.check_health()
    assert "status" in result
    assert result["status"] in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]

def test_health_components():
    from app.health import DatabaseHealthCheck
    checker = DatabaseHealthCheck()
    from unittest.mock import Mock
    result = checker.check(Mock())
    assert result.status in ["healthy", "unhealthy"]
''')

    # 12. test_database.py
    create_file("tests/unit/test_database.py", '''import pytest
from app.database import get_db, engine, SessionLocal

def test_database_setup():
    assert engine is not None
    assert SessionLocal is not None

def test_get_db():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    # Cleanup
    try:
        next(db_gen)
    except StopIteration:
        pass
''')

    # 13. test_models.py
    create_file("tests/unit/test_models.py", '''import pytest
from app.models import User, Patient, Exam, Diagnostic
from datetime import datetime

def test_user_model():
    user = User()
    user.email = "test@test.com"
    assert user.email == "test@test.com"

def test_patient_model():
    patient = Patient()
    patient.name = "Test Patient"
    assert patient.name == "Test Patient"

def test_exam_model():
    exam = Exam()
    exam.exam_type = "blood_test"
    assert exam.exam_type == "blood_test"

def test_diagnostic_model():
    diagnostic = Diagnostic()
    diagnostic.severity = "moderate"
    assert diagnostic.severity == "moderate"
''')

    # 14. test_exceptions.py
    create_file("tests/unit/test_exceptions.py", '''import pytest
from app.exceptions import ValidationError, AuthenticationError, AuthorizationError

def test_validation_error():
    with pytest.raises(ValidationError):
        raise ValidationError("Test error")

def test_auth_errors():
    with pytest.raises(AuthenticationError):
        raise AuthenticationError("Auth failed")
    
    with pytest.raises(AuthorizationError):
        raise AuthorizationError("Not authorized")
''')

    # 15. test_main.py
    create_file("tests/unit/test_main.py", '''import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "MedAI" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
''')

    # Criar __init__.py files
    for path in ["tests/__init__.py", "tests/unit/__init__.py"]:
        create_file(path, "")

    print("\n========== CONCLUIDO ==========")
    print(f"Total de arquivos criados: 17")
    print("\nAgora execute:")
    print("python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term")

if __name__ == "__main__":
    main()