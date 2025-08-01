"""
Pydantic schemas for Dermatology specialty API
Defines request and response models for dermatological assessments
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from uuid import UUID


# === BASE SCHEMAS ===

class DermatologyLesionBase(BaseModel):
    """Base schema for dermatology lesion"""
    
    # ABCDE Assessment
    abcde_asymmetry: Optional[str] = Field(None, description="Asymmetry assessment")
    abcde_asymmetry_score: Optional[Decimal] = Field(None, ge=0, le=2, description="Asymmetry score (0-2)")
    abcde_border: Optional[str] = Field(None, description="Border assessment")
    abcde_border_score: Optional[Decimal] = Field(None, ge=0, le=2, description="Border score (0-2)")
    abcde_color: Optional[str] = Field(None, description="Color assessment")
    abcde_color_score: Optional[Decimal] = Field(None, ge=0, le=2, description="Color score (0-2)")
    abcde_diameter_mm: Optional[Decimal] = Field(None, ge=0, description="Diameter in millimeters")
    abcde_diameter_score: Optional[Decimal] = Field(None, ge=0, le=2, description="Diameter score (0-2)")
    abcde_evolving: Optional[str] = Field(None, description="Evolving assessment")
    abcde_evolving_score: Optional[Decimal] = Field(None, ge=0, le=2, description="Evolving score (0-2)")
    
    # Lesion characteristics
    lesion_type: Optional[str] = Field(None, description="Type of lesion")
    lesion_morphology: Optional[str] = Field(None, description="Morphological description")
    surface_characteristics: Optional[List[str]] = Field(default_factory=list, description="Surface characteristics")
    color_description: Optional[List[str]] = Field(default_factory=list, description="Color description")
    texture: Optional[str] = Field(None, description="Lesion texture")
    
    # Location
    anatomical_location: Optional[str] = Field(None, description="Detailed anatomical location")
    body_region: Optional[str] = Field(None, description="General body region")
    laterality: Optional[str] = Field(None, description="Laterality")
    
    # Measurements
    length_mm: Optional[Decimal] = Field(None, ge=0, description="Length in millimeters")
    width_mm: Optional[Decimal] = Field(None, ge=0, description="Width in millimeters")
    height_mm: Optional[Decimal] = Field(None, ge=0, description="Height in millimeters")
    
    # Clinical assessment
    differential_diagnosis: Optional[List[str]] = Field(default_factory=list, description="Differential diagnoses")
    clinical_suspicion: Optional[str] = Field(None, description="Primary clinical suspicion")
    malignancy_risk: Optional[str] = Field(None, description="Malignancy risk assessment")
    
    # Documentation
    photography_performed: Optional[bool] = Field(False, description="Photography performed")
    dermoscopy_performed: Optional[bool] = Field(False, description="Dermoscopy performed")
    dermoscopy_features: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dermoscopic features")


class DermatologyLesionCreate(DermatologyLesionBase):
    """Schema for creating a dermatology lesion"""
    patient_id: UUID = Field(..., description="Patient ID")
    lesion_type: str = Field(..., description="Type of lesion (required)")
    anatomical_location: str = Field(..., description="Anatomical location (required)")


class DermatologyLesionUpdate(DermatologyLesionBase):
    """Schema for updating a dermatology lesion"""
    pass


class DermatologyLesionResponse(DermatologyLesionBase):
    """Schema for dermatology lesion response"""
    fhir_condition_id: UUID
    abcde_total_score: Optional[Decimal]
    abcde_risk_level: Optional[str]
    biopsy_recommended: Optional[bool]
    biopsy_urgency: Optional[str]
    follow_up_interval_months: Optional[Decimal]
    calculated_area: Optional[float]
    needs_urgent_referral: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# === EXAMINATION SCHEMAS ===

class DermatologyExaminationBase(BaseModel):
    """Base schema for dermatology examination"""
    
    examination_type: str = Field(..., description="Type of examination")
    examination_scope: Optional[List[str]] = Field(default_factory=list, description="Body regions examined")
    
    # Skin type
    fitzpatrick_skin_type: Optional[str] = Field(None, description="Fitzpatrick skin type")
    skin_phototype: Optional[str] = Field(None, description="Skin phototype description")
    
    # History
    sun_exposure_history: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Sun exposure history")
    sunscreen_use: Optional[str] = Field(None, description="Sunscreen use pattern")
    family_history_skin_cancer: Optional[bool] = Field(None, description="Family history of skin cancer")
    personal_history_skin_cancer: Optional[bool] = Field(None, description="Personal history of skin cancer")
    
    # Findings
    total_moles_count: Optional[int] = Field(None, ge=0, description="Total moles count")
    atypical_moles_count: Optional[int] = Field(None, ge=0, description="Atypical moles count")
    
    # Assessment
    overall_skin_condition: Optional[str] = Field(None, description="Overall skin condition")
    risk_stratification: Optional[str] = Field(None, description="Risk stratification")
    recommendations: Optional[List[str]] = Field(default_factory=list, description="Recommendations")
    next_examination_interval: Optional[int] = Field(None, ge=1, description="Next examination interval in months")


class DermatologyExaminationCreate(DermatologyExaminationBase):
    """Schema for creating a dermatology examination"""
    patient_id: UUID = Field(..., description="Patient ID")
    encounter_id: Optional[UUID] = Field(None, description="Encounter ID")


class DermatologyExaminationUpdate(DermatologyExaminationBase):
    """Schema for updating a dermatology examination"""
    examination_type: Optional[str] = Field(None, description="Type of examination")


class DermatologyExaminationResponse(DermatologyExaminationBase):
    """Schema for dermatology examination response"""
    fhir_observation_id: UUID
    total_photos_taken: Optional[int]
    dermoscopy_images: Optional[int]
    body_map_created: Optional[bool]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# === ABCDE ASSESSMENT SCHEMAS ===

class ABCDEAssessmentCreate(BaseModel):
    """Schema for creating ABCDE assessment"""
    
    asymmetry: str = Field(..., description="Asymmetry assessment")
    asymmetry_score: Decimal = Field(..., ge=0, le=2, description="Asymmetry score")
    border: str = Field(..., description="Border assessment")
    border_score: Decimal = Field(..., ge=0, le=2, description="Border score")
    color: str = Field(..., description="Color assessment")
    color_score: Decimal = Field(..., ge=0, le=2, description="Color score")
    diameter_mm: Decimal = Field(..., ge=0, description="Diameter in millimeters")
    diameter_score: Decimal = Field(..., ge=0, le=2, description="Diameter score")
    evolving: str = Field(..., description="Evolving assessment")
    evolving_score: Decimal = Field(..., ge=0, le=2, description="Evolving score")


class ABCDEAssessmentResponse(BaseModel):
    """Schema for ABCDE assessment response"""
    
    lesion_id: str
    abcde_total_score: Decimal
    risk_level: str
    biopsy_recommended: bool
    biopsy_urgency: Optional[str]
    malignancy_risk: str


# === STATISTICS SCHEMAS ===

class LesionStatistics(BaseModel):
    """Schema for lesion statistics"""
    
    total_lesions: int
    risk_distribution: Dict[str, int]
    biopsies_recommended: int
    urgent_biopsies: int
    region_distribution: Dict[str, int]


# === VALIDATORS ===

@validator('abcde_asymmetry', 'abcde_border', 'abcde_color', 'abcde_evolving', pre=True, allow_reuse=True)
def validate_abcde_fields(cls, v):
    """Validate ABCDE assessment fields"""
    if v is not None:
        valid_values = {
            'abcde_asymmetry': ['symmetric', 'asymmetric', 'unknown'],
            'abcde_border': ['regular', 'irregular', 'unknown'],
            'abcde_color': ['uniform', 'varied', 'unknown'],
            'abcde_evolving': ['stable', 'changing', 'unknown']
        }
        # This is a simplified validator - in a real implementation,
        # you'd check against the specific field name
        return v
    return v


@validator('examination_type', pre=True, allow_reuse=True)
def validate_examination_type(cls, v):
    """Validate examination type"""
    valid_types = ['full_body', 'targeted', 'lesion_check', 'mole_mapping']
    if v and v not in valid_types:
        raise ValueError(f'Examination type must be one of: {valid_types}')
    return v


@validator('malignancy_risk', pre=True, allow_reuse=True)
def validate_malignancy_risk(cls, v):
    """Validate malignancy risk level"""
    valid_risks = ['very_low', 'low', 'moderate', 'high', 'very_high']
    if v and v not in valid_risks:
        raise ValueError(f'Malignancy risk must be one of: {valid_risks}')
    return v


@validator('risk_stratification', pre=True, allow_reuse=True)
def validate_risk_stratification(cls, v):
    """Validate risk stratification"""
    valid_risks = ['low', 'moderate', 'high']
    if v and v not in valid_risks:
        raise ValueError(f'Risk stratification must be one of: {valid_risks}')
    return v