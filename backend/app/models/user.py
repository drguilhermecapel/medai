"""
Modelo de usuário do sistema MedAI
Define usuários médicos, técnicos, pacientes e administrativos
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid_property import hybrid_property

from app.models.base import AuditableModel, StatusMixin, MetadataMixin
from app.core.constants import UserRole, Gender
from app.core.security import password_manager


class User(AuditableModel, StatusMixin, MetadataMixin):
    """
    Modelo de usuário do sistema
    
    Suporta diferentes tipos de usuários:
    - Administradores
    - Médicos
    - Enfermeiros
    - Técnicos
    - Pacientes
    - Visualizadores
    """
    
    __tablename__ = "users"
    
    # === CAMPOS BÁSICOS ===
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Email do usuário (usado para login)"
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        doc="Hash da senha do usuário"
    )
    
    # === INFORMAÇÕES PESSOAIS ===
    first_name = Column(
        String(100),
        nullable=False,
        doc="Primeiro nome"
    )
    
    last_name = Column(
        String(100),
        nullable=False,
        doc="Sobrenome"
    )
    
    full_name = Column(
        String(255),
        nullable=True,
        doc="Nome completo (gerado automaticamente)"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        doc="Telefone de contato"
    )
    
    birth_date = Column(
        DateTime,
        nullable=True,
        doc="Data de nascimento"
    )
    
    gender = Column(
        String(20),
        nullable=True,
        doc="Gênero do usuário"
    )
    
    # === INFORMAÇÕES PROFISSIONAIS ===
    role = Column(
        String(50),
        nullable=False,
        default=UserRole.PATIENT.value,
        index=True,
        doc="Role/função do usuário no sistema"
    )
    
    professional_id = Column(
        String(50),
        nullable=True,
        unique=True,
        doc="Registro profissional (CRM, COREN, etc.)"
    )
    
    specialization = Column(
        String(100),
        nullable=True,
        doc="Especialização médica"
    )
    
    institution = Column(
        String(255),
        nullable=True,
        doc="Instituição onde trabalha"
    )
    
    department = Column(
        String(100),
        nullable=True,
        doc="Departamento/setor"
    )
    
    # === CONFIGURAÇÕES DE CONTA ===
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Conta ativa"
    )
    
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Email verificado"
    )
    
    is_premium = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Usuário premium"
    )
    
    # === CAMPOS DE ACESSO ===
    last_login = Column(
        DateTime,
        nullable=True,
        doc="Último login"
    )
    
    login_count = Column(
        String(10),
        default="0",
        doc="Contador de logins"
    )
    
    failed_login_attempts = Column(
        String(5),
        default="0",
        doc="Tentativas de login falhadas"
    )
    
    locked_until = Column(
        DateTime,
        nullable=True,
        doc="Conta bloqueada até esta data"
    )
    
    # === CAMPOS DE VERIFICAÇÃO ===
    verification_token = Column(
        String(255),
        nullable=True,
        doc="Token de verificação de email"
    )
    
    verification_token_expires = Column(
        DateTime,
        nullable=True,
        doc="Expiração do token de verificação"
    )
    
    password_reset_token = Column(
        String(255),
        nullable=True,
        doc="Token de reset de senha"
    )
    
    password_reset_expires = Column(
        DateTime,
        nullable=True,
        doc="Expiração do token de reset"
    )
    
    # === CONFIGURAÇÕES PESSOAIS ===
    preferences = Column(
        JSONB,
        default=dict,
        doc="Preferências do usuário"
    )
    
    profile_settings = Column(
        JSONB,
        default=dict,
        doc="Configurações do perfil"
    )
    
    notification_settings = Column(
        JSONB,
        default=dict,
        doc="Configurações de notificação"
    )
    
    # === BIOGRAFIA/NOTAS ===
    bio = Column(
        Text,
        nullable=True,
        doc="Biografia ou descrição do usuário"
    )
    
    notes = Column(
        Text,
        nullable=True,
        doc="Notas administrativas"
    )
    
    # === RELACIONAMENTOS ===
    # Os relacionamentos serão definidos nos modelos específicos
    # para evitar importações circulares
    
    # === ÍNDICES ===
    __table_args__ = (
        Index('ix_users_email_active', 'email', 'is_active'),
        Index('ix_users_role_active', 'role', 'is_active'),
        Index('ix_users_professional_id', 'professional_id'),
        Index('ix_users_last_login', 'last_login'),
    )
    
    # === PROPRIEDADES CALCULADAS ===
    
    @hybrid_property
    def display_name(self) -> str:
        """Nome para exibição"""
        if self.full_name:
            return self.full_name
        return f"{self.first_name} {self.last_name}".strip()
    
    @hybrid_property
    def is_medical_professional(self) -> bool:
        """Verifica se é profissional médico"""
        medical_roles = [UserRole.DOCTOR.value, UserRole.NURSE.value]
        return self.role in medical_roles
    
    @hybrid_property
    def is_admin(self) -> bool:
        """Verifica se é administrador"""
        return self.role == UserRole.ADMIN.value
    
    @hybrid_property
    def is_doctor(self) -> bool:
        """Verifica se é médico"""
        return self.role == UserRole.DOCTOR.value
    
    @hybrid_property
    def is_patient(self) -> bool:
        """Verifica se é paciente"""
        return self.role == UserRole.PATIENT.value
    
    @hybrid_property
    def age(self) -> Optional[int]:
        """Calcula idade baseada na data de nascimento"""
        if self.birth_date:
            today = datetime.now().date()
            birth_date = self.birth_date.date() if isinstance(self.birth_date, datetime) else self.birth_date
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return None
    
    @hybrid_property
    def is_account_locked(self) -> bool:
        """Verifica se a conta está bloqueada"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    # === MÉTODOS DE SENHA ===
    
    def set_password(self, password: str) -> None:
        """
        Define nova senha para o usuário
        
        Args:
            password: Nova senha em texto plano
        """
        self.password_hash = password_manager.get_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verifica se a senha está correta
        
        Args:
            password: Senha em texto plano para verificar
            
        Returns:
            True se a senha estiver correta
        """
        return password_manager.verify_password(password, self.password_hash)
    
    def generate_verification_token(self) -> str:
        """
        Gera token de verificação de email
        
        Returns:
            Token de verificação
        """
        import secrets
        from datetime import timedelta
        
        token = secrets.token_urlsafe(32)
        self.verification_token = token
        self.verification_token_expires = datetime.utcnow() + timedelta(days=1)
        
        return token
    
    def generate_password_reset_token(self) -> str:
        """
        Gera token de reset de senha
        
        Returns:
            Token de reset
        """
        import secrets
        from datetime import timedelta
        
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=2)
        
        return token
    
    def verify_email(self) -> bool:
        """
        Verifica o email do usuário
        
        Returns:
            True se a verificação foi bem-sucedida
        """
        if (self.verification_token and 
            self.verification_token_expires and 
            datetime.utcnow() < self.verification_token_expires):
            
            self.is_verified = True
            self.verification_token = None
            self.verification_token_expires = None
            return True
        
        return False
    
    def reset_password(self, new_password: str, token: str) -> bool:
        """
        Reset de senha usando token
        
        Args:
            new_password: Nova senha
            token: Token de reset
            
        Returns:
            True se o reset foi bem-sucedido
        """
        if (self.password_reset_token == token and 
            self.password_reset_expires and 
            datetime.utcnow() < self.password_reset_expires):
            
            self.set_password(new_password)
            self.password_reset_token = None
            self.password_reset_expires = None
            self.failed_login_attempts = "0"
            self.locked_until = None
            return True
        
        return False
    
    # === MÉTODOS DE ACESSO ===
    
    def record_login(self) -> None:
        """Registra login bem-sucedido"""
        self.last_login = datetime.utcnow()
        self.login_count = str(int(self.login_count or "0") + 1)
        self.failed_login_attempts = "0"
    
    def record_failed_login(self) -> None:
        """Registra tentativa de login falhada"""
        attempts = int(self.failed_login_attempts or "0") + 1
        self.failed_login_attempts = str(attempts)
        
        # Bloquear conta após 5 tentativas falhadas
        if attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def unlock_account(self) -> None:
        """Desbloqueia a conta"""
        self.locked_until = None
        self.failed_login_attempts = "0"
    
    # === MÉTODOS DE PREFERÊNCIAS ===
    
    def get_preference(self, key: str, default=None):
        """Obtém preferência do usuário"""
        if not self.preferences:
            self.preferences = {}
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value):
        """Define preferência do usuário"""
        if not self.preferences:
            self.preferences = {}
        self.preferences[key] = value
    
    def get_notification_setting(self, key: str, default=True):
        """Obtém configuração de notificação"""
        if not self.notification_settings:
            self.notification_settings = {
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True,
                "diagnostic_ready": True,
                "exam_completed": True,
                "appointment_reminder": True
            }
        return self.notification_settings.get(key, default)
    
    def set_notification_setting(self, key: str, value: bool):
        """Define configuração de notificação"""
        if not self.notification_settings:
            self.notification_settings = {}
        self.notification_settings[key] = value
    
    # === MÉTODOS DE VALIDAÇÃO ===
    
    def can_access_patient_data(self, patient_user_id: uuid.UUID) -> bool:
        """
        Verifica se pode acessar dados de paciente
        
        Args:
            patient_user_id: ID do usuário paciente
            
        Returns:
            True se pode acessar
        """
        # Admin pode acessar tudo
        if self.is_admin:
            return True
        
        # Paciente pode acessar seus próprios dados
        if self.is_patient and self.id == patient_user_id:
            return True
        
        # Médicos e enfermeiros podem acessar (com outras validações necessárias)
        if self.is_medical_professional:
            return True
        
        return False
    
    def can_perform_diagnosis(self) -> bool:
        """Verifica se pode realizar diagnósticos"""
        return self.role in [UserRole.DOCTOR.value, UserRole.ADMIN.value]
    
    def can_review_diagnosis(self) -> bool:
        """Verifica se pode revisar diagnósticos"""
        return self.role in [UserRole.DOCTOR.value, UserRole.ADMIN.value]
    
    def can_manage_users(self) -> bool:
        """Verifica se pode gerenciar usuários"""
        return self.is_admin
    
    # === MÉTODOS DE CONSULTA ===
    
    @classmethod
    def get_by_email(cls, db: Session, email: str) -> Optional['User']:
        """
        Busca usuário por email
        
        Args:
            db: Sessão do banco
            email: Email para buscar
            
        Returns:
            Usuário encontrado ou None
        """
        return db.query(cls).filter(
            cls.email == email.lower(),
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_professional_id(cls, db: Session, professional_id: str) -> Optional['User']:
        """
        Busca usuário por registro profissional
        
        Args:
            db: Sessão do banco
            professional_id: Registro profissional
            
        Returns:
            Usuário encontrado ou None
        """
        return db.query(cls).filter(
            cls.professional_id == professional_id,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_role(cls, db: Session, role: UserRole, is_active: bool = True) -> List['User']:
        """
        Busca usuários por role
        
        Args:
            db: Sessão do banco
            role: Role para buscar
            is_active: Filtrar apenas ativos
            
        Returns:
            Lista de usuários
        """
        query = db.query(cls).filter(
            cls.role == role.value,
            cls.is_deleted.is_(False)
        )
        
        if is_active:
            query = query.filter(cls.is_active.is_(True))
        
        return query.all()
    
    @classmethod
    def search_users(cls, db: Session, search_term: str, role: Optional[UserRole] = None) -> List['User']:
        """
        Busca usuários por termo
        
        Args:
            db: Sessão do banco
            search_term: Termo para buscar
            role: Filtrar por role (opcional)
            
        Returns:
            Lista de usuários encontrados
        """
        query = db.query(cls).filter(
            cls.is_deleted.is_(False)
        )
        
        # Buscar em nome, email e registro profissional
        search_filter = (
            cls.first_name.ilike(f"%{search_term}%") |
            cls.last_name.ilike(f"%{search_term}%") |
            cls.full_name.ilike(f"%{search_term}%") |
            cls.email.ilike(f"%{search_term}%") |
            cls.professional_id.ilike(f"%{search_term}%")
        )
        
        query = query.filter(search_filter)
        
        if role:
            query = query.filter(cls.role == role.value)
        
        return query.limit(50).all()
    
    # === MÉTODOS DE LIFECYCLE ===
    
    def __init__(self, **kwargs):
        """Inicialização do usuário"""
        super().__init__(**kwargs)
        
        # Gerar nome completo se não fornecido
        if not self.full_name and self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        
        # Normalizar email
        if self.email:
            self.email = self.email.lower().strip()
        
        # Configurações padrão
        if not self.preferences:
            self.preferences = {
                "language": "pt-BR",
                "timezone": "America/Sao_Paulo",
                "theme": "light"
            }
        
        if not self.notification_settings:
            self.notification_settings = {
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True,
                "diagnostic_ready": True,
                "exam_completed": True,
                "appointment_reminder": True
            }
    
    def before_save(self):
        """Executado antes de salvar"""
        # Atualizar nome completo
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        
        # Normalizar email
        if self.email:
            self.email = self.email.lower().strip()
    
    def to_dict(self, exclude: Optional[List[str]] = None, include_sensitive: bool = False):
        """
        Converte para dicionário com controle de dados sensíveis
        
        Args:
            exclude: Campos para excluir
            include_sensitive: Se deve incluir dados sensíveis
            
        Returns:
            Dicionário com dados do usuário
        """
        exclude = exclude or []
        
        # Sempre excluir dados sensíveis por padrão
        if not include_sensitive:
            exclude.extend([
                'password_hash',
                'verification_token',
                'password_reset_token',
                'failed_login_attempts',
                'locked_until'
            ])
        
        result = super().to_dict(exclude)
        
        # Adicionar propriedades calculadas
        result.update({
            'display_name': self.display_name,
            'age': self.age,
            'is_medical_professional': self.is_medical_professional,
            'is_account_locked': self.is_account_locked
        })
        
        return result