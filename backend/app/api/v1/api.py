"""
Router principal da API v1 do MedAI - Multi-specialty EHR system
Centraliza todas as rotas da versão 1 da API
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, patients, exams, diagnostics, 
    prescriptions, appointments, notifications, health
)
from app.core.config import settings
from app.core.feature_flags import feature_flags

# Router principal da API v1
api_router = APIRouter()

# === ROTAS DE AUTENTICAÇÃO ===
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Authentication"]
)

# === ROTAS DE USUÁRIOS ===
api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["Users"]
)

# === ROTAS DE PACIENTES ===
api_router.include_router(
    patients.router, 
    prefix="/patients", 
    tags=["Patients"]
)

# === ROTAS DE EXAMES ===
api_router.include_router(
    exams.router, 
    prefix="/exams", 
    tags=["Exams"]
)

# === ROTAS DE DIAGNÓSTICOS ===
api_router.include_router(
    diagnostics.router, 
    prefix="/diagnostics", 
    tags=["Diagnostics"]
)

# === ROTAS DE PRESCRIÇÕES ===
api_router.include_router(
    prescriptions.router, 
    prefix="/prescriptions", 
    tags=["Prescriptions"]
)

# === ROTAS DE CONSULTAS ===
api_router.include_router(
    appointments.router, 
    prefix="/appointments", 
    tags=["Appointments"]
)

# === ROTAS DE NOTIFICAÇÕES ===
api_router.include_router(
    notifications.router, 
    prefix="/notifications", 
    tags=["Notifications"]
)

# === ROTAS DE SAÚDE/MONITORAMENTO ===
api_router.include_router(
    health.router, 
    prefix="/health", 
    tags=["Health & Monitoring"]
)

# === SPECIALTY ROTAS (Feature Flag Controlled) ===
# Only include specialty routers if they are enabled via feature flags

if feature_flags.DERMATOLOGY_ENABLED:
    from app.api.v1.endpoints.specialties import dermatology_router
    api_router.include_router(
        dermatology_router,
        prefix="/specialties",
        tags=["Specialties - Dermatology"]
    )

# Add other specialty routers as they are implemented
# if feature_flags.PEDIATRICS_ENABLED:
#     from app.api.v1.endpoints.specialties import pediatrics_router
#     api_router.include_router(
#         pediatrics_router,
#         prefix="/specialties",
#         tags=["Specialties - Pediatrics"]
#     )

# if feature_flags.FAMILY_MEDICINE_ENABLED:
#     from app.api.v1.endpoints.specialties import family_medicine_router
#     api_router.include_router(
#         family_medicine_router,
#         prefix="/specialties",
#         tags=["Specialties - Family Medicine"]
#     )


# === FEATURE FLAGS ENDPOINT ===
@api_router.get("/feature-flags", tags=["Configuration"])
async def get_feature_flags():
    """
    Get current feature flags configuration
    
    Returns information about enabled specialties and features
    """
    return feature_flags.to_dict()