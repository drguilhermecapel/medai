"""
Serviço de diagnóstico por IA do MedAI
Gerencia análise de exames médicos usando modelos de machine learning
"""
import uuid
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import json
from dataclasses import dataclass, asdict

from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.diagnostic import Diagnostic
from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository
from app.services.ml_model_service import MLModelService
from app.services.validation_service import ValidationService
from app.core.constants import (
    DiagnosticStatus, DiagnosticCategory, AnalysisStatus,
    ClinicalUrgency, Priority, ModelType, ExamType
)
from app.core.exceptions import (
    AIError, ModelNotFoundError, InferenceError, InsufficientDataError,
    LowConfidenceError, ValidationError
)
from app.utils.logging_config import get_ai_logger, log_ai_operation
from app.core.config import ML_CONFIG

logger = get_ai_logger()


@dataclass
class DiagnosticResult:
    """Resultado de diagnóstico por IA"""
    primary_diagnosis: str
    confidence: float
    differential_diagnoses: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    features_detected: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    measurements: Dict[str, Any]
    interpretation: str
    recommendations: List[str]
    urgency_level: ClinicalUrgency
    quality_score: float
    processing_time: float
    model_info: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        result = asdict(self)
        result['urgency_level'] = self.urgency_level.value
        return result


@dataclass
class AnalysisMetrics:
    """Métricas de análise"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confidence_distribution: Dict[str, int]
    processing_stats: Dict[str, float]


class AIDiagnosticService:
    """Serviço principal de diagnóstico por IA"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ml_service = MLModelService()
        self.validation_service = ValidationService()
        self.diagnostic_repo = BaseRepository(Diagnostic, db)
        self.exam_repo = BaseRepository(Exam, db)
        self.logger = logger
        
        # Configurações de análise
        self.min_confidence_threshold = 0.7
        self.high_confidence_threshold = 0.9
        self.max_processing_time = 120  # 2 minutos
        
        # Cache de modelos carregados
        self._model_cache = {}
        self._cache_ttl = timedelta(hours=1)
        self._cache_timestamps = {}
    
    # === MÉTODOS PRINCIPAIS DE DIAGNÓSTICO ===
    
    @log_ai_operation("diagnostic_analysis", "multi_model")
    async def analyze_exam(
        self, 
        exam_id: uuid.UUID,
        model_preferences: Optional[List[str]] = None,
        force_reanalysis: bool = False
    ) -> DiagnosticResult:
        """
        Analisa exame médico usando IA
        
        Args:
            exam_id: ID do exame para analisar
            model_preferences: Lista de modelos preferidos
            force_reanalysis: Forçar nova análise mesmo se já existe
            
        Returns:
            Resultado do diagnóstico
            
        Raises:
            ModelNotFoundError: Modelo não encontrado
            InferenceError: Erro durante inferência
            InsufficientDataError: Dados insuficientes
        """
        start_time = datetime.utcnow()
        
        # Buscar exame
        exam = self.exam_repo.get_or_404(exam_id)
        
        # Verificar se já existe diagnóstico
        if not force_reanalysis:
            existing_diagnostic = self._get_existing_diagnostic(exam_id)
            if existing_diagnostic and existing_diagnostic.diagnostic_status == DiagnosticStatus.AI_COMPLETED.value:
                self.logger.info(f"Using existing diagnostic for exam {exam_id}")
                return self._convert_diagnostic_to_result(existing_diagnostic)
        
        # Validar dados do exame
        validation_result = self.validation_service.validate_exam_data(exam.to_dict())
        if not validation_result.is_valid:
            raise ValidationError(f"Exam validation failed: {validation_result.errors}")
        
        # Criar ou atualizar diagnóstico
        diagnostic = await self._create_or_update_diagnostic(exam)
        
        try:
            # Determinar modelos para usar
            models_to_use = self._determine_models(exam, model_preferences)
            
            # Executar análise
            analysis_results = await self._run_multi_model_analysis(exam, models_to_use)
            
            # Consolidar resultados
            consolidated_result = self._consolidate_results(analysis_results, exam)
            
            # Calcular métricas de qualidade
            quality_metrics = self._calculate_quality_metrics(consolidated_result, analysis_results)
            consolidated_result.quality_score = quality_metrics.accuracy
            
            # Calcular tempo de processamento
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            consolidated_result.processing_time = processing_time
            
            # Atualizar diagnóstico no banco
            await self._update_diagnostic_with_results(diagnostic, consolidated_result)
            
            self.logger.log_ai_operation(
                level=20,  # INFO
                operation="diagnostic_completed",
                model_name="multi_model",
                confidence=consolidated_result.confidence,
                processing_time=processing_time,
                extra={
                    'exam_id': str(exam_id),
                    'diagnosis': consolidated_result.primary_diagnosis,
                    'urgency': consolidated_result.urgency_level.value
                }
            )
            
            return consolidated_result
            
        except Exception as e:
            # Marcar diagnóstico como falhou
            diagnostic.fail_ai_analysis(str(e))
            self.db.add(diagnostic)
            self.db.commit()
            
            self.logger.log_ai_operation(
                level=40,  # ERROR
                operation="diagnostic_failed",
                model_name="multi_model",
                extra={'exam_id': str(exam_id), 'error': str(e)}
            )
            
            if isinstance(e, (ModelNotFoundError, InferenceError, InsufficientDataError)):
                raise
            else:
                raise InferenceError("multi_model", str(e))
    
    async def _run_multi_model_analysis(
        self, 
        exam: Exam, 
        models: List[str]
    ) -> Dict[str, DiagnosticResult]:
        """
        Executa análise com múltiplos modelos
        
        Args:
            exam: Exame para analisar
            models: Lista de modelos para usar
            
        Returns:
            Resultados de cada modelo
        """
        results = {}
        
        # Executar modelos em paralelo quando possível
        tasks = []
        for model_name in models:
            task = self._analyze_with_single_model(exam, model_name)
            tasks.append((model_name, task))
        
        # Aguardar resultados
        for model_name, task in tasks:
            try:
                result = await task
                results[model_name] = result
            except Exception as e:
                self.logger.error(f"Model {model_name} failed: {e}")
                # Continuar com outros modelos
                continue
        
        if not results:
            raise InferenceError("multi_model", "All models failed")
        
        return results
    
    async def _analyze_with_single_model(
        self, 
        exam: Exam, 
        model_name: str
    ) -> DiagnosticResult:
        """
        Analisa exame com um modelo específico
        
        Args:
            exam: Exame para analisar
            model_name: Nome do modelo
            
        Returns:
            Resultado do diagnóstico
        """
        start_time = datetime.utcnow()
        
        try:
            # Carregar modelo se necessário
            model = await self._load_model(model_name)
            
            # Preparar dados
            input_data = self._prepare_input_data(exam, model_name)
            
            # Executar inferência
            raw_results = await self._run_inference(model, input_data, model_name)
            
            # Processar resultados
            processed_results = self._process_model_results(raw_results, exam, model_name)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            processed_results.processing_time = processing_time
            processed_results.model_info = {
                "name": model_name,
                "version": ML_CONFIG.get(model_name, {}).get("version", "unknown"),
                "type": ML_CONFIG.get(model_name, {}).get("type", "unknown")
            }
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Single model analysis failed for {model_name}: {e}")
            raise InferenceError(model_name, str(e))
    
    def _consolidate_results(
        self, 
        model_results: Dict[str, DiagnosticResult], 
        exam: Exam
    ) -> DiagnosticResult:
        """
        Consolida resultados de múltiplos modelos
        
        Args:
            model_results: Resultados de cada modelo
            exam: Exame analisado
            
        Returns:
            Resultado consolidado
        """
        if not model_results:
            raise InferenceError("consolidation", "No model results to consolidate")
        
        # Estratégia de consolidação baseada em confiança e concordância
        primary_diagnoses = {}
        all_findings = []
        all_features = []
        all_anomalies = []
        all_measurements = {}
        all_recommendations = set()
        
        total_confidence = 0
        max_confidence = 0
        best_model_result = None
        
        # Coletar dados de todos os modelos
        for model_name, result in model_results.items():
            # Diagnósticos primários
            diagnosis = result.primary_diagnosis
            if diagnosis in primary_diagnoses:
                primary_diagnoses[diagnosis]['count'] += 1
                primary_diagnoses[diagnosis]['total_confidence'] += result.confidence
                primary_diagnoses[diagnosis]['models'].append(model_name)
            else:
                primary_diagnoses[diagnosis] = {
                    'count': 1,
                    'total_confidence': result.confidence,
                    'models': [model_name]
                }
            
            # Coletar outros dados
            all_findings.extend(result.findings)
            all_features.extend(result.features_detected)
            all_anomalies.extend(result.anomalies)
            all_measurements.update(result.measurements)
            all_recommendations.update(result.recommendations)
            
            total_confidence += result.confidence
            if result.confidence > max_confidence:
                max_confidence = result.confidence
                best_model_result = result
        
        # Determinar diagnóstico primário consolidado
        best_diagnosis = max(
            primary_diagnoses.items(),
            key=lambda x: (x[1]['count'], x[1]['total_confidence'] / x[1]['count'])
        )
        
        primary_diagnosis = best_diagnosis[0]
        consensus_confidence = best_diagnosis[1]['total_confidence'] / best_diagnosis[1]['count']
        
        # Criar diagnósticos diferenciais
        differential_diagnoses = []
        for diagnosis, data in primary_diagnoses.items():
            if diagnosis != primary_diagnosis:
                avg_confidence = data['total_confidence'] / data['count']
                differential_diagnoses.append({
                    'diagnosis': diagnosis,
                    'confidence': avg_confidence,
                    'supporting_models': data['models'],
                    'agreement_count': data['count']
                })
        
        # Ordenar por confiança
        differential_diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Determinar urgência baseada no consenso
        urgency_level = self._determine_urgency(primary_diagnosis, consensus_confidence, all_findings)
        
        # Criar interpretação consolidada
        interpretation = self._generate_consolidated_interpretation(
            primary_diagnosis, consensus_confidence, model_results, exam
        )
        
        # Consolidar resultado final
        consolidated_result = DiagnosticResult(
            primary_diagnosis=primary_diagnosis,
            confidence=consensus_confidence,
            differential_diagnoses=differential_diagnoses,
            findings=self._deduplicate_findings(all_findings),
            features_detected=self._deduplicate_features(all_features),
            anomalies=self._deduplicate_anomalies(all_anomalies),
            measurements=all_measurements,
            interpretation=interpretation,
            recommendations=list(all_recommendations),
            urgency_level=urgency_level,
            quality_score=0.0,  # Será calculado separadamente
            processing_time=0.0,  # Será calculado separadamente
            model_info={
                "ensemble": True,
                "models_used": list(model_results.keys()),
                "consensus_strength": len(best_diagnosis[1]['models']) / len(model_results)
            }
        )
        
        return consolidated_result
    
    # === MÉTODOS DE SUPORTE ===
    
    def _determine_models(self, exam: Exam, preferences: Optional[List[str]] = None) -> List[str]:
        """
        Determina quais modelos usar para o exame
        
        Args:
            exam: Exame para analisar
            preferences: Modelos preferidos
            
        Returns:
            Lista de modelos para usar
        """
        available_models = list(ML_CONFIG.keys())
        
        # Filtrar modelos baseado no tipo de exame
        exam_type_models = self._get_models_for_exam_type(exam.exam_type)
        
        if preferences:
            # Usar preferências se especificadas
            models = [m for m in preferences if m in available_models and m in exam_type_models]
        else:
            # Usar modelos padrão para o tipo de exame
            models = exam_type_models
        
        if not models:
            # Fallback para modelo diagnóstico padrão
            models = ["diagnostic"]
        
        return models
    
    def _get_models_for_exam_type(self, exam_type: str) -> List[str]:
        """
        Retorna modelos apropriados para tipo de exame
        
        Args:
            exam_type: Tipo do exame
            
        Returns:
            Lista de modelos apropriados
        """
        # Mapeamento de tipos de exame para modelos
        exam_model_mapping = {
            ExamType.XRAY.value: ["diagnostic", "pathology"],
            ExamType.CT_SCAN.value: ["diagnostic", "multi_pathology"],
            ExamType.MRI.value: ["diagnostic", "multi_pathology"],
            ExamType.ULTRASOUND.value: ["diagnostic"],
            ExamType.BLOOD_TEST.value: ["pathology"],
            ExamType.PATHOLOGY.value: ["pathology", "multi_pathology"],
            ExamType.DERMATOLOGY.value: ["diagnostic", "pathology"]
        }
        
        return exam_model_mapping.get(exam_type, ["diagnostic"])
    
    async def _load_model(self, model_name: str):
        """
        Carrega modelo de IA
        
        Args:
            model_name: Nome do modelo
            
        Returns:
            Modelo carregado
        """
        # Verificar cache
        if model_name in self._model_cache:
            cache_time = self._cache_timestamps.get(model_name)
            if cache_time and datetime.utcnow() - cache_time < self._cache_ttl:
                return self._model_cache[model_name]
        
        # Carregar modelo
        try:
            model = await self.ml_service.load_model(model_name)
            
            # Armazenar no cache
            self._model_cache[model_name] = model
            self._cache_timestamps[model_name] = datetime.utcnow()
            
            return model
            
        except Exception as e:
            raise ModelNotFoundError(model_name)
    
    def _prepare_input_data(self, exam: Exam, model_name: str) -> Dict[str, Any]:
        """
        Prepara dados de entrada para o modelo
        
        Args:
            exam: Exame para processar
            model_name: Nome do modelo
            
        Returns:
            Dados preparados para inferência
        """
        # Configuração do modelo
        model_config = ML_CONFIG.get(model_name, {})
        
        input_data = {
            "exam_id": str(exam.id),
            "exam_type": exam.exam_type,
            "patient_age": self._calculate_patient_age(exam),
            "exam_data": exam.exam_data or {},
            "findings": exam.findings or "",
            "measurements": exam.measurements or {},
            "clinical_indication": exam.clinical_indication or "",
            "symptoms": exam.symptoms or [],
            "file_paths": exam.get_all_files(),
            "model_config": model_config
        }
        
        # Adicionar dados específicos por tipo de modelo
        if model_name == "multi_pathology":
            input_data["body_part"] = exam.body_part
            input_data["contrast_used"] = exam.requires_contrast
        
        return input_data
    
    def _calculate_patient_age(self, exam: Exam) -> Optional[int]:
        """Calcula idade do paciente no momento do exame"""
        try:
            if hasattr(exam, 'patient') and exam.patient and exam.patient.birth_date:
                exam_date = exam.performed_date or exam.created_at
                birth_date = exam.patient.birth_date
                
                if isinstance(birth_date, datetime):
                    birth_date = birth_date.date()
                if isinstance(exam_date, datetime):
                    exam_date = exam_date.date()
                
                age = exam_date.year - birth_date.year
                if (exam_date.month, exam_date.day) < (birth_date.month, birth_date.day):
                    age -= 1
                
                return age
        except Exception as e:
            self.logger.warning(f"Could not calculate patient age: {e}")
        
        return None
    
    async def _run_inference(self, model, input_data: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """
        Executa inferência do modelo
        
        Args:
            model: Modelo carregado
            input_data: Dados de entrada
            model_name: Nome do modelo
            
        Returns:
            Resultados brutos da inferência
        """
        try:
            # Usar serviço ML para inferência
            results = await self.ml_service.predict(model_name, input_data)
            return results
            
        except Exception as e:
            raise InferenceError(model_name, str(e))
    
    def _process_model_results(
        self, 
        raw_results: Dict[str, Any], 
        exam: Exam, 
        model_name: str
    ) -> DiagnosticResult:
        """
        Processa resultados brutos do modelo
        
        Args:
            raw_results: Resultados brutos
            exam: Exame analisado
            model_name: Nome do modelo
            
        Returns:
            Resultado processado
        """
        # Extrair dados principais
        primary_diagnosis = raw_results.get("prediction", "Inconclusivo")
        confidence = float(raw_results.get("confidence", 0.0))
        
        # Verificar confiança mínima
        if confidence < self.min_confidence_threshold:
            raise LowConfidenceError(confidence, self.min_confidence_threshold)
        
        # Processar diagnósticos diferenciais
        differential_diagnoses = []
        if "differential_diagnoses" in raw_results:
            for diff in raw_results["differential_diagnoses"]:
                differential_diagnoses.append({
                    "diagnosis": diff.get("diagnosis", ""),
                    "confidence": float(diff.get("confidence", 0.0)),
                    "reasoning": diff.get("reasoning", "")
                })
        
        # Processar achados
        findings = []
        if "findings" in raw_results:
            for finding in raw_results["findings"]:
                findings.append({
                    "description": finding.get("description", ""),
                    "confidence": float(finding.get("confidence", 0.0)),
                    "location": finding.get("location", ""),
                    "severity": finding.get("severity", "normal")
                })
        
        # Processar características detectadas
        features = []
        if "features" in raw_results:
            for feature in raw_results["features"]:
                features.append({
                    "name": feature.get("name", ""),
                    "value": feature.get("value", ""),
                    "confidence": float(feature.get("confidence", 0.0))
                })
        
        # Processar anomalias
        anomalies = []
        if "anomalies" in raw_results:
            for anomaly in raw_results["anomalies"]:
                anomalies.append({
                    "type": anomaly.get("type", ""),
                    "description": anomaly.get("description", ""),
                    "severity": anomaly.get("severity", "mild"),
                    "location": anomaly.get("location", "")
                })
        
        # Medições
        measurements = raw_results.get("measurements", {})
        
        # Interpretação
        interpretation = raw_results.get("interpretation", f"Análise realizada com modelo {model_name}")
        
        # Recomendações
        recommendations = raw_results.get("recommendations", [])
        
        # Determinar urgência
        urgency_level = self._determine_urgency(primary_diagnosis, confidence, findings)
        
        return DiagnosticResult(
            primary_diagnosis=primary_diagnosis,
            confidence=confidence,
            differential_diagnoses=differential_diagnoses,
            findings=findings,
            features_detected=features,
            anomalies=anomalies,
            measurements=measurements,
            interpretation=interpretation,
            recommendations=recommendations,
            urgency_level=urgency_level,
            quality_score=0.0,  # Será calculado
            processing_time=0.0,  # Será calculado
            model_info={"name": model_name}
        )
    
    def _determine_urgency(
        self, 
        diagnosis: str, 
        confidence: float, 
        findings: List[Dict[str, Any]]
    ) -> ClinicalUrgency:
        """
        Determina urgência clínica baseada no diagnóstico
        
        Args:
            diagnosis: Diagnóstico principal
            confidence: Confiança da IA
            findings: Achados do exame
            
        Returns:
            Nível de urgência clínica
        """
        # Palavras-chave para urgência
        urgent_keywords = [
            "emergência", "crítico", "grave", "agudo", "hemorragia",
            "infarto", "embolia", "trombose", "perfuração", "ruptura"
        ]
        
        emergency_keywords = [
            "parada", "choque", "pneumotórax", "tamponamento",
            "aneurisma roto", "trauma craniano"
        ]
        
        diagnosis_lower = diagnosis.lower()
        
        # Verificar emergência
        if any(keyword in diagnosis_lower for keyword in emergency_keywords):
            return ClinicalUrgency.EMERGENCY
        
        # Verificar urgência
        if any(keyword in diagnosis_lower for keyword in urgent_keywords):
            return ClinicalUrgency.URGENT
        
        # Verificar achados preocupantes
        severe_findings = [f for f in findings if f.get("severity") in ["severe", "critical"]]
        if severe_findings and confidence > 0.8:
            return ClinicalUrgency.URGENT
        
        # Verificar confiança alta em diagnóstico sério
        if confidence > 0.9 and any(keyword in diagnosis_lower for keyword in ["tumor", "câncer", "maligno"]):
            return ClinicalUrgency.URGENT
        
        return ClinicalUrgency.ROUTINE
    
    def _deduplicate_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove achados duplicados"""
        seen = set()
        unique_findings = []
        
        for finding in findings:
            description = finding.get("description", "").lower()
            if description not in seen:
                seen.add(description)
                unique_findings.append(finding)
        
        return unique_findings
    
    def _deduplicate_features(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove características duplicadas"""
        seen = set()
        unique_features = []
        
        for feature in features:
            name = feature.get("name", "").lower()
            if name not in seen:
                seen.add(name)
                unique_features.append(feature)
        
        return unique_features
    
    def _deduplicate_anomalies(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove anomalias duplicadas"""
        seen = set()
        unique_anomalies = []
        
        for anomaly in anomalies:
            key = f"{anomaly.get('type', '')}_{anomaly.get('location', '')}".lower()
            if key not in seen:
                seen.add(key)
                unique_anomalies.append(anomaly)
        
        return unique_anomalies
    
    # === MÉTODOS DE PERSISTÊNCIA ===
    
    async def _create_or_update_diagnostic(self, exam: Exam) -> Diagnostic:
        """
        Cria ou atualiza diagnóstico para o exame
        
        Args:
            exam: Exame para diagnosticar
            
        Returns:
            Diagnóstico criado ou atualizado
        """
        # Verificar se já existe
        existing = self._get_existing_diagnostic(exam.id)
        
        if existing:
            # Atualizar existente
            existing.start_ai_analysis("multi_model", "ensemble")
            diagnostic = existing
        else:
            # Criar novo
            diagnostic = Diagnostic(
                exam_id=exam.id,
                patient_id=exam.patient_id,
                title=f"Diagnóstico AI - {exam.title}",
                category=DiagnosticCategory.ABNORMAL.value,  # Será atualizado
                clinical_urgency=ClinicalUrgency.ROUTINE.value  # Será atualizado
            )
            diagnostic.start_ai_analysis("multi_model", "ensemble")
            self.db.add(diagnostic)
        
        self.db.commit()
        return diagnostic
    
    def _get_existing_diagnostic(self, exam_id: uuid.UUID) -> Optional[Diagnostic]:
        """Busca diagnóstico existente para o exame"""
        return self.db.query(Diagnostic).filter(
            Diagnostic.exam_id == exam_id,
            Diagnostic.is_deleted.is_(False)
        ).first()
    
    async def _update_diagnostic_with_results(
        self, 
        diagnostic: Diagnostic, 
        results: DiagnosticResult
    ) -> None:
        """
        Atualiza diagnóstico com resultados da IA
        
        Args:
            diagnostic: Diagnóstico para atualizar
            results: Resultados da análise
        """
        # Converter resultado para dados do diagnóstico
        diagnostic.complete_ai_analysis(results.to_dict())
        
        # Atualizar campos específicos
        diagnostic.category = self._determine_category(results.primary_diagnosis)
        diagnostic.clinical_urgency = results.urgency_level.value
        diagnostic.quality_score = results.quality_score
        
        self.db.add(diagnostic)
        self.db.commit()
    
    def _determine_category(self, diagnosis: str) -> str:
        """Determina categoria do diagnóstico"""
        normal_keywords = ["normal", "negativo", "sem alterações", "dentro da normalidade"]
        
        if any(keyword in diagnosis.lower() for keyword in normal_keywords):
            return DiagnosticCategory.NORMAL.value
        
        pathological_keywords = ["tumor", "câncer", "infarto", "fratura", "lesão"]
        
        if any(keyword in diagnosis.lower() for keyword in pathological_keywords):
            return DiagnosticCategory.PATHOLOGICAL.value
        
        return DiagnosticCategory.ABNORMAL.value
    
    def _convert_diagnostic_to_result(self, diagnostic: Diagnostic) -> DiagnosticResult:
        """Converte diagnóstico existente para DiagnosticResult"""
        return DiagnosticResult(
            primary_diagnosis=diagnostic.ai_primary_diagnosis or "Inconclusivo",
            confidence=float(diagnostic.ai_confidence or 0.0),
            differential_diagnoses=diagnostic.ai_differential_diagnoses or [],
            findings=diagnostic.ai_findings or [],
            features_detected=diagnostic.ai_features_detected or [],
            anomalies=diagnostic.ai_anomalies or [],
            measurements=diagnostic.ai_measurements or {},
            interpretation=diagnostic.ai_interpretation or "",
            recommendations=diagnostic.ai_recommendations or [],
            urgency_level=ClinicalUrgency(diagnostic.clinical_urgency),
            quality_score=float(diagnostic.quality_score or 0.0),
            processing_time=float(diagnostic.ai_processing_time or 0.0),
            model_info={
                "name": diagnostic.ai_model_used or "unknown",
                "version": diagnostic.ai_model_version or "unknown"
            }
        )
    
    def _calculate_quality_metrics(
        self, 
        result: DiagnosticResult, 
        model_results: Dict[str, DiagnosticResult]
    ) -> AnalysisMetrics:
        """Calcula métricas de qualidade da análise"""
        
        # Simular métricas (em produção viriam de validação real)
        accuracy = min(result.confidence + 0.1, 1.0)
        precision = result.confidence
        recall = result.confidence * 0.95
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Distribuição de confiança
        confidence_ranges = {"low": 0, "medium": 0, "high": 0}
        for model_result in model_results.values():
            if model_result.confidence < 0.7:
                confidence_ranges["low"] += 1
            elif model_result.confidence < 0.9:
                confidence_ranges["medium"] += 1
            else:
                confidence_ranges["high"] += 1
        
        # Estatísticas de processamento
        processing_times = [r.processing_time for r in model_results.values()]
        processing_stats = {
            "min_time": min(processing_times) if processing_times else 0,
            "max_time": max(processing_times) if processing_times else 0,
            "avg_time": sum(processing_times) / len(processing_times) if processing_times else 0
        }
        
        return AnalysisMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            confidence_distribution=confidence_ranges,
            processing_stats=processing_stats
        )
    
    def _generate_consolidated_interpretation(
        self, 
        diagnosis: str, 
        confidence: float, 
        model_results: Dict[str, DiagnosticResult], 
        exam: Exam
    ) -> str:
        """Gera interpretação consolidada"""
        
        model_count = len(model_results)
        agreement_info = f"Consenso entre {model_count} modelos de IA"
        
        interpretation_parts = [
            f"Diagnóstico: {diagnosis}",
            f"Confiança: {confidence:.1%}",
            f"Baseado em: {agreement_info}",
            f"Tipo de exame: {exam.exam_type}"
        ]
        
        if exam.clinical_indication:
            interpretation_parts.append(f"Indicação clínica: {exam.clinical_indication}")
        
        # Adicionar observações sobre concordância
        diagnoses_found = set(r.primary_diagnosis for r in model_results.values())
        if len(diagnoses_found) == 1:
            interpretation_parts.append("Todos os modelos concordaram com o diagnóstico.")
        else:
            interpretation_parts.append(f"Foram considerados {len(diagnoses_found)} diagnósticos diferentes.")
        
        return " | ".join(interpretation_parts)
    
    # === MÉTODOS PÚBLICOS ADICIONAIS ===
    
    async def get_diagnostic_status(self, exam_id: uuid.UUID) -> Dict[str, Any]:
        """
        Retorna status do diagnóstico para um exame
        
        Args:
            exam_id: ID do exame
            
        Returns:
            Status do diagnóstico
        """
        diagnostic = self._get_existing_diagnostic(exam_id)
        
        if not diagnostic:
            return {
                "status": "not_started",
                "message": "Diagnóstico não iniciado"
            }
        
        return {
            "status": diagnostic.diagnostic_status,
            "ai_status": diagnostic.ai_analysis_status,
            "confidence": diagnostic.ai_confidence,
            "started_at": diagnostic.ai_started_at.isoformat() if diagnostic.ai_started_at else None,
            "completed_at": diagnostic.ai_completed_at.isoformat() if diagnostic.ai_completed_at else None,
            "processing_time": diagnostic.ai_processing_time
        }
    
    async def reanalyze_exam(
        self, 
        exam_id: uuid.UUID, 
        reason: str = "Manual reanalysis"
    ) -> DiagnosticResult:
        """
        Força nova análise de um exame
        
        Args:
            exam_id: ID do exame
            reason: Motivo da nova análise
            
        Returns:
            Novo resultado do diagnóstico
        """
        self.logger.info(f"Reanalyzing exam {exam_id}: {reason}")
        return await self.analyze_exam(exam_id, force_reanalysis=True)