"""
Modelos relacionados a pacientes
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy import String, DateTime, Date, Float, Integer, Boolean, Text, JSON, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship as db_relationship, Mapped, mapped_column

from app.database import Base
from app.core.constants import Gender, BloodType


class Patient(Base):
    """Modelo principal de paciente"""
    __tablename__ = "patients"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid4())
    )
    
    # Informações básicas
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Documentos
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    rg: Mapped[Optional[str]] = mapped_column(String(20))
    health_card_number: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Dados pessoais
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(
        String(20),
        default=Gender.NOT_SPECIFIED,
        nullable=False
    )
    
    # Contato
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    secondary_phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Endereço
    address_street: Mapped[Optional[str]] = mapped_column(String(255))
    address_number: Mapped[Optional[str]] = mapped_column(String(20))
    address_complement: Mapped[Optional[str]] = mapped_column(String(100))
    address_neighborhood: Mapped[Optional[str]] = mapped_column(String(100))
    address_city: Mapped[Optional[str]] = mapped_column(String(100))
    address_state: Mapped[Optional[str]] = mapped_column(String(2))
    address_zip: Mapped[Optional[str]] = mapped_column(String(8))
    
    # Informações médicas básicas
    blood_type: Mapped[Optional[str]] = mapped_column(
        String(10),
        default=BloodType.UNKNOWN
    )
    
    height_cm: Mapped[Optional[float]] = mapped_column(Float)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deceased: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    death_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Preferências
    preferred_language: Mapped[str] = mapped_column(String(10), default="pt-BR")
    timezone: Mapped[str] = mapped_column(String(50), default="America/Sao_Paulo")
    
    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    
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
    ecg_records = db_relationship("ECGRecord", back_populates="patient", cascade="all, delete-orphan")
    diagnoses = db_relationship("Diagnosis", back_populates="patient", cascade="all, delete-orphan")
    medications = db_relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    patient_history = db_relationship("PatientHistory", back_populates="patient", cascade="all, delete-orphan")
    emergency_contacts = db_relationship("EmergencyContact", back_populates="patient", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index("idx_patients_cpf", "cpf"),
        Index("idx_patients_email", "email"),
        Index("idx_patients_phone", "phone"),
        Index("idx_patients_name", "first_name", "last_name"),
        Index("idx_patients_birth_date", "birth_date"),
        Index("idx_patients_created_at", "created_at"),
    )
    
    @property
    def full_name(self) -> str:
        """Retorna o nome completo do paciente"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    @property
    def age(self) -> int:
        """Calcula a idade do paciente"""
        today = date.today()
        age = today.year - self.birth_date.year
        if today.month < self.birth_date.month or (
            today.month == self.birth_date.month and today.day < self.birth_date.day
        ):
            age -= 1
        return age
    
    @property
    def bmi(self) -> Optional[float]:
        """Calcula o IMC do paciente"""
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 2)
        return None
    
    def __repr__(self):
        return f"<Patient {self.id} - {self.full_name}>"


class PatientHistory(Base):
    """Histórico médico do paciente"""
    __tablename__ = "patient_history"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid4())
    )
    
    # Foreign key
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Tipo de histórico
    history_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # medical, surgical, family, social
    
    # Detalhes
    condition: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Datas
    occurrence_date: Mapped[Optional[date]] = mapped_column(Date)
    resolution_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_chronic: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Severidade
    severity: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Informações adicionais
    related_medications: Mapped[Optional[List[str]]] = mapped_column(JSON)
    complications: Mapped[Optional[List[str]]] = mapped_column(JSON)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Quem registrou
    recorded_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id")
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
    patient = db_relationship("Patient", back_populates="patient_history")
    
    # Índices
    __table_args__ = (
        Index("idx_patient_history_patient_id", "patient_id"),
        Index("idx_patient_history_type", "history_type"),
        Index("idx_patient_history_condition", "condition"),
    )
    
    def __repr__(self):
        return f"<PatientHistory {self.id} - {self.condition}>"


class EmergencyContact(Base):
    """Contatos de emergência do paciente"""
    __tablename__ = "emergency_contacts"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid4())
    )
    
    # Foreign key
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Informações do contato
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Contatos
    primary_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    secondary_phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Endereço (opcional)
    address: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Prioridade
    priority: Mapped[int] = mapped_column(Integer, default=1)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Autorização
    can_make_decisions: Mapped[bool] = mapped_column(Boolean, default=False)
    has_access_to_records: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
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
    patient = db_relationship("Patient", back_populates="emergency_contacts")
    
    # Índices
    __table_args__ = (
        Index("idx_emergency_contacts_patient_id", "patient_id"),
        Index("idx_emergency_contacts_priority", "priority"),
    )
    
    def __repr__(self):
        return f"<EmergencyContact {self.id} - {self.name} ({self.relationship_type})>"