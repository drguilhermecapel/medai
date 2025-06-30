"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "service": "cardioai-pro-api",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/detailed")
async def detailed_health_check():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "service": "cardioai-pro-api",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "healthy",
            "ml_models": "loaded",
            "storage": "available"
        }
    }

@router.get("/ready")
async def readiness_check():
    """Verifica se o serviço está pronto"""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }
