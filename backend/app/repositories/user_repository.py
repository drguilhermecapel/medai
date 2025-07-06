"""
Repositório para gerenciamento de usuários
Implementa operações específicas para o modelo User
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from datetime import datetime, timedelta

from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.core.constants import UserRole
from app.core.exceptions import NotFoundError, DuplicateError
from app.core.security import password_manager
from app.utils.logging_config import get_security_logger


class UserRepository(BaseRepository[User]):
    """Repositório para operações específicas de usuários"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
        self.security_logger = get_security_logger()
    
    # === MÉTODOS DE AUTENTICAÇÃO ===
    
    def get_by_email(self, email: str, include_inactive: bool = False) -> Optional[User]:
        """
        Busca usuário por email
        
        Args:
            email: Email do usuário
            include_inactive: Se deve incluir usuários inativos
            
        Returns:
            Usuário encontrado ou None
        """
        query = self.db.query(self.model).filter(
            self.model.email == email.lower().strip(),
            self.model.is_deleted.is_(False)
        )
        
        if not include_inactive:
            query = query.filter(self.model.is_active.is_(True))
        
        return query.first()
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Autentica usuário com email e senha
        
        Args:
            email: Email do usuário
            password: Senha em texto plano
            
        Returns:
            Usuário autenticado ou None se credenciais inválidas
        """
        user = self.get_by_email(email, include_inactive=True)
        
        if not user:
            self.security_logger.log_security_event(
                level=30,  # WARNING
                event="login_attempt_user_not_found",
                user_id=None,
                extra={'email': email}
            )
            return None
        
        # Verificar se conta está bloqueada
        if user.is_account_locked:
            self.security_logger.log_security_event(
                level=30,  # WARNING
                event="login_attempt_account_locked",
                user_id=str(user.id),
                extra={'email': email}
            )
            return None
        
        # Verificar senha
        if not password_manager.verify_password(password, user.password_hash):
            # Registrar tentativa falhada
            user.record_failed_login()
            self.db.add(user)
            self.db.commit()
            
            self.security_logger.log_security_event(
                level=30,  # WARNING
                event="login_attempt_wrong_password",
                user_id=str(user.id),
                extra={'email': email, 'failed_attempts': user.failed_login_attempts}
            )
            return None
        
        # Verificar se usuário está ativo
        if not user.is_active:
            self.security_logger.log_security_event(
                level=30,  # WARNING
                event="login_attempt_inactive_user",
                user_id=str(user.id),
                extra={'email': email}
            )
            return None
        
        # Login bem-sucedido
        user.record_login()
        self.db.add(user)
        self.db.commit()
        
        self.security_logger.log_security_event(
            level=20,  # INFO
            event="login_successful",
            user_id=str(user.id),
            extra={'email': email}
        )
        
        return user
    
    def create_user(
        self, 
        email: str, 
        password: str, 
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.PATIENT,
        **kwargs
    ) -> User:
        """
        Cria novo usuário
        
        Args:
            email: Email do usuário
            password: Senha em texto plano
            first_name: Primeiro nome
            last_name: Sobrenome
            role: Role do usuário
            **kwargs: Dados adicionais
            
        Returns:
            Usuário criado
            
        Raises:
            DuplicateError: Email já existe
        """
        # Verificar se email já existe
        existing_user = self.get_by_email(email, include_inactive=True)
        if existing_user:
            raise DuplicateError("User", "email", email)
        
        # Validar força da senha
        password_validation = password_manager.validate_password_strength(password)
        if not password_validation["is_valid"]:
            from app.core.exceptions import WeakPasswordError
            raise WeakPasswordError(password_validation["errors"])
        
        # Criar usuário
        user_data = {
            "email": email.lower().strip(),
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "role": role.value,
            "is_active": True,
            "is_verified": False,
            **kwargs
        }
        
        user = User(**user_data)
        user.set_password(password)
        
        # Gerar token de verificação se necessário
        if not kwargs.get('is_verified', False):
            user.generate_verification_token()
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        self.security_logger.log_security_event(
            level=20,  # INFO
            event="user_created",
            user_id=str(user.id),
            extra={'email': email, 'role': role.value}
        )
        
        return user
    
    def change_password(
        self, 
        user_id: uuid.UUID, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Altera senha do usuário
        
        Args:
            user_id: ID do usuário
            current_password: Senha atual
            new_password: Nova senha
            
        Returns:
            True se alterada com sucesso
            
        Raises:
            NotFoundError: Usuário não encontrado
            ValidationError: Senha atual incorreta ou nova senha fraca
        """
        user = self.get_or_404(user_id)
        
        # Verificar senha atual
        if not password_manager.verify_password(current_password, user.password_hash):
            self.security_logger.log_security_event(
                level=30,  # WARNING
                event="password_change_wrong_current",
                user_id=str(user_id)
            )
            from app.core.exceptions import ValidationError
            raise ValidationError("Senha atual incorreta")
        
        # Validar nova senha
        password_validation = password_manager.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            from app.core.exceptions import WeakPasswordError
            raise WeakPasswordError(password_validation["errors"])
        
        # Alterar senha
        user.set_password(new_password)
        user.failed_login_attempts = "0"  # Reset tentativas falhadas
        user.locked_until = None  # Desbloquear se estava bloqueado
        
        self.db.add(user)
        self.db.commit()
        
        self.security_logger.log_security_event(
            level=20,  # INFO
            event="password_changed",
            user_id=str(user_id)
        )
        
        return True
    
    def reset_password(self, email: str) -> Optional[str]:
        """
        Inicia processo de reset de senha
        
        Args:
            email: Email do usuário
            
        Returns:
            Token de reset se usuário encontrado, None caso contrário
        """
        user = self.get_by_email(email, include_inactive=True)
        
        if not user:
            # Por segurança, não revelar se email existe
            self.security_logger.log_security_event(
                level=20,  # INFO
                event="password_reset_request_unknown_email",
                extra={'email': email}
            )
            return None
        
        # Gerar token de reset
        reset_token = user.generate_password_reset_token()
        
        self.db.add(user)
        self.db.commit()
        
        self.security_logger.log_security_event(
            level=20,  # INFO
            event="password_reset_token_generated",
            user_id=str(user.id),
            extra={'email': email}
        )
        
        return reset_token
    
    def confirm_password_reset(
        self, 
        email: str, 
        token: str, 
        new_password: str
    ) -> bool:
        """
        Confirma reset de senha com token
        
        Args:
            email: Email do usuário
            token: Token de reset
            new_password: Nova senha
            
        Returns:
            True se reset foi bem-sucedido
        """
        user = self.get_by_email(email, include_inactive=True)
        
        if not user:
            self.security_logger.log_security_event(
                level=30,  # WARNING
                event="password_reset_confirm_unknown_email",
                extra={'email': email}
            )
            return False
        
        # Validar nova senha
        password_validation = password_manager.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            from app.core.exceptions import WeakPasswordError
            raise WeakPasswordError(password_validation["errors"])
        
        # Confirmar reset
        if user.reset_password(new_password, token):
            self.db.add(user)
            self.db.commit()
            
            self.security_logger.log_security_event(
                level=20,  # INFO
                event="password_reset_completed",
                user_id=str(user.id),
                extra={'email': email}
            )
            
            return True
        else:
            self.security_logger.log_security_event(
                level=30,  # WARNING
                event="password_reset_invalid_token",
                user_id=str(user.id),
                extra={'email': email}
            )
            
            return False
    
    # === MÉTODOS DE VERIFICAÇÃO ===
    
    def verify_email(self, email: str, token: str) -> bool:
        """
        Verifica email do usuário
        
        Args:
            email: Email do usuário
            token: Token de verificação
            
        Returns:
            True se verificação foi bem-sucedida
        """
        user = self.get_by_email(email, include_inactive=True)
        
        if not user:
            return False
        
        if user.verification_token == token and user.verify_email():
            self.db.add(user)
            self.db.commit()
            
            self.security_logger.log_security_event(
                level=20,  # INFO
                event="email_verified",
                user_id=str(user.id),
                extra={'email': email}
            )
            
            return True
        
        return False
    
    def resend_verification(self, email: str) -> Optional[str]:
        """
        Reenvia token de verificação
        
        Args:
            email: Email do usuário
            
        Returns:
            Novo token de verificação ou None
        """
        user = self.get_by_email(email, include_inactive=True)
        
        if not user or user.is_verified:
            return None
        
        token = user.generate_verification_token()
        
        self.db.add(user)
        self.db.commit()
        
        return token
    
    # === MÉTODOS DE CONSULTA ESPECÍFICOS ===
    
    def get_by_role(self, role: UserRole, active_only: bool = True) -> List[User]:
        """
        Busca usuários por role
        
        Args:
            role: Role para filtrar
            active_only: Se deve incluir apenas usuários ativos
            
        Returns:
            Lista de usuários
        """
        query = self.db.query(self.model).filter(
            self.model.role == role.value,
            self.model.is_deleted.is_(False)
        )
        
        if active_only:
            query = query.filter(self.model.is_active.is_(True))
        
        return query.order_by(self.model.first_name, self.model.last_name).all()
    
    def get_by_professional_id(self, professional_id: str) -> Optional[User]:
        """
        Busca usuário por registro profissional
        
        Args:
            professional_id: Registro profissional (CRM, COREN, etc.)
            
        Returns:
            Usuário encontrado ou None
        """
        return self.db.query(self.model).filter(
            self.model.professional_id == professional_id,
            self.model.is_deleted.is_(False),
            self.model.is_active.is_(True)
        ).first()
    
    def search_users(
        self, 
        search_term: str, 
        role: Optional[UserRole] = None,
        limit: int = 50
    ) -> List[User]:
        """
        Busca usuários por termo
        
        Args:
            search_term: Termo para buscar
            role: Filtrar por role (opcional)
            limit: Limite de resultados
            
        Returns:
            Lista de usuários encontrados
        """
        query = self.db.query(self.model).filter(
            self.model.is_deleted.is_(False),
            self.model.is_active.is_(True)
        )
        
        # Buscar em múltiplos campos
        search_filter = or_(
            self.model.first_name.ilike(f"%{search_term}%"),
            self.model.last_name.ilike(f"%{search_term}%"),
            self.model.full_name.ilike(f"%{search_term}%"),
            self.model.email.ilike(f"%{search_term}%"),
            self.model.professional_id.ilike(f"%{search_term}%")
        )
        
        query = query.filter(search_filter)
        
        if role:
            query = query.filter(self.model.role == role.value)
        
        return query.limit(limit).all()
    
    def get_medical_professionals(self, specialization: str = None) -> List[User]:
        """
        Busca profissionais médicos
        
        Args:
            specialization: Filtrar por especialização (opcional)
            
        Returns:
            Lista de profissionais médicos
        """
        medical_roles = [UserRole.DOCTOR.value, UserRole.NURSE.value]
        
        query = self.db.query(self.model).filter(
            self.model.role.in_(medical_roles),
            self.model.is_deleted.is_(False),
            self.model.is_active.is_(True)
        )
        
        if specialization:
            query = query.filter(
                self.model.specialization.ilike(f"%{specialization}%")
            )
        
        return query.order_by(self.model.specialization, self.model.first_name).all()
    
    def get_recent_logins(self, days: int = 30) -> List[User]:
        """
        Busca usuários com login recente
        
        Args:
            days: Número de dias para considerar
            
        Returns:
            Lista de usuários com login recente
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(self.model).filter(
            self.model.last_login >= cutoff_date,
            self.model.is_deleted.is_(False)
        ).order_by(self.model.last_login.desc()).all()
    
    def get_inactive_users(self, days: int = 90) -> List[User]:
        """
        Busca usuários inativos
        
        Args:
            days: Número de dias sem login para considerar inativo
            
        Returns:
            Lista de usuários inativos
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(self.model).filter(
            or_(
                self.model.last_login < cutoff_date,
                self.model.last_login.is_(None)
            ),
            self.model.is_deleted.is_(False),
            self.model.is_active.is_(True)
        ).order_by(self.model.last_login.asc()).all()
    
    # === MÉTODOS DE GESTÃO ===
    
    def activate_user(self, user_id: uuid.UUID) -> User:
        """
        Ativa usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Usuário ativado
        """
        user = self.get_or_404(user_id)
        user.is_active = True
        user.locked_until = None
        user.failed_login_attempts = "0"
        
        self.db.add(user)
        self.db.commit()
        
        self.security_logger.log_security_event(
            level=20,  # INFO
            event="user_activated",
            user_id=str(user_id)
        )
        
        return user
    
    def deactivate_user(self, user_id: uuid.UUID, reason: str = None) -> User:
        """
        Desativa usuário
        
        Args:
            user_id: ID do usuário
            reason: Motivo da desativação
            
        Returns:
            Usuário desativado
        """
        user = self.get_or_404(user_id)
        user.is_active = False
        
        if reason:
            user.notes = f"Desativado: {reason}"
        
        self.db.add(user)
        self.db.commit()
        
        self.security_logger.log_security_event(
            level=20,  # INFO
            event="user_deactivated",
            user_id=str(user_id),
            extra={'reason': reason}
        )
        
        return user
    
    def unlock_user(self, user_id: uuid.UUID) -> User:
        """
        Desbloqueia usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Usuário desbloqueado
        """
        user = self.get_or_404(user_id)
        user.unlock_account()
        
        self.db.add(user)
        self.db.commit()
        
        self.security_logger.log_security_event(
            level=20,  # INFO
            event="user_unlocked",
            user_id=str(user_id)
        )
        
        return user
    
    # === MÉTODOS DE ESTATÍSTICAS ===
    
    def get_user_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de usuários
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {}
        
        # Total de usuários
        stats['total_users'] = self.count()
        
        # Usuários por role
        for role in UserRole:
            count = self.db.query(func.count(self.model.id)).filter(
                self.model.role == role.value,
                self.model.is_deleted.is_(False)
            ).scalar()
            stats[f'{role.value}_users'] = count
        
        # Usuários ativos/inativos
        stats['active_users'] = self.db.query(func.count(self.model.id)).filter(
            self.model.is_active.is_(True),
            self.model.is_deleted.is_(False)
        ).scalar()
        
        stats['inactive_users'] = self.db.query(func.count(self.model.id)).filter(
            self.model.is_active.is_(False),
            self.model.is_deleted.is_(False)
        ).scalar()
        
        # Usuários verificados
        stats['verified_users'] = self.db.query(func.count(self.model.id)).filter(
            self.model.is_verified.is_(True),
            self.model.is_deleted.is_(False)
        ).scalar()
        
        # Logins recentes (últimos 30 dias)
        recent_cutoff = datetime.utcnow() - timedelta(days=30)
        stats['recent_logins'] = self.db.query(func.count(self.model.id)).filter(
            self.model.last_login >= recent_cutoff,
            self.model.is_deleted.is_(False)
        ).scalar()
        
        return stats