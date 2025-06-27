"""
Modelos relacionados a diagnósticos
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy import String, DateTime, Float, Integer, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship as db_relationship, Mapped, mapped_column

from app.database import Base
from app.core.constants import (
    DiagnosisCategory, ClinicalUrgency, ValidationStatus,
    ECGDiagnosisType, RiskLevel
)


class Diagnosis(Base):
    """Modelo principal de diagnóstico"""
    __tablename__ = "diagnoses"
    
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
    
    analysis_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("ecg_analyses.id", ondelete="SET NULL")
    )
    
    doctor_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    
    # Informações do diagnóstico
    diagnosis_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        default=lambda: f"DIAG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid4())[:8]}"
    )
    
    diagnosis_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    # Categoria e urgência
    category: Mapped[str] = mapped_column(
        String(30),
        default=DiagnosisCategory.BENIGN,
        nullable=False
    )
    
    urgency: Mapped[str] = mapped_column(
        String(20),
        default=ClinicalUrgency.ROUTINE,
        nullable=False
    )
    
    risk_level: Mapped[str] = mapped_column(
        String(20),
        default=RiskLevel.LOW,
        nullable=False
    )
    
    # Detalhes do diagnóstico
    primary_diagnosis: Mapped[str] = mapped_column(String(500), nullable=False)
    secondary_diagnoses: Mapped[Optional[List[str]]] = mapped_column(JSON)
    differential_diagnoses: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # CID-10
    icd10_codes: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Descrição e observações
    description: Mapped[Optional[str]] = mapped_column(Text)
    clinical_findings: Mapped[Optional[str]] = mapped_column(Text)
    recommendations: Mapped[Optional[str]] = mapped_column(Text)
    
    # Scores e métricas
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    severity_score: Mapped[Optional[float]] = mapped_column(Float)
    risk_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Dados estruturados
    findings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Status de validação
    validation_status: Mapped[str] = mapped_column(
        String(20),
        default=ValidationStatus.PENDING,
        nullable=False
    )
    
    validated_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id")
    )
    
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    validation_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Flags importantes
    requires_followup: Mapped[bool] = mapped_column(Boolean, default=False)
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    diagnosis_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
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
    patient = db_relationship("Patient", back_populates="diagnoses")
    analysis = db_relationship("ECGAnalysis", back_populates="diagnoses")
    
    # Índices
    __table_args__ = (
        Index("idx_diagnoses_patient_id", "patient_id"),
        Index("idx_diagnoses_analysis_id", "analysis_id"),
        Index("idx_diagnoses_doctor_id", "doctor_id"),
        Index("idx_diagnoses_diagnosis_code", "diagnosis_code"),
        Index("idx_diagnoses_category", "category"),
        Index("idx_diagnoses_urgency", "urgency"),
        Index("idx_diagnoses_validation_status", "validation_status"),
        Index("idx_diagnoses_diagnosis_date", "diagnosis_date"),
        Index("idx_diagnoses_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<Diagnosis {self.diagnosis_code} - {self.primary_diagnosis[:50]}...>"
    
    @property
    def is_critical(self) -> bool:
        """Verifica se o diagnóstico é crítico"""
        return (
            self.category in [DiagnosisCategory.CRITICAL, DiagnosisCategory.LIFE_THREATENING] or
            self.urgency == ClinicalUrgency.EMERGENCY or
            self.is_emergency
        )
    
    @property
    def needs_immediate_attention(self) -> bool:
        """Verifica se precisa de atenção imediata"""
        return (
            self.is_critical or
            self.urgency in [ClinicalUrgency.URGENT, ClinicalUrgency.EMERGENCY] or
            self.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]
        )
    
    def to_summary(self) -> Dict[str, Any]:
        """Retorna um resumo do diagnóstico"""
        return {
            "diagnosis_code": self.diagnosis_code,
            "primary_diagnosis": self.primary_diagnosis,
            "category": self.category,
            "urgency": self.urgency,
            "risk_level": self.risk_level,
            "is_critical": self.is_critical,
            "needs_immediate_attention": self.needs_immediate_attention,
            "confidence_score": self.confidence_score,
            "validation_status": self.validation_status,
            "requires_followup": self.requires_followup
        }