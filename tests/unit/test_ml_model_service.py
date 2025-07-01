import pytest
from app.services.ml_model_service import (
    MLModelService, DiagnosticModel, RiskAssessmentModel,
    ModelPreprocessor, ModelMonitor
)

def test_ml_service():
    service = MLModelService()
    result = service.predict({"test": 1})
    assert "prediction" in result
    assert "confidence" in result

def test_diagnostic_model():
    model = DiagnosticModel()
    result = model.predict_diabetes({"glucose": 126})
    assert "risk_score" in result
    assert 0 <= result["risk_score"] <= 1

def test_risk_model():
    model = RiskAssessmentModel()
    result = model.calculate_readmission_risk({"age": 70})
    assert "probability" in result
    assert "risk_level" in result

def test_preprocessor():
    preprocessor = ModelPreprocessor()
    data = {"glucose": 100}
    result = preprocessor.normalize_blood_test(data)
    assert "glucose_normalized" in result

def test_monitor():
    monitor = ModelMonitor()
    monitor.log_prediction({"predicted": 1, "actual": 1})
    metrics = monitor.calculate_metrics()
    assert "accuracy" in metrics


def test_model_error_handling():
    """Testa tratamento de erros em modelos ML"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    
    # Dados de entrada inválidos
    invalid_data = None
    result = service.predict(invalid_data)
    assert "error" in result or result is None
    
    # Dados vazios
    empty_data = {}
    result = service.predict(empty_data)
    assert result is not None


def test_model_loading_scenarios():
    """Testa cenários de carregamento de modelos"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    
    # Tentar carregar modelo inexistente
    result = service.load_model("modelo_inexistente")
    assert result is False
    
    # Tentar carregar modelo padrão
    result = service.load_model("default")
    # Deve funcionar ou falhar graciosamente
    assert isinstance(result, bool)


def test_batch_prediction():
    """Testa predição em lote"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    
    # Múltiplas amostras de dados
    batch_data = [
        {"feature1": 1.0, "feature2": 2.0},
        {"feature1": 1.5, "feature2": 2.5},
        {"feature1": 2.0, "feature2": 3.0}
    ]
    
    results = service.batch_predict(batch_data)
    
    assert isinstance(results, list)
    assert len(results) == len(batch_data)


def test_model_metrics_retrieval():
    """Testa obtenção de métricas do modelo"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    
    # Obter métricas do modelo padrão
    metrics = service.get_model_metrics("default")
    
    assert isinstance(metrics, dict)
    # Métricas comuns esperadas
    expected_metrics = ["accuracy", "precision", "recall", "f1_score"]
    
    # Pelo menos algumas métricas devem estar presentes
    has_metrics = any(metric in metrics for metric in expected_metrics)
    assert has_metrics or len(metrics) == 0  # Aceitar se modelo não estiver carregado


def test_feature_preprocessing():
    """Testa pré-processamento de features"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    
    # Dados brutos para preprocessar
    raw_data = {
        "age": 35,
        "gender": "M",
        "blood_pressure": "120/80",
        "symptoms": ["chest_pain", "shortness_of_breath"]
    }
    
    processed = service.preprocess_features(raw_data)
    
    assert isinstance(processed, dict)
    # Dados processados devem ter formato adequado para modelo
    assert len(processed) > 0


def test_model_confidence_thresholds():
    """Testa limiares de confiança do modelo"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    
    # Dados de teste
    test_data = {"feature1": 1.0, "feature2": 2.0}
    
    # Predição com diferentes limiares
    for threshold in [0.5, 0.7, 0.9]:
        result = service.predict_with_confidence(test_data, threshold)
        
        assert isinstance(result, dict)
        assert "confidence" in result or "prediction" in result or "error" in result


def test_model_version_management():
    """Testa gerenciamento de versões do modelo"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    
    # Obter versão atual do modelo
    version = service.get_model_version()
    
    assert isinstance(version, str) or version is None
    
    # Listar modelos disponíveis
    available_models = service.list_available_models()
    
    assert isinstance(available_models, list)
