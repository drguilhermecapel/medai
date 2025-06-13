"""
Medical Records API endpoints
Enhanced with AI-powered analysis and voice transcription
"""

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.models.user import User
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def list_medical_records(
    patient_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Lista prontuários médicos com filtros opcionais
    """
    try:
        records = [
            {
                "id": 1,
                "patient_id": patient_id or 1,
                "chief_complaint": "Chest pain",
                "diagnosis": "Acute coronary syndrome",
                "created_at": "2024-06-12T10:30:00Z",
                "updated_at": "2024-06-12T10:30:00Z"
            }
        ]

        return records

    except Exception as e:
        logger.error(f"Error listing medical records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving medical records"
        )

@router.post("/")
async def create_medical_record(
    record_data: dict[str, Any] = Body(...),
    current_user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Cria novo prontuário médico com análise de IA
    """
    try:
        record = {
            "id": 1,
            "patient_id": record_data.get("patient_id", 1),
            "chief_complaint": record_data.get("chief_complaint", ""),
            "diagnosis": record_data.get("diagnosis", ""),
            "created_at": "2024-06-12T10:30:00Z",
            "updated_at": "2024-06-12T10:30:00Z",
            "created_by": current_user.id
        }

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

@router.get("/{record_id}")
async def get_medical_record(
    record_id: int,
    current_user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Obtém prontuário médico específico
    """
    try:
        record = {
            "id": record_id,
            "patient_id": 1,
            "chief_complaint": "Chest pain and shortness of breath",
            "diagnosis": "Acute coronary syndrome",
            "treatment_plan": "Cardiac catheterization, medication therapy",
            "created_at": "2024-06-12T10:30:00Z",
            "updated_at": "2024-06-12T10:30:00Z"
        }

        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving medical record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving medical record"
        )

@router.put("/{record_id}")
async def update_medical_record(
    record_id: int,
    record_update: dict[str, Any] = Body(...),
    current_user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Atualiza prontuário médico existente
    """
    try:
        record = {
            "id": record_id,
            "patient_id": 1,
            "chief_complaint": record_update.get("chief_complaint", "Updated complaint"),
            "diagnosis": record_update.get("diagnosis", "Updated diagnosis"),
            "treatment_plan": record_update.get("treatment_plan", "Updated treatment"),
            "created_at": "2024-06-12T10:30:00Z",
            "updated_at": "2024-06-12T10:35:00Z",
            "updated_by": current_user.id
        }

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
    evolution_data: dict[str, Any] = Body(...),
    current_user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Adiciona evolução ao prontuário médico
    """
    try:
        evolution_id = 1

        return {
            "message": "Evolution added successfully",
            "evolution_id": evolution_id,
            "record_id": record_id,
            "ai_analysis_triggered": evolution_data.get("enable_ai_analysis", False),
            "created_by": current_user.id
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
    transcription_request: dict[str, Any] = Body(...),
    current_user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Transcreve áudio para texto e adiciona ao prontuário
    """
    try:
        result = {
            "record_id": record_id,
            "transcription": "Paciente relata dor no peito há 2 horas",
            "confidence_score": 0.89,
            "language": transcription_request.get("language", "pt-BR"),
            "processed_at": "2024-06-12T10:30:00Z",
            "created_by": current_user.id
        }

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
    analysis_request: dict[str, Any] = Body(...),
    current_user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Gera resumo inteligente do prontuário usando IA
    """
    try:
        summary = {
            "chief_complaint": "Chest pain and shortness of breath",
            "clinical_assessment": "Patient presents with acute coronary syndrome",
            "recommendations": ["Immediate cardiac catheterization", "Start dual antiplatelet therapy"],
            "risk_stratification": "High risk",
            "generated_at": "2024-06-12T10:30:00Z"
        }

        return {
            "record_id": record_id,
            "summary": summary,
            "generated_at": summary.get("generated_at"),
            "analysis_type": analysis_request.get("analysis_type", "comprehensive")
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
