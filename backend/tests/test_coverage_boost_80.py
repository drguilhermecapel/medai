"""
Comprehensive test suite to boost coverage to 80%
Focus on modules with 0% coverage first for maximum impact
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import json

try:
    import torch
except ImportError:
    torch = Mock()

try:
    from PIL import Image
except ImportError:
    Image = Mock()

try:
    import pandas as pd
except ImportError:
    pd = Mock()

import io

class TestAdvancedMLService:
    """Tests for the advanced ML service module"""
    
    @pytest.fixture
    def ml_service(self):
        from app.services.advanced_ml_service import AdvancedMLService
        return AdvancedMLService()
    
    @pytest.fixture
    def sample_ecg_data(self):
        return {
            'signal': np.random.randn(12, 5000),
            'metadata': {
                'patient_id': 'TEST001',
                'sampling_rate': 500,
                'leads': ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 
                         'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
            }
        }
    
    def test_init_models(self, ml_service):
        """Test model initialization"""
        assert ml_service.models is not None
        assert hasattr(ml_service, 'preprocessing_pipeline')
        assert hasattr(ml_service, 'feature_extractor')
        assert hasattr(ml_service, 'ensemble_predictor')
    
    def test_preprocess_signal(self, ml_service, sample_ecg_data):
        """Test signal preprocessing"""
        processed = ml_service.preprocess_signal(sample_ecg_data['signal'])
        assert processed.shape == sample_ecg_data['signal'].shape
        assert not np.isnan(processed).any()
        assert not np.isinf(processed).any()
    
    def test_extract_deep_features(self, ml_service, sample_ecg_data):
        """Test deep feature extraction"""
        features = ml_service.extract_deep_features(sample_ecg_data['signal'])
        assert isinstance(features, dict)
        assert 'morphological' in features
        assert 'temporal' in features
        assert 'spectral' in features
        assert 'nonlinear' in features
    
    @pytest.mark.asyncio
    async def test_predict_pathologies(self, ml_service, sample_ecg_data):
        """Test pathology prediction"""
        predictions = await ml_service.predict_pathologies(
            sample_ecg_data['signal'],
            sample_ecg_data['metadata']
        )
        assert 'pathologies' in predictions
        assert 'confidence_scores' in predictions
        assert 'risk_assessment' in predictions
        assert 'recommendations' in predictions
    
    def test_ensemble_prediction(self, ml_service, sample_ecg_data):
        """Test ensemble prediction mechanism"""
        features = ml_service.extract_deep_features(sample_ecg_data['signal'])
        ensemble_result = ml_service._ensemble_predict(features)
        assert 'predictions' in ensemble_result
        assert 'uncertainties' in ensemble_result
        assert 'model_agreements' in ensemble_result
    
    def test_attention_mechanism(self, ml_service, sample_ecg_data):
        """Test attention mechanism for interpretability"""
        attention_weights = ml_service._compute_attention_weights(
            sample_ecg_data['signal']
        )
        assert attention_weights.shape[0] == 12  # Number of leads
        assert np.allclose(attention_weights.sum(axis=1), 1.0)  # Normalized
    
    def test_multi_scale_analysis(self, ml_service, sample_ecg_data):
        """Test multi-scale temporal analysis"""
        scales = [1, 2, 4, 8, 16]
        multi_scale_features = ml_service._multi_scale_analysis(
            sample_ecg_data['signal'], scales
        )
        assert len(multi_scale_features) == len(scales)
        for scale_features in multi_scale_features:
            assert not np.isnan(scale_features).any()
    
    def test_rhythm_classification(self, ml_service, sample_ecg_data):
        """Test rhythm classification"""
        rhythm_result = ml_service._classify_rhythm(sample_ecg_data['signal'])
        assert 'rhythm_type' in rhythm_result
        assert 'confidence' in rhythm_result
        assert rhythm_result['rhythm_type'] in [
            'Normal Sinus Rhythm', 'Atrial Fibrillation', 
            'Atrial Flutter', 'Ventricular Tachycardia'
        ]
    
    def test_morphology_analysis(self, ml_service, sample_ecg_data):
        """Test morphology analysis"""
        morphology = ml_service._analyze_morphology(sample_ecg_data['signal'])
        assert 'p_wave' in morphology
        assert 'qrs_complex' in morphology
        assert 't_wave' in morphology
        assert 'st_segment' in morphology
    
    def test_error_handling(self, ml_service):
        """Test error handling for invalid inputs"""
        with pytest.raises(ValueError):
            ml_service.preprocess_signal(np.random.randn(5, 100))
        
        signal_with_nan = np.random.randn(12, 5000)
        signal_with_nan[0, :100] = np.nan
        processed = ml_service.preprocess_signal(signal_with_nan)
        assert not np.isnan(processed).any()


class TestClinicalExplanations:
    """Tests for clinical explanations module"""
    
    @pytest.fixture
    def explanation_generator(self):
        from app.utils.clinical_explanations import ClinicalExplanationGenerator
        return ClinicalExplanationGenerator()
    
    @pytest.fixture
    def sample_diagnosis(self):
        return {
            'condition': 'Atrial Fibrillation',
            'confidence': 0.87,
            'severity': 'moderate',
            'features': {
                'irregular_rr': True,
                'absent_p_waves': True,
                'heart_rate': 110
            }
        }
    
    def test_generate_explanation(self, explanation_generator, sample_diagnosis):
        """Test clinical explanation generation"""
        explanation = explanation_generator.generate_explanation(sample_diagnosis)
        assert isinstance(explanation, dict)
        assert 'summary' in explanation
        assert 'detailed_findings' in explanation
        assert 'clinical_significance' in explanation
        assert 'recommendations' in explanation
    
    def test_format_for_clinician(self, explanation_generator, sample_diagnosis):
        """Test formatting for clinician readability"""
        explanation = explanation_generator.generate_explanation(sample_diagnosis)
        formatted = explanation_generator.format_for_clinician(explanation)
        assert isinstance(formatted, str)
        assert sample_diagnosis['condition'] in formatted
        assert 'Clinical Significance' in formatted
    
    def test_generate_patient_summary(self, explanation_generator, sample_diagnosis):
        """Test patient-friendly summary generation"""
        patient_summary = explanation_generator.generate_patient_summary(
            sample_diagnosis
        )
        assert isinstance(patient_summary, str)
        assert len(patient_summary) < 500  # Should be concise
        assert 'irregular heartbeat' in patient_summary.lower()
    
    def test_risk_assessment_explanation(self, explanation_generator):
        """Test risk assessment explanation"""
        risk_data = {
            'overall_risk': 'high',
            'risk_factors': ['age', 'hypertension', 'diabetes'],
            'risk_score': 0.75
        }
        risk_explanation = explanation_generator.explain_risk_assessment(risk_data)
        assert 'risk level' in risk_explanation.lower()
        assert all(factor in risk_explanation for factor in risk_data['risk_factors'])
    
    def test_multiple_conditions(self, explanation_generator):
        """Test explanation for multiple conditions"""
        conditions = [
            {'condition': 'Atrial Fibrillation', 'confidence': 0.87},
            {'condition': 'Left Ventricular Hypertrophy', 'confidence': 0.65}
        ]
        explanation = explanation_generator.generate_multi_condition_explanation(
            conditions
        )
        assert all(cond['condition'] in explanation['summary'] for cond in conditions)
    
    def test_urgency_classification(self, explanation_generator, sample_diagnosis):
        """Test clinical urgency classification"""
        urgency = explanation_generator.classify_urgency(sample_diagnosis)
        assert urgency in ['routine', 'urgent', 'emergent']
        
        emergent_diagnosis = {
            'condition': 'ST-Elevation Myocardial Infarction',
            'confidence': 0.95,
            'features': {'st_elevation': 3.0}
        }
        assert explanation_generator.classify_urgency(emergent_diagnosis) == 'emergent'
    
    def test_medication_recommendations(self, explanation_generator, sample_diagnosis):
        """Test medication recommendation explanations"""
        recommendations = explanation_generator.generate_medication_recommendations(
            sample_diagnosis
        )
        assert isinstance(recommendations, list)
        assert all('medication' in rec and 'rationale' in rec for rec in recommendations)
    
    def test_follow_up_recommendations(self, explanation_generator, sample_diagnosis):
        """Test follow-up recommendation generation"""
        follow_up = explanation_generator.generate_follow_up_plan(sample_diagnosis)
        assert 'timeline' in follow_up
        assert 'tests_recommended' in follow_up
        assert 'specialist_referral' in follow_up


class TestECGVisualizations:
    """Tests for ECG visualization module"""
    
    @pytest.fixture
    def visualizer(self):
        from app.utils.ecg_visualizations import ECGVisualizer
        return ECGVisualizer()
    
    @pytest.fixture
    def sample_ecg_signal(self):
        t = np.linspace(0, 10, 5000)
        signal = np.zeros((12, 5000))
        for i in range(12):
            signal[i] = np.sin(2 * np.pi * 1.2 * t) + 0.1 * np.random.randn(5000)
        return signal
    
    def test_plot_standard_12_lead(self, visualizer, sample_ecg_signal):
        """Test standard 12-lead ECG plotting"""
        fig = visualizer.plot_standard_12_lead(sample_ecg_signal)
        assert fig is not None
        assert len(fig.axes) == 12  # One subplot per lead
    
    def test_plot_rhythm_strip(self, visualizer, sample_ecg_signal):
        """Test rhythm strip plotting"""
        fig = visualizer.plot_rhythm_strip(sample_ecg_signal[1], lead_name='II')
        assert fig is not None
        assert len(fig.axes) == 1
    
    def test_plot_with_annotations(self, visualizer, sample_ecg_signal):
        """Test plotting with annotations"""
        annotations = {
            'r_peaks': [500, 1000, 1500, 2000],
            'p_waves': [(450, 480), (950, 980)],
            'qrs_complexes': [(490, 510), (990, 1010)]
        }
        fig = visualizer.plot_with_annotations(
            sample_ecg_signal[1], annotations, lead_name='II'
        )
        assert fig is not None
        assert len(fig.axes[0].patches) > 0  # Should have annotation patches
    
    def test_plot_heart_rate_trend(self, visualizer):
        """Test heart rate trend plotting"""
        try:
            timestamps = pd.date_range('2024-01-01', periods=100, freq='min')
            heart_rates = 60 + 10 * np.sin(np.linspace(0, 4*np.pi, 100))
        except:
            timestamps = [datetime.now() + timedelta(minutes=i) for i in range(100)]
            heart_rates = 60 + 10 * np.sin(np.linspace(0, 4*np.pi, 100))
        
        fig = visualizer.plot_heart_rate_trend(timestamps, heart_rates)
        assert fig is not None
        assert 'Heart Rate Trend' in fig.axes[0].get_title()
    
    def test_plot_feature_importance(self, visualizer):
        """Test feature importance visualization"""
        features = {
            'Heart Rate Variability': 0.25,
            'QRS Duration': 0.20,
            'ST Elevation': 0.35,
            'PR Interval': 0.10,
            'QT Interval': 0.10
        }
        fig = visualizer.plot_feature_importance(features)
        assert fig is not None
        assert len(fig.axes[0].patches) == len(features)
    
    def test_generate_report_pdf(self, visualizer, sample_ecg_signal):
        """Test PDF report generation"""
        analysis_results = {
            'diagnosis': 'Normal Sinus Rhythm',
            'heart_rate': 72,
            'pr_interval': 160,
            'qrs_duration': 90,
            'qt_interval': 400
        }
        pdf_bytes = visualizer.generate_report_pdf(
            sample_ecg_signal, analysis_results
        )
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000  # Should be a substantial PDF
    
    def test_interactive_plot(self, visualizer, sample_ecg_signal):
        """Test interactive plot generation"""
        html_content = visualizer.generate_interactive_plot(sample_ecg_signal[1])
        assert isinstance(html_content, str)
        assert '<script' in html_content  # Should contain plotly script
        assert 'plotly' in html_content.lower()
    
    def test_plot_comparison(self, visualizer, sample_ecg_signal):
        """Test ECG comparison plotting"""
        signal1 = sample_ecg_signal[1]
        signal2 = signal1 + 0.1 * np.random.randn(5000)
        fig = visualizer.plot_comparison(
            signal1, signal2, 
            label1='Baseline', label2='Follow-up'
        )
        assert fig is not None
        assert len(fig.axes[0].lines) == 2  # Two signals plotted
    
    def test_export_formats(self, visualizer, sample_ecg_signal):
        """Test different export formats"""
        fig = visualizer.plot_standard_12_lead(sample_ecg_signal)
        
        png_bytes = visualizer.export_figure(fig, format='png')
        assert isinstance(png_bytes, bytes)
        
        svg_content = visualizer.export_figure(fig, format='svg')
        assert isinstance(svg_content, str)
        assert '<svg' in svg_content


class TestAdaptiveThresholds:
    """Tests for adaptive thresholds module"""
    
    @pytest.fixture
    def threshold_manager(self):
        from app.utils.adaptive_thresholds import AdaptiveThresholdManager
        return AdaptiveThresholdManager()
    
    def test_initialize_thresholds(self, threshold_manager):
        """Test threshold initialization"""
        thresholds = threshold_manager.get_current_thresholds()
        assert 'heart_rate' in thresholds
        assert 'pr_interval' in thresholds
        assert 'qrs_duration' in thresholds
        assert 'qt_interval' in thresholds
    
    def test_update_thresholds(self, threshold_manager):
        """Test adaptive threshold updates"""
        historical_data = {
            'heart_rate': np.random.normal(70, 10, 1000),
            'pr_interval': np.random.normal(160, 20, 1000),
            'qrs_duration': np.random.normal(90, 10, 1000)
        }
        
        threshold_manager.update_thresholds(historical_data)
        updated = threshold_manager.get_current_thresholds()
        
        assert updated['heart_rate']['lower'] < 70
        assert updated['heart_rate']['upper'] > 70
    
    def test_population_specific_thresholds(self, threshold_manager):
        """Test population-specific threshold adjustments"""
        patient_demographics = {
            'age': 75,
            'gender': 'female',
            'ethnicity': 'asian'
        }
        
        adjusted = threshold_manager.get_adjusted_thresholds(patient_demographics)
        default = threshold_manager.get_current_thresholds()
        
        assert adjusted['heart_rate']['upper'] != default['heart_rate']['upper']
    
    def test_dynamic_threshold_learning(self, threshold_manager):
        """Test dynamic learning from feedback"""
        feedback = {
            'parameter': 'qt_interval',
            'value': 450,
            'clinical_judgment': 'normal',
            'patient_context': {'medication': 'amiodarone'}
        }
        
        threshold_manager.learn_from_feedback(feedback)
        
        context_thresholds = threshold_manager.get_contextual_thresholds(
            {'medication': 'amiodarone'}
        )
        assert context_thresholds['qt_interval']['upper'] >= 450
    
    def test_anomaly_detection(self, threshold_manager):
        """Test anomaly detection with adaptive thresholds"""
        measurements = {
            'heart_rate': 150,  # Tachycardia
            'pr_interval': 160,  # Normal
            'qrs_duration': 140  # Wide QRS
        }
        
        anomalies = threshold_manager.detect_anomalies(measurements)
        assert 'heart_rate' in anomalies
        assert 'qrs_duration' in anomalies
        assert 'pr_interval' not in anomalies
    
    def test_confidence_intervals(self, threshold_manager):
        """Test confidence interval calculation"""
        parameter = 'heart_rate'
        value = 85
        
        confidence = threshold_manager.calculate_confidence(parameter, value)
        assert 0 <= confidence <= 1
        
        extreme_confidence = threshold_manager.calculate_confidence(parameter, 200)
        assert extreme_confidence < 0.1
    
    def test_threshold_persistence(self, threshold_manager):
        """Test threshold persistence and loading"""
        historical_data = {
            'heart_rate': np.random.normal(70, 10, 1000)
        }
        threshold_manager.update_thresholds(historical_data)
        
        saved_state = threshold_manager.export_thresholds()
        
        new_manager = type(threshold_manager)()
        new_manager.import_thresholds(saved_state)
        
        assert new_manager.get_current_thresholds() == threshold_manager.get_current_thresholds()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=term-missing"])
