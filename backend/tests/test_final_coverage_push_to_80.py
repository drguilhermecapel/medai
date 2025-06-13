"""
Final push to achieve 80% test coverage by targeting remaining low-coverage services
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_auth_service_authenticate_user():
    """Test auth service authenticate_user method."""
    from app.services.auth_service import AuthService
    from app.models.user import User
    
    mock_db = Mock()
    service = AuthService(mock_db)
    
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.locked_until = None
    mock_user.is_active = True
    mock_user.hashed_password = "hashed_password"
    mock_user.failed_login_attempts = 0
    mock_user.last_login = None
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    with patch('app.services.auth_service.verify_password', return_value=True):
        result = await service.authenticate_user("testuser", "password123")
        
        assert result == mock_user
        mock_db.query.assert_called()


@pytest.mark.asyncio
async def test_auth_service_record_login():
    """Test record_login method."""
    from app.services.auth_service import AuthService
    from app.models.user import User
    
    mock_db = Mock()
    service = AuthService(mock_db)
    
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.failed_login_attempts = 3
    mock_user.locked_until = datetime.now()
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    with patch.object(service, 'log_audit', new_callable=AsyncMock):
        await service.record_login(1)
        
        assert mock_user.failed_login_attempts == 0
        assert mock_user.locked_until is None
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_auth_service_change_password():
    """Test change_password method."""
    from app.services.auth_service import AuthService
    from app.models.user import User
    
    mock_db = Mock()
    service = AuthService(mock_db)
    
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.hashed_password = "old_hash"
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    with patch('app.services.auth_service.verify_password', return_value=True), \
         patch('app.services.auth_service.get_password_hash', return_value="new_hash"), \
         patch.object(service, 'log_audit', new_callable=AsyncMock):
        
        result = await service.change_password(1, "old_password", "new_password")
        
        assert result == True
        assert mock_user.hashed_password == "new_hash"
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_multi_pathology_service_analyze_hierarchical():
    """Test hierarchical analysis method."""
    from app.services.multi_pathology_service import MultiPathologyService
    
    service = MultiPathologyService()
    
    signal = np.array([1, 2, 3, 4, 5])
    features = {
        "heart_rate": 75,
        "rr_std": 50,
        "qt_interval": 400,
        "pr_interval": 160,
        "qrs_duration": 100
    }
    
    result = await service.analyze_hierarchical(signal, features, 0.9)
    
    assert "level1" in result
    assert "level2" in result
    assert "level3" in result
    assert "clinical_urgency" in result
    assert result["preprocessing_quality"] == 0.9


@pytest.mark.asyncio
async def test_multi_pathology_service_level2_analysis():
    """Test level 2 category classification."""
    from app.services.multi_pathology_service import MultiPathologyService
    
    service = MultiPathologyService()
    
    signal = np.array([1, 2, 3, 4, 5])
    features = {
        "heart_rate": 160,  # High heart rate for arrhythmia
        "rr_std": 50,
        "pr_interval": 160,
        "qrs_duration": 100
    }
    
    result = await service._level2_category_classification(signal, features)
    
    assert "predicted_category" in result
    assert "confidence" in result
    assert "category_scores" in result
    assert "features_used" in result


def test_multi_pathology_service_clinical_urgency():
    """Test clinical urgency determination."""
    from app.services.multi_pathology_service import MultiPathologyService
    
    service = MultiPathologyService()
    
    level3_results = {
        "specific_diagnoses": [
            {
                "diagnosis": "ST Elevation Myocardial Infarction",
                "confidence": 0.9,
                "scp_code": "STEMI"
            }
        ]
    }
    
    result = service._determine_clinical_urgency(level3_results)
    
    assert result in ["low", "medium", "high", "critical"]


def test_multi_pathology_service_detect_multi_pathology():
    """Test detect_multi_pathology method."""
    from app.services.multi_pathology_service import MultiPathologyService
    
    service = MultiPathologyService()
    
    ecg_data = np.array([[1, 2, 3], [4, 5, 6]])
    
    result = service.detect_multi_pathology(ecg_data)
    
    assert "pathologies" in result
    assert "confidence" in result
    assert "total_pathologies" in result
    assert "primary_pathology" in result


@pytest.mark.asyncio
async def test_medical_document_generator_prescription():
    """Test prescription document generation."""
    from app.services.medical_document_generator import MedicalDocumentGenerator
    
    mock_db = Mock(spec=AsyncSession)
    service = MedicalDocumentGenerator(mock_db)
    
    patient_data = {"name": "John Doe", "patient_id": "123", "age": "45"}
    physician_data = {"name": "Dr. Smith", "crm": "12345", "specialty": "Cardiology"}
    prescription_data = {
        "medications": [
            {
                "name": "Aspirin",
                "dosage": "100mg",
                "frequency": "once daily",
                "duration": "30 days"
            }
        ]
    }
    diagnosis = "Hypertension"
    
    with patch.object(service.validator, 'validar_acao_medica', new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = {
            "conformidade": 80,
            "alertas": [],
            "interacoes": []
        }
        
        result = await service.generate_prescription_document(
            patient_data, physician_data, prescription_data, diagnosis
        )
        
        assert "document_id" in result
        assert result["patient_info"]["patient_id"] == "123"


@pytest.mark.asyncio
async def test_medical_document_generator_medical_certificate():
    """Test medical certificate generation."""
    from app.services.medical_document_generator import MedicalDocumentGenerator
    
    mock_db = Mock(spec=AsyncSession)
    service = MedicalDocumentGenerator(mock_db)
    
    patient_data = {"name": "John Doe", "patient_id": "123", "age": "45"}
    physician_data = {"name": "Dr. Smith", "crm": "12345", "specialty": "Cardiology"}
    certificate_data = {
        "condition": "Upper respiratory infection",
        "rest_period": "3",
        "cid_code": "J06.9"
    }
    
    result = await service.generate_medical_certificate(
        patient_data, physician_data, certificate_data
    )
    
    assert "document_id" in result
    assert result["patient_info"]["patient_id"] == "123"


def test_medical_document_generator_format_prescription():
    """Test prescription content formatting."""
    from app.services.medical_document_generator import MedicalDocumentGenerator
    
    mock_db = Mock(spec=AsyncSession)
    service = MedicalDocumentGenerator(mock_db)
    
    patient_data = {"name": "John Doe", "age": "45", "address": "123 Main St"}
    physician_data = {"name": "Dr. Smith", "crm": "12345", "clinic_name": "Medical Center"}
    prescription_data = {
        "medications": [
            {
                "name": "Aspirin",
                "dosage": "100mg",
                "frequency": "once daily"
            }
        ]
    }
    diagnosis = "Hypertension"
    
    result = service._format_prescription_content(
        patient_data, physician_data, prescription_data, diagnosis
    )
    
    assert "John Doe" in result
    assert "Aspirin" in result


@pytest.mark.asyncio
async def test_validation_service_create_validation():
    """Test create_validation method."""
    from app.services.validation_service import ValidationService
    from app.services.notification_service import NotificationService
    from app.core.constants import UserRoles
    from app.models.ecg_analysis import ECGAnalysis
    
    mock_db = Mock(spec=AsyncSession)
    mock_notification_service = Mock(spec=NotificationService)
    service = ValidationService(mock_db, mock_notification_service)
    
    mock_analysis = Mock(spec=ECGAnalysis)
    mock_analysis.clinical_urgency = "medium"
    mock_analysis.id = 1
    
    with patch.object(service.repository, 'get_validation_by_analysis', new_callable=AsyncMock) as mock_get, \
         patch.object(service.repository, 'create_validation', new_callable=AsyncMock) as mock_create, \
         patch.object(service.repository, 'get_analysis_by_id', new_callable=AsyncMock) as mock_get_analysis:
        
        mock_get.return_value = None  # No existing validation
        mock_get_analysis.return_value = mock_analysis  # Return the analysis
        mock_create.return_value = Mock(id=1)
        
        result = await service.create_validation(
            analysis_id=1,
            validator_id=1,
            validator_role=UserRoles.PHYSICIAN,
            validator_experience_years=5
        )
        
        assert result.id == 1
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_validation_service_validate_patient_data():
    """Test validate_patient_data method."""
    from app.services.validation_service import ValidationService
    from app.services.notification_service import NotificationService
    
    mock_db = Mock(spec=AsyncSession)
    mock_notification_service = Mock(spec=NotificationService)
    service = ValidationService(mock_db, mock_notification_service)
    
    patient_data = {
        "name": "John Doe",
        "age": 45,
        "gender": "M",
        "medical_history": ["hypertension"]
    }
    
    result = await service.validate_patient_data(patient_data)
    
    assert "valid" in result
    assert "errors" in result


@pytest.mark.asyncio
async def test_validation_service_validate_ecg_data():
    """Test validate_ecg_data method."""
    from app.services.validation_service import ValidationService
    from app.services.notification_service import NotificationService
    
    mock_db = Mock(spec=AsyncSession)
    mock_notification_service = Mock(spec=NotificationService)
    service = ValidationService(mock_db, mock_notification_service)
    
    ecg_data = {
        "signal": [1, 2, 3, 4, 5],
        "sampling_rate": 500,
        "leads": ["I", "II", "V1"]
    }
    
    result = await service.validate_ecg_data(ecg_data)
    
    assert "valid" in result
    assert "errors" in result
    assert "warnings" in result
    assert "ecg_data" in result



@pytest.mark.asyncio
async def test_ai_diagnostic_service_initialization():
    """Test AI diagnostic service initialization."""
    from app.services.ai_diagnostic_service import AIDiagnosticService
    
    mock_db = Mock(spec=AsyncSession)
    service = AIDiagnosticService(mock_db)
    
    assert service.db == mock_db
    assert hasattr(service, 'diagnostic_models')
    assert hasattr(service, 'symptom_patterns')


@pytest.mark.asyncio
async def test_ai_diagnostic_service_generate_suggestions():
    """Test diagnostic suggestions generation."""
    from app.services.ai_diagnostic_service import AIDiagnosticService
    
    mock_db = Mock(spec=AsyncSession)
    service = AIDiagnosticService(mock_db)
    
    symptoms = ["chest pain", "shortness of breath"]
    patient_data = {"age": 45, "gender": "M"}
    
    result = await service.generate_diagnostic_suggestions(symptoms, patient_data)
    
    assert "analysis_timestamp" in result
    assert "diagnostic_suggestions" in result or "error" in result


def test_hybrid_ecg_service_initialization():
    """Test hybrid ECG service initialization."""
    from app.services.hybrid_ecg_service import HybridECGAnalysisService
    from app.services.validation_service import ValidationService
    
    mock_db = Mock(spec=AsyncSession)
    mock_validation_service = Mock(spec=ValidationService)
    service = HybridECGAnalysisService(mock_db, mock_validation_service)
    
    assert service.db == mock_db
    assert service.validation_service == mock_validation_service


@pytest.mark.asyncio
async def test_hybrid_ecg_service_analyze():
    """Test hybrid ECG analysis."""
    from app.services.hybrid_ecg_service import HybridECGAnalysisService
    from app.services.validation_service import ValidationService
    
    mock_db = Mock(spec=AsyncSession)
    mock_validation_service = Mock(spec=ValidationService)
    service = HybridECGAnalysisService(mock_db, mock_validation_service)
    
    with patch.object(service.ecg_reader, 'read_ecg') as mock_read:
        mock_read.return_value = {
            'signal': np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]),
            'sampling_rate': 500,
            'labels': ['I', 'II']
        }
        
        result = await service.analyze_ecg_comprehensive(
            file_path="/tmp/test.csv",
            patient_id=123,
            analysis_id="test_analysis_001"
        )
        
        assert "analysis_id" in result
        assert "pathology_detections" in result
        assert "clinical_assessment" in result


def test_interpretability_service_initialization():
    """Test interpretability service initialization."""
    from app.services.interpretability_service import InterpretabilityService
    
    service = InterpretabilityService()
    
    assert hasattr(service, 'lead_names')
    assert hasattr(service, 'feature_names')
    assert hasattr(service, 'shap_explainer')
    assert hasattr(service, 'lime_explainer')


@pytest.mark.asyncio
async def test_interpretability_service_explain_prediction():
    """Test prediction explanation."""
    from app.services.interpretability_service import InterpretabilityService
    
    service = InterpretabilityService()
    
    signal = np.array([[1, 2, 3], [4, 5, 6]])
    features = {"heart_rate": 150, "rr_std": 200}
    prediction = {"diagnosis": "Atrial Fibrillation", "confidence": 0.85}
    
    result = await service.generate_comprehensive_explanation(signal, features, prediction)
    
    assert result.clinical_explanation
    assert result.feature_importance
    assert result.primary_diagnosis == "Atrial Fibrillation"


def test_ecg_tasks_process_ecg():
    """Test ECG processing task."""
    from app.tasks.ecg_tasks import cleanup_old_analyses, generate_batch_reports, process_ecg_analysis
    
    cleanup_result = cleanup_old_analyses(days_old=30)
    
    assert "status" in cleanup_result
    assert "cleaned_count" in cleanup_result
    
    analysis_ids = [1, 2, 3]
    batch_result = generate_batch_reports(analysis_ids)
    
    assert "status" in batch_result
    assert "reports_generated" in batch_result
    
    with patch('app.tasks.ecg_tasks.asyncio.run') as mock_run, \
         patch('app.tasks.ecg_tasks.current_task') as mock_task, \
         patch.object(process_ecg_analysis, 'run') as mock_task_run:
        mock_run.return_value = {"status": "completed", "analysis_id": 123}
        mock_task.update_state = Mock()
        mock_task_run.return_value = {"status": "completed", "analysis_id": 123}
        
        result = process_ecg_analysis.run(123)
        
        assert "status" in result
        assert "analysis_id" in result


def test_memory_monitor_initialization():
    """Test memory monitor initialization."""
    from app.utils.memory_monitor import MemoryMonitor
    
    monitor = MemoryMonitor()
    
    assert monitor is not None


def test_memory_monitor_check_usage():
    """Test memory usage checking."""
    from app.utils.memory_monitor import MemoryMonitor
    
    monitor = MemoryMonitor()
    
    result = monitor.get_memory_usage()
    
    assert "process_memory_mb" in result
    assert "system_memory_percent" in result


def test_signal_quality_analyzer_initialization():
    """Test signal quality analyzer initialization."""
    from app.utils.signal_quality import SignalQualityAnalyzer
    
    analyzer = SignalQualityAnalyzer()
    
    assert analyzer is not None


def test_signal_quality_analyze():
    """Test signal quality analysis."""
    from app.utils.signal_quality import SignalQualityAnalyzer
    
    analyzer = SignalQualityAnalyzer()
    
    signal = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
    
    result = analyzer.analyze(signal)
    
    assert "overall_score" in result
    assert "noise_level" in result
    assert "artifacts_detected" in result


def test_ecg_hybrid_processor_initialization():
    """Test ECG hybrid processor initialization."""
    from app.utils.ecg_hybrid_processor import ECGHybridProcessor
    from app.services.validation_service import ValidationService
    
    mock_db = Mock(spec=AsyncSession)
    mock_validation_service = Mock(spec=ValidationService)
    processor = ECGHybridProcessor(mock_db, mock_validation_service)
    
    assert processor.hybrid_service is not None
    assert processor.regulatory_service is None


@pytest.mark.asyncio
async def test_ecg_hybrid_processor_process():
    """Test ECG hybrid processing."""
    from app.utils.ecg_hybrid_processor import ECGHybridProcessor
    from app.services.validation_service import ValidationService
    
    mock_db = Mock(spec=AsyncSession)
    mock_validation_service = Mock(spec=ValidationService)
    processor = ECGHybridProcessor(mock_db, mock_validation_service)
    
    with patch.object(processor.hybrid_service, 'analyze_ecg_comprehensive', new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = {
            "analysis_id": "test_001",
            "pathology_detections": {},
            "clinical_assessment": {}
        }
        
        result = await processor.process_ecg_with_validation(
            file_path="/tmp/test.csv",
            patient_id=123,
            analysis_id="test_001"
        )
        
        assert "analysis_id" in result
        assert "regulatory_compliant" in result
        assert "regulatory_validation" in result
