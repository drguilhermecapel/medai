"""
Sistema de Realidade Virtual para Reabilitação
"""

import asyncio
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger('MedAI.Reabilitacao.RealidadeVirtual')

class SistemaRealidadeVirtual:
    """Sistema de reabilitação com realidade virtual"""
    
    def __init__(self):
        self.ambiente_vr = AmbienteVirtualTerapeutico()
        self.gamificador = GamificadorReabilitacao()
        self.adaptador_dificuldade = AdaptadorDificuldadeIA()
        
    async def criar_sessao_vr_personalizada(self, paciente: Dict, objetivos: List) -> Dict:
        """Criação de sessão de reabilitação em VR"""
        
        try:
            ambiente = await self.selecionar_ambiente_terapeutico(
                condicao=paciente.get('condicao', ''),
                preferencias=paciente.get('preferencias_vr', {}),
                objetivos_terapeuticos=objetivos
            )
            
            exercicios_vr = await self.gamificador.criar_exercicios_gamificados(
                exercicios_base=objetivos,
                nivel_dificuldade=paciente.get('nivel_funcional', 'moderado'),
                elementos_motivacionais=self.definir_elementos_motivacionais(paciente)
            )
            
            sistema_recompensas = self.criar_sistema_recompensas(
                perfil_paciente=paciente,
                metas_curto_prazo=True,
                metas_longo_prazo=True
            )
            
            configuracao_adaptativa = {
                'ajuste_dificuldade': 'automatico',
                'threshold_sucesso': 0.7,
                'threshold_frustacao': 0.3,
                'velocidade_adaptacao': 'moderada'
            }
            
            return {
                'ambiente': ambiente,
                'exercicios': exercicios_vr,
                'recompensas': sistema_recompensas,
                'configuracao': configuracao_adaptativa,
                'metricas_engajamento': self.definir_metricas_engajamento(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na criação da sessão VR: {e}")
            return {
                'error': str(e),
                'ambiente': {},
                'exercicios': []
            }

    async def selecionar_ambiente_terapeutico(self, condicao: str, preferencias: Dict, objetivos_terapeuticos: List) -> Dict:
        """Seleciona ambiente virtual mais adequado"""
        
        ambientes_disponiveis = {
            'casa_virtual': {
                'descricao': 'Ambiente doméstico para treino de AVDs',
                'indicacoes': ['reabilitacao_funcional', 'treino_avds'],
                'elementos': ['cozinha', 'banheiro', 'sala', 'escadas'],
                'dificuldade': 'baixa_moderada'
            },
            'parque_natural': {
                'descricao': 'Ambiente natural para exercícios de equilíbrio',
                'indicacoes': ['treino_equilibrio', 'marcha_terrenos'],
                'elementos': ['trilhas', 'obstaculos_naturais', 'terrenos_variados'],
                'dificuldade': 'moderada_alta'
            },
            'academia_virtual': {
                'descricao': 'Ambiente de academia para fortalecimento',
                'indicacoes': ['fortalecimento', 'condicionamento'],
                'elementos': ['equipamentos', 'espelhos', 'instrutor_virtual'],
                'dificuldade': 'baixa_alta'
            },
            'cidade_virtual': {
                'descricao': 'Ambiente urbano para reintegração social',
                'indicacoes': ['reintegracao_social', 'navegacao_urbana'],
                'elementos': ['ruas', 'transporte_publico', 'lojas', 'multidoes'],
                'dificuldade': 'alta'
            }
        }
        
        ambiente_selecionado = 'casa_virtual'  # Default
        
        if any('equilibrio' in obj.lower() for obj in objetivos_terapeuticos):
            ambiente_selecionado = 'parque_natural'
        elif any('forca' in obj.lower() for obj in objetivos_terapeuticos):
            ambiente_selecionado = 'academia_virtual'
        elif any('social' in obj.lower() for obj in objetivos_terapeuticos):
            ambiente_selecionado = 'cidade_virtual'
        
        ambiente = ambientes_disponiveis[ambiente_selecionado]
        ambiente['nome'] = ambiente_selecionado
        
        return ambiente

    def definir_elementos_motivacionais(self, paciente: Dict) -> List[str]:
        """Define elementos motivacionais baseados no perfil"""
        
        elementos = []
        
        idade = paciente.get('idade', 50)
        if idade < 30:
            elementos.extend(['pontuacao_competitiva', 'rankings', 'conquistas'])
        elif idade < 60:
            elementos.extend(['progresso_visual', 'metas_pessoais', 'feedback_positivo'])
        else:
            elementos.extend(['encorajamento_verbal', 'progresso_gradual', 'celebracao_marcos'])
        
        preferencias = paciente.get('preferencias', {})
        if preferencias.get('gosta_jogos', False):
            elementos.extend(['elementos_jogo', 'desafios', 'narrativa'])
        if preferencias.get('competitivo', False):
            elementos.extend(['comparacao_performance', 'desafios_tempo'])
        
        return elementos

    def criar_sistema_recompensas(self, perfil_paciente: Dict, metas_curto_prazo: bool, metas_longo_prazo: bool) -> Dict:
        """Cria sistema de recompensas personalizado"""
        
        sistema = {
            'tipos_recompensa': [],
            'criterios_desbloqueio': {},
            'progressao': {}
        }
        
        if metas_curto_prazo:
            sistema['tipos_recompensa'].extend([
                'feedback_imediato',
                'pontos_por_exercicio',
                'badges_diarias'
            ])
            sistema['criterios_desbloqueio']['curto_prazo'] = {
                'exercicio_completo': 10,
                'qualidade_boa': 25,
                'sessao_completa': 50
            }
        
        if metas_longo_prazo:
            sistema['tipos_recompensa'].extend([
                'desbloqueio_ambientes',
                'personalizacao_avatar',
                'certificados_progresso'
            ])
            sistema['criterios_desbloqueio']['longo_prazo'] = {
                'semana_completa': 200,
                'marco_funcional': 500,
                'objetivo_atingido': 1000
            }
        
        sistema['progressao'] = {
            'nivel_inicial': 1,
            'pontos_proximo_nivel': 100,
            'multiplicador_dificuldade': 1.2,
            'bonus_consistencia': 0.1
        }
        
        return sistema

    def definir_metricas_engajamento(self) -> Dict:
        """Define métricas para medir engajamento"""
        
        return {
            'tempo_sessao': 'minutos_ativo',
            'interacoes_por_minuto': 'frequencia_comandos',
            'taxa_conclusao': 'exercicios_completados/planejados',
            'nivel_frustacao': 'tentativas_falhadas/total',
            'satisfacao_subjetiva': 'escala_1_10',
            'retorno_voluntario': 'sessoes_extras_iniciadas',
            'progressao_dificuldade': 'niveis_avancados_atingidos'
        }

    async def executar_sessao_vr(self, configuracao_sessao: Dict) -> Dict:
        """Executa sessão de VR e coleta métricas"""
        
        try:
            resultados = {
                'inicio_sessao': datetime.now().isoformat(),
                'exercicios_executados': [],
                'metricas_coletadas': {},
                'adaptacoes_realizadas': [],
                'feedback_paciente': {}
            }
            
            for exercicio in configuracao_sessao.get('exercicios', []):
                resultado_exercicio = await self.executar_exercicio_vr(exercicio)
                resultados['exercicios_executados'].append(resultado_exercicio)
                
                performance = self.analisar_performance_tempo_real(resultado_exercicio)
                
                if performance['necessita_adaptacao']:
                    adaptacao = await self.adaptador_dificuldade.adaptar_exercicio(
                        exercicio, performance
                    )
                    resultados['adaptacoes_realizadas'].append(adaptacao)
            
            resultados['metricas_coletadas'] = self.calcular_metricas_sessao(resultados)
            
            resultados['feedback_paciente'] = await self.coletar_feedback_paciente()
            
            resultados['fim_sessao'] = datetime.now().isoformat()
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro na execução da sessão VR: {e}")
            return {
                'error': str(e),
                'exercicios_executados': [],
                'metricas_coletadas': {}
            }

    async def executar_exercicio_vr(self, exercicio: Dict) -> Dict:
        """Executa exercício individual em VR"""
        
        return {
            'exercicio': exercicio.get('nome', 'Exercício VR'),
            'tempo_execucao': 180,  # segundos
            'tentativas': 3,
            'sucessos': 2,
            'taxa_sucesso': 0.67,
            'pontuacao': 85,
            'qualidade_movimento': 0.8,
            'engajamento': 0.9,
            'dificuldade_percebida': 6,  # escala 1-10
            'satisfacao': 8  # escala 1-10
        }

    def analisar_performance_tempo_real(self, resultado_exercicio: Dict) -> Dict:
        """Analisa performance em tempo real"""
        
        taxa_sucesso = resultado_exercicio.get('taxa_sucesso', 0)
        dificuldade_percebida = resultado_exercicio.get('dificuldade_percebida', 5)
        
        return {
            'performance_adequada': 0.4 <= taxa_sucesso <= 0.8,
            'muito_facil': taxa_sucesso > 0.9 and dificuldade_percebida < 4,
            'muito_dificil': taxa_sucesso < 0.3 and dificuldade_percebida > 7,
            'necessita_adaptacao': taxa_sucesso < 0.3 or taxa_sucesso > 0.9,
            'direcao_adaptacao': 'aumentar' if taxa_sucesso > 0.9 else 'diminuir'
        }

    def calcular_metricas_sessao(self, resultados: Dict) -> Dict:
        """Calcula métricas consolidadas da sessão"""
        
        exercicios = resultados.get('exercicios_executados', [])
        
        if not exercicios:
            return {}
        
        taxa_sucesso_media = sum(ex.get('taxa_sucesso', 0) for ex in exercicios) / len(exercicios)
        engajamento_medio = sum(ex.get('engajamento', 0) for ex in exercicios) / len(exercicios)
        satisfacao_media = sum(ex.get('satisfacao', 0) for ex in exercicios) / len(exercicios)
        
        return {
            'taxa_sucesso_sessao': taxa_sucesso_media,
            'engajamento_sessao': engajamento_medio,
            'satisfacao_sessao': satisfacao_media,
            'exercicios_completados': len(exercicios),
            'tempo_total_sessao': sum(ex.get('tempo_execucao', 0) for ex in exercicios),
            'adaptacoes_necessarias': len(resultados.get('adaptacoes_realizadas', [])),
            'score_sessao_geral': (taxa_sucesso_media + engajamento_medio + satisfacao_media/10) / 3
        }

    async def coletar_feedback_paciente(self) -> Dict:
        """Coleta feedback do paciente sobre a sessão VR"""
        
        return {
            'facilidade_uso': 8,  # 1-10
            'conforto_visual': 7,
            'motivacao_continuar': 9,
            'realismo_ambiente': 8,
            'utilidade_percebida': 9,
            'desconforto_fisico': 2,  # 1-10 (menor é melhor)
            'enjoo_movimento': 1,
            'comentarios_livres': 'Gostei muito do ambiente da academia virtual',
            'sugestoes_melhoria': ['Mais variedade de exercícios', 'Música de fundo']
        }

    async def gerar_relatorio_vr(self, paciente_id: str, periodo: str = '1_mes') -> Dict:
        """Gera relatório de uso de VR"""
        
        return {
            'paciente_id': paciente_id,
            'periodo': periodo,
            'data_relatorio': datetime.now().isoformat(),
            'resumo_uso': {
                'sessoes_realizadas': 12,
                'tempo_total_vr': 720,  # minutos
                'ambientes_utilizados': ['casa_virtual', 'academia_virtual'],
                'exercicios_dominados': 8,
                'nivel_atual': 3
            },
            'progressao_metricas': {
                'engajamento_inicial': 0.6,
                'engajamento_atual': 0.85,
                'satisfacao_inicial': 6,
                'satisfacao_atual': 8.5,
                'taxa_sucesso_inicial': 0.4,
                'taxa_sucesso_atual': 0.75
            },
            'recomendacoes': [
                'Introduzir ambiente parque natural',
                'Aumentar dificuldade dos exercícios de equilíbrio',
                'Manter frequência atual de sessões'
            ],
            'alertas': [],
            'proximos_objetivos': [
                'Desbloqueio do ambiente cidade virtual',
                'Atingir nível 4 de dificuldade',
                'Completar programa de reintegração social'
            ]
        }


class AmbienteVirtualTerapeutico:
    pass


class GamificadorReabilitacao:
    async def criar_exercicios_gamificados(self, exercicios_base: List, nivel_dificuldade: str, elementos_motivacionais: List) -> List[Dict]:
        """Cria exercícios gamificados"""
        
        exercicios_gamificados = []
        
        for i, exercicio in enumerate(exercicios_base[:3]):  # Limita a 3 exercícios
            exercicio_gamificado = {
                'nome': f'Desafio {i+1}: {exercicio}',
                'tipo': 'gamificado',
                'nivel_dificuldade': nivel_dificuldade,
                'elementos_jogo': elementos_motivacionais[:2],  # Primeiros 2 elementos
                'objetivos_jogo': [
                    'Completar movimento com precisão',
                    'Manter ritmo constante',
                    'Atingir pontuação mínima'
                ],
                'recompensas': {
                    'pontos_base': 50,
                    'bonus_qualidade': 25,
                    'bonus_tempo': 15
                },
                'criterios_sucesso': {
                    'precisao_minima': 0.7,
                    'tempo_maximo': 300,
                    'tentativas_maximas': 5
                }
            }
            exercicios_gamificados.append(exercicio_gamificado)
        
        return exercicios_gamificados


class AdaptadorDificuldadeIA:
    async def adaptar_exercicio(self, exercicio: Dict, performance: Dict) -> Dict:
        """Adapta dificuldade do exercício baseado na performance"""
        
        adaptacao = {
            'exercicio_original': exercicio.get('nome', 'Exercício'),
            'motivo_adaptacao': '',
            'mudancas_realizadas': [],
            'nova_configuracao': {}
        }
        
        if performance.get('muito_facil'):
            adaptacao['motivo_adaptacao'] = 'Exercício muito fácil para o paciente'
            adaptacao['mudancas_realizadas'] = [
                'Aumentar velocidade requerida',
                'Adicionar obstáculos',
                'Reduzir tempo disponível'
            ]
        elif performance.get('muito_dificil'):
            adaptacao['motivo_adaptacao'] = 'Exercício muito difícil para o paciente'
            adaptacao['mudancas_realizadas'] = [
                'Reduzir velocidade requerida',
                'Simplificar movimentos',
                'Aumentar tempo disponível',
                'Adicionar assistência visual'
            ]
        
        adaptacao['nova_configuracao'] = {
            'nivel_dificuldade': 'adaptado',
            'parametros_ajustados': True,
            'timestamp_adaptacao': datetime.now().isoformat()
        }
        
        return adaptacao
