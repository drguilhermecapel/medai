# app/services/patient_service.py - CORREÇÃO
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.repositories.patient_repository import PatientRepository

class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PatientRepository(db)
    
    async def create_patient(self, patient_data: PatientCreate, created_by: int) -> Patient:
        """Criar novo paciente"""
        patient = Patient(
            **patient_data.dict(),
            created_by=created_by
        )
        return await self.repository.create(patient)
    
    async def get_patient(self, patient_id: int) -> Optional[Patient]:
        """Buscar paciente por ID"""
        return await self.repository.get(patient_id)
    
    async def update_patient(self, patient_id: int, patient_data: PatientUpdate) -> Optional[Patient]:
        """Atualizar dados do paciente"""
        patient = await self.repository.get(patient_id)
        if not patient:
            return None
        
        update_data = patient_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        return await self.repository.update(patient)
    
    async def search_patients(
        self, 
        query: str, 
        search_fields: List[str] = None
    ) -> List[Patient]:
        """Buscar pacientes por nome, ID ou email"""
        if search_fields is None:
            search_fields = ["first_name", "last_name", "patient_id", "email"]
        
        return await self.repository.search(query, search_fields)
    
    async def list_patients(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[Patient]:
        """Listar pacientes com paginação"""
        return await self.repository.list_all(skip=skip, limit=limit, filters=filters)

# app/services/user_service.py - CORREÇÃO
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Criar novo usuário"""
        # Verificar se email já existe
        existing_user = await self.repository.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash da senha
        hashed_password = get_password_hash(user_data.password)
        
        # Criar usuário
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            license_number=user_data.license_number,
            specialization=user_data.specialization
        )
        
        return await self.repository.create(user)
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Buscar usuário por ID"""
        return await self.repository.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        return await self.repository.get_user_by_email(email)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Atualizar dados do usuário"""
        user = await self.repository.get(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        return await self.repository.update(user)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autenticar usuário"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

# app/services/notification_service.py - CORREÇÃO
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.repositories.notification_repository import NotificationRepository

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = NotificationRepository(db)
    
    async def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Criar nova notificação"""
        notification = Notification(**notification_data.dict())
        return await self.repository.create(notification)
    
    async def get_user_notifications(
        self, 
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Buscar notificações do usuário"""
        return await self.repository.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit
        )
    
    async def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """Marcar notificação como lida"""
        notification = await self.repository.get(notification_id)
        
        if not notification or notification.user_id != user_id:
            return None
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        return await self.repository.update(notification)
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """Marcar todas as notificações como lidas"""
        return await self.repository.mark_all_as_read(user_id)

# app/services/ecg_service.py - CORREÇÃO
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

class ECGAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ECGRepository(db)
    
    async def create_analysis(
        self,
        patient_id: int,
        file_path: str,
        original_filename: str,
        created_by: int,
        metadata: Dict[str, Any]
    ) -> ECGAnalysis:
        """Criar nova análise de ECG"""
        try:
            # Verificar se arquivo existe
            if not os.path.exists(file_path):
                raise ECGProcessingException(f"File not found: {file_path}")
            
            # Criar análise
            analysis = ECGAnalysis(
                patient_id=patient_id,
                file_path=file_path,
                original_filename=original_filename,
                created_by=created_by,
                acquisition_date=metadata.get('acquisition_date', datetime.utcnow()),
                sample_rate=metadata['sample_rate'],
                duration_seconds=metadata['duration_seconds'],
                leads_count=metadata['leads_count'],
                leads_names=metadata['leads_names'],
                status=AnalysisStatus.PENDING
            )
            
            return await self.repository.create(analysis)
            
        except Exception as e:
            raise ECGProcessingException(f"Failed to create analysis: {str(e)}")
    
    async def get_analysis(self, analysis_id: int) -> Optional[ECGAnalysis]:
        """Buscar análise por ID"""
        return await self.repository.get_analysis_by_id(analysis_id)
    
    async def update_analysis(
        self,
        analysis_id: int,
        update_data: ECGAnalysisUpdate
    ) -> Optional[ECGAnalysis]:
        """Atualizar análise"""
        analysis = await self.repository.get_analysis_by_id(analysis_id)
        if not analysis:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(analysis, field, value)
        
        analysis.updated_at = datetime.utcnow()
        return await self.repository.update(analysis)
    
    async def delete_analysis(self, analysis_id: int) -> bool:
        """Deletar análise"""
        analysis = await self.repository.get_analysis_by_id(analysis_id)
        if not analysis:
            return False
        
        # Deletar arquivo se existir
        if os.path.exists(analysis.file_path):
            os.remove(analysis.file_path)
        
        await self.repository.delete(analysis)
        return True