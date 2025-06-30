"""
Utilitários de segurança para autenticação e autorização
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
import secrets
import string

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

# Configuração do contexto de criptografia de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração do OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def hash_password(password: str) -> str:
    """
    Cria um hash da senha usando bcrypt
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha armazenado
        
    Returns:
        True se a senha corresponde, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração do token
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token de acesso JWT
    
    Args:
        subject: Identificador do usuário (geralmente user_id)
        expires_delta: Tempo de expiração customizado
        
    Returns:
        Token de acesso JWT
    """
    if expires_delta:
        expires = expires_delta
    else:
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return create_token(
        data={"sub": str(subject), "type": "access"},
        expires_delta=expires
    )

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token de refresh JWT
    
    Args:
        subject: Identificador do usuário (geralmente user_id)
        expires_delta: Tempo de expiração customizado
        
    Returns:
        Token de refresh JWT
    """
    if expires_delta:
        expires = expires_delta
    else:
        expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return create_token(
        data={"sub": str(subject), "type": "refresh"},
        expires_delta=expires
    )

def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """
    Verifica e decodifica um token JWT
    
    Args:
        token: Token JWT a ser verificado
        token_type: Tipo do token ("access" ou "refresh")
        
    Returns:
        ID do usuário se o token for válido, None caso contrário
        
    Raises:
        HTTPException: Se o token for inválido
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        token_type_claim: str = payload.get("type")
        
        if user_id is None or token_type_claim != token_type:
            raise credentials_exception
            
        return user_id
        
    except JWTError:
        raise credentials_exception

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtém o usuário atual baseado no token JWT
    
    Args:
        token: Token JWT do header Authorization
        db: Sessão do banco de dados
        
    Returns:
        Objeto User do usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou o usuário não existir
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    
    user_id = verify_token(token, token_type="access")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Obtém o usuário atual ativo
    
    Args:
        current_user: Usuário obtido do token
        
    Returns:
        Usuário se estiver ativo
        
    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_current_user_with_roles(required_roles: list = None):
    """
    Dependency para verificar se o usuário tem os papéis necessários
    
    Args:
        required_roles: Lista de papéis necessários
        
    Returns:
        Função dependency do FastAPI
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if required_roles:
            if current_user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        return current_user
    
    return role_checker

def generate_password(length: int = 12) -> str:
    """
    Gera uma senha aleatória segura
    
    Args:
        length: Comprimento da senha
        
    Returns:
        Senha aleatória
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def generate_api_key() -> str:
    """
    Gera uma chave de API segura
    
    Returns:
        Chave de API no formato: medai_xxxxxxxxxxxxxxxxxxxxx
    """
    key = secrets.token_urlsafe(32)
    return f"medai_{key}"

def is_strong_password(password: str) -> tuple[bool, list[str]]:
    """
    Verifica se a senha atende aos critérios de segurança
    
    Args:
        password: Senha a ser verificada
        
    Returns:
        Tupla (é_forte, lista_de_problemas)
    """
    problems = []
    
    if len(password) < settings.SystemConfig.PASSWORD_MIN_LENGTH:
        problems.append(f"Senha deve ter pelo menos {settings.SystemConfig.PASSWORD_MIN_LENGTH} caracteres")
    
    if not any(c.isupper() for c in password):
        problems.append("Senha deve conter pelo menos uma letra maiúscula")
    
    if not any(c.islower() for c in password):
        problems.append("Senha deve conter pelo menos uma letra minúscula")
    
    if not any(c.isdigit() for c in password):
        problems.append("Senha deve conter pelo menos um número")
    
    if not any(c in string.punctuation for c in password):
        problems.append("Senha deve conter pelo menos um caractere especial")
    
    return len(problems) == 0, problems

def mask_email(email: str) -> str:
    """
    Mascara um endereço de email para exibição
    
    Args:
        email: Email a ser mascarado
        
    Returns:
        Email mascarado (ex: u***r@example.com)
    """
    if '@' not in email:
        return email
    
    local, domain = email.split('@')
    
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"

def mask_cpf(cpf: str) -> str:
    """
    Mascara um CPF para exibição
    
    Args:
        cpf: CPF a ser mascarado
        
    Returns:
        CPF mascarado (ex: 123.***.***-**)
    """
    if len(cpf) != 11:
        return cpf
    
    return f"{cpf[:3]}.***.***.{cpf[-2:]}"

# Alias para compatibilidade
get_password_hash = hash_password
verify_password_hash = verify_password