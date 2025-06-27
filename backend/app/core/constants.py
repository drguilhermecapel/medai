# app/core/constants.py - CORREÇÃO (remover importação circular)
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

# Manter compatibilidade com código antigo
UserRoles = UserRole  # Alias para compatibilidade

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

# Classes adicionais que podem estar sendo usadas
class QualityScore:
    """Scores de qualidade para ECG"""
    EXCELLENT = 1.0
    GOOD = 0.8
    FAIR = 0.6
    POOR = 0.4
    UNACCEPTABLE = 0.2

class FileStatus:
    """Status de arquivos"""
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"
    DELETED = "deleted"

class DiagnosisCategory(str, Enum):
    """Categorias de diagnóstico"""
    NORMAL = "normal"
    ARRHYTHMIA = "arrhythmia"
    CONDUCTION = "conduction"
    ISCHEMIA = "ischemia"
    HYPERTROPHY = "hypertrophy"
    OTHER = "other"

class Priority(str, Enum):
    """Níveis de prioridade"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class PathologyType(str, Enum):
    """Tipos de patologia"""
    ARRHYTHMIA = "arrhythmia"
    CONDUCTION_DISORDER = "conduction_disorder"
    ISCHEMIA = "ischemia"
    STRUCTURAL = "structural"
    OTHER = "other"

class Gender(str, Enum):
    """Gêneros"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class ReportFormat(str, Enum):
    """Formatos de relatório"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"

class ConfidenceLevel(str, Enum):
    """Níveis de confiança para diagnósticos"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class DosageUnit(str, Enum):
    """Unidades de dosagem de medicamentos"""
    MG = "mg"
    MCG = "mcg"
    G = "g"
    ML = "ml"
    UI = "ui"
    DROPS = "drops"
    TABLETS = "tablets"
    CAPSULES = "capsules"

class ECGDiagnosisType(str, Enum):
    """Tipos de diagnóstico ECG"""
    NORMAL_SINUS_RHYTHM = "normal_sinus_rhythm"
    ATRIAL_FIBRILLATION = "atrial_fibrillation"
    ATRIAL_FLUTTER = "atrial_flutter"
    VENTRICULAR_TACHYCARDIA = "ventricular_tachycardia"
    BRADYCARDIA = "bradycardia"
    TACHYCARDIA = "tachycardia"
    AV_BLOCK = "av_block"
    BUNDLE_BRANCH_BLOCK = "bundle_branch_block"
    ST_ELEVATION = "st_elevation"
    ST_DEPRESSION = "st_depression"
    OTHER = "other"

class ECGLeads(str, Enum):
    """Derivações do ECG"""
    I = "I"
    II = "II"
    III = "III"
    AVR = "aVR"
    AVL = "aVL"
    AVF = "aVF"
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V5 = "V5"
    V6 = "V6"

class MedicationFrequency(str, Enum):
    """Frequência de medicação"""
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"
    EVERY_6_HOURS = "every_6_hours"
    EVERY_8_HOURS = "every_8_hours"
    EVERY_12_HOURS = "every_12_hours"
    AS_NEEDED = "as_needed"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class NotificationChannel(str, Enum):
    """Canais de notificação"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class NotificationPriority(str, Enum):
    """Prioridade de notificação"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class RiskLevel(str, Enum):
    """Níveis de risco"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class SCPCategory(str, Enum):
    """Categorias SCP-ECG"""
    DIAGNOSTIC = "diagnostic"
    RHYTHM = "rhythm"
    MORPHOLOGY = "morphology"
    TECHNICAL = "technical"

class TreatmentType(str, Enum):
    """Tipos de tratamento"""
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    SURGERY = "surgery"
    THERAPY = "therapy"
    LIFESTYLE = "lifestyle"
    MONITORING = "monitoring"
    EMERGENCY = "emergency"

# Export all para facilitar imports
__all__ = [
    "UserRole",
    "UserRoles",  # Alias para compatibilidade
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
    "ROLE_PERMISSIONS",
    "QualityScore",
    "FileStatus",
    "DiagnosisCategory",
    "Priority",
    "PathologyType",
    "Gender",
    "ReportFormat",
    "ConfidenceLevel",
    "DosageUnit",
    "ECGDiagnosisType",
    "ECGLeads",
    "MedicationFrequency",
    "NotificationChannel",
    "NotificationPriority",
    "RiskLevel",
    "SCPCategory",
    "TreatmentType"
]