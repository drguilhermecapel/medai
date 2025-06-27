# app/models/ecg_analysis.py - CORREÇÃO FINAL
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
    
    # Relacionamentos - usar strings para evitar problemas de importação circular
    patient = relationship("Patient", back_populates="ecg_analyses", lazy="select")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_analyses", lazy="select")
    validator = relationship("User", foreign_keys=[validated_by], back_populates="validated_analyses", lazy="select")
    validations = relationship("Validation", back_populates="analysis", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        return f"<ECGAnalysis(id={self.id}, patient_id={self.patient_id}, status={self.status})>"