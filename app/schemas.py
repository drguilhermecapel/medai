# -*- coding: utf-8 -*-
"""Schemas Pydantic da API MedAI."""
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# === AUTENTICAÇÃO ===

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    role: str = "user"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    role: str
    created_at: Optional[datetime] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


# === PACIENTES ===

class PatientBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    cpf: str = Field(min_length=11, max_length=14)
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    medical_history: Optional[Dict[str, Any]] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    medical_history: Optional[Dict[str, Any]] = None


class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: Optional[int] = None
    created_at: Optional[datetime] = None


# === EXAMES ===

class ExamBase(BaseModel):
    patient_id: int
    exam_type: str
    exam_date: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    reference_values: Optional[Dict[str, Any]] = None
    status: str = "pending"


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    exam_type: Optional[str] = None
    exam_date: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    reference_values: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ExamResponse(ExamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: Optional[int] = None
    created_at: Optional[datetime] = None


# === DIAGNÓSTICOS ===

class DiagnosticBase(BaseModel):
    patient_id: int
    exam_id: Optional[int] = None
    diagnostic_text: str
    ai_analysis: Optional[Dict[str, Any]] = None
    severity: str = "normal"


class DiagnosticCreate(DiagnosticBase):
    pass


class DiagnosticResponse(DiagnosticBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: Optional[int] = None
    created_at: Optional[datetime] = None


class DiagnosticListResponse(BaseModel):
    items: List[DiagnosticResponse]
    total: int
