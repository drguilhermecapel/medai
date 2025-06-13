"""Test AI diagnostic service."""


import pytest

from app.services.ai_diagnostic_service import (
    AIDiagnosticService,
    DiagnosticCategory,
    DiagnosticConfidence,
)


@pytest.fixture
def ai_diagnostic_service(test_db):
    """Create AI diagnostic service instance."""
    return AIDiagnosticService(test_db)


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "patient_id": "PAT123456",
        "age": 45,
        "gender": "male",
        "medical_history": ["hypertension", "diabetes"],
        "risk_factors": ["smoking", "family_history"]
    }


@pytest.fixture
def sample_clinical_presentation():
    """Sample clinical presentation data for testing."""
    return {
        "chief_complaint": "chest pain",
        "symptoms": ["chest_pain", "shortness_of_breath", "fatigue"],
        "vital_signs": {
            "systolic_blood_pressure": 140,
            "heart_rate": 85,
            "temperature": 98.6,
            "respiratory_rate": 16,
            "oxygen_saturation": 98
        },
        "physical_exam": {
            "cardiovascular": "regular rhythm, no murmurs",
            "respiratory": "clear to auscultation"
        }
    }


@pytest.mark.asyncio
async def test_generate_diagnostic_suggestions_success(ai_diagnostic_service, sample_patient_data, sample_clinical_presentation):
    """Test successful diagnostic suggestion generation."""
    result = await ai_diagnostic_service.generate_diagnostic_suggestions(
        sample_patient_data, sample_clinical_presentation
    )

    assert isinstance(result, dict)
    assert "patient_id" in result
    assert "analysis_timestamp" in result
    assert "primary_suggestions" in result
    assert "differential_diagnoses" in result
    assert "confidence_summary" in result
    assert "recommended_tests" in result
    assert "red_flags" in result
    assert "follow_up_recommendations" in result
    assert isinstance(result["primary_suggestions"], list)
    assert isinstance(result["differential_diagnoses"], list)


@pytest.mark.asyncio
async def test_analyze_symptom_patterns(ai_diagnostic_service, sample_patient_data, sample_clinical_presentation):
    """Test symptom pattern analysis."""
    symptoms = ["chest_pain", "shortness_of_breath", "fatigue"]
    patterns = await ai_diagnostic_service._analyze_symptom_patterns(
        symptoms, sample_patient_data, sample_clinical_presentation
    )

    assert isinstance(patterns, dict)
    for _pattern_name, pattern_data in patterns.items():
        assert "match_score" in pattern_data
        assert "matched_symptoms" in pattern_data
        assert "urgency" in pattern_data
        assert "confidence_boost" in pattern_data


@pytest.mark.asyncio
async def test_generate_category_suggestions(ai_diagnostic_service, sample_patient_data, sample_clinical_presentation):
    """Test category-specific diagnostic suggestions."""
    symptoms = ["chest_pain", "shortness_of_breath"]
    model_config = {
        "features": ["chest_pain", "shortness_of_breath", "fatigue"],
        "common_diagnoses": ["myocardial_infarction", "angina"],
        "confidence_threshold": 0.3
    }

    suggestions = await ai_diagnostic_service._generate_category_suggestions(
        "cardiovascular", model_config, symptoms, sample_patient_data, sample_clinical_presentation
    )

    assert isinstance(suggestions, list)
    for suggestion in suggestions:
        assert "diagnosis" in suggestion
        assert "category" in suggestion
        assert "confidence" in suggestion
        assert "supporting_features" in suggestion
        assert "icd10_code" in suggestion
        assert "urgency" in suggestion


@pytest.mark.asyncio
async def test_apply_pattern_boost(ai_diagnostic_service):
    """Test pattern confidence boost application."""
    diagnostic_result = {
        "differential_diagnoses": [
            {"diagnosis": "Myocardial Infarction", "confidence": 0.6}
        ]
    }
    pattern_data = {"confidence_boost": 0.2}

    await ai_diagnostic_service._apply_pattern_boost(
        diagnostic_result, "myocardial", pattern_data
    )

    assert diagnostic_result["differential_diagnoses"][0]["confidence"] == 0.8


@pytest.mark.asyncio
async def test_generate_test_recommendations(ai_diagnostic_service, sample_clinical_presentation):
    """Test diagnostic test recommendations."""
    primary_suggestions = [
        {"category": "cardiovascular", "diagnosis": "myocardial_infarction", "confidence": 0.8}
    ]

    tests = await ai_diagnostic_service._generate_test_recommendations(
        primary_suggestions, sample_clinical_presentation
    )

    assert isinstance(tests, list)
    assert len(tests) > 0
    for test in tests:
        assert isinstance(test, str)


@pytest.mark.asyncio
async def test_identify_red_flags(ai_diagnostic_service):
    """Test red flag identification."""
    symptoms = ["chest_pain", "shortness_of_breath"]
    vital_signs = {
        "systolic_blood_pressure": 85,  # Hypotension
        "heart_rate": 125,  # Tachycardia
        "respiratory_rate": 35,  # Tachypnea
        "oxygen_saturation": 85  # Hypoxemia
    }
    physical_exam = {}

    red_flags = await ai_diagnostic_service._identify_red_flags(
        symptoms, vital_signs, physical_exam
    )

    assert isinstance(red_flags, list)
    assert len(red_flags) > 0
    for flag in red_flags:
        assert isinstance(flag, str)


@pytest.mark.asyncio
async def test_calculate_confidence_summary(ai_diagnostic_service):
    """Test confidence summary calculation."""
    differential_diagnoses = [
        {"confidence": 0.8},
        {"confidence": 0.6},
        {"confidence": 0.4}
    ]

    summary = await ai_diagnostic_service._calculate_confidence_summary(differential_diagnoses)

    assert isinstance(summary, dict)
    assert "overall_confidence" in summary
    assert "model_agreement" in summary
    assert "data_completeness" in summary
    assert isinstance(summary["overall_confidence"], DiagnosticConfidence)


@pytest.mark.asyncio
async def test_get_icd10_code(ai_diagnostic_service):
    """Test ICD-10 code mapping."""
    code = ai_diagnostic_service._get_icd10_code("myocardial_infarction")
    assert code == "I21.9"

    code = ai_diagnostic_service._get_icd10_code("unknown_diagnosis")
    assert code == "Z00.00"


@pytest.mark.asyncio
async def test_determine_urgency(ai_diagnostic_service):
    """Test urgency level determination."""
    urgency = ai_diagnostic_service._determine_urgency("myocardial_infarction", 0.8)
    assert urgency == "critical"

    urgency = ai_diagnostic_service._determine_urgency("common_cold", 0.5)
    assert urgency == "low"


@pytest.mark.asyncio
async def test_empty_patient_data_handling(ai_diagnostic_service):
    """Test handling of empty patient data."""
    result = await ai_diagnostic_service.generate_diagnostic_suggestions({}, {})

    assert isinstance(result, dict)
    assert "primary_suggestions" in result
    assert "differential_diagnoses" in result
    assert isinstance(result["primary_suggestions"], list)


@pytest.mark.asyncio
async def test_service_initialization(ai_diagnostic_service):
    """Test service initialization."""
    assert hasattr(ai_diagnostic_service, 'diagnostic_models')
    assert hasattr(ai_diagnostic_service, 'symptom_patterns')
    assert isinstance(ai_diagnostic_service.diagnostic_models, dict)
    assert isinstance(ai_diagnostic_service.symptom_patterns, dict)


@pytest.mark.asyncio
async def test_diagnostic_confidence_enum():
    """Test diagnostic confidence enum values."""
    assert DiagnosticConfidence.VERY_LOW.value == "very_low"
    assert DiagnosticConfidence.LOW.value == "low"
    assert DiagnosticConfidence.MODERATE.value == "moderate"
    assert DiagnosticConfidence.HIGH.value == "high"
    assert DiagnosticConfidence.VERY_HIGH.value == "very_high"


@pytest.mark.asyncio
async def test_diagnostic_category_enum():
    """Test diagnostic category enum values."""
    assert DiagnosticCategory.CARDIOVASCULAR.value == "cardiovascular"
    assert DiagnosticCategory.RESPIRATORY.value == "respiratory"
    assert DiagnosticCategory.NEUROLOGICAL.value == "neurological"
    assert DiagnosticCategory.GASTROINTESTINAL.value == "gastrointestinal"
    assert DiagnosticCategory.ENDOCRINE.value == "endocrine"
    assert DiagnosticCategory.INFECTIOUS.value == "infectious"
    assert DiagnosticCategory.OTHER.value == "other"


@pytest.mark.asyncio
async def test_error_handling(ai_diagnostic_service):
    """Test error handling in diagnostic suggestions."""
    invalid_patient_data = {"age": "invalid"}
    invalid_clinical_data = {"symptoms": "not_a_list"}

    result = await ai_diagnostic_service.generate_diagnostic_suggestions(
        invalid_patient_data, invalid_clinical_data
    )

    assert isinstance(result, dict)
    assert "error" in result or "primary_suggestions" in result
