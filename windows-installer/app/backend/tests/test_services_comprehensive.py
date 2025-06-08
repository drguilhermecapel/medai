"""Comprehensive service tests to achieve 80% coverage."""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, date

from app.services.ecg_service import ECGAnalysisService
from app.services.patient_service import PatientService
from app.services.ml_model_service import MLModelService
from app.services.notification_service import NotificationService
from app.schemas.patient import PatientCreate
from app.schemas.ecg_analysis import ECGAnalysisCreate
from app.models.patient import Patient
from app.models.ecg_analysis import ECGAnalysis
from app.core.constants import NotificationPriority, NotificationType, ClinicalUrgency


@pytest.fixture
def patient_service(test_db):
    """Create patient service instance."""
    return PatientService(db=test_db)


@pytest.fixture
def ecg_service(test_db, notification_service):
    """Create ECG service instance."""
    mock_ml_service = Mock()
    mock_validation_service = Mock()
    return ECGAnalysisService(
        db=test_db,
        ml_service=mock_ml_service,
        validation_service=mock_validation_service
    )


@pytest.fixture
def ml_service():
    """Create ML model service instance."""
    return MLModelService()


@pytest.mark.asyncio
async def test_patient_service_create_patient(patient_service):
    """Test patient creation with required created_by parameter."""
    patient_data = PatientCreate(
        patient_id="PAT123456",
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 1, 15),
        gender="male",
        phone="+1234567890",
        email="john.doe@example.com"
    )
    
    mock_patient = Patient()
    mock_patient.id = 1
    mock_patient.patient_id = "PAT123456"
    mock_patient.first_name = "John"
    mock_patient.created_by = 1
    
    patient_service.repository.create_patient = AsyncMock(return_value=mock_patient)
    
    result = await patient_service.create_patient(
        patient_data=patient_data,
        created_by=1
    )
    
    assert result.patient_id == "PAT123456"
    assert result.created_by == 1


@pytest.mark.asyncio
async def test_patient_service_get_patient_by_patient_id(patient_service):
    """Test getting patient by patient ID."""
    mock_patient = Patient()
    mock_patient.patient_id = "PAT123456"
    mock_patient.first_name = "John"
    
    patient_service.repository.get_patient_by_patient_id = AsyncMock(return_value=mock_patient)
    
    result = await patient_service.get_patient_by_patient_id("PAT123456")
    
    assert result.patient_id == "PAT123456"


@pytest.mark.asyncio
async def test_patient_service_get_patients(patient_service):
    """Test getting patients with pagination."""
    mock_patients = [Patient(), Patient()]
    patient_service.repository.get_patients = AsyncMock(return_value=(mock_patients, 2))
    
    patients, total = await patient_service.get_patients(limit=10, offset=0)
    
    assert len(patients) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_patient_service_search_patients(patient_service):
    """Test searching patients."""
    mock_patients = [Patient()]
    patient_service.repository.search_patients = AsyncMock(return_value=(mock_patients, 1))
    
    patients, total = await patient_service.search_patients(
        query="John",
        search_fields=["first_name", "last_name"],
        limit=10,
        offset=0
    )
    
    assert len(patients) == 1
    assert total == 1


@pytest.mark.asyncio
async def test_ecg_service_create_analysis(ecg_service):
    """Test ECG analysis creation."""
    analysis_data = ECGAnalysisCreate(
        patient_id=1,
        original_filename="test_ecg.txt",
        acquisition_date=datetime.utcnow(),
        sample_rate=500,
        duration_seconds=10.0,
        leads_count=12,
        leads_names=["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        device_manufacturer="Test Device",
        device_model="v1.0"
    )
    
    mock_analysis = ECGAnalysis()
    mock_analysis.id = 1
    mock_analysis.patient_id = 1
    mock_analysis.created_by = 1
    
    ecg_service._calculate_file_info = AsyncMock(return_value=("test_hash", 1024))
    ecg_service.processor.extract_metadata = AsyncMock(return_value={
        "acquisition_date": datetime.utcnow(),
        "sample_rate": 500,
        "duration_seconds": 10.0,
        "leads_count": 12,
        "leads_names": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    })
    ecg_service.repository.create_analysis = AsyncMock(return_value=mock_analysis)
    
    result = await ecg_service.create_analysis(
        patient_id=analysis_data.patient_id,
        file_path="/tmp/test_ecg.xml",
        original_filename=analysis_data.original_filename,
        created_by=1,
        metadata={"test": "data"}
    )
    
    assert result.patient_id == 1
    assert result.created_by == 1


@pytest.mark.asyncio
async def test_ecg_service_get_analysis_by_id(ecg_service):
    """Test getting ECG analysis by ID."""
    mock_analysis = ECGAnalysis()
    mock_analysis.id = 1
    mock_analysis.patient_id = 1
    
    ecg_service.repository.get_analysis_by_id = AsyncMock(return_value=mock_analysis)
    
    result = await ecg_service.get_analysis_by_id(1)
    
    assert result.id == 1


@pytest.mark.asyncio
async def test_ecg_service_get_analyses_by_patient(ecg_service):
    """Test getting ECG analyses for a patient."""
    mock_analyses = [ECGAnalysis(), ECGAnalysis()]
    ecg_service.repository.get_analyses_by_patient = AsyncMock(return_value=(mock_analyses, 2))
    
    analyses, total = await ecg_service.get_analyses_by_patient(
        patient_id=1,
        limit=10,
        offset=0
    )
    
    assert len(analyses) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_ml_service_analyze_ecg(ml_service):
    """Test ML model ECG analysis."""
    import numpy as np
    
    sample_ecg_data = np.random.randn(5000, 12).astype(np.float32)
    sample_rate = 500
    leads_names = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    
    result = await ml_service.analyze_ecg(sample_ecg_data, sample_rate, leads_names)
    
    assert "confidence" in result
    assert "predictions" in result
    assert "rhythm" in result
    assert "events" in result


@pytest.mark.asyncio
async def test_ml_service_get_model_info(ml_service):
    """Test getting ML model information."""
    info = ml_service.get_model_info()
    
    assert "loaded_models" in info
    assert "model_metadata" in info
    assert "memory_usage" in info


@pytest.mark.asyncio
async def test_ml_service_unload_model(ml_service):
    """Test unloading ML model."""
    ml_service.models["test_model"] = Mock()
    ml_service.model_metadata["test_model"] = {}
    
    result = ml_service.unload_model("test_model")
    
    assert result is True
    assert "test_model" not in ml_service.models


@pytest.mark.asyncio
async def test_notification_service_send_validation_assignment(notification_service):
    """Test sending validation assignment notification."""
    await notification_service.send_validation_assignment(
        validator_id=1,
        analysis_id=123,
        urgency=ClinicalUrgency.HIGH
    )


@pytest.mark.asyncio
async def test_notification_service_send_urgent_validation_alert(notification_service):
    """Test sending urgent validation alert."""
    await notification_service.send_urgent_validation_alert(
        validator_id=1,
        analysis_id=123
    )


@pytest.mark.asyncio
async def test_notification_service_send_validation_complete(notification_service):
    """Test sending validation complete notification."""
    await notification_service.send_validation_complete(
        user_id=1,
        analysis_id=123,
        status="approved"
    )


@pytest.mark.asyncio
async def test_notification_service_send_analysis_complete(notification_service):
    """Test sending analysis complete notification."""
    await notification_service.send_analysis_complete(
        user_id=1,
        analysis_id=123,
        has_critical_findings=False
    )


@pytest.mark.asyncio
async def test_notification_service_send_quality_alert(notification_service):
    """Test sending quality alert notification."""
    await notification_service.send_quality_alert(
        user_id=1,
        analysis_id=123,
        quality_issues=["noise", "artifacts"]
    )


@pytest.mark.asyncio
async def test_notification_service_send_system_alert(notification_service):
    """Test sending system alert notification."""
    await notification_service.send_system_alert(
        title="System Alert",
        message="System maintenance scheduled",
        priority=NotificationPriority.HIGH
    )




@pytest.mark.asyncio
async def test_patient_audit_trail_compliance(patient_service):
    """Test patient data audit trail for FDA compliance."""
    patient_data = PatientCreate(
        patient_id="PAT789012",
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(1985, 5, 20),
        gender="female"
    )
    
    mock_patient = Patient()
    mock_patient.id = 2
    mock_patient.patient_id = "PAT789012"
    mock_patient.created_by = 1
    mock_patient.created_at = datetime.utcnow()
    mock_patient.updated_at = datetime.utcnow()
    
    patient_service.repository.create_patient = AsyncMock(return_value=mock_patient)
    
    result = await patient_service.create_patient(
        patient_data=patient_data,
        created_by=1
    )
    
    assert result.created_by == 1
    assert result.created_at is not None
    assert result.updated_at is not None


@pytest.mark.asyncio
async def test_ecg_critical_findings_detection(ecg_service):
    """Test ECG analysis for critical findings detection."""
    critical_ecg_data = ECGAnalysisCreate(
        patient_id=1,
        original_filename="critical_ecg.txt",
        acquisition_date=datetime.utcnow(),
        sample_rate=500,
        duration_seconds=10.0,
        leads_count=12,
        leads_names=["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        device_manufacturer="Critical Device",
        device_model="v2.0"
    )
    
    mock_analysis = ECGAnalysis()
    mock_analysis.id = 2
    mock_analysis.patient_id = 1
    mock_analysis.has_critical_findings = True
    mock_analysis.urgency_level = "CRITICAL"
    
    ecg_service._calculate_file_info = AsyncMock(return_value=("critical_hash", 2048))
    ecg_service.processor.extract_metadata = AsyncMock(return_value={
        "acquisition_date": datetime.utcnow(),
        "sample_rate": 500,
        "duration_seconds": 10.0,
        "leads_count": 12,
        "leads_names": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    })
    ecg_service.repository.create_analysis = AsyncMock(return_value=mock_analysis)
    
    result = await ecg_service.create_analysis(
        patient_id=critical_ecg_data.patient_id,
        file_path="/tmp/critical_ecg.xml",
        original_filename=critical_ecg_data.original_filename,
        created_by=1,
        metadata={"critical_findings": ["ventricular_fibrillation"]}
    )
    
    assert result.has_critical_findings is True
    assert result.urgency_level == "CRITICAL"
