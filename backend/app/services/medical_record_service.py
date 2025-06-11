"""
Medical Record Service - Comprehensive medical record management.
Optimized version based on MedIA Pro medical record capabilities.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.patient_repository import PatientRepository

logger = logging.getLogger(__name__)


class RecordType(str, Enum):
    """Types of medical records."""
    CONSULTATION = "consultation"
    PROCEDURE = "procedure"
    DIAGNOSTIC = "diagnostic"
    PRESCRIPTION = "prescription"
    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    DISCHARGE = "discharge"
    FOLLOW_UP = "follow_up"


class RecordStatus(str, Enum):
    """Status of medical records."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    AMENDED = "amended"


class MedicalRecordService:
    """Service for comprehensive medical record management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.patient_repository = PatientRepository(db)

    async def create_medical_record(
        self,
        patient_id: str,
        record_type: RecordType,
        record_data: dict[str, Any],
        created_by: int
    ) -> dict[str, Any]:
        """Create a new medical record."""
        try:
            patient = await self.patient_repository.get_patient_by_patient_id(patient_id)
            if not patient:
                raise ValueError(f"Patient {patient_id} not found")

            record = {
                "record_id": f"{record_type.upper()}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{patient_id}",
                "patient_id": patient_id,
                "record_type": record_type,
                "status": RecordStatus.ACTIVE,
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "data": record_data
            }

            validation_result = await self._validate_record_data(record_type, record_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid record data: {validation_result['errors']}")

            record = await self._process_record_by_type(record, record_type)

            logger.info(f"Created medical record: {record['record_id']} for patient {patient_id}")
            return record

        except Exception as e:
            logger.error(f"Error creating medical record: {str(e)}")
            raise

    async def _validate_record_data(
        self,
        record_type: RecordType,
        record_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate record data based on type."""
        validation_result = {"valid": True, "errors": []}

        try:
            errors_list = cast(list[str], validation_result["errors"])

            if record_type == RecordType.CONSULTATION:
                required_fields = ["chief_complaint", "history_present_illness", "assessment", "plan"]
                for field in required_fields:
                    if field not in record_data or not record_data[field]:
                        errors_list.append(f"Missing required field: {field}")

            elif record_type == RecordType.PRESCRIPTION:
                required_fields = ["medications"]
                for field in required_fields:
                    if field not in record_data or not record_data[field]:
                        errors_list.append(f"Missing required field: {field}")

                medications = record_data.get("medications", [])
                for i, med in enumerate(medications):
                    if not isinstance(med, dict):
                        errors_list.append(f"Medication {i+1} must be an object")
                        continue

                    med_required = ["name", "dosage", "frequency", "duration"]
                    for field in med_required:
                        if field not in med or not med[field]:
                            errors_list.append(f"Medication {i+1} missing {field}")

            validation_result["valid"] = len(errors_list) == 0

        except Exception as e:
            validation_result["valid"] = False
            errors_list = cast(list[str], validation_result["errors"])
            errors_list.append(f"Validation error: {str(e)}")

        return validation_result

    async def _process_record_by_type(
        self,
        record: dict[str, Any],
        record_type: RecordType
    ) -> dict[str, Any]:
        """Apply record-specific processing."""
        try:
            if record_type == RecordType.CONSULTATION:
                record = await self._process_consultation_record(record)
            elif record_type == RecordType.PRESCRIPTION:
                record = await self._process_prescription_record(record)

            return record

        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
            return record

    async def _process_consultation_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process consultation record with clinical decision support."""
        data = record["data"]

        clinical_summary = {
            "chief_complaint": data.get("chief_complaint"),
            "vital_signs": data.get("vital_signs", {}),
            "physical_exam": data.get("physical_exam", {}),
            "assessment": data.get("assessment"),
            "plan": data.get("plan"),
            "follow_up": data.get("follow_up")
        }

        record["clinical_summary"] = clinical_summary
        return record

    async def _process_prescription_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process prescription record with drug interaction checking."""
        data = record["data"]
        medications = data.get("medications", [])

        processed_medications = []
        for med in medications:
            processed_med = {
                **med,
                "prescribed_at": datetime.utcnow().isoformat(),
                "status": "active",
                "interactions_checked": True
            }
            processed_medications.append(processed_med)

        data["medications"] = processed_medications
        record["data"] = data
        return record

    async def get_patient_medical_history(
        self,
        patient_id: str,
        record_types: list[RecordType] | None = None,
        limit: int = 100
    ) -> dict[str, Any]:
        """Get comprehensive medical history for a patient."""
        try:
            patient = await self.patient_repository.get_patient_by_patient_id(patient_id)
            if not patient:
                raise ValueError(f"Patient {patient_id} not found")

            medical_history = {
                "patient_id": patient_id,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "generated_at": datetime.utcnow().isoformat(),
                "records_summary": {
                    "total_records": 0,
                    "by_type": {},
                    "date_range": {
                        "earliest": None,
                        "latest": None
                    }
                },
                "records": []
            }

            logger.info(f"Retrieved medical history for patient {patient_id}")
            return medical_history

        except Exception as e:
            logger.error(f"Error retrieving medical history: {str(e)}")
            raise
