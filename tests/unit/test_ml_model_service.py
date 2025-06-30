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
