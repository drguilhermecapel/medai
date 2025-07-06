"""
Schemas Pydantic para autenticação
Define modelos de entrada e saída para endpoints de auth
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field

from app.core.constants import UserRole, Gender


# === SCHEMAS DE REQUEST ===

class UserLogin(BaseModel):
    """Schema para login de usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=1, description="Senha do usuário")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "medico@exemplo.com",
                "password": "senha123"
            }
        }


class UserRegister(BaseModel):
    """Schema para registro de usuário"""
    email: EmailStr = Field(..., description="Email único do usuário")
    password: str = Field(..., min_length=8, description="Senha forte (mínimo 8 caracteres)")
    first_name: str = Field(..., min_length=2, max_length=100, description="Primeiro nome")
    last_name: str = Field(..., min_length=2, max_length=100, description="Sobrenome")
    phone: Optional[str] = Field(None, description="Telefone de contato")
    birth_date: Optional[date] = Field(None, description="Data de nascimento")
    gender: Optional[Gender] = Field(None, description="Gênero")
    role: Optional[UserRole] = Field(UserRole.PATIENT, description="Role do usuário")
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validação básica de força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Senha deve conter ao menos uma letra maiúscula, uma minúscula e um número')
        
        return v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        """Validação da data de nascimento"""
        if v and v > date.today():
            raise ValueError('Data de nascimento não pode ser no futuro')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "novo.usuario@exemplo.com",
                "password": "SenhaForte123",
                "first_name": "João",
                "last_name": "Silva",
                "phone": "+5511999999999",
                "birth_date": "1990-01-01",
                "gender": "male",
                "role": "patient"
            }
        }


class PasswordReset(BaseModel):
    """Schema para solicitação de reset de senha"""
    email: EmailStr = Field(..., description="Email do usuário")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@exemplo.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Schema para confirmação de reset de senha"""
    email: EmailStr = Field(..., description="Email do usuário")
    token: str = Field(..., description="Token de reset recebido por email")
    new_password: str = Field(..., min_length=8, description="Nova senha forte")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validação básica de força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Senha deve conter ao menos uma letra maiúscula, uma minúscula e um número')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@exemplo.com",
                "token": "abc123def456",
                "new_password": "NovaSenhaForte123"
            }
        }


class EmailVerification(BaseModel):
    """Schema para verificação de email"""
    email: EmailStr = Field(..., description="Email do usuário")
    token: str = Field(..., description="Token de verificação recebido por email")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@exemplo.com",
                "token": "xyz789abc123"
            }
        }


class RefreshToken(BaseModel):
    """Schema para renovação de token"""
    refresh_token: str = Field(..., description="Token de refresh válido")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordChange(BaseModel):
    """Schema para alteração de senha"""
    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(..., min_length=8, description="Nova senha forte")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validação básica de força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Senha deve conter ao menos uma letra maiúscula, uma minúscula e um número')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "senhaAtual123",
                "new_password": "NovaSenhaForte456"
            }
        }


# === SCHEMAS DE RESPONSE ===

class Token(BaseModel):
    """Schema para resposta de token"""
    access_token: str = Field(..., description="Token de acesso JWT")
    refresh_token: str = Field(..., description="Token de refresh JWT")
    token_type: str = Field("bearer", description="Tipo do token")
    expires_in: Optional[int] = Field(None, description="Tempo de expiração em segundos")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class LoginResponse(BaseModel):
    """Schema para resposta de login completa"""
    access_token: str = Field(..., description="Token de acesso JWT")
    refresh_token: str = Field(..., description="Token de refresh JWT")
    token_type: str = Field("bearer", description="Tipo do token")
    expires_in: Optional[int] = Field(None, description="Tempo de expiração em segundos")
    user: dict = Field(..., description="Dados básicos do usuário")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "usuario@exemplo.com",
                    "first_name": "João",
                    "last_name": "Silva",
                    "role": "patient",
                    "is_active": True,
                    "is_verified": True
                }
            }
        }


class AuthResponse(BaseModel):
    """Schema base para respostas de autenticação"""
    message: str = Field(..., description="Mensagem de resposta")
    success: bool = Field(True, description="Indica se a operação foi bem-sucedida")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Operação realizada com sucesso",
                "success": True
            }
        }


class EmailVerificationResponse(AuthResponse):
    """Schema para resposta de verificação de email"""
    verified: bool = Field(..., description="Indica se o email foi verificado")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Email verificado com sucesso",
                "success": True,
                "verified": True
            }
        }


class PasswordResetResponse(AuthResponse):
    """Schema para resposta de reset de senha"""
    reset_sent: bool = Field(..., description="Indica se o email de reset foi enviado")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Se o email existir, um link de reset foi enviado",
                "success": True,
                "reset_sent": True
            }
        }


# === SCHEMAS DE VALIDAÇÃO ===

class TokenValidation(BaseModel):
    """Schema para validação de token"""
    token: str = Field(..., description="Token para validar")
    token_type: Optional[str] = Field("access", description="Tipo do token (access/refresh)")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "access"
            }
        }


class TokenValidationResponse(BaseModel):
    """Schema para resposta de validação de token"""
    valid: bool = Field(..., description="Indica se o token é válido")
    user_id: Optional[str] = Field(None, description="ID do usuário se token válido")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração do token")
    error: Optional[str] = Field(None, description="Erro se token inválido")
    
    class Config:
        schema_extra = {
            "example": {
                "valid": True,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "expires_at": "2024-01-01T12:00:00Z",
                "error": None
            }
        }


# === SCHEMAS PARA PERMISSÕES ===

class PermissionCheck(BaseModel):
    """Schema para verificação de permissões"""
    permission: str = Field(..., description="Permissão a verificar")
    resource_id: Optional[str] = Field(None, description="ID do recurso (opcional)")
    
    class Config:
        schema_extra = {
            "example": {
                "permission": "read_patient",
                "resource_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class PermissionResponse(BaseModel):
    """Schema para resposta de verificação de permissões"""
    has_permission: bool = Field(..., description="Indica se o usuário tem a permissão")
    permission: str = Field(..., description="Permissão verificada")
    user_role: str = Field(..., description="Role do usuário")
    
    class Config:
        schema_extra = {
            "example": {
                "has_permission": True,
                "permission": "read_patient",
                "user_role": "doctor"
            }
        }