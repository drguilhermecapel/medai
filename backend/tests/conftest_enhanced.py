"""
Configuração de Pytest para Testes Abrangentes
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
import numpy as np

# Configuração para testes assíncronos
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    """Mock database session for all tests."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_ml_service():
    """Mock ML service for all tests."""
    service = AsyncMock()
    service.classify_ecg.return_value = {
        "predictions": {"normal": 0.8, "arrhythmia": 0.2},
        "confidence": 0.85,
        "primary_diagnosis": "Normal Sinus Rhythm"
    }
    service.load_model.return_value = True
    return service


@pytest.fixture
def mock_validation_service():
    """Mock validation service for all tests."""
    service = AsyncMock()
    service.create_validation.return_value = Mock(id=1)
    return service


@pytest.fixture
def sample_ecg_data():
    """Generate sample ECG data for testing."""
    # 12-lead ECG, 10 seconds at 500 Hz
    return np.random.randn(5000, 12).astype(np.float32)


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "id": 123,
        "age": 65,
        "gender": "male",
        "medical_history": ["hypertension"],
        "medications": ["lisinopril"]
    }


# Configurações de cobertura
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "critical: mark test as critical for 100% coverage"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


# Configuração de cobertura específica
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Marcar testes críticos
        if "critical" in item.nodeid or "enhanced" in item.nodeid:
            item.add_marker(pytest.mark.critical)
        
        # Marcar testes de integração
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Marcar testes E2E
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)

