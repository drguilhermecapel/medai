"""
API v1 router configuration.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    auth,
    medical_records,
    notifications,
    patients,
    prescriptions,
    users,
    validations)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(ai.router, prefix="/ai", tags=["artificial-intelligence"])
api_router.include_router(medical_records.router, prefix="/medical-records", tags=["medical-records"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(prescriptions.router, prefix="/prescriptions", tags=["prescriptions"])
api_router.include_router(validations.router, prefix="/validations", tags=["validations"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

