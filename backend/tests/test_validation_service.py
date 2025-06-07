"""Test Validation Service."""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from app.services.validation_service import ValidationService
from app.models.validation import Validation
from app.models.ecg_analysis import ECGAnalysis
from app.models.patient import Patient
from app.models.user import User
from app.schemas.validation import ValidationCreate, ValidationUpdate
from app.core.constants import ValidationStatus, UserRoles


@pytest.fixture
def validation_service(test_db, notification_service):
    """Create validation service instance."""
    return ValidationService(db=test_db, notification_service=notification_service)


@pytest_asyncio.fixture
async def sample_ecg_analysis(test_db):
    """Create sample ECG analysis."""
    analysis = ECGAnalysis(
        analysis_id="test_analysis_001",
        patient_id=1,
        created_by=1,
        original_filename="test.txt",
        file_path="/tmp/test.txt",
        file_hash="test_hash",
        file_size=1024,
        acquisition_date=datetime.utcnow(),
        sample_rate=500,
        duration_seconds=10.0,
        leads_count=12,
        leads_names=["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        status="completed",
        rhythm="atrial_fibrillation",
        heart_rate_bpm=95,
        signal_quality_score=0.88
    )
    test_db.add(analysis)
    await test_db.commit()
    await test_db.refresh(analysis)
    return analysis


@pytest.fixture
def sample_validation_data():
    """Sample validation data."""
    return {
        "analysis_id": 1,
        "validator_id": 1,
        "notes": "Requires immediate attention"
    }


@pytest.mark.asyncio
async def test_create_validation_success(validation_service, sample_validation_data, test_db):
    """Test successful validation creation."""
    from app.models.ecg_analysis import ECGAnalysis
    from app.models.patient import Patient
    from app.models.user import User
    from datetime import datetime
    
    patient = Patient(
        patient_id="TEST001",
        first_name="Test",
        last_name="Patient",
        date_of_birth=datetime(1990, 1, 1).date(),
        gender="M",
        created_by=1
    )
    test_db.add(patient)
    await test_db.flush()
    
    user = User(
        username="test_doctor",
        email="doctor@test.com",
        first_name="Test",
        last_name="Doctor",
        hashed_password="test_hash",
        role=UserRoles.PHYSICIAN,
        experience_years=5
    )
    test_db.add(user)
    await test_db.flush()
    
    analysis = ECGAnalysis(
        analysis_id="test_analysis_validation_unique_001",
        patient_id=patient.id,
        created_by=user.id,
        original_filename="test.txt",
        file_path="/tmp/test.txt",
        file_hash="test_hash",
        file_size=1024,
        acquisition_date=datetime.utcnow(),
        sample_rate=500,
        duration_seconds=10.0,
        leads_count=12,
        leads_names=["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        status="completed"
    )
    test_db.add(analysis)
    await test_db.commit()
    await test_db.refresh(analysis)
    
    result = await validation_service.create_validation(
        analysis_id=analysis.id,
        validator_id=user.id,
        validator_role=UserRoles.PHYSICIAN,
        validator_experience_years=5
    )
    
    assert result is not None
    assert result.analysis_id == analysis.id
    assert result.validator_id == user.id
    assert result.status == "pending"


@pytest.mark.asyncio
async def test_submit_validation(validation_service, test_db):
    """Test submitting validation results."""
    from app.models.ecg_analysis import ECGAnalysis
    from app.models.patient import Patient
    from app.models.user import User
    from datetime import datetime
    
    patient = Patient(
        patient_id="TEST002",
        first_name="Test",
        last_name="Patient",
        date_of_birth=datetime(1990, 1, 1).date(),
        gender="M",
        created_by=1
    )
    test_db.add(patient)
    await test_db.flush()
    
    user = User(
        username="test_validator",
        email="validator@test.com",
        first_name="Test",
        last_name="Validator",
        hashed_password="test_hash",
        role=UserRoles.PHYSICIAN,
        experience_years=5
    )
    test_db.add(user)
    await test_db.flush()
    
    analysis = ECGAnalysis(
        analysis_id="test_analysis_submit_unique_001",
        patient_id=patient.id,
        created_by=user.id,
        original_filename="test.txt",
        file_path="/tmp/test.txt",
        file_hash="test_hash",
        file_size=1024,
        acquisition_date=datetime.utcnow(),
        sample_rate=500,
        duration_seconds=10.0,
        leads_count=12,
        leads_names=["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        status="completed"
    )
    test_db.add(analysis)
    await test_db.commit()
    await test_db.refresh(analysis)
    
    validation = await validation_service.create_validation(
        analysis_id=analysis.id,
        validator_id=user.id,
        validator_role=UserRoles.PHYSICIAN,
        validator_experience_years=5
    )
    
    validation_data = {
        "approved": True,
        "clinical_notes": "Normal ECG findings",
        "signal_quality_rating": 4,
        "ai_confidence_rating": 5,
        "overall_quality_score": 0.95
    }
    
    result = await validation_service.submit_validation(
        validation_id=validation.id,
        validator_id=user.id,
        validation_data=validation_data
    )
    
    assert result is not None
    assert result.status == ValidationStatus.APPROVED
    assert result.clinical_notes == "Normal ECG findings"


@pytest.mark.asyncio
async def test_create_urgent_validation(validation_service, test_db):
    """Test creating urgent validation."""
    from app.models.ecg_analysis import ECGAnalysis
    from app.models.patient import Patient
    from app.models.user import User
    from datetime import datetime
    
    patient = Patient(
        patient_id="TEST003",
        first_name="Test",
        last_name="Patient",
        date_of_birth=datetime(1990, 1, 1).date(),
        gender="M",
        created_by=1
    )
    test_db.add(patient)
    await test_db.flush()
    
    user = User(
        username="test_urgent_validator",
        email="urgent@test.com",
        first_name="Test",
        last_name="Urgent",
        hashed_password="test_hash",
        role=UserRoles.PHYSICIAN,
        experience_years=10
    )
    test_db.add(user)
    await test_db.flush()
    
    analysis = ECGAnalysis(
        analysis_id="test_analysis_urgent_unique_001",
        patient_id=patient.id,
        created_by=user.id,
        original_filename="urgent.txt",
        file_path="/tmp/urgent.txt",
        file_hash="urgent_hash",
        file_size=1024,
        acquisition_date=datetime.utcnow(),
        sample_rate=500,
        duration_seconds=10.0,
        leads_count=12,
        leads_names=["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        status="completed"
    )
    test_db.add(analysis)
    await test_db.commit()
    await test_db.refresh(analysis)
    
    await validation_service.create_urgent_validation(analysis_id=analysis.id)
    


@pytest.mark.asyncio
async def test_run_automated_validation_rules(validation_service, test_db):
    """Test running automated validation rules."""
    from app.models.ecg_analysis import ECGAnalysis
    from app.models.patient import Patient
    from datetime import datetime
    
    patient = Patient(
        patient_id="TEST004",
        first_name="Test",
        last_name="Patient",
        date_of_birth=datetime(1990, 1, 1).date(),
        gender="M",
        created_by=1
    )
    test_db.add(patient)
    await test_db.flush()
    
    analysis = ECGAnalysis(
        analysis_id="test_analysis_rules_unique_001",
        patient_id=patient.id,
        created_by=1,
        original_filename="rules.txt",
        file_path="/tmp/rules.txt",
        file_hash="rules_hash",
        file_size=1024,
        acquisition_date=datetime.utcnow(),
        sample_rate=500,
        duration_seconds=10.0,
        leads_count=12,
        leads_names=["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        status="completed",
        heart_rate_bpm=180,  # High heart rate for testing
        signal_quality_score=0.95
    )
    test_db.add(analysis)
    await test_db.commit()
    await test_db.refresh(analysis)
    
    results = await validation_service.run_automated_validation_rules(analysis.id)
    
    assert results is not None
    assert isinstance(results, list)
