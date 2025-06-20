"""
Tests for schemas to improve coverage.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate, User
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.schemas.ecg_analysis import ECGAnalysisCreate, ECGAnalysisResponse
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.schemas.validation import ValidationCreate, ValidationResponse


class TestUserSchemas:
    """Test User schemas."""

    def test_user_create_valid(self):
        """Test valid user creation."""
        user_data = {
            "email": "test@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
            "role": "physician"
        }
        
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.password == "securepassword123"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == "physician"

    def test_user_create_invalid_email(self):
        """Test user creation with invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
            "role": "physician"
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_update_partial(self):
        """Test partial user update."""
        update_data = {
            "first_name": "Jane"
        }
        
        user_update = UserUpdate(**update_data)
        assert user_update.first_name == "Jane"
        assert user_update.last_name is None

    def test_user_response_serialization(self):
        """Test user response serialization."""
        user_data = {
            "id": 123,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "physician",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user_response = User(**user_data)
        assert user_response.id == 123
        assert user_response.email == "test@example.com"
        assert user_response.is_active is True

    def test_user_password_validation(self):
        """Test password validation."""
        # Test short password
        user_data = {
            "email": "test@example.com",
            "password": "123",
            "first_name": "John",
            "last_name": "Doe",
            "role": "physician"
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)


class TestPatientSchemas:
    """Test Patient schemas."""

    def test_patient_create_valid(self):
        """Test valid patient creation."""
        patient_data = {
            "name": "John Doe",
            "birth_date": "1990-01-01",
            "gender": "male",
            "phone": "123-456-7890",
            "email": "patient@example.com"
        }
        
        patient = PatientCreate(**patient_data)
        assert patient.name == "John Doe"
        assert patient.gender == "male"
        assert patient.phone == "123-456-7890"

    def test_patient_create_minimal(self):
        """Test patient creation with minimal data."""
        patient_data = {
            "name": "Jane Doe",
            "birth_date": "1985-05-15",
            "gender": "female"
        }
        
        patient = PatientCreate(**patient_data)
        assert patient.name == "Jane Doe"
        assert patient.gender == "female"
        assert patient.phone is None

    def test_patient_update(self):
        """Test patient update."""
        update_data = {
            "phone": "987-654-3210",
            "email": "newemail@example.com"
        }
        
        patient_update = PatientUpdate(**update_data)
        assert patient_update.phone == "987-654-3210"
        assert patient_update.email == "newemail@example.com"

    def test_patient_response(self):
        """Test patient response."""
        patient_data = {
            "id": 123,
            "name": "John Doe",
            "birth_date": datetime(1990, 1, 1),
            "gender": "male",
            "phone": "123-456-7890",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        patient_response = PatientResponse(**patient_data)
        assert patient_response.id == 123
        assert patient_response.name == "John Doe"

    def test_patient_gender_validation(self):
        """Test patient gender validation."""
        patient_data = {
            "name": "John Doe",
            "birth_date": "1990-01-01",
            "gender": "invalid_gender"
        }
        
        with pytest.raises(ValidationError):
            PatientCreate(**patient_data)


class TestECGAnalysisSchemas:
    """Test ECG Analysis schemas."""

    def test_ecg_analysis_create(self):
        """Test ECG analysis creation."""
        analysis_data = {
            "patient_id": 123,
            "file_path": "/path/to/ecg.txt",
            "original_filename": "ecg.txt"
        }
        
        analysis = ECGAnalysisCreate(**analysis_data)
        assert analysis.patient_id == 123
        assert analysis.file_path == "/path/to/ecg.txt"
        assert analysis.original_filename == "ecg.txt"

    def test_ecg_analysis_response(self):
        """Test ECG analysis response."""
        analysis_data = {
            "id": 456,
            "patient_id": 123,
            "status": "completed",
            "clinical_urgency": "low",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 789
        }
        
        analysis_response = ECGAnalysisResponse(**analysis_data)
        assert analysis_response.id == 456
        assert analysis_response.patient_id == 123
        assert analysis_response.status == "completed"

    def test_ecg_analysis_with_results(self):
        """Test ECG analysis with results."""
        analysis_data = {
            "id": 456,
            "patient_id": 123,
            "status": "completed",
            "clinical_urgency": "low",
            "heart_rate": 75,
            "rhythm": "sinus",
            "diagnosis": "Normal ECG",
            "confidence_score": 0.95,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 789
        }
        
        analysis_response = ECGAnalysisResponse(**analysis_data)
        assert analysis_response.heart_rate == 75
        assert analysis_response.rhythm == "sinus"
        assert analysis_response.confidence_score == 0.95


class TestNotificationSchemas:
    """Test Notification schemas."""

    def test_notification_create(self):
        """Test notification creation."""
        notification_data = {
            "recipient_id": 123,
            "title": "Test Notification",
            "message": "This is a test message",
            "type": "info"
        }
        
        notification = NotificationCreate(**notification_data)
        assert notification.recipient_id == 123
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test message"
        assert notification.type == "info"

    def test_notification_response(self):
        """Test notification response."""
        notification_data = {
            "id": 456,
            "recipient_id": 123,
            "title": "Test Notification",
            "message": "This is a test message",
            "type": "info",
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        
        notification_response = NotificationResponse(**notification_data)
        assert notification_response.id == 456
        assert notification_response.is_read is False

    def test_notification_priority(self):
        """Test notification with priority."""
        notification_data = {
            "recipient_id": 123,
            "title": "Critical Alert",
            "message": "Critical finding detected",
            "type": "critical_finding",
            "priority": "critical"
        }
        
        notification = NotificationCreate(**notification_data)
        assert notification.priority == "critical"
        assert notification.type == "critical_finding"


class TestValidationSchemas:
    """Test Validation schemas."""

    def test_validation_create(self):
        """Test validation creation."""
        validation_data = {
            "analysis_id": 123,
            "priority": "urgent"
        }
        
        validation = ValidationCreate(**validation_data)
        assert validation.analysis_id == 123
        assert validation.priority == "urgent"

    def test_validation_response(self):
        """Test validation response."""
        validation_data = {
            "id": 456,
            "analysis_id": 123,
            "validator_id": 789,
            "status": "pending",
            "priority": "urgent",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        validation_response = ValidationResponse(**validation_data)
        assert validation_response.id == 456
        assert validation_response.analysis_id == 123
        assert validation_response.status == "pending"

    def test_validation_with_comments(self):
        """Test validation with comments."""
        validation_data = {
            "id": 456,
            "analysis_id": 123,
            "validator_id": 789,
            "status": "approved",
            "priority": "routine",
            "comments": "Analysis is correct and complete",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        validation_response = ValidationResponse(**validation_data)
        assert validation_response.comments == "Analysis is correct and complete"
        assert validation_response.status == "approved"


class TestSchemaValidation:
    """Test schema validation edge cases."""

    def test_empty_string_validation(self):
        """Test empty string validation."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="",
                password="password123",
                first_name="John",
                last_name="Doe",
                role="physician"
            )

    def test_none_values_in_optional_fields(self):
        """Test None values in optional fields."""
        patient_data = {
            "name": "John Doe",
            "birth_date": "1990-01-01",
            "gender": "male",
            "phone": None,
            "email": None
        }
        
        patient = PatientCreate(**patient_data)
        assert patient.phone is None
        assert patient.email is None

    def test_date_format_validation(self):
        """Test date format validation."""
        with pytest.raises(ValidationError):
            PatientCreate(
                name="John Doe",
                birth_date="invalid-date",
                gender="male"
            )

    def test_enum_validation(self):
        """Test enum field validation."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="password123",
                first_name="John",
                last_name="Doe",
                role="invalid_role"
            )

    def test_positive_integer_validation(self):
        """Test positive integer validation."""
        with pytest.raises(ValidationError):
            ECGAnalysisCreate(
                patient_id=-1,  # Negative ID should be invalid
                file_path="/path/to/ecg.txt",
                original_filename="ecg.txt"
            )

    def test_string_length_validation(self):
        """Test string length validation."""
        # Test very long string
        long_string = "x" * 1000
        
        with pytest.raises(ValidationError):
            NotificationCreate(
                recipient_id=123,
                title=long_string,  # Title too long
                message="Test message",
                type="info"
            )

