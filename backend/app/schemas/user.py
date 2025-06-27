# app/schemas/user.py - CORREÇÃO
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., regex="^(physician|cardiologist|technician|admin)$")
    license_number: Optional[str] = None
    specialization: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserResponse(User):
    pass

# app/schemas/patient.py - CORREÇÃO
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class PatientBase(BaseModel):
    patient_id: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(..., regex="^(male|female|other)$")
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None

class Patient(PatientBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PatientResponse(Patient):
    full_name: str
    age: int
    
    @validator('full_name', always=True)
    def compute_full_name(cls, v, values):
        return f"{values.get('first_name', '')} {values.get('last_name', '')}"
    
    @validator('age', always=True)
    def compute_age(cls, v, values):
        if 'date_of_birth' in values:
            today = date.today()
            dob = values['date_of_birth']
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None

# app/schemas/ecg_analysis.py - CORREÇÃO
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ECGAnalysisBase(BaseModel):
    patient_id: int
    acquisition_date: datetime
    sample_rate: int = Field(..., gt=0)
    duration_seconds: float = Field(..., gt=0)
    leads_count: int = Field(..., ge=1, le=12)
    leads_names: List[str]

class ECGAnalysisCreate(ECGAnalysisBase):
    file_path: str
    original_filename: str

class ECGAnalysisUpdate(BaseModel):
    status: Optional[str] = None
    analysis_results: Optional[Dict[str, Any]] = None
    ai_predictions: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    interpretation: Optional[str] = None
    clinical_notes: Optional[str] = None

class ECGAnalysis(ECGAnalysisBase):
    id: int
    created_by: int
    file_path: str
    original_filename: str
    status: str
    analysis_results: Optional[Dict[str, Any]] = None
    ai_predictions: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    interpretation: Optional[str] = None
    clinical_notes: Optional[str] = None
    validated_by: Optional[int] = None
    validated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ECGAnalysisResponse(ECGAnalysis):
    patient_name: Optional[str] = None
    creator_name: Optional[str] = None
    validator_name: Optional[str] = None

# app/schemas/notification.py - CORREÇÃO
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str
    notification_type: str = Field(..., regex="^(info|warning|error|success|critical)$")
    priority: str = Field(default="normal", regex="^(low|normal|high|critical)$")

class NotificationCreate(NotificationBase):
    user_id: int
    related_id: Optional[int] = None
    related_type: Optional[str] = None

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NotificationResponse(Notification):
    pass

# app/schemas/validation.py - CORREÇÃO
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ValidationBase(BaseModel):
    analysis_id: int
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")

class ValidationCreate(ValidationBase):
    validator_id: int
    status: str = Field(default="pending", regex="^(pending|approved|rejected|requires_review)$")

class ValidationSubmit(BaseModel):
    status: str = Field(..., regex="^(approved|rejected|requires_review)$")
    comments: Optional[str] = None
    corrections: Optional[str] = None
    requires_senior_review: bool = False

class Validation(ValidationBase):
    id: int
    validator_id: int
    status: str
    comments: Optional[str] = None
    corrections: Optional[str] = None
    is_urgent: bool
    requires_senior_review: bool
    created_at: datetime
    validated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ValidationResponse(Validation):
    validator_name: Optional[str] = None
    analysis_patient_name: Optional[str] = None