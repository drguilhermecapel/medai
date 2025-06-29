"""
Mocks inteligentes para simular comportamentos realistas
em testes do MedAI
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio


@dataclass
class AIDiagnosticResult:
    """Resultado de diagnóstico AI"""
    primary_diagnosis: str
    differential_diagnoses: List[Dict[str, float]]
    clinical_correlation: float
    recommendations: List[str]
    icd10_codes: List[str]
    severity: str
    processing_time: float


@dataclass
class MLPredictionResult:
    """Resultado de predição ML"""
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    features_importance: Dict[str, float]
    model_version: str
    processing_time: float


@dataclass
class ValidationResult:
    """Resultado de validação"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]


class SmartAIMock:
    """Mock inteligente para diagnóstico AI"""
    
    def __init__(self):
        self.diagnoses = {
            "respiratory": [
                ("Pneumonia", ["J18.9", "J18.1"]),
                ("COPD Exacerbation", ["J44.0", "J44.1"]),
                ("Asthma", ["J45.9", "J45.0"]),
                ("COVID-19", ["U07.1", "U07.2"]),
            ],
            "cardiovascular": [
                ("Acute Myocardial Infarction", ["I21.0", "I21.1"]),
                ("Heart Failure", ["I50.0", "I50.1"]),
                ("Hypertensive Crisis", ["I16.0", "I16.1"]),
            ],
            "neurological": [
                ("Stroke", ["I64", "I63.9"]),
                ("Migraine", ["G43.0", "G43.1"]),
                ("Seizure", ["G40.9", "G40.8"]),
            ],
            "general": [
                ("Viral Infection", ["B34.9", "B34.8"]),
                ("Bacterial Infection", ["A49.9", "A49.8"]),
                ("Dehydration", ["E86.0", "E86.1"]),
            ]
        }
        self.call_count = 0
        
    async def diagnose(self, patient_data: Dict, clinical_data: Dict) -> AIDiagnosticResult:
        """Simula diagnóstico AI integrado"""
        self.call_count += 1
        
        processing_time = random.uniform(1.0, 3.0)
        await asyncio.sleep(processing_time)
        
        # Determina categoria baseada nos sintomas
        symptoms = clinical_data.get("symptoms", [])
        if any(s in ["tosse", "falta de ar", "dor no peito"] for s in symptoms):
            category = "respiratory"
        elif any(s in ["dor no peito", "palpitações"] for s in symptoms):
            category = "cardiovascular"
        elif any(s in ["dor de cabeça", "tontura", "confusão"] for s in symptoms):
            category = "neurological"
        else:
            category = "general"
            
        # Seleciona diagnóstico primário
        primary_diagnosis, icd_codes = random.choice(self.diagnoses[category])
        
        # Gera diagnósticos diferenciais
        all_diagnoses = []
        for cat_diagnoses in self.diagnoses.values():
            all_diagnoses.extend(cat_diagnoses)
            
        differential = []
        for diag, codes in all_diagnoses:
            if diag != primary_diagnosis:
                differential.append({
                    "diagnosis": diag,
                    "probability": random.uniform(0.1, 0.7)
                })
        differential.sort(key=lambda x: x["probability"], reverse=True)
        differential = differential[:3]
        
        # Determina severidade
        age = patient_data.get("age", 50)
        has_comorbidities = len(patient_data.get("medical_history", [])) > 0
        vital_signs = clinical_data.get("vital_signs", {})
        
        severity = self._calculate_severity(age, has_comorbidities, vital_signs)
        
        # Gera recomendações
        recommendations = self._generate_ai_recommendations(primary_diagnosis, severity)
        
        return AIDiagnosticResult(
            primary_diagnosis=primary_diagnosis,
            differential_diagnoses=differential,
            clinical_correlation=random.uniform(0.7, 0.95),
            recommendations=recommendations,
            icd10_codes=icd_codes,
            severity=severity,
            processing_time=processing_time
        )
        
    def _calculate_severity(self, age: int, has_comorbidities: bool, vital_signs: Dict) -> str:
        """Calcula severidade baseada em múltiplos fatores"""
        severity_score = 0
        
        # Idade
        if age > 70:
            severity_score += 2
        elif age > 50:
            severity_score += 1
            
        # Comorbidades
        if has_comorbidities:
            severity_score += 2
            
        # Sinais vitais
        temp = vital_signs.get("temperature", 36.5)
        if temp > 39 or temp < 35:
            severity_score += 2
        elif temp > 38:
            severity_score += 1
            
        hr = vital_signs.get("heart_rate", 70)
        if hr > 120 or hr < 50:
            severity_score += 2
        elif hr > 100 or hr < 60:
            severity_score += 1
            
        # Determina severidade final
        if severity_score >= 5:
            return "high"
        elif severity_score >= 3:
            return "moderate"
        else:
            return "low"
        
    def _generate_ai_recommendations(self, diagnosis: str, severity: str) -> List[str]:
        """Gera recomendações baseadas em AI"""
        base_recommendations = {
            "Pneumonia": [
                "Antibioticoterapia empírica",
                "Radiografia de tórax",
                "Hemograma completo",
                "PCR e procalcitonina",
                "Oximetria contínua"
            ],
            "Acute Myocardial Infarction": [
                "ECG de 12 derivações urgente",
                "Troponina seriada",
                "Dupla antiagregação plaquetária",
                "Betabloqueador e IECA",
                "Angioplastia primária"
            ],
            "Stroke": [
                "TC de crânio sem contraste urgente",
                "Glicemia capilar",
                "Avaliação neurológica completa",
                "Considerar trombólise",
                "Monitorização neurológica"
            ],
        }
        
        recommendations = base_recommendations.get(
            diagnosis, 
            ["Avaliação clínica", "Exames complementares", "Monitorar sintomas"]
        )
        
        if severity == "high":
            recommendations.insert(0, "Admissão em UTI recomendada")
        elif severity == "moderate":
            recommendations.insert(0, "Monitorização contínua")
            
        return recommendations[:5]  # Máximo 5 recomendações


class SmartMLMock:
    """Mock inteligente para modelos ML"""
    
    def __init__(self):
        self.models = {
            "clinical_risk_predictor": {
                "version": "3.1.0",
                "accuracy": 0.912,
                "type": "regression",
                "output": "risk_score"
            },
            "diagnosis_classifier": {
                "version": "2.5.0",
                "accuracy": 0.945,
                "type": "classification",
                "classes": ["Viral", "Bacterial", "Fungal", "Other"]
            },
            "severity_predictor": {
                "version": "1.8.0",
                "accuracy": 0.887,
                "type": "ordinal",
                "classes": ["low", "moderate", "high", "critical"]
            }
        }
        self.call_count = 0
        
    async def predict(self, model_name: str, features: np.ndarray) -> MLPredictionResult:
        """Simula predição de modelo ML"""
        self.call_count += 1
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
            
        model_info = self.models[model_name]
        processing_time = random.uniform(0.1, 0.5)
        await asyncio.sleep(processing_time)
        
        if model_info["type"] == "regression":
            prediction = str(round(random.uniform(0, 1), 3))
            probabilities = {"risk_score": float(prediction)}
        elif model_info["type"] == "classification":
            classes = model_info["classes"]
            probs = np.random.dirichlet(np.ones(len(classes)))
            probabilities = dict(zip(classes, probs))
            prediction = max(probabilities, key=probabilities.get)
        else:  # ordinal
            classes = model_info["classes"]
            # Gera probabilidades ordenadas
            base_probs = sorted(np.random.rand(len(classes)), reverse=True)
            probabilities = dict(zip(classes, base_probs))
            prediction = classes[0]
            
        # Simula importância de features
        num_features = features.shape[0] if hasattr(features, 'shape') else len(features)
        feature_names = [f"feature_{i}" for i in range(num_features)]
        importances = np.random.dirichlet(np.ones(len(feature_names)))
        features_importance = dict(zip(feature_names, importances))
        
        return MLPredictionResult(
            prediction=prediction,
            confidence=max(probabilities.values()) if probabilities else 0.95,
            probabilities=probabilities,
            features_importance=features_importance,
            model_version=model_info["version"],
            processing_time=processing_time
        )


class SmartValidationMock:
    """Mock inteligente para validação médica"""
    
    def __init__(self):
        self.drug_interactions = {
            ("warfarina", "aspirina"): "Alto risco de sangramento",
            ("metformina", "contraste"): "Risco de acidose láctica",
            ("IECA", "espironolactona"): "Risco de hipercalemia",
        }
        self.contraindications = {
            "aspirina": ["úlcera péptica ativa", "sangramento ativo"],
            "metformina": ["insuficiência renal grave", "acidose"],
            "betabloqueador": ["asma grave", "bloqueio AV avançado"],
        }
        
    async def validate_prescription(self, medications: List[Dict]) -> ValidationResult:
        """Valida prescrição médica"""
        errors = []
        warnings = []
        suggestions = []
        
        # Verifica interações medicamentosas
        med_names = [m["name"].lower() for m in medications]
        for i, med1 in enumerate(med_names):
            for med2 in med_names[i+1:]:
                interaction_key = tuple(sorted([med1, med2]))
                if interaction_key in self.drug_interactions:
                    warnings.append(f"Interação entre {med1} e {med2}: {self.drug_interactions[interaction_key]}")
                    
        # Verifica contraindicações
        for med in medications:
            med_name = med["name"].lower()
            if med_name in self.contraindications:
                patient_conditions = med.get("patient_conditions", [])
                for condition in patient_conditions:
                    if condition in self.contraindications[med_name]:
                        errors.append(f"{med_name} contraindicado em {condition}")
                        
        # Verifica doses
        for med in medications:
            dose = med.get("dose", 0)
            max_dose = med.get("max_daily_dose", float('inf'))
            if dose > max_dose:
                errors.append(f"Dose de {med['name']} excede limite diário")
                
        # Gera sugestões
        if len(medications) > 5:
            suggestions.append("Considere revisar polifarmácia")
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
        
    async def validate_lab_results(self, lab_results: Dict) -> ValidationResult:
        """Valida resultados laboratoriais"""
        errors = []
        warnings = []
        suggestions = []
        
        # Define ranges normais
        normal_ranges = {
            "hemoglobin": (12.0, 16.0),
            "leukocytes": (4000, 11000),
            "platelets": (150000, 400000),
            "glucose": (70, 100),
            "creatinine": (0.6, 1.2),
        }
        
        for test, value in lab_results.items():
            if test in normal_ranges:
                min_val, max_val = normal_ranges[test]
                if value < min_val:
                    warnings.append(f"{test} baixo: {value} (normal: {min_val}-{max_val})")
                elif value > max_val:
                    warnings.append(f"{test} alto: {value} (normal: {min_val}-{max_val})")
                    
                # Valores críticos
                if test == "hemoglobin" and value < 7:
                    errors.append(f"Hemoglobina criticamente baixa: {value}")
                elif test == "glucose" and value > 500:
                    errors.append(f"Glicose criticamente alta: {value}")
                    
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )


# Fixtures para uso em testes
@pytest.fixture
def smart_ai_mock():
    """Fixture para AI mock"""
    return SmartAIMock()


@pytest.fixture
def smart_ml_mock():
    """Fixture para ML mock"""
    return SmartMLMock()


@pytest.fixture
def smart_validation_mock():
    """Fixture para validation mock"""
    return SmartValidationMock()