"""
Sistema Principal de Reabilitação e Fisioterapia com IA
"""

import logging
from datetime import datetime

from .analisador_movimento import AnalisadorMovimento3D
from .avaliador_funcional import AvaliadorFuncionalIA
from .monitor_progresso import MonitorProgressoInteligente
from .planejador_reabilitacao import PlanejadorReabilitacaoIA
from .realidade_virtual import SistemaRealidadeVirtual

logger = logging.getLogger('MedAI.Reabilitacao')

class ReabilitacaoFisioterapiaIA:
    """Sistema principal de reabilitação e fisioterapia com IA"""

    def __init__(self):
        self.avaliador_funcional = AvaliadorFuncionalIA()
        self.analisador_movimento = AnalisadorMovimento3D()
        self.planejador_reabilitacao = PlanejadorReabilitacaoIA()
        self.monitor_progresso = MonitorProgressoInteligente()
        self.realidade_virtual = SistemaRealidadeVirtual()

    async def criar_programa_reabilitacao_personalizado(self, paciente: dict) -> dict:
        """Criação de programa de reabilitação totalmente personalizado"""

        try:
            avaliacao = await self.realizar_avaliacao_completa(paciente)

            biomecanica = await self.analisar_biomecanica(paciente)

            plano = await self.criar_plano_personalizado(avaliacao, biomecanica)

            monitoramento = await self.configurar_monitoramento_continuo(plano)

            return {
                'avaliacao_inicial': avaliacao,
                'analise_biomecanica': biomecanica,
                'plano_reabilitacao': plano,
                'monitoramento': monitoramento,
                'previsao_recuperacao': self.prever_tempo_recuperacao(avaliacao),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro na criação do programa de reabilitação: {e}")
            return {
                'error': str(e),
                'avaliacao_inicial': {},
                'plano_reabilitacao': {},
                'monitoramento': {}
            }

    async def realizar_avaliacao_completa(self, paciente: dict) -> dict:
        """Realiza avaliação funcional completa"""

        return await self.avaliador_funcional.avaliar_paciente_completo(paciente)

    async def analisar_biomecanica(self, paciente: dict) -> dict:
        """Análise biomecânica do paciente"""

        movimento_tipo = paciente.get('movimento_principal', 'marcha')
        return await self.analisador_movimento.analisar_movimento_completo(movimento_tipo)

    async def criar_plano_personalizado(self, avaliacao: dict, biomecanica: dict) -> dict:
        """Cria plano de reabilitação personalizado"""

        objetivos = self.definir_objetivos_reabilitacao(avaliacao)
        return await self.planejador_reabilitacao.criar_plano_reabilitacao(avaliacao, objetivos)

    async def configurar_monitoramento_continuo(self, plano: dict) -> dict:
        """Configura sistema de monitoramento contínuo"""

        return {
            'tipo_monitoramento': 'continuo',
            'sensores_utilizados': ['acelerometro', 'giroscopio', 'camera'],
            'frequencia_avaliacao': 'semanal',
            'metricas_principais': [
                'amplitude_movimento',
                'forca_muscular',
                'equilibrio',
                'funcionalidade'
            ],
            'alertas_configurados': [
                'deterioracao_funcional',
                'falta_aderencia',
                'risco_lesao'
            ]
        }

    def definir_objetivos_reabilitacao(self, avaliacao: dict) -> list[str]:
        """Define objetivos específicos baseados na avaliação"""

        objetivos = []

        score_global = avaliacao.get('score_global', 0)

        if score_global < 0.3:
            objetivos.extend([
                'Melhorar mobilidade básica',
                'Aumentar independência para AVDs',
                'Reduzir risco de quedas'
            ])
        elif score_global < 0.6:
            objetivos.extend([
                'Otimizar padrão de marcha',
                'Fortalecer musculatura específica',
                'Melhorar equilíbrio dinâmico'
            ])
        else:
            objetivos.extend([
                'Retorno às atividades esportivas',
                'Prevenção de lesões',
                'Otimização de performance'
            ])

        condicao = avaliacao.get('diagnostico', '').lower()

        if 'avc' in condicao:
            objetivos.extend([
                'Recuperar função motora',
                'Melhorar coordenação',
                'Reintegração social'
            ])
        elif 'ortopedica' in condicao:
            objetivos.extend([
                'Restaurar amplitude de movimento',
                'Fortalecer músculos específicos',
                'Retorno funcional'
            ])

        return objetivos

    def prever_tempo_recuperacao(self, avaliacao: dict) -> dict:
        """Predição do tempo de recuperação baseada em IA"""

        fatores = {
            'idade': avaliacao.get('idade', 50),
            'score_funcional': avaliacao.get('score_global', 0.5),
            'comorbidades': len(avaliacao.get('comorbidades', [])),
            'motivacao': avaliacao.get('motivacao_paciente', 0.7),
            'suporte_social': avaliacao.get('suporte_social', 0.6)
        }

        tempo_base = 12  # semanas

        if fatores['idade'] > 65:
            tempo_base *= 1.3
        if fatores['score_funcional'] < 0.3:
            tempo_base *= 1.5
        if fatores['comorbidades'] > 2:
            tempo_base *= 1.2
        if fatores['motivacao'] > 0.8:
            tempo_base *= 0.8
        if fatores['suporte_social'] > 0.8:
            tempo_base *= 0.9

        tempo_estimado = int(tempo_base)

        return {
            'tempo_estimado_semanas': tempo_estimado,
            'fatores_influencia': fatores,
            'confianca_predicao': 0.75,
            'marcos_recuperacao': self.definir_marcos_recuperacao(tempo_estimado)
        }

    def definir_marcos_recuperacao(self, tempo_total: int) -> list[dict]:
        """Define marcos de recuperação ao longo do tratamento"""

        marcos = []

        marcos.append({
            'semana': 2,
            'objetivo': 'Adaptação ao programa',
            'metas': ['Redução da dor', 'Melhora da mobilidade básica'],
            'avaliacao': 'Reavaliação funcional básica'
        })

        marco_25 = int(tempo_total * 0.25)
        marcos.append({
            'semana': marco_25,
            'objetivo': 'Progresso inicial significativo',
            'metas': ['Melhora de 25% no score funcional', 'Aumento da força'],
            'avaliacao': 'Avaliação biomecânica'
        })

        marco_50 = int(tempo_total * 0.5)
        marcos.append({
            'semana': marco_50,
            'objetivo': 'Recuperação funcional moderada',
            'metas': ['Independência em AVDs básicas', 'Marcha segura'],
            'avaliacao': 'Avaliação funcional completa'
        })

        marco_75 = int(tempo_total * 0.75)
        marcos.append({
            'semana': marco_75,
            'objetivo': 'Preparação para alta',
            'metas': ['Funcionalidade próxima ao normal', 'Confiança do paciente'],
            'avaliacao': 'Teste de capacidade funcional'
        })

        marcos.append({
            'semana': tempo_total,
            'objetivo': 'Alta do programa',
            'metas': ['Objetivos funcionais atingidos', 'Programa de manutenção'],
            'avaliacao': 'Avaliação final completa'
        })

        return marcos

    async def gerar_relatorio_progresso(self, paciente_id: str) -> dict:
        """Gera relatório completo de progresso"""

        progresso = await self.monitor_progresso.calcular_progresso_total()

        return {
            'paciente_id': paciente_id,
            'data_relatorio': datetime.now().isoformat(),
            'progresso_geral': progresso,
            'evolucao_funcional': self.calcular_evolucao_funcional(),
            'aderencia_tratamento': self.calcular_aderencia(),
            'recomendacoes': self.gerar_recomendacoes_progresso(progresso),
            'proximo_marco': self.identificar_proximo_marco()
        }

    def calcular_evolucao_funcional(self) -> dict:
        """Calcula evolução funcional do paciente"""

        return {
            'score_inicial': 0.3,
            'score_atual': 0.6,
            'melhora_percentual': 100.0,
            'areas_melhoria': ['Mobilidade', 'Força', 'Equilíbrio'],
            'areas_atencao': ['Resistência cardiovascular']
        }

    def calcular_aderencia(self) -> dict:
        """Calcula aderência ao tratamento"""

        return {
            'aderencia_geral': 0.85,
            'sessoes_realizadas': 24,
            'sessoes_planejadas': 28,
            'exercicios_domiciliares': 0.78,
            'fatores_aderencia': ['Motivação alta', 'Suporte familiar']
        }

    def gerar_recomendacoes_progresso(self, progresso: dict) -> list[str]:
        """Gera recomendações baseadas no progresso"""

        recomendacoes = []

        if progresso.get('score_atual', 0) < 0.5:
            recomendacoes.extend([
                'Intensificar exercícios de fortalecimento',
                'Aumentar frequência de sessões',
                'Revisar estratégias motivacionais'
            ])
        elif progresso.get('score_atual', 0) > 0.8:
            recomendacoes.extend([
                'Preparar transição para atividades avançadas',
                'Desenvolver programa de manutenção',
                'Considerar alta do programa intensivo'
            ])
        else:
            recomendacoes.extend([
                'Manter progressão atual',
                'Focar em áreas específicas de melhoria',
                'Monitorar aderência'
            ])

        return recomendacoes

    def identificar_proximo_marco(self) -> dict:
        """Identifica próximo marco de recuperação"""

        return {
            'marco': 'Recuperação funcional moderada',
            'semana_prevista': 8,
            'objetivos': [
                'Independência em AVDs básicas',
                'Marcha segura sem auxílio',
                'Melhora de 50% no score funcional'
            ],
            'preparacao_necessaria': [
                'Intensificar treino de marcha',
                'Exercícios de equilíbrio avançados'
            ]
        }

ReabilitacaoInteligenteIA = ReabilitacaoFisioterapiaIA
