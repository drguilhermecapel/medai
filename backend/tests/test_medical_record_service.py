"""Test medical record service."""

from unittest.mock import AsyncMock, Mock

import pytest

from app.services.medical_record_service import (
    MedicalRecordService,
    RecordStatus,
    RecordType,
)


@pytest.fixture
def medical_record_service(test_db):
    """Create medical record service instance."""
    return MedicalRecordService(test_db)


@pytest.fixture
def sample_consultation_data():
    """Sample consultation record data."""
    return {
        "chief_complaint": "chest pain",
        "history_present_illness": "Patient reports chest pain for 2 hours",
        "assessment": "Possible angina",
        "plan": "ECG, cardiac enzymes, cardiology consult",
        "vital_signs": {
            "blood_pressure": "140/90",
            "heart_rate": 85,
            "temperature": 98.6
        }
    }


@pytest.fixture
def sample_prescription_data():
    """Sample prescription record data."""
    return {
        "medications": [
            {
                "name": "Aspirin",
                "dosage": "81mg",
                "frequency": "once daily",
                "duration": "ongoing"
            },
            {
                "name": "Metoprolol",
                "dosage": "25mg",
                "frequency": "twice daily",
                "duration": "30 days"
            }
        ]
    }


@pytest.fixture
def mock_patient():
    """Mock patient object."""
    patient = Mock()
    patient.patient_id = "PAT123456"
    patient.first_name = "John"
    patient.last_name = "Doe"
    return patient


@pytest.mark.asyncio
async def test_create_consultation_record(medical_record_service, mock_patient, sample_consultation_data):
    """Test creating a consultation record."""
    medical_record_service.patient_repository.get_patient_by_patient_id = AsyncMock(return_value=mock_patient)

    record = await medical_record_service.create_medical_record(
        "PAT123456", RecordType.CONSULTATION, sample_consultation_data, 1
    )

    assert isinstance(record, dict)
    assert record["patient_id"] == "PAT123456"
    assert record["record_type"] == RecordType.CONSULTATION
    assert record["status"] == RecordStatus.ACTIVE
    assert record["created_by"] == 1
    assert "record_id" in record
    assert "created_at" in record
    assert "clinical_summary" in record


@pytest.mark.asyncio
async def test_create_prescription_record(medical_record_service, mock_patient, sample_prescription_data):
    """Test creating a prescription record."""
    medical_record_service.patient_repository.get_patient_by_patient_id = AsyncMock(return_value=mock_patient)

    record = await medical_record_service.create_medical_record(
        "PAT123456", RecordType.PRESCRIPTION, sample_prescription_data, 1
    )

    assert isinstance(record, dict)
    assert record["patient_id"] == "PAT123456"
    assert record["record_type"] == RecordType.PRESCRIPTION
    assert record["status"] == RecordStatus.ACTIVE
    assert record["created_by"] == 1
    assert "record_id" in record
    assert len(record["data"]["medications"]) == 2


@pytest.mark.asyncio
async def test_create_record_patient_not_found(medical_record_service, sample_consultation_data):
    """Test creating record for non-existent patient."""
    medical_record_service.patient_repository.get_patient_by_patient_id = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="Patient .* not found"):
        await medical_record_service.create_medical_record(
            "NONEXISTENT", RecordType.CONSULTATION, sample_consultation_data, 1
        )


@pytest.mark.asyncio
async def test_validate_consultation_record_data(medical_record_service):
    """Test consultation record data validation."""
    valid_data = {
        "chief_complaint": "chest pain",
        "history_present_illness": "Patient reports chest pain",
        "assessment": "Possible angina",
        "plan": "ECG, cardiac enzymes"
    }

    result = await medical_record_service._validate_record_data(RecordType.CONSULTATION, valid_data)

    assert result["valid"] is True
    assert len(result["errors"]) == 0


@pytest.mark.asyncio
async def test_validate_consultation_record_missing_fields(medical_record_service):
    """Test consultation record validation with missing fields."""
    invalid_data = {
        "chief_complaint": "chest pain"
    }

    result = await medical_record_service._validate_record_data(RecordType.CONSULTATION, invalid_data)

    assert result["valid"] is False
    assert len(result["errors"]) > 0


@pytest.mark.asyncio
async def test_validate_prescription_record_data(medical_record_service):
    """Test prescription record data validation."""
    valid_data = {
        "medications": [
            {
                "name": "Aspirin",
                "dosage": "81mg",
                "frequency": "once daily",
                "duration": "ongoing"
            }
        ]
    }

    result = await medical_record_service._validate_record_data(RecordType.PRESCRIPTION, valid_data)

    assert result["valid"] is True
    assert len(result["errors"]) == 0


@pytest.mark.asyncio
async def test_validate_prescription_record_missing_medications(medical_record_service):
    """Test prescription record validation with missing medications."""
    invalid_data = {}

    result = await medical_record_service._validate_record_data(RecordType.PRESCRIPTION, invalid_data)

    assert result["valid"] is False
    assert len(result["errors"]) > 0


@pytest.mark.asyncio
async def test_process_consultation_record(medical_record_service):
    """Test consultation record processing."""
    record = {
        "record_id": "CONSULTATION_20250611_120000_PAT123456",
        "data": {
            "chief_complaint": "chest pain",
            "vital_signs": {"blood_pressure": "140/90"},
            "assessment": "Possible angina",
            "plan": "ECG, cardiac enzymes"
        }
    }

    processed = await medical_record_service._process_consultation_record(record)

    assert "clinical_summary" in processed
    assert processed["clinical_summary"]["chief_complaint"] == "chest pain"


@pytest.mark.asyncio
async def test_process_prescription_record(medical_record_service):
    """Test prescription record processing."""
    record = {
        "record_id": "PRESCRIPTION_20250611_120000_PAT123456",
        "data": {
            "medications": [
                {
                    "name": "Aspirin",
                    "dosage": "81mg",
                    "frequency": "once daily",
                    "duration": "ongoing"
                }
            ]
        }
    }

    processed = await medical_record_service._process_prescription_record(record)

    assert len(processed["data"]["medications"]) == 1
    assert processed["data"]["medications"][0]["status"] == "active"
    assert "prescribed_at" in processed["data"]["medications"][0]


@pytest.mark.asyncio
async def test_get_patient_medical_history(medical_record_service, mock_patient):
    """Test getting patient medical history."""
    medical_record_service.patient_repository.get_patient_by_patient_id = AsyncMock(return_value=mock_patient)

    history = await medical_record_service.get_patient_medical_history("PAT123456")

    assert isinstance(history, dict)
    assert history["patient_id"] == "PAT123456"
    assert history["patient_name"] == "John Doe"
    assert "generated_at" in history
    assert "records_summary" in history
    assert "records" in history


@pytest.mark.asyncio
async def test_get_medical_history_patient_not_found(medical_record_service):
    """Test getting medical history for non-existent patient."""
    medical_record_service.patient_repository.get_patient_by_patient_id = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="Patient .* not found"):
        await medical_record_service.get_patient_medical_history("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_medical_history_with_filters(medical_record_service, mock_patient):
    """Test getting medical history with record type filters."""
    medical_record_service.patient_repository.get_patient_by_patient_id = AsyncMock(return_value=mock_patient)

    history = await medical_record_service.get_patient_medical_history(
        "PAT123456",
        record_types=[RecordType.CONSULTATION, RecordType.PRESCRIPTION],
        limit=50
    )

    assert isinstance(history, dict)
    assert history["patient_id"] == "PAT123456"


@pytest.mark.asyncio
async def test_record_type_enum():
    """Test record type enum values."""
    assert RecordType.CONSULTATION.value == "consultation"
    assert RecordType.PROCEDURE.value == "procedure"
    assert RecordType.DIAGNOSTIC.value == "diagnostic"
    assert RecordType.PRESCRIPTION.value == "prescription"
    assert RecordType.LAB_RESULT.value == "lab_result"
    assert RecordType.IMAGING.value == "imaging"
    assert RecordType.DISCHARGE.value == "discharge"
    assert RecordType.FOLLOW_UP.value == "follow_up"


@pytest.mark.asyncio
async def test_record_status_enum():
    """Test record status enum values."""
    assert RecordStatus.DRAFT.value == "draft"
    assert RecordStatus.ACTIVE.value == "active"
    assert RecordStatus.COMPLETED.value == "completed"
    assert RecordStatus.CANCELLED.value == "cancelled"
    assert RecordStatus.AMENDED.value == "amended"
