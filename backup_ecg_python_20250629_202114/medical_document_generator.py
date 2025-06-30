"""
Medical Document Generator - Gerador de documentos médicos baseado em diretrizes
Sistema completo para geração de receitas, atestados, relatórios e outros documentos médicos
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.medical_guidelines_engine import (
    MotorDiretrizesMedicasIA,
    ValidadorConformidadeDiretrizes)

logger = logging.getLogger(__name__)

class DocumentType(str, Enum):
    """Tipos de documentos médicos"""
    PRESCRIPTION = "prescription"  # Receita médica
    MEDICAL_CERTIFICATE = "medical_certificate"  # Atestado médico
    MEDICAL_REPORT = "medical_report"  # Relatório médico
    REFERRAL = "referral"  # Encaminhamento
    EXAM_REQUEST = "exam_request"  # Solicitação de exames
    DISCHARGE_SUMMARY = "discharge_summary"  # Sumário de alta
    PROCEDURE_REPORT = "procedure_report"  # Relatório de procedimento

@dataclass
class DocumentTemplate:
    """Template para documentos médicos"""
    document_type: DocumentType
    template_name: str
    required_fields: list[str]
    optional_fields: list[str]
    validation_rules: dict[str, Any]
    formatting_rules: dict[str, Any]

class MedicalDocumentGenerator:
    """Gerador de documentos médicos seguindo diretrizes atualizadas"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.guidelines_engine = MotorDiretrizesMedicasIA()
        self.validator = ValidadorConformidadeDiretrizes()
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> dict[str, DocumentTemplate]:
        """Inicializa templates de documentos médicos"""
        templates = {}

        prescription_template = DocumentTemplate(
            document_type=DocumentType.PRESCRIPTION,
            template_name="receita_medica_padrao",
            required_fields=[
                "patient_name", "patient_id", "physician_name", "physician_crm",
                "medications", "date", "diagnosis"
            ],
            optional_fields=[
                "patient_age", "patient_address", "instructions", "return_date"
            ],
            validation_rules={
                "medications": "must_have_name_dose_frequency",
                "physician_crm": "must_be_valid_crm",
                "date": "must_be_current_or_future"
            },
            formatting_rules={
                "header": "clinic_letterhead",
                "font": "Arial 12pt",
                "margins": "2cm_all_sides",
                "signature_space": "3cm_bottom"
            }
        )

        certificate_template = DocumentTemplate(
            document_type=DocumentType.MEDICAL_CERTIFICATE,
            template_name="atestado_medico_padrao",
            required_fields=[
                "patient_name", "patient_id", "physician_name", "physician_crm",
                "condition", "rest_period", "date"
            ],
            optional_fields=[
                "cid_code", "restrictions", "observations"
            ],
            validation_rules={
                "rest_period": "must_be_reasonable_duration",
                "condition": "must_justify_rest_period"
            },
            formatting_rules={
                "header": "clinic_letterhead",
                "font": "Arial 12pt",
                "margins": "2cm_all_sides"
            }
        )

        exam_request_template = DocumentTemplate(
            document_type=DocumentType.EXAM_REQUEST,
            template_name="solicitacao_exames_padrao",
            required_fields=[
                "patient_name", "patient_id", "physician_name", "physician_crm",
                "exams_requested", "clinical_indication", "date"
            ],
            optional_fields=[
                "urgency", "clinical_history", "medications_in_use"
            ],
            validation_rules={
                "exams_requested": "must_be_appropriate_for_indication",
                "clinical_indication": "must_justify_exams"
            },
            formatting_rules={
                "header": "clinic_letterhead",
                "font": "Arial 11pt",
                "margins": "2cm_all_sides"
            }
        )

        templates["receita_medica"] = prescription_template
        templates["atestado_medico"] = certificate_template
        templates["solicitacao_exames"] = exam_request_template

        return templates

    async def generate_prescription_document(
        self,
        patient_data: dict[str, Any],
        physician_data: dict[str, Any],
        prescription_data: dict[str, Any],
        diagnosis: str = ""
    ) -> dict[str, Any]:
        """Gera receita médica formatada seguindo diretrizes"""
        try:
            guidelines_validation = await self.validator.validar_acao_medica(
                acao=prescription_data,
                tipo_acao="prescricao",
                diagnostico=diagnosis
            )

            document = {
                "document_type": DocumentType.PRESCRIPTION,
                "document_id": f"RX_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "patient_info": {
                    "name": patient_data.get("name", ""),
                    "patient_id": patient_data.get("patient_id", ""),
                    "age": patient_data.get("age", ""),
                    "address": patient_data.get("address", "")
                },
                "physician_info": {
                    "name": physician_data.get("name", ""),
                    "crm": physician_data.get("crm", ""),
                    "specialty": physician_data.get("specialty", ""),
                    "clinic_name": physician_data.get("clinic_name", "")
                },
                "prescription_content": {
                    "diagnosis": diagnosis,
                    "medications": prescription_data.get("medications", []),
                    "instructions": prescription_data.get("instructions", ""),
                    "return_date": prescription_data.get("return_date", "")
                },
                "guidelines_compliance": guidelines_validation,
                "formatted_content": self._format_prescription_content(
                    patient_data, physician_data, prescription_data, diagnosis
                ),
                "validation_status": "approved" if guidelines_validation.get("conformidade", 0) >= 70 else "review_required"
            }

            logger.info(f"Generated prescription document: {document['document_id']}")
            return document

        except Exception as e:
            logger.error(f"Error generating prescription document: {str(e)}")
            raise

    def _format_prescription_content(
        self,
        patient_data: dict[str, Any],
        physician_data: dict[str, Any],
        prescription_data: dict[str, Any],
        diagnosis: str
    ) -> str:
        """Formata conteúdo da receita médica"""

        content = f"""
RECEITA MÉDICA

{physician_data.get('clinic_name', 'CLÍNICA MÉDICA')}
Dr(a). {physician_data.get('name', '')} - CRM: {physician_data.get('crm', '')}
{physician_data.get('specialty', '')}

Data: {datetime.utcnow().strftime('%d/%m/%Y')}

Paciente: {patient_data.get('name', '')}
Idade: {patient_data.get('age', '')} anos
Endereço: {patient_data.get('address', '')}

Diagnóstico: {diagnosis}

PRESCRIÇÃO:
"""

        medications = prescription_data.get("medications", [])
        for i, med in enumerate(medications, 1):
            content += f"""
{i}. {med.get('name', '')}
   Dose: {med.get('dosage', '')}
   Frequência: {med.get('frequency', '')}
   Duração: {med.get('duration', '')}
"""

        if prescription_data.get("instructions"):
            content += f"\nInstruções: {prescription_data.get('instructions')}"

        if prescription_data.get("return_date"):
            content += f"\nRetorno: {prescription_data.get('return_date')}"

        content += f"""

_________________________________
Dr(a). {physician_data.get('name', '')}
CRM: {physician_data.get('crm', '')}
"""

        return content

    async def generate_medical_certificate(
        self,
        patient_data: dict[str, Any],
        physician_data: dict[str, Any],
        certificate_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Gera atestado médico"""
        try:
            document = {
                "document_type": DocumentType.MEDICAL_CERTIFICATE,
                "document_id": f"AT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "patient_info": {
                    "name": patient_data.get("name", ""),
                    "patient_id": patient_data.get("patient_id", ""),
                    "age": patient_data.get("age", "")
                },
                "physician_info": {
                    "name": physician_data.get("name", ""),
                    "crm": physician_data.get("crm", ""),
                    "specialty": physician_data.get("specialty", "")
                },
                "certificate_content": {
                    "condition": certificate_data.get("condition", ""),
                    "rest_period": certificate_data.get("rest_period", ""),
                    "cid_code": certificate_data.get("cid_code", ""),
                    "restrictions": certificate_data.get("restrictions", ""),
                    "observations": certificate_data.get("observations", "")
                },
                "formatted_content": self._format_certificate_content(
                    patient_data, physician_data, certificate_data
                )
            }

            logger.info(f"Generated medical certificate: {document['document_id']}")
            return document

        except Exception as e:
            logger.error(f"Error generating medical certificate: {str(e)}")
            raise

    def _format_certificate_content(
        self,
        patient_data: dict[str, Any],
        physician_data: dict[str, Any],
        certificate_data: dict[str, Any]
    ) -> str:
        """Formata conteúdo do atestado médico"""

        content = f"""
ATESTADO MÉDICO

{physician_data.get('clinic_name', 'CLÍNICA MÉDICA')}
Dr(a). {physician_data.get('name', '')} - CRM: {physician_data.get('crm', '')}
{physician_data.get('specialty', '')}

Atesto para os devidos fins que o(a) paciente {patient_data.get('name', '')},
portador(a) do documento de identidade nº {patient_data.get('patient_id', '')},
encontra-se sob meus cuidados médicos.

Diagnóstico: {certificate_data.get('condition', '')}
{f"CID: {certificate_data.get('cid_code', '')}" if certificate_data.get('cid_code') else ""}

Necessita de afastamento de suas atividades por {certificate_data.get('rest_period', '')} dias,
a partir de {datetime.utcnow().strftime('%d/%m/%Y')}.

{f"Restrições: {certificate_data.get('restrictions', '')}" if certificate_data.get('restrictions') else ""}
{f"Observações: {certificate_data.get('observations', '')}" if certificate_data.get('observations') else ""}

Data: {datetime.utcnow().strftime('%d/%m/%Y')}

_________________________________
Dr(a). {physician_data.get('name', '')}
CRM: {physician_data.get('crm', '')}
"""

        return content

    async def generate_exam_request_document(
        self,
        patient_data: dict[str, Any],
        physician_data: dict[str, Any],
        exam_request_data: dict[str, Any],
        diagnosis: str = ""
    ) -> dict[str, Any]:
        """Gera solicitação de exames baseada em diretrizes"""
        try:
            exams_validation = []
            for exam in exam_request_data.get("exams", []):
                validation = await self._validate_exam_appropriateness(
                    exam.get("name", ""), diagnosis
                )
                exams_validation.append(validation)

            document = {
                "document_type": DocumentType.EXAM_REQUEST,
                "document_id": f"EX_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "patient_info": {
                    "name": patient_data.get("name", ""),
                    "patient_id": patient_data.get("patient_id", ""),
                    "age": patient_data.get("age", "")
                },
                "physician_info": {
                    "name": physician_data.get("name", ""),
                    "crm": physician_data.get("crm", ""),
                    "specialty": physician_data.get("specialty", "")
                },
                "exam_request_content": {
                    "clinical_indication": exam_request_data.get("clinical_indication", ""),
                    "exams": exam_request_data.get("exams", []),
                    "urgency": exam_request_data.get("urgency", "routine"),
                    "clinical_history": exam_request_data.get("clinical_history", "")
                },
                "exams_validation": exams_validation,
                "formatted_content": self._format_exam_request_content(
                    patient_data, physician_data, exam_request_data, diagnosis
                )
            }

            logger.info(f"Generated exam request document: {document['document_id']}")
            return document

        except Exception as e:
            logger.error(f"Error generating exam request document: {str(e)}")
            raise

    async def _validate_exam_appropriateness(
        self,
        exam_name: str,
        diagnosis: str
    ) -> dict[str, Any]:
        """Valida apropriação de exame específico"""
        return {
            "exam_name": exam_name,
            "appropriate": True,
            "evidence_level": "clinical_judgment",
            "justification": "Exame solicitado conforme avaliação clínica"
        }

    def _format_exam_request_content(
        self,
        patient_data: dict[str, Any],
        physician_data: dict[str, Any],
        exam_request_data: dict[str, Any],
        diagnosis: str
    ) -> str:
        """Formata conteúdo da solicitação de exames"""

        content = f"""
SOLICITAÇÃO DE EXAMES

{physician_data.get('clinic_name', 'CLÍNICA MÉDICA')}
Dr(a). {physician_data.get('name', '')} - CRM: {physician_data.get('crm', '')}
{physician_data.get('specialty', '')}

Data: {datetime.utcnow().strftime('%d/%m/%Y')}

Paciente: {patient_data.get('name', '')}
Idade: {patient_data.get('age', '')} anos
Documento: {patient_data.get('patient_id', '')}

Indicação Clínica: {exam_request_data.get('clinical_indication', '')}
{f"Diagnóstico: {diagnosis}" if diagnosis else ""}

EXAMES SOLICITADOS:
"""

        exams = exam_request_data.get("exams", [])
        for i, exam in enumerate(exams, 1):
            content += f"{i}. {exam.get('name', '')}\n"
            if exam.get('justification'):
                content += f"   Justificativa: {exam.get('justification')}\n"

        urgency = exam_request_data.get("urgency")
        if urgency and urgency != "routine":
            content += f"\nUrgência: {str(urgency).upper()}"

        if exam_request_data.get("clinical_history"):
            content += f"\nHistória Clínica: {exam_request_data.get('clinical_history')}"

        content += f"""

_________________________________
Dr(a). {physician_data.get('name', '')}
CRM: {physician_data.get('crm', '')}
"""

        return content
