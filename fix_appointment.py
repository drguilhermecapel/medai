print('🔧 CRIANDO CLASSE APPOINTMENT...')

appointment_class = '''
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Appointment(BaseModel):
    """Appointment model"""
    __tablename__ = 'appointments'
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(50), default='scheduled')
    is_virtual = Column(Boolean, default=False)
    meeting_url = Column(String(500))
    notes = Column(Text)
    
    # Relationships
    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('User', back_populates='appointments')

class Prescription(BaseModel):
    """Prescription model"""
    __tablename__ = 'prescriptions'
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    medication_name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    instructions = Column(Text)
    
    # Relationships
    appointment = relationship('Appointment')
'''

# Criar diretório models se não existir
import os
os.makedirs('backend/app/models', exist_ok=True)

with open('backend/app/models/appointment.py', 'w', encoding='utf-8') as f:
    f.write(appointment_class)

print('✅ Classe Appointment criada!')

