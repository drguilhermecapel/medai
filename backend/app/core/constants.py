# Adicionar ao arquivo app/core/constants.py após os enums existentes

# Atualizar UserRole para incluir PHYSICIAN
class UserRole(str, Enum):
    PHYSICIAN = "physician"
    CARDIOLOGIST = "cardiologist"
    TECHNICIAN = "technician"
    ADMIN = "admin"
    VIEWER = "viewer"  # Adicionar se necessário
    PATIENT = "patient"  # Adicionar se necessário
    RECEPTIONIST = "receptionist"  # Adicionar se necessário
    NURSE = "nurse"  # Adicionar se necessário
    DOCTOR = "doctor"  # Adicionar se necessário

# Atualizar AnalysisStatus
class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"  # Adicionar
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"

# Atualizar ClinicalUrgency
class ClinicalUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"  # Adicionar
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    ROUTINE = "routine"  # Adicionar
    PRIORITY = "priority"  # Adicionar
    URGENT = "urgent"
    EMERGENCY = "emergency"  # Adicionar
    ELECTIVE = "elective"  # Adicionar

# Atualizar ValidationStatus
class ValidationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"

# Adicionar enum para tipos de modelo
class ModelType(str, Enum):
    ECG_CLASSIFIER = "ecg_classifier"
    RISK_PREDICTOR = "risk_predictor"
    ARRHYTHMIA_DETECTOR = "arrhythmia_detector"