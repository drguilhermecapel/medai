"""
Modelos do banco de dados MedAI
"""

# Importa todos os modelos para garantir que sejam registrados no SQLAlchemy
from app.models.user import User, UserSession, APIKey
from app.models.patient import Patient, PatientHistory, EmergencyContact
from app.models.ecg_record import ECGRecord, ECGData, ECGFile
from app.models.ecg_analysis import ECGAnalysis, ECGAnnotation, ECGMeasurement
from app.models.diagnosis import Diagnosis
from app.models.medication import Medication
from app.models.notification import Notification

# Exporta os modelos principais
__all__ = [
    # User models
    "User",
    "UserSession", 
    "APIKey",
    
    # Patient models
    "Patient",
    "PatientHistory",
    "EmergencyContact",
    
    # ECG models
    "ECGRecord",
    "ECGData",
    "ECGFile",
    "ECGAnalysis",
    "ECGAnnotation",
    "ECGMeasurement",
    
    # Other core models
    "Diagnosis",
    "Medication",
    "Notification",
]