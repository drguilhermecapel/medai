# app/api/__init__.py
"""API module"""

# app/api/v1/__init__.py
"""API v1 module"""

# app/api/v1/endpoints/__init__.py
"""API v1 endpoints"""

# Importar todos os routers quando estiverem disponíveis
from .auth import router as auth_router
from .users import router as users_router
from .patients import router as patients_router
from .ecg_analysis import router as ecg_router
from .validations import router as validations_router
from .notifications import router as notifications_router

__all__ = [
    "auth_router",
    "users_router", 
    "patients_router",
    "ecg_router",
    "validations_router",
    "notifications_router"
]

# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "CardioAI Pro API",
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check including database"""
    try:
        # Testar conexão com banco
        await db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "not ready",
            "database": "disconnected",
            "error": str(e)
        }

@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check"""
    try:
        # Verificar banco de dados
        result = await db.execute(text("SELECT version()"))
        db_version = result.scalar()
        
        return {
            "status": "healthy",
            "service": "CardioAI Pro API",
            "version": "1.0.0",
            "database": {
                "status": "connected",
                "version": db_version
            },
            "timestamp": "2025-01-27T12:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }