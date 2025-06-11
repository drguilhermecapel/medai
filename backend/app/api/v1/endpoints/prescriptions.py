"""
Prescription management endpoints.
Enhanced with AI validation and drug interaction checking.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.prescription_service import PrescriptionService, PrescriptionStatus
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/")
async def create_prescription(
    patient_id: str,
    medications: list[dict[str, Any]],
    diagnosis_codes: list[str] | None = None,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new prescription with AI validation."""
    prescription_service = PrescriptionService(db)

    try:
        prescription = await prescription_service.create_prescription(
            patient_id, current_user.id, medications, diagnosis_codes
        )
        return prescription

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.error(f"Error creating prescription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating prescription"
        ) from e


@router.get("/{prescription_id}")
async def get_prescription(
    prescription_id: str,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get prescription by ID."""
    prescription_service = PrescriptionService(db)

    prescription = await prescription_service.get_prescription_by_id(prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )

    return prescription


@router.put("/{prescription_id}/status")
async def update_prescription_status(
    prescription_id: str,
    new_status: PrescriptionStatus,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update prescription status."""
    prescription_service = PrescriptionService(db)

    try:
        result = await prescription_service.update_prescription_status(
            prescription_id, new_status, current_user.id
        )
        return result

    except Exception as e:
        logger.error(f"Error updating prescription status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating prescription status"
        ) from e


@router.get("/patient/{patient_id}")
async def get_patient_prescriptions(
    patient_id: str,
    status_filter: PrescriptionStatus | None = None,
    limit: int = 50,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get prescriptions for a patient."""
    prescription_service = PrescriptionService(db)

    try:
        prescriptions = await prescription_service.get_patient_prescriptions(
            patient_id, status_filter, limit
        )
        return {
            "patient_id": patient_id,
            "prescriptions": prescriptions,
            "total": len(prescriptions)
        }

    except Exception as e:
        logger.error(f"Error retrieving patient prescriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving prescriptions"
        ) from e


@router.get("/{prescription_id}/adherence")
async def check_prescription_adherence(
    prescription_id: str,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Check prescription adherence."""
    prescription_service = PrescriptionService(db)

    try:
        adherence_report = await prescription_service.check_prescription_adherence(
            prescription_id
        )
        return adherence_report

    except Exception as e:
        logger.error(f"Error checking prescription adherence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking adherence"
        ) from e
