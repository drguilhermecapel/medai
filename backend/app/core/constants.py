# app/core/constants.py - CORREÇÃO
from enum import Enum, IntEnum
from typing import Dict, List, Tuple

# Enums de Status
class UserRole(str, Enum):
    PHYSICIAN = "physician"
    CARDIOLOGIST = "cardiologist"
    TECHNICIAN = "technician"
    ADMIN = "admin"
    
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"

class ValidationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"

class ClinicalUrgency(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    CRITICAL = "critical"

class ModelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    TESTING = "testing"

# Constantes de ECG
ECG_STANDARD_LEADS = [
    "I", "II", "III", 
    "aVR", "aVL", "aVF",
    "V1", "V2", "V3", "V4", "V5", "V6"
]

ECG_SAMPLE_RATES = [250, 500, 1000, 2000]  # Hz

# Limites de valores normais
NORMAL_HEART_RATE_RANGE = (60, 100)  # BPM
NORMAL_PR_INTERVAL = (120, 200)  # ms
NORMAL_QRS_DURATION = (80, 120)  # ms
NORMAL_QT_INTERVAL = (350, 450)  # ms

# Condições detectáveis
DETECTABLE_CONDITIONS = [
    "normal_sinus_rhythm",
    "atrial_fibrillation",
    "atrial_flutter",
    "ventricular_tachycardia",
    "ventricular_fibrillation",
    "bradycardia",
    "tachycardia",
    "first_degree_av_block",
    "second_degree_av_block",
    "third_degree_av_block",
    "left_bundle_branch_block",
    "right_bundle_branch_block",
    "premature_atrial_complex",
    "premature_ventricular_complex",
    "st_elevation",
    "st_depression",
    "t_wave_inversion",
    "prolonged_qt"
]

# Configurações do sistema
class SystemConfig:
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES = [".txt", ".csv", ".xml", ".edf", ".dat"]
    MIN_SIGNAL_QUALITY = 0.7
    AUTO_DELETE_DAYS = 90
    MAX_CONCURRENT_ANALYSES = 10
    CACHE_TTL = 3600  # segundos

# Mensagens padrão
class Messages:
    ANALYSIS_STARTED = "ECG analysis has been started"
    ANALYSIS_COMPLETED = "ECG analysis completed successfully"
    ANALYSIS_FAILED = "ECG analysis failed: {error}"
    VALIDATION_REQUIRED = "This ECG requires medical validation"
    CRITICAL_FINDING = "Critical finding detected - immediate review required"
    
# Mapeamento de condições para urgência
CONDITION_URGENCY_MAP = {
    "normal_sinus_rhythm": ClinicalUrgency.LOW,
    "bradycardia": ClinicalUrgency.NORMAL,
    "tachycardia": ClinicalUrgency.NORMAL,
    "atrial_fibrillation": ClinicalUrgency.HIGH,
    "ventricular_tachycardia": ClinicalUrgency.CRITICAL,
    "ventricular_fibrillation": ClinicalUrgency.CRITICAL,
    "st_elevation": ClinicalUrgency.CRITICAL,
    "third_degree_av_block": ClinicalUrgency.CRITICAL,
}

# Permissões por role
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["all"],
    UserRole.CARDIOLOGIST: [
        "create_analysis", "view_analysis", "validate_analysis",
        "create_patient", "view_patient", "update_patient",
        "view_reports", "create_reports"
    ],
    UserRole.PHYSICIAN: [
        "create_analysis", "view_analysis",
        "create_patient", "view_patient", "update_patient",
        "view_reports"
    ],
    UserRole.TECHNICIAN: [
        "create_analysis", "view_analysis",
        "view_patient"
    ]
}

# Export all para facilitar imports
__all__ = [
    "UserRole",
    "AnalysisStatus",
    "ValidationStatus", 
    "ClinicalUrgency",
    "NotificationType",
    "ModelStatus",
    "ECG_STANDARD_LEADS",
    "ECG_SAMPLE_RATES",
    "NORMAL_HEART_RATE_RANGE",
    "NORMAL_PR_INTERVAL",
    "NORMAL_QRS_DURATION",
    "NORMAL_QT_INTERVAL",
    "DETECTABLE_CONDITIONS",
    "SystemConfig",
    "Messages",
    "CONDITION_URGENCY_MAP",
    "ROLE_PERMISSIONS"
]

# app/core/database.py - CORREÇÃO
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Criar engine assíncrona
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Criar session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# app/core/config.py - NOVO
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/medai"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "CardioAI Pro API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # File upload
    UPLOAD_FOLDER: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        env_file = ".env"

settings = Settings()

# app/api/v1/endpoints/health.py - NOVO
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@router.get("/ready")
async def readiness_check():
    # Adicionar verificações de banco de dados, etc
    return {"status": "ready"}

# app/main.py - CORREÇÃO PARCIAL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import health

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(health.router, tags=["health"])

# Adicionar outras rotas conforme necessário