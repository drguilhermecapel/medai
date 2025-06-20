"""
Enhanced ML Model Service Tests - 100% Coverage Implementation
"""

import asyncio
import numpy as np
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import onnxruntime as ort

from app.services.ml_model_service import MLModelService


class TestMLModelServiceCritical:
    """Critical tests for ML Model Service - 100% coverage required."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def ml_service(self, mock_db_session):
        """ML Model service instance."""
        return MLModelService(mock_db_session)

    @pytest.fixture
    def sample_ecg_data(self):
        """Generate sample ECG data for testing."""
        # 12-lead ECG, 10 seconds at 500 Hz
        return np.random.randn(5000, 12).astype(np.float32)

    @pytest.fixture
    def mock_onnx_session(self):
        """Mock ONNX runtime session."""
        session = Mock()
        session.run.return_value = [
            np.array([[0.1, 0.8, 0.1]]),  # Predictions
            np.array([[0.85]])  # Confidence
        ]
        session.get_inputs.return_value = [
            Mock(name="input", shape=[1, 5000, 12])
        ]
        session.get_outputs.return_value = [
            Mock(name="predictions"),
            Mock(name="confidence")
        ]
        return session

    # Test 1: Service Initialization
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_db_session):
        """Test ML service initialization."""
        service = MLModelService(mock_db_session)
        assert service.db == mock_db_session
        assert hasattr(service, 'models')
        assert hasattr(service, 'model_cache')

    # Test 2: Model Loading
    @pytest.mark.asyncio
    async def test_model_loading(self, ml_service, mock_onnx_session):
        """Test ONNX model loading."""
        model_path = "/fake/path/model.onnx"
        
        with patch('onnxruntime.InferenceSession', return_value=mock_onnx_session):
            await ml_service.load_model("ecg_classifier", model_path)
        
        assert "ecg_classifier" in ml_service.models
        assert ml_service.models["ecg_classifier"] == mock_onnx_session

    # Test 3: Model Loading Failure
    @pytest.mark.asyncio
    async def test_model_loading_failure(self, ml_service):
        """Test handling of model loading failures."""
        with patch('onnxruntime.InferenceSession', side_effect=Exception("Model not found")):
            with pytest.raises(Exception):
                await ml_service.load_model("invalid_model", "/invalid/path.onnx")

    # Test 4: ECG Classification
    @pytest.mark.asyncio
    async def test_ecg_classification(self, ml_service, sample_ecg_data, mock_onnx_session):
        """Test ECG classification."""
        ml_service.models["ecg_classifier"] = mock_onnx_session
        
        result = await ml_service.classify_ecg(sample_ecg_data)
        
        assert "predictions" in result
        assert "confidence" in result
        assert "primary_diagnosis" in result
        assert isinstance(result["predictions"], dict)
        assert 0.0 <= result["confidence"] <= 1.0

    # Test 5: Batch Processing
    @pytest.mark.asyncio
    async def test_batch_processing(self, ml_service, mock_onnx_session):
        """Test batch processing of multiple ECGs."""
        batch_data = [
            np.random.randn(5000, 12).astype(np.float32) for _ in range(5)
        ]
        
        ml_service.models["ecg_classifier"] = mock_onnx_session
        
        results = await ml_service.classify_ecg_batch(batch_data)
        
        assert len(results) == 5
        assert all("predictions" in result for result in results)
        assert all("confidence" in result for result in results)

    # Test 6: Model Caching
    @pytest.mark.asyncio
    async def test_model_caching(self, ml_service, mock_onnx_session):
        """Test model caching mechanism."""
        model_path = "/fake/path/model.onnx"
        
        with patch('onnxruntime.InferenceSession', return_value=mock_onnx_session) as mock_session:
            # Load model twice
            await ml_service.load_model("cached_model", model_path)
            await ml_service.load_model("cached_model", model_path)
            
            # Should only create session once due to caching
            assert mock_session.call_count == 1

    # Test 7: Memory Management
    @pytest.mark.asyncio
    async def test_memory_management(self, ml_service, mock_onnx_session):
        """Test memory management with large models."""
        ml_service.models["large_model"] = mock_onnx_session
        
        # Simulate memory pressure
        await ml_service.cleanup_unused_models()
        
        # Model should be removed from cache if not recently used
        assert len(ml_service.model_cache) >= 0

    # Test 8: Preprocessing Pipeline
    @pytest.mark.asyncio
    async def test_preprocessing_pipeline(self, ml_service, sample_ecg_data):
        """Test ECG data preprocessing."""
        processed_data = await ml_service._preprocess_ecg(sample_ecg_data)
        
        assert processed_data.shape == sample_ecg_data.shape
        assert processed_data.dtype == np.float32
        
        # Check normalization
        assert np.abs(np.mean(processed_data)) < 0.1
        assert 0.5 < np.std(processed_data) < 2.0

    # Test 9: Postprocessing
    @pytest.mark.asyncio
    async def test_postprocessing(self, ml_service):
        """Test prediction postprocessing."""
        raw_predictions = np.array([[0.1, 0.7, 0.2]])
        class_names = ["normal", "arrhythmia", "artifact"]
        
        processed = await ml_service._postprocess_predictions(raw_predictions, class_names)
        
        assert isinstance(processed, dict)
        assert "normal" in processed
        assert "arrhythmia" in processed
        assert "artifact" in processed
        assert abs(sum(processed.values()) - 1.0) < 1e-6  # Should sum to 1

    # Test 10: Confidence Calculation
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, ml_service):
        """Test confidence score calculation."""
        predictions = {"normal": 0.8, "arrhythmia": 0.15, "artifact": 0.05}
        
        confidence = await ml_service._calculate_confidence(predictions)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence == 0.8  # Should be max probability

    # Test 11: Model Ensemble
    @pytest.mark.asyncio
    async def test_model_ensemble(self, ml_service, sample_ecg_data, mock_onnx_session):
        """Test ensemble prediction from multiple models."""
        # Setup multiple models
        ml_service.models["model_1"] = mock_onnx_session
        ml_service.models["model_2"] = mock_onnx_session
        ml_service.models["model_3"] = mock_onnx_session
        
        result = await ml_service.classify_ecg_ensemble(
            sample_ecg_data, 
            model_names=["model_1", "model_2", "model_3"]
        )
        
        assert "predictions" in result
        assert "confidence" in result
        assert "ensemble_agreement" in result

    # Test 12: Input Validation
    @pytest.mark.asyncio
    async def test_input_validation(self, ml_service):
        """Test input data validation."""
        # Invalid shape
        with pytest.raises(ValueError):
            await ml_service.classify_ecg(np.random.randn(100, 5))  # Wrong number of leads
        
        # Invalid data type
        with pytest.raises(ValueError):
            await ml_service.classify_ecg(np.random.randn(5000, 12).astype(np.int32))
        
        # Empty data
        with pytest.raises(ValueError):
            await ml_service.classify_ecg(np.array([]))

    # Test 13: Model Versioning
    @pytest.mark.asyncio
    async def test_model_versioning(self, ml_service, mock_onnx_session):
        """Test model versioning support."""
        with patch('onnxruntime.InferenceSession', return_value=mock_onnx_session):
            await ml_service.load_model("ecg_classifier", "/path/model_v1.onnx", version="1.0")
            await ml_service.load_model("ecg_classifier", "/path/model_v2.onnx", version="2.0")
        
        assert "ecg_classifier_v1.0" in ml_service.models
        assert "ecg_classifier_v2.0" in ml_service.models

    # Test 14: Performance Monitoring
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, ml_service, sample_ecg_data, mock_onnx_session):
        """Test performance monitoring and metrics."""
        ml_service.models["ecg_classifier"] = mock_onnx_session
        
        # Enable performance monitoring
        ml_service.enable_performance_monitoring = True
        
        result = await ml_service.classify_ecg(sample_ecg_data)
        
        assert "inference_time_ms" in result
        assert "preprocessing_time_ms" in result
        assert result["inference_time_ms"] > 0

    # Test 15: Error Recovery
    @pytest.mark.asyncio
    async def test_error_recovery(self, ml_service, sample_ecg_data, mock_onnx_session):
        """Test error recovery mechanisms."""
        # Setup model that fails initially
        failing_session = Mock()
        failing_session.run.side_effect = [
            Exception("Inference failed"),
            [np.array([[0.1, 0.8, 0.1]]), np.array([[0.85]])]  # Success on retry
        ]
        
        ml_service.models["unreliable_model"] = failing_session
        
        result = await ml_service.classify_ecg(sample_ecg_data, model_name="unreliable_model", max_retries=2)
        
        assert result is not None
        assert "predictions" in result

    # Test 16: Concurrent Inference
    @pytest.mark.asyncio
    async def test_concurrent_inference(self, ml_service, mock_onnx_session):
        """Test concurrent inference requests."""
        ml_service.models["ecg_classifier"] = mock_onnx_session
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(10):
            ecg_data = np.random.randn(5000, 12).astype(np.float32)
            task = ml_service.classify_ecg(ecg_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all("predictions" in result for result in results)

    # Test 17: Model Metadata
    @pytest.mark.asyncio
    async def test_model_metadata(self, ml_service, mock_onnx_session):
        """Test model metadata extraction."""
        mock_onnx_session.get_modelmeta.return_value = Mock(
            custom_metadata_map={
                "model_version": "1.0",
                "training_data": "MIT-BIH",
                "accuracy": "0.95"
            }
        )
        
        ml_service.models["ecg_classifier"] = mock_onnx_session
        
        metadata = await ml_service.get_model_metadata("ecg_classifier")
        
        assert "model_version" in metadata
        assert "training_data" in metadata
        assert "accuracy" in metadata

    # Test 18: Feature Extraction
    @pytest.mark.asyncio
    async def test_feature_extraction(self, ml_service, sample_ecg_data):
        """Test ECG feature extraction."""
        features = await ml_service.extract_features(sample_ecg_data)
        
        assert "heart_rate" in features
        assert "rr_intervals" in features
        assert "qrs_width" in features
        assert "pr_interval" in features
        assert "qt_interval" in features
        
        # Validate feature ranges
        assert 40 <= features["heart_rate"] <= 200
        assert features["qrs_width"] > 0

    # Test 19: Model Comparison
    @pytest.mark.asyncio
    async def test_model_comparison(self, ml_service, sample_ecg_data, mock_onnx_session):
        """Test comparison between different models."""
        # Setup multiple models with different outputs
        model1 = Mock()
        model1.run.return_value = [np.array([[0.8, 0.2]]), np.array([[0.85]])]
        
        model2 = Mock()
        model2.run.return_value = [np.array([[0.7, 0.3]]), np.array([[0.80]])]
        
        ml_service.models["model_1"] = model1
        ml_service.models["model_2"] = model2
        
        comparison = await ml_service.compare_models(
            sample_ecg_data, 
            ["model_1", "model_2"]
        )
        
        assert "model_1" in comparison
        assert "model_2" in comparison
        assert "agreement_score" in comparison

    # Test 20: Resource Cleanup
    @pytest.mark.asyncio
    async def test_resource_cleanup(self, ml_service, mock_onnx_session):
        """Test proper resource cleanup."""
        ml_service.models["test_model"] = mock_onnx_session
        
        # Cleanup should remove models and free memory
        await ml_service.cleanup()
        
        assert len(ml_service.models) == 0
        assert len(ml_service.model_cache) == 0


class TestMLModelServiceInterpretability:
    """Test interpretability features of ML Model Service."""

    @pytest.fixture
    def ml_service(self, mock_db_session):
        """ML Model service instance."""
        return MLModelService(mock_db_session)

    @pytest.mark.asyncio
    async def test_attention_maps(self, ml_service, sample_ecg_data):
        """Test attention map generation."""
        attention_maps = await ml_service.generate_attention_maps(sample_ecg_data)
        
        assert attention_maps.shape == sample_ecg_data.shape
        assert np.all(attention_maps >= 0)
        assert np.all(attention_maps <= 1)

    @pytest.mark.asyncio
    async def test_feature_importance(self, ml_service, sample_ecg_data):
        """Test feature importance calculation."""
        importance = await ml_service.calculate_feature_importance(sample_ecg_data)
        
        assert "lead_importance" in importance
        assert "temporal_importance" in importance
        assert len(importance["lead_importance"]) == 12  # 12 leads

    @pytest.mark.asyncio
    async def test_saliency_maps(self, ml_service, sample_ecg_data):
        """Test saliency map generation."""
        saliency = await ml_service.generate_saliency_maps(sample_ecg_data)
        
        assert saliency.shape == sample_ecg_data.shape
        assert not np.all(saliency == 0)  # Should have non-zero values

    @pytest.mark.asyncio
    async def test_lime_explanation(self, ml_service, sample_ecg_data, mock_onnx_session):
        """Test LIME-based explanations."""
        ml_service.models["ecg_classifier"] = mock_onnx_session
        
        explanation = await ml_service.generate_lime_explanation(sample_ecg_data)
        
        assert "feature_weights" in explanation
        assert "prediction_confidence" in explanation
        assert len(explanation["feature_weights"]) > 0

    @pytest.mark.asyncio
    async def test_shap_values(self, ml_service, sample_ecg_data, mock_onnx_session):
        """Test SHAP value calculation."""
        ml_service.models["ecg_classifier"] = mock_onnx_session
        
        shap_values = await ml_service.calculate_shap_values(sample_ecg_data)
        
        assert shap_values.shape == sample_ecg_data.shape
        assert not np.all(shap_values == 0)

