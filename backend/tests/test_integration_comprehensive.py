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
        services = integrated_services
        
        # Step 1: Create patient
        patient_data = {
            "patient_id": "TEST001",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1960-01-01",
            "gender": "male",
            "medical_history": ["hypertension", "diabetes"],
            "medications": ["metformin", "lisinopril"]
        }
        
        with patch.object(services["patient"], 'create_patient', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = Mock(id=123, **patient_data)
            patient = await services["patient"].create_patient(patient_data, created_by=1)
            assert patient.id == 123
        
        # Step 2: Upload and process ECG
        ecg_data = np.random.randn(5000, 12).astype(np.float32)  # 10 seconds, 12 leads
        
        with patch.object(services["ecg"], 'create_analysis', new_callable=AsyncMock) as mock_analysis:
            mock_analysis.return_value = Mock(
                id=1,
                analysis_id="ECG_TEST001",
                patient_id=123,
                status=AnalysisStatus.PROCESSING
            )
            
            analysis = await services["ecg"].create_analysis(
                patient_id=123,
                file_path="/tmp/test_ecg.xml",
                original_filename="test_ecg.xml",
                created_by=1
            )
            
            assert analysis.patient_id == 123
            assert analysis.status == AnalysisStatus.PROCESSING
        
        # Step 3: ML Analysis
        ml_result = await services["ml"].classify_ecg(ecg_data)
        assert ml_result["confidence"] > 0.9
        assert "atrial_fibrillation" in ml_result["predictions"]
        
        # Step 4: AI Diagnostic Integration
        symptoms = {
            "palpitations": {"severity": 7, "duration": "2 hours"},
            "shortness_of_breath": {"severity": 6, "duration": "1 hour"}
        }
        
        with patch.object(services["diagnostic"], 'integrate_multimodal_data', new_callable=AsyncMock) as mock_integrate:
            mock_integrate.return_value = {
                "integrated_diagnosis": "Atrial Fibrillation with RVR",
                "confidence_score": 0.94,
                "clinical_urgency": ClinicalUrgency.HIGH,
                "recommendations": ["anticoagulation", "rate_control"]
            }
            
            diagnostic_result = await services["diagnostic"].integrate_multimodal_data(
                symptoms=symptoms,
                patient_data=patient_data,
                ecg_analysis=ml_result
            )
            
            assert diagnostic_result["confidence_score"] > 0.9
            assert diagnostic_result["clinical_urgency"] == ClinicalUrgency.HIGH
        
        # Step 5: Notification for high urgency
        with patch.object(services["notification"], 'send_urgent_notification', new_callable=AsyncMock) as mock_notify:
            mock_notify.return_value = True
            
            notification_sent = await services["notification"].send_urgent_notification(
                patient_id=123,
                analysis_id="ECG_TEST001",
                urgency=ClinicalUrgency.HIGH,
                diagnosis="Atrial Fibrillation with RVR"
            )
            
            assert notification_sent == True

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_critical_patient_pathway(self, integrated_services):
        """Test critical patient pathway with immediate escalation."""
        services = integrated_services
        
        # Critical ECG findings
        services["ml"].classify_ecg.return_value = {
            "predictions": {"stemi": 0.95, "normal": 0.05},
            "confidence": 0.98,
            "primary_diagnosis": "ST-Elevation Myocardial Infarction"
        }
        
        # Critical symptoms
        critical_symptoms = {
            "chest_pain": {"severity": 10, "type": "crushing", "radiation": "left_arm"},
            "diaphoresis": {"severity": 9},
            "nausea": {"severity": 8}
        }
        
        # Patient with high risk factors
        high_risk_patient = {
            "age": 68,
            "gender": "male",
            "medical_history": ["diabetes", "hypertension", "hyperlipidemia"],
            "family_history": ["coronary_artery_disease"]
        }
        
        # Integrate critical data
        with patch.object(services["diagnostic"], 'integrate_multimodal_data', new_callable=AsyncMock) as mock_integrate:
            mock_integrate.return_value = {
                "integrated_diagnosis": "STEMI - Acute Myocardial Infarction",
                "confidence_score": 0.98,
                "clinical_urgency": ClinicalUrgency.CRITICAL,
                "immediate_actions": ["activate_cath_lab", "aspirin", "heparin", "clopidogrel"],
                "time_to_treatment": "< 90 minutes"
            }
            
            critical_result = await services["diagnostic"].integrate_multimodal_data(
                symptoms=critical_symptoms,
                patient_data=high_risk_patient,
                ecg_analysis=services["ml"].classify_ecg.return_value
            )
            
            assert critical_result["clinical_urgency"] == ClinicalUrgency.CRITICAL
            assert "activate_cath_lab" in critical_result["immediate_actions"]
        
        # Verify immediate notification
        with patch.object(services["notification"], 'send_critical_alert', new_callable=AsyncMock) as mock_alert:
            mock_alert.return_value = {
                "alert_sent": True,
                "recipients": ["cardiology_team", "emergency_physician", "cath_lab"],
                "response_time": "< 2 minutes"
            }
            
            alert_result = await services["notification"].send_critical_alert(
                patient_id=123,
                diagnosis="STEMI",
                urgency=ClinicalUrgency.CRITICAL
            )
            
            assert alert_result["alert_sent"] == True
            assert "cath_lab" in alert_result["recipients"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_lead_ecg_processing(self, integrated_services):
        """Test processing of multi-lead ECG with complex arrhythmias."""
        services = integrated_services
        
        # Generate complex arrhythmia data
        complex_ecg = np.random.randn(15000, 15).astype(np.float32)  # 30 seconds, 15 leads
        
        # Mock complex ML analysis
        services["ml"].classify_ecg.return_value = {
            "predictions": {
                "atrial_fibrillation": 0.4,
                "ventricular_tachycardia": 0.3,
                "multifocal_atrial_tachycardia": 0.2,
                "normal": 0.1
            },
            "confidence": 0.75,
            "primary_diagnosis": "Complex Arrhythmia - Requires Expert Review",
            "secondary_findings": ["irregular_rhythm", "wide_qrs", "variable_rr"]
        }
        
        # Process complex ECG
        ml_result = await services["ml"].classify_ecg(complex_ecg)
        
        # Should trigger expert review for low confidence complex cases
        assert ml_result["confidence"] < 0.8
        assert "Complex Arrhythmia" in ml_result["primary_diagnosis"]
        
        # Verify validation service is called for expert review
        with patch.object(services["validation"], 'create_validation', new_callable=AsyncMock) as mock_validation:
            mock_validation.return_value = Mock(
                id=1,
                status="pending_expert_review",
                requires_second_opinion=True
            )
            
            validation = await services["validation"].create_validation(
                analysis_id=1,
                validator_id=1,
                requires_expert_review=True
            )
            
            assert validation.requires_second_opinion == True

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pediatric_ecg_workflow(self, integrated_services):
        """Test pediatric-specific ECG analysis workflow."""
        services = integrated_services
        
        # Pediatric patient data
        pediatric_patient = {
            "age": 8,
            "gender": "female",
            "weight": 25,  # kg
            "height_cm": 125,
            "medical_history": ["congenital_heart_disease"]
        }
        
        # Pediatric ECG characteristics
        pediatric_ecg = np.random.randn(5000, 12).astype(np.float32)
        
        # Mock pediatric-specific analysis
        services["ml"].classify_ecg.return_value = {
            "predictions": {"normal_pediatric": 0.8, "rbbb": 0.15, "artifact": 0.05},
            "confidence": 0.88,
            "primary_diagnosis": "Normal Pediatric ECG",
            "age_adjusted_parameters": {
                "heart_rate": 110,  # Normal for age 8
                "pr_interval": 140,  # ms
                "qrs_duration": 85   # ms
            }
        }
        
        # Pediatric diagnostic considerations
        with patch.object(services["diagnostic"], 'analyze_pediatric_case', new_callable=AsyncMock) as mock_pediatric:
            mock_pediatric.return_value = {
                "age_appropriate_diagnosis": True,
                "growth_considerations": "normal_development",
                "follow_up_recommendations": ["routine_cardiology", "annual_echo"],
                "parent_education": ["normal_findings", "when_to_seek_care"]
            }
            
            pediatric_result = await services["diagnostic"].analyze_pediatric_case(pediatric_patient)
            
            assert pediatric_result["age_appropriate_diagnosis"] == True
            assert "routine_cardiology" in pediatric_result["follow_up_recommendations"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_geriatric_polypharmacy_workflow(self, integrated_services):
        """Test geriatric patient with polypharmacy considerations."""
        services = integrated_services
        
        # Geriatric patient with multiple medications
        geriatric_patient = {
            "age": 85,
            "gender": "female",
            "medications": [
                "warfarin", "digoxin", "metoprolol", "furosemide",
                "lisinopril", "atorvastatin", "metformin", "amlodipine"
            ],
            "comorbidities": [
                "atrial_fibrillation", "heart_failure", "diabetes",
                "hypertension", "chronic_kidney_disease"
            ]
        }
        
        # ECG showing medication effects
        services["ml"].classify_ecg.return_value = {
            "predictions": {"atrial_fibrillation": 0.9, "normal": 0.1},
            "confidence": 0.92,
            "primary_diagnosis": "Atrial Fibrillation - Rate Controlled",
            "medication_effects": {
                "digoxin_effect": "present",
                "beta_blocker_effect": "rate_control"
            }
        }
        
        # Geriatric-specific analysis
        with patch.object(services["diagnostic"], 'analyze_geriatric_case', new_callable=AsyncMock) as mock_geriatric:
            mock_geriatric.return_value = {
                "polypharmacy_risks": ["drug_interactions", "fall_risk"],
                "medication_review_needed": True,
                "cognitive_considerations": "mild_impairment",
                "fall_risk_score": "high",
                "recommendations": [
                    "medication_reconciliation",
                    "fall_prevention_measures",
                    "simplified_dosing_schedule"
                ]
            }
            
            geriatric_result = await services["diagnostic"].analyze_geriatric_case(geriatric_patient)
            
            assert geriatric_result["medication_review_needed"] == True
            assert "fall_prevention_measures" in geriatric_result["recommendations"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_emergency_department_workflow(self, integrated_services):
        """Test emergency department rapid triage workflow."""
        services = integrated_services
        
        # Multiple patients arriving simultaneously
        patients = [
            {
                "id": 1,
                "chief_complaint": "chest_pain",
                "triage_level": "urgent",
                "symptoms": {"chest_pain": {"severity": 9}}
            },
            {
                "id": 2,
                "chief_complaint": "palpitations",
                "triage_level": "less_urgent",
                "symptoms": {"palpitations": {"severity": 5}}
            },
            {
                "id": 3,
                "chief_complaint": "syncope",
                "triage_level": "urgent",
                "symptoms": {"syncope": {"duration": "brief"}}
            }
        ]
        
        # Process multiple ECGs concurrently
        ecg_tasks = []
        for patient in patients:
            ecg_data = np.random.randn(5000, 12).astype(np.float32)
            task = services["ml"].classify_ecg(ecg_data)
            ecg_tasks.append(task)
        
        # Mock different results for each patient
        services["ml"].classify_ecg.side_effect = [
            {  # Patient 1 - Critical
                "predictions": {"stemi": 0.95},
                "confidence": 0.98,
                "primary_diagnosis": "STEMI"
            },
            {  # Patient 2 - Stable
                "predictions": {"normal": 0.85},
                "confidence": 0.90,
                "primary_diagnosis": "Normal"
            },
            {  # Patient 3 - Concerning
                "predictions": {"heart_block": 0.80},
                "confidence": 0.85,
                "primary_diagnosis": "Third Degree Heart Block"
            }
        ]
        
        # Emergency triage for each patient
        triage_results = []
        for i, patient in enumerate(patients):
            with patch.object(services["diagnostic"], 'perform_emergency_triage', new_callable=AsyncMock) as mock_triage:
                if i == 0:  # Critical patient
                    mock_triage.return_value = {
                        "triage_level": "critical",
                        "time_to_treatment": "immediate",
                        "required_resources": ["cath_lab", "cardiology", "icu"],
                        "priority_score": 10
                    }
                elif i == 1:  # Stable patient
                    mock_triage.return_value = {
                        "triage_level": "stable",
                        "time_to_treatment": "4_hours",
                        "required_resources": ["observation"],
                        "priority_score": 3
                    }
                else:  # Urgent patient
                    mock_triage.return_value = {
                        "triage_level": "urgent",
                        "time_to_treatment": "30_minutes",
                        "required_resources": ["cardiology", "pacemaker"],
                        "priority_score": 8
                    }
                
                triage = await services["diagnostic"].perform_emergency_triage(
                    symptoms=patient["symptoms"],
                    patient_data=patient
                )
                triage_results.append(triage)
        
        # Verify proper prioritization
        priorities = [result["priority_score"] for result in triage_results]
        assert priorities == [10, 3, 8]  # Critical, Stable, Urgent
        
        # Verify critical patient gets immediate attention
        assert triage_results[0]["time_to_treatment"] == "immediate"
        assert "cath_lab" in triage_results[0]["required_resources"]


class TestDataFlowIntegration:
    """Test data flow integration across the system."""

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
            # Mock processing time
            await asyncio.sleep(0.1)
            return {
                "patient_id": patient_id,
                "status": "completed",
                "processing_time": 0.1
            }
        
        # Process patients concurrently
        tasks = [process_patient(i) for i in range(patient_count)]
        results = await asyncio.gather(*tasks)
        
        # Verify all patients processed
        assert len(results) == patient_count
        assert all(result["status"] == "completed" for result in results)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, mock_db_session):
        """Test error handling and recovery mechanisms."""
        # Test various failure scenarios and recovery
        
        # Scenario 1: ML service failure
        with patch('app.services.ml_model_service.MLModelService') as mock_ml:
            mock_ml_instance = mock_ml.return_value
            mock_ml_instance.classify_ecg.side_effect = Exception("ML service unavailable")
            
            # Should gracefully handle ML failure
            try:
                await mock_ml_instance.classify_ecg(np.random.randn(5000, 12))
                assert False, "Should have raised exception"
            except Exception as e:
                assert "ML service unavailable" in str(e)
        
        # Scenario 2: Database connection failure
        mock_db_session.commit.side_effect = Exception("Database connection lost")
        
        try:
            await mock_db_session.commit()
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Database connection lost" in str(e)
        
        # Scenario 3: Recovery after failure
        mock_db_session.commit.side_effect = None  # Reset
        mock_db_session.commit.return_value = None
        
        # Should work after recovery
        await mock_db_session.commit()  # Should not raise

