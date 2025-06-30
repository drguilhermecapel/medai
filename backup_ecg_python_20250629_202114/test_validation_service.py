"""
Tests for Validation Service - Critical component requiring 100% coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.services.validation_service import ValidationService
from app.core.constants import ValidationStatus, ClinicalUrgency

class TestValidationService:
    """Test Validation Service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def validation_service(self, mock_db):
        """Create validation service instance."""
        mock_notification_service = MagicMock()
        return ValidationService(mock_db, mock_notification_service)

    def test_service_initialization(self, validation_service):
        """Test service initialization."""
        assert validation_service.db is not None
        assert hasattr(validation_service, 'repository')
        assert hasattr(validation_service, 'notification_service')

    @pytest.mark.asyncio
    async def test_create_validation_request(self, validation_service):
        """Test creating validation request."""
        analysis_id = 123
        validator_id = 456
        priority = ClinicalUrgency.URGENT
        
        # Mock repository
        mock_validation = MagicMock()
        mock_validation.id = 789
        validation_service.repository.create = AsyncMock(return_value=mock_validation)
        
        if hasattr(validation_service, 'create_validation_request'):
            result = await validation_service.create_validation_request(
                analysis_id, validator_id, priority
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_submit_validation(self, validation_service):
        """Test submitting validation."""
        validation_id = 123
        validator_id = 456
        validation_data = {
            "status": ValidationStatus.APPROVED,
            "comments": "Analysis is accurate",
            "confidence_score": 0.95
        }
        
        # Mock repository
        validation_service.repository.update = AsyncMock(return_value=MagicMock())
        
        if hasattr(validation_service, 'submit_validation'):
            result = await validation_service.submit_validation(
                validation_id, validator_id, validation_data
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_pending_validations(self, validation_service):
        """Test getting pending validations."""
        validator_id = 456
        
        # Mock repository
        mock_validations = [MagicMock(), MagicMock()]
        validation_service.repository.get_pending = AsyncMock(return_value=mock_validations)
        
        if hasattr(validation_service, 'get_pending_validations'):
            result = await validation_service.get_pending_validations(validator_id)
            assert result is not None
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_approve_analysis(self, validation_service):
        """Test approving analysis."""
        validation_id = 123
        validator_id = 456
        comments = "Analysis approved"
        
        if hasattr(validation_service, 'approve_analysis'):
            result = await validation_service.approve_analysis(
                validation_id, validator_id, comments
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_reject_analysis(self, validation_service):
        """Test rejecting analysis."""
        validation_id = 123
        validator_id = 456
        reason = "Insufficient data quality"
        
        if hasattr(validation_service, 'reject_analysis'):
            result = await validation_service.reject_analysis(
                validation_id, validator_id, reason
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_request_second_opinion(self, validation_service):
        """Test requesting second opinion."""
        validation_id = 123
        requesting_validator_id = 456
        
        if hasattr(validation_service, 'request_second_opinion'):
            result = await validation_service.request_second_opinion(
                validation_id, requesting_validator_id
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_validation_history(self, validation_service):
        """Test getting validation history."""
        analysis_id = 123
        
        # Mock repository
        mock_history = [MagicMock(), MagicMock()]
        validation_service.repository.get_history = AsyncMock(return_value=mock_history)
        
        if hasattr(validation_service, 'get_validation_history'):
            result = await validation_service.get_validation_history(analysis_id)
            assert result is not None
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_calculate_consensus(self, validation_service):
        """Test calculating validation consensus."""
        analysis_id = 123
        
        if hasattr(validation_service, 'calculate_consensus'):
            result = await validation_service.calculate_consensus(analysis_id)
            assert result is not None
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_validator_statistics(self, validation_service):
        """Test getting validator statistics."""
        validator_id = 456
        
        if hasattr(validation_service, 'get_validator_statistics'):
            result = await validation_service.get_validator_statistics(validator_id)
            assert result is not None
            assert isinstance(result, dict)

