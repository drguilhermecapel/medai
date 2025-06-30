"""
Sistema de Reabilitação Robótica
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.Reabilitacao.RobotReabilitacao')

class RobotReabilitacao:
    """Sistema de reabilitação assistida por robô"""

    def __init__(self):
        self.controlador_robo = ControladorRoboTerapeutico()
        self.sensor_forca = SensorForcaTorque()
        self.adaptador_impedancia = AdaptadorImpedanciaIA()

    async def sessao_robotica_assistida(self, paciente: dict, exercicio: dict) -> dict:
        """Sessão de reabilitação com assistência robótica"""

        try:
            calibracao = await self.calibrar_sistema_paciente(
                antropometria=paciente.get('medidas', {}),
                limitacoes_movimento=paciente.get('limitacoes', []),
                nivel_assistencia=self.calcular_nivel_assistencia_inicial(paciente)
            )

            resultado_sessao = []
            repeticoes = exercicio.get('repeticoes', 10)

            for repeticao in range(repeticoes):
                dados_sensores = await self.coletar_dados_sensores()

                impedancia = self.adaptador_impedancia.ajustar(
                    forca_paciente=dados_sensores['forca'],
                    posicao_atual=dados_sensores['posicao'],
                    velocidade=dados_sensores['velocidade'],
                    objetivo_movimento=exercicio.get('trajetoria', {})
                )

                assistencia = await self.controlador_robo.aplicar_assistencia(
                    impedancia=impedancia,
                    modo=exercicio.get('modo_assistencia', 'assist_as_needed')
                )

                resultado_sessao.append({
                    'repeticao': repeticao + 1,
                    'qualidade': self.avaliar_qualidade_movimento(dados_sensores),
                    'assistencia_fornecida': assistencia,
                    'fadiga_estimada': self.estimar_fadiga(dados_sensores),
                    'timestamp': datetime.now().isoformat()
                })

            return {
                'calibracao': calibracao,
                'resultados': resultado_sessao,
                'evolucao_sessao': self.analisar_evolucao_sessao(resultado_sessao),
                'recomendacoes': self.gerar_recomendacoes_proxima_sessao(resultado_sessao),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro na sessão robótica: {e}")
            return {
                'error': str(e),
                'calibracao': {},
                'resultados': []
            }

    async def calibrar_sistema_paciente(self, antropometria: dict, limitacoes_movimento: list, nivel_assistencia: float) -> dict:
        """Calibra sistema robótico para o paciente específico"""

        calibracao = {
            'parametros_antropometricos': {
                'altura': antropometria.get('altura', 170),
                'peso': antropometria.get('peso', 70),
                'comprimento_bracos': antropometria.get('comprimento_bracos', 60),
                'comprimento_pernas': antropometria.get('comprimento_pernas', 90)
            },
            'limitacoes_identificadas': limitacoes_movimento,
            'nivel_assistencia_inicial': nivel_assistencia,
            'configuracao_seguranca': {
                'forca_maxima': self.calcular_forca_maxima_segura(antropometria),
                'amplitude_permitida': self.calcular_amplitude_segura(limitacoes_movimento),
                'velocidade_maxima': self.calcular_velocidade_segura(nivel_assistencia)
            },
            'status_calibracao': 'completa',
            'timestamp': datetime.now().isoformat()
        }

        return calibracao

    def calcular_nivel_assistencia_inicial(self, paciente: dict) -> float:
        """Calcula nível inicial de assistência robótica"""

        score_funcional = paciente.get('score_funcional', 0.5)
        forca_muscular = paciente.get('forca_muscular_media', 0.5)
        controle_motor = paciente.get('controle_motor', 0.5)

        nivel_assistencia = 1.0 - ((score_funcional + forca_muscular + controle_motor) / 3)

        if 'hemiplegia' in paciente.get('diagnostico', '').lower():
            nivel_assistencia = max(nivel_assistencia, 0.7)
        elif 'paraplegia' in paciente.get('diagnostico', '').lower():
            nivel_assistencia = max(nivel_assistencia, 0.8)

        return min(1.0, max(0.1, nivel_assistencia))

    async def coletar_dados_sensores(self) -> dict:
        """Coleta dados dos sensores do robô"""

        return {
            'forca': {
                'x': 15.2,  # N
                'y': 8.7,
                'z': 22.1,
                'magnitude': 28.5
            },
            'posicao': {
                'x': 0.25,  # m
                'y': 0.15,
                'z': 0.30,
                'angulo_articular': 45  # graus
            },
            'velocidade': {
                'linear': 0.12,  # m/s
                'angular': 15    # graus/s
            },
            'aceleracao': {
                'linear': 0.05,  # m/s²
                'angular': 8     # graus/s²
            },
            'timestamp': datetime.now().isoformat()
        }

    def avaliar_qualidade_movimento(self, dados_sensores: dict) -> dict:
        """Avalia qualidade do movimento baseado nos sensores"""

        forca = dados_sensores.get('forca', {})
        velocidade = dados_sensores.get('velocidade', {})

        suavidade = 1.0 - min(1.0, dados_sensores.get('aceleracao', {}).get('linear', 0) / 0.1)
        consistencia_forca = 1.0 - abs(forca.get('magnitude', 0) - 25) / 25
        velocidade_adequada = 1.0 - abs(velocidade.get('linear', 0) - 0.1) / 0.1

        score_qualidade = (suavidade + consistencia_forca + velocidade_adequada) / 3

        return {
            'score_qualidade': max(0, min(1, score_qualidade)),
            'suavidade': suavidade,
            'consistencia_forca': consistencia_forca,
            'velocidade_adequada': velocidade_adequada,
            'classificacao': self.classificar_qualidade(score_qualidade)
        }

    def classificar_qualidade(self, score: float) -> str:
        """Classifica qualidade do movimento"""

        if score >= 0.8:
            return 'Excelente'
        elif score >= 0.6:
            return 'Boa'
        elif score >= 0.4:
            return 'Regular'
        else:
            return 'Necessita melhoria'

    def estimar_fadiga(self, dados_sensores: dict) -> dict:
        """Estima nível de fadiga baseado nos sensores"""

        reducao_forca = max(0, (30 - dados_sensores.get('forca', {}).get('magnitude', 25)) / 30)
        reducao_velocidade = max(0, (0.15 - dados_sensores.get('velocidade', {}).get('linear', 0.12)) / 0.15)
        aumento_tremor = min(1, dados_sensores.get('aceleracao', {}).get('linear', 0) / 0.2)

        nivel_fadiga = (reducao_forca + reducao_velocidade + aumento_tremor) / 3

        return {
            'nivel_fadiga': nivel_fadiga,
            'indicadores': {
                'reducao_forca': reducao_forca,
                'reducao_velocidade': reducao_velocidade,
                'aumento_tremor': aumento_tremor
            },
            'classificacao': self.classificar_fadiga(nivel_fadiga),
            'recomendacao': self.recomendar_acao_fadiga(nivel_fadiga)
        }

    def classificar_fadiga(self, nivel: float) -> str:
        """Classifica nível de fadiga"""

        if nivel < 0.3:
            return 'Baixa'
        elif nivel < 0.6:
            return 'Moderada'
        else:
            return 'Alta'

    def recomendar_acao_fadiga(self, nivel: float) -> str:
        """Recomenda ação baseada no nível de fadiga"""

        if nivel < 0.3:
            return 'Continuar exercício'
        elif nivel < 0.6:
            return 'Reduzir intensidade'
        else:
            return 'Pausa necessária'

    def analisar_evolucao_sessao(self, resultado_sessao: list[dict]) -> dict:
        """Analisa evolução durante a sessão"""

        if not resultado_sessao:
            return {}

        qualidades = [r['qualidade']['score_qualidade'] for r in resultado_sessao]
        assistencias = [r['assistencia_fornecida']['nivel'] for r in resultado_sessao]
        fadigas = [r['fadiga_estimada']['nivel_fadiga'] for r in resultado_sessao]

        return {
            'qualidade_inicial': qualidades[0] if qualidades else 0,
            'qualidade_final': qualidades[-1] if qualidades else 0,
            'melhoria_qualidade': qualidades[-1] - qualidades[0] if len(qualidades) > 1 else 0,
            'assistencia_inicial': assistencias[0] if assistencias else 0,
            'assistencia_final': assistencias[-1] if assistencias else 0,
            'reducao_assistencia': assistencias[0] - assistencias[-1] if len(assistencias) > 1 else 0,
            'fadiga_progressiva': fadigas[-1] - fadigas[0] if len(fadigas) > 1 else 0,
            'tendencia_geral': self.determinar_tendencia(qualidades, assistencias, fadigas)
        }

    def determinar_tendencia(self, qualidades: list[float], assistencias: list[float], fadigas: list[float]) -> str:
        """Determina tendência geral da sessão"""

        if not qualidades:
            return 'Indeterminada'

        melhoria_qualidade = qualidades[-1] > qualidades[0] if len(qualidades) > 1 else False
        reducao_assistencia = assistencias[-1] < assistencias[0] if len(assistencias) > 1 else False
        fadiga_controlada = fadigas[-1] < 0.7 if fadigas else True

        if melhoria_qualidade and reducao_assistencia and fadiga_controlada:
            return 'Excelente progresso'
        elif melhoria_qualidade and fadiga_controlada:
            return 'Bom progresso'
        elif fadiga_controlada:
            return 'Progresso moderado'
        else:
            return 'Necessita ajustes'

    def gerar_recomendacoes_proxima_sessao(self, resultado_sessao: list[dict]) -> list[dict]:
        """Gera recomendações para próxima sessão"""

        recomendacoes = []

        if not resultado_sessao:
            return recomendacoes

        evolucao = self.analisar_evolucao_sessao(resultado_sessao)

        if evolucao.get('melhoria_qualidade', 0) > 0.1:
            recomendacoes.append({
                'categoria': 'Progressão',
                'recomendacao': 'Reduzir nível de assistência em 10%',
                'justificativa': 'Melhoria significativa na qualidade do movimento'
            })

        if evolucao.get('fadiga_progressiva', 0) > 0.3:
            recomendacoes.append({
                'categoria': 'Carga',
                'recomendacao': 'Reduzir número de repetições ou aumentar pausas',
                'justificativa': 'Fadiga excessiva detectada'
            })

        if evolucao.get('reducao_assistencia', 0) < 0:
            recomendacoes.append({
                'categoria': 'Assistência',
                'recomendacao': 'Manter ou aumentar nível de assistência',
                'justificativa': 'Paciente necessitou mais assistência durante sessão'
            })

        tendencia = evolucao.get('tendencia_geral', '')
        if 'Excelente' in tendencia:
            recomendacoes.append({
                'categoria': 'Geral',
                'recomendacao': 'Considerar progressão para exercícios mais complexos',
                'justificativa': 'Desempenho excepcional na sessão'
            })
        elif 'Necessita ajustes' in tendencia:
            recomendacoes.append({
                'categoria': 'Geral',
                'recomendacao': 'Revisar parâmetros de exercício e calibração',
                'justificativa': 'Desempenho abaixo do esperado'
            })

        return recomendacoes

    def calcular_forca_maxima_segura(self, antropometria: dict) -> float:
        """Calcula força máxima segura baseada na antropometria"""

        peso = antropometria.get('peso', 70)
        return peso * 0.3  # 30% do peso corporal

    def calcular_amplitude_segura(self, limitacoes: list[str]) -> dict:
        """Calcula amplitude de movimento segura"""

        amplitude_base = {
            'flexao': 90,
            'extensao': 45,
            'abducao': 60,
            'rotacao': 30
        }

        for limitacao in limitacoes:
            if 'rigidez' in limitacao.lower():
                for movimento in amplitude_base:
                    amplitude_base[movimento] *= 0.8
            elif 'dor' in limitacao.lower():
                for movimento in amplitude_base:
                    amplitude_base[movimento] *= 0.7

        return amplitude_base

    def calcular_velocidade_segura(self, nivel_assistencia: float) -> float:
        """Calcula velocidade máxima segura"""

        velocidade_base = 0.2  # m/s
        return velocidade_base * (1 - nivel_assistencia * 0.5)

class ControladorRoboTerapeutico:
    async def aplicar_assistencia(self, impedancia: dict, modo: str) -> dict:
        """Aplica assistência robótica"""

        return {
            'modo_assistencia': modo,
            'nivel': impedancia.get('nivel_assistencia', 0.5),
            'forca_aplicada': {
                'x': 5.2,
                'y': 3.1,
                'z': 7.8
            },
            'tipo_controle': 'impedancia_adaptativa',
            'timestamp': datetime.now().isoformat()
        }

class SensorForcaTorque:
    pass

class AdaptadorImpedanciaIA:
    def ajustar(self, forca_paciente: dict, posicao_atual: dict, velocidade: dict, objetivo_movimento: dict) -> dict:
        """Ajusta impedância baseado na performance do paciente"""

        forca_magnitude = forca_paciente.get('magnitude', 20)
        velocidade_atual = velocidade.get('linear', 0.1)

        if forca_magnitude < 15:
            nivel_assistencia = 0.8  # Alta assistência
        elif forca_magnitude > 30:
            nivel_assistencia = 0.3  # Baixa assistência
        else:
            nivel_assistencia = 0.5  # Assistência moderada

        return {
            'nivel_assistencia': nivel_assistencia,
            'rigidez': 100 * (1 - nivel_assistencia),  # N/m
            'amortecimento': 20 * (1 - nivel_assistencia),  # Ns/m
            'modo_controle': 'assist_as_needed',
            'parametros_ajustados': {
                'forca_referencia': forca_magnitude,
                'velocidade_referencia': velocidade_atual
            }
        }
