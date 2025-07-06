"""
Router principal da API v1 do MedAI
Centraliza todas as rotas da versão 1 da API
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, patients, exams, diagnostics, 
    prescriptions, appointments, notifications, health
)
from app.core.config import settings

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