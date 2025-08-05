"""
Services package for MedAI Pro backend.

This module provides all service classes for business logic implementation.
"""

from .multi_specialty_emr import (
    MultiSpecialtyEMRService,
    ConsultationType,
    CoordinationStatus,
    MultiSpecialtyCase
)

__all__ = [
    "MultiSpecialtyEMRService",
    "ConsultationType", 
    "CoordinationStatus",
    "MultiSpecialtyCase"
]
