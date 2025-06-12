"""
Medical Records API endpoints
Enhanced with AI-powered analysis and voice transcription
"""

import logging
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.medical_record import (
    MedicalRecordCreate, MedicalRecordResponse, MedicalRecordUpdate,
    EvolutionCreate, VoiceTranscriptionRequest, AIAnalysisRequest
)
from app.services.medical_record_service import MedicalRecordService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[MedicalRecordResponse])
async def list_medical_records(
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Lista prontuários médicos com filtros opcionais
    """
    try:
        service = MedicalRecordService(db)
        
        if patient_id:
            records = await service.get_patient_records(
                patient_id=patient_id,
                skip=skip,
                limit=limit,
                user_id=current_user.id
            )
        else:
            records = await service.get_all_records(
                skip=skip,
                limit=limit,
                user_id=current_user.id
            )
        
        return records
        
    except Exception as e:
        logger.error(f"Error listing medical records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving medical records"
        )

@router.post("/", response_model=MedicalRecordResponse)
async def create_medical_record(
    record_data: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Cria novo prontuário médico com análise de IA
    """
    try:
        service = MedicalRecordService(db)
        
        record = await service.create_record(
            record_data=record_data,
            created_by=current_user.id
        )
        
        if record_data.enable_ai_analysis:
            await service.trigger_ai_analysis(
                record_id=record.id,
                analysis_type="comprehensive"
            )
        
        return record
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.error(f"Error creating medical record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating medical record"
        )

@router.get("/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtém prontuário médico específico
    """
    try:
        service = MedicalRecordService(db)
        record = await service.get_record(record_id, current_user.id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving medical record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving medical record"
        )

@router.put("/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: int,
    record_update: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Atualiza prontuário médico existente
    """
    try:
        service = MedicalRecordService(db)
        
        record = await service.update_record(
            record_id=record_id,
            record_update=record_update,
            updated_by=current_user.id
        )
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating medical record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating medical record"
        )

@router.post("/{record_id}/evolutions")
async def add_evolution(
    record_id: int,
    evolution_data: EvolutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Adiciona evolução ao prontuário médico
    """
    try:
        service = MedicalRecordService(db)
        
        evolution = await service.add_evolution(
            record_id=record_id,
            evolution_data=evolution_data,
            created_by=current_user.id
        )
        
        if evolution_data.enable_ai_analysis:
            await service.analyze_evolution(
                evolution_id=evolution.id,
                analysis_type="clinical_assessment"
            )
        
        return {
            "message": "Evolution added successfully",
            "evolution_id": evolution.id,
            "ai_analysis_triggered": evolution_data.enable_ai_analysis
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.error(f"Error adding evolution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding evolution"
        )

@router.post("/{record_id}/transcribe-voice")
async def transcribe_voice(
    record_id: int,
    transcription_request: VoiceTranscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Transcreve áudio para texto e adiciona ao prontuário
    """
    try:
        service = MedicalRecordService(db)
        
        result = await service.transcribe_voice_to_record(
            record_id=record_id,
            audio_data=transcription_request.audio_data,
            audio_format=transcription_request.audio_format,
            language=transcription_request.language,
            created_by=current_user.id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.error(f"Error transcribing voice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error transcribing voice"
        )

@router.post("/{record_id}/ai-summary")
async def get_ai_summary(
    record_id: int,
    analysis_request: AIAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Gera resumo inteligente do prontuário usando IA
    """
    try:
        service = MedicalRecordService(db)
        
        summary = await service.generate_ai_summary(
            record_id=record_id,
            analysis_type=analysis_request.analysis_type,
            include_recommendations=analysis_request.include_recommendations,
            user_id=current_user.id
        )
        
        return {
            "record_id": record_id,
            "summary": summary,
            "generated_at": summary.get("generated_at"),
            "analysis_type": analysis_request.analysis_type
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.error(f"Error generating AI summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating AI summary"
        )
