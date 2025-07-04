"""
Modelos relacionados a medicamentos e prescrições
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy import String, DateTime, Date, Float, Integer, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship as db_relationship, Mapped, mapped_column

from app.database import Base
from app.core.constants import (
    MedicationFrequency, DosageUnit, TreatmentType, ValidationStatus
)

class Medication(Base):
    """Modelo principal de medicamento/prescrição"""
    __tablename__ = "medications"
    __table_args__ = {"extend_existing": True}
    
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
    
    prescribed_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    
    diagnosis_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("diagnoses.id", ondelete="SET NULL")
    )
    
    # Informações do medicamento
    medication_name: Mapped[str] = mapped_column(String(255), nullable=False)
    generic_name: Mapped[Optional[str]] = mapped_column(String(255))
    brand_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Classificação
    drug_class: Mapped[Optional[str]] = mapped_column(String(100))
    therapeutic_class: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Dosagem
    dosage: Mapped[float] = mapped_column(Float, nullable=False)
    dosage_unit: Mapped[str] = mapped_column(
        String(20),
        default=DosageUnit.MG,
        nullable=False
    )
    
    # Frequência
    frequency: Mapped[str] = mapped_column(
        String(30),
        default=MedicationFrequency.TWICE_DAILY,
        nullable=False
    )
    
    custom_frequency: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Via de administração
    route: Mapped[str] = mapped_column(
        String(50),
        default="oral",
        nullable=False
    )  # oral, intravenous, intramuscular, subcutaneous, topical, etc.
    
    # Período de tratamento
    start_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False
    )
    
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    is_continuous: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Instruções
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    special_instructions: Mapped[Optional[str]] = mapped_column(Text)
    food_instructions: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Quantidade
    quantity_prescribed: Mapped[Optional[int]] = mapped_column(Integer)
    refills_allowed: Mapped[int] = mapped_column(Integer, default=0)
    refills_remaining: Mapped[int] = mapped_column(Integer, default=0)
    
    # Indicação
    indication: Mapped[Optional[str]] = mapped_column(String(500))
    treatment_type: Mapped[Optional[str]] = mapped_column(String(30))
    
    # Contraindicações e alertas
    contraindications: Mapped[Optional[List[str]]] = mapped_column(JSON)
    warnings: Mapped[Optional[List[str]]] = mapped_column(JSON)
    interactions: Mapped[Optional[List[str]]] = mapped_column(JSON)
    side_effects: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    suspension_reason: Mapped[Optional[str]] = mapped_column(String(500))
    suspension_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Validação
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
    
    # Adesão ao tratamento
    adherence_score: Mapped[Optional[float]] = mapped_column(Float)
    missed_doses: Mapped[int] = mapped_column(Integer, default=0)
    last_taken_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Informações adicionais
    notes: Mapped[Optional[str]] = mapped_column(Text)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Controle de substância
    is_controlled: Mapped[bool] = mapped_column(Boolean, default=False)
    controlled_substance_schedule: Mapped[Optional[str]] = mapped_column(String(10))
    
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
    patient = db_relationship("Patient", back_populates="medications")
    prescriber = db_relationship("User", foreign_keys=[prescribed_by])
    validator = db_relationship("User", foreign_keys=[validated_by])
    diagnosis = db_relationship("Diagnosis", backref="medications")
    
    # Índices
    __table_args__ = (
        Index("idx_medications_patient_id", "patient_id"),
        Index("idx_medications_prescribed_by", "prescribed_by"),
        Index("idx_medications_diagnosis_id", "diagnosis_id"),
        Index("idx_medications_medication_name", "medication_name"),
        Index("idx_medications_start_date", "start_date"),
        Index("idx_medications_is_active", "is_active"),
        Index("idx_medications_validation_status", "validation_status"),
        Index("idx_medications_created_at", "created_at"))
    
    def __repr__(self):
        return f"<Medication {self.id} - {self.medication_name} for Patient {self.patient_id}>"
    
    @property
    def is_expired(self) -> bool:
        """Verifica se a prescrição está expirada"""
        if self.end_date:
            return date.today() > self.end_date
        return False
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Calcula quantos dias restam de tratamento"""
        if self.end_date and not self.is_expired:
            return (self.end_date - date.today()).days
        return None
    
    @property
    def requires_refill(self) -> bool:
        """Verifica se precisa de renovação"""
        if self.is_continuous:
            return self.refills_remaining == 0
        return self.is_expired and self.refills_remaining > 0
    
    def calculate_next_dose_time(self) -> Optional[datetime]:
        """Calcula o horário da próxima dose"""
        if not self.is_active or self.is_suspended:
            return None
            
        if self.last_taken_at:
            # Calcula baseado na frequência
            if self.frequency == MedicationFrequency.ONCE_DAILY:
                return self.last_taken_at + timedelta(days=1)
            elif self.frequency == MedicationFrequency.TWICE_DAILY:
                return self.last_taken_at + timedelta(hours=12)
            elif self.frequency == MedicationFrequency.THREE_TIMES_DAILY:
                return self.last_taken_at + timedelta(hours=8)
            elif self.frequency == MedicationFrequency.FOUR_TIMES_DAILY:
                return self.last_taken_at + timedelta(hours=6)
            elif self.frequency == MedicationFrequency.EVERY_6_HOURS:
                return self.last_taken_at + timedelta(hours=6)
            elif self.frequency == MedicationFrequency.EVERY_8_HOURS:
                return self.last_taken_at + timedelta(hours=8)
            elif self.frequency == MedicationFrequency.EVERY_12_HOURS:
                return self.last_taken_at + timedelta(hours=12)
        
        return None
    
    def to_prescription_format(self) -> Dict[str, Any]:
        """Formata para impressão de receita"""
        return {
            "medication": f"{self.medication_name} ({self.generic_name})" if self.generic_name else self.medication_name,
            "dosage": f"{self.dosage} {self.dosage_unit}",
            "frequency": self.custom_frequency or self.frequency,
            "route": self.route,
            "duration": f"{self.duration_days} dias" if self.duration_days else "Uso contínuo" if self.is_continuous else None,
            "quantity": self.quantity_prescribed,
            "refills": self.refills_allowed,
            "instructions": self.instructions,
            "special_instructions": self.special_instructions
        }