"""
AI Diagnostic Service - Enhanced diagnostic assistance with machine learning.
Optimized version based on MedIA Pro diagnostic AI capabilities.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DiagnosticConfidence(str, Enum):
    """Confidence levels for AI diagnostics."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DiagnosticCategory(str, Enum):
    """Categories of medical diagnoses."""
    CARDIOVASCULAR = "cardiovascular"
    RESPIRATORY = "respiratory"
    NEUROLOGICAL = "neurological"
    GASTROINTESTINAL = "gastrointestinal"
    INFECTIOUS = "infectious"
    ENDOCRINE = "endocrine"
    MUSCULOSKELETAL = "musculoskeletal"
    DERMATOLOGICAL = "dermatological"
    PSYCHIATRIC = "psychiatric"
    OTHER = "other"


class AIDiagnosticService:
    """Service for AI-powered diagnostic assistance."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.diagnostic_models = self._initialize_diagnostic_models()
        self.symptom_patterns = self._initialize_symptom_patterns()

    def _initialize_diagnostic_models(self) -> dict[str, dict[str, Any]]:
        """Initialize diagnostic AI models configuration."""
        return {
            "cardiovascular": {
                "model_name": "cardio_diagnostic_v2",
                "confidence_threshold": 0.7,
                "features": ["chest_pain", "shortness_of_breath", "palpitations", "syncope"],
                "common_diagnoses": ["myocardial_infarction", "angina", "arrhythmia", "heart_failure"]
            },
            "respiratory": {
                "model_name": "respiratory_diagnostic_v1",
                "confidence_threshold": 0.65,
                "features": ["cough", "dyspnea", "chest_pain", "fever"],
                "common_diagnoses": ["pneumonia", "asthma", "copd", "pulmonary_embolism"]
            },
            "neurological": {
                "model_name": "neuro_diagnostic_v1",
                "confidence_threshold": 0.75,
                "features": ["headache", "weakness", "numbness", "confusion"],
                "common_diagnoses": ["stroke", "migraine", "seizure", "meningitis"]
            }
        }

    def _initialize_symptom_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize symptom pattern recognition."""
        return {
            "acute_coronary_syndrome": {
                "primary_symptoms": ["chest_pain", "shortness_of_breath"],
                "secondary_symptoms": ["nausea", "sweating", "arm_pain"],
                "risk_factors": ["age_over_50", "diabetes", "hypertension", "smoking"],
                "urgency": "critical",
                "confidence_boost": 0.2
            },
            "stroke": {
                "primary_symptoms": ["facial_droop", "arm_weakness", "speech_difficulty"],
                "secondary_symptoms": ["confusion", "vision_changes", "severe_headache"],
                "risk_factors": ["age_over_65", "atrial_fibrillation", "hypertension"],
                "urgency": "critical",
                "confidence_boost": 0.25
            },
            "sepsis": {
                "primary_symptoms": ["fever", "altered_mental_status", "hypotension"],
                "secondary_symptoms": ["tachycardia", "tachypnea", "oliguria"],
                "risk_factors": ["immunocompromised", "recent_surgery", "chronic_illness"],
                "urgency": "critical",
                "confidence_boost": 0.15
            }
        }

    async def generate_diagnostic_suggestions(
        self,
        patient_data: dict[str, Any],
        clinical_presentation: dict[str, Any],
        additional_context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Generate AI-powered diagnostic suggestions."""
        try:
            diagnostic_result = {
                "patient_id": patient_data.get("patient_id"),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "primary_suggestions": [],
                "differential_diagnoses": [],
                "confidence_summary": {
                    "overall_confidence": DiagnosticConfidence.MODERATE,
                    "model_agreement": 0.0,
                    "data_completeness": 0.0
                },
                "recommended_tests": [],
                "red_flags": [],
                "follow_up_recommendations": []
            }

            symptoms = clinical_presentation.get("symptoms", [])
            vital_signs = clinical_presentation.get("vital_signs", {})
            physical_exam = clinical_presentation.get("physical_exam", {})

            pattern_matches = await self._analyze_symptom_patterns(
                symptoms, patient_data, clinical_presentation
            )

            for category, model_config in self.diagnostic_models.items():
                category_suggestions = await self._generate_category_suggestions(
                    category, model_config, symptoms, patient_data, clinical_presentation
                )

                if category_suggestions:
                    diagnostic_result["differential_diagnoses"].extend(category_suggestions)

            for pattern_name, pattern_data in pattern_matches.items():
                if pattern_data["match_score"] > 0.6:
                    await self._apply_pattern_boost(
                        diagnostic_result, pattern_name, pattern_data
                    )

            diagnostic_result["differential_diagnoses"].sort(
                key=lambda x: x.get("confidence", 0), reverse=True
            )

            diagnostic_result["primary_suggestions"] = diagnostic_result["differential_diagnoses"][:3]

            diagnostic_result["recommended_tests"] = await self._generate_test_recommendations(
                diagnostic_result["primary_suggestions"], clinical_presentation
            )

            diagnostic_result["red_flags"] = await self._identify_red_flags(
                symptoms, vital_signs, physical_exam
            )

            diagnostic_result["confidence_summary"] = await self._calculate_confidence_summary(
                diagnostic_result["differential_diagnoses"]
            )

            logger.info(f"Generated diagnostic suggestions for patient {patient_data.get('patient_id')}")
            return diagnostic_result

        except Exception as e:
            logger.error(f"Error generating diagnostic suggestions: {str(e)}")
            return {
                "error": str(e),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

    async def _analyze_symptom_patterns(
        self,
        symptoms: list[str],
        patient_data: dict[str, Any],
        clinical_presentation: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Analyze symptoms against known patterns."""
        pattern_matches = {}

        for pattern_name, pattern_config in self.symptom_patterns.items():
            match_score = 0.0
            matched_symptoms = []

            primary_matches = 0
            for symptom in pattern_config["primary_symptoms"]:
                if symptom in symptoms:
                    primary_matches += 1
                    matched_symptoms.append(symptom)

            if len(pattern_config["primary_symptoms"]) > 0:
                primary_score = primary_matches / len(pattern_config["primary_symptoms"])
                match_score += primary_score * 0.7  # Primary symptoms weighted heavily

            secondary_matches = 0
            for symptom in pattern_config["secondary_symptoms"]:
                if symptom in symptoms:
                    secondary_matches += 1
                    matched_symptoms.append(symptom)

            if len(pattern_config["secondary_symptoms"]) > 0:
                secondary_score = secondary_matches / len(pattern_config["secondary_symptoms"])
                match_score += secondary_score * 0.2  # Secondary symptoms weighted less

            risk_factor_matches = 0
            patient_risk_factors = patient_data.get("risk_factors", [])
            for risk_factor in pattern_config["risk_factors"]:
                if risk_factor in patient_risk_factors:
                    risk_factor_matches += 1

            if len(pattern_config["risk_factors"]) > 0:
                risk_score = risk_factor_matches / len(pattern_config["risk_factors"])
                match_score += risk_score * 0.1  # Risk factors weighted least

            pattern_matches[pattern_name] = {
                "match_score": match_score,
                "matched_symptoms": matched_symptoms,
                "urgency": pattern_config["urgency"],
                "confidence_boost": pattern_config["confidence_boost"]
            }

        return pattern_matches

    async def _generate_category_suggestions(
        self,
        category: str,
        model_config: dict[str, Any],
        symptoms: list[str],
        patient_data: dict[str, Any],
        clinical_presentation: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate diagnostic suggestions for a specific category."""
        suggestions = []

        relevant_features = [f for f in model_config["features"] if f in symptoms]

        if len(relevant_features) >= 1:  # At least one relevant feature
            for diagnosis in model_config["common_diagnoses"]:
                base_confidence = len(relevant_features) / len(model_config["features"])

                age_factor = 1.0
                if patient_data.get("age", 0) > 65:
                    age_factor = 1.1  # Slightly higher confidence for older patients

                final_confidence = min(base_confidence * age_factor, 1.0)

                if final_confidence >= model_config["confidence_threshold"]:
                    suggestion = {
                        "diagnosis": diagnosis,
                        "category": category,
                        "confidence": final_confidence,
                        "supporting_features": relevant_features,
                        "icd10_code": self._get_icd10_code(diagnosis),
                        "urgency": self._determine_urgency(diagnosis, final_confidence)
                    }
                    suggestions.append(suggestion)

        return suggestions

    async def _apply_pattern_boost(
        self,
        diagnostic_result: dict[str, Any],
        pattern_name: str,
        pattern_data: dict[str, Any]
    ) -> None:
        """Apply confidence boost for pattern matches."""
        boost = pattern_data["confidence_boost"]

        for suggestion in diagnostic_result["differential_diagnoses"]:
            if pattern_name.replace("_", " ") in suggestion["diagnosis"].lower():
                suggestion["confidence"] = min(suggestion["confidence"] + boost, 1.0)
                suggestion["pattern_match"] = pattern_name

    async def _generate_test_recommendations(
        self,
        primary_suggestions: list[dict[str, Any]],
        clinical_presentation: dict[str, Any]
    ) -> list[str]:
        """Generate recommended diagnostic tests."""
        recommendations = []

        for suggestion in primary_suggestions:
            category = suggestion.get("category", "")
            diagnosis = suggestion.get("diagnosis", "")

            if category == "cardiovascular":
                recommendations.extend(["ECG", "Troponin levels", "Chest X-ray"])
            elif category == "respiratory":
                recommendations.extend(["Chest X-ray", "Arterial blood gas", "Sputum culture"])
            elif category == "neurological":
                recommendations.extend(["CT head", "MRI brain", "Lumbar puncture"])

            if "myocardial" in diagnosis.lower():
                recommendations.append("Cardiac catheterization")
            elif "stroke" in diagnosis.lower():
                recommendations.append("CT angiography")
            elif "sepsis" in diagnosis.lower():
                recommendations.extend(["Blood cultures", "Lactate level", "Procalcitonin"])

        return list(dict.fromkeys(recommendations))

    async def _identify_red_flags(
        self,
        symptoms: list[str],
        vital_signs: dict[str, Any],
        physical_exam: dict[str, Any]
    ) -> list[str]:
        """Identify clinical red flags requiring immediate attention."""
        red_flags = []

        if vital_signs.get("systolic_blood_pressure", 0) < 90:
            red_flags.append("Severe hypotension")

        if vital_signs.get("heart_rate", 0) > 120:
            red_flags.append("Severe tachycardia")

        if vital_signs.get("respiratory_rate", 0) > 30:
            red_flags.append("Severe tachypnea")

        if vital_signs.get("oxygen_saturation", 100) < 90:
            red_flags.append("Severe hypoxemia")

        critical_symptoms = [
            "chest_pain", "shortness_of_breath", "altered_mental_status",
            "severe_headache", "focal_neurological_deficit"
        ]

        for symptom in symptoms:
            if symptom in critical_symptoms:
                red_flags.append(f"Critical symptom: {symptom.replace('_', ' ')}")

        return red_flags

    async def _calculate_confidence_summary(
        self,
        differential_diagnoses: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate overall confidence summary."""
        if not differential_diagnoses:
            return {
                "overall_confidence": DiagnosticConfidence.VERY_LOW,
                "model_agreement": 0.0,
                "data_completeness": 0.5
            }

        confidences = [d.get("confidence", 0) for d in differential_diagnoses]
        avg_confidence = sum(confidences) / len(confidences)

        if avg_confidence >= 0.8:
            overall_confidence = DiagnosticConfidence.VERY_HIGH
        elif avg_confidence >= 0.7:
            overall_confidence = DiagnosticConfidence.HIGH
        elif avg_confidence >= 0.5:
            overall_confidence = DiagnosticConfidence.MODERATE
        elif avg_confidence >= 0.3:
            overall_confidence = DiagnosticConfidence.LOW
        else:
            overall_confidence = DiagnosticConfidence.VERY_LOW

        return {
            "overall_confidence": overall_confidence,
            "model_agreement": avg_confidence,
            "data_completeness": 0.8  # Would be calculated based on available data
        }

    def _get_icd10_code(self, diagnosis: str) -> str:
        """Get ICD-10 code for diagnosis (simplified mapping)."""
        icd10_mapping = {
            "myocardial_infarction": "I21.9",
            "angina": "I20.9",
            "arrhythmia": "I49.9",
            "heart_failure": "I50.9",
            "pneumonia": "J18.9",
            "asthma": "J45.9",
            "copd": "J44.1",
            "stroke": "I64",
            "migraine": "G43.9",
            "seizure": "G40.9"
        }
        return icd10_mapping.get(diagnosis, "Z00.00")

    def _determine_urgency(self, diagnosis: str, confidence: float) -> str:
        """Determine urgency level for diagnosis."""
        critical_diagnoses = [
            "myocardial_infarction", "stroke", "sepsis", "pulmonary_embolism"
        ]

        if diagnosis in critical_diagnoses and confidence > 0.7:
            return "critical"
        elif confidence > 0.8:
            return "high"
        elif confidence > 0.6:
            return "moderate"
        else:
            return "low"
