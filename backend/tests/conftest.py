"""
Basic pytest configuration for MedAI
"""

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis():
    """Mock Redis for tests"""
    with patch("redis.asyncio.Redis") as mock:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=None)
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.delete = AsyncMock(return_value=True)
        mock_instance.exists = AsyncMock(return_value=False)
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_database():
    """Mock database session for tests"""
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.refresh = AsyncMock()
    return mock_session


@pytest.fixture
def sample_medical_data() -> dict:
    """Generate sample medical data"""
    return {
        "symptoms": ["fever", "cough", "headache"],
        "duration_days": 3,
        "vital_signs": {
            "temperature": 38.5,
            "blood_pressure": "120/80",
            "heart_rate": 90,
            "respiratory_rate": 18,
            "oxygen_saturation": 96
        },
        "medical_history": ["hypertension", "diabetes type 2"],
        "medications": ["metformin", "losartan"],
        "allergies": ["penicillin"],
        "lab_results": {
            "hemoglobin": 14.5,
            "leukocytes": 12000,
            "platelets": 250000,
            "glucose": 120,
            "creatinine": 1.1
        }
    }