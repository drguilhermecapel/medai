"""
Patient schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class PatientBase(BaseModel):
    patient_id: str = Field(..., description="ID único do paciente")
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    medical_record_number: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class Patient(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PatientResponse(Patient):
    pass
