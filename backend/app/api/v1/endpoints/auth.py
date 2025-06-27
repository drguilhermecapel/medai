# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.database import get_db
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint"""
    service = UserService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token():
    """Refresh token endpoint"""
    # Implementar lógica de refresh token
    return {"message": "Token refreshed"}

@router.post("/logout")
async def logout():
    """Logout endpoint"""
    # Implementar lógica de logout se necessário
    return {"message": "Logged out successfully"}

# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=User)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    service = UserService(db)
    try:
        return await service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID"""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# app/api/v1/endpoints/patients.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.schemas.patient import Patient, PatientCreate, PatientUpdate
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("", response_model=Patient)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from auth
):
    """Create a new patient"""
    service = PatientService(db)
    return await service.create_patient(patient_data, current_user_id)

@router.get("/{patient_id}", response_model=Patient)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get patient by ID"""
    service = PatientService(db)
    patient = await service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("", response_model=List[Patient])
async def search_patients(
    q: Optional[str] = Query(None, description="Search query"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Search patients"""
    service = PatientService(db)
    if q:
        return await service.search_patients(q)
    return await service.list_patients(skip=skip, limit=limit)

# app/api/v1/endpoints/ecg_analysis.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.ecg_analysis import ECGAnalysis, ECGAnalysisCreate
from app.services.ecg_service import ECGAnalysisService

router = APIRouter(prefix="/ecg", tags=["ecg_analysis"])

@router.post("/upload", response_model=ECGAnalysis)
async def upload_ecg(
    patient_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from auth
):
    """Upload ECG file for analysis"""
    # Implementar upload e processamento
    return {"message": "ECG uploaded"}

@router.get("/analysis/{analysis_id}", response_model=ECGAnalysis)
async def get_ecg_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get ECG analysis by ID"""
    service = ECGAnalysisService(db)
    analysis = await service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

# app/api/v1/endpoints/validations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.validation import Validation, ValidationCreate, ValidationSubmit

router = APIRouter(prefix="/validations", tags=["validations"])

@router.post("", response_model=Validation)
async def create_validation(
    validation_data: ValidationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create validation request"""
    # Implementar
    return {"message": "Validation created"}

@router.get("/pending", response_model=List[Validation])
async def get_pending_validations(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from auth
):
    """Get pending validations"""
    # Implementar
    return []

# app/api/v1/endpoints/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.notification import Notification, NotificationCreate
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[Notification])
async def get_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from auth
):
    """Get user notifications"""
    service = NotificationService(db)
    return await service.get_user_notifications(
        current_user_id,
        unread_only=unread_only
    )

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from auth
):
    """Mark notification as read"""
    service = NotificationService(db)
    result = await service.mark_as_read(notification_id, current_user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}