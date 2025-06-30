"""
Modelos do banco de dados MedAI
"""
from app.models.base import Base
from app.models.user import User
from app.models.patient import Patient
from app.models.exam import Exam
from app.models.diagnostic import Diagnostic
from app.models.prescription import Prescription
from app.models.appointment import Appointment
from app.models.notification import Notification

__all__ = [
    'Base',
    'User',
    'Patient',
    'Exam',
    'Diagnostic',
    'Prescription',
    'Appointment',
    'Notification'
]