"""
Constantes do sistema MedAI
"""
from enum import Enum


class UserRoles(str, Enum):
    """Papéis de usuário no sistema"""
    VIEWER = "viewer"
    PATIENT = "patient"
    RECEPTIONIST = "receptionist"
    TECHNICIAN = "technician"
    NURSE = "nurse"
    DOCTOR = "doctor"
    PHYSICIAN = "physician"  # Alias para compatibilidade
    ADMIN = "admin"


class AnalysisStatus(str, Enum):
    """Status de análise"""
    PENDING = "pending"
    PROCESSING = "processing"  # Adicionado
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REQUIRES_REVIEW = "requires_review"


class ClinicalUrgency(str, Enum):
    """Níveis de urgência clínica"""
    LOW = "low"
    ROUTINE = "routine"
    MEDIUM = "medium"  # Adicionado
    PRIORITY = "priority"
    URGENT = "urgent"
    CRITICAL = "critical"  # Adicionado
    EMERGENCY = "emergency"
    ELECTIVE = "elective"


class ValidationStatus(str, Enum):
    """Status de validação"""
    PENDING = "pending"
    VALIDATED = "validated"
    APPROVED = "approved"  # Adicionado para compatibilidade
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class NotificationChannel(str, Enum):
    """Canais de notificação"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Prioridade de notificações"""
    LOW = "low"
    NORMAL = "normal"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    """Tipos de notificação"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ALERT = "alert"
    REMINDER = "reminder"


class NotificationStatus(str, Enum):
    """Status de notificação"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ExamType(str, Enum):
    """Tipos de exame"""
    ECG = "ecg"
    XRAY = "xray"
    MRI = "mri"
    CT_SCAN = "ct_scan"
    ULTRASOUND = "ultrasound"
    BLOOD_TEST = "blood_test"
    URINE_TEST = "urine_test"


class Gender(str, Enum):
    """Gênero"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    NOT_SPECIFIED = "not_specified"


class BloodType(str, Enum):
    """Tipos sanguíneos"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"


class AppointmentStatus(str, Enum):
    """Status de agendamento"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class PaymentStatus(str, Enum):
    """Status de pagamento"""
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


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


class DosageUnit(str, Enum):
    """Unidades de dosagem"""
    MG = "mg"
    ML = "ml"
    MCG = "mcg"
    G = "g"
    UNITS = "units"
    DROPS = "drops"
    TABLETS = "tablets"
    CAPSULES = "capsules"
    INHALATIONS = "inhalations"


class ConfidenceLevel(str, Enum):
    """Níveis de confiança"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ModelStatus(str, Enum):
    """Status de modelos de ML"""
    DRAFT = "draft"
    TRAINING = "training"
    TRAINED = "trained"
    VALIDATING = "validating"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class ModelType(str, Enum):
    """Tipos de modelos de ML"""
    ECG_CLASSIFIER = "ecg_classifier"  # Adicionado
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    MULTIMODAL = "multimodal"
    CUSTOM = "custom"


class DiagnosisCategory(str, Enum):
    """Categorias de diagnóstico"""
    NORMAL = "normal"
    BENIGN = "benign"
    POTENTIALLY_SERIOUS = "potentially_serious"
    SERIOUS = "serious"
    CRITICAL = "critical"
    LIFE_THREATENING = "life_threatening"


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


class ECGDiagnosisType(str, Enum):
    """Tipos de diagnóstico ECG"""
    NORMAL_SINUS_RHYTHM = "normal_sinus_rhythm"
    SINUS_BRADYCARDIA = "sinus_bradycardia"
    SINUS_TACHYCARDIA = "sinus_tachycardia"
    ATRIAL_FIBRILLATION = "atrial_fibrillation"
    ATRIAL_FLUTTER = "atrial_flutter"
    VENTRICULAR_TACHYCARDIA = "ventricular_tachycardia"
    VENTRICULAR_FIBRILLATION = "ventricular_fibrillation"
    FIRST_DEGREE_AV_BLOCK = "first_degree_av_block"
    SECOND_DEGREE_AV_BLOCK = "second_degree_av_block"
    THIRD_DEGREE_AV_BLOCK = "third_degree_av_block"
    LEFT_BUNDLE_BRANCH_BLOCK = "left_bundle_branch_block"
    RIGHT_BUNDLE_BRANCH_BLOCK = "right_bundle_branch_block"
    PREMATURE_ATRIAL_CONTRACTION = "premature_atrial_contraction"
    PREMATURE_VENTRICULAR_CONTRACTION = "premature_ventricular_contraction"
    ST_ELEVATION = "st_elevation"
    ST_DEPRESSION = "st_depression"
    T_WAVE_INVERSION = "t_wave_inversion"
    LONG_QT_SYNDROME = "long_qt_syndrome"
    SHORT_QT_SYNDROME = "short_qt_syndrome"
    WOLFF_PARKINSON_WHITE = "wolff_parkinson_white"
    MYOCARDIAL_INFARCTION = "myocardial_infarction"
    MYOCARDIAL_ISCHEMIA = "myocardial_ischemia"
    LEFT_VENTRICULAR_HYPERTROPHY = "left_ventricular_hypertrophy"
    RIGHT_VENTRICULAR_HYPERTROPHY = "right_ventricular_hypertrophy"
    PERICARDITIS = "pericarditis"
    OTHER = "other"


class LabTestType(str, Enum):
    """Tipos de exames laboratoriais"""
    COMPLETE_BLOOD_COUNT = "complete_blood_count"
    BASIC_METABOLIC_PANEL = "basic_metabolic_panel"
    COMPREHENSIVE_METABOLIC_PANEL = "comprehensive_metabolic_panel"
    LIPID_PANEL = "lipid_panel"
    LIVER_FUNCTION = "liver_function"
    KIDNEY_FUNCTION = "kidney_function"
    THYROID_FUNCTION = "thyroid_function"
    CARDIAC_MARKERS = "cardiac_markers"
    COAGULATION = "coagulation"
    URINALYSIS = "urinalysis"
    GLUCOSE = "glucose"
    HEMOGLOBIN_A1C = "hemoglobin_a1c"
    ELECTROLYTES = "electrolytes"
    BLOOD_GAS = "blood_gas"
    DRUG_SCREEN = "drug_screen"
    PREGNANCY_TEST = "pregnancy_test"
    INFECTIOUS_DISEASE = "infectious_disease"
    TUMOR_MARKERS = "tumor_markers"
    HORMONES = "hormones"
    VITAMINS = "vitamins"
    MINERALS = "minerals"
    ANTIBODIES = "antibodies"
    GENETIC = "genetic"
    OTHER = "other"


class ImagingType(str, Enum):
    """Tipos de exames de imagem"""
    XRAY = "xray"
    CT_SCAN = "ct_scan"
    MRI = "mri"
    ULTRASOUND = "ultrasound"
    PET_SCAN = "pet_scan"
    MAMMOGRAPHY = "mammography"
    DEXA_SCAN = "dexa_scan"
    FLUOROSCOPY = "fluoroscopy"
    ANGIOGRAPHY = "angiography"
    ECHOCARDIOGRAM = "echocardiogram"
    NUCLEAR_MEDICINE = "nuclear_medicine"
    OTHER = "other"


class AllergyType(str, Enum):
    """Tipos de alergia"""
    DRUG = "drug"
    FOOD = "food"
    ENVIRONMENTAL = "environmental"
    CONTACT = "contact"
    LATEX = "latex"
    INSECT = "insect"
    ANIMAL = "animal"
    OTHER = "other"


class AllergySeverity(str, Enum):
    """Severidade de alergia"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    LIFE_THREATENING = "life_threatening"


class VitalSignType(str, Enum):
    """Tipos de sinais vitais"""
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    TEMPERATURE = "temperature"
    RESPIRATORY_RATE = "respiratory_rate"
    OXYGEN_SATURATION = "oxygen_saturation"
    PAIN_LEVEL = "pain_level"
    WEIGHT = "weight"
    HEIGHT = "height"
    BMI = "bmi"


class SymptomSeverity(str, Enum):
    """Severidade de sintomas"""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"


class TreatmentType(str, Enum):
    """Tipos de tratamento"""
    MEDICATION = "medication"
    SURGERY = "surgery"
    THERAPY = "therapy"
    PROCEDURE = "procedure"
    LIFESTYLE = "lifestyle"
    MONITORING = "monitoring"
    PALLIATIVE = "palliative"
    PREVENTIVE = "preventive"
    EMERGENCY = "emergency"
    OTHER = "other"


class ReportType(str, Enum):
    """Tipos de relatório"""
    CONSULTATION = "consultation"
    DIAGNOSTIC = "diagnostic"
    PROGRESS = "progress"
    DISCHARGE = "discharge"
    REFERRAL = "referral"
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    SURGICAL = "surgical"
    EMERGENCY = "emergency"
    DEATH = "death"
    OTHER = "other"


class FileType(str, Enum):
    """Tipos de arquivo"""
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    DICOM = "dicom"
    ECG = "ecg"
    LAB_RESULT = "lab_result"
    REPORT = "report"
    OTHER = "other"


class QualityScore(str, Enum):
    """Scores de qualidade"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"


class RiskLevel(str, Enum):
    """Níveis de risco"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


# Configurações do sistema
class SystemConfig:
    """Configurações gerais do sistema"""
    
    # Limites de upload
    MAX_FILE_SIZE_MB = 50
    ALLOWED_FILE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.dcm', '.nii', '.csv', '.txt'}
    
    # Timeouts
    ANALYSIS_TIMEOUT_SECONDS = 300
    API_TIMEOUT_SECONDS = 30
    
    # Paginação
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Cache
    CACHE_TTL_SECONDS = 3600
    
    # Segurança
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # Tokens
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Notificações
    MAX_NOTIFICATIONS_PER_USER = 1000
    NOTIFICATION_RETENTION_DAYS = 90


# Mensagens padrão
class Messages:
    """Mensagens padrão do sistema"""
    
    # Sucesso
    LOGIN_SUCCESS = "Login realizado com sucesso"
    LOGOUT_SUCCESS = "Logout realizado com sucesso"
    CREATED_SUCCESS = "Registro criado com sucesso"
    UPDATED_SUCCESS = "Registro atualizado com sucesso"
    DELETED_SUCCESS = "Registro excluído com sucesso"
    
    # Erros
    INVALID_CREDENTIALS = "Credenciais inválidas"
    UNAUTHORIZED = "Não autorizado"
    FORBIDDEN = "Acesso negado"
    NOT_FOUND = "Registro não encontrado"
    ALREADY_EXISTS = "Registro já existe"
    VALIDATION_ERROR = "Erro de validação"
    INTERNAL_ERROR = "Erro interno do servidor"
    
    # Validações
    INVALID_EMAIL = "Email inválido"
    INVALID_PASSWORD = "Senha deve ter no mínimo 8 caracteres"
    PASSWORDS_DONT_MATCH = "Senhas não conferem"
    INVALID_TOKEN = "Token inválido ou expirado"
    
    # Análises
    ANALYSIS_STARTED = "Análise iniciada"
    ANALYSIS_COMPLETED = "Análise concluída"
    ANALYSIS_FAILED = "Falha na análise"
    ANALYSIS_CANCELLED = "Análise cancelada"


# Códigos de erro
class ErrorCodes:
    """Códigos de erro padronizados"""
    
    # Autenticação (1xxx)
    INVALID_CREDENTIALS = 1001
    TOKEN_EXPIRED = 1002
    TOKEN_INVALID = 1003
    ACCOUNT_LOCKED = 1004
    ACCOUNT_INACTIVE = 1005
    
    # Validação (2xxx)
    VALIDATION_ERROR = 2001
    MISSING_FIELD = 2002
    INVALID_FORMAT = 2003
    VALUE_OUT_OF_RANGE = 2004
    
    # Recursos (3xxx)
    NOT_FOUND = 3001
    ALREADY_EXISTS = 3002
    CONFLICT = 3003
    GONE = 3004
    
    # Permissões (4xxx)
    UNAUTHORIZED = 4001
    FORBIDDEN = 4002
    INSUFFICIENT_PERMISSIONS = 4003
    
    # Sistema (5xxx)
    INTERNAL_ERROR = 5001
    SERVICE_UNAVAILABLE = 5002
    TIMEOUT = 5003
    RATE_LIMIT_EXCEEDED = 5004
    
    # Análises (6xxx)
    ANALYSIS_FAILED = 6001
    INVALID_FILE_FORMAT = 6002
    FILE_TOO_LARGE = 6003
    PROCESSING_ERROR = 6004


# Configurações médicas
class MedicalConfig:
    """Configurações e limites médicos"""
    
    # ECG
    ECG_SAMPLE_RATE = 500  # Hz
    ECG_DURATION_SECONDS = 10
    ECG_LEADS = 12
    
    # Sinais vitais - valores normais
    NORMAL_HEART_RATE_MIN = 60
    NORMAL_HEART_RATE_MAX = 100
    NORMAL_BLOOD_PRESSURE_SYSTOLIC_MIN = 90
    NORMAL_BLOOD_PRESSURE_SYSTOLIC_MAX = 140
    NORMAL_BLOOD_PRESSURE_DIASTOLIC_MIN = 60
    NORMAL_BLOOD_PRESSURE_DIASTOLIC_MAX = 90
    NORMAL_TEMPERATURE_MIN = 36.0
    NORMAL_TEMPERATURE_MAX = 37.5
    NORMAL_OXYGEN_SATURATION_MIN = 95
    NORMAL_RESPIRATORY_RATE_MIN = 12
    NORMAL_RESPIRATORY_RATE_MAX = 20
    
    # Limites críticos
    CRITICAL_HEART_RATE_LOW = 40
    CRITICAL_HEART_RATE_HIGH = 150
    CRITICAL_BLOOD_PRESSURE_SYSTOLIC_LOW = 70
    CRITICAL_BLOOD_PRESSURE_SYSTOLIC_HIGH = 180
    CRITICAL_OXYGEN_SATURATION_LOW = 90
    
    # Pesos para cálculo de risco
    RISK_WEIGHT_AGE = 0.15
    RISK_WEIGHT_VITALS = 0.25
    RISK_WEIGHT_HISTORY = 0.30
    RISK_WEIGHT_SYMPTOMS = 0.30


# Configurações de IA
class AIConfig:
    """Configurações para modelos de IA"""
    
    # Modelos
    DEFAULT_MODEL = "gpt-4"
    FALLBACK_MODEL = "gpt-3.5-turbo"
    
    # Limites
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 60
    
    # Confiança
    MIN_CONFIDENCE_SCORE = 0.7
    HIGH_CONFIDENCE_THRESHOLD = 0.9
    
    # Processamento
    BATCH_SIZE = 32
    MAX_CONCURRENT_REQUESTS = 5


# Configurações de Cache
class CacheConfig:
    """Configurações de cache"""
    
    # TTL por tipo de dado
    USER_CACHE_TTL = 3600  # 1 hora
    PATIENT_CACHE_TTL = 1800  # 30 minutos
    ANALYSIS_CACHE_TTL = 7200  # 2 horas
    REPORT_CACHE_TTL = 86400  # 24 horas
    
    # Prefixos
    USER_PREFIX = "user:"
    PATIENT_PREFIX = "patient:"
    ANALYSIS_PREFIX = "analysis:"
    REPORT_PREFIX = "report:"
    SESSION_PREFIX = "session:"


# Configurações de Webhook
class WebhookEvents(str, Enum):
    """Eventos de webhook"""
    ANALYSIS_COMPLETED = "analysis.completed"
    ANALYSIS_FAILED = "analysis.failed"
    REPORT_GENERATED = "report.generated"
    PATIENT_REGISTERED = "patient.registered"
    APPOINTMENT_SCHEDULED = "appointment.scheduled"
    APPOINTMENT_CANCELLED = "appointment.cancelled"
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_FAILED = "payment.failed"
    USER_LOGGED_IN = "user.logged_in"
    USER_LOGGED_OUT = "user.logged_out"
    CRITICAL_ALERT = "critical.alert"
    SYSTEM_ERROR = "system.error"


# Configurações de Integração
class IntegrationProvider(str, Enum):
    """Provedores de integração"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    APPLE = "apple"
    FACEBOOK = "facebook"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SLACK = "slack"
    WEBHOOK = "webhook"
    API = "api"
    HL7 = "hl7"
    FHIR = "fhir"
    DICOM = "dicom"


# Configurações de Auditoria
class AuditAction(str, Enum):
    """Ações de auditoria"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    SHARE = "share"
    PRINT = "print"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    APPROVE = "approve"
    REJECT = "reject"
    ARCHIVE = "archive"
    RESTORE = "restore"


# Configurações de Fila
class QueuePriority(str, Enum):
    """Prioridade de fila"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class QueueStatus(str, Enum):
    """Status de fila"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


# Configurações de Armazenamento
class StorageProvider(str, Enum):
    """Provedores de armazenamento"""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    MINIO = "minio"


# Configurações de Email
class EmailTemplate(str, Enum):
    """Templates de email"""
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_REMINDER = "appointment_reminder"
    ANALYSIS_READY = "analysis_ready"
    REPORT_READY = "report_ready"
    PAYMENT_RECEIPT = "payment_receipt"
    CRITICAL_ALERT = "critical_alert"
    NEWSLETTER = "newsletter"


# Configurações de SMS
class SMSTemplate(str, Enum):
    """Templates de SMS"""
    APPOINTMENT_REMINDER = "appointment_reminder"
    ANALYSIS_READY = "analysis_ready"
    CRITICAL_ALERT = "critical_alert"
    VERIFICATION_CODE = "verification_code"
    PAYMENT_CONFIRMATION = "payment_confirmation"


# IDs de teste para desenvolvimento
class TestIDs:
    """IDs de teste para desenvolvimento"""
    TEST_USER_ID = "test-user-001"
    TEST_PATIENT_ID = "test-patient-001"
    TEST_DOCTOR_ID = "test-doctor-001"
    TEST_ANALYSIS_ID = "test-analysis-001"
    TEST_APPOINTMENT_ID = "test-appointment-001"