# tests/unit/test_ml_model_service.py
"""
Testes unitários para o serviço de Machine Learning do MedAI.
Cobre modelos de diagnóstico, predição de risco e análise de imagens médicas.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock
import torch
import tensorflow as tf

from app.services.ml_model_service import (
    MLModelService,
    DiagnosticModel,
    RiskAssessmentModel,
    ImageAnalysisModel,
    NLPMedicalModel,
    ModelPreprocessor,
    ModelPostprocessor,
    FeatureExtractor,
    ModelEnsemble,
    MLPipeline,
    ModelMetrics,
    ModelMonitor
)


class TestModelPreprocessor:
    """Testes para pré-processamento de dados."""
    
    @pytest.fixture
    def preprocessor(self):
        return ModelPreprocessor()
    
    def test_normalize_blood_test_data(self, preprocessor):
        """Testa normalização de dados de exame de sangue."""
        blood_data = {
            "glucose": 126,
            "cholesterol_total": 220,
            "cholesterol_hdl": 40,
            "cholesterol_ldl": 150,
            "triglycerides": 200,
            "hemoglobin": 13.5,
            "creatinine": 1.2
        }
        
        normalized = preprocessor.normalize_blood_test(blood_data)
        
        # Verifica que valores estão normalizados (entre 0 e 1 ou padronizados)
        assert all(isinstance(v, float) for v in normalized.values())
        assert "glucose_normalized" in normalized
        assert 0 <= normalized["glucose_normalized"] <= 1
    
    def test_handle_missing_values(self, preprocessor):
        """Testa tratamento de valores ausentes."""
        incomplete_data = {
            "glucose": 95,
            "cholesterol_total": None,
            "cholesterol_hdl": 55,
            "cholesterol_ldl": None,
            "triglycerides": 120
        }
        
        completed = preprocessor.handle_missing_values(
            incomplete_data,
            strategy="median"
        )
        
        # Verifica que não há mais valores None
        assert all(v is not None for v in completed.values())
        assert completed["cholesterol_total"] > 0
    
    def test_encode_categorical_features(self, preprocessor):
        """Testa codificação de features categóricas."""
        patient_data = {
            "gender": "F",
            "smoking_status": "former",
            "diabetes_family_history": "yes",
            "exercise_frequency": "moderate"
        }
        
        encoded = preprocessor.encode_categorical(patient_data)
        
        # Verifica one-hot encoding
        assert "gender_F" in encoded
        assert "gender_M" in encoded
        assert encoded["gender_F"] == 1
        assert encoded["gender_M"] == 0
        assert "smoking_status_former" in encoded
    
    def test_create_time_series_features(self, preprocessor):
        """Testa criação de features de série temporal."""
        glucose_history = [
            {"date": "2024-01-01", "value": 95},
            {"date": "2024-02-01", "value": 102},
            {"date": "2024-03-01", "value": 108},
            {"date": "2024-04-01", "value": 115},
            {"date": "2024-05-01", "value": 121}
        ]
        
        features = preprocessor.extract_time_series_features(glucose_history)
        
        assert "mean" in features
        assert "std" in features
        assert "trend" in features
        assert "last_value" in features
        assert features["trend"] > 0  # Tendência crescente
    
    def test_outlier_detection_and_removal(self, preprocessor):
        """Testa detecção e remoção de outliers."""
        data_with_outliers = {
            "values": [95, 98, 102, 105, 99, 300, 97, 101]  # 300 é outlier
        }
        
        cleaned = preprocessor.remove_outliers(
            data_with_outliers["values"],
            method="iqr"
        )
        
        assert 300 not in cleaned
        assert len(cleaned) == 7


class TestDiagnosticModel:
    """Testes para modelo de diagnóstico."""
    
    @pytest.fixture
    def diagnostic_model(self):
        with patch('app.services.ml_model_service.load_model'):
            return DiagnosticModel(model_path="fake_model.pkl")
    
    def test_predict_diabetes_risk(self, diagnostic_model):
        """Testa predição de risco de diabetes."""
        patient_features = {
            "age": 55,
            "bmi": 28.5,
            "glucose_fasting": 126,
            "hba1c": 7.2,
            "family_history": True,
            "physical_activity": "sedentary",
            "blood_pressure_systolic": 140
        }
        
        with patch.object(diagnostic_model, 'model') as mock_model:
            mock_model.predict_proba.return_value = np.array([[0.15, 0.85]])
            
            result = diagnostic_model.predict_diabetes(patient_features)
            
            assert result["risk_score"] == 0.85
            assert result["risk_category"] == "high"
            assert "recommendations" in result
            assert len(result["recommendations"]) > 0
    
    def test_predict_cardiovascular_risk(self, diagnostic_model):
        """Testa predição de risco cardiovascular."""
        patient_data = {
            "age": 60,
            "gender": "M",
            "cholesterol_total": 240,
            "cholesterol_hdl": 35,
            "blood_pressure_systolic": 150,
            "smoking": True,
            "diabetes": False
        }
        
        with patch.object(diagnostic_model, 'model') as mock_model:
            mock_model.predict.return_value = np.array([0.72])
            
            result = diagnostic_model.predict_cardiovascular_risk(patient_data)
            
            assert 0 <= result["risk_score"] <= 1
            assert result["framingham_score"] > 0
            assert "risk_factors" in result
    
    def test_multi_disease_prediction(self, diagnostic_model):
        """Testa predição de múltiplas doenças."""
        comprehensive_data = {
            "demographics": {"age": 45, "gender": "F"},
            "vitals": {"bp_systolic": 130, "bp_diastolic": 85},
            "lab_results": {
                "glucose": 110,
                "cholesterol_total": 200,
                "creatinine": 0.9,
                "alt": 35
            },
            "symptoms": ["fatigue", "thirst", "blurred_vision"]
        }
        
        with patch.object(diagnostic_model, 'multi_disease_model') as mock_model:
            mock_model.predict.return_value = {
                "diabetes": 0.75,
                "hypertension": 0.60,
                "kidney_disease": 0.15,
                "liver_disease": 0.10
            }
            
            results = diagnostic_model.predict_multi_disease(comprehensive_data)
            
            assert len(results) == 4
            assert results["diabetes"] == 0.75
            assert all(0 <= score <= 1 for score in results.values())
    
    def test_model_interpretability(self, diagnostic_model):
        """Testa interpretabilidade do modelo."""
        patient_features = {
            "glucose": 140,
            "bmi": 30,
            "age": 50,
            "blood_pressure": 140
        }
        
        with patch.object(diagnostic_model, 'model') as mock_model:
            # Simula SHAP values
            mock_model.get_feature_importance.return_value = {
                "glucose": 0.35,
                "bmi": 0.25,
                "age": 0.20,
                "blood_pressure": 0.20
            }
            
            interpretation = diagnostic_model.explain_prediction(
                patient_features,
                prediction=0.80
            )
            
            assert "feature_importance" in interpretation
            assert interpretation["feature_importance"]["glucose"] == 0.35
            assert "explanation_text" in interpretation


class TestRiskAssessmentModel:
    """Testes para modelo de avaliação de risco."""
    
    @pytest.fixture
    def risk_model(self):
        return RiskAssessmentModel()
    
    def test_calculate_readmission_risk(self, risk_model):
        """Testa cálculo de risco de readmissão."""
        patient_history = {
            "previous_admissions": 2,
            "days_since_last_discharge": 45,
            "chronic_conditions": ["diabetes", "heart_failure"],
            "age": 72,
            "medications_count": 8,
            "social_support": "limited"
        }
        
        risk = risk_model.calculate_readmission_risk(patient_history)
        
        assert 0 <= risk["probability"] <= 1
        assert risk["risk_level"] in ["low", "medium", "high"]
        assert "contributing_factors" in risk
        assert len(risk["interventions"]) > 0
    
    def test_surgical_complication_risk(self, risk_model):
        """Testa avaliação de risco de complicação cirúrgica."""
        surgical_data = {
            "procedure_type": "cardiac_surgery",
            "patient_age": 65,
            "asa_score": 3,
            "bmi": 32,
            "diabetes": True,
            "smoking": False,
            "anesthesia_type": "general",
            "emergency": False
        }
        
        risk = risk_model.assess_surgical_risk(surgical_data)
        
        assert "mortality_risk" in risk
        assert "morbidity_risk" in risk
        assert "specific_complications" in risk
        assert risk["risk_category"] in ["low", "moderate", "high", "very_high"]
    
    def test_medication_interaction_risk(self, risk_model):
        """Testa avaliação de risco de interação medicamentosa."""
        medications = [
            {"name": "Warfarin", "dosage": "5mg", "frequency": "daily"},
            {"name": "Aspirin", "dosage": "100mg", "frequency": "daily"},
            {"name": "Amiodarone", "dosage": "200mg", "frequency": "daily"}
        ]
        
        interactions = risk_model.check_drug_interactions(medications)
        
        assert len(interactions) > 0
        assert any(i["severity"] == "major" for i in interactions)
        assert all("drugs" in i for i in interactions)
        assert all("recommendation" in i for i in interactions)
    
    def test_fall_risk_assessment(self, risk_model):
        """Testa avaliação de risco de queda."""
        patient_data = {
            "age": 78,
            "previous_falls": 1,
            "medications": ["diuretic", "sedative", "antihypertensive"],
            "mobility_score": 3,  # 1-5 scale
            "vision_problems": True,
            "cognitive_impairment": "mild"
        }
        
        fall_risk = risk_model.assess_fall_risk(patient_data)
        
        assert fall_risk["risk_score"] > 0
        assert fall_risk["risk_category"] == "high"
        assert "prevention_measures" in fall_risk
        assert len(fall_risk["prevention_measures"]) >= 3


class TestImageAnalysisModel:
    """Testes para modelo de análise de imagens médicas."""
    
    @pytest.fixture
    def image_model(self):
        with patch('app.services.ml_model_service.load_torch_model'):
            return ImageAnalysisModel(model_type="chest_xray")
    
    def test_chest_xray_analysis(self, image_model):
        """Testa análise de raio-X de tórax."""
        # Simula imagem como array numpy
        fake_image = np.random.rand(224, 224, 3).astype(np.float32)
        
        with patch.object(image_model.model, 'predict') as mock_predict:
            mock_predict.return_value = np.array([[0.1, 0.05, 0.8, 0.05]])
            
            result = image_model.analyze_chest_xray(fake_image)
            
            assert "findings" in result
            assert "pneumonia" in result["findings"]
            assert result["findings"]["pneumonia"]["probability"] == 0.8
            assert result["findings"]["pneumonia"]["present"] is True
            assert "heatmap" in result  # Mapa de calor das áreas relevantes
    
    def test_ct_scan_segmentation(self, image_model):
        """Testa segmentação de tomografia."""
        fake_ct_slice = np.random.rand(512, 512).astype(np.float32)
        
        with patch.object(image_model, 'segmentation_model') as mock_model:
            mock_mask = np.zeros((512, 512))
            mock_mask[100:200, 100:200] = 1  # Simula lesão
            mock_model.predict.return_value = mock_mask
            
            result = image_model.segment_ct_scan(fake_ct_slice)
            
            assert "segmentation_mask" in result
            assert "detected_regions" in result
            assert len(result["detected_regions"]) > 0
            assert "volume_estimation" in result
    
    def test_mri_brain_analysis(self, image_model):
        """Testa análise de ressonância magnética cerebral."""
        fake_mri = np.random.rand(256, 256, 150).astype(np.float32)  # 3D
        
        with patch.object(image_model, 'brain_model') as mock_model:
            mock_model.predict.return_value = {
                "tumor_probability": 0.15,
                "tumor_location": None,
                "brain_volume": 1450,
                "ventricle_volume": 25,
                "white_matter_lesions": 2
            }
            
            result = image_model.analyze_brain_mri(fake_mri)
            
            assert result["tumor_detected"] is False
            assert result["brain_volume_ml"] == 1450
            assert result["abnormalities"]["white_matter_lesions"] == 2
    
    def test_image_quality_assessment(self, image_model):
        """Testa avaliação de qualidade de imagem."""
        low_quality_image = np.random.rand(100, 100).astype(np.float32)
        
        quality = image_model.assess_image_quality(low_quality_image)
        
        assert 0 <= quality["score"] <= 1
        assert quality["usable"] is False  # Imagem muito pequena
        assert "issues" in quality
        assert "resolution_too_low" in quality["issues"]


class TestNLPMedicalModel:
    """Testes para modelo de NLP médico."""
    
    @pytest.fixture
    def nlp_model(self):
        with patch('app.services.ml_model_service.load_bert_model'):
            return NLPMedicalModel()
    
    def test_extract_symptoms_from_text(self, nlp_model):
        """Testa extração de sintomas de texto."""
        clinical_text = """
        Paciente relata dor de cabeça intensa há 3 dias, acompanhada de 
        febre alta (39°C) e rigidez na nuca. Também apresenta fotofobia 
        e náuseas. Nega vômitos ou alterações visuais.
        """
        
        with patch.object(nlp_model, 'ner_model') as mock_ner:
            mock_ner.predict.return_value = [
                {"entity": "SYMPTOM", "value": "dor de cabeça", "score": 0.95},
                {"entity": "SYMPTOM", "value": "febre alta", "score": 0.98},
                {"entity": "SYMPTOM", "value": "rigidez na nuca", "score": 0.92},
                {"entity": "SYMPTOM", "value": "fotofobia", "score": 0.88},
                {"entity": "SYMPTOM", "value": "náuseas", "score": 0.90}
            ]
            
            symptoms = nlp_model.extract_symptoms(clinical_text)
            
            assert len(symptoms) == 5
            assert any(s["value"] == "febre alta" for s in symptoms)
            assert all(s["score"] > 0.85 for s in symptoms)
    
    def test_extract_medications_and_dosages(self, nlp_model):
        """Testa extração de medicamentos e dosagens."""
        prescription_text = """
        Prescrever:
        - Amoxicilina 500mg VO 8/8h por 7 dias
        - Paracetamol 750mg VO se febre
        - Omeprazol 20mg VO 1x ao dia em jejum
        """
        
        medications = nlp_model.extract_medications(prescription_text)
        
        assert len(medications) == 3
        assert medications[0]["name"] == "Amoxicilina"
        assert medications[0]["dosage"] == "500mg"
        assert medications[0]["route"] == "VO"
        assert medications[0]["frequency"] == "8/8h"
        assert medications[0]["duration"] == "7 dias"
    
    def test_clinical_text_summarization(self, nlp_model):
        """Testa sumarização de texto clínico."""
        long_clinical_note = """
        [Texto longo de evolução clínica com múltiplos parágrafos...]
        Paciente evoluiu bem após início da antibioticoterapia.
        Febre cedeu em 48h. Alta hospitalar programada.
        """
        
        with patch.object(nlp_model, 'summarizer') as mock_summarizer:
            mock_summarizer.summarize.return_value = (
                "Paciente com boa evolução após antibiótico. "
                "Afebril há 48h. Alta programada."
            )
            
            summary = nlp_model.summarize_clinical_note(
                long_clinical_note,
                max_length=50
            )
            
            assert len(summary) < len(long_clinical_note)
            assert "evolução" in summary.lower()
            assert "alta" in summary.lower()
    
    def test_icd10_suggestion_from_text(self, nlp_model):
        """Testa sugestão de CID-10 baseada em texto."""
        diagnosis_text = """
        Diagnóstico: Pneumonia bacteriana em lobo inferior direito,
        com derrame pleural pequeno associado.
        """
        
        with patch.object(nlp_model, 'icd_classifier') as mock_classifier:
            mock_classifier.predict.return_value = [
                {"code": "J18.9", "description": "Pneumonia não especificada", "score": 0.85},
                {"code": "J15.9", "description": "Pneumonia bacteriana", "score": 0.92},
                {"code": "J94.8", "description": "Outras afecções pleurais", "score": 0.78}
            ]
            
            suggestions = nlp_model.suggest_icd10_codes(diagnosis_text)
            
            assert len(suggestions) >= 2
            assert suggestions[0]["code"] == "J15.9"  # Maior score
            assert all("description" in s for s in suggestions)


class TestModelEnsemble:
    """Testes para ensemble de modelos."""
    
    @pytest.fixture
    def ensemble(self):
        models = [Mock() for _ in range(3)]
        return ModelEnsemble(models=models)
    
    def test_ensemble_voting_prediction(self, ensemble):
        """Testa predição por votação do ensemble."""
        # Configura predições dos modelos
        ensemble.models[0].predict.return_value = {"class": "diabetes", "prob": 0.8}
        ensemble.models[1].predict.return_value = {"class": "diabetes", "prob": 0.75}
        ensemble.models[2].predict.return_value = {"class": "pre_diabetes", "prob": 0.6}
        
        result = ensemble.predict_voting({"glucose": 126})
        
        assert result["prediction"] == "diabetes"  # Maioria
        assert result["confidence"] > 0.7
        assert "model_predictions" in result
    
    def test_ensemble_weighted_average(self, ensemble):
        """Testa média ponderada do ensemble."""
        weights = [0.5, 0.3, 0.2]
        predictions = [0.8, 0.75, 0.6]
        
        for i, (model, pred) in enumerate(zip(ensemble.models, predictions)):
            model.predict_proba.return_value = pred
        
        result = ensemble.predict_weighted(
            {"data": "test"},
            weights=weights
        )
        
        expected = sum(p * w for p, w in zip(predictions, weights))
        assert abs(result["probability"] - expected) < 0.01
    
    def test_ensemble_stacking(self, ensemble):
        """Testa stacking de modelos."""
        # Predições dos modelos base
        base_predictions = [
            {"score": 0.8, "features": [0.1, 0.2]},
            {"score": 0.75, "features": [0.15, 0.25]},
            {"score": 0.7, "features": [0.2, 0.3]}
        ]
        
        for model, pred in zip(ensemble.models, base_predictions):
            model.predict.return_value = pred
        
        with patch.object(ensemble, 'meta_model') as mock_meta:
            mock_meta.predict.return_value = 0.82
            
            result = ensemble.predict_stacking({"input": "data"})
            
            assert result["final_prediction"] == 0.82
            assert "base_predictions" in result


class TestModelMonitor:
    """Testes para monitoramento de modelos."""
    
    @pytest.fixture
    def monitor(self):
        return ModelMonitor()
    
    def test_track_prediction_metrics(self, monitor):
        """Testa rastreamento de métricas de predição."""
        predictions = [
            {"predicted": 1, "actual": 1, "confidence": 0.9},
            {"predicted": 0, "actual": 0, "confidence": 0.85},
            {"predicted": 1, "actual": 0, "confidence": 0.6},
            {"predicted": 0, "actual": 0, "confidence": 0.95}
        ]
        
        for pred in predictions:
            monitor.log_prediction(pred)
        
        metrics = monitor.calculate_metrics()
        
        assert metrics["accuracy"] == 0.75
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert metrics["average_confidence"] > 0.8
    
    def test_detect_model_drift(self, monitor):
        """Testa detecção de drift do modelo."""
        # Dados históricos
        historical_features = np.random.normal(0, 1, (1000, 10))
        
        # Dados atuais com drift
        current_features = np.random.normal(0.5, 1.2, (100, 10))
        
        drift_result = monitor.detect_drift(
            historical_features,
            current_features,
            method="kolmogorov_smirnov"
        )
        
        assert drift_result["drift_detected"] is True
        assert drift_result["drift_score"] > 0.5
        assert "features_with_drift" in drift_result
    
    def test_performance_degradation_alert(self, monitor):
        """Testa alerta de degradação de performance."""
        # Simula queda de performance ao longo do tempo
        for day in range(30):
            if day < 20:
                accuracy = 0.92 + np.random.normal(0, 0.02)
            else:
                accuracy = 0.85 + np.random.normal(0, 0.02)
            
            monitor.log_daily_performance({
                "date": datetime.now() - timedelta(days=30-day),
                "accuracy": accuracy,
                "predictions_count": 100
            })
        
        alerts = monitor.check_performance_alerts()
        
        assert len(alerts) > 0
        assert any(a["type"] == "performance_degradation" for a in alerts)
        assert any(a["severity"] == "high" for a in alerts)