"""
Sistema de Segurança do MedAI
Gerenciamento de autenticação, autorização e criptografia
"""
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Any, Union, Optional, Dict, List
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from passlib.hash import bcrypt
import re
from functools import wraps

from app.core.config import settings
from app.core.constants import UserRole, ROLE_PERMISSIONS, VALIDATION_RULES
from app.models.user import User


# === CONFIGURAÇÃO DE CRIPTOGRAFIA ===

# Context para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração JWT
JWT_ALGORITHM = settings.ALGORITHM
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
JWT_REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Bearer token security
security = HTTPBearer()


# === CLASSES DE SEGURANÇA ===

class SecurityError(Exception):
    """Exceção base para erros de segurança"""
    pass


class AuthenticationError(SecurityError):
    """Erro de autenticação"""
    pass


class AuthorizationError(SecurityError):
    """Erro de autorização"""
    pass


class TokenExpiredError(SecurityError):
    """Token expirado"""
    pass


class InvalidTokenError(SecurityError):
    """Token inválido"""
    pass


class WeakPasswordError(SecurityError):
    """Senha muito fraca"""
    pass


# === GERENCIAMENTO DE SENHAS ===

class PasswordManager:
    """Gerenciador de senhas e validação"""
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Gera hash da senha usando bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Union[bool, List[str]]]:
        """
        Valida a força da senha
        
        Returns:
            Dict com resultado da validação e lista de erros
        """
        errors = []
        rules = VALIDATION_RULES["password"]
        
        # Verificar comprimento mínimo
        if len(password) < rules["min_length"]:
            errors.append(f"Senha deve ter pelo menos {rules['min_length']} caracteres")
        
        # Verificar comprimento máximo
        if len(password) > rules["max_length"]:
            errors.append(f"Senha deve ter no máximo {rules['max_length']} caracteres")
        
        # Verificar maiúscula
        if rules["require_uppercase"] and not re.search(r"[A-Z]", password):
            errors.append("Senha deve conter pelo menos uma letra maiúscula")
        
        # Verificar minúscula
        if rules["require_lowercase"] and not re.search(r"[a-z]", password):
            errors.append("Senha deve conter pelo menos uma letra minúscula")
        
        # Verificar números
        if rules["require_numbers"] and not re.search(r"\d", password):
            errors.append("Senha deve conter pelo menos um número")
        
        # Verificar caracteres especiais
        if rules["require_special_chars"] and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Senha deve conter pelo menos um caractere especial")
        
        # Verificar padrões comuns fracos
        weak_patterns = [
            r"123456", r"password", r"qwerty", r"abc123",
            r"111111", r"000000", r"admin", r"login"
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                errors.append("Senha contém padrão muito comum")
                break
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        """Gera uma senha segura aleatória"""
        import string
        
        # Garantir pelo menos um de cada tipo
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice("!@#$%^&*")
        ]
        
        # Preencher o resto
        all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Embaralhar
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)


# === GERENCIAMENTO DE TOKENS JWT ===

class TokenManager:
    """Gerenciador de tokens JWT"""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Cria token de acesso JWT
        
        Args:
            data: Dados para incluir no token
            expires_delta: Tempo de expiração customizado
            
        Returns:
            Token JWT como string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Cria token de refresh JWT
        
        Args:
            data: Dados para incluir no token
            
        Returns:
            Token JWT como string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decodifica token JWT
        
        Args:
            token: Token JWT para decodificar
            
        Returns:
            Payload do token decodificado
            
        Raises:
            InvalidTokenError: Token inválido
            TokenExpiredError: Token expirado
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token expirado")
        except jwt.JWTError:
            raise InvalidTokenError("Token inválido")
    
    @staticmethod
    def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
        """
        Verifica se o token é do tipo esperado
        
        Args:
            payload: Payload do token
            expected_type: Tipo esperado ("access" ou "refresh")
            
        Returns:
            True se o tipo estiver correto
        """
        return payload.get("type") == expected_type
    
    @staticmethod
    def extract_user_id(payload: Dict[str, Any]) -> str:
        """
        Extrai ID do usuário do payload
        
        Args:
            payload: Payload do token
            
        Returns:
            ID do usuário
            
        Raises:
            InvalidTokenError: Se não conseguir extrair o ID
        """
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Token não contém ID do usuário")
        return user_id


# === AUTORIZAÇÃO E CONTROLE DE ACESSO ===

class AuthorizationManager:
    """Gerenciador de autorização e controle de acesso"""
    
    @staticmethod
    def check_permission(user_role: UserRole, required_permission: str) -> bool:
        """
        Verifica se o usuário tem a permissão necessária
        
        Args:
            user_role: Role do usuário
            required_permission: Permissão necessária
            
        Returns:
            True se o usuário tem a permissão
        """
        user_permissions = ROLE_PERMISSIONS.get(user_role, [])
        return required_permission in user_permissions
    
    @staticmethod
    def check_resource_access(
        user_id: str, 
        user_role: UserRole, 
        resource_owner_id: str, 
        required_permission: str
    ) -> bool:
        """
        Verifica acesso a recurso específico
        
        Args:
            user_id: ID do usuário solicitante
            user_role: Role do usuário
            resource_owner_id: ID do dono do recurso
            required_permission: Permissão necessária
            
        Returns:
            True se o acesso for permitido
        """
        # Admin tem acesso total
        if user_role == UserRole.ADMIN:
            return True
        
        # Verificar permissão geral
        if not AuthorizationManager.check_permission(user_role, required_permission):
            return False
        
        # Se é recurso próprio e tem permissão de "own"
        if user_id == resource_owner_id and "own" in required_permission:
            return True
        
        # Verificar permissões específicas por role
        if user_role in [UserRole.DOCTOR, UserRole.NURSE]:
            return True
        
        return False


# === DEPENDÊNCIAS FASTAPI ===

async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Extrai e valida token do usuário atual
    
    Returns:
        Payload do token decodificado
        
    Raises:
        HTTPException: Se o token for inválido
    """
    try:
        token = credentials.credentials
        payload = TokenManager.decode_token(token)
        
        if not TokenManager.verify_token_type(payload, "access"):
            raise InvalidTokenError("Tipo de token inválido")
        
        return payload
        
    except (TokenExpiredError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
) -> str:
    """
    Obtém ID do usuário atual do token
    
    Returns:
        ID do usuário
    """
    try:
        return TokenManager.extract_user_id(token_payload)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


def require_permission(permission: str):
    """
    Decorator para exigir permissão específica
    
    Args:
        permission: Permissão necessária
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair usuário dos argumentos
            user_role = kwargs.get('current_user_role')
            
            if not user_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Role do usuário não fornecido"
                )
            
            if not AuthorizationManager.check_permission(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão necessária: {permission}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(*allowed_roles: UserRole):
    """
    Decorator para exigir role específico
    
    Args:
        allowed_roles: Roles permitidos
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_role = kwargs.get('current_user_role')
            
            if not user_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Role do usuário não fornecido"
                )
            
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Roles permitidos: {[role.value for role in allowed_roles]}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# === UTILITÁRIOS DE SEGURANÇA ===

class SecurityUtils:
    """Utilitários de segurança diversos"""
    
    @staticmethod
    def generate_api_key() -> str:
        """Gera chave de API segura"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Gera token CSRF"""
        return secrets.token_hex(32)
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitiza entrada do usuário
        
        Args:
            input_str: String para sanitizar
            
        Returns:
            String sanitizada
        """
        # Remover caracteres perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\n', '\r', '\t']
        
        for char in dangerous_chars:
            input_str = input_str.replace(char, '')
        
        return input_str.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida formato de email
        
        Args:
            email: Email para validar
            
        Returns:
            True se o email for válido
        """
        pattern = VALIDATION_RULES["email"]["pattern"]
        return bool(re.match(pattern, email))
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
        """
        Mascara dados sensíveis para logs
        
        Args:
            data: Dados para mascarar
            mask_char: Caractere para usar na máscara
            
        Returns:
            Dados mascarados
        """
        if len(data) <= 4:
            return mask_char * len(data)
        
        return data[:2] + mask_char * (len(data) - 4) + data[-2:]


# === INSTÂNCIAS GLOBAIS ===

# Managers globais
password_manager = PasswordManager()
token_manager = TokenManager()
auth_manager = AuthorizationManager()
security_utils = SecurityUtils()


# === FUNÇÕES DE CONVENIÊNCIA ===

def create_user_token(user: User) -> Dict[str, str]:
    """
    Cria tokens para usuário
    
    Args:
        user: Usuário para criar tokens
        
    Returns:
        Dict com access_token e refresh_token
    """
    # Dados para incluir no token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active
    }
    
    access_token = token_manager.create_access_token(token_data)
    refresh_token = token_manager.create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def verify_password_and_get_user(email: str, password: str, user_repository) -> Optional[User]:
    """
    Verifica senha e retorna usuário se válido
    
    Args:
        email: Email do usuário
        password: Senha fornecida
        user_repository: Repositório de usuários
        
    Returns:
        Usuário se credenciais válidas, None caso contrário
    """
    user = user_repository.get_by_email(email)
    
    if not user:
        return None
    
    if not password_manager.verify_password(password, user.password_hash):
        return None
    
    if not user.is_active:
        return None
    
    return user


# === CONSTANTES DE SEGURANÇA ===

# Headers de segurança recomendados
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# Configurações de rate limiting por endpoint
RATE_LIMIT_CONFIGS = {
    "/api/v1/auth/login": {"requests": 5, "window": 900},  # 5 por 15 min
    "/api/v1/auth/register": {"requests": 3, "window": 3600},  # 3 por hora
    "/api/v1/auth/reset-password": {"requests": 2, "window": 3600},  # 2 por hora
    "default": {"requests": 100, "window": 3600}  # 100 por hora
}