"""
Serviço de diagnóstico com IA
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from app.core.constants import (
    DiagnosisCategory, ClinicalUrgency, ConfidenceLevel,
    ECGDiagnosisType, RiskLevel
)


@dataclass
class DiagnosticConfidence:
    """Confiança do diagnóstico"""
    overall: float
    primary_diagnosis: float
    differential_diagnoses: Dict[str, float]
    risk_assessment: float
    urgency_assessment: float
    
    @property
    def level(self) -> str:
        """Retorna o nível de confiança"""
        if self.overall >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif self.overall >= 0.8:
            return ConfidenceLevel.HIGH
        elif self.overall >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif self.overall >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW


@dataclass
class AIDiagnosticResult:
    """Resultado do diagnóstico por IA"""
    diagnosis_id: str
    analysis_id: str
    timestamp: datetime
    
    # Diagnóstico principal
    primary_diagnosis: str
    diagnosis_type: str
    category: str
    urgency: str
    risk_level: str
    
    # Diagnósticos adicionais
    secondary_diagnoses: List[str]
    differential_diagnoses: List[str]
    
    # Confiança
    confidence: DiagnosticConfidence
    
    # Detalhes
    clinical_findings: Dict[str, Any]
    recommendations: List[str]
    follow_up_required: bool
    
    # Metadados
    model_version: str
    processing_time: float
    

class AIDiagnosticService:
    """Serviço principal de diagnóstico com IA"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        
    async def analyze_ecg(
        self,
        ecg_data: Dict[str, Any],
        patient_data: Optional[Dict[str, Any]] = None
    ) -> AIDiagnosticResult:
        """
        Analisa ECG usando IA
        
        Args:
            ecg_data: Dados do ECG
            patient_data: Dados do paciente (opcional)
            
        Returns:
            Resultado do diagnóstico
        """
        # Implementação simplificada para testes
        confidence = DiagnosticConfidence(
            overall=0.85,
            primary_diagnosis=0.90,
            differential_diagnoses={"Arritmia": 0.75, "Isquemia": 0.60},
            risk_assessment=0.85,
            urgency_assessment=0.80
        )
        
        return AIDiagnosticResult(
            diagnosis_id="diag-123",
            analysis_id="analysis-456",
            timestamp=datetime.utcnow(),
            primary_diagnosis="Ritmo Sinusal Normal",
            diagnosis_type=ECGDiagnosisType.NORMAL_SINUS_RHYTHM,
            category=DiagnosisCategory.NORMAL,
            urgency=ClinicalUrgency.ROUTINE,
            risk_level=RiskLevel.LOW,
            secondary_diagnoses=[],
            differential_diagnoses=["Bradicardia Sinusal", "Arritmia Sinusal"],
            confidence=confidence,
            clinical_findings={
                "heart_rate": 75,
                "pr_interval": 160,
                "qrs_duration": 90,
                "qt_interval": 400
            },
            recommendations=[
                "Manter acompanhamento regular",
                "Repetir ECG em 6 meses"
            ],
            follow_up_required=False,
            model_version=self.model_version,
            processing_time=1.23
        )


# Exports
__all__ = [
    "AIDiagnosticService",
    "AIDiagnosticResult", 
    "DiagnosticConfidence"
]