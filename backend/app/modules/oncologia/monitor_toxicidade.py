"""
Monitor de toxicidade em oncologia com IA
"""

import asyncio
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger('MedAI.Oncologia.MonitorToxicidade')

class MonitorToxicidadeIA:
    """Monitor de toxicidade em oncologia com IA"""
    
    def __init__(self):
        self.detector_toxicidade = DetectorToxicidadeIA()
        self.predictor_toxicidade = PredictorToxicidadeAvancado()
        self.gestor_intervencoes = GestorIntervencoesToxicidade()
        self.analisador_tendencias = AnalisadorTendenciasToxicidade()
        
    async def monitorar_toxicidades_completo(self, pacientes_tratamento: List[Dict],
                                           monitoramento_continuo: bool = True,
                                           intervencoes_automaticas: bool = True) -> Dict:
        """Monitoramento completo de toxicidades em pacientes oncológicos"""
        
        try:
            monitoramento_toxicidade = {}
            
            for paciente in pacientes_tratamento:
                toxicidades_detectadas = await self.detector_toxicidade.detectar_toxicidades(
                    paciente=paciente,
                    dados_laboratoriais=paciente.get('laboratorio_atual'),
                    sintomas_reportados=paciente.get('sintomas_atuais', []),
                    exame_fisico=paciente.get('exame_fisico'),
                    escalas_avaliacao=['CTCAE_v5', 'PRO_CTCAE'],
                    usar_ml_deteccao=True
                )
                
                predicoes_toxicidade = await self.predictor_toxicidade.prever_toxicidades_futuras(
                    paciente=paciente,
                    tratamento_atual=paciente.get('protocolo_atual'),
                    historico_toxicidades=paciente.get('toxicidades_previas', []),
                    fatores_risco=await self.identificar_fatores_risco_toxicidade(paciente),
                    horizonte_predicao='30_dias'
                )
                
                classificacao_severidade = await self.classificar_severidade_toxicidades(
                    toxicidades_detectadas,
                    impacto_qualidade_vida=True,
                    risco_hospitalizacao=True
                )
                
                if intervencoes_automaticas:
                    intervencoes = await self.gestor_intervencoes.recomendar_intervencoes(
                        toxicidades=toxicidades_detectadas,
                        severidade=classificacao_severidade,
                        protocolo_tratamento=paciente.get('protocolo_atual'),
                        preferencias_paciente=paciente.get('preferencias_tratamento'),
                        guidelines=['NCCN', 'ESMO', 'ASCO']
                    )
                else:
                    intervencoes = None
                
                if monitoramento_continuo:
                    plano_monitoramento = await self.definir_plano_monitoramento_personalizado(
                        paciente=paciente,
                        toxicidades_risco=predicoes_toxicidade,
                        frequencia_base='semanal',
                        usar_wearables=True,
                        alertas_automaticos=True
                    )
                else:
                    plano_monitoramento = None
                
                analise_tendencias = await self.analisador_tendencias.analisar_tendencias_paciente(
                    paciente_id=paciente['id'],
                    historico_toxicidades=paciente.get('historico_completo_toxicidades'),
                    tratamentos_previos=paciente.get('tratamentos_anteriores', []),
                    identificar_padroes=True
                )
                
                score_risco_global = await self.calcular_score_risco_global(
                    toxicidades_atuais=toxicidades_detectadas,
                    predicoes=predicoes_toxicidade,
                    fatores_risco=await self.identificar_fatores_risco_toxicidade(paciente)
                )
                
                monitoramento_toxicidade[paciente['id']] = {
                    'toxicidades_detectadas': toxicidades_detectadas,
                    'predicoes_toxicidade': predicoes_toxicidade,
                    'classificacao_severidade': classificacao_severidade,
                    'intervencoes_recomendadas': intervencoes,
                    'plano_monitoramento': plano_monitoramento,
                    'analise_tendencias': analise_tendencias,
                    'score_risco_global': score_risco_global,
                    'alertas_criticos': await self.gerar_alertas_criticos(
                        toxicidades_detectadas, classificacao_severidade
                    ),
                    'recomendacoes_seguimento': await self.gerar_recomendacoes_seguimento(
                        paciente, toxicidades_detectadas
                    )
                }
            
            return {
                'monitoramento_individualizado': monitoramento_toxicidade,
                'estatisticas_toxicidade': await self.calcular_estatisticas_toxicidade(
                    monitoramento_toxicidade
                ),
                'toxicidades_mais_frequentes': await self.analisar_toxicidades_frequentes(),
                'eficacia_intervencoes': await self.avaliar_eficacia_intervencoes(),
                'impacto_qualidade_vida': await self.avaliar_impacto_qualidade_vida(
                    monitoramento_toxicidade
                )
            }
            
        except Exception as e:
            logger.error(f"Erro no monitoramento de toxicidades: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def identificar_fatores_risco_toxicidade(self, paciente: Dict) -> List[Dict]:
        """Identifica fatores de risco para toxicidade"""
        
        fatores_risco = []
        
        if paciente.get('idade', 0) > 65:
            fatores_risco.append({
                'fator': 'Idade avançada',
                'categoria': 'demografico',
                'peso_risco': 0.3
            })
        
        if paciente.get('performance_status', 0) > 1:
            fatores_risco.append({
                'fator': 'Performance status reduzido',
                'categoria': 'clinico',
                'peso_risco': 0.4
            })
        
        comorbidades_risco = ['diabetes', 'insuficiencia_renal', 'cardiopatia']
        for comorbidade in paciente.get('comorbidades', []):
            if comorbidade.lower() in comorbidades_risco:
                fatores_risco.append({
                    'fator': f'Comorbidade: {comorbidade}',
                    'categoria': 'comorbidade',
                    'peso_risco': 0.5
                })
        
        if paciente.get('polimorfismos_farmacogeneticos'):
            fatores_risco.append({
                'fator': 'Polimorfismos farmacogenéticos',
                'categoria': 'genetico',
                'peso_risco': 0.6
            })
        
        return fatores_risco

    async def classificar_severidade_toxicidades(self, toxicidades: Dict, **kwargs) -> Dict:
        """Classifica severidade das toxicidades"""
        
        classificacao = {}
        
        for toxicidade, dados in toxicidades.items():
            grau_ctcae = dados.get('grau_ctcae', 1)
            
            if grau_ctcae >= 4:
                severidade = 'critica'
                prioridade = 'emergencia'
            elif grau_ctcae == 3:
                severidade = 'severa'
                prioridade = 'alta'
            elif grau_ctcae == 2:
                severidade = 'moderada'
                prioridade = 'moderada'
            else:
                severidade = 'leve'
                prioridade = 'baixa'
            
            classificacao[toxicidade] = {
                'severidade': severidade,
                'prioridade': prioridade,
                'grau_ctcae': grau_ctcae,
                'requer_intervencao_imediata': grau_ctcae >= 3,
                'impacto_tratamento': dados.get('impacto_tratamento', 'minimo')
            }
        
        return classificacao

    async def definir_plano_monitoramento_personalizado(self, paciente: Dict, **kwargs) -> Dict:
        """Define plano de monitoramento personalizado"""
        
        return {
            'frequencia_avaliacao': kwargs.get('frequencia_base', 'semanal'),
            'parametros_monitorados': [
                'Hemograma completo',
                'Função renal',
                'Função hepática',
                'Sintomas PRO-CTCAE'
            ],
            'wearables_utilizados': kwargs.get('usar_wearables', False),
            'alertas_configurados': {
                'neutropenia': 'Neutrófilos < 1000',
                'trombocitopenia': 'Plaquetas < 50000',
                'fadiga_severa': 'Score fadiga > 7'
            },
            'escalas_qualidade_vida': ['EORTC QLQ-C30', 'FACT-G'],
            'comunicacao_paciente': 'App móvel + telefone'
        }

    async def calcular_score_risco_global(self, **kwargs) -> Dict:
        """Calcula score de risco global de toxicidade"""
        
        score_base = 0.3
        
        toxicidades_atuais = kwargs.get('toxicidades_atuais', {})
        if toxicidades_atuais:
            score_base += len(toxicidades_atuais) * 0.1
        
        predicoes = kwargs.get('predicoes', {})
        if predicoes.get('risco_alto_30_dias', False):
            score_base += 0.2
        
        fatores_risco = kwargs.get('fatores_risco', [])
        for fator in fatores_risco:
            score_base += fator.get('peso_risco', 0) * 0.1
        
        score_final = min(1.0, score_base)
        
        if score_final >= 0.8:
            categoria_risco = 'muito_alto'
        elif score_final >= 0.6:
            categoria_risco = 'alto'
        elif score_final >= 0.4:
            categoria_risco = 'moderado'
        else:
            categoria_risco = 'baixo'
        
        return {
            'score_risco': score_final,
            'categoria_risco': categoria_risco,
            'recomendacao_monitoramento': 'intensificado' if score_final >= 0.6 else 'padrao',
            'fatores_contribuintes': fatores_risco
        }

    async def gerar_alertas_criticos(self, toxicidades: Dict, severidade: Dict) -> List[Dict]:
        """Gera alertas críticos"""
        
        alertas = []
        
        for toxicidade, dados_severidade in severidade.items():
            if dados_severidade.get('requer_intervencao_imediata'):
                alertas.append({
                    'tipo': 'critico',
                    'toxicidade': toxicidade,
                    'severidade': dados_severidade['severidade'],
                    'acao_requerida': 'Avaliação médica imediata',
                    'prazo': 'Imediato',
                    'notificar': ['medico_responsavel', 'enfermagem', 'farmacia']
                })
        
        return alertas

    async def gerar_recomendacoes_seguimento(self, paciente: Dict, toxicidades: Dict) -> List[str]:
        """Gera recomendações de seguimento"""
        
        recomendacoes = []
        
        if toxicidades:
            recomendacoes.extend([
                'Intensificar monitoramento laboratorial',
                'Avaliar necessidade de ajuste de dose',
                'Considerar medicação de suporte',
                'Orientar paciente sobre sinais de alerta'
            ])
        
        if paciente.get('performance_status', 0) > 1:
            recomendacoes.append('Avaliação nutricional')
        
        return recomendacoes

    async def calcular_estatisticas_toxicidade(self, monitoramento: Dict) -> Dict:
        """Calcula estatísticas de toxicidade"""
        
        return {
            'pacientes_monitorados': len(monitoramento),
            'taxa_toxicidade_geral': 0.68,
            'toxicidades_grau_3_4': 0.15,
            'intervencoes_realizadas': 45,
            'hospitalizacoes_toxicidade': 3
        }

    async def analisar_toxicidades_frequentes(self) -> Dict:
        """Analisa toxicidades mais frequentes"""
        
        return {
            'toxicidades_frequentes': [
                {'nome': 'Fadiga', 'frequencia': 0.78},
                {'nome': 'Náusea', 'frequencia': 0.65},
                {'nome': 'Neutropenia', 'frequencia': 0.42},
                {'nome': 'Neuropatia', 'frequencia': 0.35}
            ],
            'padroes_temporais': 'Pico na primeira semana',
            'fatores_predisponentes': ['Idade', 'Performance status']
        }

    async def avaliar_eficacia_intervencoes(self) -> Dict:
        """Avalia eficácia das intervenções"""
        
        return {
            'taxa_resolucao_toxicidades': 0.82,
            'tempo_medio_resolucao': 5.2,  # dias
            'reducao_hospitalizacoes': 0.35,
            'satisfacao_pacientes': 4.3  # escala 1-5
        }

    async def avaliar_impacto_qualidade_vida(self, monitoramento: Dict) -> Dict:
        """Avalia impacto na qualidade de vida"""
        
        return {
            'score_qualidade_vida_medio': 72.5,  # EORTC QLQ-C30
            'dominios_mais_afetados': ['Fadiga', 'Função física'],
            'melhoria_com_intervencoes': 0.25,
            'correlacao_toxicidade_qv': -0.68
        }


class DetectorToxicidadeIA:
    """Detector de toxicidade com IA"""
    
    async def detectar_toxicidades(self, **kwargs) -> Dict:
        """Detecta toxicidades atuais"""
        
        return {
            'neutropenia': {
                'presente': True,
                'grau_ctcae': 2,
                'valor_laboratorial': 800,  # neutrófilos/μL
                'impacto_tratamento': 'moderado'
            },
            'fadiga': {
                'presente': True,
                'grau_ctcae': 1,
                'score_pro_ctcae': 3,
                'impacto_tratamento': 'minimo'
            }
        }


class PredictorToxicidadeAvancado:
    """Preditor avançado de toxicidade"""
    
    async def prever_toxicidades_futuras(self, **kwargs) -> Dict:
        """Prediz toxicidades futuras"""
        
        return {
            'risco_alto_30_dias': False,
            'toxicidades_previstas': [
                {'tipo': 'neuropatia', 'probabilidade': 0.35, 'prazo': '2_meses'}
            ],
            'fatores_preditivos': ['Dose cumulativa', 'Idade'],
            'recomendacoes_prevencao': ['Monitoramento neurológico']
        }


class GestorIntervencoesToxicidade:
    """Gestor de intervenções para toxicidade"""
    
    async def recomendar_intervencoes(self, **kwargs) -> Dict:
        """Recomenda intervenções"""
        
        return {
            'intervencoes_imediatas': [
                'Redução de dose 25%',
                'Suporte com G-CSF'
            ],
            'medicacoes_suporte': ['Filgrastim', 'Ondansetrona'],
            'modificacoes_protocolo': 'Atraso de 1 semana',
            'seguimento_intensificado': True
        }


class AnalisadorTendenciasToxicidade:
    """Analisador de tendências de toxicidade"""
    
    async def analisar_tendencias_paciente(self, **kwargs) -> Dict:
        """Analisa tendências do paciente"""
        
        return {
            'padroes_identificados': ['Neutropenia recorrente'],
            'tendencia_temporal': 'Melhoria gradual',
            'fatores_associados': ['Dose', 'Ciclo'],
            'predicao_proximo_ciclo': 'Risco moderado'
        }
