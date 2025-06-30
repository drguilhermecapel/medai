# tests/unit/test_validation_service.py
"""
Testes unitários para o serviço de validação do MedAI.
Cobre validação de dados médicos, exames, diagnósticos e regras de negócio.
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Any

from app.services.validation_service import (
    ValidationService,
    ValidationError,
    ValidationResult,
    PatientValidator,
    ExamValidator,
    DiagnosticValidator,
    MedicalDataValidator,
    validate_cpf,
    validate_phone,
    validate_email,
    validate_date_range,
    validate_medical_values,
    validate_icd10_code,
    validate_medication_dosage
)


class TestBasicValidators:
    """Testes para validadores básicos."""
    
    def test_validate_cpf_valid(self):
        """Testa validação de CPF válido."""
        valid_cpfs = [
            "11144477735",
            "111.444.777-35",
            "12345678909",
            "123.456.789-09"
        ]
        
        for cpf in valid_cpfs:
            assert validate_cpf(cpf) is True
    
    def test_validate_cpf_invalid(self):
        """Testa validação de CPF inválido."""
        invalid_cpfs = [
            "00000000000",
            "11111111111",
            "12345678901",  # Dígito verificador errado
            "123.456.789-10",  # Dígito verificador errado
            "12345",  # Muito curto
            "abc12345678",  # Letras
            None,
            ""
        ]
        
        for cpf in invalid_cpfs:
            assert validate_cpf(cpf) is False
    
    def test_validate_phone_valid(self):
        """Testa validação de telefone válido."""
        valid_phones = [
            "11999999999",
            "(11) 99999-9999",
            "(11) 9999-9999",
            "1199999999",
            "+5511999999999",
            "011999999999"
        ]
        
        for phone in valid_phones:
            assert validate_phone(phone) is True
    
    def test_validate_phone_invalid(self):
        """Testa validação de telefone inválido."""
        invalid_phones = [
            "9999",  # Muito curto
            "119999",  # Incompleto
            "(11) 9999-999",  # Formato errado
            "abcdefghijk",  # Letras
            "",
            None
        ]
        
        for phone in invalid_phones:
            assert validate_phone(phone) is False
    
    def test_validate_email_valid(self):
        """Testa validação de email válido."""
        valid_emails = [
            "user@example.com",
            "test.user@medai.com.br",
            "patient+tag@hospital.org",
            "dr.smith@clinic.med.br"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Testa validação de email inválido."""
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "user space@example.com",
            "user@exam ple.com",
            "",
            None
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False


class TestDateValidation:
    """Testes para validação de datas."""
    
    def test_validate_date_range_valid(self):
        """Testa validação de intervalo de datas válido."""
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        
        assert validate_date_range(start, end) is True
    
    def test_validate_date_range_invalid(self):
        """Testa validação de intervalo de datas inválido."""
        # Data final antes da inicial
        start = date(2024, 12, 31)
        end = date(2024, 1, 1)
        
        with pytest.raises(ValidationError, match="Data final deve ser após"):
            validate_date_range(start, end)
    
    def test_validate_date_range_same_day(self):
        """Testa validação com mesma data."""
        same_date = date(2024, 6, 15)
        
        assert validate_date_range(same_date, same_date) is True
    
    def test_validate_date_range_max_interval(self):
        """Testa validação com intervalo máximo."""
        start = date(2020, 1, 1)
        end = date(2025, 1, 1)
        max_days = 365  # 1 ano
        
        with pytest.raises(ValidationError, match="Intervalo máximo"):
            validate_date_range(start, end, max_days=max_days)


class TestPatientValidator:
    """Testes para validador de pacientes."""
    
    @pytest.fixture
    def patient_validator(self):
        return PatientValidator()
    
    def test_validate_patient_data_valid(self, patient_validator):
        """Testa validação de dados válidos de paciente."""
        patient_data = {
            "name": "João Silva Santos",
            "cpf": "11144477735",
            "birth_date": "1980-05-15",
            "gender": "M",
            "phone": "(11) 99999-9999",
            "email": "joao.silva@email.com",
            "address": "Rua das Flores, 123",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01234-567"
        }
        
        result = patient_validator.validate(patient_data)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_patient_data_invalid(self, patient_validator):
        """Testa validação de dados inválidos de paciente."""
        patient_data = {
            "name": "JS",  # Nome muito curto
            "cpf": "12345678901",  # CPF inválido
            "birth_date": "2030-01-01",  # Data futura
            "gender": "X",  # Gênero inválido
            "phone": "9999",  # Telefone inválido
            "email": "invalid.email",  # Email inválido
        }
        
        result = patient_validator.validate(patient_data)
        assert result.is_valid is False
        assert len(result.errors) >= 6
        assert any("nome" in error.lower() for error in result.errors)
        assert any("cpf" in error.lower() for error in result.errors)
    
    def test_validate_patient_age_restrictions(self, patient_validator):
        """Testa validação de restrições de idade."""
        # Paciente muito jovem (recém-nascido)
        patient_data = {
            "name": "Bebê Silva",
            "birth_date": datetime.now().date().isoformat(),
            "gender": "F",
            "responsible_name": "Maria Silva",
            "responsible_cpf": "11144477735"
        }
        
        result = patient_validator.validate(patient_data)
        assert result.is_valid is True  # Válido com responsável
        
        # Sem responsável para menor
        patient_data.pop("responsible_name")
        patient_data.pop("responsible_cpf")
        result = patient_validator.validate(patient_data)
        assert result.is_valid is False
        assert any("responsável" in error.lower() for error in result.errors)
    
    def test_validate_patient_medical_history(self, patient_validator):
        """Testa validação de histórico médico."""
        patient_data = {
            "name": "Maria Santos",
            "medical_history": {
                "chronic_conditions": ["Diabetes", "Hipertensão"],
                "allergies": ["Penicilina", "Dipirona"],
                "surgeries": [
                    {"name": "Apendicectomia", "date": "2020-03-15"},
                    {"name": "Colecistectomia", "date": "2022-08-20"}
                ],
                "medications": [
                    {"name": "Metformina", "dosage": "850mg", "frequency": "2x ao dia"},
                    {"name": "Losartana", "dosage": "50mg", "frequency": "1x ao dia"}
                ]
            }
        }
        
        result = patient_validator.validate_medical_history(patient_data["medical_history"])
        assert result.is_valid is True


class TestExamValidator:
    """Testes para validador de exames."""
    
    @pytest.fixture
    def exam_validator(self):
        return ExamValidator()
    
    def test_validate_blood_test_valid(self, exam_validator):
        """Testa validação de exame de sangue válido."""
        exam_data = {
            "exam_type": "blood_test",
            "exam_date": datetime.now().date().isoformat(),
            "results": {
                "hemoglobin": 14.5,
                "hematocrit": 42.0,
                "glucose": 95,
                "cholesterol_total": 180,
                "cholesterol_hdl": 55,
                "cholesterol_ldl": 100,
                "triglycerides": 125,
                "creatinine": 0.9,
                "urea": 30
            }
        }
        
        result = exam_validator.validate(exam_data)
        assert result.is_valid is True
        assert len(result.warnings) == 0
    
    def test_validate_blood_test_out_of_range(self, exam_validator):
        """Testa validação com valores fora da faixa."""
        exam_data = {
            "exam_type": "blood_test",
            "results": {
                "glucose": 250,  # Alto
                "cholesterol_total": 280,  # Alto
                "cholesterol_hdl": 30,  # Baixo
                "triglycerides": 400  # Muito alto
            }
        }
        
        result = exam_validator.validate_blood_test(exam_data["results"])
        assert result.is_valid is True  # Ainda válido, mas com avisos
        assert len(result.warnings) >= 4
        assert any("glucose" in warning.lower() for warning in result.warnings)
        assert any("colesterol" in warning.lower() for warning in result.warnings)
    
    def test_validate_imaging_exam(self, exam_validator):
        """Testa validação de exame de imagem."""
        exam_data = {
            "exam_type": "mri",
            "exam_date": datetime.now().date().isoformat(),
            "body_region": "brain",
            "contrast_used": True,
            "findings": {
                "description": "Exame sem alterações significativas",
                "measurements": {
                    "ventricle_size": "normal",
                    "cortical_thickness": "preserved"
                }
            },
            "images": [
                {"sequence": "T1", "slices": 20},
                {"sequence": "T2", "slices": 20},
                {"sequence": "FLAIR", "slices": 20}
            ]
        }
        
        result = exam_validator.validate_imaging_exam(exam_data)
        assert result.is_valid is True
    
    def test_validate_exam_date_constraints(self, exam_validator):
        """Testa validação de restrições de data do exame."""
        # Exame futuro
        future_exam = {
            "exam_type": "blood_test",
            "exam_date": (datetime.now() + timedelta(days=7)).date().isoformat()
        }
        
        result = exam_validator.validate(future_exam)
        assert result.is_valid is False
        assert any("futura" in error.lower() for error in result.errors)
        
        # Exame muito antigo
        old_exam = {
            "exam_type": "blood_test",
            "exam_date": "1990-01-01"
        }
        
        result = exam_validator.validate(old_exam)
        assert len(result.warnings) > 0
        assert any("antigo" in warning.lower() for warning in result.warnings)


class TestDiagnosticValidator:
    """Testes para validador de diagnósticos."""
    
    @pytest.fixture
    def diagnostic_validator(self):
        return DiagnosticValidator()
    
    def test_validate_diagnostic_valid(self, diagnostic_validator):
        """Testa validação de diagnóstico válido."""
        diagnostic_data = {
            "patient_id": 1,
            "exam_id": 1,
            "diagnostic_text": "Paciente apresenta quadro compatível com diabetes mellitus tipo 2, "
                             "evidenciado por glicemia de jejum elevada (126 mg/dL) e hemoglobina "
                             "glicada de 7.2%. Recomenda-se início de tratamento medicamentoso.",
            "icd10_codes": ["E11.9", "E78.5"],
            "severity": "moderate",
            "confidence": 0.85,
            "recommendations": [
                "Iniciar metformina 500mg 2x ao dia",
                "Orientação nutricional",
                "Atividade física regular",
                "Retorno em 3 meses"
            ]
        }
        
        result = diagnostic_validator.validate(diagnostic_data)
        assert result.is_valid is True
    
    def test_validate_icd10_codes(self, diagnostic_validator):
        """Testa validação de códigos ICD-10."""
        valid_codes = ["A00.0", "E11.9", "I10", "J45.0", "M79.3"]
        
        for code in valid_codes:
            assert validate_icd10_code(code) is True
        
        invalid_codes = ["A00", "XX99.9", "E111.9", "123.4", ""]
        
        for code in invalid_codes:
            assert validate_icd10_code(code) is False
    
    def test_validate_diagnostic_consistency(self, diagnostic_validator):
        """Testa validação de consistência do diagnóstico."""
        # Diagnóstico inconsistente
        diagnostic_data = {
            "diagnostic_text": "Paciente saudável, sem alterações.",
            "severity": "critical",  # Inconsistente
            "recommendations": [
                "Internação urgente",  # Inconsistente
                "UTI"
            ]
        }
        
        result = diagnostic_validator.validate_consistency(diagnostic_data)
        assert result.is_valid is False
        assert any("inconsistente" in error.lower() for error in result.errors)
    
    def test_validate_ai_analysis(self, diagnostic_validator):
        """Testa validação de análise de IA."""
        ai_analysis = {
            "confidence": 0.92,
            "model_version": "v2.1.0",
            "risk_factors": [
                {"factor": "glucose", "weight": 0.35, "value": 126},
                {"factor": "bmi", "weight": 0.25, "value": 28.5},
                {"factor": "family_history", "weight": 0.20, "value": True}
            ],
            "differential_diagnosis": [
                {"condition": "Diabetes tipo 2", "probability": 0.85},
                {"condition": "Pré-diabetes", "probability": 0.12},
                {"condition": "Síndrome metabólica", "probability": 0.03}
            ]
        }
        
        result = diagnostic_validator.validate_ai_analysis(ai_analysis)
        assert result.is_valid is True
        
        # Confidence muito baixa
        ai_analysis["confidence"] = 0.45
        result = diagnostic_validator.validate_ai_analysis(ai_analysis)
        assert len(result.warnings) > 0


class TestMedicalDataValidator:
    """Testes para validador de dados médicos gerais."""
    
    @pytest.fixture
    def medical_validator(self):
        return MedicalDataValidator()
    
    def test_validate_vital_signs(self, medical_validator):
        """Testa validação de sinais vitais."""
        vital_signs = {
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 75,
            "respiratory_rate": 16,
            "temperature": 36.5,
            "oxygen_saturation": 98
        }
        
        result = medical_validator.validate_vital_signs(vital_signs)
        assert result.is_valid is True
        
        # Valores anormais
        abnormal_vitals = {
            "blood_pressure_systolic": 180,  # Alta
            "blood_pressure_diastolic": 110,  # Alta
            "heart_rate": 130,  # Taquicardia
            "temperature": 39.5,  # Febre alta
            "oxygen_saturation": 88  # Baixa
        }
        
        result = medical_validator.validate_vital_signs(abnormal_vitals)
        assert result.is_valid is True  # Ainda válido
        assert len(result.warnings) >= 5  # Mas com avisos
    
    def test_validate_medication_dosage(self):
        """Testa validação de dosagem de medicamentos."""
        valid_dosages = [
            {"medication": "Paracetamol", "dosage": "500mg", "frequency": "6/6h"},
            {"medication": "Amoxicilina", "dosage": "875mg", "frequency": "12/12h"},
            {"medication": "Omeprazol", "dosage": "20mg", "frequency": "1x ao dia"}
        ]
        
        for med in valid_dosages:
            assert validate_medication_dosage(
                med["medication"], 
                med["dosage"], 
                med["frequency"]
            ) is True
        
        # Dosagem excessiva
        result = validate_medication_dosage(
            "Paracetamol", 
            "2000mg",  # Muito alto para dose única
            "4/4h"
        )
        assert result is False
    
    def test_validate_lab_results_correlation(self, medical_validator):
        """Testa validação de correlação entre resultados laboratoriais."""
        lab_results = {
            "ast": 150,  # Elevado
            "alt": 180,  # Elevado
            "ggt": 200,  # Elevado
            "bilirubin_total": 3.5,  # Elevado
            "albumin": 2.8  # Baixo
        }
        
        result = medical_validator.validate_lab_correlation(lab_results)
        assert len(result.warnings) > 0
        assert any("hepática" in warning.lower() for warning in result.warnings)


class TestValidationService:
    """Testes para o serviço de validação principal."""
    
    @pytest.fixture
    def validation_service(self):
        return ValidationService()
    
    def test_validate_complete_patient_record(self, validation_service):
        """Testa validação de registro completo de paciente."""
        patient_record = {
            "patient": {
                "name": "Ana Maria Silva",
                "cpf": "11144477735",
                "birth_date": "1975-03-20",
                "gender": "F"
            },
            "exams": [
                {
                    "exam_type": "blood_test",
                    "exam_date": datetime.now().date().isoformat(),
                    "results": {"glucose": 110, "cholesterol_total": 190}
                }
            ],
            "diagnostics": [
                {
                    "diagnostic_text": "Pré-diabetes identificado",
                    "icd10_codes": ["R73.0"],
                    "severity": "mild"
                }
            ]
        }
        
        result = validation_service.validate_patient_record(patient_record)
        assert result.is_valid is True
    
    def test_validate_with_business_rules(self, validation_service):
        """Testa validação com regras de negócio."""
        # Regra: Exame de gravidez só para mulheres
        invalid_exam = {
            "patient": {"gender": "M"},
            "exam": {"exam_type": "pregnancy_test", "result": "positive"}
        }
        
        result = validation_service.validate_with_rules(invalid_exam)
        assert result.is_valid is False
        assert any("gravidez" in error.lower() for error in result.errors)
    
    def test_validation_performance(self, validation_service):
        """Testa performance da validação em lote."""
        import time
        
        # Cria 1000 registros de paciente
        records = []
        for i in range(1000):
            records.append({
                "name": f"Paciente {i}",
                "cpf": "11144477735",
                "birth_date": "1980-01-01"
            })
        
        start_time = time.time()
        results = validation_service.validate_batch(records)
        end_time = time.time()
        
        # Deve processar 1000 registros em menos de 1 segundo
        assert (end_time - start_time) < 1.0
        assert len(results) == 1000
        assert all(r.is_valid for r in results)