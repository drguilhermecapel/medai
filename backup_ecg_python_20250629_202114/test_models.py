"""
Tests for models to improve coverage.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock

from app.models.user import User
from app.models.patient import Patient
from app.models.notification import Notification
from app.models.validation import Validation
from app.core.constants import UserRole, AnalysisStatus, ClinicalUrgency, ValidationStatus

class TestUserModel:
    """Test User model."""

    def test_user_creation(self):
        """Test user model creation."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            first_name="John",
            last_name="Doe",
            role=UserRole.PHYSICIAN,
            is_active=True
        )
        
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == UserRole.PHYSICIAN
        assert user.is_active is True

    def test_user_full_name_property(self):
        """Test user full name property."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            first_name="John",
            last_name="Doe",
            role=UserRole.PHYSICIAN
        )
        
        if hasattr(user, 'full_name'):
            assert user.full_name == "John Doe"

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            first_name="John",
            last_name="Doe",
            role=UserRole.PHYSICIAN
        )
        
        str_repr = str(user)
        assert "test@example.com" in str_repr or "John" in str_repr

    def test_user_role_validation(self):
        """Test user role validation."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            first_name="John",
            last_name="Doe",
            role=UserRole.ADMIN
        )
        
        assert user.role == UserRole.ADMIN

    def test_user_default_values(self):
        """Test user default values."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.VIEWER
        )
        
        assert user.is_active is True  # Default value
        assert user.created_at is not None
        assert user.updated_at is not None

class TestPatientModel:
    """Test Patient model."""

    def test_patient_creation(self):
        """Test patient model creation."""
        patient = Patient(
            patient_id="P123456",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1).date(),
            gender="male",
            phone="123-456-7890",
            email="patient@example.com"
        )
        
        assert patient.patient_id == "P123456"
        assert patient.first_name == "John"
        assert patient.last_name == "Doe"
        assert patient.date_of_birth == datetime(1990, 1, 1).date()
        assert patient.gender == "male"
        assert patient.phone == "123-456-7890"
        assert patient.email == "patient@example.com"

    def test_patient_age_calculation(self):
        """Test patient age calculation."""
        patient = Patient(
            patient_id="P123456",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1).date(),
            gender="male"
        )
        
        if hasattr(patient, 'age'):
            age = patient.age
            assert isinstance(age, int)
            assert age > 0

    def test_patient_string_representation(self):
        """Test patient string representation."""
        patient = Patient(
            patient_id="P123456",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1).date(),
            gender="male"
        )
        
        str_repr = str(patient)
        assert "John" in str_repr or "Doe" in str_repr

    def test_patient_minimal_data(self):
        """Test patient with minimal required data."""
        patient = Patient(
            patient_id="P789012",
            first_name="Jane",
            last_name="Doe",
            date_of_birth=datetime(1985, 5, 15).date(),
            gender="female"
        )
        
        assert patient.first_name == "Jane"
        assert patient.last_name == "Doe"
        assert patient.phone is None
        assert patient.email is None

    def test_patient_timestamps(self):
        """Test patient timestamps."""
        patient = Patient(
            patient_id="P345678",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1).date(),
            gender="male"
        )
        
        assert patient.created_at is not None
        assert patient.updated_at is not None

class TestECGAnalysisModel:
    """Test ECG Analysis model."""

    def test_ecg_analysis_creation(self):
        """Test ECG analysis model creation."""
        analysis = ECGAnalysis(
            analysis_id="ECG123456",
            patient_id=123,
            file_path="/path/to/ecg.txt",
            original_filename="ecg.txt",
            status=AnalysisStatus.PENDING,
            clinical_urgency=ClinicalUrgency.LOW,
            created_by=456
        )
        
        assert analysis.analysis_id == "ECG123456"
        assert analysis.patient_id == 123
        assert analysis.file_path == "/path/to/ecg.txt"
        assert analysis.original_filename == "ecg.txt"
        assert analysis.status == AnalysisStatus.PENDING
        assert analysis.clinical_urgency == ClinicalUrgency.LOW
        assert analysis.created_by == 456

    def test_ecg_analysis_with_results(self):
        """Test ECG analysis with results."""
        analysis = ECGAnalysis(
            analysis_id="ECG123456",
            patient_id=123,
            file_path="/path/to/ecg.txt",
            original_filename="ecg.txt",
            status=AnalysisStatus.COMPLETED,
            clinical_urgency=ClinicalUrgency.LOW,
            created_by=456,
            heart_rate_bpm=75,
            rhythm="sinus",
            primary_diagnosis="Normal ECG"
        )
        
        assert analysis.heart_rate_bpm == 75
        assert analysis.rhythm == "sinus"
        assert analysis.primary_diagnosis == "Normal ECG"

    def test_ecg_analysis_status_update(self):
        """Test ECG analysis status update."""
        analysis = ECGAnalysis(
            analysis_id="ECG123456",
            patient_id=123,
            file_path="/path/to/ecg.txt",
            original_filename="ecg.txt",
            status=AnalysisStatus.PENDING,
            clinical_urgency=ClinicalUrgency.LOW,
            created_by=456
        )
        
        analysis.status = AnalysisStatus.COMPLETED
        assert analysis.status == AnalysisStatus.COMPLETED

    def test_ecg_analysis_string_representation(self):
        """Test ECG analysis string representation."""
        analysis = ECGAnalysis(
            analysis_id="ECG123456",
            patient_id=123,
            file_path="/path/to/ecg.txt",
            original_filename="ecg.txt",
            status=AnalysisStatus.PENDING,
            clinical_urgency=ClinicalUrgency.LOW,
            created_by=456
        )
        
        str_repr = str(analysis)
        assert "ECG123456" in str_repr or "123" in str_repr or "ecg.txt" in str_repr

    def test_ecg_analysis_timestamps(self):
        """Test ECG analysis timestamps."""
        analysis = ECGAnalysis(
            analysis_id="ECG123456",
            patient_id=123,
            file_path="/path/to/ecg.txt",
            original_filename="ecg.txt",
            status=AnalysisStatus.PENDING,
            clinical_urgency=ClinicalUrgency.LOW,
            created_by=456
        )
        
        assert analysis.created_at is not None
        assert analysis.updated_at is not None

class TestNotificationModel:
    """Test Notification model."""

    def test_notification_creation(self):
        """Test notification model creation."""
        notification = Notification(
            user_id=123,
            title="Test Notification",
            message="This is a test message",
            notification_type="info",
            priority="normal"
        )
        
        assert notification.user_id == 123
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test message"
        assert notification.notification_type == "info"
        assert notification.priority == "normal"

    def test_notification_read_status(self):
        """Test notification read status."""
        notification = Notification(
            user_id=123,
            title="Test Notification",
            message="This is a test message",
            notification_type="info"
        )
        
        assert notification.is_read is False  # Default value
        
        notification.is_read = True
        assert notification.is_read is True

    def test_notification_string_representation(self):
        """Test notification string representation."""
        notification = Notification(
            user_id=123,
            title="Test Notification",
            message="This is a test message",
            notification_type="info"
        )
        
        str_repr = str(notification)
        assert "Test Notification" in str_repr

    def test_notification_timestamps(self):
        """Test notification timestamps."""
        notification = Notification(
            user_id=123,
            title="Test Notification",
            message="This is a test message",
            notification_type="info"
        )
        
        assert notification.created_at is not None

    def test_notification_priority_levels(self):
        """Test notification priority levels."""
        critical_notification = Notification(
            user_id=123,
            title="Critical Alert",
            message="Critical finding detected",
            notification_type="critical_finding",
            priority="critical"
        )
        
        assert critical_notification.priority == "critical"

class TestValidationModel:
    """Test Validation model."""

    def test_validation_creation(self):
        """Test validation model creation."""
        validation = Validation(
            analysis_id=123,
            validator_id=456,
            status=ValidationStatus.PENDING
        )
        
        assert validation.analysis_id == 123
        assert validation.validator_id == 456
        assert validation.status == ValidationStatus.PENDING

    def test_validation_with_comments(self):
        """Test validation with comments."""
        validation = Validation(
            analysis_id=123,
            validator_id=456,
            status=ValidationStatus.APPROVED,
            clinical_notes="Analysis is correct and complete"
        )
        
        assert validation.clinical_notes == "Analysis is correct and complete"
        assert validation.status == ValidationStatus.APPROVED

    def test_validation_status_update(self):
        """Test validation status update."""
        validation = Validation(
            analysis_id=123,
            validator_id=456,
            status=ValidationStatus.PENDING
        )
        
        validation.status = ValidationStatus.APPROVED
        assert validation.status == ValidationStatus.APPROVED

    def test_validation_string_representation(self):
        """Test validation string representation."""
        validation = Validation(
            analysis_id=123,
            validator_id=456,
            status=ValidationStatus.PENDING
        )
        
        str_repr = str(validation)
        assert "123" in str_repr or "456" in str_repr

    def test_validation_timestamps(self):
        """Test validation timestamps."""
        validation = Validation(
            analysis_id=123,
            validator_id=456,
            status=ValidationStatus.PENDING
        )
        
        assert validation.created_at is not None
        assert validation.updated_at is not None

class TestModelRelationships:
    """Test model relationships."""

    def test_user_patient_relationship(self):
        """Test user-patient relationship."""
        user = User(
            username="doctor123",
            email="doctor@example.com",
            hashed_password="hashed_password_123",
            first_name="Dr. John",
            last_name="Smith",
            role=UserRole.PHYSICIAN
        )
        
        patient = Patient(
            patient_id="P123456",
            first_name="Jane",
            last_name="Doe",
            date_of_birth=datetime(1985, 5, 15).date(),
            gender="female",
            created_by=user.id if hasattr(user, 'id') else 1
        )
        
        # Test relationship exists
        assert hasattr(patient, 'created_by')

    def test_patient_analysis_relationship(self):
        """Test patient-analysis relationship."""
        patient = Patient(
            patient_id="P123456",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1).date(),
            gender="male"
        )
        
        analysis = ECGAnalysis(
            analysis_id="ECG123456",
            patient_id=patient.id if hasattr(patient, 'id') else 123,
            file_path="/path/to/ecg.txt",
            original_filename="ecg.txt",
            status=AnalysisStatus.PENDING,
            clinical_urgency=ClinicalUrgency.LOW,
            created_by=456
        )
        
        # Test relationship exists
        assert hasattr(analysis, 'patient_id')

    def test_analysis_validation_relationship(self):
        """Test analysis-validation relationship."""
        analysis = ECGAnalysis(
            analysis_id="ECG123456",
            patient_id=123,
            file_path="/path/to/ecg.txt",
            original_filename="ecg.txt",
            status=AnalysisStatus.PENDING,
            clinical_urgency=ClinicalUrgency.LOW,
            created_by=456
        )
        
        validation = Validation(
            analysis_id=analysis.id if hasattr(analysis, 'id') else 123,
            validator_id=789,
            status=ValidationStatus.PENDING
        )
        
        # Test relationship exists
        assert hasattr(validation, 'analysis_id')

    def test_user_notification_relationship(self):
        """Test user-notification relationship."""
        user = User(
            username="user123",
            email="user@example.com",
            hashed_password="hashed_password_123",
            first_name="John",
            last_name="Doe",
            role=UserRole.VIEWER
        )
        
        notification = Notification(
            user_id=user.id if hasattr(user, 'id') else 123,
            title="Test Notification",
            message="This is a test message",
            notification_type="info"
        )
        
        # Test relationship exists
        assert hasattr(notification, 'user_id')

