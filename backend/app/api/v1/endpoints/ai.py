"""
AI-powered medical analysis endpoints
Enhanced with specialized medical AI modules
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.ai import (
    TextAnalysisRequest, TextAnalysisResponse,
    DiagnosisSuggestionRequest, DiagnosisSuggestionResponse,
    ClinicalPredictionRequest, ClinicalPredictionResponse,
    DrugInteractionRequest, DrugInteractionResponse,
    MedicalImageAnalysisResponse
)
from app.services.ai.ai_engine import AIEngine
from app.modules.saude_mental import SaudeMentalPsiquiatriaIA
from app.modules.oncologia import OncologiaInteligenteIA
from app.modules.farmacia import FarmaciaHospitalarIA
from app.modules.reabilitacao import ReabilitacaoFisioterapiaIA

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze-text", response_model=TextAnalysisResponse)
async def analyze_medical_text(
    request: TextAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    ai_engine: AIEngine = Depends(lambda: AIEngine())
) -> Any:
    """
    Analisar texto médico com processamento de linguagem natural
    """
    try:
        result = await ai_engine.process_medical_text(
            text=request.text,
            context_type=request.context_type,
            patient_context=request.patient_context
        )
        
        return TextAnalysisResponse(
            processed_text=result.get("processed_text", {}),
            entities=result.get("entities", []),
            clinical_sentiment=result.get("clinical_sentiment", {}),
            suggestions=result.get("suggestions", []),
            confidence_score=result.get("confidence_score", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Error processing medical text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing text: {str(e)}"
        )

@router.post("/suggest-diagnoses", response_model=DiagnosisSuggestionResponse)
async def suggest_diagnoses(
    request: DiagnosisSuggestionRequest,
    current_user: User = Depends(get_current_active_user),
    ai_engine: AIEngine = Depends(lambda: AIEngine())
) -> Any:
    """
    Sugerir diagnósticos baseados em sintomas e dados clínicos
    """
    try:
        suggestions = await ai_engine.suggest_diagnoses(
            symptoms=request.symptoms,
            exam_results=request.exam_results,
            patient_history=request.patient_history
        )
        
        return DiagnosisSuggestionResponse(
            suggestions=suggestions,
            total_found=len(suggestions)
        )
        
    except Exception as e:
        logger.error(f"Error suggesting diagnoses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating diagnosis suggestions"
        )

@router.post("/predict-outcomes", response_model=ClinicalPredictionResponse)
async def predict_clinical_outcomes(
    request: ClinicalPredictionRequest,
    current_user: User = Depends(get_current_active_user),
    ai_engine: AIEngine = Depends(lambda: AIEngine())
) -> Any:
    """
    Predizer desfechos clínicos usando modelos de IA
    """
    try:
        predictions = await ai_engine.predict_clinical_outcomes(
            patient_data=request.patient_data,
            clinical_context=request.clinical_context,
            prediction_horizon=request.prediction_horizon
        )
        
        return ClinicalPredictionResponse(
            predictions=predictions,
            confidence_intervals=predictions.get("confidence_intervals", {}),
            risk_factors=predictions.get("risk_factors", [])
        )
        
    except Exception as e:
        logger.error(f"Error predicting clinical outcomes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating clinical predictions"
        )

@router.post("/extract-voice")
async def extract_from_voice(
    audio_file: UploadFile = File(...),
    language: str = "pt-BR",
    current_user: User = Depends(get_current_active_user),
    ai_engine: AIEngine = Depends(lambda: AIEngine())
) -> Any:
    """
    Extrair informações médicas de áudio
    """
    try:
        audio_content = await audio_file.read()
        
        result = await ai_engine.extract_medical_info_from_voice(
            audio_data=audio_content,
            audio_format=audio_file.content_type,
            language=language
        )
        
        return {
            "transcription": result.get("transcription", ""),
            "medical_entities": result.get("medical_entities", []),
            "clinical_notes": result.get("clinical_notes", {}),
            "confidence_score": result.get("confidence_score", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Error extracting from voice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing voice input"
        )

@router.post("/clinical-summary")
async def generate_clinical_summary(
    patient_id: int,
    summary_type: str = "comprehensive",
    current_user: User = Depends(get_current_active_user),
    ai_engine: AIEngine = Depends(lambda: AIEngine())
) -> Any:
    """
    Gerar resumo clínico inteligente
    """
    try:
        summary = await ai_engine.generate_clinical_summary(
            patient_id=patient_id,
            summary_type=summary_type,
            user_id=current_user.id
        )
        
        return {
            "patient_id": patient_id,
            "summary": summary,
            "summary_type": summary_type,
            "generated_by": "AI Engine",
            "timestamp": summary.get("generated_at")
        }
        
    except Exception as e:
        logger.error(f"Error generating clinical summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating clinical summary"
        )

@router.post("/drug-interactions", response_model=DrugInteractionResponse)
async def check_drug_interactions(
    request: DrugInteractionRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Verificar interações medicamentosas usando IA farmacêutica
    """
    try:
        farmacia_ai = FarmaciaHospitalarIA()
        
        interactions = await farmacia_ai.analisar_interacoes_medicamentosas(
            medicamentos=request.medications,
            paciente_contexto=request.patient_context,
            incluir_suplementos=request.include_supplements
        )
        
        return DrugInteractionResponse(
            interactions=interactions.get("interacoes_encontradas", []),
            severity_levels=interactions.get("niveis_severidade", {}),
            recommendations=interactions.get("recomendacoes", []),
            total_interactions=len(interactions.get("interacoes_encontradas", []))
        )
        
    except Exception as e:
        logger.error(f"Error checking drug interactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking drug interactions"
        )

@router.post("/analyze-image", response_model=MedicalImageAnalysisResponse)
async def analyze_medical_image(
    image_file: UploadFile = File(...),
    analysis_type: str = "general",
    current_user: User = Depends(get_current_active_user),
    ai_engine: AIEngine = Depends(lambda: AIEngine())
) -> Any:
    """
    Analisar imagens médicas usando IA
    """
    try:
        image_content = await image_file.read()
        
        analysis = await ai_engine.analyze_medical_image(
            image_data=image_content,
            image_format=image_file.content_type,
            analysis_type=analysis_type
        )
        
        return MedicalImageAnalysisResponse(
            findings=analysis.get("findings", []),
            confidence_scores=analysis.get("confidence_scores", {}),
            recommendations=analysis.get("recommendations", []),
            image_quality=analysis.get("image_quality", {}),
            analysis_type=analysis_type
        )
        
    except Exception as e:
        logger.error(f"Error analyzing medical image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing medical image"
        )

@router.get("/metrics")
async def get_ai_metrics(
    current_user: User = Depends(get_current_active_user),
    ai_engine: AIEngine = Depends(lambda: AIEngine())
) -> Any:
    """
    Obter métricas de performance da IA
    """
    try:
        metrics = await ai_engine.get_performance_metrics()
        
        return {
            "system_metrics": metrics.get("system_performance", {}),
            "accuracy_metrics": metrics.get("model_accuracy", {}),
            "usage_statistics": metrics.get("usage_stats", {}),
            "model_versions": metrics.get("model_versions", {}),
            "last_updated": metrics.get("last_updated")
        }
        
    except Exception as e:
        logger.error(f"Error retrieving AI metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving AI metrics"
        )

@router.post("/mental-health/assess")
async def assess_mental_health(
    patient_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Avaliação psiquiátrica usando IA especializada
    """
    try:
        mental_health_ai = SaudeMentalPsiquiatriaIA()
        
        assessment = await mental_health_ai.avaliar_estado_mental_completo(
            dados_paciente=patient_data,
            incluir_predicao_crise=True,
            gerar_plano_terapeutico=True
        )
        
        return {
            "assessment_results": assessment,
            "risk_level": assessment.get("nivel_risco"),
            "recommendations": assessment.get("recomendacoes"),
            "therapy_plan": assessment.get("plano_terapeutico")
        }
        
    except Exception as e:
        logger.error(f"Error in mental health assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing mental health assessment"
        )

@router.post("/oncology/analyze")
async def analyze_oncology_case(
    case_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Análise oncológica usando IA especializada
    """
    try:
        oncology_ai = OncologiaInteligenteIA()
        
        analysis = await oncology_ai.analisar_caso_oncologico_completo(
            dados_caso=case_data,
            incluir_medicina_precisao=True,
            gerar_plano_tratamento=True
        )
        
        return {
            "oncology_analysis": analysis,
            "treatment_recommendations": analysis.get("recomendacoes_tratamento"),
            "prognosis": analysis.get("prognostico"),
            "precision_medicine": analysis.get("medicina_precisao")
        }
        
    except Exception as e:
        logger.error(f"Error in oncology analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing oncology analysis"
        )

@router.post("/rehabilitation/plan")
async def create_rehabilitation_plan(
    patient_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Criar plano de reabilitação usando IA especializada
    """
    try:
        rehab_ai = ReabilitacaoFisioterapiaIA()
        
        plan = await rehab_ai.criar_programa_reabilitacao_personalizado(
            dados_paciente=patient_data,
            incluir_realidade_virtual=True,
            monitoramento_continuo=True
        )
        
        return {
            "rehabilitation_plan": plan,
            "exercises": plan.get("exercicios_recomendados"),
            "monitoring_schedule": plan.get("cronograma_monitoramento"),
            "expected_outcomes": plan.get("resultados_esperados")
        }
        
    except Exception as e:
        logger.error(f"Error creating rehabilitation plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating rehabilitation plan"
        )
