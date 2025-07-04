"""
Enhanced ML Model Service Tests - 100% Coverage Implementation
"""

import pytest
import numpy as np
import tempfile
import os
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import pickle

from app.services.ml_model_service import MLModelService
from app.core.constants import ModelStatus, ModelType, AnalysisStatus
from app.core.exceptions import MLModelException

class TestMLModelServiceCritical:
    """Critical tests for ML Model Service - 100% coverage required."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_model_registry(self):
        """Mock model registry."""
        registry = Mock()
        registry.get_model.return_value = {
            "id": "model_v2.0",
            "type": ModelType.ECG_CLASSIFIER,
            "version": "2.0",
            "status": ModelStatus.ACTIVE,
            "accuracy": 0.98,
            "path": "/models/ecg_classifier_v2.onnx"
        }
        return registry

    @pytest.fixture
    def ml_service(self, mock_db_session, mock_model_registry):
        """ML Model service instance."""
        service = MLModelService(mock_db_session)
        service.model_registry = mock_model_registry
        return service

    @pytest.fixture
    def sample_ecg_features(self):
        """Generate sample ECG features for model input."""
        return {
            "temporal_features": np.random.rand(50),
            "frequency_features": np.random.rand(30),
            "morphological_features": np.random.rand(20)
        }

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_loading_and_initialization(self, ml_service):
        """Test model loading and initialization process."""
        # Mock model file
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp:
            # Simulate ONNX model content
            tmp.write(b"ONNX_MODEL_CONTENT")
            model_path = tmp.name

        try:
            # Mock ONNX runtime
            with patch('onnxruntime.InferenceSession') as mock_session:
                mock_session.return_value.get_inputs.return_value = [
                    Mock(name='input', shape=[1, 100])
                ]
                mock_session.return_value.get_outputs.return_value = [
                    Mock(name='output', shape=[1, 5])
                ]
                
                # Load model
                result = await ml_service.load_model(model_path, ModelType.ECG_CLASSIFIER)
                
                assert result["status"] == "loaded"
                assert result["model_type"] == ModelType.ECG_CLASSIFIER
                assert "load_time" in result
                mock_session.assert_called_once_with(model_path)
        finally:
            os.unlink(model_path)

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_ecg_classification_normal(self, ml_service, sample_ecg_features):
        """Test ECG classification for normal rhythm."""
        # Mock model inference
        ml_service.models = {
            # Mock models dictionary - empty for this test
        }
        
        # Mock prediction - Normal Sinus Rhythm
        mock_output = np.array([[0.95, 0.02, 0.01, 0.01, 0.01]])  # [normal, af, vt, svt, other]
        ml_service.models[ModelType.ECG_CLASSIFIER].run.return_value = [mock_output]
        
        # Classify
        result = await ml_service.classify_ecg(sample_ecg_features)
        
        assert result["primary_diagnosis"] == "Normal Sinus Rhythm"
        assert result["confidence"] >= 0.95
        assert result["predictions"]["normal"] == 0.95
        assert result["clinical_significance"] == "benign"

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_ecg_classification_atrial_fibrillation(self, ml_service, sample_ecg_features):
        """Test ECG classification for atrial fibrillation."""
        # Mock model inference
        ml_service.models = {
            # Mock models dictionary - empty for this test
        }
        
        # Mock prediction - Atrial Fibrillation
        mock_output = np.array([[0.05, 0.89, 0.03, 0.02, 0.01]])
        ml_service.models[ModelType.ECG_CLASSIFIER].run.return_value = [mock_output]
        
        # Classify
        result = await ml_service.classify_ecg(sample_ecg_features)
        
        assert result["primary_diagnosis"] == "Atrial Fibrillation"
        assert result["confidence"] >= 0.89
        assert result["predictions"]["atrial_fibrillation"] == 0.89
        assert result["clinical_significance"] == "requires_attention"
        assert result["recommended_actions"] is not None

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_multi_model_ensemble(self, ml_service):
        """Test ensemble prediction using multiple models."""
        # Setup multiple models
        models = {
            "model1": Mock(),
            "model2": Mock(),
            "model3": Mock()
        }
        
        # Different predictions from each model
        models["model1"].run.return_value = [np.array([[0.8, 0.1, 0.1]])]
        models["model2"].run.return_value = [np.array([[0.85, 0.1, 0.05]])]
        models["model3"].run.return_value = [np.array([[0.75, 0.15, 0.1]])]
        
        ml_service.ensemble_models = models
        
        # Run ensemble
        result = await ml_service.ensemble_predict(
            sample_ecg_features,
            voting_method="soft"
        )
        
        # Check ensemble result (average of predictions)
        assert result["ensemble_prediction"]["normal"] == pytest.approx(0.8, rel=0.1)
        assert result["model_agreement"] > 0.8
        assert len(result["individual_predictions"]) == 3

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_versioning_and_fallback(self, ml_service):
        """Test model versioning and fallback mechanisms."""
        # Primary model fails
        primary_model = Mock()
        primary_model.run.side_effect = Exception("Model inference failed")
        
        # Fallback model works
        fallback_model = Mock()
        fallback_model.run.return_value = [np.array([[0.9, 0.1]])]
        
        ml_service.models = {
            "primary": primary_model,
            "fallback": fallback_model
        }
        
        # Test fallback
        result = await ml_service.classify_with_fallback(sample_ecg_features)
        
        assert result["model_used"] == "fallback"
        assert result["fallback_reason"] == "primary_model_failure"
        assert result["predictions"] is not None

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_performance_monitoring(self, ml_service):
        """Test model performance monitoring and metrics."""
        # Setup metrics tracking
        ml_service.metrics_collector = Mock()
        
        # Perform multiple predictions
        for i in range(100):
            features = np.random.rand(100)
            
            # Mock varying inference times
            inference_time = 0.01 + (i % 10) * 0.002
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [0, inference_time]
                
                await ml_service.predict_with_metrics(features)
        
        # Check metrics
        metrics = ml_service.get_performance_metrics()
        
        assert metrics["total_predictions"] == 100
        assert metrics["average_inference_time"] < 0.05  # 50ms
        assert metrics["p95_inference_time"] < 0.1  # 100ms
        assert "predictions_per_second" in metrics

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_input_validation_and_preprocessing(self, ml_service):
        """Test input validation and preprocessing."""
        # Test valid input
        valid_input = np.random.rand(100)
        processed = await ml_service.preprocess_input(valid_input)
        assert processed.shape == (1, 100)
        assert processed.dtype == np.float32
        
        # Test invalid inputs
        invalid_inputs = [
            np.array([]),  # Empty
            np.random.rand(50),  # Wrong shape
            None,  # None
            "not_an_array"  # Wrong type
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                await ml_service.validate_input(invalid_input)

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_output_postprocessing(self, ml_service):
        """Test model output postprocessing and interpretation."""
        # Raw model output
        raw_output = np.array([[0.1, 0.7, 0.15, 0.05]])
        
        # Process output
        processed = await ml_service.postprocess_output(
            raw_output,
            class_names=["normal", "af", "vt", "other"]
        )
        
        assert processed["primary_class"] == "af"
        assert processed["primary_probability"] == 0.7
        assert processed["confidence_calibrated"] <= 0.7  # Calibration reduces overconfidence
        assert len(processed["all_probabilities"]) == 4
        assert sum(processed["all_probabilities"].values()) == pytest.approx(1.0)

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_explainability(self, ml_service):
        """Test model explainability features."""
        # Mock SHAP or LIME explainer
        with patch('shap.Explainer') as mock_explainer:
            mock_shap_values = Mock()
            mock_shap_values.values = np.random.rand(100)
            mock_explainer.return_value.return_value = mock_shap_values
            
            # Get explanations
            explanations = await ml_service.explain_prediction(
                input_features=np.random.rand(100),
                prediction={"class": "af", "probability": 0.85}
            )
            
            assert "feature_importance" in explanations
            assert "top_features" in explanations
            assert len(explanations["top_features"]) <= 10
            assert "explanation_method" in explanations
            assert explanations["explanation_method"] == "SHAP"

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_batch_inference(self, ml_service):
        """Test batch inference capabilities."""
        # Create batch of inputs
        batch_size = 32
        batch_inputs = [np.random.rand(100) for _ in range(batch_size)]
        
        # Mock batch processing
        ml_service.models = {
            # Mock models dictionary - empty for this test
        }
        
        # Mock batch output
        batch_output = np.random.rand(batch_size, 5)
        ml_service.models[ModelType.ECG_CLASSIFIER].run.return_value = [batch_output]
        
        # Process batch
        results = await ml_service.batch_classify(batch_inputs)
        
        assert len(results) == batch_size
        assert all("primary_diagnosis" in r for r in results)
        assert all("confidence" in r for r in results)

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_update_and_deployment(self, ml_service, mock_model_registry):
        """Test model update and deployment process."""
        # New model metadata
        new_model = {
            "id": "model_v3.0",
            "version": "3.0",
            "path": "/models/ecg_classifier_v3.onnx",
            "validation_metrics": {
                "accuracy": 0.99,
                "sensitivity": 0.98,
                "specificity": 0.99
            }
        }
        
        # Mock validation
        ml_service.validate_model = AsyncMock(return_value=True)
        
        # Deploy new model
        deployment_result = await ml_service.deploy_model(new_model)
        
        assert deployment_result["status"] == "deployed"
        assert deployment_result["previous_version"] == "2.0"
        assert deployment_result["rollback_available"] is True
        
        # Verify model registry updated
        mock_model_registry.update_active_model.assert_called_once()

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_validation(self, ml_service):
        """Test model validation before deployment."""
        # Create test dataset
        test_data = {
            "inputs": [np.random.rand(100) for _ in range(100)],
            "labels": np.random.randint(0, 5, 100)
        }
        
        # Mock model predictions
        predictions = np.random.randint(0, 5, 100)
        ml_service.predict_batch = AsyncMock(return_value=predictions)
        
        # Validate model
        validation_result = await ml_service.validate_model_performance(
            test_data,
            minimum_accuracy=0.95
        )
        
        assert "accuracy" in validation_result
        assert "confusion_matrix" in validation_result
        assert "per_class_metrics" in validation_result
        assert validation_result["meets_threshold"] is not None

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_error_handling(self, ml_service):
        """Test comprehensive error handling in model service."""
        # Test model not loaded error
        ml_service.models = {}
        
        with pytest.raises(MLModelException, match="Model not loaded"):
            await ml_service.classify_ecg(np.random.rand(100))
        
        # Test inference error
        ml_service.models = {ModelType.ECG_CLASSIFIER: Mock()}
        ml_service.models[ModelType.ECG_CLASSIFIER].run.side_effect = RuntimeError("ONNX error")
        
        with pytest.raises(MLModelException, match="Inference failed"):
            await ml_service.classify_ecg(np.random.rand(100))

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_caching(self, ml_service):
        """Test model prediction caching."""
        # Enable caching
        ml_service.enable_caching = True
        ml_service.cache = {}
        
        # Mock model
        ml_service.models = {ModelType.ECG_CLASSIFIER: Mock()}
        ml_service.models[ModelType.ECG_CLASSIFIER].run.return_value = [
            np.array([[0.9, 0.1]])
        ]
        
        # First prediction
        input_data = np.random.rand(100)
        result1 = await ml_service.classify_ecg_with_cache(input_data)
        
        # Second prediction with same input
        result2 = await ml_service.classify_ecg_with_cache(input_data)
        
        # Model should only be called once
        ml_service.models[ModelType.ECG_CLASSIFIER].run.assert_called_once()
        
        # Results should be identical
        assert result1 == result2

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_resource_management(self, ml_service):
        """Test model resource management and cleanup."""
        # Load multiple models
        models_to_load = [
            ("model1.onnx", ModelType.ECG_CLASSIFIER),
            ("model2.onnx", ModelType.ARRHYTHMIA_DETECTOR),
            ("model3.onnx", ModelType.RISK_PREDICTOR)
        ]
        
        for model_path, model_type in models_to_load:
            with patch('onnxruntime.InferenceSession'):
                await ml_service.load_model(model_path, model_type)
        
        # Check memory usage
        memory_usage = ml_service.get_memory_usage()
        assert memory_usage["total_models"] == 3
        assert memory_usage["total_memory_mb"] > 0
        
        # Unload models
        await ml_service.cleanup_models()
        
        # Verify cleanup
        assert len(ml_service.models) == 0
        assert ml_service.get_memory_usage()["total_memory_mb"] == 0

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_a_b_testing(self, ml_service):
        """Test A/B testing framework for models."""
        # Setup A/B test
        model_a = Mock()
        model_b = Mock()
        
        model_a.run.return_value = [np.array([[0.9, 0.1]])]
        model_b.run.return_value = [np.array([[0.85, 0.15]])]
        
        ml_service.ab_test_config = {
            "model_a": {"model": model_a, "traffic": 0.5},
            "model_b": {"model": model_b, "traffic": 0.5}
        }
        
        # Run predictions and track which model was used
        model_usage = {"model_a": 0, "model_b": 0}
        
        for _ in range(100):
            result = await ml_service.predict_with_ab_test(np.random.rand(100))
            model_usage[result["model_used"]] += 1
        
        # Check distribution (should be roughly 50/50)
        assert 40 <= model_usage["model_a"] <= 60
        assert 40 <= model_usage["model_b"] <= 60

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_model_drift_detection(self, ml_service):
        """Test model drift detection capabilities."""
        # Baseline distribution
        baseline_predictions = np.random.normal(0.8, 0.1, 1000)
        
        # Current distribution (with drift)
        current_predictions = np.random.normal(0.6, 0.15, 100)
        
        # Detect drift
        drift_result = await ml_service.detect_model_drift(
            baseline_predictions,
            current_predictions,
            threshold=0.05
        )
        
        assert drift_result["drift_detected"] is True
        assert drift_result["drift_score"] > 0.05
        assert "statistical_test" in drift_result
        assert "recommendation" in drift_result

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_federated_learning_support(self, ml_service):
        """Test federated learning model update support."""
        # Mock local model updates from different sites
        site_updates = [
            {"site_id": "hospital_a", "gradients": np.random.rand(100)},
            {"site_id": "hospital_b", "gradients": np.random.rand(100)},
            {"site_id": "hospital_c", "gradients": np.random.rand(100)}
        ]
        
        # Aggregate updates
        aggregated = await ml_service.aggregate_federated_updates(site_updates)
        
        assert aggregated["num_sites"] == 3
        assert aggregated["aggregation_method"] == "federated_averaging"
        assert "global_update" in aggregated
        assert aggregated["global_update"].shape == (100)

    @pytest.mark.critical
    async def test_model_compression(self, ml_service):
        """Test model compression for edge deployment."""
        # Mock full model
        full_model = Mock()
        full_model.size = 100 * 1024 * 1024  # 100 MB
        
        # Compress model
        compressed = await ml_service.compress_model(
            full_model,
            compression_type="quantization",
            target_size_mb=10
        )
        
        assert compressed["size_mb"] <= 10
        assert compressed["compression_ratio"] >= 10
        assert compressed["accuracy_loss"] < 0.02  # Less than 2% accuracy loss
        assert compressed["inference_speedup"] > 1.5  # At least 1.5x faster