"""
Serviço de gerenciamento de modelos ML do MedAI
Carrega, gerencia e executa modelos de machine learning
"""
import pickle
import joblib
import numpy as np
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import json
import hashlib
from dataclasses import dataclass
from abc import ABC, abstractmethod

from app.core.config import ML_CONFIG, settings
from app.core.constants import ModelType
from app.core.exceptions import (
    ModelNotFoundError, ModelLoadError, InferenceError,
    ConfigurationError
)
from app.utils.logging_config import get_ai_logger, log_ai_operation
from app.services.validation_service import ValidationService

logger = get_ai_logger()


@dataclass
class ModelInfo:
    """Informações de um modelo"""
    name: str
    version: str
    type: str
    path: str
    size_mb: float
    loaded_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    performance_metrics: Dict[str, float]


@dataclass
class PredictionResult:
    """Resultado de uma predição"""
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    features: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class BaseMLModel(ABC):
    """Classe base para modelos ML"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.model = None
        self.is_loaded = False
        self.load_time = None
        self.usage_count = 0
    
    @abstractmethod
    async def load(self) -> None:
        """Carrega o modelo"""
        pass
    
    @abstractmethod
    async def predict(self, input_data: Dict[str, Any]) -> PredictionResult:
        """Executa predição"""
        pass
    
    @abstractmethod
    def preprocess(self, input_data: Dict[str, Any]) -> Any:
        """Pré-processa dados de entrada"""
        pass
    
    @abstractmethod
    def postprocess(self, raw_output: Any, input_data: Dict[str, Any]) -> PredictionResult:
        """Pós-processa saída do modelo"""
        pass
    
    def unload(self) -> None:
        """Descarrega modelo da memória"""
        self.model = None
        self.is_loaded = False
    
    def get_info(self) -> ModelInfo:
        """Retorna informações do modelo"""
        model_path = Path(self.config.get("path", ""))
        size_mb = model_path.stat().st_size / (1024 * 1024) if model_path.exists() else 0
        
        return ModelInfo(
            name=self.name,
            version=self.config.get("version", "unknown"),
            type=self.config.get("type", "unknown"),
            path=str(model_path),
            size_mb=round(size_mb, 2),
            loaded_at=self.load_time,
            last_used=None,  # Seria rastreado em produção
            usage_count=self.usage_count,
            performance_metrics=self.config.get("performance_metrics", {})
        )


class DiagnosticModel(BaseMLModel):
    """Modelo para diagnóstico geral"""
    
    async def load(self) -> None:
        """Carrega modelo de diagnóstico"""
        try:
            model_path = self.config.get("path")
            if not model_path or not Path(model_path).exists():
                # Para desenvolvimento, usar modelo simulado
                self.model = self._create_mock_model()
                logger.warning(f"Using mock model for {self.name} - file not found: {model_path}")
            else:
                # Carregar modelo real
                if model_path.endswith('.pkl'):
                    with open(model_path, 'rb') as f:
                        self.model = pickle.load(f)
                elif model_path.endswith('.joblib'):
                    self.model = joblib.load(model_path)
                else:
                    raise ModelLoadError(self.name, f"Unsupported file format: {model_path}")
            
            self.is_loaded = True
            self.load_time = datetime.utcnow()
            
            logger.info(f"Loaded diagnostic model: {self.name}")
            
        except Exception as e:
            raise ModelLoadError(self.name, str(e))
    
    def _create_mock_model(self) -> Dict[str, Any]:
        """Cria modelo simulado para desenvolvimento"""
        return {
            "type": "mock_diagnostic",
            "classes": [
                "Normal", "Pneumonia", "Fratura", "Tumor", "Inflamação",
                "Obstrução", "Calcificação", "Inconclusivo"
            ],
            "confidence_ranges": {
                "Normal": (0.7, 0.95),
                "Pneumonia": (0.8, 0.92),
                "Fratura": (0.85, 0.98),
                "Tumor": (0.75, 0.90),
                "Inflamação": (0.70, 0.88),
                "Obstrução": (0.72, 0.89),
                "Calcificação": (0.80, 0.94),
                "Inconclusivo": (0.5, 0.7)
            }
        }
    
    async def predict(self, input_data: Dict[str, Any]) -> PredictionResult:
        """Executa predição diagnóstica"""
        if not self.is_loaded:
            await self.load()
        
        self.usage_count += 1
        
        try:
            # Pré-processar dados
            processed_input = self.preprocess(input_data)
            
            # Executar inferência
            if isinstance(self.model, dict) and self.model.get("type") == "mock_diagnostic":
                raw_output = self._mock_predict(processed_input, input_data)
            else:
                # Inferência real do modelo
                raw_output = self.model.predict(processed_input)
            
            # Pós-processar resultado
            result = self.postprocess(raw_output, input_data)
            
            return result
            
        except Exception as e:
            raise InferenceError(self.name, str(e))
    
    def preprocess(self, input_data: Dict[str, Any]) -> Any:
        """Pré-processa dados para diagnóstico"""
        # Extrair características relevantes
        features = {
            "exam_type": input_data.get("exam_type", "unknown"),
            "patient_age": input_data.get("patient_age", 0),
            "symptoms": len(input_data.get("symptoms", [])),
            "has_findings": bool(input_data.get("findings", "")),
            "has_measurements": bool(input_data.get("measurements", {})),
            "file_count": len(input_data.get("file_paths", []))
        }
        
        # Em produção, aqui seria feita normalização e feature engineering
        return features
    
    def postprocess(self, raw_output: Any, input_data: Dict[str, Any]) -> PredictionResult:
        """Pós-processa resultado do diagnóstico"""
        if isinstance(raw_output, dict):
            # Resultado do modelo mock
            prediction = raw_output["prediction"]
            confidence = raw_output["confidence"]
            probabilities = raw_output["probabilities"]
            features = raw_output.get("features", [])
        else:
            # Resultado de modelo real
            prediction = str(raw_output[0]) if len(raw_output) > 0 else "Inconclusivo"
            confidence = float(raw_output[1]) if len(raw_output) > 1 else 0.5
            probabilities = {"primary": confidence, "others": 1 - confidence}
            features = []
        
        # Adicionar metadados
        metadata = {
            "model_name": self.name,
            "model_type": "diagnostic",
            "exam_type": input_data.get("exam_type"),
            "processing_time": datetime.utcnow().isoformat(),
            "input_features": list(input_data.keys())
        }
        
        return PredictionResult(
            prediction=prediction,
            confidence=confidence,
            probabilities=probabilities,
            features=features,
            metadata=metadata
        )
    
    def _mock_predict(self, processed_input: Dict[str, Any], original_input: Dict[str, Any]) -> Dict[str, Any]:
        """Predição simulada para desenvolvimento"""
        import random
        
        # Selecionar diagnóstico baseado em heurísticas simples
        exam_type = original_input.get("exam_type", "unknown")
        patient_age = original_input.get("patient_age", 30)
        symptoms = original_input.get("symptoms", [])
        findings = original_input.get("findings", "")
        
        # Lógica simplificada para demonstração
        if "pneumonia" in findings.lower() or any("pneumonia" in str(s).lower() for s in symptoms):
            prediction = "Pneumonia"
        elif "fratura" in findings.lower() or exam_type == "xray":
            prediction = "Fratura" if random.random() > 0.6 else "Normal"
        elif patient_age > 60 and random.random() > 0.7:
            prediction = random.choice(["Tumor", "Calcificação", "Normal"])
        elif exam_type == "blood_test":
            prediction = random.choice(["Normal", "Inflamação", "Inconclusivo"])
        else:
            prediction = random.choice(["Normal", "Inconclusivo"])
        
        # Gerar confiança baseada no diagnóstico
        confidence_range = self.model["confidence_ranges"].get(prediction, (0.5, 0.8))
        confidence = random.uniform(*confidence_range)
        
        # Gerar probabilidades para outras classes
        other_classes = [c for c in self.model["classes"] if c != prediction]
        remaining_prob = 1 - confidence
        other_probs = np.random.dirichlet(np.ones(len(other_classes))) * remaining_prob
        
        probabilities = {prediction: confidence}
        for i, class_name in enumerate(other_classes):
            probabilities[class_name] = float(other_probs[i])
        
        # Gerar características detectadas
        features = []
        if prediction != "Normal":
            features.append({
                "name": f"Característica indicativa de {prediction}",
                "confidence": confidence * 0.9,
                "location": "região central" if exam_type in ["xray", "ct_scan"] else "amostra"
            })
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
            "features": features
        }


class MultiPathologyModel(BaseMLModel):
    """Modelo para detecção de múltiplas patologias"""
    
    async def load(self) -> None:
        """Carrega modelo multi-patologia"""
        try:
            model_path = self.config.get("path")
            if not model_path or not Path(model_path).exists():
                self.model = self._create_mock_model()
                logger.warning(f"Using mock multi-pathology model for {self.name}")
            else:
                # Carregar modelo real
                self.model = joblib.load(model_path)
            
            self.is_loaded = True
            self.load_time = datetime.utcnow()
            
            logger.info(f"Loaded multi-pathology model: {self.name}")
            
        except Exception as e:
            raise ModelLoadError(self.name, str(e))
    
    def _create_mock_model(self) -> Dict[str, Any]:
        """Cria modelo mock para múltiplas patologias"""
        return {
            "type": "mock_multi_pathology",
            "pathologies": [
                "Pneumonia", "Derrame pleural", "Pneumotórax", "Atelectasia",
                "Edema pulmonar", "Fibrose", "Nódulo pulmonar", "Calcificação"
            ],
            "max_pathologies": 3
        }
    
    async def predict(self, input_data: Dict[str, Any]) -> PredictionResult:
        """Executa predição multi-patologia"""
        if not self.is_loaded:
            await self.load()
        
        self.usage_count += 1
        
        try:
            processed_input = self.preprocess(input_data)
            
            if isinstance(self.model, dict) and self.model.get("type") == "mock_multi_pathology":
                raw_output = self._mock_predict_multi(processed_input, input_data)
            else:
                raw_output = self.model.predict(processed_input)
            
            result = self.postprocess(raw_output, input_data)
            return result
            
        except Exception as e:
            raise InferenceError(self.name, str(e))
    
    def preprocess(self, input_data: Dict[str, Any]) -> Any:
        """Pré-processa dados para multi-patologia"""
        return {
            "exam_type": input_data.get("exam_type"),
            "body_part": input_data.get("body_part"),
            "patient_age": input_data.get("patient_age", 0),
            "contrast_used": input_data.get("contrast_used", False),
            "symptoms_count": len(input_data.get("symptoms", [])),
            "files_available": len(input_data.get("file_paths", []))
        }
    
    def postprocess(self, raw_output: Any, input_data: Dict[str, Any]) -> PredictionResult:
        """Pós-processa resultado multi-patologia"""
        if isinstance(raw_output, dict):
            pathologies = raw_output["pathologies"]
            overall_confidence = raw_output["overall_confidence"]
            individual_confidences = raw_output["individual_confidences"]
            features = raw_output.get("features", [])
        else:
            pathologies = ["Inconclusivo"]
            overall_confidence = 0.5
            individual_confidences = {"Inconclusivo": 0.5}
            features = []
        
        # Criar resultado consolidado
        if len(pathologies) == 1:
            prediction = pathologies[0]
        elif len(pathologies) > 1:
            prediction = f"Múltiplas patologias: {', '.join(pathologies)}"
        else:
            prediction = "Normal"
        
        metadata = {
            "model_name": self.name,
            "model_type": "multi_pathology",
            "pathologies_detected": len(pathologies),
            "individual_confidences": individual_confidences
        }
        
        return PredictionResult(
            prediction=prediction,
            confidence=overall_confidence,
            probabilities=individual_confidences,
            features=features,
            metadata=metadata
        )
    
    def _mock_predict_multi(self, processed_input: Dict[str, Any], original_input: Dict[str, Any]) -> Dict[str, Any]:
        """Predição mock para múltiplas patologias"""
        import random
        
        # Simular detecção de múltiplas patologias
        available_pathologies = self.model["pathologies"]
        max_pathologies = self.model["max_pathologies"]
        
        # Decidir quantas patologias detectar
        num_pathologies = random.choices(
            range(0, max_pathologies + 1),
            weights=[0.4, 0.3, 0.2, 0.1]  # Mais provável ter 0-1 patologias
        )[0]
        
        detected_pathologies = []
        individual_confidences = {}
        
        if num_pathologies > 0:
            detected_pathologies = random.sample(available_pathologies, num_pathologies)
            
            for pathology in detected_pathologies:
                confidence = random.uniform(0.6, 0.9)
                individual_confidences[pathology] = confidence
        
        # Calcular confiança geral
        if detected_pathologies:
            overall_confidence = sum(individual_confidences.values()) / len(individual_confidences)
        else:
            overall_confidence = random.uniform(0.8, 0.95)  # Alta confiança para "normal"
            individual_confidences["Normal"] = overall_confidence
        
        # Gerar características
        features = []
        for pathology in detected_pathologies:
            features.append({
                "pathology": pathology,
                "confidence": individual_confidences[pathology],
                "location": f"Região associada a {pathology}",
                "size": random.choice(["pequeno", "médio", "grande"])
            })
        
        return {
            "pathologies": detected_pathologies if detected_pathologies else ["Normal"],
            "overall_confidence": overall_confidence,
            "individual_confidences": individual_confidences,
            "features": features
        }


class ValidationModel(BaseMLModel):
    """Modelo para validação de qualidade de exames"""
    
    async def load(self) -> None:
        """Carrega modelo de validação"""
        try:
            # Para este modelo, usar lógica baseada em regras
            self.model = self._create_validation_rules()
            self.is_loaded = True
            self.load_time = datetime.utcnow()
            
            logger.info(f"Loaded validation model: {self.name}")
            
        except Exception as e:
            raise ModelLoadError(self.name, str(e))
    
    def _create_validation_rules(self) -> Dict[str, Any]:
        """Cria regras de validação"""
        return {
            "type": "validation_rules",
            "quality_factors": [
                "image_resolution", "contrast_quality", "positioning",
                "artifacts", "completeness", "technical_parameters"
            ],
            "quality_thresholds": {
                "excellent": 0.9,
                "good": 0.75,
                "acceptable": 0.6,
                "poor": 0.4
            }
        }
    
    async def predict(self, input_data: Dict[str, Any]) -> PredictionResult:
        """Executa validação de qualidade"""
        if not self.is_loaded:
            await self.load()
        
        self.usage_count += 1
        
        try:
            processed_input = self.preprocess(input_data)
            quality_assessment = self._assess_quality(processed_input, input_data)
            result = self.postprocess(quality_assessment, input_data)
            
            return result
            
        except Exception as e:
            raise InferenceError(self.name, str(e))
    
    def preprocess(self, input_data: Dict[str, Any]) -> Any:
        """Pré-processa dados para validação"""
        return {
            "has_files": bool(input_data.get("file_paths")),
            "file_count": len(input_data.get("file_paths", [])),
            "has_measurements": bool(input_data.get("measurements")),
            "has_findings": bool(input_data.get("findings")),
            "exam_type": input_data.get("exam_type"),
            "technical_params": input_data.get("model_config", {})
        }
    
    def postprocess(self, quality_assessment: Dict[str, Any], input_data: Dict[str, Any]) -> PredictionResult:
        """Pós-processa resultado de validação"""
        quality_score = quality_assessment["overall_score"]
        quality_level = quality_assessment["quality_level"]
        issues = quality_assessment["issues"]
        
        # Determinar se é válido para diagnóstico
        is_valid = quality_score >= 0.6
        
        prediction = f"Qualidade {quality_level}" + ("" if is_valid else " - Não recomendado para diagnóstico")
        
        probabilities = {
            "excellent": quality_assessment["scores"]["excellent"],
            "good": quality_assessment["scores"]["good"],
            "acceptable": quality_assessment["scores"]["acceptable"],
            "poor": quality_assessment["scores"]["poor"]
        }
        
        features = [
            {
                "factor": factor,
                "score": score,
                "acceptable": score >= 0.6
            }
            for factor, score in quality_assessment["factor_scores"].items()
        ]
        
        metadata = {
            "model_name": self.name,
            "model_type": "validation",
            "is_valid_for_diagnosis": is_valid,
            "quality_issues": issues,
            "recommendations": quality_assessment.get("recommendations", [])
        }
        
        return PredictionResult(
            prediction=prediction,
            confidence=quality_score,
            probabilities=probabilities,
            features=features,
            metadata=metadata
        )
    
    def _assess_quality(self, processed_input: Dict[str, Any], original_input: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia qualidade do exame"""
        import random
        
        # Simular avaliação de qualidade
        factor_scores = {}
        issues = []
        recommendations = []
        
        # Avaliar cada fator
        base_score = 0.8  # Score base
        
        # Penalizar falta de arquivos
        if not processed_input["has_files"]:
            factor_scores["completeness"] = 0.3
            issues.append("Nenhum arquivo de exame encontrado")
            recommendations.append("Anexar arquivos do exame")
        else:
            factor_scores["completeness"] = random.uniform(0.7, 0.95)
        
        # Avaliar baseado no tipo de exame
        exam_type = processed_input["exam_type"]
        if exam_type in ["xray", "ct_scan", "mri"]:
            # Exames de imagem precisam de boa qualidade
            factor_scores["image_quality"] = random.uniform(0.6, 0.9)
            factor_scores["positioning"] = random.uniform(0.7, 0.95)
            factor_scores["artifacts"] = random.uniform(0.8, 0.95)
        else:
            # Outros tipos de exame
            factor_scores["technical_quality"] = random.uniform(0.7, 0.9)
            factor_scores["data_integrity"] = random.uniform(0.8, 0.95)
        
        # Verificar medições
        if processed_input["has_measurements"]:
            factor_scores["measurements"] = random.uniform(0.8, 0.95)
        else:
            factor_scores["measurements"] = random.uniform(0.5, 0.7)
            if exam_type in ["ultrasound", "ct_scan"]:
                recommendations.append("Incluir medições quando possível")
        
        # Calcular score geral
        overall_score = sum(factor_scores.values()) / len(factor_scores)
        
        # Determinar nível de qualidade
        thresholds = self.model["quality_thresholds"]
        if overall_score >= thresholds["excellent"]:
            quality_level = "excelente"
        elif overall_score >= thresholds["good"]:
            quality_level = "boa"
        elif overall_score >= thresholds["acceptable"]:
            quality_level = "aceitável"
        else:
            quality_level = "ruim"
            issues.append("Qualidade geral insuficiente para diagnóstico confiável")
            recommendations.append("Repetir exame com melhor qualidade técnica")
        
        # Calcular probabilidades para cada nível
        scores = {}
        for level, threshold in thresholds.items():
            scores[level] = max(0, min(1, overall_score - threshold + 0.1))
        
        return {
            "overall_score": overall_score,
            "quality_level": quality_level,
            "factor_scores": factor_scores,
            "scores": scores,
            "issues": issues,
            "recommendations": recommendations
        }


class MLModelService:
    """Serviço principal de gerenciamento de modelos ML"""
    
    def __init__(self):
        self.models: Dict[str, BaseMLModel] = {}
        self.validation_service = ValidationService()
        self.logger = logger
        
        # Configurações
        self.max_models_in_memory = 3
        self.model_timeout = timedelta(hours=2)
        
        # Mapeamento de tipos para classes
        self.model_classes = {
            "diagnostic": DiagnosticModel,
            "multi_pathology": MultiPathologyModel,
            "validation": ValidationModel
        }
    
    async def load_model(self, model_name: str) -> BaseMLModel:
        """
        Carrega modelo especificado
        
        Args:
            model_name: Nome do modelo para carregar
            
        Returns:
            Modelo carregado
            
        Raises:
            ModelNotFoundError: Modelo não encontrado na configuração
            ModelLoadError: Erro ao carregar modelo
        """
        if model_name not in ML_CONFIG:
            raise ModelNotFoundError(model_name)
        
        # Verificar se já está carregado
        if model_name in self.models and self.models[model_name].is_loaded:
            return self.models[model_name]
        
        # Carregar modelo
        config = ML_CONFIG[model_name]
        model_type = config.get("type", "diagnostic")
        
        if model_type not in self.model_classes:
            raise ModelLoadError(model_name, f"Unknown model type: {model_type}")
        
        model_class = self.model_classes[model_type]
        model = model_class(model_name, config)
        
        await model.load()
        
        # Gerenciar memória
        await self._manage_memory()
        
        self.models[model_name] = model
        
        self.logger.info(f"Successfully loaded model: {model_name}")
        return model
    
    @log_ai_operation("prediction", "model_service")
    async def predict(self, model_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa predição com modelo especificado
        
        Args:
            model_name: Nome do modelo
            input_data: Dados de entrada
            
        Returns:
            Resultado da predição
        """
        # Validar dados de entrada
        if not input_data:
            raise InferenceError(model_name, "Input data is empty")
        
        # Carregar modelo se necessário
        model = await self.load_model(model_name)
        
        # Executar predição
        result = await model.predict(input_data)
        
        # Converter resultado para dicionário compatível
        prediction_dict = {
            "prediction": result.prediction,
            "confidence": result.confidence,
            "probabilities": result.probabilities,
            "features": result.features,
            "metadata": result.metadata
        }
        
        # Adicionar campos específicos baseado no tipo de modelo
        model_type = ML_CONFIG[model_name].get("type", "diagnostic")
        
        if model_type == "diagnostic":
            prediction_dict.update({
                "differential_diagnoses": self._extract_differential_diagnoses(result),
                "findings": self._extract_findings(result),
                "interpretation": self._generate_interpretation(result, input_data),
                "recommendations": self._generate_recommendations(result, input_data)
            })
        elif model_type == "multi_pathology":
            prediction_dict.update({
                "pathologies": result.metadata.get("pathologies_detected", 0),
                "individual_confidences": result.metadata.get("individual_confidences", {}),
                "anomalies": self._extract_anomalies(result),
                "measurements": self._extract_measurements(result, input_data)
            })
        elif model_type == "validation":
            prediction_dict.update({
                "quality_score": result.confidence,
                "is_valid": result.metadata.get("is_valid_for_diagnosis", False),
                "issues": result.metadata.get("quality_issues", []),
                "recommendations": result.metadata.get("recommendations", [])
            })
        
        return prediction_dict
    
    async def get_model_info(self, model_name: str) -> ModelInfo:
        """
        Retorna informações de um modelo
        
        Args:
            model_name: Nome do modelo
            
        Returns:
            Informações do modelo
        """
        if model_name not in ML_CONFIG:
            raise ModelNotFoundError(model_name)
        
        if model_name in self.models:
            return self.models[model_name].get_info()
        else:
            # Modelo não carregado - criar info básica
            config = ML_CONFIG[model_name]
            model_path = Path(config.get("path", ""))
            size_mb = model_path.stat().st_size / (1024 * 1024) if model_path.exists() else 0
            
            return ModelInfo(
                name=model_name,
                version=config.get("version", "unknown"),
                type=config.get("type", "unknown"),
                path=str(model_path),
                size_mb=round(size_mb, 2),
                loaded_at=None,
                last_used=None,
                usage_count=0,
                performance_metrics=config.get("performance_metrics", {})
            )
    
    async def list_available_models(self) -> List[ModelInfo]:
        """
        Lista todos os modelos disponíveis
        
        Returns:
            Lista de informações de modelos
        """
        models_info = []
        for model_name in ML_CONFIG.keys():
            try:
                info = await self.get_model_info(model_name)
                models_info.append(info)
            except Exception as e:
                self.logger.error(f"Error getting info for model {model_name}: {e}")
        
        return models_info
    
    async def unload_model(self, model_name: str) -> bool:
        """
        Descarrega modelo da memória
        
        Args:
            model_name: Nome do modelo
            
        Returns:
            True se descarregado com sucesso
        """
        if model_name in self.models:
            self.models[model_name].unload()
            del self.models[model_name]
            self.logger.info(f"Unloaded model: {model_name}")
            return True
        
        return False
    
    async def _manage_memory(self) -> None:
        """Gerencia memória descarregando modelos antigos"""
        if len(self.models) >= self.max_models_in_memory:
            # Encontrar modelo mais antigo para descarregar
            oldest_model = None
            oldest_time = datetime.utcnow()
            
            for name, model in self.models.items():
                if model.load_time and model.load_time < oldest_time:
                    oldest_time = model.load_time
                    oldest_model = name
            
            if oldest_model:
                await self.unload_model(oldest_model)
    
    def _extract_differential_diagnoses(self, result: PredictionResult) -> List[Dict[str, Any]]:
        """Extrai diagnósticos diferenciais do resultado"""
        differentials = []
        
        # Usar probabilidades para criar diagnósticos diferenciais
        sorted_probs = sorted(result.probabilities.items(), key=lambda x: x[1], reverse=True)
        
        # Pular o primeiro (diagnóstico principal)
        for diagnosis, prob in sorted_probs[1:4]:  # Top 3 diferenciais
            if prob > 0.1:  # Apenas probabilidades significativas
                differentials.append({
                    "diagnosis": diagnosis,
                    "confidence": prob,
                    "reasoning": f"Probabilidade significativa: {prob:.1%}"
                })
        
        return differentials
    
    def _extract_findings(self, result: PredictionResult) -> List[Dict[str, Any]]:
        """Extrai achados do resultado"""
        findings = []
        
        for feature in result.features:
            findings.append({
                "description": feature.get("name", "Achado detectado"),
                "confidence": feature.get("confidence", 0.5),
                "location": feature.get("location", "Não especificado"),
                "severity": "normal" if result.confidence > 0.8 else "abnormal"
            })
        
        return findings
    
    def _extract_anomalies(self, result: PredictionResult) -> List[Dict[str, Any]]:
        """Extrai anomalias do resultado"""
        anomalies = []
        
        for feature in result.features:
            if feature.get("pathology"):
                anomalies.append({
                    "type": feature["pathology"],
                    "description": f"Possível {feature['pathology']} detectada",
                    "severity": feature.get("size", "indeterminado"),
                    "location": feature.get("location", "Não especificado")
                })
        
        return anomalies
    
    def _extract_measurements(self, result: PredictionResult, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai medições do resultado"""
        measurements = input_data.get("measurements", {}).copy()
        
        # Adicionar medições calculadas pelo modelo
        for feature in result.features:
            if feature.get("size"):
                measurements[f"size_{feature.get('pathology', 'finding')}"] = feature["size"]
        
        return measurements
    
    def _generate_interpretation(self, result: PredictionResult, input_data: Dict[str, Any]) -> str:
        """Gera interpretação do resultado"""
        exam_type = input_data.get("exam_type", "exame")
        confidence_text = "alta" if result.confidence > 0.8 else "moderada" if result.confidence > 0.6 else "baixa"
        
        interpretation = f"Análise de {exam_type} sugere: {result.prediction} (confiança {confidence_text}: {result.confidence:.1%})"
        
        if result.features:
            interpretation += f". Foram identificadas {len(result.features)} características relevantes."
        
        if result.confidence < 0.7:
            interpretation += " Recomenda-se revisão médica devido à confiança limitada."
        
        return interpretation
    
    def _generate_recommendations(self, result: PredictionResult, input_data: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas no resultado"""
        recommendations = []
        
        if result.confidence > 0.9:
            recommendations.append("Resultado com alta confiança")
        elif result.confidence < 0.7:
            recommendations.append("Considerar repetir exame ou análise adicional")
            recommendations.append("Revisão médica recomendada")
        
        if result.prediction != "Normal" and result.prediction != "Inconclusivo":
            recommendations.append("Acompanhamento médico recomendado")
            recommendations.append("Considerar exames complementares se indicado")
        
        # Recomendações específicas por tipo
        exam_type = input_data.get("exam_type")
        if exam_type == "xray" and "fratura" in result.prediction.lower():
            recommendations.append("Imobilização da área afetada")
        elif exam_type == "blood_test" and "inflamação" in result.prediction.lower():
            recommendations.append("Monitorar marcadores inflamatórios")
        
        return recommendations