# app/models/user.py - CORREÇÃO COMPLETA
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.constants import UserRole

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Informações profissionais
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PHYSICIAN)
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
    created_patients = relationship("Patient", back_populates="creator", lazy="select")
    created_analyses = relationship(
        "ECGAnalysis", 
        foreign_keys="ECGAnalysis.created_by", 
        back_populates="creator",
        lazy="select"
    )
    validated_analyses = relationship(
        "ECGAnalysis", 
        foreign_keys="ECGAnalysis.validated_by", 
        back_populates="validator",
        lazy="select"
    )
    uploaded_records = relationship("ECGRecord", back_populates="uploader", lazy="select")
    notifications = relationship(
        "Notification", 
        back_populates="user", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    validations = relationship(
        "Validation", 
        back_populates="validator", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"