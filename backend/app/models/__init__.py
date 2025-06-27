# app/models/__init__.py - CORREÇÃO COMPLETA
"""
Modelos do banco de dados
Importação ordenada para evitar dependências circulares
"""

# Importar Base primeiro
from app.models.base import Base

# Importar modelos na ordem correta de dependências
from app.models.user import User
from app.models.patient import Patient
from app.models.ecg_record import ECGRecord
from app.models.ecg_analysis import ECGAnalysis
from app.models.validation import Validation
from app.models.notification import Notification
from app.models.diagnosis import Diagnosis
from app.models.medication import Medication

# Exportar todos os modelos
__all__ = [
    "Base",
    "User",
    "Patient",
    "ECGRecord",
    "ECGAnalysis",
    "Validation",
    "Notification",
    "Diagnosis",
    "Medication"
]