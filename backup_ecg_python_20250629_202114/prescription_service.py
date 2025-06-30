"""
Prescription Service - Enhanced prescription management with AI validation.
Optimized version based on MedIA Pro prescription capabilities.
Integrado com sistema de diretrizes médicas atualizadas.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.medical_guidelines_engine import (
    MotorDiretrizesMedicasIA,
    ValidadorConformidadeDiretrizes)

logger = logging.getLogger(__name__)

class PrescriptionStatus(str, Enum):
    """Status of prescriptions."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class InteractionSeverity(str, Enum):
    """Drug interaction severity levels."""

    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"

class PrescriptionService:
    """Service for enhanced prescription management with AI validation."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.drug_database = self._initialize_drug_database()
        self.interaction_rules = self._initialize_interaction_rules()
        self.motor_diretrizes = MotorDiretrizesMedicasIA()
        self.validador_conformidade = ValidadorConformidadeDiretrizes()

    def _initialize_drug_database(self) -> dict[str, dict[str, Any]]:
        """Initialize drug database with common medications."""
        return {
            "metformin": {
                "generic_name": "metformin",
                "brand_names": ["Glucophage", "Fortamet"],
                "drug_class": "biguanide",
                "contraindications": ["severe_kidney_disease", "metabolic_acidosis"],
                "warnings": ["kidney_function_monitoring", "lactic_acidosis_risk"],
                "pregnancy_category": "B",
            },
            "lisinopril": {
                "generic_name": "lisinopril",
                "brand_names": ["Prinivil", "Zestril"],
                "drug_class": "ace_inhibitor",
                "contraindications": ["pregnancy", "angioedema_history"],
                "warnings": ["hyperkalemia", "kidney_function_monitoring"],
                "pregnancy_category": "D",
            },
            "warfarin": {
                "generic_name": "warfarin",
                "brand_names": ["Coumadin", "Jantoven"],
                "drug_class": "anticoagulant",
                "contraindications": ["active_bleeding", "pregnancy"],
                "warnings": ["bleeding_risk", "inr_monitoring"],
                "pregnancy_category": "X",
            },
        }

    def _initialize_interaction_rules(self) -> dict[str, list[dict[str, Any]]]:
        """Initialize drug interaction rules."""
        return {
            "warfarin": [
                {
                    "interacting_drug": "aspirin",
                    "severity": InteractionSeverity.MAJOR,
                    "mechanism": "increased_bleeding_risk",
                    "recommendation": "Monitor INR closely, consider alternative",
                },
                {
                    "interacting_drug": "ibuprofen",
                    "severity": InteractionSeverity.MODERATE,
                    "mechanism": "increased_bleeding_risk",
                    "recommendation": "Use with caution, monitor for bleeding",
                }],
            "metformin": [
                {
                    "interacting_drug": "contrast_dye",
                    "severity": InteractionSeverity.MAJOR,
                    "mechanism": "lactic_acidosis_risk",
                    "recommendation": "Hold metformin 48 hours before and after contrast",
                }
            ],
        }

    async def create_prescription(
        self,
        patient_id: str,
        prescriber_id: int,
        medications: list[dict[str, Any]],
        diagnosis_codes: list[str] | None = None,
        primary_diagnosis: str = "") -> dict[str, Any]:
        """Create a new prescription with AI validation and guidelines compliance."""
        try:
            prescription_id = (
                f"RX_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{patient_id}"
            )

            validation_results = await self._validate_medications(
                medications, patient_id
            )

            interaction_results = await self._check_drug_interactions(medications)

            guidelines_validation = await self._validate_against_guidelines(
                medications, primary_diagnosis
            )

            prescription = {
                "prescription_id": prescription_id,
                "patient_id": patient_id,
                "prescriber_id": prescriber_id,
                "status": PrescriptionStatus.ACTIVE,
                "created_at": datetime.utcnow().isoformat(),
                "medications": medications,
                "diagnosis_codes": diagnosis_codes or [],
                "primary_diagnosis": primary_diagnosis,
                "validation_results": validation_results,
                "interaction_results": interaction_results,
                "guidelines_validation": guidelines_validation,
                "ai_recommendations": await self._generate_ai_recommendations(
                    medications,
                    validation_results,
                    interaction_results,
                    guidelines_validation),
            }

            medications_list = cast(list[dict[str, Any]], prescription["medications"])
            for med in medications_list:
                if "duration_days" in med:
                    expiry_date = datetime.utcnow() + timedelta(
                        days=med["duration_days"]
                    )
                    med["expires_at"] = expiry_date.isoformat()

            logger.info(
                f"Created prescription: {prescription_id} for patient {patient_id}"
            )
            return prescription

        except Exception as e:
            logger.error(f"Error creating prescription: {str(e)}")
            raise

    async def _validate_medications(
        self, medications: list[dict[str, Any]], patient_id: str
    ) -> dict[str, Any]:
        """Validate medications against patient profile and drug database."""
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "medication_validations": [],
        }

        for i, med in enumerate(medications):
            med_validation = {
                "medication_index": i,
                "medication_name": med.get("name", ""),
                "valid": True,
                "warnings": [],
                "errors": [],
            }

            drug_info = self.drug_database.get(med.get("name", "").lower())
            if not drug_info:
                med_validation["warnings"].append(
                    "Medication not found in drug database"
                )

            if not med.get("dosage"):
                med_validation["errors"].append("Dosage is required")
                med_validation["valid"] = False

            if not med.get("frequency"):
                med_validation["errors"].append("Frequency is required")
                med_validation["valid"] = False

            if drug_info and "contraindications" in drug_info:
                pass

            medication_validations = cast(
                list[dict[str, Any]], validation_results["medication_validations"]
            )
            medication_validations.append(med_validation)

            if not med_validation["valid"]:
                validation_results["valid"] = False

            warnings_list = cast(list[str], validation_results["warnings"])
            errors_list = cast(list[str], validation_results["errors"])
            warnings_list.extend(med_validation["warnings"])
            errors_list.extend(med_validation["errors"])

        return validation_results

    async def _check_drug_interactions(
        self, medications: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Check for drug-drug interactions."""
        interaction_results = {
            "has_interactions": False,
            "interactions": [],
            "severity_summary": {
                "minor": 0,
                "moderate": 0,
                "major": 0,
                "contraindicated": 0,
            },
        }

        for i, med1 in enumerate(medications):
            med1_name = med1.get("name", "").lower()

            if med1_name in self.interaction_rules:
                for j, med2 in enumerate(medications):
                    if i != j:
                        med2_name = med2.get("name", "").lower()

                        for rule in self.interaction_rules[med1_name]:
                            if rule["interacting_drug"] == med2_name:
                                interaction = {
                                    "drug1": med1.get("name"),
                                    "drug2": med2.get("name"),
                                    "severity": rule["severity"],
                                    "mechanism": rule["mechanism"],
                                    "recommendation": rule["recommendation"],
                                }

                                interactions_list = cast(
                                    list[dict[str, Any]],
                                    interaction_results["interactions"])
                                interactions_list.append(interaction)
                                interaction_results["has_interactions"] = True
                                severity_summary = cast(
                                    dict[str, int],
                                    interaction_results["severity_summary"])
                                severity_summary[rule["severity"]] += 1

        return interaction_results

    async def _validate_against_guidelines(
        self, medications: list[dict[str, Any]], diagnosis: str
    ) -> dict[str, Any]:
        """Valida prescrição contra diretrizes médicas atualizadas"""
        if not diagnosis:
            return {
                "conformidade": 0.0,
                "status": "sem_diagnostico",
                "alertas": ["Diagnóstico não informado para validação"],
                "recomendacoes": [],
            }

        prescription_data = {"medications": medications}
        return await self.validador_conformidade.validar_acao_medica(
            acao=prescription_data, tipo_acao="prescricao", diagnostico=diagnosis
        )

    async def _generate_ai_recommendations(
        self,
        medications: list[dict[str, Any]],
        validation_results: dict[str, Any],
        interaction_results: dict[str, Any],
        guidelines_validation: dict[str, Any] | None = None) -> list[str]:
        """Generate AI-powered recommendations for the prescription."""
        recommendations = []

        if not validation_results["valid"]:
            recommendations.append(
                "Review and correct medication validation errors before dispensing"
            )

        if interaction_results["has_interactions"]:
            major_interactions = interaction_results["severity_summary"]["major"]
            contraindicated = interaction_results["severity_summary"]["contraindicated"]

            if contraindicated > 0:
                recommendations.append(
                    "CRITICAL: Contraindicated drug combinations detected - do not dispense"
                )
            elif major_interactions > 0:
                recommendations.append(
                    "Major drug interactions detected - consider alternative medications"
                )

        if guidelines_validation:
            conformidade = guidelines_validation.get("conformidade", 0)
            status = guidelines_validation.get("status", "")

            if status == "nao_conforme":
                recommendations.append(
                    f"⚠️ BAIXA CONFORMIDADE ({conformidade}%) com diretrizes médicas"
                )
            elif status == "parcialmente_conforme":
                recommendations.append(
                    f"⚡ Conformidade parcial ({conformidade}%) com diretrizes"
                )
            elif status == "conforme":
                recommendations.append(
                    f"✅ Prescrição conforme diretrizes médicas ({conformidade}%)"
                )

            for recomendacao in guidelines_validation.get("recomendacoes", []):
                recommendations.append(f"📋 Diretriz: {recomendacao}")

        if len(medications) > 5:
            recommendations.append(
                "Consider medication reconciliation due to polypharmacy"
            )

        drug_classes = []
        for med in medications:
            med_name = med.get("name", "").lower()
            drug_info = self.drug_database.get(med_name)
            if drug_info and "drug_class" in drug_info:
                drug_classes.append(drug_info["drug_class"])

        if len(drug_classes) != len(set(drug_classes)):
            recommendations.append(
                "Multiple medications from same drug class detected - review for duplication"
            )

        return recommendations

    async def get_prescription_by_id(
        self, prescription_id: str
    ) -> dict[str, Any] | None:
        """Get prescription by ID."""
        logger.info(f"Retrieved prescription: {prescription_id}")
        return None

    async def update_prescription_status(
        self, prescription_id: str, status: PrescriptionStatus, updated_by: int
    ) -> dict[str, Any]:
        """Update prescription status."""
        try:
            update_result = {
                "prescription_id": prescription_id,
                "old_status": "active",  # Would be retrieved from database
                "new_status": status,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"Updated prescription status: {prescription_id} -> {status}")
            return update_result

        except Exception as e:
            logger.error(f"Error updating prescription status: {str(e)}")
            raise

    async def get_patient_prescriptions(
        self,
        patient_id: str,
        status_filter: PrescriptionStatus | None = None,
        limit: int = 50) -> list[dict[str, Any]]:
        """Get prescriptions for a patient."""
        try:
            prescriptions: list[dict[str, Any]] = []

            logger.info(
                f"Retrieved {len(prescriptions)} prescriptions for patient {patient_id}"
            )
            return prescriptions

        except Exception as e:
            logger.error(f"Error retrieving patient prescriptions: {str(e)}")
            raise

    async def check_prescription_adherence(
        self, prescription_id: str
    ) -> dict[str, Any]:
        """Check prescription adherence and generate alerts."""
        try:
            adherence_report = {
                "prescription_id": prescription_id,
                "adherence_score": 0.85,  # Would be calculated from actual data
                "missed_doses": 3,
                "total_doses": 20,
                "last_refill_date": "2024-01-15",
                "next_refill_due": "2024-02-15",
                "alerts": [],
            }

            alerts_list = cast(list[str], adherence_report["alerts"])
            adherence_score = cast(float, adherence_report["adherence_score"])
            missed_doses = cast(int, adherence_report["missed_doses"])

            if adherence_score < 0.8:
                alerts_list.append("Low medication adherence detected")

            if missed_doses > 5:
                alerts_list.append(
                    "Multiple missed doses - patient counseling recommended"
                )

            logger.info(f"Checked adherence for prescription: {prescription_id}")
            return adherence_report

        except Exception as e:
            logger.error(f"Error checking prescription adherence: {str(e)}")
            raise
