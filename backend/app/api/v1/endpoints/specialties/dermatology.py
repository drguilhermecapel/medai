"""
Dermatology API endpoints for multi-specialty EHR system
Provides CRUD operations for dermatological assessments, lesions, and procedures
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.models.specialties.dermatology import DermatologyLesion, DermatologyExamination
from app.models.fhir_base import FHIRPatient, FHIREncounter, FHIRCondition, FHIRObservation
from app.schemas.specialties.dermatology import (
    DermatologyLesionCreate, DermatologyLesionUpdate, DermatologyLesionResponse,
    DermatologyExaminationCreate, DermatologyExaminationUpdate, DermatologyExaminationResponse,
    ABCDEAssessmentCreate, ABCDEAssessmentResponse
)
from app.core.feature_flags import require_specialty, require_feature, feature_flags

router = APIRouter(prefix="/dermatology", tags=["dermatology"])


# === LESION ENDPOINTS ===

@router.post("/lesions", response_model=DermatologyLesionResponse, status_code=status.HTTP_201_CREATED)
@require_specialty("dermatology")
async def create_lesion(
    lesion_data: DermatologyLesionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new dermatological lesion record
    
    Creates both FHIR Condition and specialized Dermatology Lesion records
    """
    try:
        # First create the FHIR Condition
        fhir_condition = FHIRCondition(
            patient_id=lesion_data.patient_id,
            clinical_status={"coding": [{"code": "active", "system": "http://terminology.hl7.org/CodeSystem/condition-clinical"}]},
            verification_status={"coding": [{"code": "confirmed", "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status"}]},
            category=[{"coding": [{"code": "problem-list-item", "system": "http://terminology.hl7.org/CodeSystem/condition-category"}]}],
            code={"coding": [{"code": "400006008", "system": "http://snomed.info/sct", "display": "Skin lesion"}]},
            subject=f"Patient/{lesion_data.patient_id}",
            specialty_data={"specialty": "dermatology", "lesion_type": lesion_data.lesion_type}
        )
        
        db.add(fhir_condition)
        db.flush()  # Get the ID without committing
        
        # Create the specialized dermatology lesion
        dermatology_lesion = DermatologyLesion(
            fhir_condition_id=fhir_condition.id,
            **lesion_data.dict(exclude={'patient_id'})
        )
        
        db.add(dermatology_lesion)
        db.commit()
        db.refresh(dermatology_lesion)
        
        return dermatology_lesion
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating lesion: {str(e)}"
        )


@router.get("/lesions", response_model=List[DermatologyLesionResponse])
async def list_lesions(
    db: Session = Depends(get_db),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    risk_level: Optional[str] = Query(None, description="Filter by ABCDE risk level"),
    body_region: Optional[str] = Query(None, description="Filter by body region"),
    limit: int = Query(50, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List dermatological lesions with optional filtering
    """
    query = db.query(DermatologyLesion).join(FHIRCondition)
    
    # Apply filters
    if patient_id:
        query = query.filter(FHIRCondition.patient_id == patient_id)
    if risk_level:
        query = query.filter(DermatologyLesion.abcde_risk_level == risk_level)
    if body_region:
        query = query.filter(DermatologyLesion.body_region == body_region)
    
    # Apply pagination
    lesions = query.offset(offset).limit(limit).all()
    
    return lesions


@router.get("/lesions/{lesion_id}", response_model=DermatologyLesionResponse)
async def get_lesion(
    lesion_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific dermatological lesion by ID
    """
    lesion = db.query(DermatologyLesion).filter(
        DermatologyLesion.fhir_condition_id == lesion_id
    ).first()
    
    if not lesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesion not found"
        )
    
    return lesion


@router.put("/lesions/{lesion_id}", response_model=DermatologyLesionResponse)
async def update_lesion(
    lesion_id: str,
    lesion_update: DermatologyLesionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a dermatological lesion
    """
    lesion = db.query(DermatologyLesion).filter(
        DermatologyLesion.fhir_condition_id == lesion_id
    ).first()
    
    if not lesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesion not found"
        )
    
    try:
        # Update fields
        update_data = lesion_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lesion, field, value)
        
        # Recalculate ABCDE score if components were updated
        if any(field.startswith('abcde_') for field in update_data.keys()):
            lesion.abcde_total_score = _calculate_abcde_score(lesion)
            lesion.abcde_risk_level = _determine_risk_level(lesion.abcde_total_score)
        
        db.commit()
        db.refresh(lesion)
        
        return lesion
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating lesion: {str(e)}"
        )


@router.delete("/lesions/{lesion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesion(
    lesion_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a dermatological lesion
    """
    lesion = db.query(DermatologyLesion).filter(
        DermatologyLesion.fhir_condition_id == lesion_id
    ).first()
    
    if not lesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesion not found"
        )
    
    try:
        # Delete the specialized record (FHIR Condition will be cascade deleted)
        db.delete(lesion)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting lesion: {str(e)}"
        )


# === EXAMINATION ENDPOINTS ===

@router.post("/examinations", response_model=DermatologyExaminationResponse, status_code=status.HTTP_201_CREATED)
async def create_examination(
    examination_data: DermatologyExaminationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new dermatological examination record
    """
    try:
        # First create the FHIR Observation
        fhir_observation = FHIRObservation(
            patient_id=examination_data.patient_id,
            encounter_id=examination_data.encounter_id,
            status="final",
            category=[{"coding": [{"code": "exam", "system": "http://terminology.hl7.org/CodeSystem/observation-category"}]}],
            code={"coding": [{"code": "5880005", "system": "http://snomed.info/sct", "display": "Physical examination procedure"}]},
            subject=f"Patient/{examination_data.patient_id}",
            specialty_data={"specialty": "dermatology", "examination_type": examination_data.examination_type}
        )
        
        db.add(fhir_observation)
        db.flush()
        
        # Create the specialized dermatology examination
        dermatology_examination = DermatologyExamination(
            fhir_observation_id=fhir_observation.id,
            **examination_data.dict(exclude={'patient_id', 'encounter_id'})
        )
        
        db.add(dermatology_examination)
        db.commit()
        db.refresh(dermatology_examination)
        
        return dermatology_examination
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating examination: {str(e)}"
        )


@router.get("/examinations", response_model=List[DermatologyExaminationResponse])
async def list_examinations(
    db: Session = Depends(get_db),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    examination_type: Optional[str] = Query(None, description="Filter by examination type"),
    limit: int = Query(50, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List dermatological examinations with optional filtering
    """
    query = db.query(DermatologyExamination).join(FHIRObservation)
    
    # Apply filters
    if patient_id:
        query = query.filter(FHIRObservation.patient_id == patient_id)
    if examination_type:
        query = query.filter(DermatologyExamination.examination_type == examination_type)
    
    # Apply pagination
    examinations = query.offset(offset).limit(limit).all()
    
    return examinations


@router.get("/examinations/{examination_id}", response_model=DermatologyExaminationResponse)
async def get_examination(
    examination_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific dermatological examination by ID
    """
    examination = db.query(DermatologyExamination).filter(
        DermatologyExamination.fhir_observation_id == examination_id
    ).first()
    
    if not examination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examination not found"
        )
    
    return examination


# === ABCDE ASSESSMENT ENDPOINTS ===

@router.post("/lesions/{lesion_id}/abcde", response_model=ABCDEAssessmentResponse)
@require_specialty("dermatology")
@require_feature(feature_flags.DERMATOLOGY_ABCDE_ENABLED)
async def perform_abcde_assessment(
    lesion_id: str,
    abcde_data: ABCDEAssessmentCreate,
    db: Session = Depends(get_db)
):
    """
    Perform or update ABCDE assessment for a lesion
    """
    lesion = db.query(DermatologyLesion).filter(
        DermatologyLesion.fhir_condition_id == lesion_id
    ).first()
    
    if not lesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesion not found"
        )
    
    try:
        # Update ABCDE scores
        lesion.abcde_asymmetry = abcde_data.asymmetry
        lesion.abcde_asymmetry_score = abcde_data.asymmetry_score
        lesion.abcde_border = abcde_data.border
        lesion.abcde_border_score = abcde_data.border_score
        lesion.abcde_color = abcde_data.color
        lesion.abcde_color_score = abcde_data.color_score
        lesion.abcde_diameter_mm = abcde_data.diameter_mm
        lesion.abcde_diameter_score = abcde_data.diameter_score
        lesion.abcde_evolving = abcde_data.evolving
        lesion.abcde_evolving_score = abcde_data.evolving_score
        
        # Calculate total score and risk level
        lesion.abcde_total_score = _calculate_abcde_score(lesion)
        lesion.abcde_risk_level = _determine_risk_level(lesion.abcde_total_score)
        
        # Set biopsy recommendations based on score
        if lesion.abcde_total_score >= 8:
            lesion.biopsy_recommended = True
            lesion.biopsy_urgency = "emergent"
            lesion.malignancy_risk = "very_high"
        elif lesion.abcde_total_score >= 6:
            lesion.biopsy_recommended = True
            lesion.biopsy_urgency = "urgent"
            lesion.malignancy_risk = "high"
        elif lesion.abcde_total_score >= 4:
            lesion.biopsy_recommended = True
            lesion.biopsy_urgency = "routine"
            lesion.malignancy_risk = "moderate"
        else:
            lesion.biopsy_recommended = False
            lesion.malignancy_risk = "low"
        
        db.commit()
        db.refresh(lesion)
        
        return {
            "lesion_id": lesion_id,
            "abcde_total_score": lesion.abcde_total_score,
            "risk_level": lesion.abcde_risk_level,
            "biopsy_recommended": lesion.biopsy_recommended,
            "biopsy_urgency": lesion.biopsy_urgency,
            "malignancy_risk": lesion.malignancy_risk
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error performing ABCDE assessment: {str(e)}"
        )


@router.get("/statistics/lesion-summary")
async def get_lesion_statistics(
    db: Session = Depends(get_db),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID")
):
    """
    Get summary statistics for dermatological lesions
    """
    query = db.query(DermatologyLesion).join(FHIRCondition)
    
    if patient_id:
        query = query.filter(FHIRCondition.patient_id == patient_id)
    
    total_lesions = query.count()
    
    # Risk level distribution
    risk_distribution = {}
    for risk_level in ['low', 'moderate', 'high', 'critical']:
        count = query.filter(DermatologyLesion.abcde_risk_level == risk_level).count()
        risk_distribution[risk_level] = count
    
    # Biopsy recommendations
    biopsies_recommended = query.filter(DermatologyLesion.biopsy_recommended == True).count()
    urgent_biopsies = query.filter(DermatologyLesion.biopsy_urgency == 'emergent').count()
    
    # Body region distribution
    body_regions = db.query(DermatologyLesion.body_region).distinct().all()
    region_distribution = {}
    for region in body_regions:
        if region[0]:  # Skip None values
            count = query.filter(DermatologyLesion.body_region == region[0]).count()
            region_distribution[region[0]] = count
    
    return {
        "total_lesions": total_lesions,
        "risk_distribution": risk_distribution,
        "biopsies_recommended": biopsies_recommended,
        "urgent_biopsies": urgent_biopsies,
        "region_distribution": region_distribution
    }


# === HELPER FUNCTIONS ===

def _calculate_abcde_score(lesion: DermatologyLesion) -> float:
    """Calculate total ABCDE score from individual components"""
    score = 0.0
    
    if lesion.abcde_asymmetry_score:
        score += float(lesion.abcde_asymmetry_score)
    if lesion.abcde_border_score:
        score += float(lesion.abcde_border_score)
    if lesion.abcde_color_score:
        score += float(lesion.abcde_color_score)
    if lesion.abcde_diameter_score:
        score += float(lesion.abcde_diameter_score)
    if lesion.abcde_evolving_score:
        score += float(lesion.abcde_evolving_score)
    
    return score


def _determine_risk_level(total_score: float) -> str:
    """Determine risk level based on ABCDE total score"""
    if total_score >= 8:
        return "critical"
    elif total_score >= 6:
        return "high"
    elif total_score >= 4:
        return "moderate"
    else:
        return "low"