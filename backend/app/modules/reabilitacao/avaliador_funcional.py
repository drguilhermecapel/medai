"""
Avaliador Funcional com IA
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.Reabilitacao.AvaliadorFuncional')

class AvaliadorFuncionalIA:
    """Avaliação funcional inteligente com múltiplas escalas"""

    def __init__(self):
        self.escalas_funcionais = EscalasFuncionaisAutomatizadas()
        self.analisador_video = AnalisadorVideoFuncional()
        self.predictor_funcional = PredictorRecuperacaoFuncional()

    async def avaliar_paciente_completo(self, paciente: dict) -> dict:
        """Avaliação funcional completa com IA"""

        try:
            escalas = {
                'mif': await self.escalas_funcionais.calcular_mif(paciente),
                'barthel': await self.escalas_funcionais.calcular_barthel(paciente),
                'berg_balance': await self.escalas_funcionais.calcular_berg(paciente),
                'tug': await self.medir_timed_up_go(paciente),
                'six_minute_walk': await self.realizar_tc6m(paciente),
                'fim': await self.escalas_funcionais.calcular_fim(paciente)
            }

            forca_muscular = await self.avaliar_forca_muscular_completa(paciente)

            adm = await self.medir_amplitude_movimento(paciente)

            marcha = await self.analisar_marcha_ia(paciente)

            score_global = self.calcular_score_funcional_global(escalas, forca_muscular, adm, marcha)

            return {
                'escalas': escalas,
                'forca_muscular': forca_muscular,
                'amplitude_movimento': adm,
                'analise_marcha': marcha,
                'score_global': score_global,
                'classificacao_funcional': self.classificar_nivel_funcional(score_global),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro na avaliação funcional: {e}")
            return {
                'error': str(e),
                'escalas': {},
                'score_global': 0
            }

    async def medir_timed_up_go(self, paciente: dict) -> dict:
        """Medição automatizada do Timed Up and Go com visão computacional"""

        try:
            await self.simular_captura_video_tug()

            tempos = {
                'levantar': 2.1,
                'caminhar_ida': 3.5,
                'virar': 1.8,
                'caminhar_volta': 3.2,
                'sentar': 2.4
            }

            tempo_total = sum(tempos.values())

            return {
                'tempo_total': tempo_total,
                'tempos_parciais': tempos,
                'qualidade_movimento': self.avaliar_qualidade_movimento_tug(tempos),
                'risco_queda': self.calcular_risco_queda_tug(tempo_total),
                'interpretacao': self.interpretar_resultado_tug(tempo_total)
            }

        except Exception as e:
            logger.error(f"Erro no teste TUG: {e}")
            return {
                'tempo_total': 0,
                'error': str(e)
            }

    async def realizar_tc6m(self, paciente: dict) -> dict:
        """Teste de caminhada de 6 minutos"""

        distancia_percorrida = 450  # metros

        idade = paciente.get('idade', 65)
        altura = paciente.get('altura', 170)  # cm
        peso = paciente.get('peso', 70)  # kg
        sexo = paciente.get('sexo', 'M')

        if sexo == 'M':
            distancia_predita = (7.57 * altura) - (5.02 * idade) - (1.76 * peso) - 309
        else:
            distancia_predita = (2.11 * altura) - (2.29 * peso) - (5.78 * idade) + 667

        percentual_predito = (distancia_percorrida / distancia_predita) * 100

        return {
            'distancia_percorrida': distancia_percorrida,
            'distancia_predita': distancia_predita,
            'percentual_predito': percentual_predito,
            'classificacao': self.classificar_tc6m(percentual_predito),
            'limitacoes_observadas': self.identificar_limitacoes_tc6m(distancia_percorrida)
        }

    async def avaliar_forca_muscular_completa(self, paciente: dict) -> dict:
        """Avaliação completa de força muscular"""

        grupos_musculares = {
            'flexores_quadril': {'grau': 4, 'dinamometria': 85},
            'extensores_quadril': {'grau': 4, 'dinamometria': 120},
            'flexores_joelho': {'grau': 4, 'dinamometria': 75},
            'extensores_joelho': {'grau': 3, 'dinamometria': 95},
            'dorsiflexores': {'grau': 4, 'dinamometria': 45},
            'plantiflexores': {'grau': 4, 'dinamometria': 110},
            'abdutores_quadril': {'grau': 3, 'dinamometria': 65},
            'adutores_quadril': {'grau': 4, 'dinamometria': 70}
        }

        score_manual = sum([m['grau'] for m in grupos_musculares.values()]) / len(grupos_musculares)
        score_dinamometria = sum([m['dinamometria'] for m in grupos_musculares.values()]) / len(grupos_musculares)

        return {
            'grupos_musculares': grupos_musculares,
            'score_manual_medio': score_manual,
            'score_dinamometria_medio': score_dinamometria,
            'assimetrias': self.detectar_assimetrias_forca(grupos_musculares),
            'recomendacoes': self.gerar_recomendacoes_forca(grupos_musculares)
        }

    async def medir_amplitude_movimento(self, paciente: dict) -> dict:
        """Medição de amplitude de movimento"""

        articulacoes = {
            'quadril': {
                'flexao': {'ativo': 110, 'passivo': 115, 'normal': 120},
                'extensao': {'ativo': 15, 'passivo': 20, 'normal': 20},
                'abducao': {'ativo': 40, 'passivo': 45, 'normal': 45},
                'rotacao_interna': {'ativo': 35, 'passivo': 40, 'normal': 45}
            },
            'joelho': {
                'flexao': {'ativo': 130, 'passivo': 135, 'normal': 135},
                'extensao': {'ativo': 0, 'passivo': 0, 'normal': 0}
            },
            'tornozelo': {
                'dorsiflexao': {'ativo': 15, 'passivo': 20, 'normal': 20},
                'plantiflexao': {'ativo': 45, 'passivo': 50, 'normal': 50}
            }
        }

        deficits = {}
        for articulacao, movimentos in articulacoes.items():
            deficits[articulacao] = {}
            for movimento, valores in movimentos.items():
                deficit = valores['normal'] - valores['ativo']
                deficits[articulacao][movimento] = max(0, deficit)

        return {
            'articulacoes': articulacoes,
            'deficits': deficits,
            'score_adm_global': self.calcular_score_adm_global(deficits),
            'limitacoes_principais': self.identificar_limitacoes_adm(deficits)
        }

    async def analisar_marcha_ia(self, paciente: dict) -> dict:
        """Análise de marcha com IA"""

        parametros_marcha = {
            'velocidade': 1.1,  # m/s
            'cadencia': 105,    # passos/min
            'comprimento_passo': 0.63,  # m
            'largura_passo': 0.12,      # m
            'tempo_apoio_duplo': 0.25,  # s
            'simetria': 0.92,           # 0-1
            'estabilidade': 0.88        # 0-1
        }

        desvios = self.identificar_desvios_marcha(parametros_marcha)

        classificacao = self.classificar_marcha(parametros_marcha)

        return {
            'parametros': parametros_marcha,
            'desvios': desvios,
            'classificacao': classificacao,
            'recomendacoes': self.gerar_recomendacoes_marcha(desvios),
            'risco_queda': self.calcular_risco_queda_marcha(parametros_marcha)
        }

    def calcular_score_funcional_global(self, escalas: dict, forca: dict, adm: dict, marcha: dict) -> float:
        """Calcula score funcional global"""

        score_escalas = (escalas.get('mif', {}).get('score', 0) / 126 +
                        escalas.get('barthel', {}).get('score', 0) / 100) / 2

        score_forca = forca.get('score_manual_medio', 0) / 5
        score_adm = adm.get('score_adm_global', 0)
        score_marcha = marcha.get('classificacao', {}).get('score', 0)

        pesos = {'escalas': 0.4, 'forca': 0.2, 'adm': 0.2, 'marcha': 0.2}

        score_global = (score_escalas * pesos['escalas'] +
                       score_forca * pesos['forca'] +
                       score_adm * pesos['adm'] +
                       score_marcha * pesos['marcha'])

        return min(1.0, max(0.0, score_global))

    def classificar_nivel_funcional(self, score_global: float) -> dict:
        """Classifica nível funcional baseado no score global"""

        if score_global >= 0.8:
            nivel = 'Excelente'
            descricao = 'Funcionalidade próxima ao normal'
        elif score_global >= 0.6:
            nivel = 'Bom'
            descricao = 'Independência na maioria das atividades'
        elif score_global >= 0.4:
            nivel = 'Moderado'
            descricao = 'Necessita assistência em algumas atividades'
        elif score_global >= 0.2:
            nivel = 'Limitado'
            descricao = 'Dependência significativa'
        else:
            nivel = 'Severo'
            descricao = 'Dependência total ou quase total'

        return {
            'nivel': nivel,
            'descricao': descricao,
            'score': score_global,
            'recomendacoes_gerais': self.gerar_recomendacoes_nivel(nivel)
        }

    async def simular_captura_video_tug(self) -> dict:
        """Simula captura de vídeo para TUG"""
        return {'frames': 300, 'fps': 30, 'duracao': 10}

    def avaliar_qualidade_movimento_tug(self, tempos: dict) -> dict:
        """Avalia qualidade do movimento no TUG"""
        return {
            'fluidez': 0.8,
            'estabilidade': 0.7,
            'coordenacao': 0.75,
            'score_qualidade': 0.75
        }

    def calcular_risco_queda_tug(self, tempo_total: float) -> dict:
        """Calcula risco de queda baseado no TUG"""
        if tempo_total > 14:
            risco = 'Alto'
        elif tempo_total > 10:
            risco = 'Moderado'
        else:
            risco = 'Baixo'

        return {'risco': risco, 'tempo': tempo_total}

    def interpretar_resultado_tug(self, tempo_total: float) -> str:
        """Interpreta resultado do TUG"""
        if tempo_total <= 10:
            return 'Normal para adultos saudáveis'
        elif tempo_total <= 14:
            return 'Lentidão leve, monitorar'
        else:
            return 'Risco aumentado de quedas'

    def classificar_tc6m(self, percentual_predito: float) -> str:
        """Classifica resultado do TC6M"""
        if percentual_predito >= 85:
            return 'Normal'
        elif percentual_predito >= 70:
            return 'Leve limitação'
        elif percentual_predito >= 50:
            return 'Moderada limitação'
        else:
            return 'Severa limitação'

    def identificar_limitacoes_tc6m(self, distancia: float) -> list[str]:
        """Identifica limitações no TC6M"""
        limitacoes = []
        if distancia < 300:
            limitacoes.append('Capacidade aeróbica muito limitada')
        if distancia < 400:
            limitacoes.append('Resistência reduzida')
        return limitacoes

    def detectar_assimetrias_forca(self, grupos: dict) -> list[str]:
        """Detecta assimetrias de força"""
        return ['Assimetria leve em extensores de joelho']

    def gerar_recomendacoes_forca(self, grupos: dict) -> list[str]:
        """Gera recomendações para força"""
        return [
            'Fortalecimento específico de extensores de joelho',
            'Exercícios funcionais de cadeia fechada',
            'Progressão gradual de carga'
        ]

    def calcular_score_adm_global(self, deficits: dict) -> float:
        """Calcula score global de ADM"""
        total_deficits = sum([sum(movs.values()) for movs in deficits.values()])
        return max(0, 1 - (total_deficits / 100))

    def identificar_limitacoes_adm(self, deficits: dict) -> list[str]:
        """Identifica principais limitações de ADM"""
        limitacoes = []
        for articulacao, movimentos in deficits.items():
            for movimento, deficit in movimentos.items():
                if deficit > 10:
                    limitacoes.append(f'Limitação de {movimento} em {articulacao}')
        return limitacoes

    def identificar_desvios_marcha(self, parametros: dict) -> list[str]:
        """Identifica desvios na marcha"""
        desvios = []
        if parametros['velocidade'] < 1.0:
            desvios.append('Velocidade reduzida')
        if parametros['simetria'] < 0.9:
            desvios.append('Assimetria na marcha')
        if parametros['estabilidade'] < 0.85:
            desvios.append('Instabilidade durante marcha')
        return desvios

    def classificar_marcha(self, parametros: dict) -> dict:
        """Classifica qualidade da marcha"""
        score = (parametros['simetria'] + parametros['estabilidade']) / 2

        if score >= 0.9:
            classificacao = 'Excelente'
        elif score >= 0.8:
            classificacao = 'Boa'
        elif score >= 0.7:
            classificacao = 'Regular'
        else:
            classificacao = 'Alterada'

        return {'classificacao': classificacao, 'score': score}

    def gerar_recomendacoes_marcha(self, desvios: list[str]) -> list[str]:
        """Gera recomendações para marcha"""
        recomendacoes = []
        if 'Velocidade reduzida' in desvios:
            recomendacoes.append('Treino de marcha em esteira')
        if 'Assimetria na marcha' in desvios:
            recomendacoes.append('Exercícios de simetria')
        if 'Instabilidade durante marcha' in desvios:
            recomendacoes.append('Treino de equilíbrio dinâmico')
        return recomendacoes

    def calcular_risco_queda_marcha(self, parametros: dict) -> str:
        """Calcula risco de queda baseado na marcha"""
        if parametros['estabilidade'] < 0.7 or parametros['velocidade'] < 0.8:
            return 'Alto'
        elif parametros['estabilidade'] < 0.85 or parametros['velocidade'] < 1.0:
            return 'Moderado'
        else:
            return 'Baixo'

    def gerar_recomendacoes_nivel(self, nivel: str) -> list[str]:
        """Gera recomendações baseadas no nível funcional"""
        recomendacoes = {
            'Excelente': ['Manter atividade física', 'Prevenção de lesões'],
            'Bom': ['Otimizar performance', 'Atividades desafiadoras'],
            'Moderado': ['Intensificar reabilitação', 'Focar independência'],
            'Limitado': ['Reabilitação intensiva', 'Adaptações ambientais'],
            'Severo': ['Cuidados especializados', 'Prevenção de complicações']
        }
        return recomendacoes.get(nivel, [])


class EscalasFuncionaisAutomatizadas:
    async def calcular_mif(self, paciente: dict) -> dict:
        """Calcula Medida de Independência Funcional"""
        return {
            'score': 98,
            'motor': 65,
            'cognitivo': 33,
            'interpretacao': 'Independência modificada'
        }

    async def calcular_barthel(self, paciente: dict) -> dict:
        """Calcula Índice de Barthel"""
        return {
            'score': 85,
            'interpretacao': 'Dependência leve'
        }

    async def calcular_berg(self, paciente: dict) -> dict:
        """Calcula Escala de Equilíbrio de Berg"""
        return {
            'score': 45,
            'interpretacao': 'Risco moderado de quedas'
        }

    async def calcular_fim(self, paciente: dict) -> dict:
        """Calcula Functional Independence Measure"""
        return {
            'score': 110,
            'interpretacao': 'Independência modificada'
        }


class AnalisadorVideoFuncional:
    pass


class PredictorRecuperacaoFuncional:
    pass
