"""
Serviço de modelos de Machine Learning
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from app.core.config import settings
from app.core.constants import ExamType, DiagnosticStatus
from app.schemas.ml_model import (
    MLModelCreate,
    MLModelUpdate,
    PredictionRequest,
    PredictionResponse,
    ModelMetrics
)

logger = logging.getLogger(__name__)


class MLModelService:
    """Serviço para gerenciamento de modelos de ML"""
    
    def __init__(self):
        self.models_dir = Path(settings.ML_MODELS_DIR)
        self.models_dir.mkdir(exist_ok=True)
        self.loaded_models = {}
        self.scalers = {}
        
    def load_model(self, model_name: str, exam_type: ExamType) -> Any:
        """Carrega um modelo do disco"""
        try:
            model_path = self.models_dir / f"{exam_type.value}_{model_name}.pkl"
            
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                self.loaded_models[f"{exam_type.value}_{model_name}"] = model
                logger.info(f"Modelo {model_name} para {exam_type.value} carregado com sucesso")
                return model
            else:
                logger.warning(f"Modelo {model_name} para {exam_type.value} não encontrado")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            raise
    
    def save_model(self, model: Any, model_name: str, exam_type: ExamType) -> bool:
        """Salva um modelo no disco"""
        try:
            model_path = self.models_dir / f"{exam_type.value}_{model_name}.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
                
            logger.info(f"Modelo {model_name} para {exam_type.value} salvo com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {str(e)}")
            return False
    
    def train_model(
        self,
        data: pd.DataFrame,
        target_column: str,
        exam_type: ExamType,
        model_name: str,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Treina um novo modelo"""
        try:
            # Preparar dados
            X = data.drop(columns=[target_column])
            y = data[target_column]
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # Normalizar dados
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Treinar modelo
            model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            y_pred = model.predict(X_test_scaled)
            
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average='weighted'),
                "recall": recall_score(y_test, y_pred, average='weighted'),
                "f1_score": f1_score(y_test, y_pred, average='weighted')
            }
            
            # Salvar modelo e scaler
            self.save_model(model, model_name, exam_type)
            self.save_scaler(scaler, model_name, exam_type)
            
            # Manter em memória
            model_key = f"{exam_type.value}_{model_name}"
            self.loaded_models[model_key] = model
            self.scalers[model_key] = scaler
            
            return {
                "success": True,
                "metrics": metrics,
                "model_name": model_name,
                "exam_type": exam_type.value,
                "trained_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def predict(
        self,
        model_name: str,
        exam_type: ExamType,
        features: Dict[str, Any]
    ) -> PredictionResponse:
        """Realiza predição usando um modelo"""
        try:
            model_key = f"{exam_type.value}_{model_name}"
            
            # Carregar modelo se não estiver em memória
            if model_key not in self.loaded_models:
                model = self.load_model(model_name, exam_type)
                if not model:
                    raise ValueError(f"Modelo {model_name} não encontrado")
            else:
                model = self.loaded_models[model_key]
            
            # Carregar scaler
            if model_key not in self.scalers:
                scaler = self.load_scaler(model_name, exam_type)
                if scaler:
                    self.scalers[model_key] = scaler
            
            # Preparar features
            feature_array = self._prepare_features(features, exam_type)
            
            # Normalizar se scaler disponível
            if model_key in self.scalers:
                feature_array = self.scalers[model_key].transform([feature_array])
            else:
                feature_array = [feature_array]
            
            # Predição
            prediction = model.predict(feature_array)[0]
            probabilities = model.predict_proba(feature_array)[0]
            
            # Preparar resposta
            response = PredictionResponse(
                prediction=str(prediction),
                confidence=float(max(probabilities)),
                probabilities={
                    str(cls): float(prob)
                    for cls, prob in zip(model.classes_, probabilities)
                },
                model_name=model_name,
                exam_type=exam_type.value,
                status=DiagnosticStatus.COMPLETED,
                processed_at=datetime.utcnow()
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erro na predição: {str(e)}")
            raise
    
    def _prepare_features(
        self,
        features: Dict[str, Any],
        exam_type: ExamType
    ) -> np.ndarray:
        """Prepara features para predição baseado no tipo de exame"""
        if exam_type == ExamType.ECG:
            # Processar dados de ECG
            return self._prepare_ecg_features(features)
        elif exam_type == ExamType.BLOOD_TEST:
            # Processar exame de sangue
            return self._prepare_blood_test_features(features)
        elif exam_type == ExamType.XRAY:
            # Processar raio-X
            return self._prepare_xray_features(features)
        else:
            # Processar outros tipos
            return np.array(list(features.values()))
    
    def _prepare_ecg_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepara features específicas de ECG"""
        # Extrair características do ECG
        ecg_features = []
        
        # Taxa cardíaca
        if 'heart_rate' in features:
            ecg_features.append(features['heart_rate'])
        else:
            # Calcular a partir dos dados brutos se disponível
            if 'raw_data' in features:
                raw_data = np.array(features['raw_data'])
                # Simplificação: usar frequência de amostragem padrão
                if exam_type == ExamType.ECG:
                    target_sample_rate = 500
                else:
                    target_sample_rate = 250
                
                heart_rate = self._calculate_heart_rate(raw_data, target_sample_rate)
                ecg_features.append(heart_rate)
        
        # Intervalos
        for interval in ['pr_interval', 'qrs_duration', 'qt_interval']:
            if interval in features:
                ecg_features.append(features[interval])
        
        # Amplitudes
        for amplitude in ['p_wave_amplitude', 'qrs_amplitude', 't_wave_amplitude']:
            if amplitude in features:
                ecg_features.append(features[amplitude])
        
        # Variabilidade da frequência cardíaca
        if 'hrv' in features:
            ecg_features.append(features['hrv'])
        
        return np.array(ecg_features)
    
    def _prepare_blood_test_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepara features específicas de exame de sangue"""
        blood_features = []
        
        # Hemograma
        hemogram_params = [
            'hemoglobin', 'hematocrit', 'red_cells', 'white_cells',
            'platelets', 'mcv', 'mch', 'mchc'
        ]
        
        for param in hemogram_params:
            if param in features:
                blood_features.append(features[param])
        
        # Bioquímica
        biochemistry_params = [
            'glucose', 'urea', 'creatinine', 'cholesterol_total',
            'hdl', 'ldl', 'triglycerides', 'ast', 'alt'
        ]
        
        for param in biochemistry_params:
            if param in features:
                blood_features.append(features[param])
        
        return np.array(blood_features)
    
    def _prepare_xray_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepara features específicas de raio-X"""
        xray_features = []
        
        # Features extraídas da imagem
        image_features = [
            'lung_density', 'heart_size', 'mediastinum_width',
            'diaphragm_position', 'bone_density'
        ]
        
        for feature in image_features:
            if feature in features:
                xray_features.append(features[feature])
        
        # Presença de padrões
        patterns = [
            'infiltrate', 'consolidation', 'nodule',
            'mass', 'cavity', 'calcification'
        ]
        
        for pattern in patterns:
            if pattern in features:
                # Converter booleano para numérico
                xray_features.append(1 if features[pattern] else 0)
        
        return np.array(xray_features)
    
    def _calculate_heart_rate(self, ecg_signal: np.ndarray, sample_rate: int) -> float:
        """Calcula frequência cardíaca a partir do sinal ECG"""
        # Implementação simplificada
        # Em produção, usar algoritmo mais robusto (ex: Pan-Tompkins)
        
        # Detectar picos R (simplificado)
        threshold = np.mean(ecg_signal) + 2 * np.std(ecg_signal)
        peaks = np.where(ecg_signal > threshold)[0]
        
        if len(peaks) < 2:
            return 60.0  # Valor padrão
        
        # Calcular intervalos RR
        rr_intervals = np.diff(peaks) / sample_rate
        
        # Frequência cardíaca média
        if len(rr_intervals) > 0:
            mean_rr = np.mean(rr_intervals)
            heart_rate = 60.0 / mean_rr
            return np.clip(heart_rate, 40, 200)  # Limitar a valores fisiológicos
        
        return 60.0
    
    def save_scaler(self, scaler: StandardScaler, model_name: str, exam_type: ExamType) -> bool:
        """Salva o scaler do modelo"""
        try:
            scaler_path = self.models_dir / f"{exam_type.value}_{model_name}_scaler.pkl"
            
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar scaler: {str(e)}")
            return False
    
    def load_scaler(self, model_name: str, exam_type: ExamType) -> Optional[StandardScaler]:
        """Carrega o scaler do modelo"""
        try:
            scaler_path = self.models_dir / f"{exam_type.value}_{model_name}_scaler.pkl"
            
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    return pickle.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao carregar scaler: {str(e)}")
            return None
    
    def get_model_info(self, model_name: str, exam_type: ExamType) -> Dict[str, Any]:
        """Obtém informações sobre um modelo"""
        model_path = self.models_dir / f"{exam_type.value}_{model_name}.pkl"
        
        if not model_path.exists():
            return {"exists": False}
        
        model_key = f"{exam_type.value}_{model_name}"
        
        # Carregar modelo se necessário
        if model_key not in self.loaded_models:
            self.load_model(model_name, exam_type)
        
        model = self.loaded_models.get(model_key)
        
        if model:
            info = {
                "exists": True,
                "name": model_name,
                "exam_type": exam_type.value,
                "type": type(model).__name__,
                "created_at": datetime.fromtimestamp(model_path.stat().st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(model_path.stat().st_mtime).isoformat(),
                "size_bytes": model_path.stat().st_size
            }
            
            # Adicionar informações específicas do modelo
            if hasattr(model, 'n_estimators'):
                info['n_estimators'] = model.n_estimators
            if hasattr(model, 'feature_importances_'):
                info['n_features'] = len(model.feature_importances_)
            
            return info
        
        return {"exists": False}
    
    def list_models(self, exam_type: Optional[ExamType] = None) -> List[Dict[str, Any]]:
        """Lista todos os modelos disponíveis"""
        models = []
        
        for model_file in self.models_dir.glob("*.pkl"):
            if model_file.name.endswith("_scaler.pkl"):
                continue
                
            parts = model_file.stem.split("_", 1)
            if len(parts) == 2:
                file_exam_type, model_name = parts
                
                if exam_type and file_exam_type != exam_type.value:
                    continue
                
                try:
                    exam_type_enum = ExamType(file_exam_type)
                    model_info = self.get_model_info(model_name, exam_type_enum)
                    if model_info.get("exists"):
                        models.append(model_info)
                except ValueError:
                    logger.warning(f"Tipo de exame inválido: {file_exam_type}")
        
        return models
    
    def delete_model(self, model_name: str, exam_type: ExamType) -> bool:
        """Remove um modelo"""
        try:
            # Remover arquivos
            model_path = self.models_dir / f"{exam_type.value}_{model_name}.pkl"
            scaler_path = self.models_dir / f"{exam_type.value}_{model_name}_scaler.pkl"
            
            if model_path.exists():
                model_path.unlink()
            
            if scaler_path.exists():
                scaler_path.unlink()
            
            # Remover da memória
            model_key = f"{exam_type.value}_{model_name}"
            
            if model_key in self.loaded_models:
                del self.loaded_models[model_key]
            
            if model_key in self.scalers:
                del self.scalers[model_key]
            
            logger.info(f"Modelo {model_name} para {exam_type.value} removido com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover modelo: {str(e)}")
            return False
    
    def evaluate_model(
        self,
        model_name: str,
        exam_type: ExamType,
        test_data: pd.DataFrame,
        target_column: str
    ) -> ModelMetrics:
        """Avalia um modelo com dados de teste"""
        try:
            model_key = f"{exam_type.value}_{model_name}"
            
            # Carregar modelo
            if model_key not in self.loaded_models:
                model = self.load_model(model_name, exam_type)
                if not model:
                    raise ValueError(f"Modelo {model_name} não encontrado")
            else:
                model = self.loaded_models[model_key]
            
            # Preparar dados
            X_test = test_data.drop(columns=[target_column])
            y_test = test_data[target_column]
            
            # Normalizar se scaler disponível
            if model_key in self.scalers:
                X_test = self.scalers[model_key].transform(X_test)
            
            # Predições
            y_pred = model.predict(X_test)
            
            # Calcular métricas
            metrics = ModelMetrics(
                accuracy=accuracy_score(y_test, y_pred),
                precision=precision_score(y_test, y_pred, average='weighted'),
                recall=recall_score(y_test, y_pred, average='weighted'),
                f1_score=f1_score(y_test, y_pred, average='weighted'),
                model_name=model_name,
                exam_type=exam_type.value,
                evaluated_at=datetime.utcnow()
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao avaliar modelo: {str(e)}")
            raise