"""
Enhanced AI Diagnostic Service Tests - 100% Coverage Implementation
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json

from app.services.ai_diagnostic_service import AIDiagnosticService
from app.core.constants import DiagnosisCategory, ClinicalUrgency, ConfidenceLevel
from tests.smart_mocks import SmartECGMock, SmartPatientMock


class TestAIDiagnosticServiceCritical:
    """Critical tests for AI Diagnostic Service - 100% coverage required."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_knowledge_base(self):
        """Mock medical knowledge base."""
        kb = Mock()
        kb.get_diagnosis_info.return_value = {
            "icd10_codes": ["I48.91"],
            "clinical_guidelines": ["Rate control", "Anticoagulation assessment"],
            "differential_diagnoses": ["Atrial flutter", "MAT"],
            "risk_factors": ["Age > 65", "Hypertension", "Diabetes"]
        }
        return kb

    @pytest.fixture
    def mock_nlp_service(self):
        """Mock NLP service for report generation."""
        nlp = AsyncMock()
        nlp.generate_clinical_narrative.return_value = (
            "ECG analysis reveals atrial fibrillation with rapid ventricular response. "
            "Recommend rate control and anticoagulation assessment."
        )
        return nlp

    @pytest.fixture
    def ai_diagnostic_service(self, mock_db_session, mock_knowledge_base, mock_nlp_service):
        """AI Diagnostic service instance."""
        service = AIDiagnosticService(mock_db_session)
        service.knowledge_base = mock_knowledge_base
        service.nlp_service = mock_nlp_service
        return service

    @pytest.fixture
    def ecg_analysis_result(self):
        """Sample ECG analysis result."""
        return {
            "diagnosis": "Atrial Fibrillation",
            "confidence": 0.92,
            "features": {
                "heart_rate": 145,
                "rhythm_regularity": 0.2,
                "p_wave_present": False,
                "qrs_duration": 85,
                "qt_interval": 380
            },
            "ml_predictions": {
                "atrial_fibrillation": 0.92,
                "normal": 0.05,
                "other": 0.03
            }
        }

    @pytest.fixture
    def patient_context(self):
        """Sample patient context."""
        return SmartPatientMock.generate_patient_data(
            age_range=(70, 80),
            condition="cardiac"
        )

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_generate_comprehensive_diagnosis(self, ai_diagnostic_service, 
                                                  ecg_analysis_result, patient_context):
        """Test comprehensive diagnosis generation."""
        # Generate diagnosis
        diagnosis = await ai_diagnostic_service.generate_diagnosis(
            ecg_analysis=ecg_analysis_result,
            patient_data=patient_context,
            include_differentials=True,
            include_recommendations=True
        )
        
        # Verify diagnosis structure
        assert diagnosis["primary_diagnosis"] == "Atrial Fibrillation with RVR"
        assert diagnosis["confidence_level"] == ConfidenceLevel.HIGH
        assert diagnosis["clinical_urgency"] == ClinicalUrgency.HIGH
        
        # Verify ICD codes
        assert "I48.91" in diagnosis["icd10_codes"]
        
        # Verify differential diagnoses
        assert len(diagnosis["differential_diagnoses"]) > 0
        assert any("flutter" in d["diagnosis"].lower() 
                  for d in diagnosis["differential_diagnoses"])
        
        # Verify recommendations
        assert len(diagnosis["recommendations"]) > 0
        assert any("rate control" in r.lower() 
                  for r in diagnosis["recommendations"])
        
        # Verify risk assessment
        assert "stroke_risk" in diagnosis["risk_assessment"]
        assert diagnosis["risk_assessment"]["cha2ds2_vasc_score"] >= 2

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_multimodal_data_integration(self, ai_diagnostic_service):
        """Test integration of multiple data sources."""
        # Multiple data sources
        ecg_data = {
            "diagnosis": "Possible MI",
            "st_elevation": True,
            "affected_leads": ["II", "III", "aVF"]
        }
        
        lab_data = SmartPatientMock.generate_lab_results(
            test_type="cardiac",
            condition="myocardial_infarction"
        )
        
        imaging_data = {
            "modality": "echo",
            "ejection_fraction": 35,
            "wall_motion_abnormality": "inferior",
            "valve_function": "normal"
        }
        
        vitals_data = {
            "blood_pressure": "140/90",
            "heart_rate": 95,
            "oxygen_saturation": 94,
            "temperature": 37.2
        }
        
        # Integrate data
        integrated_diagnosis = await ai_diagnostic_service.integrate_multimodal_data(
            ecg=ecg_data,
            labs=lab_data,
            imaging=imaging_data,
            vitals=vitals_data
        )
        
        # Verify integration
        assert integrated_diagnosis["diagnosis"] == "Acute Inferior STEMI"
        assert integrated_diagnosis["data_sources_used"] == ["ecg", "labs", "imaging", "vitals"]
        assert integrated_diagnosis["confidence_boost"] > 0  # Multiple sources increase confidence
        assert integrated_diagnosis["clinical_correlation"]["troponin_elevated"] is True
        assert integrated_diagnosis["clinical_correlation"]["wall_motion_matches_ecg"] is True

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_clinical_decision_support(self, ai_diagnostic_service, ecg_analysis_result):
        """Test clinical decision support system."""
        # Generate clinical decision support
        cds_result = await ai_diagnostic_service.get_clinical_decision_support(
            diagnosis="STEMI",
            patient_age=65,
            symptom_onset_minutes=45,
            contraindications=["aspirin_allergy"]
        )
        
        # Verify immediate actions
        assert "immediate_actions" in cds_result
        assert any("cath lab" in action.lower() 
                  for action in cds_result["immediate_actions"])
        
        # Verify medication recommendations
        assert "medications" in cds_result
        assert not any("aspirin" in med["name"].lower() 
                      for med in cds_result["medications"])  # Contraindication respected
        
        # Verify time targets
        assert cds_result["time_targets"]["door_to_balloon_minutes"] == 90
        assert cds_result["time_critical"] is True
        
        # Verify clinical pathways
        assert "clinical_pathway" in cds_result
        assert cds_result["clinical_pathway"]["name"] == "STEMI Protocol"

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_risk_stratification(self, ai_diagnostic_service, patient_context):
        """Test comprehensive risk stratification."""
        # Add cardiac risk factors
        patient_context.update({
            "hypertension": True,
            "diabetes": True,
            "smoking_status": "current",
            "family_history_cad": True,
            "ldl_cholesterol": 180
        })
        
        ecg_findings = {
            "diagnosis": "Atrial Fibrillation",
            "heart_rate": 120,
            "pvcs_per_hour": 50
        }
        
        # Calculate risk scores
        risk_assessment = await ai_diagnostic_service.calculate_risk_scores(
            patient_data=patient_context,
            ecg_findings=ecg_findings
        )
        
        # Verify risk calculations
        assert "cardiovascular_risk" in risk_assessment
        assert risk_assessment["cardiovascular_risk"]["score"] > 20  # High risk
        assert risk_assessment["cardiovascular_risk"]["category"] == "high"
        
        # Verify stroke risk (CHA2DS2-VASc)
        assert risk_assessment["stroke_risk"]["cha2ds2_vasc"] >= 3
        assert risk_assessment["stroke_risk"]["annual_stroke_risk"] > 3.0
        
        # Verify bleeding risk (HAS-BLED)
        assert "bleeding_risk" in risk_assessment
        assert risk_assessment["bleeding_risk"]["has_bled"] >= 0
        
        # Verify recommendations based on risk
        assert risk_assessment["recommendations"]["anticoagulation"] == "strongly_recommended"

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_treatment_recommendation_engine(self, ai_diagnostic_service):
        """Test treatment recommendation engine."""
        diagnosis_data = {
            "primary": "Heart Failure with Reduced EF",
            "ejection_fraction": 30,
            "nyha_class": 3,
            "comorbidities": ["diabetes", "ckd_stage_3"]
        }
        
        # Get treatment recommendations
        recommendations = await ai_diagnostic_service.get_treatment_recommendations(
            diagnosis_data,
            consider_interactions=True,
            include_alternatives=True
        )
        
        # Verify GDMT (Guideline-Directed Medical Therapy)
        assert "medications" in recommendations
        med_classes = [m["class"] for m in recommendations["medications"]]
        assert "ACE_inhibitor" in med_classes or "ARB" in med_classes
        assert "beta_blocker" in med_classes
        assert "mineralocorticoid_antagonist" in med_classes
        
        # Verify dose adjustments for CKD
        ace_med = next(m for m in recommendations["medications"] 
                      if m["class"] in ["ACE_inhibitor", "ARB"])
        assert ace_med["dose_adjustment"] == "reduce_for_ckd"
        
        # Verify device therapy recommendations
        assert "device_therapy" in recommendations
        assert recommendations["device_therapy"]["icd_indicated"] is True
        assert recommendations["device_therapy"]["crt_indicated"] is True

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_natural_language_report_generation(self, ai_diagnostic_service, 
                                                     ecg_analysis_result, patient_context):
        """Test natural language report generation."""
        # Generate clinical report
        report = await ai_diagnostic_service.generate_clinical_report(
            ecg_analysis=ecg_analysis_result,
            patient_data=patient_context,
            report_type="comprehensive",
            audience="physician"
        )
        
        # Verify report sections
        assert "clinical_summary" in report
        assert "findings" in report
        assert "interpretation" in report
        assert "recommendations" in report
        assert "follow_up" in report
        
        # Verify content quality
        assert len(report["clinical_summary"]) > 100  # Substantial content
        assert "atrial fibrillation" in report["findings"].lower()
        assert "anticoagulation" in report["recommendations"].lower()
        
        # Verify medical terminology usage
        assert any(term in report["interpretation"].lower() 
                  for term in ["irregularly irregular", "absent p waves"])

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_pediatric_diagnostic_adjustments(self, ai_diagnostic_service):
        """Test pediatric-specific diagnostic adjustments."""
        pediatric_patient = {
            "age": 8,
            "weight_kg": 28,
            "height_cm": 130
        }
        
        pediatric_ecg = {
            "heart_rate": 110,  # Normal for age
            "pr_interval": 140,
            "qrs_duration": 70,
            "qt_interval": 340
        }
        
        # Generate pediatric diagnosis
        diagnosis = await ai_diagnostic_service.generate_pediatric_diagnosis(
            ecg_data=pediatric_ecg,
            patient_data=pediatric_patient
        )
        
        # Verify age-adjusted interpretation
        assert diagnosis["age_adjusted_normal"] is True
        assert diagnosis["heart_rate_percentile"] > 25 and diagnosis["heart_rate_percentile"] < 75
        
        # Verify pediatric-specific considerations
        assert "growth_adjusted_parameters" in diagnosis
        assert "congenital_screening" in diagnosis
        assert diagnosis["congenital_screening"]["performed"] is True

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_emergency_diagnostic_pathway(self, ai_diagnostic_service):
        """Test emergency diagnostic pathway with time tracking."""
        # Emergency presentation
        emergency_data = {
            "presentation": "chest_pain",
            "symptom_onset": datetime.now() - timedelta(minutes=30),
            "vital_signs": {
                "blood_pressure": "80/50",
                "heart_rate": 140,
                "respiratory_rate": 28
            },
            "ecg_findings": {
                "st_elevation": True,
                "new_lbbb": False,
                "reciprocal_changes": True
            }
        }
        
        # Process emergency diagnosis
        with patch('app.services.ai_diagnostic_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            
            emergency_diagnosis = await ai_diagnostic_service.process_emergency_diagnosis(
                emergency_data
            )
        
        # Verify emergency response
        assert emergency_diagnosis["diagnosis"] == "Acute STEMI with Cardiogenic Shock"
        assert emergency_diagnosis["urgency"] == ClinicalUrgency.CRITICAL
        assert emergency_diagnosis["processing_time_seconds"] < 5
        
        # Verify critical alerts
        assert emergency_diagnosis["alerts_triggered"] == ["cath_lab", "shock_team"]
        assert emergency_diagnosis["time_to_treatment_target"] == 90

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_diagnostic_uncertainty_handling(self, ai_diagnostic_service):
        """Test handling of diagnostic uncertainty."""
        # Ambiguous ECG findings
        uncertain_ecg = {
            "ml_predictions": {
                "normal": 0.4,
                "atrial_fibrillation": 0.35,
                "atrial_flutter": 0.25
            },
            "feature_quality": {
                "signal_quality": 0.6,
                "lead_dropout": ["V5", "V6"]
            }
        }
        
        # Process with uncertainty
        diagnosis = await ai_diagnostic_service.handle_uncertain_diagnosis(
            uncertain_ecg,
            confidence_threshold=0.8
        )
        
        # Verify uncertainty handling
        assert diagnosis["confidence_level"] == ConfidenceLevel.LOW
        assert diagnosis["requires_human_review"] is True
        assert len(diagnosis["differential_diagnoses"]) >= 2
        assert diagnosis["recommended_actions"] == ["repeat_ecg", "physician_review"]
        assert diagnosis["uncertainty_reasons"] == ["low_confidence", "poor_signal_quality"]

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_longitudinal_analysis(self, ai_diagnostic_service):
        """Test longitudinal ECG analysis and trend detection."""
        # Historical ECG data
        historical_ecgs = [
            {
                "date": datetime.now() - timedelta(days=365),
                "heart_rate": 70,
                "pr_interval": 160,
                "qt_interval": 400,
                "diagnosis": "Normal Sinus Rhythm"
            },
            {
                "date": datetime.now() - timedelta(days=180),
                "heart_rate": 75,
                "pr_interval": 180,
                "qt_interval": 410,
                "diagnosis": "First Degree AV Block"
            },
            {
                "date": datetime.now(),
                "heart_rate": 80,
                "pr_interval": 220,
                "qt_interval": 440,
                "diagnosis": "First Degree AV Block - Progressing"
            }
        ]
        
        # Analyze trends
        trend_analysis = await ai_diagnostic_service.analyze_ecg_trends(
            historical_ecgs,
            patient_id=123
        )
        
        # Verify trend detection
        assert trend_analysis["pr_interval_trend"] == "increasing"
        assert trend_analysis["progression_detected"] is True
        assert trend_analysis["clinical_significance"] == "monitor_closely"
        assert "consider EP consultation" in trend_analysis["recommendations"]

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_drug_interaction_checking(self, ai_diagnostic_service):
        """Test drug interaction checking for cardiac medications."""
        current_medications = [
            "metoprolol",
            "amiodarone",
            "warfarin",
            "digoxin"
        ]
        
        proposed_medication = "verapamil"
        
        # Check interactions
        interaction_result = await ai_diagnostic_service.check_drug_interactions(
            current_medications,
            proposed_medication,
            patient_conditions=["atrial_fibrillation", "heart_failure"]
        )
        
        # Verify interaction detection
        assert interaction_result["has_interactions"] is True
        assert len(interaction_result["interactions"]) > 0
        
        # Verify specific interactions
        beta_blocker_interaction = next(
            i for i in interaction_result["interactions"]
            if "beta blocker" in i["description"].lower()
        )
        assert beta_blocker_interaction["severity"] == "major"
        assert "bradycardia" in beta_blocker_interaction["effect"].lower()
        
        # Verify alternatives suggested
        assert len(interaction_result["alternatives"]) > 0

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_evidence_based_recommendations(self, ai_diagnostic_service):
        """Test evidence-based recommendation generation."""
        diagnosis = "Heart Failure with Preserved EF"
        patient_characteristics = {
            "age": 75,
            "gender": "female",
            "comorbidities": ["hypertension", "obesity", "diabetes"],
            "current_medications": ["lisinopril", "metformin"]
        }
        
        # Get evidence-based recommendations
        recommendations = await ai_diagnostic_service.get_evidence_based_recommendations(
            diagnosis,
            patient_characteristics,
            include_citations=True
        )
        
        # Verify recommendations
        assert "lifestyle_modifications" in recommendations
        assert "pharmacological" in recommendations
        assert "monitoring" in recommendations
        
        # Verify evidence quality
        for rec in recommendations["pharmacological"]:
            assert "evidence_level" in rec
            assert rec["evidence_level"] in ["A", "B", "C"]
            assert "guideline_source" in rec
            assert rec["guideline_source"] in ["ACC/AHA", "ESC", "NICE"]
            
        # Verify citations
        assert len(recommendations["citations"]) > 0
        assert all("pmid" in cite or "doi" in cite 
                  for cite in recommendations["citations"])

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_diagnostic_confidence_calibration(self, ai_diagnostic_service):
        """Test diagnostic confidence calibration."""
        # Multiple diagnostic scenarios with varying confidence
        scenarios = [
            {
                "ml_confidence": 0.95,
                "signal_quality": 0.9,
                "clinical_correlation": 0.8
            },
            {
                "ml_confidence": 0.7,
                "signal_quality": 0.5,
                "clinical_correlation": 0.6
            }
        ]
        
        for scenario in scenarios:
            calibrated_confidence = await ai_diagnostic_service.calibrate_diagnostic_confidence(
                scenario
            )
            
            # Verify calibration reduces overconfidence
            assert calibrated_confidence["final_confidence"] <= scenario["ml_confidence"]
            
            # Verify quality impacts confidence
            if scenario["signal_quality"] < 0.7:
                assert calibrated_confidence["confidence_penalty"] > 0.1
            
            # Verify confidence level assignment
            if calibrated_confidence["final_confidence"] > 0.8:
                assert calibrated_confidence["level"] == ConfidenceLevel.HIGH
            elif calibrated_confidence["final_confidence"] > 0.6:
                assert calibrated_confidence["level"] == ConfidenceLevel.MEDIUM
            else:
                assert calibrated_confidence["level"] == ConfidenceLevel.LOW

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_clinical_validation_integration(self, ai_diagnostic_service):
        """Test integration with clinical validation workflow."""
        ai_diagnosis = {
            "diagnosis": "Ventricular Tachycardia",
            "confidence": 0.88,
            "features_detected": ["wide_qrs", "av_dissociation", "capture_beats"]
        }
        
        # Submit for validation
        validation_request = await ai_diagnostic_service.submit_for_clinical_validation(
            ai_diagnosis,
            priority="urgent",
            validator_specialty="electrophysiology"
        )
        
        # Verify validation request
        assert validation_request["status"] == "pending_validation"
        assert validation_request["priority"] == "urgent"
        assert validation_request["assigned_to_specialty"] == "electrophysiology"
        assert validation_request["sla_hours"] == 2  # Urgent SLA
        
        # Verify supporting materials included
        assert "ecg_strips" in validation_request["supporting_materials"]
        assert "feature_highlights" in validation_request["supporting_materials"]
        assert validation_request["supporting_materials"]["ai_explanation"] is not None