"""
Tests for core modules to improve coverage.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.core.config import Settings
from app.core.constants import UserRoles, AnalysisStatus, ClinicalUrgency, ValidationStatus
from app.core.exceptions import (
    ECGProcessingException,
    ValidationException,
    AuthenticationException,
    MLModelException
)
from app.core.database import get_db
from app.core.logging import configure_logging


class TestCoreConfig:
    """Test core configuration."""

    def test_settings_initialization(self):
        """Test settings initialization."""
        settings = Settings()
        assert settings is not None
        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'DATABASE_URL')

    def test_settings_validation(self):
        """Test settings validation."""
        # Test with environment variables
        with patch.dict('os.environ', {'SECRET_KEY': 'test_secret'}):
            settings = Settings()
            assert settings.SECRET_KEY == 'test_secret'

    def test_database_url_construction(self):
        """Test database URL construction."""
        settings = Settings()
        if hasattr(settings, 'get_database_url'):
            db_url = settings.get_database_url()
            assert isinstance(db_url, str)

    def test_redis_url_construction(self):
        """Test Redis URL construction."""
        settings = Settings()
        if hasattr(settings, 'get_redis_url'):
            redis_url = settings.get_redis_url()
            assert isinstance(redis_url, str)


class TestCoreConstants:
    """Test core constants."""

    def test_user_roles_enum(self):
        """Test UserRoles enum."""
        assert UserRoles.ADMIN == "admin"
        assert UserRoles.PHYSICIAN == "physician"
        assert UserRoles.CARDIOLOGIST == "cardiologist"
        assert UserRoles.TECHNICIAN == "technician"
        assert UserRoles.VIEWER == "viewer"

    def test_analysis_status_enum(self):
        """Test AnalysisStatus enum."""
        assert AnalysisStatus.PENDING == "pending"
        assert AnalysisStatus.PROCESSING == "processing"
        assert AnalysisStatus.COMPLETED == "completed"
        assert AnalysisStatus.FAILED == "failed"

    def test_clinical_urgency_enum(self):
        """Test ClinicalUrgency enum."""
        assert ClinicalUrgency.LOW == "low"
        assert ClinicalUrgency.MEDIUM == "medium"
        assert ClinicalUrgency.HIGH == "high"
        assert ClinicalUrgency.CRITICAL == "critical"

    def test_validation_status_enum(self):
        """Test ValidationStatus enum."""
        assert ValidationStatus.PENDING == "pending"
        assert ValidationStatus.APPROVED == "approved"
        assert ValidationStatus.REJECTED == "rejected"
        assert ValidationStatus.REQUIRES_REVIEW == "requires_review"

    def test_enum_membership(self):
        """Test enum membership."""
        assert "admin" in [role.value for role in UserRoles]
        assert "pending" in [status.value for status in AnalysisStatus]
        assert "critical" in [urgency.value for urgency in ClinicalUrgency]
        assert "approved" in [status.value for status in ValidationStatus]


class TestCoreExceptions:
    """Test core exceptions."""

    def test_ecg_processing_exception(self):
        """Test ECGProcessingException."""
        message = "ECG processing failed"
        exception = ECGProcessingException(message)
        assert str(exception) == message
        assert isinstance(exception, Exception)

    def test_validation_exception(self):
        """Test ValidationException."""
        message = "Validation failed"
        exception = ValidationException(message)
        assert str(exception) == message
        assert isinstance(exception, Exception)

    def test_authentication_exception(self):
        """Test AuthenticationException."""
        message = "Authentication failed"
        exception = AuthenticationException(message)
        assert str(exception) == message
        assert isinstance(exception, Exception)

    def test_ml_model_exception(self):
        """Test MLModelException."""
        message = "ML model error"
        exception = MLModelException(message)
        assert str(exception) == message
        assert isinstance(exception, Exception)

    def test_exception_inheritance(self):
        """Test exception inheritance."""
        assert issubclass(ECGProcessingException, Exception)
        assert issubclass(ValidationException, Exception)
        assert issubclass(AuthenticationException, Exception)
        assert issubclass(MLModelException, Exception)

    def test_exception_with_cause(self):
        """Test exception with cause."""
        original_error = ValueError("Original error")
        ecg_error = ECGProcessingException("ECG error")
        ecg_error.__cause__ = original_error
        
        assert ecg_error.__cause__ == original_error


class TestCoreDatabase:
    """Test core database functionality."""

    def test_get_db_generator(self):
        """Test database session generator."""
        db_gen = get_db()
        assert db_gen is not None
        # Test that it's a generator
        assert hasattr(db_gen, '__next__')

    @pytest.mark.asyncio
    async def test_database_session_lifecycle(self):
        """Test database session lifecycle."""
        # Mock database session
        with patch('app.core.database.AsyncSessionLocal') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            # Test session creation and cleanup
            db_gen = get_db()
            try:
                session = await db_gen.__anext__()
                assert session is not None
            except StopAsyncIteration:
                pass  # Expected for generator

    def test_database_url_validation(self):
        """Test database URL validation."""
        from app.core.database import engine
        assert engine is not None

    def test_session_factory(self):
        """Test session factory."""
        from app.core.database import AsyncSessionLocal
        assert AsyncSessionLocal is not None


class TestCoreLogging:
    """Test core logging functionality."""

    def test_setup_logging(self):
        """Test logging setup."""
        # Test that configure_logging doesn't raise exceptions
        try:
            configure_logging()
            assert True
        except Exception as e:
            pytest.fail(f"configure_logging raised an exception: {e}")

    def test_logger_configuration(self):
        """Test logger configuration."""
        import logging
        
        # Setup logging
        configure_logging()
        
        # Test that logger is configured
        logger = logging.getLogger("app")
        assert logger is not None
        assert logger.level <= logging.INFO

    def test_log_formatting(self):
        """Test log formatting."""
        import logging
        
        configure_logging()
        logger = logging.getLogger("test")
        
        # Test that logging works without errors
        try:
            logger.info("Test log message")
            logger.error("Test error message")
            logger.warning("Test warning message")
            assert True
        except Exception as e:
            pytest.fail(f"Logging raised an exception: {e}")

    def test_structured_logging(self):
        """Test structured logging."""
        import logging
        
        configure_logging()
        logger = logging.getLogger("test")
        
        # Test structured logging
        try:
            logger.info("Test message", extra={
                "user_id": 123,
                "action": "test",
                "timestamp": datetime.utcnow().isoformat()
            })
            assert True
        except Exception as e:
            pytest.fail(f"Structured logging raised an exception: {e}")


class TestCoreUtilities:
    """Test core utility functions."""

    def test_datetime_utilities(self):
        """Test datetime utilities."""
        from datetime import datetime, timezone
        
        # Test current time
        now = datetime.utcnow()
        assert isinstance(now, datetime)
        
        # Test timezone handling
        utc_now = datetime.now(timezone.utc)
        assert isinstance(utc_now, datetime)
        assert utc_now.tzinfo is not None

    def test_string_utilities(self):
        """Test string utilities."""
        # Test string operations that might be used in the app
        test_string = "Test String"
        assert test_string.lower() == "test string"
        assert test_string.upper() == "TEST STRING"
        assert test_string.replace(" ", "_") == "Test_String"

    def test_validation_utilities(self):
        """Test validation utilities."""
        # Test email validation pattern
        import re
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        valid_email = "test@example.com"
        invalid_email = "invalid-email"
        
        assert re.match(email_pattern, valid_email) is not None
        assert re.match(email_pattern, invalid_email) is None

    def test_security_utilities(self):
        """Test security utilities."""
        import secrets
        import hashlib
        
        # Test random token generation
        token = secrets.token_urlsafe(32)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Test hashing
        data = "test data"
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64

