"""
Serviço de diagnóstico com IA - Versão simplificada
"""
# Primeiro, importa tudo que precisamos
from app.core.constants import (
    DiagnosisCategory as _DiagnosisCategory,
    ClinicalUrgency as _ClinicalUrgency,
    ConfidenceLevel as _ConfidenceLevel,
    ECGDiagnosisType as _ECGDiagnosisType,
    RiskLevel as _RiskLevel
)

# Re-exporta as constantes no namespace do módulo
DiagnosisCategory = _DiagnosisCategory
ClinicalUrgency = _ClinicalUrgency
ConfidenceLevel = _ConfidenceLevel
ECGDiagnosisType = _ECGDiagnosisType
RiskLevel = _RiskLevel

# Classe simples para testes
class DiagnosticConfidence:
    def __init__(self, overall=0.85):
        self.overall = overall

class AIDiagnosticResult:
    def __init__(self):
        self.diagnosis_id = "test-123"

class AIDiagnosticService:
    def __init__(self):
        self.model_version = "1.0.0"

# Garante que tudo está disponível
__all__ = [
    'DiagnosisCategory',
    'ClinicalUrgency',
    'ConfidenceLevel',
    'ECGDiagnosisType',
    'RiskLevel',
    'DiagnosticConfidence',
    'AIDiagnosticResult',
    'AIDiagnosticService'
]