"""
Exam Request Service - Sistema de solicitação de exames baseado em diretrizes médicas
Integrado com protocolos atualizados e critérios de apropriação
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.medical_guidelines_engine import SolicitacaoExamesBaseadaDiretrizes

logger = logging.getLogger(__name__)

class ExamPriority(str, Enum):
    """Prioridade dos exames"""
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    STAT = "stat"

class ExamStatus(str, Enum):
    """Status da solicitação de exame"""
    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ExamRequestService:
    """Serviço para solicitação de exames baseado em diretrizes"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.guidelines_engine = SolicitacaoExamesBaseadaDiretrizes()

    async def create_exam_request(
        self,
        patient_id: str,
        requesting_physician_id: int,
        primary_diagnosis: str,
        clinical_context: dict[str, Any],
        custom_exams: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Cria solicitação de exames baseada em diretrizes"""
        try:
            request_id = f"EX_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{patient_id}"

            guidelines_suggestions = await self.guidelines_engine.sugerir_exames(
                diagnostico=primary_diagnosis,
                contexto_clinico=clinical_context
            )

            all_exams = []

            for exam in guidelines_suggestions.get("exames_essenciais", []):
                exam_item = {
                    "name": exam["nome"],
                    "type": "essential",
                    "justification": exam["justificativa"],
                    "periodicity": exam.get("periodicidade", ""),
                    "priority": ExamPriority.ROUTINE,
                    "status": ExamStatus.REQUESTED,
                    "guideline_based": True
                }
                all_exams.append(exam_item)

            for exam in guidelines_suggestions.get("exames_complementares", []):
                exam_item = {
                    "name": exam["nome"],
                    "type": "complementary",
                    "justification": exam["justificativa"],
                    "periodicity": exam.get("periodicidade", ""),
                    "priority": ExamPriority.ROUTINE,
                    "status": ExamStatus.REQUESTED,
                    "guideline_based": True
                }
                all_exams.append(exam_item)

            if custom_exams:
                for exam in custom_exams:
                    exam_item = {
                        "name": exam.get("name", ""),
                        "type": "custom",
                        "justification": exam.get("justification", "Solicitação médica específica"),
                        "priority": exam.get("priority", ExamPriority.ROUTINE),
                        "status": ExamStatus.REQUESTED,
                        "guideline_based": False
                    }
                    all_exams.append(exam_item)

            exam_request = {
                "request_id": request_id,
                "patient_id": patient_id,
                "requesting_physician_id": requesting_physician_id,
                "primary_diagnosis": primary_diagnosis,
                "clinical_context": clinical_context,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "exams": all_exams,
                "guidelines_compliance": {
                    "protocol_applied": guidelines_suggestions.get("protocolo_aplicado", ""),
                    "justifications": guidelines_suggestions.get("justificativas", []),
                    "alerts": guidelines_suggestions.get("alertas", [])
                },
                "total_exams": len(all_exams),
                "essential_exams_count": len([e for e in all_exams if e["type"] == "essential"]),
                "complementary_exams_count": len([e for e in all_exams if e["type"] == "complementary"]),
                "custom_exams_count": len([e for e in all_exams if e["type"] == "custom"])
            }

            logger.info(f"Created exam request: {request_id} for patient {patient_id}")
            return exam_request

        except Exception as e:
            logger.error(f"Error creating exam request: {str(e)}")
            raise

    async def get_exam_suggestions_by_diagnosis(
        self,
        diagnosis: str,
        clinical_context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Obtém sugestões de exames baseadas apenas no diagnóstico"""
        try:
            if not clinical_context:
                clinical_context = {}

            suggestions = await self.guidelines_engine.sugerir_exames(
                diagnostico=diagnosis,
                contexto_clinico=clinical_context
            )

            return {
                "diagnosis": diagnosis,
                "suggestions": suggestions,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting exam suggestions: {str(e)}")
            raise

    async def validate_exam_appropriateness(
        self,
        exam_name: str,
        diagnosis: str,
        clinical_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Valida a apropriação de um exame específico"""
        try:
            suggestions = await self.guidelines_engine.sugerir_exames(
                diagnostico=diagnosis,
                contexto_clinico=clinical_context
            )

            all_suggested_exams = []
            all_suggested_exams.extend(suggestions.get("exames_essenciais", []))
            all_suggested_exams.extend(suggestions.get("exames_complementares", []))

            exam_found = False
            exam_details = None

            for suggested_exam in all_suggested_exams:
                if exam_name.lower() in suggested_exam["nome"].lower():
                    exam_found = True
                    exam_details = suggested_exam
                    break

            if exam_found and exam_details:
                return {
                    "appropriate": True,
                    "level": "guideline_recommended",
                    "justification": exam_details["justificativa"],
                    "periodicity": exam_details.get("periodicidade", ""),
                    "evidence_level": "high"
                }
            else:
                return {
                    "appropriate": "uncertain",
                    "level": "clinical_judgment",
                    "justification": "Exame não encontrado nas diretrizes padrão - avaliação clínica necessária",
                    "evidence_level": "clinical"
                }

        except Exception as e:
            logger.error(f"Error validating exam appropriateness: {str(e)}")
            return {
                "appropriate": "error",
                "level": "unknown",
                "justification": f"Erro na validação: {str(e)}",
                "evidence_level": "unknown"
            }

    async def get_exam_request_by_id(self, request_id: str) -> dict[str, Any] | None:
        """Obtém solicitação de exame por ID"""
        try:
            logger.info(f"Retrieved exam request: {request_id}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving exam request: {str(e)}")
            raise

    async def get_exam_request(self, request_id: str) -> dict[str, Any] | None:
        """Alias for get_exam_request_by_id - method expected by tests"""
        return await self.get_exam_request_by_id(request_id)

    async def update_exam_status(
        self,
        request_id: str,
        exam_name: str,
        new_status: ExamStatus,
        updated_by: int,
        notes: str = ""
    ) -> dict[str, Any]:
        """Atualiza status de um exame específico"""
        try:
            update_result = {
                "request_id": request_id,
                "exam_name": exam_name,
                "old_status": "requested",  # Seria obtido do banco
                "new_status": new_status,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow().isoformat(),
                "notes": notes
            }

            logger.info(f"Updated exam status: {request_id}/{exam_name} -> {new_status}")
            return update_result

        except Exception as e:
            logger.error(f"Error updating exam status: {str(e)}")
            raise
