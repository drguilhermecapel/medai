"""Pydantic schemas."""

# Importante: certificar-se de que os schemas estão sendo importados corretamente
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.ecg import ECGAnalysis, ECGAnalysisCreate
from app.schemas.validation import Validation, ValidationCreate, ValidationUpdate

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "ECGAnalysis", "ECGAnalysisCreate",
    "Validation", "ValidationCreate", "ValidationUpdate"
]


