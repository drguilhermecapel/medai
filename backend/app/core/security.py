"""
Módulo de segurança do MedAI
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AuthenticationError, TokenError
from app.repositories.user_repository import UserRepository
from app.models.user import User


# Configuração do contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_password_hash(password: str) -> str:
    """
    Gera hash de senha usando bcrypt
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha
        
    Returns:
        True se a senha está correta
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: int,
    additional_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria token de acesso JWT
    
    Args:
        user_id: ID do usuário
        additional_claims: Claims adicionais para incluir no token
        expires_delta: Tempo de expiração customizado
        
    Returns:
        Token JWT
    """
    to_encode = {
        "sub": str(user_id),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria token de refresh JWT
    
    Args:
        user_id: ID do usuário
        expires_delta: Tempo de expiração customizado
        
    Returns:
        Token JWT de refresh
    """
    to_encode = {
        "sub": str(user_id),
        "type": "refresh"
    }
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica e valida token JWT
    
    Args:
        token: Token JWT
        
    Returns:
        Payload do token
        
    Raises:
        TokenError: Se o token for inválido ou expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenError("Token expired")
    except JWTError as e:
        raise TokenError(f"Invalid token: {str(e)}")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtém usuário atual a partir do token
    
    Args:
        token: Token de acesso
        db: Sessão do banco de dados
        
    Returns:
        Usuário autenticado
        
    Raises:
        AuthenticationError: Se não conseguir autenticar
    """
    credentials_exception = AuthenticationError(
        detail="Could not validate credentials"
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except TokenError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = user_repo.get(int(user_id))
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise AuthenticationError(detail="Inactive user")
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Garante que o usuário está ativo
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Usuário ativo
        
    Raises:
        HTTPException: Se o usuário não estiver ativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def create_password_reset_token(user_id: int) -> str:
    """
    Cria token para reset de senha
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Token para reset de senha
    """
    expires = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "sub": str(user_id),
        "type": "password_reset",
        "exp": expires
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_email_verification_token(user_id: int, email: str) -> str:
    """
    Cria token para verificação de email
    
    Args:
        user_id: ID do usuário
        email: Email a ser verificado
        
    Returns:
        Token para verificação de email
    """
    expires = datetime.utcnow() + timedelta(hours=48)
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "email_verification",
        "exp": expires
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_token_type(token: str, expected_type: str) -> Dict[str, Any]:
    """
    Verifica se o token é do tipo esperado
    
    Args:
        token: Token JWT
        expected_type: Tipo esperado do token
        
    Returns:
        Payload do token se válido
        
    Raises:
        TokenError: Se o token não for do tipo esperado
    """
    payload = decode_token(token)
    
    if payload.get("type") != expected_type:
        raise TokenError(f"Invalid token type. Expected {expected_type}")
        
    return payload


def check_password_strength(password: str) -> Dict[str, Any]:
    """
    Verifica a força da senha
    
    Args:
        password: Senha a ser verificada
        
    Returns:
        Dicionário com informações sobre a força da senha
    """
    issues = []
    score = 0
    
    # Comprimento
    if len(password) >= 8:
        score += 1
    else:
        issues.append("Password must be at least 8 characters long")
    
    # Letra maiúscula
    if any(c.isupper() for c in password):
        score += 1
    else:
        issues.append("Password must contain at least one uppercase letter")
    
    # Letra minúscula
    if any(c.islower() for c in password):
        score += 1
    else:
        issues.append("Password must contain at least one lowercase letter")
    
    # Número
    if any(c.isdigit() for c in password):
        score += 1
    else:
        issues.append("Password must contain at least one number")
    
    # Caractere especial
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        score += 1
    else:
        issues.append("Password must contain at least one special character")
    
    # Classificação
    if score == 5:
        strength = "strong"
    elif score >= 3:
        strength = "medium"
    else:
        strength = "weak"
    
    return {
        "score": score,
        "strength": strength,
        "issues": issues,
        "valid": len(issues) == 0
    }


def generate_api_key() -> str:
    """
    Gera uma chave de API aleatória
    
    Returns:
        Chave de API
    """
    import secrets
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Gera hash de chave de API
    
    Args:
        api_key: Chave de API em texto plano
        
    Returns:
        Hash da chave de API
    """
    import hashlib
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verifica se a chave de API corresponde ao hash
    
    Args:
        api_key: Chave de API em texto plano
        hashed_key: Hash da chave de API
        
    Returns:
        True se a chave está correta
    """
    return hash_api_key(api_key) == hashed_key