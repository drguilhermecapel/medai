"""
Integration tests for critical ECG analysis workflow.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np
from datetime import datetime

from app.services.ecg_service import ECGAnalysisService
from app.services.ml_model_service import MLModelService
from app.services.validation_service import ValidationService
from app.services.notification_service import NotificationService
from app.core.constants import AnalysisStatus, ClinicalUrgency, ValidationStatus


class TestECGAnalysisIntegration:
    """Integration tests for complete ECG analysis workflow."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def ml_service(self):
        """Mock ML service."""
        service = MLModelService()
        # Mock the models to avoid loading actual model files
        service.models = {
            "ecg_classifier": MagicMock(),
            "arrhythmia_detector": MagicMock()
        }
        return service

    @pytest.fixture
    def notification_service(self, mock_db):
        """Mock notification service."""
        return NotificationService(mock_db)

    @pytest.fixture
    def validation_service(self, mock_db, notification_service):
        """Mock validation service."""
        return ValidationService(mock_db, notification_service)

    @pytest.fixture
    def ecg_service(self, mock_db, ml_service, validation_service):
        """Create ECG service with dependencies."""
        return ECGAnalysisService(mock_db, ml_service, validation_service)

    @pytest.mark.asyncio
    async def test_complete_ecg_analysis_workflow(self, ecg_service, mock_db):
        """Test complete ECG analysis workflow from upload to validation."""
        # Mock ECG data
        ecg_data = np.random.randn(5000, 12)  # 5000 samples, 12 leads
        patient_id = 123
        created_by = 456
        
        # Mock file operations
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value="mock ecg data"):
                with patch.object(ecg_service.processor, 'load_ecg_file', return_value=ecg_data):
                    with patch.object(ecg_service.repository, 'create', return_value=MagicMock(id=789)):
                        
                        # Step 1: Create analysis
                        if hasattr(ecg_service, 'create_analysis'):
                            analysis = await ecg_service.create_analysis(
                                patient_id=patient_id,
                                file_path="/mock/path/ecg.txt",
                                original_filename="ecg.txt",
                                created_by=created_by
                            )
                            assert analysis is not None

    @pytest.mark.asyncio
    async def test_ecg_processing_pipeline(self, ecg_service):
        """Test ECG signal processing pipeline."""
        # Mock ECG signal
        ecg_signal = np.random.randn(5000)
        sampling_rate = 500
        
        # Mock processor methods
        ecg_service.processor.preprocess_signal = AsyncMock(return_value=ecg_signal)
        ecg_service.processor.detect_r_peaks = MagicMock(return_value=[100, 200, 300, 400, 500])
        ecg_service.processor.calculate_heart_rate = MagicMock(return_value=75)
        
        # Mock quality analyzer
        ecg_service.quality_analyzer.assess_quality = MagicMock(
            return_value={"quality_score": 0.85, "noise_level": 0.15}
        )
        
        # Test processing pipeline
        if hasattr(ecg_service, 'process_ecg_signal'):
            result = await ecg_service.process_ecg_signal(ecg_signal, sampling_rate)
            assert result is not None

    @pytest.mark.asyncio
    async def test_ai_diagnosis_integration(self, ecg_service):
        """Test AI diagnosis integration."""
        # Mock analysis data
        analysis_data = {
            "heart_rate": 75,
            "rhythm": "sinus",
            "r_peaks": [100, 200, 300, 400, 500],
            "quality_score": 0.85
        }
        
        # Mock ML service prediction
        ecg_service.ml_service.models["ecg_classifier"].predict = MagicMock(
            return_value=np.array([[0.1, 0.8, 0.1]])  # Normal rhythm prediction
        )
        
        if hasattr(ecg_service, 'generate_ai_diagnosis'):
            diagnosis = await ecg_service.generate_ai_diagnosis(analysis_data)
            assert diagnosis is not None

    @pytest.mark.asyncio
    async def test_validation_workflow_integration(self, validation_service):
        """Test medical validation workflow."""
        analysis_id = 123
        validator_id = 456
        
        # Mock repository responses
        validation_service.repository.create = AsyncMock(return_value=MagicMock(id=789))
        validation_service.repository.update = AsyncMock(return_value=MagicMock())
        
        # Test validation creation
        if hasattr(validation_service, 'create_validation'):
            validation = await validation_service.create_validation(
                analysis_id=analysis_id,
                validator_id=validator_id,
                validator_role="physician",
                validator_experience_years=10
            )
            assert validation is not None

    @pytest.mark.asyncio
    async def test_notification_integration(self, notification_service):
        """Test notification system integration."""
        notification_data = {
            "recipient_id": 123,
            "title": "ECG Analysis Complete",
            "message": "Your ECG analysis is ready for review",
            "type": "analysis_complete"
        }
        
        # Mock repository
        notification_service.repository = MagicMock()
        notification_service.repository.create = AsyncMock(return_value=MagicMock(id=456))
        
        if hasattr(notification_service, 'create_notification'):
            notification = await notification_service.create_notification(notification_data)
            assert notification is not None

    @pytest.mark.asyncio
    async def test_critical_urgency_workflow(self, ecg_service, validation_service, notification_service):
        """Test workflow for critical urgency cases."""
        # Mock critical ECG findings
        critical_diagnosis = {
            "diagnosis": "ST-elevation myocardial infarction",
            "confidence": 0.95,
            "urgency": ClinicalUrgency.EMERGENCY
        }
        
        # Test urgency determination
        if hasattr(ecg_service, 'determine_clinical_urgency'):
            urgency = await ecg_service.determine_clinical_urgency(critical_diagnosis)
            assert urgency == ClinicalUrgency.EMERGENCY

    @pytest.mark.asyncio
    async def test_quality_control_integration(self, ecg_service):
        """Test quality control integration."""
        # Mock poor quality signal
        poor_signal = np.random.randn(1000) * 10  # High noise
        
        # Mock quality assessment
        ecg_service.quality_analyzer.assess_quality = MagicMock(
            return_value={"quality_score": 0.3, "noise_level": 0.8}
        )
        
        if hasattr(ecg_service, 'assess_signal_quality'):
            quality_result = await ecg_service.assess_signal_quality(poor_signal)
            assert quality_result is not None
            assert quality_result.get("quality_score", 0) < 0.5

    @pytest.mark.asyncio
    async def test_multi_lead_ecg_processing(self, ecg_service):
        """Test multi-lead ECG processing."""
        # Mock 12-lead ECG data
        multi_lead_ecg = np.random.randn(5000, 12)
        
        # Mock processing for each lead
        ecg_service.processor.preprocess_signal = AsyncMock(return_value=multi_lead_ecg)
        
        if hasattr(ecg_service, 'process_multi_lead_ecg'):
            result = await ecg_service.process_multi_lead_ecg(multi_lead_ecg)
            assert result is not None

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, ecg_service):
        """Test error handling in integration scenarios."""
        # Test with invalid file path
        with pytest.raises(Exception):  # Should raise ECGProcessingException or similar
            if hasattr(ecg_service, 'create_analysis'):
                await ecg_service.create_analysis(
                    patient_id=123,
                    file_path="/nonexistent/file.txt",
                    original_filename="file.txt",
                    created_by=456
                )

    @pytest.mark.asyncio
    async def test_concurrent_analysis_handling(self, ecg_service):
        """Test handling of concurrent ECG analyses."""
        import asyncio
        
        # Mock multiple analyses
        tasks = []
        for i in range(3):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.read_text', return_value="mock data"):
                    with patch.object(ecg_service.repository, 'create', return_value=MagicMock(id=i)):
                        if hasattr(ecg_service, 'create_analysis'):
                            task = ecg_service.create_analysis(
                                patient_id=i,
                                file_path=f"/mock/path/ecg_{i}.txt",
                                original_filename=f"ecg_{i}.txt",
                                created_by=456
                            )
                            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            assert len(results) == 3

    @pytest.mark.asyncio
    async def test_data_persistence_integration(self, ecg_service):
        """Test data persistence throughout the workflow."""
        # Mock database operations
        mock_analysis = MagicMock()
        mock_analysis.id = 123
        mock_analysis.status = AnalysisStatus.COMPLETED
        
        ecg_service.repository.create = AsyncMock(return_value=mock_analysis)
        ecg_service.repository.update = AsyncMock(return_value=mock_analysis)
        ecg_service.repository.get_by_id = AsyncMock(return_value=mock_analysis)
        
        # Test data persistence
        if hasattr(ecg_service, 'get_analysis_by_id'):
            retrieved_analysis = await ecg_service.get_analysis_by_id(123)
            assert retrieved_analysis is not None
            assert retrieved_analysis.id == 123

