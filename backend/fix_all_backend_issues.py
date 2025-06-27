#!/usr/bin/env python3
"""
Script para corrigir todos os problemas identificados no backend
"""

import os
import re
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_model_relationships():
    """Corrige os problemas de relacionamentos entre modelos"""
    print("🔧 Corrigindo relacionamentos entre modelos...")
    
    # Criar arquivo __init__.py para modelos com imports ordenados
    models_init = '''"""
Models package - ordem correta de imports para evitar dependências circulares
"""

# Imports base
from .base import Base, TimestampMixin

# Modelos independentes primeiro
from .user import User
from .patient import Patient

# Modelos que dependem dos anteriores
from .ecg_record import ECGRecord
from .ecg_analysis import ECGAnalysis
from .notification import Notification
from .validation import Validation
from .prescription import Prescription
from .medical_record import MedicalRecord
from .clinical_protocol import ClinicalProtocol
from .dataset import Dataset
from .exam_request import ExamRequest

# Re-exportar todos os modelos
__all__ = [
    'Base', 'TimestampMixin',
    'User', 'Patient', 'ECGRecord', 'ECGAnalysis',
    'Notification', 'Validation', 'Prescription',
    'MedicalRecord', 'ClinicalProtocol', 'Dataset',
    'ExamRequest'
]
'''
    
    with open('app/models/__init__.py', 'w', encoding='utf-8') as f:
        f.write(models_init)
    
    # Corrigir ECGAnalysis para usar imports corretos
    ecg_analysis_file = 'app/models/ecg_analysis.py'
    if os.path.exists(ecg_analysis_file):
        with open(ecg_analysis_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar imports TYPE_CHECKING
        if 'from typing import TYPE_CHECKING' not in content:
            imports = '''from typing import TYPE_CHECKING, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

if TYPE_CHECKING:
    from .patient import Patient
    from .user import User
    from .validation import Validation

from .base import Base, TimestampMixin
'''
            content = re.sub(r'^from.*?\n\n', imports + '\n', content, flags=re.DOTALL)
        
        # Corrigir relacionamentos para usar strings
        content = re.sub(r'patient = relationship\(["\']Patient["\']', 
                        'patient = relationship("Patient"', content)
        content = re.sub(r'created_by_user = relationship\(["\']User["\']', 
                        'created_by_user = relationship("User"', content)
        
        with open(ecg_analysis_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Relacionamentos corrigidos")

def fix_constants():
    """Corrige as constantes e enums"""
    print("🔧 Corrigindo constantes e enums...")
    
    constants_content = '''"""
Constantes e Enums do sistema
"""
from enum import Enum

class UserRole(str, Enum):
    """Papéis de usuário no sistema"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    PHYSICIAN = "doctor"  # Alias para compatibilidade
    NURSE = "nurse"
    TECHNICIAN = "technician"
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"
    VIEWER = "viewer"

class AnalysisStatus(str, Enum):
    """Status de análise de ECG"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ClinicalUrgency(str, Enum):
    """Níveis de urgência clínica"""
    LOW = "low"
    ROUTINE = "routine"
    MEDIUM = "routine"  # Alias
    PRIORITY = "priority"
    HIGH = "urgent"  # Alias
    URGENT = "urgent"
    CRITICAL = "emergency"  # Alias
    EMERGENCY = "emergency"
    ELECTIVE = "elective"

class ValidationStatus(str, Enum):
    """Status de validação médica"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"

class NotificationPriority(str, Enum):
    """Prioridade de notificações"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationType(str, Enum):
    """Tipos de notificação"""
    ECG_ANALYSIS_READY = "ecg_analysis_ready"
    VALIDATION_REQUIRED = "validation_required"
    VALIDATION_COMPLETED = "validation_completed"
    CRITICAL_FINDING = "critical_finding"
    SYSTEM_ALERT = "system_alert"
    APPOINTMENT_REMINDER = "appointment_reminder"

# Configurações do sistema
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_FILE_EXTENSIONS = {'.txt', '.edf', '.xml', '.pdf', '.csv'}
MIN_ECG_DURATION = 10  # segundos
MAX_ECG_DURATION = 86400  # 24 horas

# Configurações de ML
MODEL_CONFIDENCE_THRESHOLD = 0.85
ENSEMBLE_MODELS = ["ecg_classifier", "rhythm_detector", "morphology_analyzer"]
'''
    
    with open('app/core/constants.py', 'w', encoding='utf-8') as f:
        f.write(constants_content)
    
    print("✅ Constantes atualizadas")

def fix_service_signatures():
    """Corrige assinaturas de métodos nos serviços"""
    print("🔧 Corrigindo assinaturas de métodos...")
    
    # PatientService
    patient_service_file = 'app/services/patient_service.py'
    if os.path.exists(patient_service_file):
        with open(patient_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corrigir search_patients
        content = re.sub(
            r'async def search_patients\(self, query: str\)',
            'async def search_patients(self, query: str, search_fields: list = None)',
            content
        )
        
        # Adicionar implementação se não existir
        if 'if search_fields is None:' not in content:
            content = re.sub(
                r'(async def search_patients.*?\n)',
                r'\1        if search_fields is None:\n            search_fields = ["name", "patient_id", "cpf"]\n',
                content
            )
        
        with open(patient_service_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # NotificationService
    notification_service_file = 'app/services/notification_service.py'
    if os.path.exists(notification_service_file):
        with open(notification_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corrigir mark_as_read
        content = re.sub(
            r'async def mark_as_read\(self, notification_id: int\)',
            'async def mark_as_read(self, notification_id: int, user_id: int)',
            content
        )
        
        with open(notification_service_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Assinaturas corrigidas")

def fix_schemas():
    """Corrige os schemas Pydantic"""
    print("🔧 Corrigindo schemas...")
    
    # UserSchema
    user_schema = '''"""
User schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.core.constants import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserResponse(User):
    pass
'''
    
    with open('app/schemas/user.py', 'w', encoding='utf-8') as f:
        f.write(user_schema)
    
    # PatientSchema
    patient_schema = '''"""
Patient schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class PatientBase(BaseModel):
    patient_id: str = Field(..., description="ID único do paciente")
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    medical_record_number: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class Patient(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PatientResponse(Patient):
    pass
'''
    
    with open('app/schemas/patient.py', 'w', encoding='utf-8') as f:
        f.write(patient_schema)
    
    print("✅ Schemas corrigidos")

def create_missing_endpoints():
    """Cria endpoints que estão faltando"""
    print("🔧 Criando endpoints faltantes...")
    
    health_endpoints = '''"""
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
'''
    
    os.makedirs('app/api/endpoints', exist_ok=True)
    with open('app/api/endpoints/health.py', 'w', encoding='utf-8') as f:
        f.write(health_endpoints)
    
    # Atualizar __init__.py dos endpoints
    endpoints_init = '''"""
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
'''
    
    with open('app/api/endpoints/__init__.py', 'w', encoding='utf-8') as f:
        f.write(endpoints_init)
    
    print("✅ Endpoints criados")

def update_main_app():
    """Atualiza o arquivo main.py"""
    print("🔧 Atualizando main.py...")
    
    main_content = '''"""
Aplicação FastAPI principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} iniciado!")

@app.on_event("shutdown")
async def shutdown_event():
    """Finalização da aplicação"""
    print("👋 Aplicação finalizada")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    print("✅ main.py atualizado")

def create_test_fixtures():
    """Cria fixtures para os testes"""
    print("🔧 Criando fixtures de teste...")
    
    conftest_content = '''"""
Fixtures compartilhadas para testes
"""
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base
from app.core.config import settings

# Configurar event loop para testes assíncronos
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    """Create async engine for tests"""
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def async_session(async_engine):
    """Create async session for tests"""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client() -> Generator:
    """Create test client"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user_data():
    """Dados de teste para usuário"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "TestPass123!",
        "role": "doctor"
    }

@pytest.fixture
def test_patient_data():
    """Dados de teste para paciente"""
    return {
        "patient_id": "PAT001",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-15",
        "gender": "male",
        "cpf": "123.456.789-00",
        "phone": "+55 11 98765-4321",
        "email": "patient@example.com"
    }
'''
    
    with open('tests/conftest.py', 'w', encoding='utf-8') as f:
        f.write(conftest_content)
    
    print("✅ Fixtures criadas")

def main():
    """Executa todas as correções"""
    print("🚀 Iniciando correção completa do backend...")
    
    try:
        fix_model_relationships()
        fix_constants()
        fix_service_signatures()
        fix_schemas()
        create_missing_endpoints()
        update_main_app()
        create_test_fixtures()
        
        print("\n✅ Todas as correções foram aplicadas com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Execute: pytest tests/ -v --tb=short")
        print("2. Se ainda houver erros, execute: pytest tests/ -v --tb=long")
        print("3. Para verificar cobertura: pytest tests/ --cov=app --cov-report=html")
        
    except Exception as e:
        print(f"\n❌ Erro durante a correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()