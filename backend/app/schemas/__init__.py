"""
Schemas package - Multi-specialty EHR system
"""
from .user import User, UserCreate, UserUpdate, UserResponse, UserInDB
from .patient import Patient, PatientCreate, PatientUpdate, PatientResponse
from .notification import Notification, NotificationCreate, NotificationUpdate, NotificationResponse
from .validation import Validation, ValidationCreate, ValidationUpdate, ValidationResponse

# Specialty schemas
from .specialties import *

__all__ = [
    # User
    'User', 'UserCreate', 'UserUpdate', 'UserResponse', 'UserInDB',
    # Patient  
    'Patient', 'PatientCreate', 'PatientUpdate', 'PatientResponse',
    # ECG
    'ECGAnalysis', 'ECGAnalysisCreate', 'ECGAnalysisUpdate', 'ECGAnalysisResponse',
    # Notification
    'Notification', 'NotificationCreate', 'NotificationUpdate', 'NotificationResponse',
    # Validation
    'Validation', 'ValidationCreate', 'ValidationUpdate', 'ValidationResponse',
    
    # Specialties - imported from specialties package
]
