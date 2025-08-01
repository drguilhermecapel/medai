"""
Modelos do banco de dados MedAI - Multi-specialty EHR system
"""
from app.models.base import Base
from app.models.user import User
from app.models.patient import Patient
from app.models.exam import Exam
from app.models.diagnostic import Diagnostic
from app.models.prescription import Prescription
from app.models.appointment import Appointment
from app.models.notification import Notification

# FHIR-compliant models
from app.models.fhir_base import (
    FHIRResource, FHIRPatient, FHIREncounter, 
    FHIRObservation, FHIRCondition, FHIRProcedure
)

# Specialty models
from app.models.specialties.dermatology import (
    DermatologyLesion, DermatologyExamination
)
from app.models.specialties.pediatrics import (
    PediatricsGrowthChart, PediatricsVaccination, PediatricsDevelopmentAssessment
)

__all__ = [
    # Base models
    'Base',
    'User',
    'Patient',
    'Exam',
    'Diagnostic',
    'Prescription',
    'Appointment',
    'Notification',
    
    # FHIR models
    'FHIRResource',
    'FHIRPatient',
    'FHIREncounter',
    'FHIRObservation',
    'FHIRCondition',
    'FHIRProcedure',
    
    # Dermatology
    'DermatologyLesion',
    'DermatologyExamination',
    
    # Pediatrics
    'PediatricsGrowthChart',
    'PediatricsVaccination',
    'PediatricsDevelopmentAssessment',
]