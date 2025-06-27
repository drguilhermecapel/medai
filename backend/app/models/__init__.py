"""
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
