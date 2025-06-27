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
