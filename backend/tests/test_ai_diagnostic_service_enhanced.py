"""
Enhanced AI Diagnostic Service Tests - 100% Coverage Implementation
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

from app.services.ai_diagnostic_service import AIDiagnosticService
from app.core.constants import ClinicalUrgency, DiagnosisCategory


class TestAIDiagnosticServiceCritical:
    """Critical tests for AI Diagnostic Service - 100% coverage required."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def diagnostic_service(self, mock_db_session):
        """AI Diagnostic service instance."""
        return AIDiagnosticService(mock_db_session)

    @pytest.fixture
    def sample_symptoms(self):
        """Sample patient symptoms."""
        return {
            "chest_pain": {"severity": 8, "duration": "2 hours", "type": "crushing"},
            "shortness_of_breath": {"severity": 7, "duration": "1 hour"},
            "nausea": {"severity": 5, "duration": "30 minutes"},
            "sweating": {"severity": 6, "duration": "1 hour"}
        }

    @pytest.fixture
    def sample_patient_data(self):
        """Sample patient data."""
        return {
            "age": 65,
            "gender": "male",
            "medical_history": ["hypertension", "diabetes"],
            "medications": ["metformin", "lisinopril"],
            "family_history": ["coronary_artery_disease"],
            "vital_signs": {
                "blood_pressure": "150/90",
                "heart_rate": 95,
                "temperature": 98.6,
                "oxygen_saturation": 96
            }
        }

    @pytest.fixture
    def sample_ecg_analysis(self):
        """Sample ECG analysis results."""
        return {
            "primary_diagnosis": "ST-elevation myocardial infarction",
            "confidence": 0.92,
            "abnormalities": ["ST elevation", "Q waves"],
            "heart_rate": 95,
            "rhythm": "sinus rhythm"
        }

    # Test 1: Service Initialization
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_db_session):
        """Test AI diagnostic service initialization."""
        service = AIDiagnosticService(mock_db_session)
        assert service.db == mock_db_session
        assert hasattr(service, 'knowledge_base')
        assert hasattr(service, 'diagnostic_rules')

    # Test 2: Symptom Analysis
    @pytest.mark.asyncio
    async def test_symptom_analysis(self, diagnostic_service, sample_symptoms, sample_patient_data):
        """Test comprehensive symptom analysis."""
        analysis = await diagnostic_service.analyze_symptoms(sample_symptoms, sample_patient_data)
        
        assert "symptom_score" in analysis
        assert "urgency_level" in analysis
        assert "primary_concerns" in analysis
        assert "risk_factors" in analysis
        
        # High severity chest pain should trigger high urgency
        assert analysis["urgency_level"] in [ClinicalUrgency.HIGH, ClinicalUrgency.CRITICAL]

    # Test 3: Differential Diagnosis Generation
    @pytest.mark.asyncio
    async def test_differential_diagnosis(self, diagnostic_service, sample_symptoms, sample_patient_data):
        """Test differential diagnosis generation."""
        differentials = await diagnostic_service.generate_differential_diagnosis(
            sample_symptoms, sample_patient_data
        )
        
        assert len(differentials) > 0
        assert all("diagnosis" in diff for diff in differentials)
        assert all("probability" in diff for diff in differentials)
        assert all("reasoning" in diff for diff in differentials)
        
        # Should include cardiac conditions given symptoms
        cardiac_diagnoses = [d for d in differentials if "cardiac" in d["diagnosis"].lower() or "heart" in d["diagnosis"].lower()]
        assert len(cardiac_diagnoses) > 0

    # Test 4: Risk Stratification
    @pytest.mark.asyncio
    async def test_risk_stratification(self, diagnostic_service, sample_patient_data):
        """Test patient risk stratification."""
        risk_assessment = await diagnostic_service.assess_patient_risk(sample_patient_data)
        
        assert "overall_risk" in risk_assessment
        assert "risk_factors" in risk_assessment
        assert "protective_factors" in risk_assessment
        assert "recommendations" in risk_assessment
        
        # Patient with diabetes and hypertension should have elevated risk
        assert risk_assessment["overall_risk"] in ["moderate", "high", "critical"]

    # Test 5: Clinical Guidelines Integration
    @pytest.mark.asyncio
    async def test_clinical_guidelines_integration(self, diagnostic_service, sample_symptoms):
        """Test integration with clinical guidelines."""
        guidelines = await diagnostic_service.apply_clinical_guidelines(
            symptoms=sample_symptoms,
            suspected_condition="acute_coronary_syndrome"
        )
        
        assert "applicable_guidelines" in guidelines
        assert "recommendations" in guidelines
        assert "evidence_level" in guidelines
        assert "contraindications" in guidelines

    # Test 6: Drug Interaction Checking
    @pytest.mark.asyncio
    async def test_drug_interaction_checking(self, diagnostic_service):
        """Test drug interaction checking."""
        medications = ["warfarin", "aspirin", "metformin"]
        
        interactions = await diagnostic_service.check_drug_interactions(medications)
        
        assert "interactions" in interactions
        assert "severity_levels" in interactions
        assert "recommendations" in interactions
        
        # Warfarin + Aspirin should show interaction
        assert len(interactions["interactions"]) > 0

    # Test 7: Allergy and Contraindication Checking
    @pytest.mark.asyncio
    async def test_allergy_contraindication_checking(self, diagnostic_service):
        """Test allergy and contraindication checking."""
        patient_allergies = ["penicillin", "shellfish"]
        proposed_treatment = ["amoxicillin", "contrast_dye"]
        
        contraindications = await diagnostic_service.check_contraindications(
            allergies=patient_allergies,
            proposed_treatments=proposed_treatment
        )
        
        assert "contraindicated" in contraindications
        assert "alternatives" in contraindications
        assert "severity" in contraindications
        
        # Amoxicillin should be contraindicated for penicillin allergy
        assert any("amoxicillin" in item for item in contraindications["contraindicated"])

    # Test 8: Diagnostic Confidence Scoring
    @pytest.mark.asyncio
    async def test_diagnostic_confidence_scoring(self, diagnostic_service, sample_symptoms, sample_patient_data):
        """Test diagnostic confidence scoring."""
        diagnosis = "acute_myocardial_infarction"
        
        confidence = await diagnostic_service.calculate_diagnostic_confidence(
            diagnosis=diagnosis,
            symptoms=sample_symptoms,
            patient_data=sample_patient_data
        )
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should be high given classic symptoms

    # Test 9: Treatment Recommendation
    @pytest.mark.asyncio
    async def test_treatment_recommendation(self, diagnostic_service, sample_patient_data):
        """Test treatment recommendation generation."""
        diagnosis = "acute_myocardial_infarction"
        
        treatment = await diagnostic_service.recommend_treatment(
            diagnosis=diagnosis,
            patient_data=sample_patient_data
        )
        
        assert "immediate_actions" in treatment
        assert "medications" in treatment
        assert "monitoring" in treatment
        assert "follow_up" in treatment
        
        # Should include emergency interventions
        assert len(treatment["immediate_actions"]) > 0

    # Test 10: Prognosis Assessment
    @pytest.mark.asyncio
    async def test_prognosis_assessment(self, diagnostic_service, sample_patient_data):
        """Test prognosis assessment."""
        diagnosis = "acute_myocardial_infarction"
        
        prognosis = await diagnostic_service.assess_prognosis(
            diagnosis=diagnosis,
            patient_data=sample_patient_data
        )
        
        assert "short_term_outlook" in prognosis
        assert "long_term_outlook" in prognosis
        assert "mortality_risk" in prognosis
        assert "recovery_timeline" in prognosis

    # Test 11: Multi-modal Data Integration
    @pytest.mark.asyncio
    async def test_multimodal_integration(self, diagnostic_service, sample_symptoms, sample_patient_data, sample_ecg_analysis):
        """Test integration of multiple data sources."""
        comprehensive_analysis = await diagnostic_service.integrate_multimodal_data(
            symptoms=sample_symptoms,
            patient_data=sample_patient_data,
            ecg_analysis=sample_ecg_analysis,
            lab_results={"troponin": 15.2, "ck_mb": 8.5}
        )
        
        assert "integrated_diagnosis" in comprehensive_analysis
        assert "confidence_score" in comprehensive_analysis
        assert "supporting_evidence" in comprehensive_analysis
        assert "conflicting_evidence" in comprehensive_analysis

    # Test 12: Emergency Triage
    @pytest.mark.asyncio
    async def test_emergency_triage(self, diagnostic_service, sample_symptoms, sample_patient_data):
        """Test emergency triage decision making."""
        triage = await diagnostic_service.perform_emergency_triage(
            symptoms=sample_symptoms,
            patient_data=sample_patient_data
        )
        
        assert "triage_level" in triage
        assert "time_to_treatment" in triage
        assert "required_resources" in triage
        assert "escalation_criteria" in triage
        
        # Severe chest pain should be high priority
        assert triage["triage_level"] in ["urgent", "emergent", "critical"]

    # Test 13: Clinical Decision Support
    @pytest.mark.asyncio
    async def test_clinical_decision_support(self, diagnostic_service, sample_patient_data):
        """Test clinical decision support system."""
        decision_support = await diagnostic_service.provide_decision_support(
            clinical_scenario="chest_pain_evaluation",
            patient_data=sample_patient_data
        )
        
        assert "recommended_tests" in decision_support
        assert "diagnostic_criteria" in decision_support
        assert "treatment_pathways" in decision_support
        assert "quality_measures" in decision_support

    # Test 14: Pediatric Considerations
    @pytest.mark.asyncio
    async def test_pediatric_considerations(self, diagnostic_service):
        """Test pediatric-specific diagnostic considerations."""
        pediatric_patient = {
            "age": 8,
            "gender": "female",
            "weight": 25,  # kg
            "symptoms": {"fever": {"severity": 7}, "cough": {"severity": 5}}
        }
        
        pediatric_analysis = await diagnostic_service.analyze_pediatric_case(pediatric_patient)
        
        assert "age_appropriate_diagnoses" in pediatric_analysis
        assert "dosing_considerations" in pediatric_analysis
        assert "developmental_factors" in pediatric_analysis

    # Test 15: Geriatric Considerations
    @pytest.mark.asyncio
    async def test_geriatric_considerations(self, diagnostic_service):
        """Test geriatric-specific diagnostic considerations."""
        geriatric_patient = {
            "age": 85,
            "gender": "female",
            "comorbidities": ["dementia", "osteoporosis", "atrial_fibrillation"],
            "medications": ["warfarin", "donepezil", "calcium"]
        }
        
        geriatric_analysis = await diagnostic_service.analyze_geriatric_case(geriatric_patient)
        
        assert "polypharmacy_risks" in geriatric_analysis
        assert "cognitive_considerations" in geriatric_analysis
        assert "fall_risk_assessment" in geriatric_analysis

    # Test 16: Rare Disease Detection
    @pytest.mark.asyncio
    async def test_rare_disease_detection(self, diagnostic_service):
        """Test rare disease detection capabilities."""
        unusual_symptoms = {
            "muscle_weakness": {"severity": 8, "pattern": "proximal"},
            "skin_rash": {"type": "heliotrope", "location": "eyelids"},
            "difficulty_swallowing": {"severity": 6}
        }
        
        rare_disease_analysis = await diagnostic_service.screen_rare_diseases(unusual_symptoms)
        
        assert "potential_rare_diseases" in rare_disease_analysis
        assert "specialist_referrals" in rare_disease_analysis
        assert "genetic_testing_recommendations" in rare_disease_analysis

    # Test 17: Quality Assurance
    @pytest.mark.asyncio
    async def test_quality_assurance(self, diagnostic_service, sample_symptoms, sample_patient_data):
        """Test diagnostic quality assurance."""
        diagnosis = "acute_myocardial_infarction"
        
        qa_results = await diagnostic_service.perform_quality_assurance(
            diagnosis=diagnosis,
            symptoms=sample_symptoms,
            patient_data=sample_patient_data
        )
        
        assert "diagnostic_accuracy_score" in qa_results
        assert "completeness_score" in qa_results
        assert "guideline_adherence" in qa_results
        assert "missing_information" in qa_results

    # Test 18: Bias Detection and Mitigation
    @pytest.mark.asyncio
    async def test_bias_detection(self, diagnostic_service):
        """Test bias detection in diagnostic recommendations."""
        # Test with different demographic groups
        patient_a = {"age": 45, "gender": "male", "race": "caucasian"}
        patient_b = {"age": 45, "gender": "female", "race": "african_american"}
        
        symptoms = {"chest_pain": {"severity": 7}}
        
        diagnosis_a = await diagnostic_service.analyze_symptoms(symptoms, patient_a)
        diagnosis_b = await diagnostic_service.analyze_symptoms(symptoms, patient_b)
        
        bias_analysis = await diagnostic_service.detect_diagnostic_bias(
            [diagnosis_a, diagnosis_b], [patient_a, patient_b]
        )
        
        assert "bias_score" in bias_analysis
        assert "fairness_metrics" in bias_analysis
        assert "recommendations" in bias_analysis

    # Test 19: Continuous Learning
    @pytest.mark.asyncio
    async def test_continuous_learning(self, diagnostic_service):
        """Test continuous learning from diagnostic outcomes."""
        diagnostic_case = {
            "symptoms": {"chest_pain": {"severity": 8}},
            "initial_diagnosis": "acute_myocardial_infarction",
            "final_diagnosis": "gastroesophageal_reflux",
            "outcome": "patient_improved"
        }
        
        learning_update = await diagnostic_service.update_from_outcome(diagnostic_case)
        
        assert "model_updates" in learning_update
        assert "confidence_adjustments" in learning_update
        assert "rule_modifications" in learning_update

    # Test 20: Performance Metrics
    @pytest.mark.asyncio
    async def test_performance_metrics(self, diagnostic_service):
        """Test diagnostic performance metrics calculation."""
        test_cases = [
            {"predicted": "pneumonia", "actual": "pneumonia", "confidence": 0.9},
            {"predicted": "bronchitis", "actual": "pneumonia", "confidence": 0.7},
            {"predicted": "pneumonia", "actual": "pneumonia", "confidence": 0.85}
        ]
        
        metrics = await diagnostic_service.calculate_performance_metrics(test_cases)
        
        assert "accuracy" in metrics
        assert "sensitivity" in metrics
        assert "specificity" in metrics
        assert "positive_predictive_value" in metrics
        assert "negative_predictive_value" in metrics
        assert "f1_score" in metrics


class TestAIDiagnosticServiceSpecialty:
    """Test specialty-specific diagnostic capabilities."""

    @pytest.fixture
    def diagnostic_service(self, mock_db_session):
        """AI Diagnostic service instance."""
        return AIDiagnosticService(mock_db_session)

    # Cardiology Tests
    @pytest.mark.asyncio
    async def test_cardiology_diagnosis(self, diagnostic_service):
        """Test cardiology-specific diagnostic capabilities."""
        cardiac_symptoms = {
            "chest_pain": {"type": "crushing", "radiation": "left_arm"},
            "shortness_of_breath": {"onset": "sudden"},
            "diaphoresis": {"severity": 8}
        }
        
        cardiac_analysis = await diagnostic_service.analyze_cardiac_symptoms(cardiac_symptoms)
        
        assert "acs_probability" in cardiac_analysis
        assert "heart_failure_risk" in cardiac_analysis
        assert "arrhythmia_likelihood" in cardiac_analysis

    # Neurology Tests
    @pytest.mark.asyncio
    async def test_neurology_diagnosis(self, diagnostic_service):
        """Test neurology-specific diagnostic capabilities."""
        neuro_symptoms = {
            "headache": {"type": "thunderclap", "severity": 10},
            "neck_stiffness": {"severity": 8},
            "photophobia": {"severity": 7}
        }
        
        neuro_analysis = await diagnostic_service.analyze_neurological_symptoms(neuro_symptoms)
        
        assert "stroke_risk" in neuro_analysis
        assert "meningitis_probability" in neuro_analysis
        assert "seizure_likelihood" in neuro_analysis

    # Pulmonology Tests
    @pytest.mark.asyncio
    async def test_pulmonology_diagnosis(self, diagnostic_service):
        """Test pulmonology-specific diagnostic capabilities."""
        pulm_symptoms = {
            "dyspnea": {"onset": "acute", "severity": 8},
            "chest_pain": {"type": "pleuritic"},
            "hemoptysis": {"severity": 5}
        }
        
        pulm_analysis = await diagnostic_service.analyze_pulmonary_symptoms(pulm_symptoms)
        
        assert "pe_probability" in pulm_analysis
        assert "pneumonia_likelihood" in pulm_analysis
        assert "pneumothorax_risk" in pulm_analysis

    # Gastroenterology Tests
    @pytest.mark.asyncio
    async def test_gastroenterology_diagnosis(self, diagnostic_service):
        """Test gastroenterology-specific diagnostic capabilities."""
        gi_symptoms = {
            "abdominal_pain": {"location": "epigastric", "severity": 7},
            "nausea": {"severity": 6},
            "vomiting": {"type": "bilious"}
        }
        
        gi_analysis = await diagnostic_service.analyze_gi_symptoms(gi_symptoms)
        
        assert "appendicitis_probability" in gi_analysis
        assert "cholecystitis_likelihood" in gi_analysis
        assert "bowel_obstruction_risk" in gi_analysis

