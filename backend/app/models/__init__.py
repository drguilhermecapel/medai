# app/models/__init__.py
"""
Centralização de imports para evitar problemas de referência circular
"""
from app.models.base import Base
from app.models.user import User
from app.models.patient import Patient
from app.models.ecg_record import ECGRecord
from app.models.ecg_analysis import ECGAnalysis
from app.models.validation import Validation
from app.models.notification import Notification
from app.models.diagnosis import Diagnosis
from app.models.medication import Medication

# Registrar todos os modelos para evitar problemas de mapeamento
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

# ===================================
# app/models/ecg_analysis.py - CORREÇÃO
# ===================================
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base

class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"

class ECGAnalysis(Base):
    __tablename__ = "ecg_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadados do ECG
    acquisition_date = Column(DateTime, nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    
    # Parâmetros técnicos
    sample_rate = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    leads_count = Column(Integer, nullable=False)
    leads_names = Column(JSON, nullable=False)
    
    # Status e resultados
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    analysis_results = Column(JSON, nullable=True)
    ai_predictions = Column(JSON, nullable=True)
    quality_metrics = Column(JSON, nullable=True)
    
    # Interpretação e validação
    interpretation = Column(Text, nullable=True)
    clinical_notes = Column(Text, nullable=True)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos - Importação no final do arquivo
    patient = relationship("Patient", back_populates="ecg_analyses")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_analyses")
    validator = relationship("User", foreign_keys=[validated_by], back_populates="validated_analyses")
    validations = relationship("Validation", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ECGAnalysis(id={self.id}, patient_id={self.patient_id}, status={self.status})>"

# ===================================
# app/models/ecg_record.py - CORREÇÃO
# ===================================
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base

class ECGRecord(Base):
    __tablename__ = "ecg_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Arquivo e metadados
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)
    
    # Informações técnicas
    sample_rate = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    leads = Column(JSON, nullable=False)
    
    # Qualidade e processamento
    quality_score = Column(Float, nullable=True)
    preprocessing_applied = Column(JSON, nullable=True)
    
    # Timestamps
    recorded_at = Column(DateTime, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", back_populates="ecg_records")
    uploader = relationship("User", back_populates="uploaded_records")
    
    def __repr__(self):
        return f"<ECGRecord(id={self.id}, patient_id={self.patient_id})>"

# ===================================
# app/models/patient.py - CORREÇÃO
# ===================================
from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Informações pessoais
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)
    
    # Contato
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    
    # Informações médicas
    blood_type = Column(String(10), nullable=True)
    allergies = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    
    # Metadados
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    creator = relationship("User", back_populates="created_patients")
    ecg_analyses = relationship("ECGAnalysis", back_populates="patient", cascade="all, delete-orphan")
    ecg_records = relationship("ECGRecord", back_populates="patient", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="patient", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.full_name})>"

# ===================================
# app/models/user.py - CORREÇÃO
# ===================================
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Informações profissionais
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # physician, cardiologist, technician, admin
    license_number = Column(String(50), nullable=True)
    specialization = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relacionamentos
    created_patients = relationship("Patient", back_populates="creator")
    created_analyses = relationship("ECGAnalysis", foreign_keys="ECGAnalysis.created_by", back_populates="creator")
    validated_analyses = relationship("ECGAnalysis", foreign_keys="ECGAnalysis.validated_by", back_populates="validator")
    uploaded_records = relationship("ECGRecord", back_populates="uploader")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    validations = relationship("Validation", back_populates="validator", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

# ===================================
# app/models/validation.py - CORREÇÃO
# ===================================
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base

class Validation(Base):
    __tablename__ = "validations"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("ecg_analyses.id"), nullable=False)
    validator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status da validação
    status = Column(String(50), nullable=False)  # pending, approved, rejected, requires_review
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Feedback
    comments = Column(Text, nullable=True)
    corrections = Column(Text, nullable=True)
    
    # Flags
    is_urgent = Column(Boolean, default=False)
    requires_senior_review = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    analysis = relationship("ECGAnalysis", back_populates="validations")
    validator = relationship("User", back_populates="validations")
    
    def __repr__(self):
        return f"<Validation(id={self.id}, analysis_id={self.analysis_id}, status={self.status})>"