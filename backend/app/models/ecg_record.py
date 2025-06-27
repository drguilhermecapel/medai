"""
Modelo para registros de ECG
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy import (
    Column, String, DateTime, Float, Integer, Boolean,
    Text, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.core.constants import (
    QualityScore, ECGLeads, ExamType
)


class ECGRecord(Base):
    """Modelo para registro de ECG"""
    __tablename__ = "ecg_records"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid4())
    )
    
    # Foreign keys
    patient_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False
    )
    
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Informações básicas
    record_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    device_id: Mapped[Optional[str]] = mapped_column(String(100))
    device_model: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Parâmetros técnicos
    sample_rate: Mapped[int] = mapped_column(
        Integer, 
        default=500,
        nullable=False
    )
    
    duration_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    
    leads_count: Mapped[int] = mapped_column(
        Integer,
        default=12,
        nullable=False
    )
    
    # Qualidade do sinal
    quality_score: Mapped[str] = mapped_column(
        String(20),
        default=QualityScore.GOOD,
        nullable=False
    )
    
    noise_level: Mapped[Optional[float]] = mapped_column(Float)
    baseline_wander: Mapped[Optional[float]] = mapped_column(Float)
    
    # Dados básicos extraídos
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer)
    pr_interval: Mapped[Optional[float]] = mapped_column(Float)
    qrs_duration: Mapped[Optional[float]] = mapped_column(Float)
    qt_interval: Mapped[Optional[float]] = mapped_column(Float)
    qtc_interval: Mapped[Optional[float]] = mapped_column(Float)
    
    # Metadados
    notes: Mapped[Optional[str]] = mapped_column(Text)
    symptoms: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Status
    is_processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    is_reviewed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relacionamentos
    patient = relationship("Patient", back_populates="ecg_records")
    user = relationship("User", back_populates="ecg_records")
    ecg_data = relationship("ECGData", back_populates="ecg_record", cascade="all, delete-orphan")
    ecg_files = relationship("ECGFile", back_populates="ecg_record", cascade="all, delete-orphan")
    analyses = relationship("ECGAnalysis", back_populates="ecg_record", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index("idx_ecg_records_patient_id", "patient_id"),
        Index("idx_ecg_records_record_date", "record_date"),
        Index("idx_ecg_records_quality_score", "quality_score"),
        Index("idx_ecg_records_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<ECGRecord {self.id} - Patient: {self.patient_id} - Date: {self.record_date}>"


class ECGData(Base):
    """Modelo para dados brutos do ECG por derivação"""
    __tablename__ = "ecg_data"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid4())
    )
    
    # Foreign key
    ecg_record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ecg_records.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Derivação
    lead: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )
    
    # Dados
    signal_data: Mapped[List[float]] = mapped_column(
        JSON,
        nullable=False
    )
    
    # Estatísticas da derivação
    min_value: Mapped[Optional[float]] = mapped_column(Float)
    max_value: Mapped[Optional[float]] = mapped_column(Float)
    mean_value: Mapped[Optional[float]] = mapped_column(Float)
    std_value: Mapped[Optional[float]] = mapped_column(Float)
    
    # Qualidade específica da derivação
    lead_quality: Mapped[Optional[str]] = mapped_column(String(20))
    is_inverted: Mapped[bool] = mapped_column(Boolean, default=False)
    has_artifact: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relacionamentos
    ecg_record = relationship("ECGRecord", back_populates="ecg_data")
    
    # Índices
    __table_args__ = (
        Index("idx_ecg_data_record_id", "ecg_record_id"),
        Index("idx_ecg_data_lead", "lead"),
        UniqueConstraint("ecg_record_id", "lead", name="uq_ecg_data_record_lead"),
    )
    
    def __repr__(self):
        return f"<ECGData {self.id} - Record: {self.ecg_record_id} - Lead: {self.lead}>"


class ECGFile(Base):
    """Modelo para arquivos de ECG"""
    __tablename__ = "ecg_files"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid4())
    )
    
    # Foreign key
    ecg_record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ecg_records.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Informações do arquivo
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    file_format: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    # Metadados
    checksum: Mapped[Optional[str]] = mapped_column(String(64))
    is_original: Mapped[bool] = mapped_column(Boolean, default=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relacionamentos
    ecg_record = relationship("ECGRecord", back_populates="ecg_files")
    
    # Índices
    __table_args__ = (
        Index("idx_ecg_files_record_id", "ecg_record_id"),
        Index("idx_ecg_files_file_format", "file_format"),
    )
    
    def __repr__(self):
        return f"<ECGFile {self.id} - {self.filename}>"