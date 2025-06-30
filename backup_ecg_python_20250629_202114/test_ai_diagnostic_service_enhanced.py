"""
Testes abrangentes para o AI Diagnostic Service - Componente Crítico
Meta: 100% de cobertura
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from app.services.ai_diagnostic_service import AIDiagnosticService
from app.models import Patient, Diagnosis
from app.schemas.ai_diagnostic import (
    DiagnosticRequest,
    DiagnosticResponse,
    SymptomInput,
    VitalSignsInput
)
from app.core.exceptions import (
    InvalidInputError,
    DiagnosticError,
    ServiceUnavailableError
)

@pytest.mark.critical
class TestAIDiagnosticServiceCritical:
    """Testes críticos do AI Diagnostic Service com 100% de cobertura"""
    
    @pytest.mark.asyncio
    async def test_diagnose_respiratory_condition(self, ai_diagnostic_service, test_patient, sample_medical_data):
        """Testa diagnóstico de condição respiratória"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=["tosse", "febre", "falta de ar"],
            duration_days=3,
            vital_signs=VitalSignsInput(
                temperature=38.5,
                blood_pressure="120/80",
                heart_rate=90,
                respiratory_rate=22,
                oxygen_saturation=94
            ),
            medical_history=["asma"],
            current_medications=["salbutamol"]
        )
        
        # Act
        result = await ai_diagnostic_service.diagnose(request)
        
        # Assert
        assert result is not None
        assert result.primary_diagnosis in ["Pneumonia", "COVID-19", "COPD Exacerbation", "Asthma"]
        assert result.confidence > 0.7
        assert len(result.differential_diagnoses) >= 2
        assert len(result.recommendations) >= 3
        assert result.severity in ["low", "moderate", "high"]
        assert len(result.icd10_codes) > 0
        
    @pytest.mark.asyncio
    async def test_diagnose_cardiovascular_condition(self, ai_diagnostic_service, test_patient):
        """Testa diagnóstico de condição cardiovascular"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=["dor no peito", "sudorese", "náusea"],
            duration_days=0,  # Início súbito
            vital_signs=VitalSignsInput(
                temperature=36.8,
                blood_pressure="160/100",
                heart_rate=110,
                respiratory_rate=20,
                oxygen_saturation=96
            ),
            medical_history=["hipertensão", "diabetes"],
            current_medications=["losartana", "metformina"]
        )
        
        # Act
        result = await ai_diagnostic_service.diagnose(request)
        
        # Assert
        assert result.severity in ["moderate", "high"]
        assert any("urgente" in rec.lower() or "emergência" in rec.lower() 
                  for rec in result.recommendations)
        
    @pytest.mark.asyncio
    async def test_diagnose_with_lab_results(self, ai_diagnostic_service, test_patient, sample_medical_data):
        """Testa diagnóstico com resultados laboratoriais"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=sample_medical_data["symptoms"],
            duration_days=sample_medical_data["duration_days"],
            vital_signs=VitalSignsInput(**sample_medical_data["vital_signs"]),
            lab_results=sample_medical_data["lab_results"]
        )
        
        # Act
        result = await ai_diagnostic_service.diagnose(request)
        
        # Assert
        assert result is not None
        assert result.lab_findings is not None
        assert "leukocytes" in str(result.lab_findings)  # Leucócitos elevados
        
    @pytest.mark.asyncio
    async def test_diagnose_invalid_symptoms(self, ai_diagnostic_service, test_patient):
        """Testa diagnóstico com sintomas inválidos"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=[],  # Sem sintomas
            duration_days=1,
            vital_signs=VitalSignsInput(
                temperature=36.5,
                blood_pressure="120/80",
                heart_rate=70,
                respiratory_rate=16,
                oxygen_saturation=98
            )
        )
        
        # Act & Assert
        with pytest.raises(InvalidInputError) as exc_info:
            await ai_diagnostic_service.diagnose(request)
            
        assert "At least one symptom is required" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_diagnose_service_unavailable(self, ai_diagnostic_service, test_patient, sample_medical_data):
        """Testa comportamento quando serviço AI está indisponível"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=sample_medical_data["symptoms"],
            duration_days=sample_medical_data["duration_days"],
            vital_signs=VitalSignsInput(**sample_medical_data["vital_signs"])
        )
        
        # Mock falha do serviço
        with patch.object(ai_diagnostic_service._ai_engine, 'diagnose') as mock_diagnose:
            mock_diagnose.side_effect = Exception("AI service unavailable")
            
            # Act & Assert
            with pytest.raises(ServiceUnavailableError):
                await ai_diagnostic_service.diagnose(request)
                
    @pytest.mark.asyncio
    async def test_diagnose_timeout(self, ai_diagnostic_service, test_patient, sample_medical_data):
        """Testa timeout no diagnóstico"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=sample_medical_data["symptoms"],
            duration_days=sample_medical_data["duration_days"],
            vital_signs=VitalSignsInput(**sample_medical_data["vital_signs"])
        )
        
        # Mock para simular processamento lento
        async def slow_diagnose(*args, **kwargs):
            await asyncio.sleep(35)  # Excede timeout de 30s
            
        with patch.object(ai_diagnostic_service._ai_engine, 'diagnose', side_effect=slow_diagnose):
            # Act & Assert
            with pytest.raises(DiagnosticError) as exc_info:
                await ai_diagnostic_service.diagnose(request)
                
            assert "timeout" in str(exc_info.value).lower()
            
    @pytest.mark.asyncio
    async def test_save_diagnosis(self, ai_diagnostic_service, db_session, test_patient):
        """Testa salvamento de diagnóstico no banco"""
        # Arrange
        diagnosis_data = {
            "patient_id": test_patient.id,
            "primary_diagnosis": "Pneumonia",
            "icd10_codes": ["J18.9"],
            "confidence": 0.89,
            "severity": "moderate",
            "differential_diagnoses": [
                {"diagnosis": "COVID-19", "probability": 0.65},
                {"diagnosis": "Bronchitis", "probability": 0.45}
            ],
            "recommendations": [
                "Antibioticoterapia",
                "Radiografia de tórax",
                "Hemograma completo"
            ]
        }
        
        # Act
        saved_diagnosis = await ai_diagnostic_service.save_diagnosis(diagnosis_data)
        
        # Assert
        assert saved_diagnosis.id is not None
        assert saved_diagnosis.patient_id == test_patient.id
        assert saved_diagnosis.primary_diagnosis == "Pneumonia"
        
        # Verifica no banco
        diagnosis_in_db = await db_session.get(Diagnosis, saved_diagnosis.id)
        assert diagnosis_in_db is not None
        
    @pytest.mark.asyncio
    async def test_get_patient_diagnosis_history(self, ai_diagnostic_service, db_session, test_patient):
        """Testa recuperação de histórico de diagnósticos"""
        # Arrange - Cria múltiplos diagnósticos
        for i in range(5):
            diagnosis = Diagnosis(
                patient_id=test_patient.id,
                primary_diagnosis=f"Diagnosis {i}",
                confidence=0.8 + i * 0.02,
                severity="moderate" if i % 2 == 0 else "low",
                icd10_codes=[f"A0{i}.0"]
            )
            db_session.add(diagnosis)
        await db_session.commit()
        
        # Act
        history = await ai_diagnostic_service.get_patient_history(test_patient.id, limit=3)
        
        # Assert
        assert len(history) == 3
        assert all(d.patient_id == test_patient.id for d in history)
        
    @pytest.mark.asyncio
    async def test_diagnose_with_red_flags(self, ai_diagnostic_service, test_patient):
        """Testa identificação de red flags"""
        # Arrange - Sintomas críticos
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=["dor no peito intensa", "falta de ar súbita", "sudorese fria"],
            duration_days=0,
            vital_signs=VitalSignsInput(
                temperature=36.5,
                blood_pressure="90/60",  # Hipotensão
                heart_rate=130,  # Taquicardia
                respiratory_rate=28,  # Taquipneia
                oxygen_saturation=88  # Hipóxia
            )
        )
        
        # Act
        result = await ai_diagnostic_service.diagnose(request)
        
        # Assert
        assert result.severity == "high"
        assert result.red_flags is not None
        assert len(result.red_flags) > 0
        assert any("emergência" in rec.lower() for rec in result.recommendations)
        
    @pytest.mark.asyncio
    async def test_diagnose_pediatric_patient(self, ai_diagnostic_service, db_session):
        """Testa diagnóstico para paciente pediátrico"""
        # Arrange - Criar paciente criança
        child_patient = Patient(
            name="Ana Silva",
            birth_date=datetime(2019, 1, 1),  # 5 anos
            gender="F",
            cpf="12345678901",
            medical_record_number="PED001"
        )
        db_session.add(child_patient)
        await db_session.commit()
        
        request = DiagnosticRequest(
            patient_id=child_patient.id,
            symptoms=["febre", "irritabilidade", "recusa alimentar"],
            duration_days=2,
            vital_signs=VitalSignsInput(
                temperature=39.0,
                blood_pressure="90/60",
                heart_rate=120,  # Normal para idade
                respiratory_rate=25,
                oxygen_saturation=97
            )
        )
        
        # Act
        result = await ai_diagnostic_service.diagnose(request)
        
        # Assert
        assert result is not None
        assert "pediátrico" in result.notes or "criança" in result.notes
        
    @pytest.mark.asyncio
    async def test_diagnose_with_allergies(self, ai_diagnostic_service, test_patient):
        """Testa diagnóstico considerando alergias"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=["urticária", "edema", "prurido"],
            duration_days=0,
            vital_signs=VitalSignsInput(
                temperature=36.8,
                blood_pressure="110/70",
                heart_rate=85,
                respiratory_rate=18,
                oxygen_saturation=97
            ),
            allergies=["penicilina", "dipirona"],
            recent_medications=["amoxicilina"]  # Penicilina!
        )
        
        # Act
        result = await ai_diagnostic_service.diagnose(request)
        
        # Assert
        assert any("alergia" in diag.lower() or "reação" in diag.lower() 
                  for diag in [result.primary_diagnosis] + 
                  [d["diagnosis"] for d in result.differential_diagnoses])
        
    @pytest.mark.asyncio
    async def test_validate_vital_signs(self, ai_diagnostic_service):
        """Testa validação de sinais vitais"""
        # Casos inválidos
        invalid_vitals = [
            {"temperature": 45},  # Muito alta
            {"temperature": 25},  # Muito baixa
            {"heart_rate": 300},  # Impossível
            {"blood_pressure": "300/200"},  # Muito alta
            {"oxygen_saturation": 150},  # > 100%
        ]
        
        for vitals in invalid_vitals:
            valid_vitals = VitalSignsInput(
                temperature=36.5,
                blood_pressure="120/80",
                heart_rate=70,
                respiratory_rate=16,
                oxygen_saturation=98
            )
            
            # Atualiza com valor inválido
            for key, value in vitals.items():
                setattr(valid_vitals, key, value)
                
            # Deve identificar como inválido
            is_valid = ai_diagnostic_service._validate_vital_signs(valid_vitals)
            assert not is_valid
            
    @pytest.mark.asyncio
    @pytest.mark.parametrize("symptoms,expected_category", [
        (["tosse", "febre", "expectoração"], "respiratory"),
        (["dor no peito", "palpitações"], "cardiovascular"),
        (["cefaleia", "tontura", "confusão"], "neurological"),
        (["dor abdominal", "náusea", "vômito"], "gastrointestinal"),
        (["disúria", "polaciúria"], "urological")
    ])
    async def test_symptom_categorization(self, ai_diagnostic_service, symptoms, expected_category):
        """Testa categorização de sintomas"""
        # Act
        category = ai_diagnostic_service._categorize_symptoms(symptoms)
        
        # Assert
        assert category == expected_category

@pytest.mark.critical
class TestAIDiagnosticServiceIntegration:
    """Testes de integração para garantir 100% de cobertura"""
    
    @pytest.mark.asyncio
    async def test_full_diagnostic_workflow(self, ai_diagnostic_service, test_patient, sample_medical_data):
        """Testa workflow completo de diagnóstico"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=sample_medical_data["symptoms"],
            duration_days=sample_medical_data["duration_days"],
            vital_signs=VitalSignsInput(**sample_medical_data["vital_signs"]),
            medical_history=sample_medical_data["medical_history"],
            current_medications=sample_medical_data["medications"],
            allergies=sample_medical_data["allergies"],
            lab_results=sample_medical_data["lab_results"]
        )
        
        # Act - Diagnóstico
        result = await ai_diagnostic_service.diagnose(request)
        
        # Act - Salvar
        saved = await ai_diagnostic_service.save_diagnosis({
            "patient_id": test_patient.id,
            "primary_diagnosis": result.primary_diagnosis,
            "icd10_codes": result.icd10_codes,
            "confidence": result.confidence,
            "severity": result.severity,
            "differential_diagnoses": result.differential_diagnoses,
            "recommendations": result.recommendations
        })
        
        # Act - Recuperar histórico
        history = await ai_diagnostic_service.get_patient_history(test_patient.id)
        
        # Assert
        assert saved.id in [d.id for d in history]
        assert result.processing_time > 0
        
    @pytest.mark.asyncio
    async def test_concurrent_diagnoses(self, ai_diagnostic_service, test_patient, sample_medical_data):
        """Testa diagnósticos concorrentes"""
        # Arrange
        num_concurrent = 10
        requests = []
        
        for i in range(num_concurrent):
            request = DiagnosticRequest(
                patient_id=test_patient.id,
                symptoms=sample_medical_data["symptoms"],
                duration_days=i,
                vital_signs=VitalSignsInput(**sample_medical_data["vital_signs"])
            )
            requests.append(request)
            
        # Act - Executa diagnósticos em paralelo
        tasks = [ai_diagnostic_service.diagnose(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        # Assert
        assert len(results) == num_concurrent
        assert all(r.primary_diagnosis is not None for r in results)
        
    @pytest.mark.asyncio
    async def test_diagnostic_with_cache(self, ai_diagnostic_service, test_patient, sample_medical_data, mock_redis):
        """Testa diagnóstico com cache"""
        # Arrange
        request = DiagnosticRequest(
            patient_id=test_patient.id,
            symptoms=sample_medical_data["symptoms"],
            duration_days=sample_medical_data["duration_days"],
            vital_signs=VitalSignsInput(**sample_medical_data["vital_signs"])
        )
        
        # Act - Primeiro diagnóstico
        result1 = await ai_diagnostic_service.diagnose(request)
        
        # Act - Segundo diagnóstico (deve usar cache)
        mock_redis.get.return_value = result1.json()
        result2 = await ai_diagnostic_service.diagnose(request)
        
        # Assert
        assert result1.primary_diagnosis == result2.primary_diagnosis
        assert mock_redis.set.called