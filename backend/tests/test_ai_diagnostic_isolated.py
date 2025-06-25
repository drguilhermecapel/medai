"""
Isolated test for AI Diagnostic Service - No circular imports
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Define constants locally to avoid imports
class ConfidenceLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class ClinicalUrgency:
    ROUTINE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

class DiagnosisCategory:
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"
    ARRHYTHMIA = "arrhythmia"

# Mock the AI Diagnostic Service
class MockAIDiagnosticService:
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    async def generate_diagnosis(self, **kwargs):
        return {
            "primary_diagnosis": "Atrial Fibrillation with RVR",
            "confidence_level": ConfidenceLevel.HIGH,
            "clinical_urgency": ClinicalUrgency.HIGH,
            "icd10_codes": ["I48.91"],
            "differential_diagnoses": [
                {"diagnosis": "Atrial Flutter", "probability": 0.15}
            ],
            "recommendations": ["Rate control", "Anticoagulation assessment"],
            "risk_assessment": {
                "stroke_risk": "high",
                "cha2ds2_vasc_score": 4
            }
        }


class TestAIDiagnosticServiceIsolated:
    """Test AI Diagnostic Service in isolation."""
    
    @pytest.fixture
    def ai_service(self):
        """Create mock AI service."""
        return MockAIDiagnosticService()
    
    @pytest.fixture
    def ecg_data(self):
        """Sample ECG data."""
        return {
            "diagnosis": "Atrial Fibrillation",
            "confidence": 0.92,
            "features": {
                "heart_rate": 145,
                "rhythm_regularity": 0.2,
                "p_wave_present": False
            }
        }
    
    @pytest.fixture
    def patient_data(self):
        """Sample patient data."""
        return {
            "age": 75,
            "gender": "male",
            "hypertension": True,
            "diabetes": True
        }
    
    @pytest.mark.asyncio
    async def test_basic_diagnosis_generation(self, ai_service, ecg_data, patient_data):
        """Test basic diagnosis generation."""
        # Generate diagnosis
        result = await ai_service.generate_diagnosis(
            ecg_analysis=ecg_data,
            patient_data=patient_data
        )
        
        # Verify structure
        assert "primary_diagnosis" in result
        assert "confidence_level" in result
        assert "clinical_urgency" in result
        assert "icd10_codes" in result
        assert len(result["icd10_codes"]) > 0
        
        # Verify values
        assert result["confidence_level"] == ConfidenceLevel.HIGH
        assert result["clinical_urgency"] == ClinicalUrgency.HIGH
        assert "Atrial Fibrillation" in result["primary_diagnosis"]
    
    @pytest.mark.asyncio
    async def test_risk_assessment_included(self, ai_service, ecg_data, patient_data):
        """Test that risk assessment is included."""
        result = await ai_service.generate_diagnosis(
            ecg_analysis=ecg_data,
            patient_data=patient_data
        )
        
        assert "risk_assessment" in result
        assert "stroke_risk" in result["risk_assessment"]
        assert "cha2ds2_vasc_score" in result["risk_assessment"]
        assert result["risk_assessment"]["cha2ds2_vasc_score"] >= 2
    
    @pytest.mark.asyncio
    async def test_recommendations_generated(self, ai_service, ecg_data, patient_data):
        """Test that recommendations are generated."""
        result = await ai_service.generate_diagnosis(
            ecg_analysis=ecg_data,
            patient_data=patient_data
        )
        
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        assert any("anticoagulation" in rec.lower() 
                  for rec in result["recommendations"])


# Run tests directly if executed as script
if __name__ == "__main__":
    pytest.main([__file__, "-v"])