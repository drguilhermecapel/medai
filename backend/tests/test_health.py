"""
Basic health check tests for MedAI backend
"""

import pytest


def test_basic_import():
    """Test basic Python imports work"""
    import json
    import datetime
    assert json.dumps({"test": True}) == '{"test": true}'
    assert datetime.datetime.now() is not None


def test_basic_math():
    """Test basic mathematical operations"""
    assert 2 + 2 == 4
    assert 10 / 2 == 5.0


@pytest.mark.asyncio
async def test_async_function():
    """Test async function works"""
    async def async_add(a, b):
        return a + b
    
    result = await async_add(2, 3)
    assert result == 5


def test_sample_medical_data(sample_medical_data):
    """Test sample medical data fixture"""
    assert "symptoms" in sample_medical_data
    assert "vital_signs" in sample_medical_data
    assert len(sample_medical_data["symptoms"]) > 0


def test_mock_redis(mock_redis):
    """Test redis mock fixture"""
    assert mock_redis is not None
    assert hasattr(mock_redis, 'get')
    assert hasattr(mock_redis, 'set')


def test_mock_database(mock_database):
    """Test database mock fixture"""
    assert mock_database is not None
    assert hasattr(mock_database, 'commit')
    assert hasattr(mock_database, 'rollback')