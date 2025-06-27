"""
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
    NORMAL = "medium"  # Alias para MEDIUM
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
    INFO = "info"  # Informação geral

class ModelType(str, Enum):
    """Tipos de modelos de ML"""
    ECG_CLASSIFIER = "ecg_classifier"
    RHYTHM_DETECTOR = "rhythm_detector"
    MORPHOLOGY_ANALYZER = "morphology_analyzer"
    RISK_PREDICTOR = "risk_predictor"

class DiagnosisCategory(str, Enum):
    """Categorias de diagnóstico"""
    NORMAL = "normal"
    ARRHYTHMIA = "arrhythmia"
    CONDUCTION_DISTURBANCE = "conduction_disturbance"
    ISCHEMIA = "ischemia"
    HYPERTROPHY = "hypertrophy"
    OTHER = "other"

# Aliases para compatibilidade
UserRoles = UserRole  # Alguns testes usam UserRoles

# Configurações do sistema
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_FILE_EXTENSIONS = {'.txt', '.edf', '.xml', '.pdf', '.csv'}
MIN_ECG_DURATION = 10  # segundos
MAX_ECG_DURATION = 86400  # 24 horas

# Configurações de ML
MODEL_CONFIDENCE_THRESHOLD = 0.85
ENSEMBLE_MODELS = ["ecg_classifier", "rhythm_detector", "morphology_analyzer"]

# Configurações de API
API_V1_STR = "/api/v1"

class ConfidenceLevel(str, Enum):
    """Níveis de confiança para diagnósticos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class ModelStatus(str, Enum):
    """Status dos modelos de ML"""
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    UPDATING = "updating"

class ECGLeads(str, Enum):
    """Derivações do ECG"""
    I = "I"
    II = "II"
    III = "III"
    aVR = "aVR"
    aVL = "aVL"
    aVF = "aVF"
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V5 = "V5"
    V6 = "V6"
