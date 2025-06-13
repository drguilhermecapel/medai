"""
Medical Guidelines API endpoints - Endpoints para sistema de diretrizes médicas
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.exam_request_service import ExamRequestService
from app.services.medical_guidelines_engine import (
    MotorDiretrizesMedicasIA,
    ValidadorConformidadeDiretrizes,
)

router = APIRouter()


@router.post("/validate-prescription")
async def validate_prescription_guidelines(
    prescription_data: dict[str, Any],
    diagnosis: str,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Valida prescrição contra diretrizes médicas"""
    try:
        validator = ValidadorConformidadeDiretrizes()
        result = await validator.validar_acao_medica(
            acao=prescription_data,
            tipo_acao="prescricao",
            diagnostico=diagnosis
        )
        return {"success": True, "validation_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/suggest-exams")
async def suggest_exams_by_diagnosis(
    diagnosis: str,
    clinical_context: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Sugere exames baseados em diretrizes para um diagnóstico"""
    try:
        exam_service = ExamRequestService(db)
        suggestions = await exam_service.get_exam_suggestions_by_diagnosis(
            diagnosis=diagnosis,
            clinical_context=clinical_context or {}
        )
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/create-exam-request")
async def create_exam_request_with_guidelines(
    patient_id: str,
    requesting_physician_id: int,
    primary_diagnosis: str,
    clinical_context: dict[str, Any],
    custom_exams: list[dict[str, Any]] | None = None,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Cria solicitação de exames baseada em diretrizes"""
    try:
        exam_service = ExamRequestService(db)
        request = await exam_service.create_exam_request(
            patient_id=patient_id,
            requesting_physician_id=requesting_physician_id,
            primary_diagnosis=primary_diagnosis,
            clinical_context=clinical_context,
            custom_exams=custom_exams
        )
        return {"success": True, "exam_request": request}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/guidelines/{condition}")
async def get_guidelines_for_condition(
    condition: str,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Obtém diretrizes para uma condição específica"""
    try:
        guidelines_engine = MotorDiretrizesMedicasIA()
        guideline = await guidelines_engine.obter_diretriz_para_condicao(
            condicao=condition,
            contexto_paciente={}
        )

        if guideline:
            return {
                "success": True,
                "guideline": {
                    "id": guideline.id,
                    "titulo": guideline.titulo,
                    "especialidade": guideline.especialidade,
                    "fonte": guideline.fonte.value,
                    "versao": guideline.versao,
                    "nivel_evidencia": guideline.nivel_evidencia,
                    "conteudo": guideline.conteudo
                }
            }
        else:
            return {"success": False, "message": f"Nenhuma diretriz encontrada para {condition}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/validate-exam-appropriateness")
async def validate_exam_appropriateness(
    exam_name: str,
    diagnosis: str,
    clinical_context: dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Valida apropriação de um exame específico"""
    try:
        exam_service = ExamRequestService(db)
        validation = await exam_service.validate_exam_appropriateness(
            exam_name=exam_name,
            diagnosis=diagnosis,
            clinical_context=clinical_context
        )
        return {"success": True, "validation": validation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
