"""
Tests for Multi-Specialty EMR Service.

Comprehensive tests for multi-specialty EMR functionality including
case creation, cross-specialty consultations, and care coordination.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.services.multi_specialty_emr import (
    MultiSpecialtyEMRService,
    MedicalSpecialty,
    ConsultationType,
    CoordinationStatus,
    MultiSpecialtyCase
)
from app.models.patient import Patient
from app.models.user import User
from app.models.doctor_profile import DoctorProfile
from app.core.constants import UserRole


class TestMultiSpecialtyEMRService:
    """Test cases for MultiSpecialtyEMRService."""

    @pytest.fixture
    async def db_session(self):
        """Mock database session."""
        mock_session = AsyncMock()
        return mock_session

    @pytest.fixture
    async def service(self, db_session):
        """Create service instance with mock dependencies."""
        return MultiSpecialtyEMRService(db_session)

    @pytest.fixture
    def sample_patient_id(self):
        """Sample patient ID for testing."""
        return uuid4()

    @pytest.fixture
    def sample_physician_id(self):
        """Sample physician ID for testing."""
        return uuid4()

    @pytest.fixture
    def sample_case_data(self, sample_patient_id, sample_physician_id):
        """Sample case data for testing."""
        return {
            "patient_id": sample_patient_id,
            "primary_specialty": MedicalSpecialty.CARDIOLOGY,
            "primary_physician_id": sample_physician_id,
            "involved_specialties": [MedicalSpecialty.NEUROLOGY, MedicalSpecialty.ENDOCRINOLOGY],
            "case_description": "Complex cardiac case requiring multi-specialty coordination"
        }

    @pytest.mark.asyncio
    async def test_medical_specialty_enum(self):
        """Test that medical specialty enum contains expected values."""
        # Test key specialties are present
        assert MedicalSpecialty.CARDIOLOGY == "cardiology"
        assert MedicalSpecialty.NEUROLOGY == "neurology"
        assert MedicalSpecialty.ONCOLOGY == "oncology"
        assert MedicalSpecialty.PEDIATRICS == "pediatrics"
        
        # Test comprehensive specialty list
        specialties = list(MedicalSpecialty)
        assert len(specialties) >= 20  # Should have at least 20 specialties
        
        # Test specialty values are strings
        for specialty in specialties:
            assert isinstance(specialty.value, str)
            assert "_" in specialty.value or specialty.value.islower()

    @pytest.mark.asyncio
    async def test_consultation_type_enum(self):
        """Test consultation type enum."""
        assert ConsultationType.REFERRAL == "referral"
        assert ConsultationType.SECOND_OPINION == "second_opinion"
        assert ConsultationType.COLLABORATIVE == "collaborative"
        assert ConsultationType.EMERGENCY == "emergency"
        assert ConsultationType.FOLLOW_UP == "follow_up"

    @pytest.mark.asyncio
    async def test_coordination_status_enum(self):
        """Test coordination status enum."""
        assert CoordinationStatus.INITIATED == "initiated"
        assert CoordinationStatus.PENDING_RESPONSE == "pending_response"
        assert CoordinationStatus.ACTIVE == "active"
        assert CoordinationStatus.COMPLETED == "completed"
        assert CoordinationStatus.CANCELLED == "cancelled"
        assert CoordinationStatus.ON_HOLD == "on_hold"

    @pytest.mark.asyncio
    async def test_multi_specialty_case_creation(self, sample_case_data):
        """Test MultiSpecialtyCase object creation."""
        case_id = uuid4()
        case = MultiSpecialtyCase(
            case_id=case_id,
            patient_id=sample_case_data["patient_id"],
            primary_specialty=sample_case_data["primary_specialty"],
            primary_physician_id=sample_case_data["primary_physician_id"],
            involved_specialties=sample_case_data["involved_specialties"],
            case_description=sample_case_data["case_description"]
        )
        
        assert case.case_id == case_id
        assert case.patient_id == sample_case_data["patient_id"]
        assert case.primary_specialty == MedicalSpecialty.CARDIOLOGY
        assert case.primary_physician_id == sample_case_data["primary_physician_id"]
        assert len(case.involved_specialties) == 2
        assert MedicalSpecialty.NEUROLOGY in case.involved_specialties
        assert MedicalSpecialty.ENDOCRINOLOGY in case.involved_specialties
        assert case.status == CoordinationStatus.INITIATED
        assert isinstance(case.created_at, datetime)
        assert case.consultations == []
        assert case.care_plan == {}
        assert case.notes == []

    @pytest.mark.asyncio
    async def test_service_initialization(self, db_session):
        """Test service initialization."""
        service = MultiSpecialtyEMRService(db_session)
        
        assert service.db == db_session
        assert hasattr(service, 'medical_record_service')
        assert hasattr(service, 'notification_service')
        assert service.active_cases == {}

    @pytest.mark.asyncio
    async def test_create_multi_specialty_case_success(self, service, sample_case_data):
        """Test successful creation of multi-specialty case."""
        # Mock patient and physician existence
        mock_patient = MagicMock(spec=Patient)
        mock_patient.id = sample_case_data["patient_id"]
        
        mock_physician = MagicMock(spec=User)
        mock_physician.id = sample_case_data["primary_physician_id"]
        mock_physician.role = UserRole.DOCTOR
        
        service._get_patient = AsyncMock(return_value=mock_patient)
        service._get_physician = AsyncMock(return_value=mock_physician)
        service._notify_involved_specialties = AsyncMock()
        service.log_audit = AsyncMock()
        
        # Create case
        case = await service.create_multi_specialty_case(**sample_case_data)
        
        # Verify case creation
        assert isinstance(case, MultiSpecialtyCase)
        assert case.patient_id == sample_case_data["patient_id"]
        assert case.primary_specialty == sample_case_data["primary_specialty"]
        assert case.primary_physician_id == sample_case_data["primary_physician_id"]
        assert case.involved_specialties == sample_case_data["involved_specialties"]
        assert case.case_description == sample_case_data["case_description"]
        assert case.status == CoordinationStatus.INITIATED
        
        # Verify case is stored in active cases
        assert case.case_id in service.active_cases
        assert service.active_cases[case.case_id] == case
        
        # Verify audit logging was called
        service.log_audit.assert_called_once()
        
        # Verify notification was called
        service._notify_involved_specialties.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_multi_specialty_case_invalid_patient(self, service, sample_case_data):
        """Test case creation with invalid patient ID."""
        # Mock patient not found
        service._get_patient = AsyncMock(return_value=None)
        
        # Attempt to create case
        with pytest.raises(ValueError, match="Patient with ID .* not found"):
            await service.create_multi_specialty_case(**sample_case_data)

    @pytest.mark.asyncio
    async def test_create_multi_specialty_case_invalid_physician(self, service, sample_case_data):
        """Test case creation with invalid physician ID."""
        # Mock patient exists but physician doesn't
        mock_patient = MagicMock(spec=Patient)
        service._get_patient = AsyncMock(return_value=mock_patient)
        service._get_physician = AsyncMock(return_value=None)
        
        # Attempt to create case
        with pytest.raises(ValueError, match="Physician with ID .* not found"):
            await service.create_multi_specialty_case(**sample_case_data)

    @pytest.mark.asyncio
    async def test_get_specialty_physicians(self, service):
        """Test getting physicians by specialty."""
        # Mock database query result
        mock_physician1 = MagicMock(spec=DoctorProfile)
        mock_physician1.specialties = ["cardiology", "internal_medicine"]
        mock_physician1.current_hospital = "General Hospital"
        
        mock_physician2 = MagicMock(spec=DoctorProfile)
        mock_physician2.specialties = ["cardiology"]
        mock_physician2.current_hospital = "Heart Center"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_physician1, mock_physician2]
        service.db.execute = AsyncMock(return_value=mock_result)
        service._filter_available_physicians = AsyncMock(side_effect=lambda x: x)
        
        # Test getting cardiology physicians
        physicians = await service.get_specialty_physicians(MedicalSpecialty.CARDIOLOGY)
        
        assert len(physicians) == 2
        assert mock_physician1 in physicians
        assert mock_physician2 in physicians
        
        # Verify database query was executed
        service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_specialty_physicians_with_hospital_filter(self, service):
        """Test getting physicians by specialty with hospital filter."""
        # Mock database query result
        mock_physician = MagicMock(spec=DoctorProfile)
        mock_physician.specialties = ["cardiology"]
        mock_physician.current_hospital = "Heart Center"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_physician]
        service.db.execute = AsyncMock(return_value=mock_result)
        service._filter_available_physicians = AsyncMock(side_effect=lambda x: x)
        
        # Test getting cardiology physicians at specific hospital
        physicians = await service.get_specialty_physicians(
            MedicalSpecialty.CARDIOLOGY,
            hospital_filter="Heart Center"
        )
        
        assert len(physicians) == 1
        assert mock_physician in physicians

    @pytest.mark.asyncio
    async def test_schedule_cross_specialty_consultation_success(self, service, sample_case_data):
        """Test successful scheduling of cross-specialty consultation."""
        # Create and store a case
        case_id = uuid4()
        case = MultiSpecialtyCase(
            case_id=case_id,
            patient_id=sample_case_data["patient_id"],
            primary_specialty=sample_case_data["primary_specialty"],
            primary_physician_id=sample_case_data["primary_physician_id"],
            involved_specialties=sample_case_data["involved_specialties"],
            case_description=sample_case_data["case_description"]
        )
        service.active_cases[case_id] = case
        
        # Mock consulting physician
        consulting_physician_id = uuid4()
        mock_physician = MagicMock(spec=User)
        mock_physician.id = consulting_physician_id
        
        service._get_physician = AsyncMock(return_value=mock_physician)
        service.log_audit = AsyncMock()
        service._notify_consultation_scheduled = AsyncMock()
        
        # Mock database operations
        mock_appointment = MagicMock()
        mock_appointment.id = uuid4()
        service.db.add = MagicMock()
        service.db.commit = AsyncMock()
        service.db.refresh = AsyncMock()
        
        # Mock the appointment creation to return our mock
        from unittest.mock import patch
        with patch('app.services.multi_specialty_emr.Appointment', return_value=mock_appointment):
            scheduled_datetime = datetime.utcnow() + timedelta(days=1)
            
            appointment = await service.schedule_cross_specialty_consultation(
                case_id=case_id,
                consulting_specialty=MedicalSpecialty.NEUROLOGY,
                consulting_physician_id=consulting_physician_id,
                scheduled_datetime=scheduled_datetime,
                consultation_notes="Neurological evaluation needed"
            )
            
            # Verify appointment was created
            assert appointment == mock_appointment
            
            # Verify consultation was added to case
            assert len(case.consultations) == 1
            consultation = case.consultations[0]
            assert consultation["appointment_id"] == mock_appointment.id
            assert consultation["specialty"] == "neurology"
            assert consultation["physician_id"] == consulting_physician_id
            assert consultation["status"] == "scheduled"
            
            # Verify database operations
            service.db.add.assert_called_once()
            service.db.commit.assert_called_once()
            service.db.refresh.assert_called_once()
            
            # Verify audit logging
            service.log_audit.assert_called_once()
            
            # Verify notification
            service._notify_consultation_scheduled.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_cross_specialty_consultation_invalid_case(self, service):
        """Test scheduling consultation with invalid case ID."""
        case_id = uuid4()
        consulting_physician_id = uuid4()
        scheduled_datetime = datetime.utcnow() + timedelta(days=1)
        
        # Attempt to schedule consultation for non-existent case
        with pytest.raises(ValueError, match="Multi-specialty case .* not found"):
            await service.schedule_cross_specialty_consultation(
                case_id=case_id,
                consulting_specialty=MedicalSpecialty.NEUROLOGY,
                consulting_physician_id=consulting_physician_id,
                scheduled_datetime=scheduled_datetime
            )

    @pytest.mark.asyncio
    async def test_create_coordinated_care_plan_success(self, service, sample_case_data):
        """Test successful creation of coordinated care plan."""
        # Create and store a case
        case_id = uuid4()
        case = MultiSpecialtyCase(
            case_id=case_id,
            patient_id=sample_case_data["patient_id"],
            primary_specialty=sample_case_data["primary_specialty"],
            primary_physician_id=sample_case_data["primary_physician_id"],
            involved_specialties=sample_case_data["involved_specialties"],
            case_description=sample_case_data["case_description"]
        )
        service.active_cases[case_id] = case
        
        # Mock dependencies
        service.log_audit = AsyncMock()
        service._notify_care_plan_created = AsyncMock()
        
        created_by = uuid4()
        care_plan_data = {
            "goals": ["Reduce cardiac risk", "Manage diabetes"],
            "interventions": {
                "cardiology": ["ECG monitoring", "Medication adjustment"],
                "endocrinology": ["Insulin optimization", "Diet counseling"]
            },
            "timelines": {
                "short_term": "2 weeks",
                "long_term": "3 months"
            },
            "coordination_points": [
                "Weekly multidisciplinary rounds",
                "Shared care protocols"
            ]
        }
        
        # Create care plan
        care_plan = await service.create_coordinated_care_plan(
            case_id=case_id,
            care_plan_data=care_plan_data,
            created_by=created_by
        )
        
        # Verify care plan creation
        assert "plan_id" in care_plan
        assert care_plan["case_id"] == str(case_id)
        assert care_plan["patient_id"] == str(case.patient_id)
        assert care_plan["primary_specialty"] == "cardiology"
        assert care_plan["involved_specialties"] == ["neurology", "endocrinology"]
        assert care_plan["created_by"] == str(created_by)
        assert care_plan["goals"] == care_plan_data["goals"]
        assert care_plan["interventions"] == care_plan_data["interventions"]
        assert care_plan["status"] == "active"
        
        # Verify care plan was added to case
        assert case.care_plan == care_plan
        
        # Verify audit logging
        service.log_audit.assert_called_once()
        
        # Verify notification
        service._notify_care_plan_created.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_coordinated_care_plan_invalid_case(self, service):
        """Test care plan creation with invalid case ID."""
        case_id = uuid4()
        created_by = uuid4()
        care_plan_data = {"goals": ["Test goal"]}
        
        # Attempt to create care plan for non-existent case
        with pytest.raises(ValueError, match="Multi-specialty case .* not found"):
            await service.create_coordinated_care_plan(
                case_id=case_id,
                care_plan_data=care_plan_data,
                created_by=created_by
            )

    @pytest.mark.asyncio
    async def test_transfer_case_specialty_success(self, service, sample_case_data):
        """Test successful case specialty transfer."""
        # Create and store a case
        case_id = uuid4()
        case = MultiSpecialtyCase(
            case_id=case_id,
            patient_id=sample_case_data["patient_id"],
            primary_specialty=sample_case_data["primary_specialty"],
            primary_physician_id=sample_case_data["primary_physician_id"],
            involved_specialties=sample_case_data["involved_specialties"],
            case_description=sample_case_data["case_description"]
        )
        service.active_cases[case_id] = case
        
        # Mock new physician
        new_physician_id = uuid4()
        mock_physician = MagicMock(spec=User)
        mock_physician.id = new_physician_id
        
        service._get_physician = AsyncMock(return_value=mock_physician)
        service.log_audit = AsyncMock()
        service._notify_case_transfer = AsyncMock()
        
        # Transfer case
        transfer_reason = "Patient requires specialized neurology care"
        transferred_by = uuid4()
        
        updated_case = await service.transfer_case_specialty(
            case_id=case_id,
            new_primary_specialty=MedicalSpecialty.NEUROLOGY,
            new_primary_physician_id=new_physician_id,
            transfer_reason=transfer_reason,
            transferred_by=transferred_by
        )
        
        # Verify case update
        assert updated_case.primary_specialty == MedicalSpecialty.NEUROLOGY
        assert updated_case.primary_physician_id == new_physician_id
        
        # Verify transfer note was added
        assert len(updated_case.notes) == 1
        transfer_note = updated_case.notes[0]
        assert transfer_note["type"] == "transfer"
        assert transfer_note["reason"] == transfer_reason
        assert transfer_note["created_by"] == str(transferred_by)
        
        # Verify audit logging
        service.log_audit.assert_called_once()
        
        # Verify notification
        service._notify_case_transfer.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_patient_specialty_history_success(self, service):
        """Test getting patient specialty history."""
        patient_id = uuid4()
        
        # Mock patient
        mock_patient = MagicMock(spec=Patient)
        mock_patient.id = patient_id
        service._get_patient = AsyncMock(return_value=mock_patient)
        
        # Mock appointments
        from app.models.appointment import Appointment
        mock_appointment1 = MagicMock(spec=Appointment)
        mock_appointment1.id = uuid4()
        mock_appointment1.specialty = "cardiology"
        mock_appointment1.scheduled_datetime = datetime.utcnow() - timedelta(days=30)
        mock_appointment1.physician_id = uuid4()
        mock_appointment1.appointment_type = "consultation"
        mock_appointment1.status = "completed"
        mock_appointment1.notes = "Regular checkup"
        mock_appointment1.diagnosis = "Hypertension"
        mock_appointment1.treatment_notes = "Started on ACE inhibitor"
        
        mock_appointment2 = MagicMock(spec=Appointment)
        mock_appointment2.id = uuid4()
        mock_appointment2.specialty = "neurology"
        mock_appointment2.scheduled_datetime = datetime.utcnow() - timedelta(days=15)
        mock_appointment2.physician_id = uuid4()
        mock_appointment2.appointment_type = "consultation"
        mock_appointment2.status = "completed"
        mock_appointment2.notes = "Headache evaluation"
        mock_appointment2.diagnosis = "Tension headache"
        mock_appointment2.treatment_notes = "Lifestyle modifications recommended"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_appointment1, mock_appointment2]
        service.db.execute = AsyncMock(return_value=mock_result)
        
        # Get history
        history = await service.get_patient_specialty_history(patient_id)
        
        # Verify response structure
        assert history["patient_id"] == str(patient_id)
        assert "specialty_history" in history
        assert "multi_specialty_cases" in history
        assert "generated_at" in history
        
        # Verify specialty history
        specialty_history = history["specialty_history"]
        assert "cardiology" in specialty_history
        assert "neurology" in specialty_history
        
        cardiology_history = specialty_history["cardiology"]
        assert len(cardiology_history["appointments"]) == 1
        assert len(cardiology_history["diagnoses"]) == 1
        assert len(cardiology_history["treatments"]) == 1
        assert cardiology_history["diagnoses"][0]["diagnosis"] == "Hypertension"
        
        neurology_history = specialty_history["neurology"]
        assert len(neurology_history["appointments"]) == 1
        assert len(neurology_history["diagnoses"]) == 1
        assert len(neurology_history["treatments"]) == 1
        assert neurology_history["diagnoses"][0]["diagnosis"] == "Tension headache"

    @pytest.mark.asyncio
    async def test_private_helper_methods(self, service):
        """Test private helper methods."""
        # Test _filter_available_physicians (placeholder implementation)
        mock_physicians = [MagicMock(), MagicMock()]
        filtered = await service._filter_available_physicians(mock_physicians)
        assert filtered == mock_physicians  # Placeholder returns all
        
        # Test notification methods (placeholders)
        mock_case = MagicMock()
        mock_case.case_id = uuid4()
        
        # These should not raise exceptions
        await service._notify_involved_specialties(mock_case, ConsultationType.REFERRAL, "normal")
        await service._notify_consultation_scheduled(mock_case, MagicMock(), MagicMock())
        await service._notify_care_plan_created(mock_case, {})
        await service._notify_case_transfer(mock_case, uuid4(), MagicMock(), "test reason")


if __name__ == "__main__":
    pytest.main([__file__])