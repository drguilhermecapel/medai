"""
Patient model
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin

class Patient(Base, TimestampMixin):
    """Patient model"""
    __tablename__ = "patients"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20))
    cpf = Column(String(20), unique=True, index=True)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    medical_record_number = Column(String(50), unique=True)
    
    # Relationships
    ecg_records = relationship("ECGRecord", back_populates="patient", cascade="all, delete-orphan")
    ecg_analyses = relationship("ECGAnalysis", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient {self.patient_id}: {self.first_name} {self.last_name}>"
