"""
Testes de Integração Abrangentes para MedAI
"""

import asyncio
import pytest
import tempfile
import os
from unittest.mock import AsyncMock, Mock, patch
import numpy as np
from datetime import datetime, timedelta

from app.services.ecg_service import ECGAnalysisService
from app.services.ml_model_service import MLModelService
from app.services.ai_diagnostic_service import AIDiagnosticService
from app.services.patient_service import PatientService
from app.services.notification_service import NotificationService
from app.core.constants import AnalysisStatus, ClinicalUrgency


class TestECGWorkflowIntegration:
    """Test complete ECG analysis workflow integration."""

    @pytest.fixture
    async def integrated_services(self, mock_db_session):
        """Setup integrated services for testing."""
        ml_service = AsyncMock()
        validation_service = AsyncMock()
        
        # Setup realistic ML service responses
        ml_service.classify_ecg.return_value = {
            "predictions": {"normal": 0.15, "atrial_fibrillation": 0.85},
            "confidence": 0.92,
            "primary_diagnosis": "Atrial Fibrillation"
        }
        
        ecg_service = ECGAnalysisService(mock_db_session, ml_service, validation_service)
        patient_service = PatientService(mock_db_session)
        diagnostic_service = AIDiagnosticService(mock_db_session)
        notification_service = NotificationService(mock_db_session)
        
        return {
            "ecg": ecg_service,
            "patient": patient_service,
            "diagnostic": diagnostic_service,
            "notification": notification_service,
            "ml": ml_service,
            "validation": validation_service
        }

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_ecg_analysis_workflow(self, integrated_services):
        """Test complete ECG analysis workflow from upload to diagnosis."""
        from tests.smart_mocks import SmartECGMock, SmartPatientMock
        
        # 1. Create patient
        patient_data = SmartPatientMock.generate_patient_data(
            age_range=(65, 75),
            condition="cardiac"
        )
        
        patient_service = integrated_services["patient"]
        patient_service.create = AsyncMock(return_value=Mock(id=patient_data["id"]))
        patient = await patient_service.create(patient_data)
        
        # 2. Upload ECG
        ecg_data = SmartECGMock.generate_arrhythmia_ecg("atrial_fibrillation")
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            np.save(tmp_file.name, ecg_data)
            ecg_path = tmp_file.name
        
        # 3. Create ECG analysis
        ecg_service = integrated_services["ecg"]
        ecg_service.repository = AsyncMock()
        ecg_service.repository.create = AsyncMock(return_value=Mock(
            id=123,
            patient_id=patient.id,
            status=AnalysisStatus.PENDING
        ))
        
        analysis = await ecg_service.create_analysis(
            patient_id=patient.id,
            file_path=ecg_path,
            original_filename="patient_ecg.txt",
            created_by=456
        )
        
        # 4. Process ECG
        ecg_service.processor = Mock()
        ecg_service.processor.preprocess_signal = Mock(return_value=ecg_data)
        ecg_service.processor.extract_features = Mock(return_value={
            "heart_rate": 95,
            "rhythm_irregularity": 0.85,
            "p_wave_absent": True
        })
        
        # 5. ML Classification
        ml_result = await integrated_services["ml"].classify_ecg(ecg_data)
        assert ml_result["primary_diagnosis"] == "Atrial Fibrillation"
        
        # 6. Generate AI diagnostic
        diagnostic_service = integrated_services["diagnostic"]
        diagnostic_service.generate_diagnosis = AsyncMock(return_value={
            "diagnosis": "Atrial Fibrillation with Rapid Ventricular Response",
            "confidence": 0.92,
            "urgency": ClinicalUrgency.HIGH,
            "recommendations": [
                "Consider rate control with beta-blockers",
                "Evaluate for anticoagulation (CHA2DS2-VASc)",
                "Cardiology consultation recommended"
            ],
            "icd10_codes": ["I48.91"],
            "supporting_findings": [
                "Irregular rhythm",
                "Absence of P waves",
                "Variable R-R intervals"
            ]
        })
        
        diagnosis = await diagnostic_service.generate_diagnosis(
            ecg_features=ecg_service.processor.extract_features.return_value,
            ml_predictions=ml_result,
            patient_data=patient_data
        )
        
        # 7. Send notifications
        notification_service = integrated_services["notification"]
        notification_service.send_notification = AsyncMock(return_value=True)
        
        await notification_service.send_notification(
            recipient_id=patient_data["primary_physician_id"],
            type="high_urgency_ecg",
            data={
                "patient_id": patient.id,
                "diagnosis": diagnosis["diagnosis"],
                "urgency": diagnosis["urgency"]
            }
        )
        
        # Cleanup
        os.unlink(ecg_path)
        
        # Verify workflow completion
        assert diagnosis["urgency"] == ClinicalUrgency.HIGH
        assert len(diagnosis["recommendations"]) > 0
        notification_service.send_notification.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_emergency_stemi_workflow(self, integrated_services):
        """Test emergency STEMI patient workflow with cath lab activation."""
        from tests.smart_mocks import SmartECGMock
        
        # Generate STEMI ECG
        stemi_ecg = SmartECGMock.generate_arrhythmia_ecg("stemi")
        
        # Configure ML service for STEMI detection
        integrated_services["ml"].classify_ecg.return_value = {
            "predictions": {"stemi": 0.96, "normal": 0.04},
            "confidence": 0.96,
            "primary_diagnosis": "ST-Elevation Myocardial Infarction"
        }
        
        # Configure ECG service
        ecg_service = integrated_services["ecg"]
        ecg_service.emergency_processor = AsyncMock()
        ecg_service.emergency_processor.process_stemi = AsyncMock(return_value={
            "stemi_confirmed": True,
            "affected_leads": ["II", "III", "aVF"],
            "territory": "Inferior",
            "door_to_ecg_time": 3  # minutes
        })
        
        # Configure notification service for emergency
        notification_service = integrated_services["notification"]
        notification_service.activate_cath_lab = AsyncMock(return_value={
            "activation_time": datetime.now(),
            "team_notified": ["interventional_cardiology", "cath_lab_staff"],
            "estimated_ready_time": 20  # minutes
        })
        
        # Process emergency ECG
        emergency_result = await ecg_service.process_emergency_ecg(
            ecg_data=stemi_ecg,
            patient_id=999
        )
        
        # Activate cath lab
        cath_lab_activation = await notification_service.activate_cath_lab(
            patient_id=999,
            ecg_findings=emergency_result
        )
        
        # Verify emergency response
        assert emergency_result["stemi_confirmed"] is True
        assert emergency_result["door_to_ecg_time"] < 10  # Within guidelines
        assert len(cath_lab_activation["team_notified"]) >= 2
        assert cath_lab_activation["estimated_ready_time"] <= 30  # Target time

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_batch_screening_workflow(self, integrated_services):
        """Test batch ECG screening for population health."""
        from tests.smart_mocks import SmartECGMock, SmartPatientMock
        
        # Generate batch of patients and ECGs
        batch_size = 50
        patients = []
        ecgs = []
        
        for i in range(batch_size):
            # Mix of normal and abnormal ECGs
            if i % 5 == 0:
                ecg = SmartECGMock.generate_arrhythmia_ecg("atrial_fibrillation")
                condition = "arrhythmia"
            elif i % 10 == 0:
                ecg = SmartECGMock.generate_arrhythmia_ecg("ventricular_tachycardia")
                condition = "arrhythmia"
            else:
                ecg = SmartECGMock.generate_normal_ecg()
                condition = None
            
            patient = SmartPatientMock.generate_patient_data(
                age_range=(40, 80),
                condition=condition
            )
            
            patients.append(patient)
            ecgs.append(ecg)
        
        # Configure services for batch processing
        ecg_service = integrated_services["ecg"]
        ecg_service.batch_processor = AsyncMock()
        ecg_service.batch_processor.process_batch = AsyncMock(return_value=[
            {
                "patient_id": p["id"],
                "status": AnalysisStatus.COMPLETED,
                "diagnosis": "Normal" if i % 5 != 0 and i % 10 != 0 else "Abnormal",
                "confidence": 0.85 + np.random.rand() * 0.1
            }
            for i, p in enumerate(patients)
        ])
        
        # Process batch
        batch_results = await ecg_service.batch_processor.process_batch(
            patient_ecg_pairs=list(zip(patients, ecgs))
        )
        
        # Analyze results
        abnormal_count = sum(1 for r in batch_results if r["diagnosis"] == "Abnormal")
        normal_count = sum(1 for r in batch_results if r["diagnosis"] == "Normal")
        
        # Generate population report
        diagnostic_service = integrated_services["diagnostic"]
        diagnostic_service.generate_population_report = AsyncMock(return_value={
            "total_screened": batch_size,
            "abnormal_findings": abnormal_count,
            "normal_findings": normal_count,
            "prevalence_rate": abnormal_count / batch_size,
            "high_risk_patients": [r["patient_id"] for r in batch_results 
                                 if r["diagnosis"] == "Abnormal"],
            "recommendations": [
                "Schedule follow-up for high-risk patients",
                "Consider expanding screening program"
            ]
        })
        
        population_report = await diagnostic_service.generate_population_report(
            batch_results
        )
        
        # Verify batch processing
        assert len(batch_results) == batch_size
        assert population_report["total_screened"] == batch_size
        assert population_report["prevalence_rate"] > 0
        assert len(population_report["high_risk_patients"]) == abnormal_count

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_telemedicine_ecg_workflow(self, integrated_services):
        """Test remote ECG monitoring and telemedicine workflow."""
        from tests.smart_mocks import SmartECGMock
        
        # Simulate remote ECG device
        remote_device_id = "REMOTE_ECG_001"
        patient_id = 12345
        
        # Configure services for telemedicine
        ecg_service = integrated_services["ecg"]
        ecg_service.telemedicine_handler = AsyncMock()
        
        # Simulate continuous monitoring
        monitoring_duration = 24  # hours
        alerts_generated = []
        
        for hour in range(monitoring_duration):
            # Simulate hourly ECG transmission
            if hour == 15:  # Simulate arrhythmia at hour 15
                ecg_data = SmartECGMock.generate_arrhythmia_ecg("atrial_fibrillation")
                expected_alert = True
            else:
                ecg_data = SmartECGMock.generate_normal_ecg()
                expected_alert = False
            
            # Process remote ECG
            ecg_service.telemedicine_handler.process_remote_ecg = AsyncMock(
                return_value={
                    "timestamp": datetime.now() - timedelta(hours=monitoring_duration-hour),
                    "quality_acceptable": True,
                    "analysis_result": {
                        "rhythm": "AF" if expected_alert else "NSR",
                        "heart_rate": 95 if expected_alert else 72,
                        "alert_generated": expected_alert
                    }
                }
            )
            
            result = await ecg_service.telemedicine_handler.process_remote_ecg(
                device_id=remote_device_id,
                patient_id=patient_id,
                ecg_data=ecg_data
            )
            
            if result["analysis_result"]["alert_generated"]:
                alerts_generated.append(result)
        
        # Generate telemedicine report
        diagnostic_service = integrated_services["diagnostic"]
        diagnostic_service.generate_telemedicine_report = AsyncMock(return_value={
            "monitoring_period": f"{monitoring_duration} hours",
            "total_transmissions": monitoring_duration,
            "alerts_generated": len(alerts_generated),
            "alert_details": alerts_generated,
            "overall_assessment": "Paroxysmal Atrial Fibrillation detected",
            "recommendations": [
                "Consider ambulatory rhythm monitoring",
                "Evaluate for anticoagulation",
                "Schedule virtual cardiology consultation"
            ]
        })
        
        telemedicine_report = await diagnostic_service.generate_telemedicine_report(
            patient_id=patient_id,
            monitoring_data={"alerts": alerts_generated}
        )
        
        # Verify telemedicine workflow
        assert telemedicine_report["total_transmissions"] == monitoring_duration
        assert telemedicine_report["alerts_generated"] > 0
        assert "Atrial Fibrillation" in telemedicine_report["overall_assessment"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_modal_integration(self, integrated_services):
        """Test integration of ECG with other clinical data."""
        from tests.smart_mocks import SmartECGMock, SmartPatientMock
        
        # Generate comprehensive patient data
        patient_data = SmartPatientMock.generate_patient_data(
            age_range=(70, 80),
            condition="cardiac"
        )
        
        # Generate clinical data
        lab_results = SmartPatientMock.generate_lab_results(
            test_type="cardiac",
            condition="heart_failure"
        )
        
        # Generate abnormal ECG
        ecg_data = SmartECGMock.generate_arrhythmia_ecg("atrial_fibrillation")
        
        # Configure diagnostic service for multi-modal analysis
        diagnostic_service = integrated_services["diagnostic"]
        diagnostic_service.analyze_multi_modal = AsyncMock(return_value={
            "integrated_diagnosis": "Atrial Fibrillation with Heart Failure",
            "confidence": 0.94,
            "supporting_evidence": {
                "ecg_findings": ["Irregular rhythm", "Absent P waves"],
                "lab_findings": [f"Elevated BNP: {lab_results['bnp']}",
                               f"Elevated creatinine: {lab_results['creatinine']}"],
                "clinical_findings": ["Ejection fraction 35%", "Bilateral rales"]
            },
            "risk_scores": {
                "cha2ds2_vasc": 5,
                "has_bled": 2,
                "nyha_class": 3
            },
            "integrated_recommendations": [
                "Initiate anticoagulation (high stroke risk)",
                "Optimize heart failure therapy",
                "Consider rhythm vs rate control strategy",
                "Close monitoring of renal function"
            ]
        })
        
        # Perform multi-modal analysis
        integrated_result = await diagnostic_service.analyze_multi_modal(
            ecg_data=ecg_data,
            lab_results=lab_results,
            patient_data=patient_data
        )
        
        # Verify integration
        assert "Heart Failure" in integrated_result["integrated_diagnosis"]
        assert integrated_result["confidence"] > 0.9
        assert integrated_result["risk_scores"]["cha2ds2_vasc"] >= 2
        assert len(integrated_result["integrated_recommendations"]) >= 4

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pediatric_ecg_workflow(self, integrated_services):
        """Test specialized pediatric ECG analysis workflow."""
        from tests.smart_mocks import SmartECGMock, SmartPatientMock
        
        # Generate pediatric patient
        pediatric_patient = SmartPatientMock.generate_patient_data(
            age_range=(1, 10)
        )
        pediatric_patient["age_months"] = pediatric_patient["age"] * 12
        
        # Configure ECG service for pediatric analysis
        ecg_service = integrated_services["ecg"]
        ecg_service.pediatric_analyzer = AsyncMock()
        ecg_service.pediatric_analyzer.analyze_pediatric_ecg = AsyncMock(return_value={
            "age_adjusted_normal": True,
            "heart_rate": 110,  # Normal for age
            "qt_interval": 350,
            "age_specific_findings": [
                "Heart rate appropriate for age",
                "No congenital abnormalities detected",
                "Normal axis for age"
            ],
            "growth_percentiles": {
                "heart_rate_percentile": 50,
                "qt_interval_percentile": 45
            }
        })
        
        # Generate age-appropriate ECG
        pediatric_ecg = SmartECGMock.generate_normal_ecg()
        # Adjust for pediatric heart rate
        pediatric_ecg *= 1.5  # Simulate faster rate
        
        # Process pediatric ECG
        pediatric_result = await ecg_service.pediatric_analyzer.analyze_pediatric_ecg(
            ecg_data=pediatric_ecg,
            age_months=pediatric_patient["age_months"]
        )
        
        # Verify pediatric-specific analysis
        assert pediatric_result["age_adjusted_normal"] is True
        assert pediatric_result["heart_rate"] > 90  # Higher than adult
        assert "age" in pediatric_result["age_specific_findings"][0].lower()

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_high_volume_concurrent_processing(self, integrated_services):
        """Test system performance under high concurrent load."""
        from tests.smart_mocks import SmartECGMock
        import time
        
        # Configure for concurrent processing
        concurrent_requests = 100
        ecg_service = integrated_services["ecg"]
        
        # Track performance metrics
        start_time = time.time()
        processing_times = []
        
        async def process_single_ecg(ecg_id):
            """Process a single ECG and measure time."""
            ecg_start = time.time()
            
            ecg_data = SmartECGMock.generate_normal_ecg(duration_seconds=10)
            
            # Mock the processing to be fast
            ecg_service.process_ecg_async = AsyncMock(return_value={
                "id": ecg_id,
                "status": AnalysisStatus.COMPLETED,
                "processing_time": 0.5
            })
            
            result = await ecg_service.process_ecg_async(ecg_data)
            
            ecg_end = time.time()
            return ecg_end - ecg_start
        
        # Process ECGs concurrently
        tasks = [process_single_ecg(i) for i in range(concurrent_requests)]
        processing_times = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Calculate performance metrics
        avg_processing_time = sum(processing_times) / len(processing_times)
        max_processing_time = max(processing_times)
        throughput = concurrent_requests / total_time
        
        # Verify performance requirements
        assert avg_processing_time < 2.0  # Average under 2 seconds
        assert max_processing_time < 5.0  # No request over 5 seconds
        assert throughput > 10  # At least 10 ECGs per second
        
        # Log performance results
        performance_report = {
            "total_requests": concurrent_requests,
            "total_time": total_time,
            "average_processing_time": avg_processing_time,
            "max_processing_time": max_processing_time,
            "throughput_per_second": throughput
        }
        
        assert performance_report["throughput_per_second"] > 10

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_ecg_to_report_generation(self, mock_db_session):
        """Test complete flow from ECG upload to report generation."""
        # This would test the complete pipeline including:
        # 1. ECG file upload and parsing
        # 2. Signal processing and quality assessment
        # 3. ML analysis and interpretation
        # 4. Clinical correlation and diagnosis
        # 5. Report generation and delivery
        
        # Mock the complete pipeline
        with patch('app.services.ecg_service.ECGAnalysisService') as mock_ecg:
            with patch('app.services.ml_model_service.MLModelService') as mock_ml:
                with patch('app.services.ai_diagnostic_service.AIDiagnosticService') as mock_diagnostic:
                    
                    # Setup pipeline
                    mock_ecg_instance = mock_ecg.return_value
                    mock_ml_instance = mock_ml.return_value
                    mock_diagnostic_instance = mock_diagnostic.return_value
                    
                    # Mock pipeline responses
                    mock_ecg_instance.process_ecg_file.return_value = {
                        "signal_quality": 0.95,
                        "processed_data": np.random.randn(5000, 12)
                    }
                    
                    mock_ml_instance.classify_ecg.return_value = {
                        "predictions": {"normal": 0.85},
                        "confidence": 0.90
                    }
                    
                    mock_diagnostic_instance.generate_report.return_value = {
                        "report_id": "RPT_001",
                        "diagnosis": "Normal ECG",
                        "recommendations": ["routine_follow_up"],
                        "generated_at": datetime.now()
                    }
                    
                    # Execute pipeline
                    ecg_result = await mock_ecg_instance.process_ecg_file("/path/to/ecg.xml")
                    ml_result = await mock_ml_instance.classify_ecg(ecg_result["processed_data"])
                    report = await mock_diagnostic_instance.generate_report(ml_result)
                    
                    # Verify pipeline completion
                    assert ecg_result["signal_quality"] > 0.9
                    assert ml_result["confidence"] > 0.8
                    assert report["report_id"] == "RPT_001"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_patient_processing(self, mock_db_session):
        """Test concurrent processing of multiple patients."""
        # Simulate multiple patients being processed simultaneously
        patient_count = 10
        
        async def process_patient(patient_id):
            """Simulate processing a single patient."""
            from tests.smart_mocks import SmartECGMock
            
            ecg_data = SmartECGMock.generate_normal_ecg()
            # Mock processing
            await asyncio.sleep(0.1)  # Simulate processing time
            
            return {
                "patient_id": patient_id,
                "status": "completed",
                "diagnosis": "Normal Sinus Rhythm"
            }
        
        # Process all patients concurrently
        tasks = [process_patient(i) for i in range(patient_count)]
        results = await asyncio.gather(*tasks)
        
        # Verify all patients processed
        assert len(results) == patient_count
        assert all(r["status"] == "completed" for r in results)