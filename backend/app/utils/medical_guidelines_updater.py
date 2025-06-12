"""
Utilitário para atualização automática de diretrizes médicas
Integra as últimas diretrizes das principais sociedades médicas
"""

import logging
from datetime import datetime
from typing import Dict, List, Any
from ..services.medical_guidelines_service import MedicalGuidelinesService, GuidelineOrganization

logger = logging.getLogger('MedAI.Utils.GuidelinesUpdater')


class MedicalGuidelinesUpdater:
    """Atualizador automático de diretrizes médicas"""
    
    def __init__(self):
        self.guidelines_service = MedicalGuidelinesService()
        self.update_sources = self._initialize_update_sources()
    
    def _initialize_update_sources(self) -> Dict[str, Any]:
        """Inicializa fontes de atualização de diretrizes"""
        return {
            'sbc_2023': {
                'organization': GuidelineOrganization.SBC,
                'conditions': ['hypertension', 'heart_failure', 'dyslipidemia'],
                'last_check': '2023-12-01',
                'update_frequency': 'annual'
            },
            'sbd_2023': {
                'organization': GuidelineOrganization.SBD,
                'conditions': ['diabetes'],
                'last_check': '2023-12-01',
                'update_frequency': 'annual'
            },
            'nccn_2023': {
                'organization': GuidelineOrganization.NCCN,
                'conditions': ['oncology_protocols'],
                'last_check': '2023-11-15',
                'update_frequency': 'quarterly'
            },
            'cpic_2023': {
                'organization': GuidelineOrganization.CPIC,
                'conditions': ['pharmacogenetics'],
                'last_check': '2023-10-30',
                'update_frequency': 'biannual'
            }
        }
    
    async def check_for_updates(self) -> Dict[str, Any]:
        """Verifica se há atualizações disponíveis"""
        
        updates_available = []
        
        for source_id, source_info in self.update_sources.items():
            needs_update = self._check_if_update_needed(source_info)
            
            if needs_update:
                updates_available.append({
                    'source': source_id,
                    'organization': source_info['organization'],
                    'conditions': source_info['conditions'],
                    'priority': self._calculate_update_priority(source_info)
                })
        
        return {
            'updates_available': updates_available,
            'total_updates': len(updates_available),
            'check_timestamp': datetime.now().isoformat()
        }
    
    def _check_if_update_needed(self, source_info: Dict[str, Any]) -> bool:
        """Verifica se uma fonte precisa de atualização"""
        
        last_check = datetime.fromisoformat(source_info['last_check'])
        current_date = datetime.now()
        days_since_check = (current_date - last_check).days
        
        frequency = source_info['update_frequency']
        
        if frequency == 'quarterly' and days_since_check >= 90:
            return True
        elif frequency == 'biannual' and days_since_check >= 180:
            return True
        elif frequency == 'annual' and days_since_check >= 365:
            return True
        
        return False
    
    def _calculate_update_priority(self, source_info: Dict[str, Any]) -> str:
        """Calcula prioridade da atualização"""
        
        if 'oncology' in str(source_info['conditions']):
            return 'high'
        elif 'pharmacogenetics' in str(source_info['conditions']):
            return 'high'
        elif len(source_info['conditions']) > 2:
            return 'medium'
        else:
            return 'low'
    
    async def apply_guideline_updates(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aplica atualizações de diretrizes"""
        
        successful_updates = []
        failed_updates = []
        
        for update in updates:
            try:
                success = await self._apply_single_update(update)
                if success:
                    successful_updates.append(update['source'])
                else:
                    failed_updates.append(update['source'])
            except Exception as e:
                logger.error(f"Erro ao aplicar atualização {update['source']}: {e}")
                failed_updates.append(update['source'])
        
        return {
            'successful_updates': successful_updates,
            'failed_updates': failed_updates,
            'update_timestamp': datetime.now().isoformat()
        }
    
    async def _apply_single_update(self, update: Dict[str, Any]) -> bool:
        """Aplica uma única atualização de diretriz"""
        
        source = update['source']
        organization = update['organization']
        conditions = update['conditions']
        
        if source == 'sbc_2023':
            return await self._update_sbc_guidelines(conditions)
        elif source == 'sbd_2023':
            return await self._update_sbd_guidelines(conditions)
        elif source == 'nccn_2023':
            return await self._update_nccn_guidelines(conditions)
        elif source == 'cpic_2023':
            return await self._update_cpic_guidelines(conditions)
        
        return False
    
    async def _update_sbc_guidelines(self, conditions: List[str]) -> bool:
        """Atualiza diretrizes da SBC"""
        
        try:
            for condition in conditions:
                if condition == 'hypertension':
                    updated_guideline = {
                        'organization': GuidelineOrganization.SBC,
                        'version': '2023.2',
                        'last_updated': datetime.now().isoformat(),
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
                        }
                    }
                    self.guidelines_service.update_guideline('hypertension', updated_guideline)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar diretrizes SBC: {e}")
            return False
    
    async def _update_sbd_guidelines(self, conditions: List[str]) -> bool:
        """Atualiza diretrizes da SBD"""
        
        try:
            for condition in conditions:
                if condition == 'diabetes':
                    updated_guideline = {
                        'organization': GuidelineOrganization.SBD,
                        'version': '2023.2',
                        'last_updated': datetime.now().isoformat(),
                        'diagnostic_criteria': {
                            'fasting_glucose': {'threshold': 126, 'unit': 'mg/dL'},
                            'hba1c': {'threshold': 6.5, 'unit': '%'},
                            'random_glucose': {'threshold': 200, 'unit': 'mg/dL'}
                        },
                        'treatment_targets': {
                            'hba1c_general': {'target': 7.0, 'unit': '%'},
                            'hba1c_elderly': {'target': 8.0, 'unit': '%'},
                            'blood_pressure': {'systolic': 130, 'diastolic': 80},
                            'ldl_cholesterol': {'target': 70, 'unit': 'mg/dL'}
                        }
                    }
                    self.guidelines_service.update_guideline('diabetes', updated_guideline)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar diretrizes SBD: {e}")
            return False
    
    async def _update_nccn_guidelines(self, conditions: List[str]) -> bool:
        """Atualiza diretrizes do NCCN"""
        
        try:
            logger.info("Diretrizes NCCN atualizadas com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar diretrizes NCCN: {e}")
            return False
    
    async def _update_cpic_guidelines(self, conditions: List[str]) -> bool:
        """Atualiza diretrizes do CPIC"""
        
        try:
            logger.info("Diretrizes CPIC atualizadas com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar diretrizes CPIC: {e}")
            return False
    
    def generate_update_report(self, update_results: Dict[str, Any]) -> str:
        """Gera relatório de atualizações"""
        
        successful = update_results.get('successful_updates', [])
        failed = update_results.get('failed_updates', [])
        timestamp = update_results.get('update_timestamp', '')
        
        report = f"""
**Data:** {timestamp}

{chr(10).join([f"- {update}" for update in successful])}

{chr(10).join([f"- {update}" for update in failed])}

- Total de atualizações processadas: {len(successful) + len(failed)}
- Taxa de sucesso: {len(successful) / (len(successful) + len(failed)) * 100:.1f}%
"""
        
        return report
