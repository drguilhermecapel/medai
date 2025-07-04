import re

print('🔧 ADICIONANDO TODAS AS CONSTANTS FALTANTES...')

# Ler arquivo constants
with open('backend/app/core/constants.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Todas as constants que precisamos adicionar
missing_constants = {
    'DiagnosisCategory': '''
class DiagnosisCategory(str, Enum):
    """Diagnosis categories"""
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"
    ARRHYTHMIA = "arrhythmia"
    ISCHEMIA = "ischemia"
    INFARCTION = "infarction"
''',
    'NotificationPriority': '''
class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"
''',
    'NotificationType': '''
class NotificationType(str, Enum):
    """Notification types"""
    ALERT = "alert"
    WARNING = "warning"
    INFO = "info"
    REMINDER = "reminder"
    EMERGENCY = "emergency"
    SYSTEM = "system"
''',
    'UserRoles': '''
class UserRoles(str, Enum):
    """User roles (alias for UserRole)"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    VIEWER = "viewer"
    PATIENT = "patient"
''',
    'AnalysisStatus': '''
class AnalysisStatus(str, Enum):
    """Analysis status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
''',
    'ClinicalUrgency': '''
class ClinicalUrgency(str, Enum):
    """Clinical urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
''',
    'ValidationStatus': '''
class ValidationStatus(str, Enum):
    """Validation status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    WARNING = "warning"
''',
    'ModelType': '''
class ModelType(str, Enum):
    """ML Model types"""
    ECG_CLASSIFIER = "ecg_classifier"
    RISK_PREDICTOR = "risk_predictor"
    ANOMALY_DETECTOR = "anomaly_detector"
    DIAGNOSTIC_AI = "diagnostic_ai"
'''
}

# Adicionar constants que não existem
constants_added = 0
for const_name, const_code in missing_constants.items():
    if const_name not in content:
        content += const_code + '\n'
        constants_added += 1
        print(f'   ✅ {const_name} adicionado')
    else:
        print(f'   ℹ️ {const_name} já existe')

# Salvar arquivo
with open('backend/app/core/constants.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'✅ {constants_added} constants adicionadas com sucesso!')

