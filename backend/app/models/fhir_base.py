"""
FHIR-compliant base models for multi-specialty Electronic Health Record system
Based on HL7 FHIR R4 standards for interoperability
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import AuditableModel, StatusMixin, MetadataMixin


class FHIRResource(AuditableModel, StatusMixin, MetadataMixin):
    """
    Base FHIR Resource class following HL7 FHIR R4 specification
    All FHIR resources inherit from this base class
    """
    
    __abstract__ = True
    
    # FHIR Resource metadata
    resource_type = Column(
        String(50),
        nullable=False,
        doc="FHIR resource type (Patient, Observation, etc.)"
    )
    
    resource_id = Column(
        String(64),
        nullable=False,
        index=True,
        doc="FHIR logical ID of the resource"
    )
    
    version_id = Column(
        String(64),
        nullable=True,
        doc="FHIR version-specific identifier"
    )
    
    last_updated = Column(
        DateTime,
        default=datetime.utcnow,
        doc="When the resource was last updated"
    )
    
    profile = Column(
        ARRAY(String),
        default=list,
        doc="FHIR profiles that this resource claims to conform to"
    )
    
    security = Column(
        JSONB,
        default=dict,
        doc="Security labels applied to this resource"
    )
    
    tag = Column(
        JSONB,
        default=list,
        doc="Tags applied to this resource"
    )
    
    def __init__(self, **kwargs):
        """Initialize FHIR resource with generated resource_id if not provided"""
        super().__init__(**kwargs)
        if not self.resource_id:
            self.resource_id = str(uuid.uuid4())


class FHIRPatient(FHIRResource):
    """
    FHIR Patient resource for multi-specialty system
    Extends the existing Patient model with FHIR compliance
    """
    
    __tablename__ = "fhir_patients"
    
    # Link to existing patient
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to existing patient record"
    )
    
    # FHIR Patient-specific fields
    identifier = Column(
        JSONB,
        default=list,
        doc="FHIR identifiers for this patient"
    )
    
    active = Column(
        Boolean,
        default=True,
        doc="Whether patient record is in active use"
    )
    
    name = Column(
        JSONB,
        default=list,
        doc="FHIR HumanName datatype"
    )
    
    telecom = Column(
        JSONB,
        default=list,
        doc="FHIR ContactPoint datatype"
    )
    
    gender = Column(
        String(20),
        nullable=True,
        doc="FHIR gender (male | female | other | unknown)"
    )
    
    birth_date = Column(
        DateTime,
        nullable=True,
        doc="FHIR date of birth"
    )
    
    address = Column(
        JSONB,
        default=list,
        doc="FHIR Address datatype"
    )
    
    marital_status = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for marital status"
    )
    
    contact = Column(
        JSONB,
        default=list,
        doc="FHIR contact parties for the patient"
    )
    
    communication = Column(
        JSONB,
        default=list,
        doc="FHIR languages which may be used to communicate"
    )
    
    general_practitioner = Column(
        JSONB,
        default=list,
        doc="FHIR references to primary care providers"
    )
    
    managing_organization = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to managing organization"
    )
    
    link = Column(
        JSONB,
        default=list,
        doc="FHIR links to other patient resources"
    )
    
    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])
    encounters = relationship("FHIREncounter", back_populates="patient")
    observations = relationship("FHIRObservation", back_populates="patient")
    conditions = relationship("FHIRCondition", back_populates="patient")
    procedures = relationship("FHIRProcedure", back_populates="patient")
    
    def __init__(self, **kwargs):
        kwargs.setdefault('resource_type', 'Patient')
        super().__init__(**kwargs)


class FHIREncounter(FHIRResource):
    """
    FHIR Encounter resource for healthcare encounters
    Represents an interaction between a patient and healthcare provider
    """
    
    __tablename__ = "fhir_encounters"
    
    # Core Encounter fields
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to FHIR patient"
    )
    
    identifier = Column(
        JSONB,
        default=list,
        doc="FHIR identifiers for this encounter"
    )
    
    status = Column(
        String(20),
        nullable=False,
        doc="FHIR encounter status (planned | arrived | triaged | in-progress | onleave | finished | cancelled)"
    )
    
    status_history = Column(
        JSONB,
        default=list,
        doc="FHIR list of past encounter statuses"
    )
    
    class_field = Column(
        "class",  # Using class_field to avoid Python keyword conflict
        JSONB,
        nullable=False,
        doc="FHIR Coding for encounter class (inpatient | outpatient | ambulatory | emergency)"
    )
    
    class_history = Column(
        JSONB,
        default=list,
        doc="FHIR list of past encounter classes"
    )
    
    type = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcept for specific encounter type"
    )
    
    service_type = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for specific service type"
    )
    
    priority = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for encounter priority"
    )
    
    subject = Column(
        String(255),
        nullable=False,
        doc="FHIR reference to the patient"
    )
    
    episode_of_care = Column(
        JSONB,
        default=list,
        doc="FHIR references to episode(s) of care"
    )
    
    based_on = Column(
        JSONB,
        default=list,
        doc="FHIR references to the ServiceRequest(s) that initiated this encounter"
    )
    
    participant = Column(
        JSONB,
        default=list,
        doc="FHIR list of participants involved in the encounter"
    )
    
    appointment = Column(
        JSONB,
        default=list,
        doc="FHIR references to appointments that scheduled this encounter"
    )
    
    period = Column(
        JSONB,
        nullable=True,
        doc="FHIR Period the encounter took place"
    )
    
    length = Column(
        JSONB,
        nullable=True,
        doc="FHIR Duration of the encounter"
    )
    
    reason_code = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcept for coded reason the encounter takes place"
    )
    
    reason_reference = Column(
        JSONB,
        default=list,
        doc="FHIR references to Condition/Procedure/Observation reasons"
    )
    
    diagnosis = Column(
        JSONB,
        default=list,
        doc="FHIR list of diagnosis relevant to this encounter"
    )
    
    account = Column(
        JSONB,
        default=list,
        doc="FHIR references to accounts associated with this encounter"
    )
    
    hospitalization = Column(
        JSONB,
        nullable=True,
        doc="FHIR details about the admission to a healthcare service"
    )
    
    location = Column(
        JSONB,
        default=list,
        doc="FHIR list of locations where the patient has been"
    )
    
    service_provider = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to the organization responsible"
    )
    
    part_of = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to another encounter this encounter is part of"
    )
    
    # Relationships
    patient = relationship("FHIRPatient", back_populates="encounters")
    observations = relationship("FHIRObservation", back_populates="encounter")
    procedures = relationship("FHIRProcedure", back_populates="encounter")
    
    # Specialty-specific extensions
    specialty_data = Column(
        JSONB,
        default=dict,
        doc="Specialty-specific data extensions"
    )
    
    def __init__(self, **kwargs):
        kwargs.setdefault('resource_type', 'Encounter')
        kwargs.setdefault('status', 'planned')
        super().__init__(**kwargs)


class FHIRObservation(FHIRResource):
    """
    FHIR Observation resource for measurements and simple assertions
    Used for vital signs, lab results, imaging results, etc.
    """
    
    __tablename__ = "fhir_observations"
    
    # Core Observation fields
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to FHIR patient"
    )
    
    encounter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_encounters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Reference to FHIR encounter"
    )
    
    identifier = Column(
        JSONB,
        default=list,
        doc="FHIR identifiers for this observation"
    )
    
    based_on = Column(
        JSONB,
        default=list,
        doc="FHIR references to the ServiceRequest that initiated this observation"
    )
    
    part_of = Column(
        JSONB,
        default=list,
        doc="FHIR references to larger event this observation is part of"
    )
    
    status = Column(
        String(20),
        nullable=False,
        doc="FHIR observation status (registered | preliminary | final | amended | corrected | cancelled | entered-in-error | unknown)"
    )
    
    category = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcept for observation classification"
    )
    
    code = Column(
        JSONB,
        nullable=False,
        doc="FHIR CodeableConcept describing what was observed"
    )
    
    subject = Column(
        String(255),
        nullable=False,
        doc="FHIR reference to the patient or group"
    )
    
    focus = Column(
        JSONB,
        default=list,
        doc="FHIR references to actual focus of observation"
    )
    
    encounter_ref = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to healthcare encounter"
    )
    
    effective_datetime = Column(
        DateTime,
        nullable=True,
        doc="FHIR dateTime when observation was made"
    )
    
    effective_period = Column(
        JSONB,
        nullable=True,
        doc="FHIR Period when observation was made"
    )
    
    issued = Column(
        DateTime,
        nullable=True,
        doc="FHIR instant when observation was published"
    )
    
    performer = Column(
        JSONB,
        default=list,
        doc="FHIR references to who performed the observation"
    )
    
    # Value fields (one of these should be populated)
    value_quantity = Column(
        JSONB,
        nullable=True,
        doc="FHIR Quantity value"
    )
    
    value_codeable_concept = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept value"
    )
    
    value_string = Column(
        Text,
        nullable=True,
        doc="FHIR string value"
    )
    
    value_boolean = Column(
        Boolean,
        nullable=True,
        doc="FHIR boolean value"
    )
    
    value_integer = Column(
        Numeric,
        nullable=True,
        doc="FHIR integer value"
    )
    
    value_range = Column(
        JSONB,
        nullable=True,
        doc="FHIR Range value"
    )
    
    value_ratio = Column(
        JSONB,
        nullable=True,
        doc="FHIR Ratio value"
    )
    
    value_sampled_data = Column(
        JSONB,
        nullable=True,
        doc="FHIR SampledData value"
    )
    
    value_time = Column(
        DateTime,
        nullable=True,
        doc="FHIR time value"
    )
    
    value_datetime = Column(
        DateTime,
        nullable=True,
        doc="FHIR dateTime value"
    )
    
    value_period = Column(
        JSONB,
        nullable=True,
        doc="FHIR Period value"
    )
    
    data_absent_reason = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for why data is absent"
    )
    
    interpretation = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcepts for observation interpretation"
    )
    
    note = Column(
        JSONB,
        default=list,
        doc="FHIR Annotation comments about the observation"
    )
    
    body_site = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for observed body part"
    )
    
    method = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for how observation was made"
    )
    
    specimen = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to specimen used"
    )
    
    device = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to device used"
    )
    
    reference_range = Column(
        JSONB,
        default=list,
        doc="FHIR reference ranges for observation values"
    )
    
    has_member = Column(
        JSONB,
        default=list,
        doc="FHIR references to related resource observations"
    )
    
    derived_from = Column(
        JSONB,
        default=list,
        doc="FHIR references to related observations this was derived from"
    )
    
    component = Column(
        JSONB,
        default=list,
        doc="FHIR component results for multi-component observations"
    )
    
    # Specialty-specific extensions
    specialty_data = Column(
        JSONB,
        default=dict,
        doc="Specialty-specific data extensions"
    )
    
    # Relationships
    patient = relationship("FHIRPatient", back_populates="observations")
    encounter = relationship("FHIREncounter", back_populates="observations")
    
    def __init__(self, **kwargs):
        kwargs.setdefault('resource_type', 'Observation')
        kwargs.setdefault('status', 'final')
        super().__init__(**kwargs)


class FHIRCondition(FHIRResource):
    """
    FHIR Condition resource for clinical conditions, problems, diagnoses
    """
    
    __tablename__ = "fhir_conditions"
    
    # Core Condition fields
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to FHIR patient"
    )
    
    identifier = Column(
        JSONB,
        default=list,
        doc="FHIR identifiers for this condition"
    )
    
    clinical_status = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for clinical status (active | recurrence | relapse | inactive | remission | resolved)"
    )
    
    verification_status = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for verification status (unconfirmed | provisional | differential | confirmed | refuted | entered-in-error)"
    )
    
    category = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcepts for condition category"
    )
    
    severity = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for condition severity"
    )
    
    code = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for the condition"
    )
    
    body_site = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcepts for anatomical location"
    )
    
    subject = Column(
        String(255),
        nullable=False,
        doc="FHIR reference to the patient"
    )
    
    encounter = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to encounter when condition was first asserted"
    )
    
    onset_datetime = Column(
        DateTime,
        nullable=True,
        doc="FHIR dateTime when condition started"
    )
    
    onset_age = Column(
        JSONB,
        nullable=True,
        doc="FHIR Age when condition started"
    )
    
    onset_period = Column(
        JSONB,
        nullable=True,
        doc="FHIR Period when condition started"
    )
    
    onset_range = Column(
        JSONB,
        nullable=True,
        doc="FHIR Range when condition started"
    )
    
    onset_string = Column(
        String(255),
        nullable=True,
        doc="FHIR string description of when condition started"
    )
    
    abatement_datetime = Column(
        DateTime,
        nullable=True,
        doc="FHIR dateTime when condition resolved"
    )
    
    abatement_age = Column(
        JSONB,
        nullable=True,
        doc="FHIR Age when condition resolved"
    )
    
    abatement_period = Column(
        JSONB,
        nullable=True,
        doc="FHIR Period when condition resolved"
    )
    
    abatement_range = Column(
        JSONB,
        nullable=True,
        doc="FHIR Range when condition resolved"
    )
    
    abatement_string = Column(
        String(255),
        nullable=True,
        doc="FHIR string description of when condition resolved"
    )
    
    recorded_date = Column(
        DateTime,
        nullable=True,
        doc="FHIR date when condition was first recorded"
    )
    
    recorder = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to who recorded the condition"
    )
    
    asserter = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to person who asserts this condition"
    )
    
    stage = Column(
        JSONB,
        default=list,
        doc="FHIR stage/grade, usually assessed formally"
    )
    
    evidence = Column(
        JSONB,
        default=list,
        doc="FHIR supporting evidence for condition"
    )
    
    note = Column(
        JSONB,
        default=list,
        doc="FHIR Annotation additional information about condition"
    )
    
    # Specialty-specific extensions
    specialty_data = Column(
        JSONB,
        default=dict,
        doc="Specialty-specific data extensions"
    )
    
    # Relationships
    patient = relationship("FHIRPatient", back_populates="conditions")
    
    def __init__(self, **kwargs):
        kwargs.setdefault('resource_type', 'Condition')
        super().__init__(**kwargs)


class FHIRProcedure(FHIRResource):
    """
    FHIR Procedure resource for actions performed on a patient
    """
    
    __tablename__ = "fhir_procedures"
    
    # Core Procedure fields
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to FHIR patient"
    )
    
    encounter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_encounters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Reference to FHIR encounter"
    )
    
    identifier = Column(
        JSONB,
        default=list,
        doc="FHIR identifiers for this procedure"
    )
    
    instantiates_canonical = Column(
        JSONB,
        default=list,
        doc="FHIR canonical references to protocols followed"
    )
    
    instantiates_uri = Column(
        JSONB,
        default=list,
        doc="FHIR URIs of protocols followed"
    )
    
    based_on = Column(
        JSONB,
        default=list,
        doc="FHIR references to ServiceRequest that initiated this procedure"
    )
    
    part_of = Column(
        JSONB,
        default=list,
        doc="FHIR references to procedures this is part of"
    )
    
    status = Column(
        String(20),
        nullable=False,
        doc="FHIR procedure status (preparation | in-progress | not-done | on-hold | stopped | completed | entered-in-error | unknown)"
    )
    
    status_reason = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for reason for current status"
    )
    
    category = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for procedure classification"
    )
    
    code = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for the procedure"
    )
    
    subject = Column(
        String(255),
        nullable=False,
        doc="FHIR reference to the patient"
    )
    
    encounter_ref = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to encounter associated with procedure"
    )
    
    performed_datetime = Column(
        DateTime,
        nullable=True,
        doc="FHIR dateTime when procedure was performed"
    )
    
    performed_period = Column(
        JSONB,
        nullable=True,
        doc="FHIR Period when procedure was performed"
    )
    
    performed_string = Column(
        String(255),
        nullable=True,
        doc="FHIR string description of when procedure was performed"
    )
    
    performed_age = Column(
        JSONB,
        nullable=True,
        doc="FHIR Age when procedure was performed"
    )
    
    performed_range = Column(
        JSONB,
        nullable=True,
        doc="FHIR Range when procedure was performed"
    )
    
    recorder = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to who recorded the procedure"
    )
    
    asserter = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to person who asserts this procedure"
    )
    
    performer = Column(
        JSONB,
        default=list,
        doc="FHIR list of who performed the procedure"
    )
    
    location = Column(
        String(255),
        nullable=True,
        doc="FHIR reference to where procedure was performed"
    )
    
    reason_code = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcepts for coded reason procedure was performed"
    )
    
    reason_reference = Column(
        JSONB,
        default=list,
        doc="FHIR references to Condition/Observation/Procedure reasons"
    )
    
    body_site = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcepts for target body sites"
    )
    
    outcome = Column(
        JSONB,
        nullable=True,
        doc="FHIR CodeableConcept for procedure outcome"
    )
    
    report = Column(
        JSONB,
        default=list,
        doc="FHIR references to procedure reports"
    )
    
    complication = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcepts for complications"
    )
    
    complication_detail = Column(
        JSONB,
        default=list,
        doc="FHIR references to conditions for complications"
    )
    
    follow_up = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcepts for follow-up instructions"
    )
    
    note = Column(
        JSONB,
        default=list,
        doc="FHIR Annotation additional information about procedure"
    )
    
    focal_device = Column(
        JSONB,
        default=list,
        doc="FHIR devices used/changed in procedure"
    )
    
    used_reference = Column(
        JSONB,
        default=list,
        doc="FHIR references to items used during procedure"
    )
    
    used_code = Column(
        JSONB,
        default=list,
        doc="FHIR CodeableConcepts for coded items used"
    )
    
    # Specialty-specific extensions
    specialty_data = Column(
        JSONB,
        default=dict,
        doc="Specialty-specific data extensions"
    )
    
    # Relationships
    patient = relationship("FHIRPatient", back_populates="procedures")
    encounter = relationship("FHIREncounter", back_populates="procedures")
    
    def __init__(self, **kwargs):
        kwargs.setdefault('resource_type', 'Procedure')
        kwargs.setdefault('status', 'completed')
        super().__init__(**kwargs)


# Index definitions for better query performance
__table_args__ = (
    Index('ix_fhir_patients_resource_id', 'resource_id'),
    Index('ix_fhir_patients_patient_id', 'patient_id'),
    Index('ix_fhir_encounters_patient_id', 'patient_id'),
    Index('ix_fhir_encounters_status', 'status'),
    Index('ix_fhir_observations_patient_id', 'patient_id'),
    Index('ix_fhir_observations_encounter_id', 'encounter_id'),
    Index('ix_fhir_observations_status', 'status'),
    Index('ix_fhir_conditions_patient_id', 'patient_id'),
    Index('ix_fhir_procedures_patient_id', 'patient_id'),
    Index('ix_fhir_procedures_encounter_id', 'encounter_id'),
)