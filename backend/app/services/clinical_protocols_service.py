"""
Clinical Protocols Service - AI-powered clinical protocol detection and assessment.
Optimized version based on MedIA Pro clinical protocols module.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class ProtocolType(str, Enum):
    """Types of clinical protocols."""
    SEPSIS = "sepsis"
    CHEST_PAIN = "chest_pain"
    STROKE = "stroke"
    VTE = "venous_thromboembolism"
    DKA = "diabetic_ketoacidosis"
    ACS = "acute_coronary_syndrome"
    HEART_FAILURE = "heart_failure"
    PNEUMONIA = "pneumonia"

class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class ClinicalProtocolsService:
    """Service for clinical protocol detection and assessment."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.protocol_definitions = self._initialize_protocols()

    def _initialize_protocols(self) -> dict[str, dict[str, Any]]:
        """Initialize clinical protocol definitions."""
        return {
            ProtocolType.SEPSIS: {
                "name": "Sepsis Detection Protocol",
                "criteria": {
                    "vital_signs": ["temperature", "heart_rate", "respiratory_rate", "blood_pressure"],
                    "lab_values": ["white_blood_cell_count", "lactate", "procalcitonin"],
                    "clinical_signs": ["altered_mental_status", "hypotension", "organ_dysfunction"]
                },
                "scoring_system": "qSOFA",
                "time_sensitive": True,
                "max_response_time_minutes": 60
            },
            ProtocolType.CHEST_PAIN: {
                "name": "Chest Pain Assessment Protocol",
                "criteria": {
                    "symptoms": ["chest_pain_character", "radiation", "duration"],
                    "risk_factors": ["age", "gender", "diabetes", "hypertension", "smoking"],
                    "ecg_findings": ["st_elevation", "st_depression", "t_wave_changes"],
                    "biomarkers": ["troponin", "ck_mb"]
                },
                "scoring_system": "HEART",
                "time_sensitive": True,
                "max_response_time_minutes": 30
            },
            ProtocolType.STROKE: {
                "name": "Stroke Assessment Protocol",
                "criteria": {
                    "neurological": ["facial_droop", "arm_weakness", "speech_difficulty"],
                    "timing": ["symptom_onset", "last_known_well"],
                    "imaging": ["ct_scan", "mri"],
                    "contraindications": ["bleeding_risk", "recent_surgery"]
                },
                "scoring_system": "NIHSS",
                "time_sensitive": True,
                "max_response_time_minutes": 15
            }
        }

    async def assess_protocol(
        self,
        protocol_type: ProtocolType,
        patient_data: dict[str, Any],
        clinical_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Assess a specific clinical protocol for a patient."""
        try:
            protocol_def = self.protocol_definitions.get(protocol_type)
            if not protocol_def:
                raise ValueError(f"Unknown protocol type: {protocol_type}")

            assessment = {
                "protocol_type": protocol_type,
                "protocol_name": protocol_def["name"],
                "assessment_timestamp": datetime.utcnow().isoformat(),
                "applicable": False,
                "risk_level": RiskLevel.LOW,
                "score": 0,
                "recommendations": [],
                "time_sensitive": protocol_def.get("time_sensitive", False),
                "max_response_time_minutes": protocol_def.get("max_response_time_minutes"),
                "criteria_met": {},
                "next_steps": []
            }

            if protocol_type == ProtocolType.SEPSIS:
                assessment = await self._assess_sepsis_protocol(patient_data, clinical_data, assessment)
            elif protocol_type == ProtocolType.CHEST_PAIN:
                assessment = await self._assess_chest_pain_protocol(patient_data, clinical_data, assessment)
            elif protocol_type == ProtocolType.STROKE:
                assessment = await self._assess_stroke_protocol(patient_data, clinical_data, assessment)

            return assessment

        except Exception as e:
            logger.error(f"Error assessing protocol {protocol_type}: {str(e)}")
            return {
                "protocol_type": protocol_type,
                "error": str(e),
                "assessment_timestamp": datetime.utcnow().isoformat()
            }

    async def _assess_sepsis_protocol(
        self,
        patient_data: dict[str, Any],
        clinical_data: dict[str, Any],
        assessment: dict[str, Any]
    ) -> dict[str, Any]:
        """Assess sepsis protocol using qSOFA criteria."""
        qsofa_score = 0
        criteria_met = {}

        vital_signs = clinical_data.get("vital_signs", {})
        lab_values = clinical_data.get("lab_values", {})

        systolic_bp = vital_signs.get("systolic_blood_pressure")
        if systolic_bp and systolic_bp <= 100:
            qsofa_score += 1
            criteria_met["hypotension"] = True

        respiratory_rate = vital_signs.get("respiratory_rate")
        if respiratory_rate and respiratory_rate >= 22:
            qsofa_score += 1
            criteria_met["tachypnea"] = True

        gcs = clinical_data.get("glasgow_coma_scale")
        if gcs and gcs < 15:
            qsofa_score += 1
            criteria_met["altered_mental_status"] = True

        temperature = vital_signs.get("temperature")
        if temperature and (temperature > 38.3 or temperature < 36.0):
            criteria_met["fever_hypothermia"] = True

        heart_rate = vital_signs.get("heart_rate")
        if heart_rate and heart_rate > 90:
            criteria_met["tachycardia"] = True

        wbc = lab_values.get("white_blood_cell_count")
        if wbc and (wbc > 12000 or wbc < 4000):
            criteria_met["abnormal_wbc"] = True

        lactate = lab_values.get("lactate")
        if lactate and lactate > 2.0:
            criteria_met["elevated_lactate"] = True

        assessment["score"] = qsofa_score
        assessment["criteria_met"] = criteria_met
        assessment["applicable"] = qsofa_score >= 2 or len(criteria_met) >= 3

        if qsofa_score >= 2:
            assessment["risk_level"] = RiskLevel.HIGH
            assessment["recommendations"].extend([
                "Immediate sepsis bundle initiation",
                "Blood cultures before antibiotics",
                "Broad-spectrum antibiotics within 1 hour",
                "Fluid resuscitation",
                "Serial lactate monitoring"
            ])
        elif len(criteria_met) >= 3:
            assessment["risk_level"] = RiskLevel.MODERATE
            assessment["recommendations"].extend([
                "Close monitoring for sepsis progression",
                "Consider blood cultures",
                "Monitor vital signs every 15 minutes"
            ])

        return assessment

    async def _assess_chest_pain_protocol(
        self,
        patient_data: dict[str, Any],
        clinical_data: dict[str, Any],
        assessment: dict[str, Any]
    ) -> dict[str, Any]:
        """Assess chest pain protocol using HEART score."""
        heart_score = 0
        criteria_met = {}

        age = patient_data.get("age", 0)
        if age >= 65:
            heart_score += 2
            criteria_met["high_risk_age"] = True
        elif age >= 45:
            heart_score += 1
            criteria_met["moderate_risk_age"] = True

        risk_factors = patient_data.get("risk_factors", [])
        risk_factor_count = len([rf for rf in risk_factors if rf in ["diabetes", "hypertension", "smoking", "hyperlipidemia"]])
        if risk_factor_count >= 3:
            heart_score += 2
            criteria_met["multiple_risk_factors"] = True
        elif risk_factor_count >= 1:
            heart_score += 1
            criteria_met["some_risk_factors"] = True

        if ecg_findings.get("st_elevation"):
            heart_score += 2
            criteria_met["st_elevation"] = True
        elif ecg_findings.get("st_depression") or ecg_findings.get("t_wave_changes"):
            heart_score += 1
            criteria_met["ecg_changes"] = True

        assessment["score"] = heart_score
        assessment["criteria_met"] = criteria_met
        assessment["applicable"] = heart_score >= 4

        if heart_score >= 7:
            assessment["risk_level"] = RiskLevel.HIGH
            assessment["recommendations"].extend([
                "Immediate cardiology consultation",
                "Serial troponins",
                "Consider cardiac catheterization"
            ])
        elif heart_score >= 4:
            assessment["risk_level"] = RiskLevel.MODERATE
            assessment["recommendations"].extend([
                "Observation and serial ECGs",
                "Troponin monitoring",
                "Stress testing if stable"
            ])

        return assessment

    async def _assess_stroke_protocol(
        self,
        patient_data: dict[str, Any],
        clinical_data: dict[str, Any],
        assessment: dict[str, Any]
    ) -> dict[str, Any]:
        """Assess stroke protocol using NIHSS criteria."""
        nihss_score = 0
        criteria_met = {}

        neurological = clinical_data.get("neurological", {})

        if neurological.get("facial_droop"):
            nihss_score += 2
            criteria_met["facial_droop"] = True

        if neurological.get("arm_weakness"):
            nihss_score += 2
            criteria_met["arm_weakness"] = True

        if neurological.get("speech_difficulty"):
            nihss_score += 2
            criteria_met["speech_difficulty"] = True

        timing = clinical_data.get("timing", {})
        symptom_onset = timing.get("symptom_onset")
        if symptom_onset and symptom_onset <= 4.5:
            criteria_met["within_window"] = True

        assessment["score"] = nihss_score
        assessment["criteria_met"] = criteria_met
        assessment["applicable"] = nihss_score >= 2

        if nihss_score >= 4 and criteria_met.get("within_window"):
            assessment["risk_level"] = RiskLevel.HIGH
            assessment["recommendations"].extend([
                "Immediate stroke team activation",
                "CT/MRI imaging",
                "Consider thrombolytic therapy"
            ])
        elif nihss_score >= 2:
            assessment["risk_level"] = RiskLevel.MODERATE
            assessment["recommendations"].extend([
                "Neurological monitoring",
                "Imaging studies",
                "Stroke workup"
            ])

        return assessment

    async def get_applicable_protocols(
        self,
        patient_data: dict[str, Any],
        clinical_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Get all applicable protocols for a patient."""
        applicable_protocols = []

        for protocol_type in ProtocolType:
            try:
                assessment = await self.assess_protocol(protocol_type, patient_data, clinical_data)
                if assessment.get("applicable", False):
                    applicable_protocols.append(assessment)
            except Exception as e:
                logger.error(f"Error assessing protocol {protocol_type}: {str(e)}")

        risk_order = {RiskLevel.CRITICAL: 4, RiskLevel.HIGH: 3, RiskLevel.MODERATE: 2, RiskLevel.LOW: 1}
        applicable_protocols.sort(
            key=lambda x: (risk_order.get(x.get("risk_level", RiskLevel.LOW), 0), x.get("time_sensitive", False)),
            reverse=True
        )

        return applicable_protocols
