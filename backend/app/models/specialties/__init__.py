"""
Medical specialties models package
Contains FHIR-compliant models for each medical specialty
"""

from .dermatology import DermatologyLesion, DermatologyExamination
from .pediatrics import PediatricsGrowthChart, PediatricsVaccination, PediatricsDevelopmentAssessment

__all__ = [
    # Dermatology
    "DermatologyLesion",
    "DermatologyExamination",
    
    # Pediatrics
    "PediatricsGrowthChart",
    "PediatricsVaccination", 
    "PediatricsDevelopmentAssessment",
]