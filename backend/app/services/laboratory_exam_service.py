"""
Serviço inteligente de solicitação de exames laboratoriais
Baseado nas últimas diretrizes médicas e protocolos institucionais
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger('MedAI.Laboratory.ExamService')


class ExamPriority(str, Enum):
    """Prioridades de exames laboratoriais"""
    URGENT = "urgente"
    HIGH = "alta"
    ROUTINE = "rotina"
    SCREENING = "rastreamento"


class ExamCategory(str, Enum):
    """Categorias de exames laboratoriais"""
    BIOCHEMISTRY = "bioquimica"
    HEMATOLOGY = "hematologia"
    IMMUNOLOGY = "imunologia"
    MICROBIOLOGY = "microbiologia"
    MOLECULAR = "biologia_molecular"
    HORMONES = "hormonios"


class LaboratoryExamService:
    """Serviço para solicitação inteligente de exames laboratoriais"""
    
    def __init__(self):
        self.exam_protocols = self._initialize_exam_protocols()
        self.clinical_guidelines = self._load_clinical_guidelines()
        self.institutional_protocols = self._load_institutional_protocols()
    
    def _initialize_exam_protocols(self) -> Dict[str, Any]:
        """Inicializa protocolos de exames baseados em diretrizes atuais"""
        return {
            'diabetes_screening': {
                'exames': ['glicemia_jejum', 'hba1c', 'glicemia_pos_prandial'],
                'frequencia': 'anual',
                'indicacoes': ['idade > 45', 'imc > 25', 'historia_familiar'],
                'diretriz': 'SBD 2023',
                'prioridade': ExamPriority.SCREENING
            },
            'dislipidemia_screening': {
                'exames': ['colesterol_total', 'hdl', 'ldl', 'triglicerideos'],
                'frequencia': '5_anos',
                'indicacoes': ['idade > 40', 'fatores_risco_cardiovascular'],
                'diretriz': 'SBC 2023',
                'prioridade': ExamPriority.SCREENING
            },
            'funcao_renal': {
                'exames': ['creatinina', 'ureia', 'clearance_creatinina', 'eas', 'microalbuminuria'],
                'frequencia': 'conforme_clinica',
                'indicacoes': ['hipertensao', 'diabetes', 'uso_nefrotoxicos'],
                'diretriz': 'SBN 2023',
                'prioridade': ExamPriority.ROUTINE
            },
            'funcao_hepatica': {
                'exames': ['alt', 'ast', 'bilirrubinas', 'fosfatase_alcalina', 'ggt', 'albumina'],
                'frequencia': 'conforme_clinica',
                'indicacoes': ['hepatopatia', 'uso_hepatotoxicos', 'alcoolismo'],
                'diretriz': 'SBH 2023',
                'prioridade': ExamPriority.ROUTINE
            },
            'perfil_tireoidiano': {
                'exames': ['tsh', 't4_livre', 't3_livre'],
                'frequencia': 'anual_se_alterado',
                'indicacoes': ['sintomas_tireoidianos', 'historia_familiar', 'mulheres > 60'],
                'diretriz': 'SBEM 2023',
                'prioridade': ExamPriority.ROUTINE
            },
            'hemograma_completo': {
                'exames': ['hemograma', 'plaquetas', 'leucograma'],
                'frequencia': 'conforme_clinica',
                'indicacoes': ['anemia', 'infeccao', 'sangramento', 'quimioterapia'],
                'diretriz': 'SBHH 2023',
                'prioridade': ExamPriority.HIGH
            },
            'marcadores_cardiacos': {
                'exames': ['troponina_i', 'ck_mb', 'bnp', 'nt_probnp'],
                'frequencia': 'urgente',
                'indicacoes': ['dor_toracica', 'dispneia', 'suspeita_iam'],
                'diretriz': 'SBC 2023',
                'prioridade': ExamPriority.URGENT
            },
            'coagulacao': {
                'exames': ['tp', 'ttpa', 'inr', 'fibrinogenio'],
                'frequencia': 'conforme_clinica',
                'indicacoes': ['anticoagulacao', 'sangramento', 'cirurgia'],
                'diretriz': 'SBHH 2023',
                'prioridade': ExamPriority.HIGH
            }
        }
    
    def _load_clinical_guidelines(self) -> Dict[str, Any]:
        """Carrega diretrizes clínicas atualizadas"""
        return {
            'diabetes': {
                'organizacao': 'SBD',
                'versao': '2023',
                'criterios_diagnosticos': {
                    'glicemia_jejum': '≥ 126 mg/dL',
                    'hba1c': '≥ 6.5%',
                    'glicemia_casual': '≥ 200 mg/dL com sintomas'
                }
            },
            'hipertensao': {
                'organizacao': 'SBC',
                'versao': '2023',
                'criterios_diagnosticos': {
                    'pa_sistolica': '≥ 140 mmHg',
                    'pa_diastolica': '≥ 90 mmHg'
                }
            },
            'dislipidemia': {
                'organizacao': 'SBC',
                'versao': '2023',
                'metas_terapeuticas': {
                    'ldl_muito_alto_risco': '< 50 mg/dL',
                    'ldl_alto_risco': '< 70 mg/dL',
                    'ldl_risco_intermediario': '< 100 mg/dL'
                }
            }
        }
    
    def _load_institutional_protocols(self) -> Dict[str, Any]:
        """Carrega protocolos institucionais específicos"""
        return {
            'urgencia_emergencia': {
                'tempo_liberacao_urgente': '1_hora',
                'tempo_liberacao_rotina': '24_horas',
                'exames_ponto_cuidado': ['glicemia', 'gasometria', 'troponina_rapida']
            },
            'internacao': {
                'exames_admissao': ['hemograma', 'bioquimica_basica', 'coagulograma'],
                'frequencia_controle': 'diaria_se_instavel'
            },
            'ambulatorio': {
                'jejum_necessario': ['glicemia_jejum', 'perfil_lipidico', 'insulina'],
                'preparo_especial': ['cortisol', 'hormonio_crescimento']
            }
        }
    
    async def solicitar_exames_inteligente(self, paciente: dict, contexto_clinico: dict) -> dict:
        """Solicitação inteligente de exames baseada em IA e diretrizes"""
        
        try:
            exames_recomendados = []
            justificativas = []
            
            idade = paciente.get('idade', 0)
            sexo = paciente.get('sexo', '')
            comorbidades = paciente.get('comorbidades', [])
            medicamentos = paciente.get('medicamentos', [])
            sintomas = contexto_clinico.get('sintomas', [])
            hipotese_diagnostica = contexto_clinico.get('hipotese_diagnostica', '')
            
            exames_recomendados.extend(
                await self._avaliar_exames_rastreamento(idade, sexo, comorbidades)
            )
            
            exames_recomendados.extend(
                await self._avaliar_exames_sintomas(sintomas)
            )
            
            exames_recomendados.extend(
                await self._avaliar_exames_hipotese_diagnostica(hipotese_diagnostica)
            )
            
            exames_recomendados.extend(
                await self._avaliar_exames_medicamentos(medicamentos)
            )
            
            exames_recomendados.extend(
                await self._avaliar_exames_comorbidades(comorbidades)
            )
            
            exames_otimizados = await self._otimizar_solicitacao_exames(exames_recomendados)
            
            return {
                'exames_recomendados': exames_otimizados,
                'justificativas': justificativas,
                'prioridade_geral': self._calcular_prioridade_geral(exames_otimizados),
                'custo_estimado': self._calcular_custo_estimado(exames_otimizados),
                'tempo_resultado': self._estimar_tempo_resultado(exames_otimizados),
                'orientacoes_preparo': self._gerar_orientacoes_preparo(exames_otimizados),
                'diretrizes_aplicadas': self._listar_diretrizes_aplicadas(exames_otimizados)
            }
            
        except Exception as e:
            logger.error(f"Erro na solicitação inteligente de exames: {e}")
            return {
                'error': str(e),
                'exames_recomendados': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _avaliar_exames_rastreamento(self, idade: int, sexo: str, comorbidades: list) -> list:
        """Avalia exames de rastreamento baseados em idade, sexo e fatores de risco"""
        
        exames = []
        
        if idade >= 45 or 'diabetes' in comorbidades or 'obesidade' in comorbidades:
            exames.extend(self.exam_protocols['diabetes_screening']['exames'])
        
        if idade >= 40 or any(comorb in comorbidades for comorb in ['hipertensao', 'tabagismo', 'historia_familiar_cardiovascular']):
            exames.extend(self.exam_protocols['dislipidemia_screening']['exames'])
        
        if sexo == 'feminino' and idade >= 60:
            exames.extend(self.exam_protocols['perfil_tireoidiano']['exames'])
        
        if any(comorb in comorbidades for comorb in ['hipertensao', 'diabetes']):
            exames.extend(self.exam_protocols['funcao_renal']['exames'])
        
        return list(set(exames))
    
    async def _avaliar_exames_sintomas(self, sintomas: list) -> list:
        """Avalia exames baseados nos sintomas apresentados"""
        
        exames = []
        
        if any(sintoma in sintomas for sintoma in ['dor_toracica', 'dispneia', 'palpitacoes']):
            exames.extend(self.exam_protocols['marcadores_cardiacos']['exames'])
        
        if any(sintoma in sintomas for sintoma in ['fadiga', 'palidez', 'fraqueza']):
            exames.extend(self.exam_protocols['hemograma_completo']['exames'])
            exames.extend(['ferritina', 'vitamina_b12', 'acido_folico'])
        
        if any(sintoma in sintomas for sintoma in ['poliuria', 'polidipsia', 'perda_peso']):
            exames.extend(self.exam_protocols['diabetes_screening']['exames'])
        
        if any(sintoma in sintomas for sintoma in ['ictericia', 'dor_abdominal_direita']):
            exames.extend(self.exam_protocols['funcao_hepatica']['exames'])
        
        return list(set(exames))
    
    async def _avaliar_exames_hipotese_diagnostica(self, hipotese: str) -> list:
        """Avalia exames baseados na hipótese diagnóstica"""
        
        exames = []
        hipotese_lower = hipotese.lower()
        
        if 'infarto' in hipotese_lower or 'iam' in hipotese_lower:
            exames.extend(['troponina_i', 'ck_mb', 'mioglobina'])
        
        if 'insuficiencia_cardiaca' in hipotese_lower:
            exames.extend(['bnp', 'nt_probnp'])
        
        if 'sepse' in hipotese_lower or 'infeccao' in hipotese_lower:
            exames.extend(['hemograma', 'pcr', 'procalcitonina', 'lactato'])
        
        if 'tromboembolia' in hipotese_lower or 'tvp' in hipotese_lower:
            exames.extend(['d_dimero', 'tp', 'ttpa'])
        
        if 'anemia' in hipotese_lower:
            exames.extend(['hemograma', 'ferritina', 'vitamina_b12', 'acido_folico', 'reticulocitos'])
        
        return list(set(exames))
    
    async def _avaliar_exames_medicamentos(self, medicamentos: list) -> list:
        """Avalia exames de monitoramento baseados nos medicamentos em uso"""
        
        exames = []
        
        for medicamento in medicamentos:
            nome = medicamento.get('nome', '').lower()
            
            if any(med in nome for med in ['warfarina', 'varfarina']):
                exames.extend(['tp', 'inr'])
            
            if any(med in nome for med in ['digoxina']):
                exames.extend(['digoxinemia', 'potassio', 'magnesio'])
            
            if any(med in nome for med in ['lítio', 'litio']):
                exames.extend(['lítio_sérico', 'creatinina', 'tsh'])
            
            if any(med in nome for med in ['metotrexato']):
                exames.extend(['hemograma', 'alt', 'ast', 'creatinina'])
            
            if any(med in nome for med in ['estatinas', 'atorvastatina', 'sinvastatina']):
                exames.extend(['alt', 'ast', 'ck'])
            
            if any(med in nome for med in ['ace_inibidores', 'enalapril', 'captopril']):
                exames.extend(['creatinina', 'potassio'])
        
        return list(set(exames))
    
    async def _avaliar_exames_comorbidades(self, comorbidades: list) -> list:
        """Avalia exames baseados nas comorbidades do paciente"""
        
        exames = []
        
        if 'diabetes' in comorbidades:
            exames.extend(['hba1c', 'microalbuminuria', 'creatinina'])
        
        if 'hipertensao' in comorbidades:
            exames.extend(['creatinina', 'potassio', 'microalbuminuria'])
        
        if 'insuficiencia_renal' in comorbidades:
            exames.extend(['creatinina', 'ureia', 'clearance_creatinina', 'eas'])
        
        if 'hepatopatia' in comorbidades:
            exames.extend(['alt', 'ast', 'bilirrubinas', 'albumina', 'tp'])
        
        if 'hipotireoidismo' in comorbidades or 'hipertireoidismo' in comorbidades:
            exames.extend(['tsh', 't4_livre'])
        
        return list(set(exames))
    
    async def _otimizar_solicitacao_exames(self, exames_brutos: list) -> list:
        """Otimiza a solicitação removendo redundâncias e agrupando exames"""
        
        exames_otimizados = []
        exames_processados = set()
        
        grupos_exames = {
            'bioquimica_basica': ['glicemia', 'ureia', 'creatinina', 'sodio', 'potassio'],
            'perfil_lipidico': ['colesterol_total', 'hdl', 'ldl', 'triglicerideos'],
            'funcao_hepatica': ['alt', 'ast', 'bilirrubinas', 'fosfatase_alcalina'],
            'coagulograma': ['tp', 'ttpa', 'inr'],
            'marcadores_cardiacos': ['troponina_i', 'ck_mb', 'bnp']
        }
        
        for grupo, exames_grupo in grupos_exames.items():
            exames_no_grupo = [e for e in exames_brutos if e in exames_grupo]
            if len(exames_no_grupo) >= 2:
                exames_otimizados.append({
                    'nome': grupo,
                    'tipo': 'grupo',
                    'exames_inclusos': exames_no_grupo,
                    'prioridade': ExamPriority.ROUTINE
                })
                exames_processados.update(exames_no_grupo)
        
        for exame in exames_brutos:
            if exame not in exames_processados:
                exames_otimizados.append({
                    'nome': exame,
                    'tipo': 'individual',
                    'prioridade': self._determinar_prioridade_exame(exame)
                })
        
        return exames_otimizados
    
    def _determinar_prioridade_exame(self, exame: str) -> ExamPriority:
        """Determina a prioridade de um exame específico"""
        
        exames_urgentes = ['troponina_i', 'gasometria', 'lactato', 'glicemia_urgente']
        exames_alta_prioridade = ['hemograma', 'creatinina', 'potassio', 'inr']
        
        if exame in exames_urgentes:
            return ExamPriority.URGENT
        elif exame in exames_alta_prioridade:
            return ExamPriority.HIGH
        else:
            return ExamPriority.ROUTINE
    
    def _calcular_prioridade_geral(self, exames: list) -> ExamPriority:
        """Calcula a prioridade geral da solicitação"""
        
        prioridades = [exame.get('prioridade', ExamPriority.ROUTINE) for exame in exames]
        
        if ExamPriority.URGENT in prioridades:
            return ExamPriority.URGENT
        elif ExamPriority.HIGH in prioridades:
            return ExamPriority.HIGH
        else:
            return ExamPriority.ROUTINE
    
    def _calcular_custo_estimado(self, exames: list) -> float:
        """Calcula o custo estimado dos exames"""
        
        custos_base = {
            'hemograma': 15.0,
            'bioquimica_basica': 25.0,
            'perfil_lipidico': 30.0,
            'funcao_hepatica': 35.0,
            'troponina_i': 45.0,
            'bnp': 80.0,
            'hba1c': 40.0
        }
        
        custo_total = 0.0
        for exame in exames:
            nome = exame.get('nome', '')
            custo_total += custos_base.get(nome, 20.0)
        
        return custo_total
    
    def _estimar_tempo_resultado(self, exames: list) -> dict:
        """Estima o tempo para liberação dos resultados"""
        
        tempos_base = {
            'hemograma': 2,
            'bioquimica_basica': 4,
            'troponina_i': 1,
            'gasometria': 0.5,
            'culturas': 72
        }
        
        tempo_minimo = min([tempos_base.get(exame.get('nome', ''), 4) for exame in exames])
        tempo_maximo = max([tempos_base.get(exame.get('nome', ''), 4) for exame in exames])
        
        return {
            'tempo_minimo_horas': tempo_minimo,
            'tempo_maximo_horas': tempo_maximo,
            'tempo_medio_horas': (tempo_minimo + tempo_maximo) / 2
        }
    
    def _gerar_orientacoes_preparo(self, exames: list) -> list:
        """Gera orientações de preparo para os exames"""
        
        orientacoes = []
        nomes_exames = [exame.get('nome', '') for exame in exames]
        
        if any(exame in nomes_exames for exame in ['glicemia_jejum', 'perfil_lipidico']):
            orientacoes.append('Jejum de 12 horas necessário')
        
        if 'cortisol' in nomes_exames:
            orientacoes.append('Coleta preferencialmente entre 7h e 9h da manhã')
        
        if any('cultura' in exame for exame in nomes_exames):
            orientacoes.append('Evitar uso de antibióticos nas últimas 48h')
        
        if not orientacoes:
            orientacoes.append('Não há preparo especial necessário')
        
        return orientacoes
    
    def _listar_diretrizes_aplicadas(self, exames: list) -> list:
        """Lista as diretrizes médicas aplicadas na solicitação"""
        
        diretrizes = set()
        
        for exame in exames:
            nome = exame.get('nome', '')
            if any(diabetes_exam in nome for diabetes_exam in ['glicemia', 'hba1c']):
                diretrizes.add('SBD 2023')
            if any(cardio_exam in nome for cardio_exam in ['troponina', 'bnp', 'perfil_lipidico']):
                diretrizes.add('SBC 2023')
            if 'hemograma' in nome:
                diretrizes.add('SBHH 2023')
        
        return list(diretrizes)
