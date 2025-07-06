"""
Schemas Pydantic para usuários
Define modelos de entrada e saída para endpoints de usuários
"""
import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, validator, Field

from app.core.constants import UserRole, Gender


# === SCHEMAS BASE ===

class UserBase(BaseModel):
    """Schema base para usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    first_name: str = Field(..., min_length=2, max_length=100, description="Primeiro nome")
    last_name: str = Field(..., min_length=2, max_length=100, description="Sobrenome")
    phone: Optional[str] = Field(None, description="Telefone de contato")
    birth_date: Optional[date] = Field(None, description="Data de nascimento")
    gender: Optional[Gender] = Field(None, description="Gênero")


# === SCHEMAS DE REQUEST ===

class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=8, description="Senha forte")
    role: UserRole = Field(UserRole.PATIENT, description="Role do usuário")
    professional_id: Optional[str] = Field(None, description="Registro profissional (CRM, COREN, etc.)")
    specialization: Optional[str] = Field(None, description="Especialização médica")
    institution: Optional[str] = Field(None, description="Instituição onde trabalha")
    department: Optional[str] = Field(None, description="Departamento/setor")
    bio: Optional[str] = Field(None, description="Biografia ou descrição")
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validação de força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Senha deve conter ao menos uma letra maiúscula, uma minúscula e um número')
        
        return v
    
    @validator('professional_id')
    def validate_professional_id(cls, v, values):
        """Validar registro profissional para roles médicos"""
        role = values.get('role')
        if role in [UserRole.DOCTOR, UserRole.NURSE] and not v:
            raise ValueError(f'Registro profissional é obrigatório para {role.value}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "dr.silva@hospital.com",
                "password": "SenhaForte123",
                "first_name": "João",
                "last_name": "Silva",
                "phone": "+5511999999999",
                "birth_date": "1980-05-15",
                "gender": "male",
                "role": "doctor",
                "professional_id": "CRM12345",
                "specialization": "Cardiologia",
                "institution": "Hospital São Paulo",
                "department": "Cardiologia"
            }
        }


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None)
    birth_date: Optional[date] = Field(None)
    gender: Optional[Gender] = Field(None)
    professional_id: Optional[str] = Field(None)
    specialization: Optional[str] = Field(None)
    institution: Optional[str] = Field(None)
    department: Optional[str] = Field(None)
    bio: Optional[str] = Field(None)
    preferences: Optional[Dict[str, Any]] = Field(None)
    notification_settings: Optional[Dict[str, Any]] = Field(None)
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "João Carlos",
                "phone": "+5511888888888",
                "specialization": "Cardiologia Intervencionista",
                "bio": "Cardiologista com 15 anos de experiência",
                "preferences": {
                    "language": "pt-BR",
                    "theme": "dark"
                }
            }
        }


class UserSearch(BaseModel):
    """Schema para busca de usuários"""
    search_term: str = Field(..., min_length=2, description="Termo para buscar")
    role: Optional[UserRole] = Field(None, description="Filtrar por role")
    specialization: Optional[str] = Field(None, description="Filtrar por especialização")
    institution: Optional[str] = Field(None, description="Filtrar por instituição")
    active_only: bool = Field(True, description="Incluir apenas usuários ativos")
    limit: int = Field(50, ge=1, le=100, description="Limite de resultados")
    
    class Config:
        schema_extra = {
            "example": {
                "search_term": "Silva",
                "role": "doctor",
                "specialization": "Cardiologia",
                "limit": 20
            }
        }


# === SCHEMAS DE RESPONSE ===

class UserResponse(BaseModel):
    """Schema para resposta básica de usuário"""
    id: uuid.UUID = Field(..., description="ID único do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    first_name: str = Field(..., description="Primeiro nome")
    last_name: str = Field(..., description="Sobrenome")
    full_name: Optional[str] = Field(None, description="Nome completo")
    role: UserRole = Field(..., description="Role do usuário")
    is_active: bool = Field(..., description="Usuário ativo")
    is_verified: bool = Field(..., description="Email verificado")
    created_at: datetime = Field(..., description="Data de criação")
    last_login: Optional[datetime] = Field(None, description="Último login")
    
    # Propriedades calculadas
    display_name: Optional[str] = Field(None, description="Nome para exibição")
    is_medical_professional: Optional[bool] = Field(None, description="É profissional médico")
    age: Optional[int] = Field(None, description="Idade calculada")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "dr.silva@hospital.com",
                "first_name": "João",
                "last_name": "Silva",
                "full_name": "João Silva",
                "role": "doctor",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T10:00:00Z",
                "last_login": "2024-01-15T08:30:00Z",
                "display_name": "Dr. João Silva",
                "is_medical_professional": True,
                "age": 35
            }
        }


class UserDetailResponse(UserResponse):
    """Schema para resposta detalhada de usuário"""
    phone: Optional[str] = Field(None, description="Telefone")
    birth_date: Optional[date] = Field(None, description="Data de nascimento")
    gender: Optional[Gender] = Field(None, description="Gênero")
    professional_id: Optional[str] = Field(None, description="Registro profissional")
    specialization: Optional[str] = Field(None, description="Especialização")
    institution: Optional[str] = Field(None, description="Instituição")
    department: Optional[str] = Field(None, description="Departamento")
    bio: Optional[str] = Field(None, description="Biografia")
    login_count: Optional[str] = Field(None, description="Contador de logins")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Preferências")
    notification_settings: Optional[Dict[str, Any]] = Field(None, description="Configurações de notificação")
    updated_at: Optional[datetime] = Field(None, description="Última atualização")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "dr.silva@hospital.com",
                "first_name": "João",
                "last_name": "Silva",
                "phone": "+5511999999999",
                "birth_date": "1980-05-15",
                "gender": "male",
                "role": "doctor",
                "professional_id": "CRM12345",
                "specialization": "Cardiologia",
                "institution": "Hospital São Paulo",
                "department": "Cardiologia",
                "bio": "Cardiologista experiente",
                "is_active": True,
                "is_verified": True,
                "login_count": "47",
                "preferences": {
                    "language": "pt-BR",
                    "theme": "light"
                },
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-15T14:20:00Z"
            }
        }


class UserProfileResponse(UserDetailResponse):
    """Schema para resposta de perfil completo"""
    is_premium: Optional[bool] = Field(None, description="Usuário premium")
    failed_login_attempts: Optional[str] = Field(None, description="Tentativas de login falhadas")
    is_account_locked: Optional[bool] = Field(None, description="Conta bloqueada")
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema para resposta de lista de usuários"""
    users: List[UserResponse] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de usuários")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Usuários por página")
    has_next: bool = Field(..., description="Tem próxima página")
    has_prev: bool = Field(..., description="Tem página anterior")
    
    class Config:
        schema_extra = {
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "dr.silva@hospital.com",
                        "first_name": "João",
                        "last_name": "Silva",
                        "role": "doctor",
                        "is_active": True,
                        "is_verified": True,
                        "created_at": "2024-01-01T10:00:00Z"
                    }
                ],
                "total": 150,
                "page": 1,
                "per_page": 20,
                "has_next": True,
                "has_prev": False
            }
        }


# === SCHEMAS DE ESTATÍSTICAS ===

class UserStats(BaseModel):
    """Schema para estatísticas de usuários"""
    total_users: int = Field(..., description="Total de usuários")
    active_users: int = Field(..., description="Usuários ativos")
    inactive_users: int = Field(..., description="Usuários inativos")
    verified_users: int = Field(..., description="Usuários verificados")
    recent_logins: int = Field(..., description="Logins recentes (30 dias)")
    
    # Por role
    admin_users: int = Field(..., description="Administradores")
    doctor_users: int = Field(..., description="Médicos")
    nurse_users: int = Field(..., description="Enfermeiros")
    technician_users: int = Field(..., description="Técnicos")
    patient_users: int = Field(..., description="Pacientes")
    viewer_users: int = Field(..., description="Visualizadores")
    
    class Config:
        schema_extra = {
            "example": {
                "total_users": 1250,
                "active_users": 1180,
                "inactive_users": 70,
                "verified_users": 1200,
                "recent_logins": 450,
                "admin_users": 5,
                "doctor_users": 85,
                "nurse_users": 120,
                "technician_users": 40,
                "patient_users": 980,
                "viewer_users": 20
            }
        }


# === SCHEMAS DE AÇÕES ===

class UserActivation(BaseModel):
    """Schema para ativação/desativação de usuário"""
    is_active: bool = Field(..., description="Ativar ou desativar usuário")
    reason: Optional[str] = Field(None, description="Motivo da ação")
    
    class Config:
        schema_extra = {
            "example": {
                "is_active": False,
                "reason": "Usuário solicitou desativação da conta"
            }
        }


class UserRoleUpdate(BaseModel):
    """Schema para atualização de role"""
    role: UserRole = Field(..., description="Nova role do usuário")
    reason: Optional[str] = Field(None, description="Motivo da alteração")
    
    class Config:
        schema_extra = {
            "example": {
                "role": "doctor",
                "reason": "Usuário completou formação médica"
            }
        }


# === SCHEMAS DE PREFERÊNCIAS ===

class UserPreferences(BaseModel):
    """Schema para preferências do usuário"""
    language: Optional[str] = Field("pt-BR", description="Idioma preferido")
    timezone: Optional[str] = Field("America/Sao_Paulo", description="Fuso horário")
    theme: Optional[str] = Field("light", description="Tema da interface (light/dark)")
    date_format: Optional[str] = Field("DD/MM/YYYY", description="Formato de data")
    time_format: Optional[str] = Field("24h", description="Formato de hora (12h/24h)")
    
    class Config:
        schema_extra = {
            "example": {
                "language": "pt-BR",
                "timezone": "America/Sao_Paulo",
                "theme": "dark",
                "date_format": "DD/MM/YYYY",
                "time_format": "24h"
            }
        }


class NotificationSettings(BaseModel):
    """Schema para configurações de notificação"""
    email_notifications: bool = Field(True, description="Notificações por email")
    sms_notifications: bool = Field(False, description="Notificações por SMS")
    push_notifications: bool = Field(True, description="Notificações push")
    diagnostic_ready: bool = Field(True, description="Diagnóstico pronto")
    exam_completed: bool = Field(True, description="Exame concluído")
    appointment_reminder: bool = Field(True, description="Lembrete de consulta")
    system_alerts: bool = Field(True, description="Alertas do sistema")
    
    class Config:
        schema_extra = {
            "example": {
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True,
                "diagnostic_ready": True,
                "exam_completed": True,
                "appointment_reminder": True,
                "system_alerts": False
            }
        }