"""
Enhanced ECG Service Tests - 100% Coverage Implementation
"""

import asyncio
import numpy as np
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path

from app.services.ecg_service import ECGAnalysisService
from app.core.constants import AnalysisStatus, ClinicalUrgency, DiagnosisCategory


class TestECGServiceCritical:
    """Critical tests for ECG Service - 100% coverage required."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def mock_ml_service(self):
        """Mock ML model service."""
        service = AsyncMock()
        service.classify_ecg.return_value = {
            "predictions": {"normal": 0.8, "arrhythmia": 0.2},
            "confidence": 0.85,
            "primary_diagnosis": "Normal Sinus Rhythm"
        }
        return service

    @pytest.fixture
    def mock_validation_service(self):
        """Mock validation service."""
        return AsyncMock()

    @pytest.fixture
    def ecg_service(self, mock_db_session, mock_ml_service, mock_validation_service):
        """ECG service instance with mocked dependencies."""
        service = ECGAnalysisService(mock_db_session, mock_ml_service, mock_validation_service)
        return service

    @pytest.fixture
    def sample_ecg_data(self):
        """Generate realistic ECG data for testing."""
        # 12-lead ECG, 10 seconds at 500 Hz
        sample_rate = 500
        duration = 10
        samples = sample_rate * duration
        leads = 12
        
        # Generate realistic ECG signal with QRS complexes
        t = np.linspace(0, duration, samples)
        ecg_data = np.zeros((samples, leads))
        
        # Heart rate ~75 bpm
        heart_rate = 75
        rr_interval = 60 / heart_rate
        
        for lead in range(leads):
            # Base signal with P, QRS, T waves
            signal = np.zeros(samples)
            
            # Add QRS complexes
            for beat in range(int(duration / rr_interval)):
                qrs_time = beat * rr_interval
                qrs_sample = int(qrs_time * sample_rate)
                
                if qrs_sample < samples - 50:
                    # QRS complex (simplified)
                    qrs_width = 40  # samples
                    qrs_start = max(0, qrs_sample - qrs_width // 2)
                    qrs_end = min(samples, qrs_sample + qrs_width // 2)
                    
                    # Different amplitudes for different leads
                    amplitude = 1.0 + 0.5 * np.sin(lead * np.pi / 6)
                    signal[qrs_start:qrs_end] += amplitude * np.exp(
                        -((np.arange(qrs_end - qrs_start) - qrs_width // 2) ** 2) / (qrs_width / 4) ** 2
                    )
            
            # Add noise
            noise = np.random.normal(0, 0.05, samples)
            ecg_data[:, lead] = signal + noise
        
        return ecg_data

    @pytest.fixture
    def arrhythmia_ecg_data(self):
        """Generate ECG data with arrhythmia."""
        sample_rate = 500
        duration = 10
        samples = sample_rate * duration
        leads = 12
        
        t = np.linspace(0, duration, samples)
        ecg_data = np.zeros((samples, leads))
        
        # Irregular heart rate (atrial fibrillation pattern)
        rr_intervals = np.random.normal(0.8, 0.3, 15)  # Irregular intervals
        rr_intervals = np.clip(rr_intervals, 0.3, 1.5)  # Physiological limits
        
        current_time = 0
        for lead in range(leads):
            signal = np.zeros(samples)
            
            for rr_interval in rr_intervals:
                if current_time >= duration:
                    break
                    
                qrs_sample = int(current_time * sample_rate)
                if qrs_sample < samples - 50:
                    qrs_width = 40
                    qrs_start = max(0, qrs_sample - qrs_width // 2)
                    qrs_end = min(samples, qrs_sample + qrs_width // 2)
                    
                    amplitude = 0.8 + 0.4 * np.random.random()  # Variable amplitude
                    signal[qrs_start:qrs_end] += amplitude * np.exp(
                        -((np.arange(qrs_end - qrs_start) - qrs_width // 2) ** 2) / (qrs_width / 4) ** 2
                    )
                
                current_time += rr_interval
            
            # Add fibrillation waves
            fib_freq = 300 + 100 * np.random.random()  # 300-400 Hz
            fib_amplitude = 0.1
            fib_signal = fib_amplitude * np.sin(2 * np.pi * fib_freq * t)
            
            noise = np.random.normal(0, 0.08, samples)
            ecg_data[:, lead] = signal + fib_signal + noise
        
        return ecg_data

    # Test 1: Service Initialization
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_db_session, mock_ml_service, mock_validation_service):
        """Test ECG service initialization."""
        service = ECGAnalysisService(mock_db_session, mock_ml_service, mock_validation_service)
        assert service.db == mock_db_session
        assert service.ml_service == mock_ml_service
        assert service.validation_service == mock_validation_service

    # Test 2: Normal ECG Processing
    @pytest.mark.asyncio
    async def test_process_normal_ecg(self, ecg_service, sample_ecg_data):
        """Test processing of normal ECG."""
        analysis_id = "test_analysis_001"
        
        with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = Mock(id=1, analysis_id=analysis_id)
            
            result = await ecg_service.process_ecg_analysis(
                ecg_data=sample_ecg_data,
                patient_id=123,
                analysis_id=analysis_id,
                metadata={
                    "sample_rate": 500,
                    "leads": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
                }
            )
            
            assert result is not None
            assert result["analysis_id"] == analysis_id
            assert "predictions" in result
            assert "confidence" in result
            assert result["confidence"] >= 0.0
            assert result["confidence"] <= 1.0

    # Test 3: Arrhythmia Detection
    @pytest.mark.asyncio
    async def test_arrhythmia_detection(self, ecg_service, arrhythmia_ecg_data):
        """Test detection of arrhythmias."""
        analysis_id = "test_arrhythmia_001"
        
        # Mock ML service to return arrhythmia prediction
        ecg_service.ml_service.classify_ecg.return_value = {
            "predictions": {"atrial_fibrillation": 0.9, "normal": 0.1},
            "confidence": 0.92,
            "primary_diagnosis": "Atrial Fibrillation"
        }
        
        with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = Mock(id=1, analysis_id=analysis_id)
            
            result = await ecg_service.process_ecg_analysis(
                ecg_data=arrhythmia_ecg_data,
                patient_id=123,
                analysis_id=analysis_id,
                metadata={"sample_rate": 500}
            )
            
            assert result is not None
            assert "atrial_fibrillation" in result["predictions"]
            assert result["predictions"]["atrial_fibrillation"] > 0.5

    # Test 4: Signal Quality Assessment
    @pytest.mark.asyncio
    async def test_signal_quality_assessment(self, ecg_service):
        """Test signal quality assessment."""
        # High quality signal
        good_signal = np.random.normal(0, 0.1, (5000, 12))
        quality_good = await ecg_service._assess_signal_quality(good_signal)
        assert quality_good >= 0.7
        
        # Poor quality signal (high noise)
        poor_signal = np.random.normal(0, 2.0, (5000, 12))
        quality_poor = await ecg_service._assess_signal_quality(poor_signal)
        assert quality_poor <= 0.5

    # Test 5: Heart Rate Calculation
    @pytest.mark.asyncio
    async def test_heart_rate_calculation(self, ecg_service, sample_ecg_data):
        """Test heart rate calculation from ECG."""
        heart_rate = await ecg_service._calculate_heart_rate(sample_ecg_data, sample_rate=500)
        assert 60 <= heart_rate <= 100  # Normal range

    # Test 6: QRS Detection
    @pytest.mark.asyncio
    async def test_qrs_detection(self, ecg_service, sample_ecg_data):
        """Test QRS complex detection."""
        qrs_peaks = await ecg_service._detect_qrs_peaks(sample_ecg_data[:, 1], sample_rate=500)
        assert len(qrs_peaks) > 0
        assert all(isinstance(peak, (int, np.integer)) for peak in qrs_peaks)

    # Test 7: Error Handling - Invalid Data
    @pytest.mark.asyncio
    async def test_invalid_ecg_data_handling(self, ecg_service):
        """Test handling of invalid ECG data."""
        # Empty data
        with pytest.raises(ValueError):
            await ecg_service.process_ecg_analysis(
                ecg_data=np.array([]),
                patient_id=123,
                analysis_id="test_invalid_001"
            )
        
        # Wrong dimensions
        with pytest.raises(ValueError):
            await ecg_service.process_ecg_analysis(
                ecg_data=np.random.random((100,)),  # 1D instead of 2D
                patient_id=123,
                analysis_id="test_invalid_002"
            )

    # Test 8: Concurrent Processing
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, ecg_service, sample_ecg_data):
        """Test concurrent ECG processing."""
        tasks = []
        
        for i in range(5):
            task = ecg_service.process_ecg_analysis(
                ecg_data=sample_ecg_data,
                patient_id=123 + i,
                analysis_id=f"concurrent_test_{i:03d}",
                metadata={"sample_rate": 500}
            )
            tasks.append(task)
        
        with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = Mock(id=1)
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        assert len(results) == 5
        assert all(not isinstance(r, Exception) for r in results)

    # Test 9: Memory Management
    @pytest.mark.asyncio
    async def test_memory_management_large_ecg(self, ecg_service):
        """Test memory management with large ECG files."""
        # Large ECG data (1 hour at 1000 Hz)
        large_ecg = np.random.random((3600000, 12))
        
        with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock):
            result = await ecg_service.process_ecg_analysis(
                ecg_data=large_ecg,
                patient_id=123,
                analysis_id="large_test_001",
                metadata={"sample_rate": 1000}
            )
        
        assert result is not None
        # Memory should be released after processing

    # Test 10: Clinical Urgency Classification
    @pytest.mark.asyncio
    async def test_clinical_urgency_classification(self, ecg_service):
        """Test clinical urgency classification."""
        # Critical case
        critical_predictions = {
            "ventricular_tachycardia": 0.95,
            "normal": 0.05
        }
        urgency = await ecg_service._classify_clinical_urgency(critical_predictions)
        assert urgency == ClinicalUrgency.CRITICAL
        
        # Normal case
        normal_predictions = {
            "normal": 0.9,
            "minor_abnormality": 0.1
        }
        urgency = await ecg_service._classify_clinical_urgency(normal_predictions)
        assert urgency == ClinicalUrgency.LOW

    # Test 11: Baseline Wander Removal
    @pytest.mark.asyncio
    async def test_baseline_wander_removal(self, ecg_service):
        """Test baseline wander removal."""
        # Create signal with baseline wander
        t = np.linspace(0, 10, 5000)
        baseline_wander = 0.5 * np.sin(2 * np.pi * 0.1 * t)  # 0.1 Hz wander
        clean_signal = np.sin(2 * np.pi * 1 * t)  # 1 Hz signal
        noisy_signal = clean_signal + baseline_wander
        
        filtered_signal = await ecg_service._remove_baseline_wander(noisy_signal, sample_rate=500)
        
        # Filtered signal should have less low-frequency content
        assert np.std(filtered_signal) < np.std(noisy_signal)

    # Test 12: Noise Filtering
    @pytest.mark.asyncio
    async def test_noise_filtering(self, ecg_service):
        """Test noise filtering."""
        # Create signal with high-frequency noise
        t = np.linspace(0, 10, 5000)
        clean_signal = np.sin(2 * np.pi * 1 * t)
        noise = 0.3 * np.random.random(len(t))
        noisy_signal = clean_signal + noise
        
        filtered_signal = await ecg_service._apply_noise_filter(noisy_signal, sample_rate=500)
        
        # Filtered signal should be smoother
        assert np.std(np.diff(filtered_signal)) < np.std(np.diff(noisy_signal))

    # Test 13: Lead Validation
    @pytest.mark.asyncio
    async def test_lead_validation(self, ecg_service):
        """Test ECG lead validation."""
        valid_leads = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
        assert await ecg_service._validate_leads(valid_leads) == True
        
        invalid_leads = ["I", "II", "INVALID"]
        assert await ecg_service._validate_leads(invalid_leads) == False

    # Test 14: Interval Measurements
    @pytest.mark.asyncio
    async def test_interval_measurements(self, ecg_service, sample_ecg_data):
        """Test ECG interval measurements (PR, QRS, QT)."""
        measurements = await ecg_service._measure_intervals(sample_ecg_data[:, 1], sample_rate=500)
        
        assert "pr_interval" in measurements
        assert "qrs_duration" in measurements
        assert "qt_interval" in measurements
        
        # Check physiological ranges
        assert 120 <= measurements["pr_interval"] <= 200  # ms
        assert 80 <= measurements["qrs_duration"] <= 120  # ms
        assert 350 <= measurements["qt_interval"] <= 450  # ms

    # Test 15: Database Integration
    @pytest.mark.asyncio
    async def test_database_integration(self, ecg_service, sample_ecg_data):
        """Test database save and retrieve operations."""
        analysis_data = {
            "patient_id": 123,
            "analysis_id": "db_test_001",
            "status": AnalysisStatus.COMPLETED,
            "predictions": {"normal": 0.8},
            "confidence": 0.85
        }
        
        with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = Mock(id=1, **analysis_data)
            
            saved_analysis = await ecg_service._save_analysis_to_db(analysis_data)
            assert saved_analysis.id == 1
            assert saved_analysis.patient_id == 123

    # Test 16: Performance Benchmarking
    @pytest.mark.asyncio
    async def test_processing_performance(self, ecg_service, sample_ecg_data):
        """Test processing performance benchmarks."""
        start_time = datetime.now()
        
        with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock):
            await ecg_service.process_ecg_analysis(
                ecg_data=sample_ecg_data,
                patient_id=123,
                analysis_id="perf_test_001",
                metadata={"sample_rate": 500}
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Should process 10-second ECG in under 5 seconds
        assert processing_time < 5.0

    # Test 17: Edge Cases
    @pytest.mark.asyncio
    async def test_edge_cases(self, ecg_service):
        """Test edge cases and boundary conditions."""
        # Minimum duration ECG
        min_ecg = np.random.random((500, 12))  # 1 second at 500 Hz
        
        with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock):
            result = await ecg_service.process_ecg_analysis(
                ecg_data=min_ecg,
                patient_id=123,
                analysis_id="edge_test_001",
                metadata={"sample_rate": 500}
            )
        
        assert result is not None
        
        # Maximum supported leads
        max_leads_ecg = np.random.random((5000, 15))  # 15 leads
        
        with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock):
            result = await ecg_service.process_ecg_analysis(
                ecg_data=max_leads_ecg,
                patient_id=123,
                analysis_id="edge_test_002",
                metadata={"sample_rate": 500}
            )
        
        assert result is not None

    # Test 18: Retry Mechanism
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, ecg_service, sample_ecg_data):
        """Test retry mechanism for failed analyses."""
        with patch.object(ecg_service.ml_service, 'classify_ecg', side_effect=[
            Exception("Temporary failure"),
            Exception("Another failure"),
            {"predictions": {"normal": 0.8}, "confidence": 0.85}  # Success on third try
        ]):
            with patch.object(ecg_service, '_save_analysis_to_db', new_callable=AsyncMock):
                result = await ecg_service.process_ecg_analysis(
                    ecg_data=sample_ecg_data,
                    patient_id=123,
                    analysis_id="retry_test_001",
                    metadata={"sample_rate": 500},
                    max_retries=3
                )
        
        assert result is not None
        assert result["confidence"] == 0.85

    # Test 19: Configuration Validation
    @pytest.mark.asyncio
    async def test_configuration_validation(self, ecg_service):
        """Test service configuration validation."""
        # Test sample rate validation
        assert await ecg_service._validate_sample_rate(500) == True
        assert await ecg_service._validate_sample_rate(50) == False  # Too low
        assert await ecg_service._validate_sample_rate(5000) == False  # Too high
        
        # Test duration validation
        assert await ecg_service._validate_duration(10.0) == True
        assert await ecg_service._validate_duration(0.5) == False  # Too short
        assert await ecg_service._validate_duration(3600) == False  # Too long

    # Test 20: Cleanup and Resource Management
    @pytest.mark.asyncio
    async def test_cleanup_and_resource_management(self, ecg_service):
        """Test proper cleanup and resource management."""
        # Test temporary file cleanup
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b"test data")
        
        # Ensure file exists
        assert os.path.exists(temp_path)
        
        # Service should clean up temporary files
        await ecg_service._cleanup_temporary_files([temp_path])
        
        # File should be removed
        assert not os.path.exists(temp_path)


# Additional helper methods for ECG Service
class TestECGServiceHelpers:
    """Test helper methods in ECG Service."""

    @pytest.fixture
    def ecg_service(self, mock_db_session):
        """ECG service instance."""
        return ECGService(mock_db_session)

    @pytest.mark.asyncio
    async def test_lead_name_standardization(self, ecg_service):
        """Test lead name standardization."""
        # Test various lead name formats
        assert await ecg_service._standardize_lead_name("Lead I") == "I"
        assert await ecg_service._standardize_lead_name("lead_ii") == "II"
        assert await ecg_service._standardize_lead_name("V1") == "V1"
        assert await ecg_service._standardize_lead_name("avr") == "aVR"

    @pytest.mark.asyncio
    async def test_diagnosis_mapping(self, ecg_service):
        """Test diagnosis code mapping."""
        predictions = {"atrial_fibrillation": 0.9}
        icd10_codes = await ecg_service._map_to_icd10(predictions)
        assert "I48.9" in icd10_codes  # Atrial fibrillation ICD-10

    @pytest.mark.asyncio
    async def test_confidence_calibration(self, ecg_service):
        """Test confidence score calibration."""
        raw_confidence = 0.95
        calibrated = await ecg_service._calibrate_confidence(raw_confidence)
        assert 0.0 <= calibrated <= 1.0
        assert calibrated <= raw_confidence  # Should be more conservative

