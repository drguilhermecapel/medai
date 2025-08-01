"""
Pydantic schemas for specialty APIs
"""

from .dermatology import (
    DermatologyLesionCreate, DermatologyLesionUpdate, DermatologyLesionResponse,
    DermatologyExaminationCreate, DermatologyExaminationUpdate, DermatologyExaminationResponse,
    ABCDEAssessmentCreate, ABCDEAssessmentResponse,
    LesionStatistics
)

__all__ = [
    # Dermatology
    "DermatologyLesionCreate",
    "DermatologyLesionUpdate", 
    "DermatologyLesionResponse",
    "DermatologyExaminationCreate",
    "DermatologyExaminationUpdate",
    "DermatologyExaminationResponse",
    "ABCDEAssessmentCreate",
    "ABCDEAssessmentResponse",
    "LesionStatistics",
]