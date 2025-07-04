"""
Modelo de usuário do sistema MedAI
"""
from sqlalchemy import Boolean, Column, Enum, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel
from app.core.constants import UserRole


class User(BaseModel):
    """Modelo de usuário do sistema"""
    
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    
    # Informações básicas
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # Tipo de usuário
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Tokens e verificação
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Última atividade
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    
    # Preferências
    notification_preferences = Column(JSON, nullable=True)
    language = Column(String(10), default="pt-BR", nullable=False)
    timezone = Column(String(50), default="America/Sao_Paulo", nullable=False)
    
    # Relacionamentos
    patient_profile = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    # Médico
    requested_exams = relationship("Exam", foreign_keys="Exam.doctor_id", back_populates="doctor")
    diagnostics = relationship("Diagnostic", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role.value})>"
    
    @property
    def is_doctor(self) -> bool:
        """Verifica se o usuário é médico"""
        return self.role == UserRole.DOCTOR
    
    @property
    def is_patient(self) -> bool:
        """Verifica se o usuário é paciente"""
        return self.role == UserRole.PATIENT
    
    @property
    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador"""
        return self.role == UserRole.ADMIN or self.is_superuser
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica se o usuário tem uma permissão específica
        
        Args:
            permission: Nome da permissão
            
        Returns:
            True se tem a permissão
        """
        # Admin tem todas as permissões
        if self.is_admin:
            return True
        
        # Mapeamento de permissões por papel
        role_permissions = {
            UserRole.DOCTOR: [
                "view_patients",
                "create_diagnosis",
                "prescribe_medication",
                "order_exams",
                "view_exam_results",
                "update_medical_records"
            ],
            UserRole.NURSE: [
                "view_patients",
                "update_patient_vitals",
                "view_exam_results",
                "schedule_appointments"
            ],
            UserRole.TECHNICIAN: [
                "upload_exam_results",
                "update_exam_status",
                "view_exam_queue"
            ],
            UserRole.PATIENT: [
                "view_own_records",
                "schedule_appointments",
                "view_own_exams",
                "update_own_profile"
            ]
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return permission in user_permissions
    
    def update_last_login(self):
        """Atualiza timestamp do último login"""
        self.last_login = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def update_activity(self):
        """Atualiza timestamp da última atividade"""
        self.last_activity = datetime.utcnow()