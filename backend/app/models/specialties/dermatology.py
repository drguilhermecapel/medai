"""
Dermatology specialty models extending FHIR base models
Supports dermatological examinations, ABCDE assessments, lesion tracking, etc.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.fhir_base import FHIRObservation, FHIRCondition, FHIRProcedure
from app.models.base import AuditableModel


class DermatologyLesion(FHIRCondition):
    """
    Dermatological lesion extending FHIR Condition
    Supports ABCDE assessment, lesion tracking, and photographic documentation
    """
    
    __tablename__ = "dermatology_lesions"
    
    # Reference to parent FHIR Condition
    fhir_condition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_conditions.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Reference to FHIR Condition"
    )
    
    # ABCDE Assessment (Asymmetry, Border, Color, Diameter, Evolving)
    abcde_asymmetry = Column(
        String(20),
        nullable=True,
        doc="ABCDE Asymmetry assessment (symmetric | asymmetric | unknown)"
    )
    
    abcde_asymmetry_score = Column(
        Numeric(2, 1),
        nullable=True,
        doc="Asymmetry score (0-2)"
    )
    
    abcde_border = Column(
        String(20),
        nullable=True,
        doc="ABCDE Border assessment (regular | irregular | unknown)"
    )
    
    abcde_border_score = Column(
        Numeric(2, 1),
        nullable=True,
        doc="Border score (0-2)"
    )
    
    abcde_color = Column(
        String(20),
        nullable=True,
        doc="ABCDE Color assessment (uniform | varied | unknown)"
    )
    
    abcde_color_score = Column(
        Numeric(2, 1),
        nullable=True,
        doc="Color score (0-2)"
    )
    
    abcde_diameter_mm = Column(
        Numeric(4, 1),
        nullable=True,
        doc="Diameter in millimeters"
    )
    
    abcde_diameter_score = Column(
        Numeric(2, 1),
        nullable=True,
        doc="Diameter score (0-2)"
    )
    
    abcde_evolving = Column(
        String(20),
        nullable=True,
        doc="ABCDE Evolving assessment (stable | changing | unknown)"
    )
    
    abcde_evolving_score = Column(
        Numeric(2, 1),
        nullable=True,
        doc="Evolving score (0-2)"
    )
    
    abcde_total_score = Column(
        Numeric(3, 1),
        nullable=True,
        doc="Total ABCDE score (0-10)"
    )
    
    abcde_risk_level = Column(
        String(20),
        nullable=True,
        doc="Risk level based on ABCDE score (low | moderate | high | critical)"
    )
    
    # Lesion characteristics
    lesion_type = Column(
        String(100),
        nullable=True,
        doc="Type of lesion (mole, freckle, seborrheic_keratosis, basal_cell_carcinoma, etc.)"
    )
    
    lesion_morphology = Column(
        String(100),
        nullable=True,
        doc="Morphological description (papule, macule, nodule, plaque, etc.)"
    )
    
    surface_characteristics = Column(
        JSONB,
        default=list,
        doc="Surface characteristics (smooth, rough, ulcerated, scaling, etc.)"
    )
    
    color_description = Column(
        JSONB,
        default=list,
        doc="Detailed color description (brown, black, red, blue, white, etc.)"
    )
    
    texture = Column(
        String(50),
        nullable=True,
        doc="Lesion texture (soft, firm, hard, fluctuant)"
    )
    
    # Location and mapping
    anatomical_location = Column(
        String(100),
        nullable=True,
        doc="Detailed anatomical location"
    )
    
    body_region = Column(
        String(50),
        nullable=True,
        doc="General body region (head, neck, trunk, arm, leg, etc.)"
    )
    
    laterality = Column(
        String(20),
        nullable=True,
        doc="Laterality (left, right, bilateral, midline)"
    )
    
    # Measurements
    length_mm = Column(
        Numeric(4, 1),
        nullable=True,
        doc="Length in millimeters"
    )
    
    width_mm = Column(
        Numeric(4, 1),
        nullable=True,
        doc="Width in millimeters"
    )
    
    height_mm = Column(
        Numeric(4, 1),
        nullable=True,
        doc="Height/thickness in millimeters"
    )
    
    area_mm2 = Column(
        Numeric(8, 2),
        nullable=True,
        doc="Calculated area in square millimeters"
    )
    
    # Clinical assessment
    differential_diagnosis = Column(
        JSONB,
        default=list,
        doc="List of differential diagnoses"
    )
    
    clinical_suspicion = Column(
        String(100),
        nullable=True,
        doc="Primary clinical suspicion"
    )
    
    malignancy_risk = Column(
        String(20),
        nullable=True,
        doc="Malignancy risk assessment (very_low | low | moderate | high | very_high)"
    )
    
    biopsy_recommended = Column(
        Boolean,
        nullable=True,
        doc="Whether biopsy is recommended"
    )
    
    biopsy_urgency = Column(
        String(20),
        nullable=True,
        doc="Biopsy urgency (routine | urgent | emergent)"
    )
    
    # Follow-up
    follow_up_interval_months = Column(
        Numeric(3, 1),
        nullable=True,
        doc="Recommended follow-up interval in months"
    )
    
    follow_up_notes = Column(
        Text,
        nullable=True,
        doc="Follow-up instructions and notes"
    )
    
    # Documentation
    photography_performed = Column(
        Boolean,
        default=False,
        doc="Whether photography was performed"
    )
    
    dermoscopy_performed = Column(
        Boolean,
        default=False,
        doc="Whether dermoscopy was performed"
    )
    
    dermoscopy_features = Column(
        JSONB,
        default=dict,
        doc="Dermoscopic features and patterns"
    )
    
    # Historical tracking
    previous_assessments = Column(
        JSONB,
        default=list,
        doc="Previous assessment data for comparison"
    )
    
    change_tracking = Column(
        JSONB,
        default=dict,
        doc="Tracking of changes over time"
    )
    
    @hybrid_property
    def calculated_area(self) -> Optional[float]:
        """Calculate area if length and width are available"""
        if self.length_mm and self.width_mm:
            return float(self.length_mm * self.width_mm * 3.14159 / 4)  # Ellipse approximation
        return None
    
    @hybrid_property
    def needs_urgent_referral(self) -> bool:
        """Determine if lesion needs urgent referral"""
        if self.abcde_total_score and self.abcde_total_score >= 8:
            return True
        if self.malignancy_risk in ['high', 'very_high']:
            return True
        if self.biopsy_urgency == 'emergent':
            return True
        return False


class DermatologyExamination(FHIRObservation):
    """
    Dermatological examination extending FHIR Observation
    Comprehensive skin examination with findings
    """
    
    __tablename__ = "dermatology_examinations"
    
    # Reference to parent FHIR Observation
    fhir_observation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_observations.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Reference to FHIR Observation"
    )
    
    # Examination type and scope
    examination_type = Column(
        String(50),
        nullable=False,
        doc="Type of examination (full_body | targeted | lesion_check | mole_mapping)"
    )
    
    examination_scope = Column(
        JSONB,
        default=list,
        doc="Body regions examined"
    )
    
    # Skin type assessment
    fitzpatrick_skin_type = Column(
        String(10),
        nullable=True,
        doc="Fitzpatrick skin type (I-VI)"
    )
    
    skin_phototype = Column(
        String(50),
        nullable=True,
        doc="Skin phototype description"
    )
    
    # Sun exposure history
    sun_exposure_history = Column(
        JSONB,
        default=dict,
        doc="Sun exposure history and risk factors"
    )
    
    sunscreen_use = Column(
        String(20),
        nullable=True,
        doc="Sunscreen use pattern (never | occasional | regular | always)"
    )
    
    # Family history
    family_history_skin_cancer = Column(
        Boolean,
        nullable=True,
        doc="Family history of skin cancer"
    )
    
    family_history_details = Column(
        JSONB,
        default=dict,
        doc="Details of family history"
    )
    
    # Personal history
    personal_history_skin_cancer = Column(
        Boolean,
        nullable=True,
        doc="Personal history of skin cancer"
    )
    
    previous_biopsies = Column(
        JSONB,
        default=list,
        doc="Previous skin biopsies and results"
    )
    
    # General findings
    total_moles_count = Column(
        Numeric(4, 0),
        nullable=True,
        doc="Total count of moles/nevi"
    )
    
    atypical_moles_count = Column(
        Numeric(4, 0),
        nullable=True,
        doc="Count of atypical moles"
    )
    
    # Specific findings
    actinic_keratoses = Column(
        JSONB,
        default=list,
        doc="Actinic keratoses findings"
    )
    
    seborrheic_keratoses = Column(
        JSONB,
        default=list,
        doc="Seborrheic keratoses findings"
    )
    
    other_lesions = Column(
        JSONB,
        default=list,
        doc="Other lesions found during examination"
    )
    
    # Overall assessment
    overall_skin_condition = Column(
        String(50),
        nullable=True,
        doc="Overall skin condition assessment"
    )
    
    risk_stratification = Column(
        String(20),
        nullable=True,
        doc="Patient risk stratification (low | moderate | high)"
    )
    
    # Recommendations
    recommendations = Column(
        JSONB,
        default=list,
        doc="Clinical recommendations"
    )
    
    next_examination_interval = Column(
        Numeric(3, 0),
        nullable=True,
        doc="Recommended next examination interval in months"
    )
    
    # Documentation
    total_photos_taken = Column(
        Numeric(3, 0),
        default=0,
        doc="Total number of photographs taken"
    )
    
    dermoscopy_images = Column(
        Numeric(3, 0),
        default=0,
        doc="Number of dermoscopy images taken"
    )
    
    body_map_created = Column(
        Boolean,
        default=False,
        doc="Whether body map was created"
    )


# Index definitions for dermatology tables
Index('ix_dermatology_lesions_abcde_total_score', DermatologyLesion.abcde_total_score)
Index('ix_dermatology_lesions_malignancy_risk', DermatologyLesion.malignancy_risk)
Index('ix_dermatology_lesions_body_region', DermatologyLesion.body_region)
Index('ix_dermatology_examinations_examination_type', DermatologyExamination.examination_type)