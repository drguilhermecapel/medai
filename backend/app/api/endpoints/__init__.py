"""
API Endpoints
"""
from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
from .users import router as users_router
from .patients import router as patients_router
from .ecg import router as ecg_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(patients_router)
api_router.include_router(ecg_router)
