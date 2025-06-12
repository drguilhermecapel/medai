"""
Serviço de integração de diretrizes médicas
Centraliza e gerencia protocolos médicos atualizados
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger('MedAI.Guidelines.MedicalGuidelinesService')


class GuidelineOrganization(str, Enum):
    """Organizações que publicam diretrizes médicas"""
    SBC = "sbc"  # Sociedade Brasileira de Cardiologia
    SBD = "sbd"  # Sociedade Brasileira de Diabetes
    SBEM = "sbem"  # Sociedade Brasileira de Endocrinologia
    SBN = "sbn"  # Sociedade Brasileira de Nefrologia
    SBHH = "sbhh"  # Sociedade Brasileira de Hematologia
    AHA = "aha"  # American Heart Association
    ESC = "esc"  # European Society of Cardiology
    NCCN = "nccn"  # National Comprehensive Cancer Network
    ESMO = "esmo"  # European Society for Medical Oncology
    CPIC = "cpic"  # Clinical Pharmacogenetics Implementation Consortium


class EvidenceLevel(str, Enum):
    """Níveis de evidência científica"""
    LEVEL_1A = "1A"  # Meta-análise de estudos randomizados
    LEVEL_1B = "1B"  # Estudo randomizado individual
    LEVEL_2A = "2A"  # Estudo de coorte bem desenhado
    LEVEL_2B = "2B"  # Estudo de coorte menos rigoroso
    LEVEL_3 = "3"    # Estudo caso-controle
    LEVEL_4 = "4"    # Série de casos
    LEVEL_5 = "5"    # Opinião de especialistas


class MedicalGuidelinesService:
    """Serviço para gestão de diretrizes médicas"""
    
    def __init__(self):
        self.guidelines_db = self._load_guidelines_database()
        self.version_control = self._initialize_version_control()
        self.compliance_checker = self._initialize_compliance_checker()
    
    def _load_guidelines_database(self) -> Dict[str, Any]:
        """Carrega base de dados de diretrizes médicas atualizadas"""
        return {
            'diabetes': {
                'organization': GuidelineOrganization.SBD,
                'version': '2023',
                'last_updated': '2023-12-01',
                'diagnostic_criteria': {
                    'fasting_glucose': {'threshold': 126, 'unit': 'mg/dL', 'evidence': EvidenceLevel.LEVEL_1A},
                    'hba1c': {'threshold': 6.5, 'unit': '%', 'evidence': EvidenceLevel.LEVEL_1A},
                    'random_glucose': {'threshold': 200, 'unit': 'mg/dL', 'evidence': EvidenceLevel.LEVEL_1A}
                },
                'treatment_targets': {
                    'hba1c_general': {'target': 7.0, 'unit': '%'},
                    'hba1c_elderly': {'target': 8.0, 'unit': '%'},
                    'blood_pressure': {'systolic': 130, 'diastolic': 80, 'unit': 'mmHg'},
                    'ldl_cholesterol': {'target': 70, 'unit': 'mg/dL'}
                },
                'monitoring_frequency': {
                    'hba1c': 'trimestral',
                    'microalbuminuria': 'anual',
                    'fundoscopia': 'anual',
                    'lipid_profile': 'anual'
                }
            },
            'hypertension': {
                'organization': GuidelineOrganization.SBC,
                'version': '2023',
                'last_updated': '2023-10-15',
                'diagnostic_criteria': {
                    'stage_1': {'systolic': 140, 'diastolic': 90, 'unit': 'mmHg'},
                    'stage_2': {'systolic': 160, 'diastolic': 100, 'unit': 'mmHg'},
                    'stage_3': {'systolic': 180, 'diastolic': 110, 'unit': 'mmHg'}
                },
                'treatment_targets': {
                    'general': {'systolic': 130, 'diastolic': 80},
                    'diabetes': {'systolic': 130, 'diastolic': 80},
                    'elderly': {'systolic': 140, 'diastolic': 90},
                    'ckd': {'systolic': 130, 'diastolic': 80}
                },
                'first_line_drugs': ['ace_inhibitors', 'arb', 'thiazide_diuretics', 'calcium_blockers']
            },
            'dyslipidemia': {
                'organization': GuidelineOrganization.SBC,
                'version': '2023',
                'last_updated': '2023-11-20',
                'risk_stratification': {
                    'very_high_risk': {'ldl_target': 50, 'conditions': ['diabetes', 'ckd', 'previous_cvd']},
                    'high_risk': {'ldl_target': 70, 'conditions': ['hypertension', 'smoking', 'family_history']},
                    'intermediate_risk': {'ldl_target': 100, 'conditions': ['age_risk', 'metabolic_syndrome']},
                    'low_risk': {'ldl_target': 130, 'conditions': []}
                },
                'treatment_algorithm': {
                    'first_line': 'statins',
                    'second_line': 'ezetimibe',
                    'third_line': 'pcsk9_inhibitors'
                }
            },
            'heart_failure': {
                'organization': GuidelineOrganization.SBC,
                'version': '2023',
                'last_updated': '2023-09-30',
                'classification': {
                    'hfref': {'ejection_fraction': '<40%', 'treatment': ['ace_arb', 'beta_blockers', 'mra']},
                    'hfmref': {'ejection_fraction': '40-49%', 'treatment': ['ace_arb', 'beta_blockers']},
                    'hfpef': {'ejection_fraction': '>=50%', 'treatment': ['symptom_management']}
                },
                'biomarkers': {
                    'bnp': {'threshold': 100, 'unit': 'pg/mL'},
                    'nt_probnp': {'threshold': 300, 'unit': 'pg/mL'}
                }
            },
            'pharmacogenetics': {
                'organization': GuidelineOrganization.CPIC,
                'version': '2023',
                'last_updated': '2023-08-15',
                'drug_gene_pairs': {
                    'warfarin': {
                        'genes': ['CYP2C9', 'VKORC1'],
                        'recommendations': {
                            'CYP2C9_*2/*2': 'reduce_dose_50%',
                            'CYP2C9_*3/*3': 'reduce_dose_50%',
                            'VKORC1_AA': 'reduce_dose_25%'
                        }
                    },
                    'clopidogrel': {
                        'genes': ['CYP2C19'],
                        'recommendations': {
                            'CYP2C19_*2/*2': 'alternative_therapy',
                            'CYP2C19_*3/*3': 'alternative_therapy'
                        }
                    },
                    'simvastatin': {
                        'genes': ['SLCO1B1'],
                        'recommendations': {
                            'SLCO1B1_*5/*5': 'alternative_statin'
                        }
                    }
                }
            }
        }
    
    def _initialize_version_control(self) -> Dict[str, Any]:
        """Inicializa controle de versão das diretrizes"""
        return {
            'current_versions': {},
            'update_history': [],
            'pending_updates': []
        }
    
    def _initialize_compliance_checker(self) -> Dict[str, Any]:
        """Inicializa verificador de conformidade"""
        return {
            'compliance_rules': {},
            'validation_functions': {},
            'alert_thresholds': {}
        }
    
    def get_current_guideline(self, condition: str, organization: str = None) -> Dict[str, Any]:
        """Obtém diretriz atual para uma condição específica"""
        
        if condition not in self.guidelines_db:
            logger.warning(f"Diretriz não encontrada para condição: {condition}")
            return {}
        
        guideline = self.guidelines_db[condition]
        
        if organization and guideline.get('organization') != organization:
            logger.warning(f"Organização {organization} não corresponde à diretriz de {condition}")
        
        return {
            'condition': condition,
            'guideline': guideline,
            'compliance_status': self._check_guideline_currency(guideline),
            'last_accessed': datetime.now().isoformat()
        }
    
    def _check_guideline_currency(self, guideline: Dict[str, Any]) -> str:
        """Verifica se a diretriz está atualizada"""
        
        last_updated = guideline.get('last_updated', '2020-01-01')
        update_date = datetime.fromisoformat(last_updated)
        current_date = datetime.now()
        
        days_since_update = (current_date - update_date).days
        
        if days_since_update <= 365:
            return 'current'
        elif days_since_update <= 730:
            return 'needs_review'
        else:
            return 'outdated'
    
    def validate_treatment_compliance(self, treatment_plan: Dict[str, Any], condition: str) -> Dict[str, Any]:
        """Valida conformidade do plano de tratamento com diretrizes atuais"""
        
        guideline = self.get_current_guideline(condition)
        
        if not guideline:
            return {
                'compliant': False,
                'reason': 'Diretriz não encontrada',
                'recommendations': []
            }
        
        compliance_result = {
            'compliant': True,
            'compliance_score': 0.0,
            'violations': [],
            'recommendations': [],
            'evidence_level': EvidenceLevel.LEVEL_5,
            'guideline_version': guideline['guideline'].get('version', 'unknown')
        }
        
        if condition == 'diabetes':
            compliance_result = self._validate_diabetes_compliance(treatment_plan, guideline, compliance_result)
        elif condition == 'hypertension':
            compliance_result = self._validate_hypertension_compliance(treatment_plan, guideline, compliance_result)
        elif condition == 'dyslipidemia':
            compliance_result = self._validate_dyslipidemia_compliance(treatment_plan, guideline, compliance_result)
        
        compliance_result['compliant'] = len(compliance_result['violations']) == 0
        compliance_result['compliance_score'] = max(0.0, 1.0 - (len(compliance_result['violations']) * 0.2))
        
        return compliance_result
    
    def _validate_diabetes_compliance(self, treatment_plan: Dict[str, Any], guideline: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Valida conformidade para diabetes"""
        
        targets = guideline['guideline']['treatment_targets']
        patient_age = treatment_plan.get('patient_age', 50)
        
        hba1c_target = targets['hba1c_elderly']['target'] if patient_age >= 65 else targets['hba1c_general']['target']
        current_hba1c = treatment_plan.get('current_hba1c', 0)
        
        if current_hba1c > hba1c_target + 1.0:
            result['violations'].append(f"HbA1c {current_hba1c}% acima da meta {hba1c_target}%")
            result['recommendations'].append("Intensificar tratamento antidiabético")
        
        bp_systolic = treatment_plan.get('blood_pressure_systolic', 0)
        bp_target = targets['blood_pressure']['systolic']
        
        if bp_systolic > bp_target:
            result['violations'].append(f"PA sistólica {bp_systolic} mmHg acima da meta {bp_target} mmHg")
            result['recommendations'].append("Otimizar controle pressórico")
        
        return result
    
    def _validate_hypertension_compliance(self, treatment_plan: Dict[str, Any], guideline: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Valida conformidade para hipertensão"""
        
        targets = guideline['guideline']['treatment_targets']
        comorbidities = treatment_plan.get('comorbidities', [])
        
        if 'diabetes' in comorbidities:
            target = targets['diabetes']
        elif treatment_plan.get('patient_age', 50) >= 65:
            target = targets['elderly']
        else:
            target = targets['general']
        
        bp_systolic = treatment_plan.get('blood_pressure_systolic', 0)
        bp_diastolic = treatment_plan.get('blood_pressure_diastolic', 0)
        
        if bp_systolic > target['systolic']:
            result['violations'].append(f"PA sistólica {bp_systolic} mmHg acima da meta {target['systolic']} mmHg")
        
        if bp_diastolic > target['diastolic']:
            result['violations'].append(f"PA diastólica {bp_diastolic} mmHg acima da meta {target['diastolic']} mmHg")
        
        medications = treatment_plan.get('medications', [])
        first_line_drugs = guideline['guideline']['first_line_drugs']
        
        has_first_line = any(med in str(medications).lower() for med in first_line_drugs)
        if not has_first_line and bp_systolic > 140:
            result['recommendations'].append("Considerar medicação de primeira linha (IECA, BRA, diurético tiazídico ou bloqueador de canal de cálcio)")
        
        return result
    
    def _validate_dyslipidemia_compliance(self, treatment_plan: Dict[str, Any], guideline: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Valida conformidade para dislipidemia"""
        
        risk_strat = guideline['guideline']['risk_stratification']
        comorbidities = treatment_plan.get('comorbidities', [])
        
        risk_category = 'low_risk'
        for category, criteria in risk_strat.items():
            if any(condition in comorbidities for condition in criteria['conditions']):
                risk_category = category
                break
        
        ldl_target = risk_strat[risk_category]['ldl_target']
        current_ldl = treatment_plan.get('ldl_cholesterol', 0)
        
        if current_ldl > ldl_target:
            result['violations'].append(f"LDL {current_ldl} mg/dL acima da meta {ldl_target} mg/dL para risco {risk_category}")
            result['recommendations'].append(f"Intensificar tratamento hipolipemiante para atingir meta de LDL < {ldl_target} mg/dL")
        
        return result
    
    def get_drug_guideline_recommendations(self, drug_name: str, patient_genetics: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtém recomendações farmacogenéticas para um medicamento"""
        
        pharmacogenetics = self.guidelines_db.get('pharmacogenetics', {})
        drug_gene_pairs = pharmacogenetics.get('drug_gene_pairs', {})
        
        drug_lower = drug_name.lower()
        recommendations = {
            'drug': drug_name,
            'genetic_recommendations': [],
            'evidence_level': EvidenceLevel.LEVEL_1A,
            'organization': GuidelineOrganization.CPIC
        }
        
        for drug, gene_info in drug_gene_pairs.items():
            if drug in drug_lower:
                if patient_genetics:
                    for gene in gene_info['genes']:
                        genotype = patient_genetics.get(gene)
                        if genotype and genotype in gene_info['recommendations']:
                            recommendation = gene_info['recommendations'][genotype]
                            recommendations['genetic_recommendations'].append({
                                'gene': gene,
                                'genotype': genotype,
                                'recommendation': recommendation,
                                'evidence': EvidenceLevel.LEVEL_1A
                            })
                break
        
        return recommendations
    
    def update_guideline(self, condition: str, new_guideline: Dict[str, Any]) -> bool:
        """Atualiza diretriz com nova versão"""
        
        try:
            if condition in self.guidelines_db:
                old_version = self.guidelines_db[condition].get('version', 'unknown')
                self.guidelines_db[condition] = new_guideline
                
                self.version_control['update_history'].append({
                    'condition': condition,
                    'old_version': old_version,
                    'new_version': new_guideline.get('version', 'unknown'),
                    'update_timestamp': datetime.now().isoformat(),
                    'updated_by': 'system'
                })
                
                logger.info(f"Diretriz atualizada para {condition}: {old_version} -> {new_guideline.get('version')}")
                return True
            else:
                logger.error(f"Condição {condition} não encontrada para atualização")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar diretriz para {condition}: {e}")
            return False
    
    def get_compliance_report(self, treatment_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera relatório de conformidade para múltiplos planos de tratamento"""
        
        total_plans = len(treatment_plans)
        compliant_plans = 0
        compliance_scores = []
        violations_summary = {}
        
        for plan in treatment_plans:
            condition = plan.get('condition')
            if condition:
                compliance = self.validate_treatment_compliance(plan, condition)
                compliance_scores.append(compliance.get('compliance_score', 0))
                
                if compliance.get('compliant', False):
                    compliant_plans += 1
                
                for violation in compliance.get('violations', []):
                    violations_summary[violation] = violations_summary.get(violation, 0) + 1
        
        return {
            'total_plans_analyzed': total_plans,
            'compliant_plans': compliant_plans,
            'compliance_rate': compliant_plans / total_plans if total_plans > 0 else 0,
            'average_compliance_score': sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0,
            'common_violations': sorted(violations_summary.items(), key=lambda x: x[1], reverse=True)[:5],
            'report_timestamp': datetime.now().isoformat()
        }
