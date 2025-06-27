# app/models/ecg_record.py - VERSÃO CORRIGIDA
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
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
    patient = relationship("Patient", back_populates="ecg_records", lazy="select")
    uploader = relationship("User", back_populates="uploaded_records", lazy="select")
    
    def __repr__(self):
        return f"<ECGRecord(id={self.id}, patient_id={self.patient_id})>"