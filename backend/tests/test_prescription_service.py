"""Test prescription service."""

from unittest.mock import Mock

import pytest

from app.services.prescription_service import (
    InteractionSeverity,
    PrescriptionService,
    PrescriptionStatus,
)


@pytest.fixture
def prescription_service(test_db):
    """Create prescription service instance."""
    return PrescriptionService(test_db)


@pytest.fixture
def sample_prescription_data():
    """Sample prescription data."""
    return {
        "medications": [
            {
                "name": "Aspirin",
                "dosage": "81mg",
                "frequency": "once daily",
                "duration": 30,
                "instructions": "Take with food"
            },
            {
                "name": "Metoprolol",
                "dosage": "25mg",
                "frequency": "twice daily",
                "duration": 30,
                "instructions": "Take in morning and evening"
            }
        ],
        "prescriber_notes": "Monitor blood pressure",
        "pharmacy_instructions": "Generic substitution allowed"
    }


@pytest.fixture
def mock_patient():
    """Mock patient object."""
    patient = Mock()
    patient.patient_id = "PAT123456"
    patient.first_name = "John"
    patient.last_name = "Doe"
    patient.age = 65
    patient.medical_history = ["hypertension", "diabetes"]
    return patient


@pytest.mark.asyncio
async def test_create_prescription_success(prescription_service, mock_patient, sample_prescription_data):
    """Test successful prescription creation."""
    medications = sample_prescription_data["medications"]

    prescription = await prescription_service.create_prescription(
        "PAT123456", 1, medications
    )

    assert isinstance(prescription, dict)
    assert prescription["patient_id"] == "PAT123456"
    assert prescription["status"] == PrescriptionStatus.ACTIVE
    assert prescription["prescriber_id"] == 1
    assert "prescription_id" in prescription
    assert "created_at" in prescription
    assert len(prescription["medications"]) == 2


@pytest.mark.asyncio
async def test_create_prescription_basic_functionality(prescription_service, sample_prescription_data):
    """Test basic prescription creation functionality."""
    medications = sample_prescription_data["medications"]

    prescription = await prescription_service.create_prescription(
        "PAT123456", 1, medications
    )

    assert isinstance(prescription, dict)
    assert "validation_results" in prescription
    assert "interaction_results" in prescription
    assert "ai_recommendations" in prescription


@pytest.mark.asyncio
async def test_validate_medications_success(prescription_service):
    """Test successful medication validation."""
    medications = [
        {
            "name": "Aspirin",
            "dosage": "81mg",
            "frequency": "once daily",
            "duration": 30
        }
    ]

    validation = await prescription_service._validate_medications(medications, "PAT123456")

    assert isinstance(validation, dict)
    assert "valid" in validation
    assert "warnings" in validation
    assert "errors" in validation
    assert "medication_validations" in validation


@pytest.mark.asyncio
async def test_validate_medications_missing_fields(prescription_service):
    """Test medication validation with missing fields."""
    medications = [
        {
            "name": "Aspirin"
        }
    ]

    validation = await prescription_service._validate_medications(medications, "PAT123456")

    assert isinstance(validation, dict)
    assert validation["valid"] is False
    assert len(validation["errors"]) > 0


@pytest.mark.asyncio
async def test_check_drug_interactions(prescription_service):
    """Test drug interaction checking."""
    medications = [
        {"name": "Warfarin", "dosage": "5mg"},
        {"name": "Aspirin", "dosage": "81mg"}
    ]

    interactions = await prescription_service._check_drug_interactions(medications)

    assert isinstance(interactions, dict)
    assert "has_interactions" in interactions
    assert "interactions" in interactions
    assert "severity_summary" in interactions
    assert isinstance(interactions["interactions"], list)

    for interaction in interactions["interactions"]:
        assert "drug1" in interaction
        assert "drug2" in interaction
        assert "severity" in interaction
        assert "mechanism" in interaction
        assert "recommendation" in interaction


@pytest.mark.asyncio
async def test_generate_ai_recommendations(prescription_service):
    """Test AI recommendation generation."""
    medications = [
        {"name": "Aspirin", "dosage": "81mg", "frequency": "once daily"}
    ]
    validation_results = {"valid": True, "warnings": [], "errors": []}
    interaction_results = {"has_interactions": False, "interactions": [], "severity_summary": {"major": 0, "contraindicated": 0}}

    recommendations = await prescription_service._generate_ai_recommendations(
        medications, validation_results, interaction_results
    )

    assert isinstance(recommendations, list)


@pytest.mark.asyncio
async def test_drug_interaction_checking(prescription_service):
    """Test drug interaction checking."""
    medications = [
        {"name": "warfarin", "dosage": "5mg"},
        {"name": "aspirin", "dosage": "81mg"}
    ]

    interactions = await prescription_service._check_drug_interactions(medications)

    assert isinstance(interactions, dict)
    assert "has_interactions" in interactions
    assert "interactions" in interactions
    assert "severity_summary" in interactions


@pytest.mark.asyncio
async def test_get_prescription_by_id(prescription_service):
    """Test getting prescription by ID."""
    prescription = await prescription_service.get_prescription_by_id("RX123456")

    assert prescription is None


@pytest.mark.asyncio
async def test_update_prescription_status(prescription_service):
    """Test updating prescription status."""
    result = await prescription_service.update_prescription_status(
        "RX123456", PrescriptionStatus.COMPLETED, 1
    )

    assert isinstance(result, dict)
    assert result["prescription_id"] == "RX123456"
    assert result["new_status"] == PrescriptionStatus.COMPLETED


@pytest.mark.asyncio
async def test_get_patient_prescriptions(prescription_service):
    """Test getting patient prescriptions."""
    prescriptions = await prescription_service.get_patient_prescriptions("PAT123456")

    assert isinstance(prescriptions, list)


@pytest.mark.asyncio
async def test_check_prescription_adherence(prescription_service):
    """Test prescription adherence checking."""
    adherence = await prescription_service.check_prescription_adherence("RX123456")

    assert isinstance(adherence, dict)
    assert "prescription_id" in adherence
    assert "adherence_score" in adherence
    assert "alerts" in adherence


@pytest.mark.asyncio
async def test_prescription_status_enum():
    """Test prescription status enum values."""
    assert PrescriptionStatus.DRAFT.value == "draft"
    assert PrescriptionStatus.ACTIVE.value == "active"
    assert PrescriptionStatus.COMPLETED.value == "completed"
    assert PrescriptionStatus.CANCELLED.value == "cancelled"
    assert PrescriptionStatus.EXPIRED.value == "expired"


@pytest.mark.asyncio
async def test_interaction_severity_enum():
    """Test interaction severity enum values."""
    assert InteractionSeverity.MINOR.value == "minor"
    assert InteractionSeverity.MODERATE.value == "moderate"
    assert InteractionSeverity.MAJOR.value == "major"
    assert InteractionSeverity.CONTRAINDICATED.value == "contraindicated"


@pytest.mark.asyncio
async def test_empty_medications_handling(prescription_service):
    """Test handling of empty medications list."""
    medications = []

    prescription = await prescription_service.create_prescription(
        "PAT123456", 1, medications
    )

    assert isinstance(prescription, dict)
    assert len(prescription["medications"]) == 0


@pytest.mark.asyncio
async def test_drug_database_initialization(prescription_service):
    """Test drug database initialization."""
    assert hasattr(prescription_service, 'drug_database')
    assert isinstance(prescription_service.drug_database, dict)
    assert "metformin" in prescription_service.drug_database
    assert "lisinopril" in prescription_service.drug_database
    assert "warfarin" in prescription_service.drug_database


@pytest.mark.asyncio
async def test_interaction_rules_initialization(prescription_service):
    """Test interaction rules initialization."""
    assert hasattr(prescription_service, 'interaction_rules')
    assert isinstance(prescription_service.interaction_rules, dict)
    assert "warfarin" in prescription_service.interaction_rules
    assert "metformin" in prescription_service.interaction_rules
