"""
Patient management endpoints.
Enhanced with clinical protocols and medical record management.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.patient import (
    Patient,
    PatientCreate,
    PatientList,
    PatientSearch,
    PatientUpdate,
)
from app.services.patient_service import PatientService
from app.services.user_service import UserService
from app.services.clinical_protocols_service import ClinicalProtocolsService, ProtocolType
from app.services.medical_record_service import MedicalRecordService, RecordType

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=Patient)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new patient."""
    patient_service = PatientService(db)

    existing = await patient_service.get_patient_by_patient_id(patient_data.patient_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient ID already exists"
        )

    patient = await patient_service.create_patient(patient_data, current_user.id)
    return patient


@router.get("/{patient_id}", response_model=Patient)
async def get_patient(
    patient_id: str,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get patient by patient ID."""
    patient_service = PatientService(db)

    patient = await patient_service.get_patient_by_patient_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


@router.put("/{patient_id}", response_model=Patient)
async def update_patient(
    patient_id: str,
    patient_update: PatientUpdate,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update patient information."""
    patient_service = PatientService(db)

    patient = await patient_service.get_patient_by_patient_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    update_data = patient_update.dict(exclude_unset=True)
    updated_patient = await patient_service.update_patient(patient.id, update_data)

    return updated_patient


@router.get("/", response_model=PatientList)
async def list_patients(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List patients."""
    patient_service = PatientService(db)

    patients, total = await patient_service.get_patients(limit, offset)

    patients_schemas = [Patient.from_orm(p) for p in patients]
    return PatientList(
        patients=patients_schemas,
        total=total,
        page=offset // limit + 1,
        size=limit,
    )


@router.post("/search", response_model=PatientList)
async def search_patients(
    search_params: PatientSearch,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Search patients."""
    patient_service = PatientService(db)

    patients, total = await patient_service.search_patients(
        search_params.query, search_params.search_fields, limit, offset
    )

    patients_schemas = [Patient.from_orm(p) for p in patients]
    return PatientList(
        patients=patients_schemas,
        total=total,
        page=offset // limit + 1,
        size=limit,
    )


@router.post("/{patient_id}/clinical-protocols")
async def assess_clinical_protocols(
    patient_id: str,
    clinical_data: Dict[str, Any],
    protocol_types: Optional[List[ProtocolType]] = None,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Assess clinical protocols for a patient."""
    patient_service = PatientService(db)
    protocols_service = ClinicalProtocolsService(db)

    patient = await patient_service.get_patient_by_patient_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    try:
        patient_data = {
            "age": getattr(patient, 'age', None),
            "gender": patient.gender,
            "medical_history": patient.medical_history,
            "risk_factors": []
        }

        if protocol_types:
            assessments = []
            for protocol_type in protocol_types:
                assessment = await protocols_service.assess_protocol(
                    protocol_type, patient_data, clinical_data
                )
                assessments.append(assessment)
        else:
            assessments = await protocols_service.get_applicable_protocols(
                patient_data, clinical_data
            )

        return {
            "patient_id": patient_id,
            "assessments": assessments,
            "assessed_at": clinical_data.get("assessment_timestamp"),
            "assessed_by": current_user.id
        }

    except Exception as e:
        logger.error(f"Error assessing clinical protocols: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error assessing clinical protocols"
        )


@router.post("/{patient_id}/medical-records")
async def create_medical_record(
    patient_id: str,
    record_type: RecordType,
    record_data: Dict[str, Any],
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a medical record for a patient."""
    patient_service = PatientService(db)
    medical_record_service = MedicalRecordService(db)

    patient = await patient_service.get_patient_by_patient_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    try:
        medical_record = await medical_record_service.create_medical_record(
            patient_id, record_type, record_data, current_user.id
        )
        return medical_record

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating medical record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating medical record"
        )


@router.get("/{patient_id}/medical-history")
async def get_medical_history(
    patient_id: str,
    record_types: Optional[List[RecordType]] = None,
    limit: int = 100,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get comprehensive medical history for a patient."""
    patient_service = PatientService(db)
    medical_record_service = MedicalRecordService(db)

    patient = await patient_service.get_patient_by_patient_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    try:
        medical_history = await medical_record_service.get_patient_medical_history(
            patient_id, record_types, limit
        )
        return medical_history

    except Exception as e:
        logger.error(f"Error retrieving medical history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving medical history"
        )
