"""
Service for detecting multiple pathologies in ECG data.
"""

import logging
from typing import Any

import numpy as np

from app.core.constants import ClinicalUrgency, SCPCategory

logger = logging.getLogger(__name__)


class MultiPathologyService:
    """Service for detecting multiple pathologies in ECG data."""

    def __init__(self):
        """Initialize the multi-pathology service."""
        self.scp_conditions = {
            "NORM": "Normal ECG",
            "MI": "Myocardial Infarction",
            "STTC": "ST/T Change",
            "CD": "Conduction Disturbance",
            "HYP": "Hypertrophy",
            "AF": "Atrial Fibrillation",
            "AFIB": "Atrial Fibrillation",
            "AFL": "Atrial Flutter",
            "STEMI": "ST Elevation MI",
            "NSTEMI": "Non-ST Elevation MI",
            "VT": "Ventricular Tachycardia",
            "VF": "Ventricular Fibrillation",
            "SVT": "Supraventricular Tachycardia",
            "PAC": "Premature Atrial Contractions",
            "PVC": "Premature Ventricular Contractions",
        }
        logger.info("MultiPathologyService initialized with SCP conditions")

    async def analyze_hierarchical(
        self, signal: np.ndarray, features: dict[str, Any], preprocessing_quality: float
    ) -> dict[str, Any]:
        """Perform hierarchical analysis of ECG pathologies."""
        try:
            level1 = await self._level1_normal_vs_abnormal(signal, features)

            level2 = await self._level2_category_classification(signal, features)

            level3 = await self._level3_specific_diagnosis(
                signal, features, [level2.get("predicted_category", "NORMAL")]
            )

            clinical_urgency = self._determine_clinical_urgency(level3)

            return {
                "level1": level1,
                "level2": level2,
                "level3": level3,
                "preprocessing_quality": preprocessing_quality,
                "clinical_urgency": clinical_urgency,
            }
        except Exception as e:
            logger.error(f"Error in hierarchical analysis: {e}")
            return {
                "level1": {"is_normal": True, "confidence": 0.5},
                "level2": {"predicted_category": "NORMAL", "confidence": 0.5},
                "level3": {"specific_diagnoses": []},
                "preprocessing_quality": preprocessing_quality,
                "clinical_urgency": ClinicalUrgency.LOW.value,
            }

    async def _level1_normal_vs_abnormal(
        self, signal: np.ndarray, features: dict[str, Any]
    ) -> dict[str, Any]:
        """Level 1: Normal vs Abnormal classification."""
        try:
            heart_rate = features.get("heart_rate", 70)
            rr_std = features.get("rr_std", 50)
            qt_interval = features.get("qt_interval", 400)

            is_normal = (
                60 <= heart_rate <= 100 and rr_std < 100 and 350 <= qt_interval <= 450
            )

            confidence = 0.9 if is_normal else 0.8
            abnormality_score = 0.1 if is_normal else 0.8

            return {
                "is_normal": is_normal,
                "confidence": confidence,
                "abnormality_score": abnormality_score,
                "features_analyzed": ["heart_rate", "rr_std", "qt_interval"],
            }
        except Exception as e:
            logger.error(f"Error in level 1 analysis: {e}")
            return {
                "is_normal": True,
                "confidence": 0.5,
                "abnormality_score": 0.5,
                "features_analyzed": [],
            }

    async def _level2_category_classification(
        self, signal: np.ndarray, features: dict[str, Any]
    ) -> dict[str, Any]:
        """Level 2: Category classification."""
        try:
            heart_rate = features.get("heart_rate", 70)
            rr_std = features.get("rr_std", 50)
            pr_interval = features.get("pr_interval", 160)
            qrs_duration = features.get("qrs_duration", 100)

            if heart_rate > 150:
                category = SCPCategory.ARRHYTHMIA.value
                confidence = 0.9
            elif heart_rate < 50:
                category = SCPCategory.CONDUCTION_ABNORMALITIES.value
                confidence = 0.85
            elif rr_std > 200:
                category = SCPCategory.ARRHYTHMIA.value
                confidence = 0.8
            elif pr_interval > 200 or qrs_duration > 120:
                category = SCPCategory.CONDUCTION_ABNORMALITIES.value
                confidence = 0.8
            elif features.get("st_elevation", False):
                category = SCPCategory.ISCHEMIC_CHANGES.value
                confidence = 0.9
            else:
                category = SCPCategory.NORMAL.value
                confidence = 0.85

            category_scores = {category: confidence}

            return {
                "predicted_category": category,
                "confidence": confidence,
                "category_scores": category_scores,
                "features_used": [
                    "heart_rate",
                    "rr_std",
                    "pr_interval",
                    "qrs_duration",
                ],
            }
        except Exception as e:
            logger.error(f"Error in level 2 analysis: {e}")
            return {
                "predicted_category": SCPCategory.NORMAL.value,
                "confidence": 0.5,
                "category_scores": {SCPCategory.NORMAL.value: 0.5},
                "features_used": [],
            }

    async def _level3_specific_diagnosis(
        self, signal: np.ndarray, features: dict[str, Any], categories: list[str]
    ) -> dict[str, Any]:
        """Level 3: Specific diagnosis within categories."""
        try:
            diagnoses = []
            heart_rate = features.get("heart_rate", 70)

            for category in categories:
                if category == SCPCategory.ARRHYTHMIA.value:
                    if heart_rate > 150:
                        if features.get("irregular_rhythm", False):
                            diagnoses.append(
                                {
                                    "diagnosis": "Atrial Fibrillation",
                                    "confidence": 0.85,
                                    "icd10_code": "I48.9",
                                    "scp_code": "AFIB",
                                }
                            )
                        else:
                            diagnoses.append(
                                {
                                    "diagnosis": "Sinus Tachycardia",
                                    "confidence": 0.8,
                                    "icd10_code": "R00.0",
                                    "scp_code": "NORM",
                                }
                            )
                    elif heart_rate > 100:
                        diagnoses.append(
                            {
                                "diagnosis": "Supraventricular Tachycardia",
                                "confidence": 0.75,
                                "icd10_code": "I47.1",
                                "scp_code": "SVT",
                            }
                        )

                elif category == SCPCategory.CONDUCTION_ABNORMALITIES.value:
                    if heart_rate < 50:
                        diagnoses.append(
                            {
                                "diagnosis": "Sinus Bradycardia",
                                "confidence": 0.8,
                                "icd10_code": "R00.1",
                                "scp_code": "NORM",
                            }
                        )
                    elif features.get("pr_interval", 160) > 200:
                        diagnoses.append(
                            {
                                "diagnosis": "First Degree AV Block",
                                "confidence": 0.85,
                                "icd10_code": "I44.0",
                                "scp_code": "CD",
                            }
                        )

                elif category == SCPCategory.ISCHEMIC_CHANGES.value:
                    if features.get("st_elevation", False):
                        diagnoses.append(
                            {
                                "diagnosis": "ST Elevation Myocardial Infarction",
                                "confidence": 0.9,
                                "icd10_code": "I21.9",
                                "scp_code": "STEMI",
                            }
                        )
                    else:
                        diagnoses.append(
                            {
                                "diagnosis": "Non-ST Elevation Myocardial Infarction",
                                "confidence": 0.8,
                                "icd10_code": "I21.4",
                                "scp_code": "NSTEMI",
                            }
                        )

                elif category == SCPCategory.HYPERTROPHY.value:
                    diagnoses.append(
                        {
                            "diagnosis": "Left Ventricular Hypertrophy",
                            "confidence": 0.75,
                            "icd10_code": "I51.7",
                            "scp_code": "HYP",
                        }
                    )

            primary_diagnosis = diagnoses[0] if diagnoses else None

            return {
                "specific_diagnoses": diagnoses,
                "primary_diagnosis": primary_diagnosis,
                "total_diagnoses": len(diagnoses),
            }
        except Exception as e:
            logger.error(f"Error in level 3 analysis: {e}")
            return {
                "specific_diagnoses": [],
                "primary_diagnosis": None,
                "total_diagnoses": 0,
            }

    def _determine_clinical_urgency(self, level3_results: dict[str, Any]) -> str:
        """Determine clinical urgency based on diagnoses."""
        try:
            diagnoses = level3_results.get("specific_diagnoses", [])

            for diagnosis in diagnoses:
                diagnosis_name = diagnosis.get("diagnosis", "").lower()
                scp_code = diagnosis.get("scp_code", "")

                if any(
                    critical in diagnosis_name
                    for critical in [
                        "stemi",
                        "ventricular fibrillation",
                        "ventricular tachycardia",
                    ]
                ):
                    return ClinicalUrgency.CRITICAL.value
                elif scp_code in ["STEMI", "VF", "VT"]:
                    return ClinicalUrgency.CRITICAL.value
                elif (
                    "tachycardia" in diagnosis_name
                    and diagnosis.get("confidence", 0) > 0.8
                ):
                    return ClinicalUrgency.HIGH.value
                elif any(
                    moderate in diagnosis_name
                    for moderate in ["fibrillation", "block", "nstemi"]
                ):
                    return ClinicalUrgency.MEDIUM.value

            return ClinicalUrgency.LOW.value
        except Exception as e:
            logger.error(f"Error determining clinical urgency: {e}")
            return ClinicalUrgency.LOW.value

    def detect_multi_pathology(self, ecg_data: Any, **kwargs: Any) -> dict[str, Any]:
        """Detect multiple pathologies in ECG data."""
        try:
            results = {
                "pathologies": [],
                "confidence": 0.0,
                "total_pathologies": 0,
                "primary_pathology": None,
            }
            if ecg_data is not None:
                if hasattr(ecg_data, "shape") and len(ecg_data.shape) >= 2:
                    mean_amplitude = np.mean(np.abs(ecg_data))
                    if mean_amplitude > 1.5:  # Arbitrary threshold
                        results["pathologies"].append(
                            {
                                "name": "High Amplitude Variation",
                                "confidence": 0.7,
                                "type": "amplitude_anomaly",
                            }
                        )
                        results["confidence"] = 0.7
                        results["total_pathologies"] = 1
                        results["primary_pathology"] = "High Amplitude Variation"

            return results
        except Exception as e:
            logger.error(f"Error in multi-pathology detection: {e}")
            return {
                "pathologies": [],
                "confidence": 0.0,
                "total_pathologies": 0,
                "primary_pathology": None,
            }
