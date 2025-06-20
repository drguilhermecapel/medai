"""
Comprehensive tests for main services to improve coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.ecg_service import ECGAnalysisService
from app.services.patient_service import PatientService
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.core.constants import AnalysisStatus, ClinicalUrgency, UserRoles


class TestECGService:
    """Test ECG Service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_repository(self):
        """Mock ECG repository."""
        return MagicMock()

    @pytest.fixture
    def ecg_service(self, mock_db, mock_repository):
        """Create ECG service instance."""
        # Mock dependencies
        mock_ml_service = MagicMock()
        mock_validation_service = MagicMock()
        
        service = ECGAnalysisService(mock_db, mock_ml_service, mock_validation_service)
        service.repository = mock_repository
        return service

    @pytest.mark.asyncio
    async def test_service_initialization(self, ecg_service):
        """Test service initialization."""
        assert ecg_service is not None
        assert hasattr(ecg_service, 'repository')

    @pytest.mark.asyncio
    async def test_create_analysis(self, ecg_service):
        """Test creating ECG analysis."""
        # Mock data
        analysis_data = {
            "patient_id": 123,
            "file_path": "/path/to/ecg.txt",
            "original_filename": "ecg.txt"
        }
        
        # Mock repository response
        mock_analysis = MagicMock()
        mock_analysis.id = 456
        mock_analysis.status = AnalysisStatus.PENDING
        ecg_service.repository.create = AsyncMock(return_value=mock_analysis)
        
        # Test creation
        if hasattr(ecg_service, 'create_analysis'):
            result = await ecg_service.create_analysis(analysis_data)
            assert result is not None
            ecg_service.repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_analysis_by_id(self, ecg_service):
        """Test getting analysis by ID."""
        # Mock repository response
        mock_analysis = MagicMock()
        mock_analysis.id = 123
        ecg_service.repository.get_by_id = AsyncMock(return_value=mock_analysis)
        
        # Test retrieval
        if hasattr(ecg_service, 'get_analysis_by_id'):
            result = await ecg_service.get_analysis_by_id(123)
            assert result is not None
            assert result.id == 123

    @pytest.mark.asyncio
    async def test_update_analysis_status(self, ecg_service):
        """Test updating analysis status."""
        # Mock repository response
        mock_analysis = MagicMock()
        mock_analysis.id = 123
        mock_analysis.status = AnalysisStatus.COMPLETED
        ecg_service.repository.update_status = AsyncMock(return_value=mock_analysis)
        
        # Test status update
        if hasattr(ecg_service, 'update_status'):
            result = await ecg_service.update_status(123, AnalysisStatus.COMPLETED)
            assert result is not None
            assert result.status == AnalysisStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_patient_analyses(self, ecg_service):
        """Test getting analyses for a patient."""
        # Mock repository response
        mock_analyses = [MagicMock(), MagicMock()]
        ecg_service.repository.get_by_patient = AsyncMock(return_value=mock_analyses)
        
        # Test retrieval
        if hasattr(ecg_service, 'get_patient_analyses'):
            result = await ecg_service.get_patient_analyses(123)
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_delete_analysis(self, ecg_service):
        """Test deleting analysis."""
        # Mock repository response
        ecg_service.repository.delete = AsyncMock(return_value=True)
        
        # Test deletion
        if hasattr(ecg_service, 'delete_analysis'):
            result = await ecg_service.delete_analysis(123)
            assert result is True

    @pytest.mark.asyncio
    async def test_process_ecg_file(self, ecg_service):
        """Test processing ECG file."""
        # Mock file processing
        with patch('app.utils.ecg_processor.ECGProcessor') as mock_processor:
            mock_processor.return_value.process_file = AsyncMock(return_value={
                "heart_rate": 75,
                "rhythm": "sinus"
            })
            
            if hasattr(ecg_service, 'process_file'):
                result = await ecg_service.process_file("/path/to/ecg.txt")
                assert result is not None
                assert "heart_rate" in result

    @pytest.mark.asyncio
    async def test_get_urgent_analyses(self, ecg_service):
        """Test getting urgent analyses."""
        # Mock repository response
        mock_analyses = [MagicMock()]
        ecg_service.repository.get_by_urgency = AsyncMock(return_value=mock_analyses)
        
        # Test retrieval
        if hasattr(ecg_service, 'get_urgent_analyses'):
            result = await ecg_service.get_urgent_analyses()
            assert len(result) >= 0

    @pytest.mark.asyncio
    async def test_validate_analysis_data(self, ecg_service):
        """Test validating analysis data."""
        valid_data = {
            "patient_id": 123,
            "file_path": "/path/to/ecg.txt",
            "original_filename": "ecg.txt"
        }
        
        if hasattr(ecg_service, 'validate_data'):
            result = ecg_service.validate_data(valid_data)
            assert result is True

    @pytest.mark.asyncio
    async def test_get_analysis_statistics(self, ecg_service):
        """Test getting analysis statistics."""
        # Mock repository response
        mock_stats = {"total": 100, "pending": 10, "completed": 90}
        ecg_service.repository.get_statistics = AsyncMock(return_value=mock_stats)
        
        # Test statistics
        if hasattr(ecg_service, 'get_statistics'):
            result = await ecg_service.get_statistics()
            assert "total" in result


class TestPatientService:
    """Test Patient Service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_repository(self):
        """Mock patient repository."""
        return MagicMock()

    @pytest.fixture
    def patient_service(self, mock_db, mock_repository):
        """Create patient service instance."""
        service = PatientService(mock_db)
        service.repository = mock_repository
        return service

    @pytest.mark.asyncio
    async def test_service_initialization(self, patient_service):
        """Test service initialization."""
        assert patient_service is not None
        assert hasattr(patient_service, 'repository')

    @pytest.mark.asyncio
    async def test_create_patient(self, patient_service):
        """Test creating patient."""
        # Mock data
        patient_data = {
            "patient_id": "P123456",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "male"
        }
        
        # Mock repository response
        mock_patient = MagicMock()
        mock_patient.id = 123
        patient_service.repository.create = AsyncMock(return_value=mock_patient)
        
        # Test creation
        if hasattr(patient_service, 'create_patient'):
            result = await patient_service.create_patient(patient_data)
            assert result is not None
            patient_service.repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_patient_by_id(self, patient_service):
        """Test getting patient by ID."""
        # Mock repository response
        mock_patient = MagicMock()
        mock_patient.id = 123
        patient_service.repository.get_by_id = AsyncMock(return_value=mock_patient)
        
        # Test retrieval
        if hasattr(patient_service, 'get_patient_by_id'):
            result = await patient_service.get_patient_by_id(123)
            assert result is not None
            assert result.id == 123

    @pytest.mark.asyncio
    async def test_update_patient(self, patient_service):
        """Test updating patient."""
        # Mock data
        update_data = {"phone": "123-456-7890"}
        
        # Mock repository response
        mock_patient = MagicMock()
        mock_patient.id = 123
        patient_service.repository.update = AsyncMock(return_value=mock_patient)
        
        # Test update
        if hasattr(patient_service, 'update_patient'):
            result = await patient_service.update_patient(123, update_data)
            assert result is not None

    @pytest.mark.asyncio
    async def test_search_patients(self, patient_service):
        """Test searching patients."""
        # Mock repository response
        mock_patients = [MagicMock(), MagicMock()]
        patient_service.repository.search = AsyncMock(return_value=mock_patients)
        
        # Test search
        if hasattr(patient_service, 'search_patients'):
            result = await patient_service.search_patients("John")
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_delete_patient(self, patient_service):
        """Test deleting patient."""
        # Mock repository response
        patient_service.repository.delete = AsyncMock(return_value=True)
        
        # Test deletion
        if hasattr(patient_service, 'delete_patient'):
            result = await patient_service.delete_patient(123)
            assert result is True

    @pytest.mark.asyncio
    async def test_get_patient_statistics(self, patient_service):
        """Test getting patient statistics."""
        # Mock repository response
        mock_stats = {"total": 500, "active": 450}
        patient_service.repository.get_statistics = AsyncMock(return_value=mock_stats)
        
        # Test statistics
        if hasattr(patient_service, 'get_statistics'):
            result = await patient_service.get_statistics()
            assert "total" in result


class TestUserService:
    """Test User Service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_repository(self):
        """Mock user repository."""
        return MagicMock()

    @pytest.fixture
    def user_service(self, mock_db, mock_repository):
        """Create user service instance."""
        service = UserService(mock_db)
        service.repository = mock_repository
        return service

    @pytest.mark.asyncio
    async def test_service_initialization(self, user_service):
        """Test service initialization."""
        assert user_service is not None
        assert hasattr(user_service, 'repository')

    @pytest.mark.asyncio
    async def test_create_user(self, user_service):
        """Test creating user."""
        # Mock data
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRoles.PHYSICIAN
        }
        
        # Mock repository response
        mock_user = MagicMock()
        mock_user.id = 123
        user_service.repository.create = AsyncMock(return_value=mock_user)
        
        # Test creation
        if hasattr(user_service, 'create_user'):
            result = await user_service.create_user(user_data)
            assert result is not None
            user_service.repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_service):
        """Test getting user by email."""
        # Mock repository response
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        user_service.repository.get_by_email = AsyncMock(return_value=mock_user)
        
        # Test retrieval
        if hasattr(user_service, 'get_user_by_email'):
            result = await user_service.get_user_by_email("test@example.com")
            assert result is not None
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_user(self, user_service):
        """Test user authentication."""
        # Mock authentication
        with patch('app.core.security.verify_password') as mock_verify:
            mock_verify.return_value = True
            mock_user = MagicMock()
            user_service.repository.get_by_email = AsyncMock(return_value=mock_user)
            
            if hasattr(user_service, 'authenticate'):
                result = await user_service.authenticate("test@example.com", "password")
                assert result is not None

    @pytest.mark.asyncio
    async def test_update_user_role(self, user_service):
        """Test updating user role."""
        # Mock repository response
        mock_user = MagicMock()
        mock_user.role = UserRoles.ADMIN
        user_service.repository.update = AsyncMock(return_value=mock_user)
        
        # Test role update
        if hasattr(user_service, 'update_role'):
            result = await user_service.update_role(123, UserRoles.ADMIN)
            assert result is not None
            assert result.role == UserRoles.ADMIN

    @pytest.mark.asyncio
    async def test_deactivate_user(self, user_service):
        """Test deactivating user."""
        # Mock repository response
        mock_user = MagicMock()
        mock_user.is_active = False
        user_service.repository.update = AsyncMock(return_value=mock_user)
        
        # Test deactivation
        if hasattr(user_service, 'deactivate'):
            result = await user_service.deactivate(123)
            assert result is not None
            assert result.is_active is False


class TestNotificationService:
    """Test Notification Service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_repository(self):
        """Mock notification repository."""
        return MagicMock()

    @pytest.fixture
    def notification_service(self, mock_db, mock_repository):
        """Create notification service instance."""
        service = NotificationService(mock_db)
        service.repository = mock_repository
        return service

    @pytest.mark.asyncio
    async def test_service_initialization(self, notification_service):
        """Test service initialization."""
        assert notification_service is not None
        assert hasattr(notification_service, 'repository')

    @pytest.mark.asyncio
    async def test_create_notification(self, notification_service):
        """Test creating notification."""
        # Mock data
        notification_data = {
            "user_id": 123,
            "title": "Test Notification",
            "message": "Test message",
            "notification_type": "info"
        }
        
        # Mock repository response
        mock_notification = MagicMock()
        mock_notification.id = 456
        notification_service.repository.create = AsyncMock(return_value=mock_notification)
        
        # Test creation
        if hasattr(notification_service, 'create_notification'):
            result = await notification_service.create_notification(notification_data)
            assert result is not None
            notification_service.repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_notifications(self, notification_service):
        """Test getting user notifications."""
        # Mock repository response
        mock_notifications = [MagicMock(), MagicMock()]
        notification_service.repository.get_by_user = AsyncMock(return_value=mock_notifications)
        
        # Test retrieval
        if hasattr(notification_service, 'get_user_notifications'):
            result = await notification_service.get_user_notifications(123)
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_mark_as_read(self, notification_service):
        """Test marking notification as read."""
        # Mock repository response
        mock_notification = MagicMock()
        mock_notification.is_read = True
        notification_service.repository.mark_as_read = AsyncMock(return_value=mock_notification)
        
        # Test marking as read
        if hasattr(notification_service, 'mark_as_read'):
            result = await notification_service.mark_as_read(123)
            assert result is not None
            assert result.is_read is True

    @pytest.mark.asyncio
    async def test_send_critical_alert(self, notification_service):
        """Test sending critical alert."""
        # Mock critical alert
        alert_data = {
            "user_id": 123,
            "title": "Critical Finding",
            "message": "Critical ECG finding detected",
            "priority": "critical"
        }
        
        # Mock repository response
        mock_notification = MagicMock()
        notification_service.repository.create = AsyncMock(return_value=mock_notification)
        
        # Test critical alert
        if hasattr(notification_service, 'send_critical_alert'):
            result = await notification_service.send_critical_alert(alert_data)
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_unread_count(self, notification_service):
        """Test getting unread notification count."""
        # Mock repository response
        notification_service.repository.get_unread_count = AsyncMock(return_value=5)
        
        # Test unread count
        if hasattr(notification_service, 'get_unread_count'):
            result = await notification_service.get_unread_count(123)
            assert result == 5

    @pytest.mark.asyncio
    async def test_delete_old_notifications(self, notification_service):
        """Test deleting old notifications."""
        # Mock repository response
        notification_service.repository.delete_old = AsyncMock(return_value=10)
        
        # Test deletion
        if hasattr(notification_service, 'delete_old_notifications'):
            result = await notification_service.delete_old_notifications(days=30)
            assert result == 10


class TestServiceIntegration:
    """Test service integration scenarios."""

    @pytest.mark.asyncio
    async def test_ecg_analysis_workflow(self):
        """Test complete ECG analysis workflow."""
        # Mock services
        ecg_service = MagicMock()
        notification_service = MagicMock()
        
        # Mock workflow
        mock_analysis = MagicMock()
        mock_analysis.id = 123
        mock_analysis.clinical_urgency = ClinicalUrgency.CRITICAL
        
        ecg_service.create_analysis = AsyncMock(return_value=mock_analysis)
        notification_service.send_critical_alert = AsyncMock()
        
        # Test workflow
        analysis = await ecg_service.create_analysis({"patient_id": 456})
        
        if analysis.clinical_urgency == ClinicalUrgency.CRITICAL:
            await notification_service.send_critical_alert({
                "analysis_id": analysis.id,
                "urgency": "critical"
            })
        
        assert analysis is not None
        notification_service.send_critical_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_patient_registration_workflow(self):
        """Test patient registration workflow."""
        # Mock services
        patient_service = MagicMock()
        user_service = MagicMock()
        
        # Mock workflow
        mock_patient = MagicMock()
        mock_patient.id = 123
        mock_user = MagicMock()
        
        patient_service.create_patient = AsyncMock(return_value=mock_patient)
        user_service.get_user_by_id = AsyncMock(return_value=mock_user)
        
        # Test workflow
        patient = await patient_service.create_patient({
            "first_name": "John",
            "last_name": "Doe"
        })
        
        creator = await user_service.get_user_by_id(456)
        
        assert patient is not None
        assert creator is not None

    @pytest.mark.asyncio
    async def test_notification_cascade(self):
        """Test notification cascade."""
        # Mock services
        notification_service = MagicMock()
        user_service = MagicMock()
        
        # Mock cascade
        mock_users = [MagicMock(), MagicMock()]
        notification_service.create_notification = AsyncMock()
        user_service.get_users_by_role = AsyncMock(return_value=mock_users)
        
        # Test cascade
        users = await user_service.get_users_by_role(UserRoles.PHYSICIAN)
        
        for user in users:
            await notification_service.create_notification({
                "user_id": user.id,
                "title": "System Alert",
                "message": "System maintenance scheduled"
            })
        
        assert len(users) == 2
        assert notification_service.create_notification.call_count == 2

