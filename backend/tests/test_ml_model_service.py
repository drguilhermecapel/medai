"""
Testes abrangentes para o serviço de modelos ML
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock, mock_open
import pickle
from pathlib import Path
from datetime import datetime
import tempfile
import os
import shutil

from app.services.ml_model_service import MLModelService
from app.core.constants import ExamType, DiagnosticStatus
from app.schemas.ml_model import (
    PredictionRequest,
    PredictionResponse,
    ModelMetrics
)


@pytest.fixture
def ml_service():
    """Fixture para criar instância do serviço ML"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('app.core.config.settings.ML_MODELS_DIR', temp_dir):
            service = MLModelService()
            yield service


@pytest.fixture
def sample_model():
    """Fixture para criar modelo de exemplo"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    
    X, y = make_classification(n_samples=100, n_features=10, n_classes=2, random_state=42)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model


@pytest.fixture
def sample_scaler():
    """Fixture para criar scaler de exemplo"""
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    data = np.random.randn(100, 10)
    scaler.fit(data)
    return scaler


@pytest.fixture
def sample_dataframe():
    """Fixture para criar DataFrame de exemplo"""
    np.random.seed(42)
    
    data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'target': np.random.randint(0, 2, 100)
    }
    
    return pd.DataFrame(data)


class TestMLModelServiceInitialization:
    """Testes para inicialização do serviço"""
    
    def test_service_initialization(self, ml_service):
        """Testa inicialização básica do serviço"""
        assert ml_service is not None
        assert isinstance(ml_service.loaded_models, dict)
        assert isinstance(ml_service.scalers, dict)
        assert ml_service.models_dir.exists()
    
    def test_models_directory_creation(self):
        """Testa criação do diretório de modelos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_path = Path(temp_dir) / "ml_models"
            
            with patch('app.core.config.settings.ML_MODELS_DIR', str(models_path)):
                service = MLModelService()
                assert models_path.exists()
                assert models_path.is_dir()


class TestMLModelServiceSaveLoad:
    """Testes para salvar e carregar modelos"""
    
    def test_save_model_success(self, ml_service, sample_model):
        """Testa salvamento bem-sucedido de modelo"""
        model_name = "test_model"
        exam_type = ExamType.ECG
        
        result = ml_service.save_model(sample_model, model_name, exam_type)
        
        assert result is True
        expected_path = ml_service.models_dir / f"{exam_type.value}_{model_name}.pkl"
        assert expected_path.exists()
    
    def test_save_model_failure(self, ml_service, sample_model):
        """Testa falha no salvamento de modelo"""
        model_name = "test_model"
        exam_type = ExamType.ECG
        
        # Torna o diretório somente leitura
        ml_service.models_dir.chmod(0o444)
        
        try:
            result = ml_service.save_model(sample_model, model_name, exam_type)
            assert result is False
        finally:
            # Restaura permissões
            ml_service.models_dir.chmod(0o755)
    
    def test_load_model_success(self, ml_service, sample_model):
        """Testa carregamento bem-sucedido de modelo"""
        model_name = "test_model"
        exam_type = ExamType.ECG
        
        # Salva modelo primeiro
        ml_service.save_model(sample_model, model_name, exam_type)
        
        # Limpa cache
        ml_service.loaded_models.clear()
        
        # Carrega modelo
        loaded_model = ml_service.load_model(model_name, exam_type)
        
        assert loaded_model is not None
        assert hasattr(loaded_model, 'predict')
        assert f"{exam_type.value}_{model_name}" in ml_service.loaded_models
    
    def test_load_nonexistent_model(self, ml_service):
        """Testa carregamento de modelo não existente"""
        model = ml_service.load_model("nonexistent", ExamType.ECG)
        assert model is None
    
    def test_load_corrupted_model(self, ml_service):
        """Testa carregamento de modelo corrompido"""
        model_name = "corrupted"
        exam_type = ExamType.ECG
        
        # Cria arquivo corrompido
        model_path = ml_service.models_dir / f"{exam_type.value}_{model_name}.pkl"
        with open(model_path, 'wb') as f:
            f.write(b"corrupted data")
        
        with pytest.raises(Exception):
            ml_service.load_model(model_name, exam_type)
    
    def test_save_and_load_scaler(self, ml_service, sample_scaler):
        """Testa salvamento e carregamento de scaler"""
        model_name = "test_model"
        exam_type = ExamType.BLOOD_TEST
        
        # Salva scaler
        result = ml_service.save_scaler(sample_scaler, model_name, exam_type)
        assert result is True
        
        # Carrega scaler
        loaded_scaler = ml_service.load_scaler(model_name, exam_type)
        assert loaded_scaler is not None
        assert hasattr(loaded_scaler, 'transform')


class TestMLModelServiceTraining:
    """Testes para treinamento de modelos"""
    
    def test_train_model_success(self, ml_service, sample_dataframe):
        """Testa treinamento bem-sucedido de modelo"""
        result = ml_service.train_model(
            data=sample_dataframe,
            target_column='target',
            exam_type=ExamType.BLOOD_TEST,
            model_name='test_classifier',
            test_size=0.2
        )
        
        assert result['success'] is True
        assert 'metrics' in result
        assert 'accuracy' in result['metrics']
        assert result['metrics']['accuracy'] > 0.5
        assert 'precision' in result['metrics']
        assert 'recall' in result['metrics']
        assert 'f1_score' in result['metrics']
    
    def test_train_model_with_invalid_target(self, ml_service, sample_dataframe):
        """Testa treinamento com coluna alvo inválida"""
        result = ml_service.train_model(
            data=sample_dataframe,
            target_column='nonexistent_column',
            exam_type=ExamType.BLOOD_TEST,
            model_name='test_classifier'
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_train_model_with_small_dataset(self, ml_service):
        """Testa treinamento com dataset pequeno"""
        small_data = pd.DataFrame({
            'feature1': [1, 2, 3],
            'target': [0, 1, 0]
        })
        
        result = ml_service.train_model(
            data=small_data,
            target_column='target',
            exam_type=ExamType.ECG,
            model_name='small_model'
        )
        
        # Deve falhar ou ter métricas baixas devido ao tamanho pequeno
        if result['success']:
            assert result['metrics']['accuracy'] <= 1.0
    
    def test_train_model_saves_artifacts(self, ml_service, sample_dataframe):
        """Testa se o treinamento salva modelo e scaler"""
        model_name = 'artifacts_test'
        exam_type = ExamType.XRAY
        
        result = ml_service.train_model(
            data=sample_dataframe,
            target_column='target',
            exam_type=exam_type,
            model_name=model_name
        )
        
        assert result['success'] is True
        
        # Verifica se arquivos foram criados
        model_path = ml_service.models_dir / f"{exam_type.value}_{model_name}.pkl"
        scaler_path = ml_service.models_dir / f"{exam_type.value}_{model_name}_scaler.pkl"
        
        assert model_path.exists()
        assert scaler_path.exists()
        
        # Verifica se estão em memória
        model_key = f"{exam_type.value}_{model_name}"
        assert model_key in ml_service.loaded_models
        assert model_key in ml_service.scalers


class TestMLModelServicePrediction:
    """Testes para predição"""
    
    def test_predict_with_trained_model(self, ml_service, sample_dataframe):
        """Testa predição com modelo treinado"""
        # Treina modelo primeiro
        model_name = 'predict_test'
        exam_type = ExamType.BLOOD_TEST
        
        train_result = ml_service.train_model(
            data=sample_dataframe,
            target_column='target',
            exam_type=exam_type,
            model_name=model_name
        )
        
        assert train_result['success'] is True
        
        # Faz predição
        features = {
            'feature1': 0.5,
            'feature2': -0.3,
            'feature3': 1.2
        }
        
        prediction = ml_service.predict(model_name, exam_type, features)
        
        assert isinstance(prediction, PredictionResponse)
        assert prediction.prediction in ['0', '1']
        assert 0 <= prediction.confidence <= 1
        assert prediction.status == DiagnosticStatus.COMPLETED
        assert len(prediction.probabilities) == 2
    
    def test_predict_with_nonexistent_model(self, ml_service):
        """Testa predição com modelo não existente"""
        with pytest.raises(ValueError, match="não encontrado"):
            ml_service.predict(
                "nonexistent_model",
                ExamType.ECG,
                {'feature1': 1.0}
            )
    
    def test_predict_loads_model_on_demand(self, ml_service, sample_model, sample_scaler):
        """Testa carregamento de modelo sob demanda durante predição"""
        model_name = 'lazy_load'
        exam_type = ExamType.CT_SCAN
        
        # Salva modelo e scaler
        ml_service.save_model(sample_model, model_name, exam_type)
        ml_service.save_scaler(sample_scaler, model_name, exam_type)
        
        # Limpa cache
        ml_service.loaded_models.clear()
        ml_service.scalers.clear()
        
        # Faz predição (deve carregar modelo)
        features = {f'feature{i}': np.random.randn() for i in range(10)}
        
        prediction = ml_service.predict(model_name, exam_type, features)
        
        assert isinstance(prediction, PredictionResponse)
        
        # Verifica se foi carregado
        model_key = f"{exam_type.value}_{model_name}"
        assert model_key in ml_service.loaded_models
        assert model_key in ml_service.scalers


class TestMLModelServiceFeaturePreparation:
    """Testes para preparação de features"""
    
    def test_prepare_ecg_features(self, ml_service):
        """Testa preparação de features de ECG"""
        features = {
            'heart_rate': 75,
            'pr_interval': 160,
            'qrs_duration': 100,
            'qt_interval': 400,
            'p_wave_amplitude': 0.1,
            'qrs_amplitude': 1.2,
            't_wave_amplitude': 0.3,
            'hrv': 50
        }
        
        prepared = ml_service._prepare_ecg_features(features)
        
        assert isinstance(prepared, np.ndarray)
        assert len(prepared) == 8
        assert prepared[0] == 75  # heart_rate
    
    def test_prepare_ecg_features_with_raw_data(self, ml_service):
        """Testa preparação de features ECG com dados brutos"""
        # Simula sinal ECG com picos
        raw_data = np.zeros(5000)
        # Adiciona picos simulados
        for i in range(0, 5000, 500):  # 10 picos em 10 segundos
            raw_data[i] = 2.0
        
        features = {'raw_data': raw_data.tolist()}
        
        prepared = ml_service._prepare_ecg_features(features)
        
        assert isinstance(prepared, np.ndarray)
        assert len(prepared) > 0
        # Deve incluir heart_rate calculado
        assert prepared[0] > 40 and prepared[0] < 200
    
    def test_prepare_blood_test_features(self, ml_service):
        """Testa preparação de features de exame de sangue"""
        features = {
            'hemoglobin': 14.5,
            'hematocrit': 42.0,
            'red_cells': 4.8,
            'white_cells': 7.5,
            'platelets': 250,
            'glucose': 90,
            'cholesterol_total': 180,
            'hdl': 50,
            'ldl': 100,
            'triglycerides': 120
        }
        
        prepared = ml_service._prepare_blood_test_features(features)
        
        assert isinstance(prepared, np.ndarray)
        assert len(prepared) > 0
        assert all(isinstance(x, (int, float)) for x in prepared)
    
    def test_prepare_xray_features(self, ml_service):
        """Testa preparação de features de raio-X"""
        features = {
            'lung_density': 0.85,
            'heart_size': 0.45,
            'mediastinum_width': 0.3,
            'infiltrate': True,
            'consolidation': False,
            'nodule': True
        }
        
        prepared = ml_service._prepare_xray_features(features)
        
        assert isinstance(prepared, np.ndarray)
        assert len(prepared) == 6
        assert prepared[3] == 1  # infiltrate = True
        assert prepared[4] == 0  # consolidation = False
    
    def test_prepare_generic_features(self, ml_service):
        """Testa preparação de features genéricas"""
        features = {
            'feature1': 1.5,
            'feature2': -0.3,
            'feature3': 2.7
        }
        
        # Para tipo de exame não específico
        prepared = ml_service._prepare_features(features, ExamType.MRI)
        
        assert isinstance(prepared, np.ndarray)
        assert len(prepared) == 3
        assert list(prepared) == [1.5, -0.3, 2.7]


class TestMLModelServiceHeartRateCalculation:
    """Testes para cálculo de frequência cardíaca"""
    
    def test_calculate_heart_rate_normal(self, ml_service):
        """Testa cálculo de frequência cardíaca normal"""
        # Simula ECG com 10 batimentos em 10 segundos (60 bpm)
        sample_rate = 500
        duration = 10
        n_samples = sample_rate * duration
        
        ecg_signal = np.zeros(n_samples)
        # Adiciona picos R a cada segundo
        for i in range(10):
            ecg_signal[i * sample_rate] = 3.0
        
        heart_rate = ml_service._calculate_heart_rate(ecg_signal, sample_rate)
        
        assert 55 <= heart_rate <= 65  # Tolerância para 60 bpm
    
    def test_calculate_heart_rate_tachycardia(self, ml_service):
        """Testa cálculo de frequência cardíaca alta"""
        sample_rate = 500
        ecg_signal = np.zeros(5000)
        
        # Adiciona 20 picos em 10 segundos (120 bpm)
        for i in range(20):
            ecg_signal[i * 250] = 3.0
        
        heart_rate = ml_service._calculate_heart_rate(ecg_signal, sample_rate)
        
        assert 110 <= heart_rate <= 130
    
    def test_calculate_heart_rate_no_peaks(self, ml_service):
        """Testa cálculo com sinal sem picos"""
        ecg_signal = np.ones(5000) * 0.1  # Sinal plano
        
        heart_rate = ml_service._calculate_heart_rate(ecg_signal, 500)
        
        assert heart_rate == 60.0  # Valor padrão
    
    def test_calculate_heart_rate_clipping(self, ml_service):
        """Testa limitação de valores fisiológicos"""
        # Sinal com picos muito frequentes
        ecg_signal = np.zeros(5000)
        for i in range(0, 5000, 50):  # 100 picos
            ecg_signal[i] = 3.0
        
        heart_rate = ml_service._calculate_heart_rate(ecg_signal, 500)
        
        assert heart_rate <= 200  # Máximo fisiológico


class TestMLModelServiceModelManagement:
    """Testes para gerenciamento de modelos"""
    
    def test_get_model_info_existing(self, ml_service, sample_model):
        """Testa obtenção de informações de modelo existente"""
        model_name = 'info_test'
        exam_type = ExamType.ECG
        
        ml_service.save_model(sample_model, model_name, exam_type)
        
        info = ml_service.get_model_info(model_name, exam_type)
        
        assert info['exists'] is True
        assert info['name'] == model_name
        assert info['exam_type'] == exam_type.value
        assert info['type'] == 'RandomForestClassifier'
        assert 'created_at' in info
        assert 'modified_at' in info
        assert info['size_bytes'] > 0
        assert info['n_estimators'] == sample_model.n_estimators
    
    def test_get_model_info_nonexistent(self, ml_service):
        """Testa obtenção de informações de modelo não existente"""
        info = ml_service.get_model_info('nonexistent', ExamType.ECG)
        
        assert info['exists'] is False
        assert len(info) == 1
    
    def test_list_models_all(self, ml_service, sample_model):
        """Testa listagem de todos os modelos"""
        # Salva vários modelos
        models_data = [
            ('model1', ExamType.ECG),
            ('model2', ExamType.ECG),
            ('model3', ExamType.BLOOD_TEST),
            ('model4', ExamType.XRAY)
        ]
        
        for model_name, exam_type in models_data:
            ml_service.save_model(sample_model, model_name, exam_type)
        
        all_models = ml_service.list_models()
        
        assert len(all_models) == 4
        assert all(model['exists'] for model in all_models)
    
    def test_list_models_by_exam_type(self, ml_service, sample_model):
        """Testa listagem filtrada por tipo de exame"""
        # Salva modelos de diferentes tipos
        ml_service.save_model(sample_model, 'ecg1', ExamType.ECG)
        ml_service.save_model(sample_model, 'ecg2', ExamType.ECG)
        ml_service.save_model(sample_model, 'blood1', ExamType.BLOOD_TEST)
        
        ecg_models = ml_service.list_models(ExamType.ECG)
        
        assert len(ecg_models) == 2
        assert all(m['exam_type'] == 'ecg' for m in ecg_models)
    
    def test_delete_model_success(self, ml_service, sample_model, sample_scaler):
        """Testa remoção bem-sucedida de modelo"""
        model_name = 'delete_test'
        exam_type = ExamType.MRI
        
        # Salva modelo e scaler
        ml_service.save_model(sample_model, model_name, exam_type)
        ml_service.save_scaler(sample_scaler, model_name, exam_type)
        
        # Carrega em memória
        ml_service.load_model(model_name, exam_type)
        ml_service.load_scaler(model_name, exam_type)
        
        # Remove modelo
        result = ml_service.delete_model(model_name, exam_type)
        
        assert result is True
        
        # Verifica remoção de arquivos
        model_path = ml_service.models_dir / f"{exam_type.value}_{model_name}.pkl"
        scaler_path = ml_service.models_dir / f"{exam_type.value}_{model_name}_scaler.pkl"
        
        assert not model_path.exists()
        assert not scaler_path.exists()
        
        # Verifica remoção da memória
        model_key = f"{exam_type.value}_{model_name}"
        assert model_key not in ml_service.loaded_models
        assert model_key not in ml_service.scalers
    
    def test_delete_nonexistent_model(self, ml_service):
        """Testa remoção de modelo não existente"""
        result = ml_service.delete_model('nonexistent', ExamType.ECG)
        assert result is True  # Não falha, apenas retorna True


class TestMLModelServiceEvaluation:
    """Testes para avaliação de modelos"""
    
    def test_evaluate_model_success(self, ml_service, sample_dataframe):
        """Testa avaliação bem-sucedida de modelo"""
        # Treina modelo
        model_name = 'eval_test'
        exam_type = ExamType.BLOOD_TEST
        
        train_result = ml_service.train_model(
            data=sample_dataframe.iloc[:80],  # 80% para treino
            target_column='target',
            exam_type=exam_type,
            model_name=model_name
        )
        
        assert train_result['success'] is True
        
        # Avalia com dados de teste
        test_data = sample_dataframe.iloc[80:].copy()  # 20% para teste
        
        metrics = ml_service.evaluate_model(
            model_name=model_name,
            exam_type=exam_type,
            test_data=test_data,
            target_column='target'
        )
        
        assert isinstance(metrics, ModelMetrics)
        assert 0 <= metrics.accuracy <= 1
        assert 0 <= metrics.precision <= 1
        assert 0 <= metrics.recall <= 1
        assert 0 <= metrics.f1_score <= 1
        assert metrics.model_name == model_name
        assert metrics.exam_type == exam_type.value
        assert isinstance(metrics.evaluated_at, datetime)
    
    def test_evaluate_nonexistent_model(self, ml_service, sample_dataframe):
        """Testa avaliação de modelo não existente"""
        with pytest.raises(ValueError, match="não encontrado"):
            ml_service.evaluate_model(
                model_name='nonexistent',
                exam_type=ExamType.ECG,
                test_data=sample_dataframe,
                target_column='target'
            )
    
    def test_evaluate_model_with_scaler(self, ml_service, sample_dataframe):
        """Testa avaliação de modelo com normalização"""
        # Treina modelo com dados normalizados
        model_name = 'scaler_eval'
        exam_type = ExamType.XRAY
        
        # Adiciona mais variabilidade aos dados
        sample_dataframe['feature1'] *= 100
        sample_dataframe['feature2'] *= 50
        
        train_result = ml_service.train_model(
            data=sample_dataframe.iloc[:80],
            target_column='target',
            exam_type=exam_type,
            model_name=model_name
        )
        
        assert train_result['success'] is True
        
        # Avalia
        test_data = sample_dataframe.iloc[80:].copy()
        
        metrics = ml_service.evaluate_model(
            model_name=model_name,
            exam_type=exam_type,
            test_data=test_data,
            target_column='target'
        )
        
        assert isinstance(metrics, ModelMetrics)
        # Verifica que o scaler foi usado
        model_key = f"{exam_type.value}_{model_name}"
        assert model_key in ml_service.scalers


class TestMLModelServiceEdgeCases:
    """Testes para casos extremos"""
    
    def test_empty_features_dict(self, ml_service):
        """Testa com dicionário de features vazio"""
        features = {}
        
        # ECG sem features
        ecg_features = ml_service._prepare_ecg_features(features)
        assert isinstance(ecg_features, np.ndarray)
        assert len(ecg_features) == 0
        
        # Blood test sem features
        blood_features = ml_service._prepare_blood_test_features(features)
        assert isinstance(blood_features, np.ndarray)
        assert len(blood_features) == 0
    
    def test_partial_features(self, ml_service):
        """Testa com features parciais"""
        # ECG com apenas algumas features
        ecg_features = {
            'heart_rate': 75,
            'pr_interval': 160
            # Faltam outras features
        }
        
        prepared = ml_service._prepare_ecg_features(ecg_features)
        assert len(prepared) == 2
        
        # Blood test com features parciais
        blood_features = {
            'hemoglobin': 14.5,
            'glucose': 90
            # Faltam outras features
        }
        
        prepared = ml_service._prepare_blood_test_features(blood_features)
        assert len(prepared) == 2
    
    def test_train_with_single_class(self, ml_service):
        """Testa treinamento com apenas uma classe"""
        single_class_data = pd.DataFrame({
            'feature1': np.random.randn(50),
            'feature2': np.random.randn(50),
            'target': [0] * 50  # Apenas classe 0
        })
        
        result = ml_service.train_model(
            data=single_class_data,
            target_column='target',
            exam_type=ExamType.ECG,
            model_name='single_class'
        )
        
        # Pode ter sucesso mas com métricas específicas
        if result['success']:
            # Com uma única classe, algumas métricas podem ser indefinidas
            assert 'metrics' in result
    
    @patch('pickle.dump')
    def test_save_model_with_pickle_error(self, mock_dump, ml_service, sample_model):
        """Testa salvamento com erro de serialização"""
        mock_dump.side_effect = Exception("Pickle error")
        
        result = ml_service.save_model(sample_model, 'error_test', ExamType.ECG)
        
        assert result is False
    
    def test_concurrent_model_access(self, ml_service, sample_model):
        """Testa acesso concorrente a modelos"""
        model_name = 'concurrent_test'
        exam_type = ExamType.ECG
        
        # Salva modelo
        ml_service.save_model(sample_model, model_name, exam_type)
        
        # Simula acesso concorrente
        model_key = f"{exam_type.value}_{model_name}"
        
        # Carrega em memória
        ml_service.load_model(model_name, exam_type)
        
        # Acessa o mesmo modelo várias vezes
        for _ in range(5):
            assert model_key in ml_service.loaded_models
            model = ml_service.loaded_models[model_key]
            assert model is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services.ml_model_service", "--cov-report=term-missing"])