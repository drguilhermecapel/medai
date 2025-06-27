# app/models/patient.py - CORREÇÃO COMPLETA
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {'extend_existing': True}
    
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
    creator = relationship("User", back_populates="created_patients", lazy="select")
    ecg_analyses = relationship("ECGAnalysis", back_populates="patient", cascade="all, delete-orphan", lazy="select")
    ecg_records = relationship("ECGRecord", back_populates="patient", cascade="all, delete-orphan", lazy="select")
    diagnoses = relationship("Diagnosis", back_populates="patient", cascade="all, delete-orphan", lazy="select")
    
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

# app/models/ecg_analysis.py - CORREÇÃO COMPLETA
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.constants import AnalysisStatus

class ECGAnalysis(Base):
    __tablename__ = "ecg_analyses"
    __table_args__ = {'extend_existing': True}
    
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
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
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
    
    # Relacionamentos
    patient = relationship("Patient", back_populates="ecg_analyses", lazy="select")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_analyses", lazy="select")
    validator = relationship("User", foreign_keys=[validated_by], back_populates="validated_analyses", lazy="select")
    validations = relationship("Validation", back_populates="analysis", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        return f"<ECGAnalysis(id={self.id}, patient_id={self.patient_id}, status={self.status})>"

# app/models/ecg_record.py - CORREÇÃO COMPLETA
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ECGRecord(Base):
    __tablename__ = "ecg_records"
    __table_args__ = {'extend_existing': True}
    
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
    patient = relationship("Patient", back_populates="ecg_records", lazy="select")
    uploader = relationship("User", back_populates="uploaded_records", lazy="select")
    
    def __repr__(self):
        return f"<ECGRecord(id={self.id}, patient_id={self.patient_id})>"

# app/models/notification.py - CORREÇÃO COMPLETA
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.constants import NotificationType, ClinicalUrgency

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Conteúdo
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False, default=NotificationType.INFO)
    priority = Column(Enum(ClinicalUrgency), nullable=False, default=ClinicalUrgency.NORMAL)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Relacionamento opcional
    related_id = Column(Integer, nullable=True)
    related_type = Column(String(50), nullable=True)  # 'analysis', 'validation', etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="notifications", lazy="select")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.notification_type})>"

# app/models/validation.py - CORREÇÃO COMPLETA
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.constants import ValidationStatus, ClinicalUrgency

class Validation(Base):
    __tablename__ = "validations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("ecg_analyses.id"), nullable=False)
    validator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status da validação
    status = Column(Enum(ValidationStatus), nullable=False, default=ValidationStatus.PENDING)
    priority = Column(Enum(ClinicalUrgency), nullable=False, default=ClinicalUrgency.NORMAL)
    
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
    analysis = relationship("ECGAnalysis", back_populates="validations", lazy="select")
    validator = relationship("User", back_populates="validations", lazy="select")
    
    def __repr__(self):
        return f"<Validation(id={self.id}, analysis_id={self.analysis_id}, status={self.status})>"

# app/models/diagnosis.py - CORREÇÃO COMPLETA
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.constants import ClinicalUrgency

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("ecg_analyses.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Diagnóstico
    diagnosis_code = Column(String(20), nullable=False)  # ICD-10
    diagnosis_text = Column(Text, nullable=False)
    severity = Column(Enum(ClinicalUrgency), nullable=False, default=ClinicalUrgency.NORMAL)
    
    # Detalhes
    findings = Column(JSON, nullable=True)
    recommendations = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", back_populates="diagnoses", lazy="select")
    
    def __repr__(self):
        return f"<Diagnosis(id={self.id}, patient_id={self.patient_id}, code={self.diagnosis_code})>"

# app/models/medication.py - BÁSICO PARA COMPLETAR O IMPORT
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from app.models.base import Base

class Medication(Base):
    __tablename__ = "medications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    prescribed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Medication(id={self.id}, name={self.name})>"