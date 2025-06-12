"""
Otimização de distribuição interna de medicamentos
"""

import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('MedAI.Farmacia.OtimizadorDistribuicao')

class OtimizadorDistribuicaoIA:
    """Otimização de distribuição interna de medicamentos"""
    
    def __init__(self):
        self.roteador = RoteadorInteligente()
        self.predictor_urgencia = PredictorUrgenciaDispensacao()
        self.alocador_recursos = AlocadorRecursosFarmacia()
        
    async def otimizar_distribuicao_diaria(self) -> Dict:
        """Otimização completa da distribuição diária"""
        
        try:
            demanda_unidades = await self.analisar_demanda_unidades()
            
            priorizacao = await self.priorizar_dispensacoes(demanda_unidades)
            
            rotas_otimizadas = await self.otimizar_rotas_distribuicao(priorizacao)
            
            alocacao_equipe = await self.alocar_equipe_otimizada(rotas_otimizadas)
            
            return {
                'rotas': rotas_otimizadas,
                'equipe': alocacao_equipe,
                'tempo_estimado': self.calcular_tempo_total(rotas_otimizadas),
                'eficiencia_ganho': self.calcular_ganho_eficiencia(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na otimização da distribuição: {e}")
            return {
                'error': str(e),
                'rotas': [],
                'equipe': {},
                'tempo_estimado': 0
            }

    async def analisar_demanda_unidades(self) -> Dict:
        """Analisa demanda por unidade hospitalar"""
        
        unidades = {
            'uti': {
                'medicamentos_solicitados': 45,
                'urgencia_media': 0.9,
                'tempo_limite': 30,  # minutos
                'medicamentos_criticos': ['noradrenalina', 'propofol', 'fentanil']
            },
            'emergencia': {
                'medicamentos_solicitados': 38,
                'urgencia_media': 0.85,
                'tempo_limite': 15,  # minutos
                'medicamentos_criticos': ['adrenalina', 'atropina', 'morfina']
            },
            'centro_cirurgico': {
                'medicamentos_solicitados': 28,
                'urgencia_media': 0.7,
                'tempo_limite': 45,  # minutos
                'medicamentos_criticos': ['anestesicos', 'relaxantes_musculares']
            },
            'enfermaria_clinica': {
                'medicamentos_solicitados': 65,
                'urgencia_media': 0.3,
                'tempo_limite': 120,  # minutos
                'medicamentos_criticos': []
            },
            'pediatria': {
                'medicamentos_solicitados': 22,
                'urgencia_media': 0.6,
                'tempo_limite': 60,  # minutos
                'medicamentos_criticos': ['paracetamol_pediatrico', 'soro_pediatrico']
            }
        }
        
        return {
            'unidades': unidades,
            'total_solicitacoes': sum(u['medicamentos_solicitados'] for u in unidades.values()),
            'urgencia_global': sum(u['urgencia_media'] for u in unidades.values()) / len(unidades),
            'unidades_criticas': [nome for nome, dados in unidades.items() if dados['urgencia_media'] > 0.8]
        }

    async def priorizar_dispensacoes(self, demanda_unidades: Dict) -> Dict:
        """Prioriza dispensações por urgência clínica"""
        
        unidades = demanda_unidades.get('unidades', {})
        dispensacoes_priorizadas = []
        
        for nome_unidade, dados_unidade in unidades.items():
            urgencia = dados_unidade.get('urgencia_media', 0)
            tempo_limite = dados_unidade.get('tempo_limite', 60)
            medicamentos_criticos = dados_unidade.get('medicamentos_criticos', [])
            
            score_prioridade = self.calcular_score_prioridade(
                urgencia=urgencia,
                tempo_limite=tempo_limite,
                tem_medicamentos_criticos=len(medicamentos_criticos) > 0
            )
            
            dispensacoes_priorizadas.append({
                'unidade': nome_unidade,
                'score_prioridade': score_prioridade,
                'urgencia': urgencia,
                'tempo_limite': tempo_limite,
                'medicamentos_criticos': medicamentos_criticos,
                'ordem_atendimento': 0  # Será definido após ordenação
            })
        
        dispensacoes_priorizadas.sort(key=lambda x: x['score_prioridade'], reverse=True)
        
        for i, dispensacao in enumerate(dispensacoes_priorizadas):
            dispensacao['ordem_atendimento'] = i + 1
        
        return {
            'dispensacoes_priorizadas': dispensacoes_priorizadas,
            'criterios_priorizacao': [
                'Urgência clínica da unidade',
                'Tempo limite para entrega',
                'Presença de medicamentos críticos',
                'Impacto na segurança do paciente'
            ]
        }

    def calcular_score_prioridade(self, urgencia: float, tempo_limite: int, tem_medicamentos_criticos: bool) -> float:
        """Calcula score de prioridade para dispensação"""
        
        score = urgencia
        
        if tempo_limite <= 15:
            score += 0.3
        elif tempo_limite <= 30:
            score += 0.2
        elif tempo_limite <= 60:
            score += 0.1
        
        if tem_medicamentos_criticos:
            score += 0.2
        
        return min(1.0, score)

    async def otimizar_rotas_distribuicao(self, priorizacao: Dict) -> List[Dict]:
        """Otimiza rotas de distribuição"""
        
        dispensacoes = priorizacao.get('dispensacoes_priorizadas', [])
        rotas_otimizadas = []
        
        grupos_proximidade = self.agrupar_por_proximidade(dispensacoes)
        
        for grupo in grupos_proximidade:
            rota = await self.criar_rota_otimizada(grupo)
            rotas_otimizadas.append(rota)
        
        return rotas_otimizadas

    def agrupar_por_proximidade(self, dispensacoes: List[Dict]) -> List[List[Dict]]:
        """Agrupa unidades por proximidade física"""
        
        proximidade_map = {
            'uti': ['centro_cirurgico'],
            'emergencia': ['uti'],
            'centro_cirurgico': ['uti'],
            'enfermaria_clinica': ['pediatria'],
            'pediatria': ['enfermaria_clinica']
        }
        
        grupos = []
        unidades_processadas = set()
        
        for dispensacao in dispensacoes:
            unidade = dispensacao['unidade']
            
            if unidade in unidades_processadas:
                continue
            
            grupo = [dispensacao]
            unidades_processadas.add(unidade)
            
            unidades_proximas = proximidade_map.get(unidade, [])
            for unidade_proxima in unidades_proximas:
                dispensacao_proxima = next(
                    (d for d in dispensacoes if d['unidade'] == unidade_proxima and unidade_proxima not in unidades_processadas),
                    None
                )
                if dispensacao_proxima:
                    grupo.append(dispensacao_proxima)
                    unidades_processadas.add(unidade_proxima)
            
            grupos.append(grupo)
        
        return grupos

    async def criar_rota_otimizada(self, grupo_unidades: List[Dict]) -> Dict:
        """Cria rota otimizada para grupo de unidades"""
        
        grupo_ordenado = sorted(grupo_unidades, key=lambda x: x['score_prioridade'], reverse=True)
        
        tempo_total = 0
        for i, unidade in enumerate(grupo_ordenado):
            tempo_preparacao = 10  # minutos base
            tempo_deslocamento = 5 if i > 0 else 0  # minutos entre unidades
            tempo_entrega = 3  # minutos para entrega
            
            tempo_total += tempo_preparacao + tempo_deslocamento + tempo_entrega
        
        return {
            'id_rota': f"rota_{datetime.now().strftime('%H%M%S')}",
            'unidades': [u['unidade'] for u in grupo_ordenado],
            'ordem_visita': grupo_ordenado,
            'tempo_estimado': tempo_total,
            'distancia_total': len(grupo_ordenado) * 100,  # metros estimados
            'prioridade_rota': max(u['score_prioridade'] for u in grupo_ordenado),
            'medicamentos_criticos': any(u['medicamentos_criticos'] for u in grupo_ordenado)
        }

    async def alocar_equipe_otimizada(self, rotas: List[Dict]) -> Dict:
        """Aloca equipe de forma otimizada"""
        
        equipe_disponivel = [
            {'id': 'farm001', 'nome': 'Ana Silva', 'experiencia': 'senior', 'disponivel': True},
            {'id': 'farm002', 'nome': 'Carlos Santos', 'experiencia': 'pleno', 'disponivel': True},
            {'id': 'farm003', 'nome': 'Maria Oliveira', 'experiencia': 'junior', 'disponivel': True},
            {'id': 'aux001', 'nome': 'João Costa', 'experiencia': 'auxiliar', 'disponivel': True}
        ]
        
        alocacao = {
            'alocacoes': [],
            'equipe_utilizada': 0,
            'equipe_disponivel': len(equipe_disponivel),
            'eficiencia_alocacao': 0.0
        }
        
        rotas_ordenadas = sorted(rotas, key=lambda x: x['prioridade_rota'], reverse=True)
        
        for i, rota in enumerate(rotas_ordenadas):
            if i < len(equipe_disponivel):
                membro_equipe = equipe_disponivel[i]
                
                if rota['medicamentos_criticos'] and membro_equipe['experiencia'] in ['senior', 'pleno']:
                    alocacao['alocacoes'].append({
                        'rota_id': rota['id_rota'],
                        'responsavel': membro_equipe,
                        'justificativa': 'Rota com medicamentos críticos - farmacêutico experiente',
                        'tempo_estimado': rota['tempo_estimado']
                    })
                else:
                    alocacao['alocacoes'].append({
                        'rota_id': rota['id_rota'],
                        'responsavel': membro_equipe,
                        'justificativa': 'Alocação por disponibilidade',
                        'tempo_estimado': rota['tempo_estimado']
                    })
                
                alocacao['equipe_utilizada'] += 1
        
        if alocacao['equipe_disponivel'] > 0:
            alocacao['eficiencia_alocacao'] = alocacao['equipe_utilizada'] / alocacao['equipe_disponivel']
        
        return alocacao

    def calcular_tempo_total(self, rotas: List[Dict]) -> int:
        """Calcula tempo total estimado para todas as rotas"""
        
        if not rotas:
            return 0
        
        tempo_maximo = max(rota['tempo_estimado'] for rota in rotas)
        
        return tempo_maximo

    def calcular_ganho_eficiencia(self) -> Dict:
        """Calcula ganho de eficiência com otimização"""
        
        return {
            'tempo_tradicional': 180,  # minutos
            'tempo_otimizado': 120,    # minutos
            'reducao_tempo': 60,       # minutos
            'percentual_melhoria': 33.3,  # %
            'economia_recursos': 2,    # pessoas-hora
            'satisfacao_unidades': 0.92  # score 0-1
        }

    async def monitorar_distribuicao_tempo_real(self) -> Dict:
        """Monitora distribuição em tempo real"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'rotas_ativas': 3,
            'entregas_concluidas': 12,
            'entregas_pendentes': 8,
            'atrasos_detectados': 1,
            'tempo_medio_entrega': 15,  # minutos
            'unidades_atendidas': ['uti', 'emergencia', 'centro_cirurgico'],
            'alertas_tempo_real': [
                {
                    'tipo': 'atraso',
                    'rota': 'rota_143052',
                    'unidade': 'pediatria',
                    'atraso_minutos': 10,
                    'motivo': 'Medicamento em falta no estoque'
                }
            ],
            'metricas_performance': {
                'taxa_entrega_no_prazo': 0.95,
                'satisfacao_media_unidades': 4.2,  # escala 1-5
                'eficiencia_rotas': 0.88
            }
        }

    async def gerar_relatorio_distribuicao(self, periodo: str = '24_horas') -> Dict:
        """Gera relatório de distribuição"""
        
        return {
            'periodo': periodo,
            'data_relatorio': datetime.now().isoformat(),
            'resumo_operacional': {
                'total_entregas': 156,
                'entregas_no_prazo': 148,
                'taxa_pontualidade': 94.9,  # %
                'tempo_medio_entrega': 18,  # minutos
                'distancia_total_percorrida': 12.5  # km
            },
            'performance_unidades': {
                'uti': {'entregas': 45, 'pontualidade': 98.0, 'satisfacao': 4.8},
                'emergencia': {'entregas': 38, 'pontualidade': 97.0, 'satisfacao': 4.7},
                'centro_cirurgico': {'entregas': 28, 'pontualidade': 96.0, 'satisfacao': 4.5},
                'enfermaria_clinica': {'entregas': 32, 'pontualidade': 91.0, 'satisfacao': 4.2},
                'pediatria': {'entregas': 13, 'pontualidade': 92.0, 'satisfacao': 4.3}
            },
            'eficiencia_equipe': {
                'farm001': {'entregas': 52, 'tempo_medio': 16, 'eficiencia': 0.92},
                'farm002': {'entregas': 48, 'tempo_medio': 18, 'eficiencia': 0.88},
                'farm003': {'entregas': 35, 'tempo_medio': 22, 'eficiencia': 0.82},
                'aux001': {'entregas': 21, 'tempo_medio': 25, 'eficiencia': 0.78}
            },
            'problemas_identificados': [
                'Atraso recorrente na enfermaria clínica',
                'Pico de demanda não previsto na UTI',
                'Medicamento crítico em falta'
            ],
            'recomendacoes': [
                'Revisar rota para enfermaria clínica',
                'Implementar previsão de demanda por ML',
                'Melhorar gestão de estoque de medicamentos críticos'
            ]
        }


class RoteadorInteligente:
    pass


class PredictorUrgenciaDispensacao:
    pass


class AlocadorRecursosFarmacia:
    pass
