"""Test clinical protocols service."""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from app.services.clinical_protocols_service import (
    ClinicalProtocolsService,
    ProtocolType,
    RiskLevel
)


@pytest.fixture
def protocols_service(test_db):
    """Create clinical protocols service instance."""
    return ClinicalProtocolsService(test_db)


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "age": 65,
        "gender": "male",
        "medical_history": ["hypertension", "diabetes"],
        "risk_factors": ["smoking"]
    }


@pytest.fixture
def sepsis_clinical_data():
    """Sample clinical data for sepsis assessment."""
    return {
        "vital_signs": {
            "systolic_bp": 90,
            "respiratory_rate": 24,
            "altered_mental_status": True,
            "temperature": 101.5
        },
        "lab_results": {
            "lactate": 3.0,
            "white_blood_count": 15000
        }
    }


@pytest.fixture
def chest_pain_clinical_data():
    """Sample clinical data for chest pain assessment."""
    return {
        "symptoms": {
            "chest_pain_type": "typical",
            "duration_hours": 2,
            "radiation": True
        },
        "vital_signs": {
            "heart_rate": 95,
            "blood_pressure": "140/90"
        },
        "risk_factors": ["smoking", "diabetes"]
    }


@pytest.fixture
def stroke_clinical_data():
    """Sample clinical data for stroke assessment."""
    return {
        "symptoms": {
            "face_droop": True,
            "arm_weakness": True,
            "speech_difficulty": True,
            "onset_time": "2 hours ago"
        },
        "vital_signs": {
            "blood_pressure": "180/100"
        }
    }


@pytest.mark.asyncio
async def test_assess_sepsis_protocol(protocols_service, sample_patient_data, sepsis_clinical_data):
    """Test sepsis protocol assessment."""
    assessment = await protocols_service.assess_protocol(
        ProtocolType.SEPSIS, sample_patient_data, sepsis_clinical_data
    )
    
    assert isinstance(assessment, dict)
    assert "protocol_type" in assessment
    assert "risk_level" in assessment
    assert "score" in assessment
    assert "criteria_met" in assessment
    assert "recommendations" in assessment
    assert assessment["protocol_type"] == ProtocolType.SEPSIS.value


@pytest.mark.asyncio
async def test_assess_chest_pain_protocol(protocols_service, sample_patient_data, chest_pain_clinical_data):
    """Test chest pain protocol assessment."""
    assessment = await protocols_service.assess_protocol(
        ProtocolType.CHEST_PAIN, sample_patient_data, chest_pain_clinical_data
    )
    
    assert isinstance(assessment, dict)
    assert "protocol_type" in assessment
    assert "risk_level" in assessment
    assert "score" in assessment
    assert "criteria_met" in assessment
    assert "recommendations" in assessment
    assert assessment["protocol_type"] == ProtocolType.CHEST_PAIN.value


@pytest.mark.asyncio
async def test_assess_stroke_protocol(protocols_service, sample_patient_data, stroke_clinical_data):
    """Test stroke protocol assessment."""
    assessment = await protocols_service.assess_protocol(
        ProtocolType.STROKE, sample_patient_data, stroke_clinical_data
    )
    
    assert isinstance(assessment, dict)
    assert "protocol_type" in assessment
    assert "risk_level" in assessment
    assert "score" in assessment
    assert "criteria_met" in assessment
    assert "recommendations" in assessment
    assert assessment["protocol_type"] == ProtocolType.STROKE.value


@pytest.mark.asyncio
async def test_assess_protocol_generic(protocols_service, sample_patient_data, sepsis_clinical_data):
    """Test generic protocol assessment method."""
    assessment = await protocols_service.assess_protocol(
        ProtocolType.SEPSIS, sample_patient_data, sepsis_clinical_data
    )
    
    assert isinstance(assessment, dict)
    assert "protocol_type" in assessment
    assert assessment["protocol_type"] == ProtocolType.SEPSIS.value


@pytest.mark.asyncio
async def test_get_applicable_protocols(protocols_service, sample_patient_data, sepsis_clinical_data):
    """Test getting applicable protocols."""
    protocols = await protocols_service.get_applicable_protocols(
        sample_patient_data, sepsis_clinical_data
    )
    
    assert isinstance(protocols, list)
    for protocol in protocols:
        assert "protocol_type" in protocol
        assert "risk_level" in protocol


@pytest.mark.asyncio
async def test_protocol_initialization(protocols_service):
    """Test protocol initialization."""
    assert hasattr(protocols_service, 'protocol_definitions')
    assert isinstance(protocols_service.protocol_definitions, dict)
    assert ProtocolType.SEPSIS in protocols_service.protocol_definitions
    assert ProtocolType.CHEST_PAIN in protocols_service.protocol_definitions
    assert ProtocolType.STROKE in protocols_service.protocol_definitions


@pytest.mark.asyncio
async def test_sepsis_assessment_with_high_risk(protocols_service):
    """Test sepsis assessment with high risk indicators."""
    patient_data = {"age": 70, "medical_history": ["diabetes"]}
    clinical_data = {
        "vital_signs": {
            "systolic_blood_pressure": 85,
            "respiratory_rate": 25,
            "temperature": 39.0
        },
        "glasgow_coma_scale": 13,
        "lab_values": {
            "lactate": 3.5,
            "white_blood_cell_count": 16000
        }
    }
    
    assessment = await protocols_service.assess_protocol(
        ProtocolType.SEPSIS, patient_data, clinical_data
    )
    
    assert assessment["applicable"] is True
    assert assessment["risk_level"] in [RiskLevel.HIGH.value, RiskLevel.MODERATE.value]
    assert len(assessment["recommendations"]) > 0


@pytest.mark.asyncio
async def test_chest_pain_assessment_with_risk_factors(protocols_service):
    """Test chest pain assessment with risk factors."""
    patient_data = {"age": 65, "risk_factors": ["smoking", "diabetes", "hypertension"]}
    clinical_data = {
        "ecg_findings": {
            "st_elevation": True
        }
    }
    
    assessment = await protocols_service.assess_protocol(
        ProtocolType.CHEST_PAIN, patient_data, clinical_data
    )
    
    assert assessment["applicable"] is True
    assert assessment["risk_level"] in [RiskLevel.HIGH.value, RiskLevel.MODERATE.value]


@pytest.mark.asyncio
async def test_stroke_assessment_with_symptoms(protocols_service):
    """Test stroke assessment with neurological symptoms."""
    patient_data = {"age": 75}
    clinical_data = {
        "neurological": {
            "facial_droop": True,
            "arm_weakness": True,
            "speech_difficulty": True
        },
        "timing": {
            "symptom_onset": 2.0
        }
    }
    
    assessment = await protocols_service.assess_protocol(
        ProtocolType.STROKE, patient_data, clinical_data
    )
    
    assert assessment["applicable"] is True
    assert assessment["risk_level"] in [RiskLevel.HIGH.value, RiskLevel.MODERATE.value]


@pytest.mark.asyncio
async def test_protocol_type_enum():
    """Test protocol type enum values."""
    assert ProtocolType.SEPSIS.value == "sepsis"
    assert ProtocolType.CHEST_PAIN.value == "chest_pain"
    assert ProtocolType.STROKE.value == "stroke"


@pytest.mark.asyncio
async def test_risk_level_enum():
    """Test risk level enum values."""
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MODERATE.value == "moderate"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.CRITICAL.value == "critical"


@pytest.mark.asyncio
async def test_empty_data_handling(protocols_service):
    """Test handling of empty data."""
    assessment = await protocols_service.assess_protocol(ProtocolType.SEPSIS, {}, {})
    
    assert isinstance(assessment, dict)
    assert "protocol_type" in assessment
    assert "risk_level" in assessment


@pytest.mark.asyncio
async def test_invalid_protocol_type_handling(protocols_service, sample_patient_data, sepsis_clinical_data):
    """Test handling of invalid protocol type."""
    assessment = await protocols_service.assess_protocol(
        "invalid_protocol", sample_patient_data, sepsis_clinical_data
    )
    
    assert "error" in assessment
    assert "Unknown protocol type" in assessment["error"]
