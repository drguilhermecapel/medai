"""
Testes para os algoritmos médicos otimizados
Verifica se as melhorias mantêm a funcionalidade e segurança
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.modules.farmacia.validador_prescricoes import ValidadorPrescricoesIA
from app.services.laboratory_exam_service import LaboratoryExamService
from app.services.medical_guidelines_service import MedicalGuidelinesService
from app.services.clinical_protocols_service import ClinicalProtocolsService


class TestOptimizedPrescriptionValidation:
    """Testa validação de prescrições otimizada"""
    
    def setup_method(self):
        self.validador = ValidadorPrescricoesIA()
    
    @pytest.mark.asyncio
    async def test_enhanced_drug_interactions(self):
        """Testa detecção de interações medicamentosas aprimorada"""
        
        prescricao = {
            'medicamentos': [
                {'nome': 'warfarina', 'dose': '5mg'},
                {'nome': 'aspirina', 'dose': '100mg'}
            ]
        }
        
        resultado = await self.validador.detectar_interacoes_graves(prescricao)
        
        assert len(resultado['interacoes_detectadas']) > 0
        assert 'sangramento' in resultado['interacoes_detectadas'][0]['descricao'].lower()
    
    @pytest.mark.asyncio
    async def test_pharmacogenetic_analysis(self):
        """Testa análise farmacogenética aprimorada"""
        
        prescricao = {
            'paciente': {
                'polimorfismos_geneticos': {
                    'CYP2C19': '*2/*2',
                    'HLA_B5701': 'positivo'
                }
            },
            'medicamentos': [
                {'nome': 'clopidogrel', 'dose': '75mg'},
                {'nome': 'abacavir', 'dose': '300mg'}
            ]
        }
        
        resultado = await self.validador.analisar_polimorfismos_geneticos(prescricao)
        
        assert len(resultado['recomendacoes_geneticas']) >= 2
        assert any('CONTRAINDICAÇÃO' in rec.get('recomendacao', '') for rec in resultado['recomendacoes_geneticas'])
        assert 'CPIC' in resultado['diretrizes_aplicadas']
    
    @pytest.mark.asyncio
    async def test_contraindication_checking(self):
        """Testa verificação de contraindicações expandida"""
        
        prescricao = {
            'paciente': {
                'condicoes_clinicas': ['asma_bronquica', 'gravidez']
            },
            'medicamentos': [
                {'nome': 'propranolol', 'dose': '40mg'},
                {'nome': 'enalapril', 'dose': '10mg'}
            ]
        }
        
        resultado = await self.validador.verificar_contraindicacoes(prescricao)
        
        assert len(resultado['contraindicacoes_detectadas']) >= 2
        assert not resultado['aprovado']


class TestLaboratoryExamService:
    """Testa serviço de exames laboratoriais"""
    
    def setup_method(self):
        self.exam_service = LaboratoryExamService()
    
    @pytest.mark.asyncio
    async def test_intelligent_exam_recommendation(self):
        """Testa recomendação inteligente de exames"""
        
        paciente = {
            'idade': 55,
            'sexo': 'masculino',
            'comorbidades': ['diabetes', 'hipertensao']
        }
        
        contexto_clinico = {
            'sintomas': ['dor_toracica', 'dispneia'],
            'hipotese_diagnostica': 'infarto_agudo_miocardio'
        }
        
        resultado = await self.exam_service.solicitar_exames_inteligente(paciente, contexto_clinico)
        
        assert len(resultado['exames_recomendados']) > 0
        assert resultado['prioridade_geral'] in ['urgente', 'alta', 'rotina']
        assert resultado['custo_estimado'] > 0
        assert len(resultado['diretrizes_aplicadas']) > 0
    
    def test_exam_optimization(self):
        """Testa otimização de solicitação de exames"""
        
        exames_brutos = ['glicemia', 'ureia', 'creatinina', 'sodio', 'potassio']
        
        resultado = self.exam_service._otimizar_solicitacao_exames(exames_brutos)
        
        assert len(resultado) < len(exames_brutos)
        assert any(exame.get('tipo') == 'grupo' for exame in resultado)
    
    def test_exam_priority_determination(self):
        """Testa determinação de prioridade de exames"""
        
        prioridade_urgente = self.exam_service._determinar_prioridade_exame('troponina_i')
        prioridade_rotina = self.exam_service._determinar_prioridade_exame('colesterol_total')
        
        assert prioridade_urgente.value == 'urgente'
        assert prioridade_rotina.value == 'rotina'


class TestMedicalGuidelinesService:
    """Testa serviço de diretrizes médicas"""
    
    def setup_method(self):
        self.guidelines_service = MedicalGuidelinesService()
    
    def test_guideline_retrieval(self):
        """Testa recuperação de diretrizes"""
        
        guideline = self.guidelines_service.get_current_guideline('diabetes')
        
        assert guideline['condition'] == 'diabetes'
        assert 'guideline' in guideline
        assert guideline['guideline']['organization'].value == 'sbd'
    
    def test_treatment_compliance_validation(self):
        """Testa validação de conformidade com tratamento"""
        
        treatment_plan = {
            'patient_age': 50,
            'current_hba1c': 8.5,
            'blood_pressure_systolic': 150,
            'comorbidities': ['diabetes']
        }
        
        resultado = self.guidelines_service.validate_treatment_compliance(treatment_plan, 'diabetes')
        
        assert 'compliant' in resultado
        assert 'compliance_score' in resultado
        assert 'violations' in resultado
        assert 'recommendations' in resultado
    
    def test_pharmacogenetic_recommendations(self):
        """Testa recomendações farmacogenéticas"""
        
        patient_genetics = {
            'CYP2C9': '*2/*2',
            'VKORC1': 'AA'
        }
        
        resultado = self.guidelines_service.get_drug_guideline_recommendations('warfarina', patient_genetics)
        
        assert len(resultado['genetic_recommendations']) > 0
        assert resultado['organization'].value == 'cpic'


class TestClinicalProtocolsService:
    """Testa serviços de protocolos clínicos expandidos"""
    
    def setup_method(self):
        self.protocols_service = ClinicalProtocolsService()
    
    @pytest.mark.asyncio
    async def test_diabetes_protocol_assessment(self):
        """Testa avaliação do protocolo de diabetes"""
        
        patient_data = {
            'age': 50,
            'bmi': 28
        }
        
        clinical_data = {
            'lab_values': {
                'fasting_glucose': 140,
                'hba1c': 7.2
            }
        }
        
        resultado = await self.protocols_service.assess_protocol('diabetes', patient_data, clinical_data)
        
        assert resultado['applicable']
        assert resultado['score'] >= 2
        assert len(resultado['recommendations']) > 0
    
    @pytest.mark.asyncio
    async def test_hypertension_protocol_assessment(self):
        """Testa avaliação do protocolo de hipertensão"""
        
        patient_data = {
            'age': 65,
            'risk_factors': ['diabetes', 'smoking']
        }
        
        clinical_data = {
            'vital_signs': {
                'systolic_blood_pressure': 160,
                'diastolic_blood_pressure': 95
            }
        }
        
        resultado = await self.protocols_service.assess_protocol('hypertension', patient_data, clinical_data)
        
        assert resultado['applicable']
        assert resultado['risk_level'] in ['low', 'moderate', 'high']
        assert len(resultado['recommendations']) > 0
    
    @pytest.mark.asyncio
    async def test_copd_protocol_assessment(self):
        """Testa avaliação do protocolo de DPOC"""
        
        patient_data = {
            'smoking_pack_years': 30
        }
        
        clinical_data = {
            'pulmonary_function': {
                'fev1_percent': 45
            },
            'symptoms': ['dyspnea', 'chronic_cough']
        }
        
        resultado = await self.protocols_service.assess_protocol('copd', patient_data, clinical_data)
        
        assert resultado['applicable']
        assert resultado['score'] >= 2
        assert len(resultado['recommendations']) > 0


class TestIntegrationOptimizations:
    """Testa integrações entre componentes otimizados"""
    
    @pytest.mark.asyncio
    async def test_prescription_with_guidelines_integration(self):
        """Testa integração entre prescrição e diretrizes"""
        
        validador = ValidadorPrescricoesIA()
        guidelines_service = MedicalGuidelinesService()
        
        prescricao = {
            'paciente': {
                'idade': 70,
                'comorbidades': ['diabetes', 'insuficiencia_renal'],
                'polimorfismos_geneticos': {'CYP2C9': '*2/*2'}
            },
            'medicamentos': [
                {'nome': 'metformina', 'dose': '850mg'},
                {'nome': 'warfarina', 'dose': '5mg'}
            ]
        }
        
        validacao = await validador.validar_prescricao_completa(prescricao)
        
        treatment_plan = {
            'patient_age': 70,
            'comorbidities': ['diabetes'],
            'medications': ['metformina', 'warfarina']
        }
        
        compliance = guidelines_service.validate_treatment_compliance(treatment_plan, 'diabetes')
        
        assert 'score_seguranca' in validacao
        assert 'compliance_score' in compliance
        assert validacao['score_seguranca'] >= 0
        assert compliance['compliance_score'] >= 0
    
    def test_exam_service_with_protocols_integration(self):
        """Testa integração entre serviço de exames e protocolos"""
        
        exam_service = LaboratoryExamService()
        protocols = exam_service.exam_protocols
        
        assert 'diabetes_screening' in protocols
        assert 'funcao_renal' in protocols
        assert 'marcadores_cardiacos' in protocols
        
        for protocol_name, protocol_data in protocols.items():
            assert 'exames' in protocol_data
            assert 'diretriz' in protocol_data
            assert 'prioridade' in protocol_data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
