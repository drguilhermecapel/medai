"""
Constantes do sistema MedAI
"""
from enum import Enum


class UserRole(str, Enum):
    """Papéis de usuário no sistema"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    PATIENT = "patient"
    VIEWER = "viewer"
    TECHNICIAN = "technician"


class ExamType(str, Enum):
    """Tipos de exames médicos"""
    ECG = "ecg"
    BLOOD_TEST = "blood_test"
    XRAY = "xray"
    MRI = "mri"
    CT_SCAN = "ct_scan"
    ULTRASOUND = "ultrasound"


class ExamStatus(str, Enum):
    """Status dos exames"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class DiagnosticStatus(str, Enum):
    """Status dos diagnósticos"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    """Níveis de prioridade"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Gender(str, Enum):
    """Gêneros"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# Configurações de validação
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100

# Configurações de paginação
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Configurações de upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf", ".dcm", ".txt", ".csv"]

# Configurações de IA/ML
ML_MODEL_VERSION = "1.0.0"
MIN_CONFIDENCE_SCORE = 0.7
MAX_PREDICTION_TIME = 30  # segundos

# Configurações de ECG
ECG_SAMPLE_RATE = 500  # Hz
ECG_DURATION = 10  # segundos
ECG_LEADS = 12
MIN_HEART_RATE = 40
MAX_HEART_RATE = 200

# Configurações de cache
CACHE_TTL = 3600  # 1 hora
CACHE_KEY_PREFIX = "medai:"

# Mensagens de erro padrão
ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Credenciais inválidas",
    "USER_NOT_FOUND": "Usuário não encontrado",
    "UNAUTHORIZED": "Não autorizado",
    "FORBIDDEN": "Acesso negado",
    "NOT_FOUND": "Recurso não encontrado",
    "INTERNAL_ERROR": "Erro interno do servidor",
    "VALIDATION_ERROR": "Erro de validação",
    "DUPLICATE_EMAIL": "Email já cadastrado",
    "DUPLICATE_USERNAME": "Nome de usuário já existe",
    "INVALID_FILE_TYPE": "Tipo de arquivo não permitido",
    "FILE_TOO_LARGE": "Arquivo muito grande",
}

# Configurações de notificação
NOTIFICATION_TYPES = {
    "EXAM_READY": "exam_ready",
    "DIAGNOSIS_COMPLETE": "diagnosis_complete",
    "APPOINTMENT_REMINDER": "appointment_reminder",
    "CRITICAL_RESULT": "critical_result",
}

# Configurações de segurança
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 24
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = 48
class DiagnosisCategory(str, Enum):
    """Diagnosis categories"""
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"
    ARRHYTHMIA = "arrhythmia"
    ISCHEMIA = "ischemia"
    INFARCTION = "infarction"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    """Notification types"""
    ALERT = "alert"
    WARNING = "warning"
    INFO = "info"
    REMINDER = "reminder"
    EMERGENCY = "emergency"
    SYSTEM = "system"


class UserRoles(str, Enum):
    """User roles (alias for UserRole)"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    VIEWER = "viewer"
    PATIENT = "patient"


class AnalysisStatus(str, Enum):
    """Analysis status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ClinicalUrgency(str, Enum):
    """Clinical urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ValidationStatus(str, Enum):
    """Validation status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    WARNING = "warning"


class ModelType(str, Enum):
    """ML Model types"""
    ECG_CLASSIFIER = "ecg_classifier"
    RISK_PREDICTOR = "risk_predictor"
    ANOMALY_DETECTOR = "anomaly_detector"
    DIAGNOSTIC_AI = "diagnostic_ai"

