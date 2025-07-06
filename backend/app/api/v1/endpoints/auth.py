"""
Endpoints de autenticação do MedAI
Gerencia login, registro, reset de senha e verificação de email
"""
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_user_token, get_current_user
from app.core.exceptions import (
    AuthenticationError, ValidationError, DuplicateError,
    InvalidCredentialsError, WeakPasswordError
)
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.auth import (
    Token, UserLogin, UserRegister, PasswordReset,
    PasswordResetConfirm, EmailVerification, RefreshToken
)
from app.schemas.user import UserResponse
from app.services.notification_service import NotificationService
from app.utils.logging_config import get_security_logger
from app.core.constants import UserRole

router = APIRouter()
security_logger = get_security_logger()


@router.post("/login", response_model=Token, summary="Login de usuário")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, Any]:
    """
    Autentica usuário e retorna tokens de acesso
    
    - **username**: Email do usuário
    - **password**: Senha do usuário
    
    Returns:
        Tokens de acesso e refresh
    """
    user_repo = UserRepository(db)
    
    try:
        # Autenticar usuário
        user = user_repo.authenticate(form_data.username, form_data.password)
        
        if not user:
            raise InvalidCredentialsError()
        
        # Criar tokens
        tokens = create_user_token(user)
        
        security_logger.log_security_event(
            level=20,  # INFO
            event="api_login_success",
            user_id=str(user.id),
            extra={'email': user.email, 'endpoint': '/auth/login'}
        )
        
        return {
            **tokens,
            "user": UserResponse.from_orm(user).dict()
        }
        
    except Exception as e:
        security_logger.log_security_event(
            level=30,  # WARNING
            event="api_login_failed",
            extra={'email': form_data.username, 'error': str(e), 'endpoint': '/auth/login'}
        )
        
        if isinstance(e, AuthenticationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.post("/register", response_model=UserResponse, summary="Registro de usuário")
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> User:
    """
    Registra novo usuário no sistema
    
    - **email**: Email único do usuário
    - **password**: Senha forte (mínimo 8 caracteres)
    - **first_name**: Primeiro nome
    - **last_name**: Sobrenome
    - **role**: Role do usuário (opcional, padrão: patient)
    """
    user_repo = UserRepository(db)
    notification_service = NotificationService(db)
    
    try:
        # Criar usuário
        user = user_repo.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role or UserRole.PATIENT,
            phone=user_data.phone,
            birth_date=user_data.birth_date,
            gender=user_data.gender
        )
        
        # Enviar email de verificação
        if user.verification_token:
            notification_service.send_email_verification(user)
        
        security_logger.log_security_event(
            level=20,  # INFO
            event="user_registered",
            user_id=str(user.id),
            extra={'email': user.email, 'role': user.role, 'endpoint': '/auth/register'}
        )
        
        return user
        
    except DuplicateError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já está cadastrado"
        )
    except WeakPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Senha não atende aos requisitos de segurança",
                "requirements": e.details.get("field_errors", {}).get("password", [])
            }
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        security_logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.post("/refresh", response_model=Token, summary="Renovar tokens")
def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Renova tokens de acesso usando refresh token
    
    - **refresh_token**: Token de refresh válido
    """
    from app.core.security import token_manager
    
    try:
        # Decodificar refresh token
        payload = token_manager.decode_token(refresh_data.refresh_token)
        
        if not token_manager.verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido"
            )
        
        # Buscar usuário
        user_id = token_manager.extract_user_id(payload)
        user_repo = UserRepository(db)
        user = user_repo.get_or_404(user_id)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        # Criar novos tokens
        tokens = create_user_token(user)
        
        security_logger.log_security_event(
            level=20,  # INFO
            event="token_refreshed",
            user_id=str(user.id),
            extra={'endpoint': '/auth/refresh'}
        )
        
        return tokens
        
    except Exception as e:
        security_logger.log_security_event(
            level=30,  # WARNING
            event="token_refresh_failed",
            extra={'error': str(e), 'endpoint': '/auth/refresh'}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh inválido"
        )


@router.post("/password-reset", summary="Solicitar reset de senha")
def request_password_reset(
    email_data: Dict[str, str] = Body(..., example={"email": "user@example.com"}),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Solicita reset de senha via email
    
    - **email**: Email do usuário
    """
    user_repo = UserRepository(db)
    notification_service = NotificationService(db)
    
    email = email_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email é obrigatório"
        )
    
    try:
        # Tentar reset (sempre retorna sucesso por segurança)
        reset_token = user_repo.reset_password(email)
        
        if reset_token:
            # Buscar usuário para enviar email
            user = user_repo.get_by_email(email)
            if user:
                notification_service.send_password_reset(user, reset_token)
        
        security_logger.log_security_event(
            level=20,  # INFO
            event="password_reset_requested",
            extra={'email': email, 'endpoint': '/auth/password-reset'}
        )
        
        return {"message": "Se o email existir, um link de reset foi enviado"}
        
    except Exception as e:
        security_logger.error(f"Password reset request error: {e}")
        # Sempre retornar sucesso por segurança
        return {"message": "Se o email existir, um link de reset foi enviado"}


@router.post("/password-reset/confirm", summary="Confirmar reset de senha")
def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Confirma reset de senha com token
    
    - **email**: Email do usuário
    - **token**: Token de reset recebido por email
    - **new_password**: Nova senha forte
    """
    user_repo = UserRepository(db)
    
    try:
        success = user_repo.confirm_password_reset(
            reset_data.email,
            reset_data.token,
            reset_data.new_password
        )
        
        if success:
            security_logger.log_security_event(
                level=20,  # INFO
                event="password_reset_completed",
                extra={'email': reset_data.email, 'endpoint': '/auth/password-reset/confirm'}
            )
            return {"message": "Senha alterada com sucesso"}
        else:
            security_logger.log_security_event(
                level=30,  # WARNING
                event="password_reset_failed",
                extra={'email': reset_data.email, 'endpoint': '/auth/password-reset/confirm'}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou expirado"
            )
            
    except WeakPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Senha não atende aos requisitos de segurança",
                "requirements": e.details.get("field_errors", {}).get("password", [])
            }
        )
    except Exception as e:
        security_logger.error(f"Password reset confirm error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.post("/verify-email", summary="Verificar email")
def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Verifica email do usuário
    
    - **email**: Email do usuário
    - **token**: Token de verificação recebido por email
    """
    user_repo = UserRepository(db)
    
    try:
        success = user_repo.verify_email(verification_data.email, verification_data.token)
        
        if success:
            security_logger.log_security_event(
                level=20,  # INFO
                event="email_verified",
                extra={'email': verification_data.email, 'endpoint': '/auth/verify-email'}
            )
            return {"message": "Email verificado com sucesso"}
        else:
            security_logger.log_security_event(
                level=30,  # WARNING
                event="email_verification_failed",
                extra={'email': verification_data.email, 'endpoint': '/auth/verify-email'}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de verificação inválido ou expirado"
            )
            
    except Exception as e:
        security_logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.post("/verify-email/resend", summary="Reenviar verificação de email")
def resend_email_verification(
    email_data: Dict[str, str] = Body(..., example={"email": "user@example.com"}),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Reenvia email de verificação
    
    - **email**: Email do usuário
    """
    user_repo = UserRepository(db)
    notification_service = NotificationService(db)
    
    email = email_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email é obrigatório"
        )
    
    try:
        token = user_repo.resend_verification(email)
        
        if token:
            user = user_repo.get_by_email(email)
            if user:
                notification_service.send_email_verification(user)
                
            security_logger.log_security_event(
                level=20,  # INFO
                event="email_verification_resent",
                extra={'email': email, 'endpoint': '/auth/verify-email/resend'}
            )
        
        # Sempre retornar sucesso por segurança
        return {"message": "Se o email existir e não estiver verificado, um novo token foi enviado"}
        
    except Exception as e:
        security_logger.error(f"Resend verification error: {e}")
        # Sempre retornar sucesso por segurança
        return {"message": "Se o email existir e não estiver verificado, um novo token foi enviado"}


@router.get("/me", response_model=UserResponse, summary="Dados do usuário atual")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Retorna informações do usuário autenticado
    
    Requer autenticação via Bearer token
    """
    return current_user


@router.post("/logout", summary="Logout")
def logout(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Realiza logout do usuário
    
    Nota: Em uma implementação completa, seria necessário invalidar o token
    no lado do servidor (blacklist de tokens)
    """
    security_logger.log_security_event(
        level=20,  # INFO
        event="user_logout",
        user_id=str(current_user.id),
        extra={'email': current_user.email, 'endpoint': '/auth/logout'}
    )
    
    return {"message": "Logout realizado com sucesso"}


@router.post("/change-password", summary="Alterar senha")
def change_password(
    password_data: Dict[str, str] = Body(..., example={
        "current_password": "senha_atual",
        "new_password": "nova_senha_forte"
    }),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Altera senha do usuário autenticado
    
    - **current_password**: Senha atual
    - **new_password**: Nova senha forte
    """
    user_repo = UserRepository(db)
    
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Senha atual e nova senha são obrigatórias"
        )
    
    try:
        success = user_repo.change_password(
            current_user.id,
            current_password,
            new_password
        )
        
        if success:
            security_logger.log_security_event(
                level=20,  # INFO
                event="password_changed_via_api",
                user_id=str(current_user.id),
                extra={'endpoint': '/auth/change-password'}
            )
            return {"message": "Senha alterada com sucesso"}
            
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except WeakPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Nova senha não atende aos requisitos de segurança",
                "requirements": e.details.get("field_errors", {}).get("password", [])
            }
        )
    except Exception as e:
        security_logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )