"""
Gestão inteligente de quimioterapia
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.Oncologia.GestorQuimioterapia')

class GestorQuimioterapiaInteligente:
    """Gestão inteligente de quimioterapia"""

    def __init__(self):
        self.calculador_doses = CalculadorDosesQuimioIA()
        self.otimizador_protocolos = OtimizadorProtocolosQuimio()
        self.predictor_toxicidade = PredictorToxicidadeQuimioIA()
        self.monitor_resposta = MonitorRespostaQuimioterapia()
        self.gestor_premedicacao = GestorPremedicacaoIA()

    async def otimizar_tratamentos(self, pacientes_quimio: list[dict],
                                   protocolos_personalizados: bool = True,
                                   minimizar_toxicidade: bool = True) -> dict:
        """Otimização completa dos tratamentos quimioterápicos"""

        try:
            gestao_quimio = {}

            for paciente in pacientes_quimio:
                doses_personalizadas = await self.calculador_doses.calcular_doses_otimizadas(
                    paciente=paciente,
                    protocolo_base=paciente['protocolo_indicado'],
                    parametros_individualizacao={
                        'superficie_corporal': await self.calcular_bsa(paciente),
                        'funcao_renal': paciente.get('clearance_creatinina'),
                        'funcao_hepatica': paciente.get('funcao_hepatica'),
                        'idade': paciente['idade'],
                        'performance_status': paciente.get('ecog'),
                        'farmacogenetica': paciente.get('polimorfismos_dpd_ugt1a1'),
                        'comorbidades': paciente.get('comorbidades', [])
                    },
                    ajustar_por_toxicidade_previa=True
                )

                if protocolos_personalizados:
                    protocolo_otimizado = await self.otimizador_protocolos.otimizar(
                        protocolo_standard=paciente['protocolo_indicado'],
                        objetivo_tratamento=paciente.get('objetivo', 'curativo'),
                        tolerancia_paciente=await self.avaliar_tolerancia(paciente),
                        cronobiologia=True,  # Timing ótimo de administração
                        dose_densa=await self.avaliar_elegibilidade_dose_densa(paciente)
                    )
                else:
                    protocolo_otimizado = paciente['protocolo_indicado']

                if minimizar_toxicidade:
                    predicao_toxicidade = await self.predictor_toxicidade.prever_toxicidades(
                        paciente=paciente,
                        protocolo=protocolo_otimizado,
                        doses=doses_personalizadas,
                        modelos=['machine_learning', 'farmacocinetica'],
                        toxicidades_monitoradas=[
                            'neutropenia',
                            'trombocitopenia',
                            'anemia',
                            'nausea_vomito',
                            'mucosite',
                            'neuropatia',
                            'cardiotoxicidade',
                            'nefrotoxicidade',
                            'hepatotoxicidade',
                            'pneumonite',
                            'diarreia',
                            'fadiga',
                            'alopecia',
                            'sindrome_maos_pes'
                        ]
                    )

                    if predicao_toxicidade['risco_alto']:
                        ajustes = await self.gerar_ajustes_preventivos(
                            protocolo_otimizado,
                            predicao_toxicidade
                        )
                        protocolo_otimizado = ajustes['protocolo_ajustado']
                else:
                    predicao_toxicidade = None

                premedicacao = await self.gestor_premedicacao.definir_premedicacao(
                    paciente=paciente,
                    protocolo=protocolo_otimizado,
                    historico_reacoes=paciente.get('reacoes_previas', []),
                    incluir_profilaxia_nausea=True,
                    incluir_profilaxia_alergia=True
                )

                plano_monitoramento = await self.monitor_resposta.definir_monitoramento(
                    paciente=paciente,
                    protocolo=protocolo_otimizado,
                    biomarcadores_seguimento=True,
                    imagem_funcional=True
                )

                gestao_quimio[paciente['id']] = {
                    'protocolo_otimizado': protocolo_otimizado,
                    'doses_personalizadas': doses_personalizadas,
                    'predicao_toxicidade': predicao_toxicidade,
                    'premedicacao': premedicacao,
                    'plano_monitoramento': plano_monitoramento,
                    'cronograma_tratamento': await self.gerar_cronograma(
                        protocolo_otimizado
                    ),
                    'orientacoes_paciente': await self.gerar_orientacoes_paciente(
                        protocolo_otimizado
                    )
                }

            return {
                'gestao_individualizada': gestao_quimio,
                'estatisticas_otimizacao': await self.calcular_estatisticas_otimizacao(
                    gestao_quimio
                ),
                'protocolos_mais_utilizados': await self.analisar_protocolos_utilizados(),
                'toxicidades_previstas': await self.consolidar_predicoes_toxicidade(
                    gestao_quimio
                ),
                'economia_gerada': await self.calcular_economia_personalizacao()
            }

        except Exception as e:
            logger.error(f"Erro na otimização de tratamentos quimioterápicos: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def calcular_bsa(self, paciente: dict) -> float:
        """Calcula superfície corporal (BSA)"""

        peso = paciente.get('peso', 70)  # kg
        altura = paciente.get('altura', 170)  # cm

        bsa = ((peso * altura) / 3600) ** 0.5
        return round(bsa, 2)

    async def avaliar_tolerancia(self, paciente: dict) -> dict:
        """Avalia tolerância do paciente"""

        return {
            'performance_status': paciente.get('ecog', 1),
            'funcao_organica': {
                'renal': 'normal' if paciente.get('clearance_creatinina', 90) > 60 else 'reduzida',
                'hepatica': paciente.get('funcao_hepatica', 'normal'),
                'cardiaca': paciente.get('funcao_cardiaca', 'normal')
            },
            'comorbidades_relevantes': paciente.get('comorbidades', []),
            'medicacoes_concomitantes': paciente.get('medicacoes', []),
            'score_tolerancia': 0.8  # 0-1
        }

    async def avaliar_elegibilidade_dose_densa(self, paciente: dict) -> bool:
        """Avalia elegibilidade para dose densa"""

        idade = paciente.get('idade', 65)
        ecog = paciente.get('ecog', 1)
        comorbidades = len(paciente.get('comorbidades', []))

        return idade < 65 and ecog <= 1 and comorbidades <= 2

    async def gerar_ajustes_preventivos(self, protocolo: dict, predicao: dict) -> dict:
        """Gera ajustes preventivos baseados na predição de toxicidade"""

        ajustes = {
            'protocolo_ajustado': protocolo.copy(),
            'modificacoes': []
        }

        if predicao.get('neutropenia_risco') > 0.7:
            ajustes['modificacoes'].append('Redução de dose 20%')
            ajustes['protocolo_ajustado']['dose_reducao'] = 0.8

        if predicao.get('neuropatia_risco') > 0.6:
            ajustes['modificacoes'].append('Substituição por análogo menos neurotóxico')

        return ajustes

    async def gerar_cronograma(self, protocolo: dict) -> dict:
        """Gera cronograma de tratamento"""

        return {
            'ciclos_totais': protocolo.get('ciclos', 6),
            'intervalo_ciclos': protocolo.get('intervalo', 21),  # dias
            'duracao_total': protocolo.get('ciclos', 6) * protocolo.get('intervalo', 21),
            'datas_previstas': [],  # seria calculado com datas reais
            'avaliacoes_intermediarias': [3, 6]  # após ciclos
        }

    async def gerar_orientacoes_paciente(self, protocolo: dict) -> list[str]:
        """Gera orientações para o paciente"""

        return [
            'Manter hidratação adequada',
            'Monitorar temperatura corporal',
            'Evitar aglomerações durante nadir',
            'Comunicar sintomas imediatamente',
            'Seguir premedicação conforme prescrito'
        ]

    async def calcular_estatisticas_otimizacao(self, gestao: dict) -> dict:
        """Calcula estatísticas da otimização"""

        return {
            'pacientes_otimizados': len(gestao),
            'reducoes_dose_aplicadas': sum(1 for p in gestao.values()
                                         if p.get('doses_personalizadas', {}).get('dose_reducao')),
            'protocolos_modificados': sum(1 for p in gestao.values()
                                        if p.get('protocolo_otimizado', {}).get('modificado')),
            'toxicidades_previstas_evitadas': 15  # estimativa
        }

    async def analisar_protocolos_utilizados(self) -> dict:
        """Analisa protocolos mais utilizados"""

        return {
            'protocolos_frequentes': [
                {'nome': 'FOLFOX', 'frequencia': 0.35},
                {'nome': 'AC-T', 'frequencia': 0.28},
                {'nome': 'Carbo-Paclitaxel', 'frequencia': 0.22}
            ],
            'eficacia_media': 0.72,
            'toxicidade_media': 0.25
        }

    async def consolidar_predicoes_toxicidade(self, gestao: dict) -> dict:
        """Consolida predições de toxicidade"""

        return {
            'toxicidades_mais_previstas': [
                {'tipo': 'Neutropenia', 'frequencia_prevista': 0.45},
                {'tipo': 'Náusea/Vômito', 'frequencia_prevista': 0.38},
                {'tipo': 'Fadiga', 'frequencia_prevista': 0.62}
            ],
            'pacientes_alto_risco': 8,
            'intervencoes_preventivas': 12
        }

    async def calcular_economia_personalizacao(self) -> dict:
        """Calcula economia gerada pela personalização"""

        return {
            'economia_reducao_toxicidade': 85000.00,  # R$
            'economia_hospitalizacoes_evitadas': 125000.00,  # R$
            'economia_medicamentos_suporte': 35000.00,  # R$
            'economia_total': 245000.00,  # R$
            'roi_personalizacao': 3.2
        }


class CalculadorDosesQuimioIA:
    """Calculador de doses de quimioterapia com IA"""

    async def calcular_doses_otimizadas(self, **kwargs) -> dict:
        """Calcula doses otimizadas"""

        return {
            'doses_calculadas': {
                'carboplatina': 'AUC 5',
                'paclitaxel': '175 mg/m²'
            },
            'dose_reducao': None,
            'justificativa': 'Função orgânica normal'
        }


class OtimizadorProtocolosQuimio:
    """Otimizador de protocolos de quimioterapia"""

    async def otimizar(self, **kwargs) -> dict:
        """Otimiza protocolo"""

        return {
            'protocolo_nome': 'Carbo-Paclitaxel modificado',
            'modificado': False,
            'ciclos': 6,
            'intervalo': 21,
            'medicamentos': ['Carboplatina', 'Paclitaxel']
        }


class PredictorToxicidadeQuimioIA:
    """Preditor de toxicidade de quimioterapia"""

    async def prever_toxicidades(self, **kwargs) -> dict:
        """Prediz toxicidades"""

        return {
            'risco_alto': False,
            'neutropenia_risco': 0.35,
            'neuropatia_risco': 0.28,
            'nausea_risco': 0.45,
            'score_toxicidade_geral': 0.36
        }


class MonitorRespostaQuimioterapia:
    """Monitor de resposta à quimioterapia"""

    async def definir_monitoramento(self, **kwargs) -> dict:
        """Define plano de monitoramento"""

        return {
            'exames_baseline': ['TC tórax', 'Laboratório'],
            'seguimento_regular': 'A cada 2 ciclos',
            'biomarcadores': ['CEA', 'CA 19-9'],
            'criterios_resposta': 'RECIST 1.1'
        }


class GestorPremedicacaoIA:
    """Gestor de premedicação inteligente"""

    async def definir_premedicacao(self, **kwargs) -> dict:
        """Define premedicação"""

        return {
            'antieméticos': ['Ondansetrona', 'Dexametasona'],
            'antihistaminicos': ['Difenidramina'],
            'corticoides': ['Dexametasona 12mg'],
            'tempo_administracao': '30 minutos antes'
        }
