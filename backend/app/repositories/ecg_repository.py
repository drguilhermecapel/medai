# app/repositories/ecg_repository.py - CORREÇÃO COMPLETA
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.ecg_analysis import ECGAnalysis
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
    
    async def delete_analysis(self, analysis_id: int) -> bool:
        """Deletar análise"""
        analysis = await self.get(analysis_id)
        if not analysis:
            return False
        await self.delete(analysis)
        return True