import pytest
from datetime import datetime
from app.models.user import User
from app.models.ecg_analysis import ECGAnalysis
from app.models.validation import Validation
from app.core.constants import UserRoles, ValidationStatus, ClinicalUrgency
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Factory functions para criar modelos de teste
def create_test_user(**kwargs):
    """Factory para criar usuário de teste com valores padrão"""
    defaults = {
        'id': 1,
        'email': 'test@example.com',
        'hashed_password': 'hashed_password',
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'is_active': True,
        'is_verified': True,
        'is_superuser': False,
        'role': UserRoles.VIEWER,
        'phone': '1234567890',
        'license_number': 'LIC123',
        'specialty': 'Cardiology',
        'institution': 'Test Hospital',
        'experience_years': 5
    }
    defaults.update(kwargs)
    return User(**defaults)

def create_test_ecg_analysis(**kwargs):
    """Factory para criar análise ECG de teste"""
    defaults = {
        'id': 1,
        'created_by': 1,
        'patient_id': 1,
        'status': 'completed',
        'clinical_urgency': ClinicalUrgency.ROUTINE,
        'ai_diagnosis': 'Normal',
        'confidence_score': 0.95
    }
    defaults.update(kwargs)
    return ECGAnalysis(**defaults)

def create_test_validation(**kwargs):
    """Factory para criar validação de teste"""
    defaults = {
        'id': 1,
        'analysis_id': 1,
        'validator_id': 1,
        'status': ValidationStatus.PENDING,
        'follow_up_required': False,
        'requires_second_opinion': False
    }
    defaults.update(kwargs)
    return Validation(**defaults)

# Configuração global para testes
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


