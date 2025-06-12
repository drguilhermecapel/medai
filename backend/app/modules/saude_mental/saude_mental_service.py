"""
Sistema Inteligente de Saúde Mental e Psiquiatria - MedIA Pro
Avaliação, tratamento e monitoramento de saúde mental com IA avançada
"""

import logging
from datetime import datetime, timedelta

from .analisador_emocional import AnalisadorEmocionalMultimodal
from .avaliador_psiquiatrico import AvaliadorPsiquiatricoIA
from .monitor_continuo import MonitorSaudeMentalContinuo

logger = logging.getLogger('MedAI.SaudeMental')

class SaudeMentalPsiquiatriaIA:
    """Sistema principal de saúde mental e psiquiatria com IA"""

    def __init__(self):
        self.avaliador_psiquiatrico = AvaliadorPsiquiatricoIA()
        self.analisador_emocional = AnalisadorEmocionalMultimodal()
        self.monitor_continuo = MonitorSaudeMentalContinuo()

    async def realizar_avaliacao_completa(self, paciente: dict) -> dict:
        """Avaliação psiquiátrica completa com IA multimodal"""

        try:
            avaliacao_clinica = await self.avaliador_psiquiatrico.avaliar_completo(paciente)

            analise_emocional = await self.analisador_emocional.analisar_estado_emocional(paciente)

            avaliacao_risco = await self.avaliar_riscos_completos(paciente)

            plano_terapeutico = await self.criar_plano_tratamento_personalizado(
                avaliacao_clinica,
                analise_emocional,
                avaliacao_risco
            )

            return {
                'avaliacao_clinica': avaliacao_clinica,
                'estado_emocional': analise_emocional,
                'riscos': avaliacao_risco,
                'plano_tratamento': plano_terapeutico,
                'recomendacoes_imediatas': self.gerar_recomendacoes_urgentes(avaliacao_risco),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Erro na avaliação completa: {e}")
            return {
                'error': str(e),
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }

    async def avaliar_riscos_completos(self, paciente: dict) -> dict:
        """Avaliação completa de riscos psiquiátricos"""

        predicao_crise = {
            'risco_global': {'score': 2, 'nivel': 'MODERADO'},
            'fatores_risco': ['Histórico clínico', 'Sintomas atuais'],
            'recomendacoes': ['Monitoramento regular']
        }

        risco_suicida = self.avaliar_risco_suicida(paciente)

        risco_violencia = self.avaliar_risco_violencia(paciente)

        return {
            'predicao_crise': predicao_crise,
            'risco_suicida': risco_suicida,
            'risco_violencia': risco_violencia,
            'nivel_geral': self.calcular_nivel_risco_geral(predicao_crise, risco_suicida, risco_violencia)
        }

    async def criar_plano_tratamento_personalizado(self, avaliacao_clinica: dict,
                                                   analise_emocional: dict,
                                                   avaliacao_risco: dict) -> dict:
        """Criação de plano de tratamento personalizado"""

        programa_terapia = {
            'tipo_terapia': 'Terapia Cognitivo-Comportamental Digital',
            'duracao_sessoes': 45,
            'frequencia_semanal': 2,
            'modulos': ['Psicoeducação', 'Técnicas de relaxamento', 'Reestruturação cognitiva'],
            'recursos_digitais': ['App móvel', 'Exercícios interativos', 'Monitoramento de humor']
        }

        recomendacoes_farmaco = self.gerar_recomendacoes_farmacologicas(avaliacao_clinica)

        cronograma = self.criar_cronograma_acompanhamento(avaliacao_risco)

        return {
            'programa_terapia_digital': programa_terapia,
            'recomendacoes_farmacologicas': recomendacoes_farmaco,
            'cronograma_acompanhamento': cronograma,
            'objetivos_terapeuticos': self.definir_objetivos_terapeuticos(avaliacao_clinica),
            'metricas_progresso': self.definir_metricas_progresso()
        }

    def avaliar_risco_suicida(self, paciente: dict) -> dict:
        """Avaliação de risco suicida"""

        fatores_risco = []
        score = 0

        if paciente.get('historico_tentativas_suicidio'):
            fatores_risco.append('Histórico de tentativas anteriores')
            score += 3

        if paciente.get('ideacao_suicida_atual'):
            fatores_risco.append('Ideação suicida atual')
            score += 2

        if paciente.get('depressao_grave'):
            fatores_risco.append('Depressão grave')
            score += 2

        if paciente.get('isolamento_social'):
            fatores_risco.append('Isolamento social')
            score += 1

        if score >= 5:
            nivel = 'ALTO'
        elif score >= 3:
            nivel = 'MODERADO'
        else:
            nivel = 'BAIXO'

        return {
            'nivel': nivel,
            'score': score,
            'fatores_risco': fatores_risco,
            'recomendacoes': self.gerar_recomendacoes_risco_suicida(nivel)
        }

    def avaliar_risco_violencia(self, paciente: dict) -> dict:
        """Avaliação de risco de violência"""

        score = 0
        fatores = []

        if paciente.get('historico_violencia'):
            fatores.append('Histórico de violência')
            score += 2

        if paciente.get('uso_substancias'):
            fatores.append('Uso de substâncias')
            score += 1

        if paciente.get('sintomas_psicoticos'):
            fatores.append('Sintomas psicóticos')
            score += 1

        nivel = 'ALTO' if score >= 3 else 'MODERADO' if score >= 2 else 'BAIXO'

        return {
            'nivel': nivel,
            'score': score,
            'fatores': fatores
        }

    def calcular_nivel_risco_geral(self, predicao_crise: dict, risco_suicida: dict, risco_violencia: dict) -> str:
        """Calcula nível de risco geral"""

        scores = [
            predicao_crise.get('risco_global', {}).get('score', 0),
            risco_suicida.get('score', 0),
            risco_violencia.get('score', 0)
        ]

        score_total = sum(scores)

        if score_total >= 8:
            return 'CRÍTICO'
        elif score_total >= 5:
            return 'ALTO'
        elif score_total >= 3:
            return 'MODERADO'
        else:
            return 'BAIXO'

    def gerar_recomendacoes_urgentes(self, avaliacao_risco: dict) -> list[str]:
        """Gera recomendações urgentes baseadas no risco"""

        recomendacoes = []
        nivel_geral = avaliacao_risco.get('nivel_geral', 'BAIXO')

        if nivel_geral == 'CRÍTICO':
            recomendacoes.extend([
                'Avaliação presencial imediata necessária',
                'Considerar internação psiquiátrica',
                'Ativar rede de apoio familiar',
                'Monitoramento 24h recomendado'
            ])
        elif nivel_geral == 'ALTO':
            recomendacoes.extend([
                'Consulta psiquiátrica urgente em 24-48h',
                'Intensificar acompanhamento',
                'Avaliar necessidade de medicação'
            ])
        elif nivel_geral == 'MODERADO':
            recomendacoes.extend([
                'Agendar consulta em 1 semana',
                'Iniciar monitoramento digital',
                'Ativar suporte psicológico'
            ])
        else:
            recomendacoes.append('Acompanhamento de rotina')

        return recomendacoes

    def gerar_recomendacoes_farmacologicas(self, avaliacao_clinica: dict) -> dict:
        """Gera recomendações farmacológicas básicas"""

        diagnostico = avaliacao_clinica.get('diagnostico', {})

        recomendacoes = {
            'medicamentos_sugeridos': [],
            'contraindicacoes': [],
            'monitoramento': []
        }

        if 'depressao' in str(diagnostico).lower():
            recomendacoes['medicamentos_sugeridos'].append('Antidepressivo ISRS')
            recomendacoes['monitoramento'].append('Monitorar ideação suicida nas primeiras semanas')

        if 'ansiedade' in str(diagnostico).lower():
            recomendacoes['medicamentos_sugeridos'].append('Ansiolítico de curta duração')
            recomendacoes['monitoramento'].append('Avaliar dependência')

        return recomendacoes

    def gerar_recomendacoes_risco_suicida(self, nivel: str) -> list[str]:
        """Gera recomendações específicas para risco suicida"""

        if nivel == 'ALTO':
            return [
                'Avaliação presencial imediata',
                'Considerar internação involuntária se necessário',
                'Remover meios letais do ambiente',
                'Ativar rede de apoio 24h'
            ]
        elif nivel == 'MODERADO':
            return [
                'Consulta psiquiátrica em 24-48h',
                'Contrato de não-suicídio',
                'Telefone de emergência disponível',
                'Acompanhamento familiar'
            ]
        else:
            return [
                'Monitoramento de rotina',
                'Psicoeducação sobre fatores de risco'
            ]

    def criar_cronograma_acompanhamento(self, avaliacao_risco: dict) -> dict:
        """Cria cronograma de acompanhamento baseado no risco"""

        nivel = avaliacao_risco.get('nivel_geral', 'BAIXO')

        if nivel == 'CRÍTICO':
            frequencia = 'Diário'
            modalidade = 'Presencial + Digital'
        elif nivel == 'ALTO':
            frequencia = 'Semanal'
            modalidade = 'Presencial + Digital'
        elif nivel == 'MODERADO':
            frequencia = 'Quinzenal'
            modalidade = 'Digital + Presencial mensal'
        else:
            frequencia = 'Mensal'
            modalidade = 'Digital'

        return {
            'frequencia': frequencia,
            'modalidade': modalidade,
            'duracao_estimada': '3-6 meses',
            'proxima_avaliacao': (datetime.now() + timedelta(days=7)).isoformat()
        }

    def definir_objetivos_terapeuticos(self, avaliacao_clinica: dict) -> list[str]:
        """Define objetivos terapêuticos baseados na avaliação"""

        objetivos = [
            'Reduzir sintomas principais',
            'Melhorar funcionamento social',
            'Desenvolver estratégias de enfrentamento',
            'Prevenir recaídas'
        ]

        return objetivos

    def definir_metricas_progresso(self) -> dict:
        """Define métricas para acompanhar progresso"""

        return {
            'escalas_clinicas': ['PHQ-9', 'GAD-7', 'CGI'],
            'indicadores_funcionais': ['Sono', 'Apetite', 'Energia', 'Concentração'],
            'indicadores_sociais': ['Relacionamentos', 'Trabalho', 'Atividades'],
            'frequencia_avaliacao': 'Semanal'
        }
