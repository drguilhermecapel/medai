"""
Constantes centrais do sistema MedAI
Todas as constantes, enums e valores fixos utilizados no sistema
"""
from enum import Enum, IntEnum
from typing import Dict, List, Tuple


# === ENUMS PRINCIPAIS ===

class UserRole(str, Enum):
    """Roles de usuários no sistema"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    PATIENT = "patient"
    VIEWER = "viewer"


class Gender(str, Enum):
    """Gêneros suportados"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    NOT_INFORMED = "not_informed"


class ExamType(str, Enum):
    """Tipos de exames médicos suportados (excluindo ECG)"""
    XRAY = "xray"
    CT_SCAN = "ct_scan"
    MRI = "mri"
    ULTRASOUND = "ultrasound"
    BLOOD_TEST = "blood_test"
    URINE_TEST = "urine_test"
    BIOPSY = "biopsy"
    ENDOSCOPY = "endoscopy"
    MAMMOGRAPHY = "mammography"
    BONE_DENSITY = "bone_density"
    PATHOLOGY = "pathology"
    DERMATOLOGY = "dermatology"


class ExamStatus(str, Enum):
    """Status dos exames"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ANALYZED = "analyzed"
    REVIEWED = "reviewed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class DiagnosticStatus(str, Enum):
    """Status dos diagnósticos"""
    PENDING = "pending"
    AI_ANALYSIS = "ai_analysis"
    AI_COMPLETED = "ai_completed"
    DOCTOR_REVIEW = "doctor_review"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"


class DiagnosticCategory(str, Enum):
    """Categorias de diagnóstico"""
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    PATHOLOGICAL = "pathological"
    INCONCLUSIVE = "inconclusive"
    REQUIRES_FOLLOW_UP = "requires_follow_up"


class Priority(str, Enum):
    """Níveis de prioridade"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class ClinicalUrgency(str, Enum):
    """Urgência clínica"""
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    IMMEDIATE = "immediate"


class NotificationType(str, Enum):
    """Tipos de notificação"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    DIAGNOSTIC_READY = "diagnostic_ready"
    EXAM_COMPLETED = "exam_completed"
    APPOINTMENT_REMINDER = "appointment_reminder"
    SYSTEM_ALERT = "system_alert"


class NotificationPriority(str, Enum):
    """Prioridade das notificações"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AnalysisStatus(str, Enum):
    """Status da análise de IA"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ValidationStatus(str, Enum):
    """Status de validação"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"


class ModelType(str, Enum):
    """Tipos de modelos de IA"""
    DIAGNOSTIC = "diagnostic"
    MULTI_PATHOLOGY = "multi_pathology"
    VALIDATION = "validation"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    SEGMENTATION = "segmentation"


class AppointmentStatus(str, Enum):
    """Status de consultas"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class PrescriptionStatus(str, Enum):
    """Status de prescrições"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


# === CONSTANTES NUMÉRICAS ===

# Validação de senhas
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Limites de arquivos
MAX_FILE_SIZE_MB = 10
MAX_UPLOAD_FILES = 5

# Timeouts
DEFAULT_REQUEST_TIMEOUT = 30
AI_INFERENCE_TIMEOUT = 60
DATABASE_TIMEOUT = 5

# Limites de rate limiting
DEFAULT_RATE_LIMIT = 100
RATE_LIMIT_WINDOW = 3600  # 1 hora

# Cache TTL (Time To Live)
CACHE_TTL_SHORT = 300      # 5 minutos
CACHE_TTL_MEDIUM = 1800    # 30 minutos
CACHE_TTL_LONG = 3600      # 1 hora
CACHE_TTL_EXTENDED = 86400 # 24 horas

# Paginação
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Precisão de modelos IA
MIN_AI_CONFIDENCE = 0.7
HIGH_CONFIDENCE_THRESHOLD = 0.9


# === CONSTANTES DE STRING ===

# Mensagens de erro
ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Credenciais inválidas",
    "ACCESS_DENIED": "Acesso negado",
    "RESOURCE_NOT_FOUND": "Recurso não encontrado",
    "VALIDATION_ERROR": "Erro de validação",
    "INTERNAL_ERROR": "Erro interno do servidor",
    "RATE_LIMIT_EXCEEDED": "Limite de requisições excedido",
    "FILE_TOO_LARGE": "Arquivo muito grande",
    "INVALID_FILE_TYPE": "Tipo de arquivo inválido",
    "MODEL_NOT_AVAILABLE": "Modelo de IA não disponível",
    "ANALYSIS_FAILED": "Falha na análise",
    "INSUFFICIENT_DATA": "Dados insuficientes para análise",
    "DUPLICATE_ENTRY": "Entrada duplicada",
    "EXPIRED_TOKEN": "Token expirado",
    "INVALID_TOKEN": "Token inválido",
    "WEAK_PASSWORD": "Senha muito fraca",
    "EMAIL_ALREADY_EXISTS": "Email já cadastrado",
    "USER_NOT_FOUND": "Usuário não encontrado",
    "EXAM_NOT_FOUND": "Exame não encontrado",
    "DIAGNOSTIC_NOT_FOUND": "Diagnóstico não encontrado",
    "APPOINTMENT_CONFLICT": "Conflito de horário",
    "INVALID_DATE_RANGE": "Período de datas inválido"
}

# Mensagens de sucesso
SUCCESS_MESSAGES = {
    "USER_CREATED": "Usuário criado com sucesso",
    "USER_UPDATED": "Usuário atualizado com sucesso",
    "LOGIN_SUCCESS": "Login realizado com sucesso",
    "LOGOUT_SUCCESS": "Logout realizado com sucesso",
    "EXAM_CREATED": "Exame criado com sucesso",
    "EXAM_UPDATED": "Exame atualizado com sucesso",
    "DIAGNOSTIC_COMPLETED": "Diagnóstico concluído",
    "ANALYSIS_STARTED": "Análise iniciada",
    "ANALYSIS_COMPLETED": "Análise concluída",
    "APPOINTMENT_SCHEDULED": "Consulta agendada",
    "PRESCRIPTION_CREATED": "Prescrição criada",
    "NOTIFICATION_SENT": "Notificação enviada",
    "PASSWORD_CHANGED": "Senha alterada com sucesso",
    "PROFILE_UPDATED": "Perfil atualizado",
    "FILE_UPLOADED": "Arquivo carregado com sucesso"
}

# Tipos de notificação
NOTIFICATION_TYPES = {
    "DIAGNOSTIC_READY": {
        "title": "Diagnóstico Pronto",
        "icon": "diagnostic",
        "color": "green"
    },
    "EXAM_COMPLETED": {
        "title": "Exame Concluído",
        "icon": "exam",
        "color": "blue"
    },
    "APPOINTMENT_REMINDER": {
        "title": "Lembrete de Consulta",
        "icon": "calendar",
        "color": "orange"
    },
    "SYSTEM_ALERT": {
        "title": "Alerta do Sistema",
        "icon": "alert",
        "color": "red"
    }
}


# === MAPEAMENTOS E DICIONÁRIOS ===

# Mapeamento de extensões de arquivo
FILE_EXTENSIONS = {
    "image": ["jpg", "jpeg", "png", "bmp", "tiff", "gif"],
    "medical": ["dcm", "dicom", "nii", "nifti"],
    "document": ["pdf", "doc", "docx", "txt"],
    "data": ["csv", "xlsx", "json", "xml"]
}

# Configurações de validação por tipo de exame
EXAM_VALIDATION_RULES = {
    ExamType.XRAY: {
        "required_fields": ["patient_id", "body_part", "view"],
        "file_types": ["dcm", "jpg", "png"],
        "max_file_size": 50 * 1024 * 1024  # 50MB
    },
    ExamType.CT_SCAN: {
        "required_fields": ["patient_id", "body_part", "contrast"],
        "file_types": ["dcm", "nii"],
        "max_file_size": 500 * 1024 * 1024  # 500MB
    },
    ExamType.MRI: {
        "required_fields": ["patient_id", "body_part", "sequence"],
        "file_types": ["dcm", "nii"],
        "max_file_size": 1024 * 1024 * 1024  # 1GB
    },
    ExamType.BLOOD_TEST: {
        "required_fields": ["patient_id", "test_type", "collection_date"],
        "file_types": ["pdf", "csv", "json"],
        "max_file_size": 10 * 1024 * 1024  # 10MB
    }
}

# Configurações de IA por tipo de modelo
AI_MODEL_CONFIGS = {
    ModelType.DIAGNOSTIC: {
        "input_shape": (224, 224, 3),
        "batch_size": 32,
        "confidence_threshold": 0.8,
        "preprocessing": ["resize", "normalize"]
    },
    ModelType.MULTI_PATHOLOGY: {
        "input_shape": (512, 512, 1),
        "batch_size": 16,
        "confidence_threshold": 0.7,
        "preprocessing": ["resize", "normalize", "augment"]
    },
    ModelType.VALIDATION: {
        "input_shape": (128, 128, 3),
        "batch_size": 64,
        "confidence_threshold": 0.9,
        "preprocessing": ["resize", "normalize"]
    }
}

# Mapeamento de roles para permissões
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        "create_user", "read_user", "update_user", "delete_user",
        "create_exam", "read_exam", "update_exam", "delete_exam",
        "create_diagnostic", "read_diagnostic", "update_diagnostic", "delete_diagnostic",
        "manage_system", "view_analytics", "manage_models"
    ],
    UserRole.DOCTOR: [
        "read_user", "update_user",
        "create_exam", "read_exam", "update_exam",
        "create_diagnostic", "read_diagnostic", "update_diagnostic",
        "create_appointment", "read_appointment", "update_appointment",
        "create_prescription", "read_prescription", "update_prescription"
    ],
    UserRole.NURSE: [
        "read_user",
        "create_exam", "read_exam", "update_exam",
        "read_diagnostic",
        "create_appointment", "read_appointment", "update_appointment"
    ],
    UserRole.TECHNICIAN: [
        "create_exam", "read_exam", "update_exam",
        "read_diagnostic"
    ],
    UserRole.PATIENT: [
        "read_own_data", "update_own_profile",
        "read_own_exams", "read_own_diagnostics",
        "read_own_appointments", "read_own_prescriptions"
    ],
    UserRole.VIEWER: [
        "read_exam", "read_diagnostic"
    ]
}

# Configurações de notificação por tipo
NOTIFICATION_CONFIGS = {
    NotificationType.DIAGNOSTIC_READY: {
        "template": "diagnostic_ready.html",
        "subject": "Diagnóstico Pronto - {patient_name}",
        "priority": NotificationPriority.HIGH,
        "channels": ["email", "sms", "push"]
    },
    NotificationType.EXAM_COMPLETED: {
        "template": "exam_completed.html", 
        "subject": "Exame Concluído - {exam_type}",
        "priority": NotificationPriority.NORMAL,
        "channels": ["email", "push"]
    },
    NotificationType.APPOINTMENT_REMINDER: {
        "template": "appointment_reminder.html",
        "subject": "Lembrete de Consulta - {appointment_date}",
        "priority": NotificationPriority.NORMAL,
        "channels": ["email", "sms"]
    },
    NotificationType.SYSTEM_ALERT: {
        "template": "system_alert.html",
        "subject": "Alerta do Sistema MedAI",
        "priority": NotificationPriority.URGENT,
        "channels": ["email", "push", "slack"]
    }
}


# === CONSTANTES DE SISTEMA ===

# Versões suportadas da API
SUPPORTED_API_VERSIONS = ["v1"]

# Headers padrão
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "X-API-Version": "v1",
    "X-Service": "MedAI"
}

# Configurações de cache por endpoint
CACHE_CONFIGS = {
    "/api/v1/users": CACHE_TTL_MEDIUM,
    "/api/v1/patients": CACHE_TTL_MEDIUM,
    "/api/v1/exams": CACHE_TTL_SHORT,
    "/api/v1/diagnostics": CACHE_TTL_SHORT,
    "/api/v1/models": CACHE_TTL_LONG,
    "/api/v1/health": 60  # 1 minuto
}

# Configurações de logging
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

# Padrões de URL
URL_PATTERNS = {
    "UUID": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "PHONE": r"^\+?1?\d{9,15}$"
}

# Configurações de ambiente
ENVIRONMENT_CONFIGS = {
    "development": {
        "debug": True,
        "log_level": "DEBUG",
        "cache_enabled": False,
        "rate_limit_enabled": False
    },
    "staging": {
        "debug": False,
        "log_level": "INFO",
        "cache_enabled": True,
        "rate_limit_enabled": True
    },
    "production": {
        "debug": False,
        "log_level": "WARNING",
        "cache_enabled": True,
        "rate_limit_enabled": True
    }
}


# === CONSTANTES DE VALIDAÇÃO ===

# Regras de validação de dados
VALIDATION_RULES = {
    "email": {
        "pattern": URL_PATTERNS["EMAIL"],
        "max_length": 255
    },
    "phone": {
        "pattern": URL_PATTERNS["PHONE"],
        "max_length": 15
    },
    "name": {
        "min_length": 2,
        "max_length": 100,
        "allow_special_chars": [" ", "-", "'"]
    },
    "password": {
        "min_length": MIN_PASSWORD_LENGTH,
        "max_length": MAX_PASSWORD_LENGTH,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": True
    }
}

# Limites por tipo de usuário
USER_LIMITS = {
    UserRole.PATIENT: {
        "max_exams_per_month": 10,
        "max_appointments_per_month": 5,
        "max_file_uploads_per_day": 3
    },
    UserRole.DOCTOR: {
        "max_patients": 1000,
        "max_exams_per_day": 50,
        "max_diagnostics_per_day": 100
    },
    UserRole.TECHNICIAN: {
        "max_exams_per_day": 30,
        "max_file_uploads_per_day": 50
    }
}