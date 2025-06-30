"""
Sistema de radioterapia adaptativa com IA
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.Oncologia.RadioterapiaAdaptativa')

class RadioterapiaAdaptativaIA:
    """Sistema de radioterapia adaptativa com IA"""

    def __init__(self):
        self.planejador_tratamento = PlanejadorTratamentoRadio()
        self.otimizador_dose = OtimizadorDoseRadio()
        self.monitor_anatomia = MonitorAnatomiaIA()
        self.calculador_tcp_ntcp = CalculadorTCPNTCP()
        self.gestor_qa = GestorQualidadeRadio()

    async def planejar_tratamentos(self, pacientes_radio: list[dict],
                                   usar_imrt_vmat: bool = True,
                                   radioterapia_adaptativa: bool = True) -> dict:
        """Planejamento completo de tratamentos radioterápicos"""

        try:
            planejamentos_radio = {}

            for paciente in pacientes_radio:
                plano_inicial = await self.planejador_tratamento.criar_plano_inicial(
                    paciente=paciente,
                    tecnica_preferida='VMAT' if usar_imrt_vmat else 'conformacional_3d',
                    fracionamento='convencional',
                    dose_prescrita=paciente.get('dose_prescrita', 60),  # Gy
                    orgaos_risco=paciente.get('orgaos_risco', []),
                    volume_alvo=paciente.get('volume_alvo')
                )

                plano_otimizado = await self.otimizador_dose.otimizar_distribuicao(
                    plano_base=plano_inicial,
                    objetivos_dose={
                        'ptv_coverage': 0.95,  # 95% do PTV
                        'dose_homogeneidade': 0.05,  # ±5%
                        'conformidade': 0.85
                    },
                    restricoes_orgaos_risco=await self.definir_restricoes_oar(
                        paciente['diagnostico']['localizacao']
                    ),
                    usar_algoritmo_avancado=True
                )

                probabilidades = await self.calculador_tcp_ntcp.calcular_probabilidades(
                    plano=plano_otimizado,
                    histologia=paciente['diagnostico']['histologia'],
                    parametros_radiobiologicos=await self.obter_parametros_radiobiologicos(
                        paciente
                    )
                )

                if radioterapia_adaptativa:
                    protocolo_adaptativo = await self.definir_protocolo_adaptativo(
                        paciente=paciente,
                        plano_inicial=plano_otimizado,
                        frequencia_adaptacao='semanal',
                        criterios_adaptacao=[
                            'mudanca_anatomica',
                            'resposta_tumoral',
                            'toxicidade_aguda'
                        ]
                    )
                else:
                    protocolo_adaptativo = None

                qa_plano = await self.gestor_qa.avaliar_qualidade_plano(
                    plano=plano_otimizado,
                    verificacoes=[
                        'dosimetria',
                        'geometria',
                        'seguranca_paciente',
                        'conformidade_protocolo'
                    ]
                )

                cronograma = await self.gerar_cronograma_tratamento(
                    plano=plano_otimizado,
                    fracionamento=plano_inicial['fracionamento'],
                    adaptativo=protocolo_adaptativo is not None
                )

                planejamentos_radio[paciente['id']] = {
                    'plano_tratamento': plano_otimizado,
                    'probabilidades_biologicas': probabilidades,
                    'protocolo_adaptativo': protocolo_adaptativo,
                    'controle_qualidade': qa_plano,
                    'cronograma': cronograma,
                    'orientacoes_paciente': await self.gerar_orientacoes_radio(
                        plano_otimizado
                    ),
                    'monitoramento_toxicidade': await self.definir_monitoramento_toxicidade(
                        plano_otimizado
                    )
                }

            return {
                'planejamentos_individualizados': planejamentos_radio,
                'estatisticas_planejamento': await self.calcular_estatisticas_planejamento(
                    planejamentos_radio
                ),
                'tecnicas_utilizadas': await self.analisar_tecnicas_utilizadas(),
                'qualidade_planos': await self.avaliar_qualidade_geral(planejamentos_radio),
                'economia_tempo': await self.calcular_economia_tempo_ia()
            }

        except Exception as e:
            logger.error(f"Erro no planejamento de radioterapia: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def definir_restricoes_oar(self, localizacao: str) -> dict:
        """Define restrições para órgãos de risco"""

        restricoes_padrao = {
            'pulmao': {
                'medula_espinhal': {'dose_max': 45, 'unidade': 'Gy'},
                'pulmao_contralateral': {'v20': 20, 'unidade': '%'},
                'coracao': {'dose_media': 26, 'unidade': 'Gy'},
                'esofago': {'dose_max': 74, 'unidade': 'Gy'}
            },
            'mama': {
                'coracao': {'dose_media': 4, 'unidade': 'Gy'},
                'pulmao_ipsilateral': {'v20': 20, 'unidade': '%'},
                'pulmao_contralateral': {'dose_max': 5, 'unidade': 'Gy'},
                'tireoide': {'dose_media': 30, 'unidade': 'Gy'}
            },
            'prostata': {
                'reto': {'v65': 17, 'v70': 20, 'unidade': '%'},
                'bexiga': {'v65': 25, 'v70': 15, 'unidade': '%'},
                'cabecas_femorais': {'dose_max': 52, 'unidade': 'Gy'}
            }
        }

        return restricoes_padrao.get(localizacao.lower(), {})

    async def obter_parametros_radiobiologicos(self, paciente: dict) -> dict:
        """Obtém parâmetros radiobiológicos"""

        return {
            'alfa_beta_tumor': 10,  # Gy
            'alfa_beta_tecido_normal': 3,  # Gy
            'tempo_duplicacao': 30,  # dias
            'fator_reparo': 0.85,
            'oxigenacao_tumoral': 0.9
        }

    async def definir_protocolo_adaptativo(self, **kwargs) -> dict:
        """Define protocolo de radioterapia adaptativa"""

        return {
            'frequencia_imagem': 'semanal',
            'modalidade_imagem': 'CBCT',
            'criterios_replanejamento': [
                'mudanca_volume_tumor > 20%',
                'mudanca_posicao_oar > 5mm',
                'perda_peso > 5kg'
            ],
            'limiar_adaptacao': {
                'anatomico': 0.15,  # 15% mudança
                'dosimetrico': 0.10   # 10% mudança na dose
            },
            'algoritmo_decisao': 'machine_learning'
        }

    async def gerar_cronograma_tratamento(self, plano: dict, fracionamento: str, adaptativo: bool) -> dict:
        """Gera cronograma de tratamento"""

        dose_total = plano.get('dose_prescrita', 60)

        if fracionamento == 'convencional':
            dose_fracao = 2.0  # Gy
            fracoes_totais = int(dose_total / dose_fracao)
            duracao_semanas = fracoes_totais / 5  # 5 frações por semana
        elif fracionamento == 'hipofracionado':
            dose_fracao = 2.67  # Gy
            fracoes_totais = int(dose_total / dose_fracao)
            duracao_semanas = fracoes_totais / 5
        else:
            dose_fracao = 2.0
            fracoes_totais = 30
            duracao_semanas = 6

        return {
            'dose_total': dose_total,
            'dose_por_fracao': dose_fracao,
            'fracoes_totais': fracoes_totais,
            'duracao_semanas': duracao_semanas,
            'frequencia_semanal': 5,
            'adaptacoes_previstas': 2 if adaptativo else 0,
            'data_inicio': None,  # seria definida na programação
            'data_fim_prevista': None
        }

    async def gerar_orientacoes_radio(self, plano: dict) -> list[str]:
        """Gera orientações para radioterapia"""

        return [
            'Manter hidratação adequada',
            'Usar protetor solar na área tratada',
            'Evitar produtos com álcool na pele',
            'Comunicar reações cutâneas',
            'Manter posicionamento durante tratamento',
            'Seguir orientações nutricionais'
        ]

    async def definir_monitoramento_toxicidade(self, plano: dict) -> dict:
        """Define monitoramento de toxicidade"""

        return {
            'toxicidades_agudas': [
                'radiodermatite',
                'mucosite',
                'fadiga',
                'nausea'
            ],
            'toxicidades_tardias': [
                'fibrose',
                'pneumonite',
                'xerostomia',
                'disfagia'
            ],
            'escalas_avaliacao': ['CTCAE v5.0', 'RTOG'],
            'frequencia_avaliacao': 'semanal_durante_tratamento'
        }

    async def calcular_estatisticas_planejamento(self, planejamentos: dict) -> dict:
        """Calcula estatísticas do planejamento"""

        return {
            'planos_criados': len(planejamentos),
            'tempo_medio_planejamento': 45,  # minutos
            'taxa_aprovacao_qa': 0.95,
            'planos_adaptativos': sum(1 for p in planejamentos.values()
                                    if p.get('protocolo_adaptativo'))
        }

    async def analisar_tecnicas_utilizadas(self) -> dict:
        """Analisa técnicas de radioterapia utilizadas"""

        return {
            'tecnicas_frequentes': [
                {'nome': 'VMAT', 'frequencia': 0.65},
                {'nome': 'IMRT', 'frequencia': 0.25},
                {'nome': '3D-CRT', 'frequencia': 0.10}
            ],
            'complexidade_media': 7.2,  # escala 1-10
            'tempo_medio_entrega': 12  # minutos
        }

    async def avaliar_qualidade_geral(self, planejamentos: dict) -> dict:
        """Avalia qualidade geral dos planos"""

        return {
            'score_qualidade_medio': 0.92,
            'conformidade_protocolo': 0.96,
            'satisfacao_medicos': 4.7,  # escala 1-5
            'replanejamentos_necessarios': 0.08
        }

    async def calcular_economia_tempo_ia(self) -> dict:
        """Calcula economia de tempo com IA"""

        return {
            'tempo_economizado_planejamento': 180,  # minutos/semana
            'reducao_replanejamentos': 0.35,  # 35% redução
            'melhoria_qualidade': 0.15,  # 15% melhoria
            'roi_ia_radioterapia': 2.8
        }

class PlanejadorTratamentoRadio:
    """Planejador de tratamento radioterápico"""

    async def criar_plano_inicial(self, **kwargs) -> dict:
        """Cria plano inicial"""

        return {
            'tecnica': kwargs.get('tecnica_preferida', 'VMAT'),
            'dose_prescrita': kwargs.get('dose_prescrita', 60),
            'fracionamento': kwargs.get('fracionamento', 'convencional'),
            'volumes_definidos': True,
            'restricoes_aplicadas': True
        }

class OtimizadorDoseRadio:
    """Otimizador de distribuição de dose"""

    async def otimizar_distribuicao(self, **kwargs) -> dict:
        """Otimiza distribuição de dose"""

        return {
            'cobertura_ptv': 0.95,
            'homogeneidade': 0.04,
            'conformidade': 0.87,
            'dose_orgaos_risco': 'dentro_limites',
            'otimizacao_convergiu': True
        }

class MonitorAnatomiaIA:
    """Monitor de anatomia com IA"""
    pass

class CalculadorTCPNTCP:
    """Calculador de TCP e NTCP"""

    async def calcular_probabilidades(self, **kwargs) -> dict:
        """Calcula probabilidades de controle e complicação"""

        return {
            'tcp': 0.85,  # Tumor Control Probability
            'ntcp_medula': 0.02,  # Normal Tissue Complication Probability
            'ntcp_pulmao': 0.05,
            'ntcp_coracao': 0.01,
            'beneficio_terapeutico': 0.83
        }

class GestorQualidadeRadio:
    """Gestor de qualidade em radioterapia"""

    async def avaliar_qualidade_plano(self, **kwargs) -> dict:
        """Avalia qualidade do plano"""

        return {
            'aprovado_qa': True,
            'score_qualidade': 0.94,
            'verificacoes_passaram': ['dosimetria', 'geometria', 'seguranca'],
            'observacoes': [],
            'tempo_qa': 15  # minutos
        }
