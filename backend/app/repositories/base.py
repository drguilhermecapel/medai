# app/repositories/base.py - NOVO
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Repositório base com operações CRUD comuns"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def create(self, obj: ModelType) -> ModelType:
        """Criar novo objeto"""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Buscar por ID"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, obj: ModelType) -> ModelType:
        """Atualizar objeto"""
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def delete(self, obj: ModelType) -> None:
        """Deletar objeto"""
        await self.db.delete(obj)
        await self.db.commit()
    
    async def list_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[ModelType]:
        """Listar com paginação e filtros"""
        query = select(self.model)
        
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    conditions.append(getattr(self.model, field) == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

# app/repositories/user_repository.py - CORREÇÃO
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Buscar usuário por username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

# app/repositories/patient_repository.py - CORREÇÃO
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.patient import Patient
from app.repositories.base import BaseRepository

class PatientRepository(BaseRepository[Patient]):
    def __init__(self, db: AsyncSession):
        super().__init__(Patient, db)
    
    async def get_by_patient_id(self, patient_id: str) -> Optional[Patient]:
        """Buscar por ID do paciente (código único)"""
        result = await self.db.execute(
            select(Patient).where(Patient.patient_id == patient_id)
        )
        return result.scalar_one_or_none()
    
    async def search(self, query: str, search_fields: List[str]) -> List[Patient]:
        """Buscar pacientes por múltiplos campos"""
        conditions = []
        
        for field in search_fields:
            if hasattr(Patient, field):
                column = getattr(Patient, field)
                conditions.append(column.ilike(f"%{query}%"))
        
        if not conditions:
            return []
        
        result = await self.db.execute(
            select(Patient).where(or_(*conditions))
        )
        return result.scalars().all()

# app/repositories/notification_repository.py - CORREÇÃO
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.notification import Notification
from app.repositories.base import BaseRepository

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)
    
    async def get_user_notifications(
        self, 
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Buscar notificações do usuário"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """Marcar todas notificações como lidas"""
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

# app/repositories/ecg_repository.py - CORREÇÃO
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository

class ECGRepository(BaseRepository[ECGAnalysis]):
    def __init__(self, db: AsyncSession):
        super().__init__(ECGAnalysis, db)
    
    async def get_analysis_by_id(self, analysis_id: int) -> Optional[ECGAnalysis]:
        """Buscar análise com relacionamentos"""
        result = await self.db.execute(
            select(ECGAnalysis)
            .options(
                selectinload(ECGAnalysis.patient),
                selectinload(ECGAnalysis.creator),
                selectinload(ECGAnalysis.validator),
                selectinload(ECGAnalysis.validations)
            )
            .where(ECGAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()
    
    async def get_patient_analyses(
        self, 
        patient_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ECGAnalysis]:
        """Buscar análises de um paciente"""
        result = await self.db.execute(
            select(ECGAnalysis)
            .where(ECGAnalysis.patient_id == patient_id)
            .order_by(ECGAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# app/repositories/validation_repository.py - CORREÇÃO
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.validation import Validation
from app.repositories.base import BaseRepository

class ValidationRepository(BaseRepository[Validation]):
    def __init__(self, db: AsyncSession):
        super().__init__(Validation, db)
    
    async def get_validation_by_id(self, validation_id: int) -> Optional[Validation]:
        """Buscar validação com relacionamentos"""
        result = await self.db.execute(
            select(Validation)
            .options(
                selectinload(Validation.analysis),
                selectinload(Validation.validator)
            )
            .where(Validation.id == validation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_validations(
        self,
        validator_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Validation]:
        """Buscar validações pendentes"""
        query = select(Validation).where(Validation.status == "pending")
        
        if validator_id:
            query = query.where(Validation.validator_id == validator_id)
        
        query = query.order_by(Validation.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()