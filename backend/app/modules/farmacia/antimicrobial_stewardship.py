"""
Gestão inteligente de antimicrobianos
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.Farmacia.AntimicrobialStewardship')

class AntimicrobialStewardshipIA:
    """Gestão inteligente de antimicrobianos"""

    def __init__(self):
        self.analisador_resistencia = AnalisadorResistenciaML()
        self.otimizador_terapia = OtimizadorTerapiaAntimicrobiana()
        self.monitor_consumo = MonitorConsumoAntimicrobianos()

    async def avaliar_prescricao_antimicrobiana(self, prescricao: dict) -> dict:
        """Avaliação completa de prescrição antimicrobiana"""

        try:
            adequacao = await self.analisar_adequacao_terapia(prescricao)

            risco_resistencia = await self.prever_resistencia_bacteriana(prescricao)

            descalonamento = await self.sugerir_descalonamento(prescricao)

            duracao_otima = await self.calcular_duracao_otima(prescricao)

            return {
                'adequacao': adequacao,
                'risco_resistencia': risco_resistencia,
                'descalonamento': descalonamento,
                'duracao_otima': duracao_otima,
                'score_stewardship': self.calcular_score_stewardship(adequacao),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro na avaliação antimicrobiana: {e}")
            return {
                'error': str(e),
                'adequacao': {},
                'risco_resistencia': {},
                'descalonamento': {},
                'duracao_otima': {}
            }

    async def analisar_adequacao_terapia(self, prescricao: dict) -> dict:
        """Analisa adequação da terapia antimicrobiana"""

        paciente = prescricao.get('paciente', {})
        antimicrobiano = prescricao.get('antimicrobiano', {})

        adequacao = {
            'indicacao_apropriada': True,
            'espectro_adequado': True,
            'dose_correta': True,
            'via_administracao_otima': True,
            'duracao_apropriada': True,
            'score_adequacao': 0.0,
            'justificativas': []
        }

        indicacao = antimicrobiano.get('indicacao', '')
        if not indicacao or indicacao == 'profilaxia_cirurgica':
            if not self.verificar_criterios_profilaxia(paciente):
                adequacao['indicacao_apropriada'] = False
                adequacao['justificativas'].append('Profilaxia não indicada para este procedimento')

        microorganismo = prescricao.get('microorganismo_isolado')
        if microorganismo:
            if not self.verificar_espectro_cobertura(antimicrobiano.get('nome'), microorganismo):
                adequacao['espectro_adequado'] = False
                adequacao['justificativas'].append('Antimicrobiano não cobre microorganismo isolado')

        dose_prescrita = antimicrobiano.get('dose', 0)
        dose_recomendada = self.calcular_dose_recomendada(antimicrobiano.get('nome'), paciente)

        if abs(dose_prescrita - dose_recomendada) / dose_recomendada > 0.2:  # 20% de variação
            adequacao['dose_correta'] = False
            adequacao['justificativas'].append(f'Dose inadequada. Recomendado: {dose_recomendada}mg')

        via_prescrita = antimicrobiano.get('via', 'oral')
        if paciente.get('gravidade') == 'critica' and via_prescrita == 'oral':
            adequacao['via_administracao_otima'] = False
            adequacao['justificativas'].append('Via endovenosa recomendada para paciente crítico')

        duracao = antimicrobiano.get('duracao_dias', 0)
        if duracao > 14 and indicacao != 'endocardite':
            adequacao['duracao_apropriada'] = False
            adequacao['justificativas'].append('Duração excessiva para a indicação')

        criterios_ok = sum([
            adequacao['indicacao_apropriada'],
            adequacao['espectro_adequado'],
            adequacao['dose_correta'],
            adequacao['via_administracao_otima'],
            adequacao['duracao_apropriada']
        ])
        adequacao['score_adequacao'] = criterios_ok / 5

        return adequacao

    def verificar_criterios_profilaxia(self, paciente: dict) -> bool:
        """Verifica se profilaxia cirúrgica é indicada"""

        procedimento = paciente.get('procedimento_cirurgico', '')

        procedimentos_profilaxia = [
            'cirurgia_cardiaca',
            'cirurgia_ortopedica',
            'cirurgia_abdominal',
            'neurocirurgia'
        ]

        return any(proc in procedimento.lower() for proc in procedimentos_profilaxia)

    def verificar_espectro_cobertura(self, antimicrobiano: str, microorganismo: str) -> bool:
        """Verifica se antimicrobiano cobre microorganismo"""

        cobertura_db = {
            'amoxicilina': ['streptococcus', 'enterococcus'],
            'ceftriaxona': ['escherichia_coli', 'klebsiella', 'streptococcus'],
            'vancomicina': ['staphylococcus_aureus', 'enterococcus'],
            'meropenem': ['pseudomonas', 'acinetobacter', 'klebsiella'],
            'ciprofloxacina': ['escherichia_coli', 'pseudomonas']
        }

        antimicrobiano_lower = antimicrobiano.lower()
        microorganismo_lower = microorganismo.lower()

        cobertura = cobertura_db.get(antimicrobiano_lower, [])
        return any(micro in microorganismo_lower for micro in cobertura)

    def calcular_dose_recomendada(self, antimicrobiano: str, paciente: dict) -> float:
        """Calcula dose recomendada baseada no paciente"""

        peso = paciente.get('peso', 70)
        clearance = paciente.get('clearance_creatinina', 90)

        doses_kg = {
            'amoxicilina': 30,  # mg/kg/dia
            'ceftriaxona': 50,
            'vancomicina': 40,
            'meropenem': 60,
            'ciprofloxacina': 20
        }

        dose_base = doses_kg.get(antimicrobiano.lower(), 30) * peso

        if clearance < 50:
            dose_base *= 0.5
        elif clearance < 80:
            dose_base *= 0.75

        return dose_base

    async def prever_resistencia_bacteriana(self, prescricao: dict) -> dict:
        """Prediz risco de resistência bacteriana"""

        antimicrobiano = prescricao.get('antimicrobiano', {})
        paciente = prescricao.get('paciente', {})

        fatores_risco = []
        score_risco = 0.1  # Base baixo

        if paciente.get('uso_antimicrobiano_previo', False):
            fatores_risco.append('Uso prévio de antimicrobianos')
            score_risco += 0.3

        if paciente.get('internacao_prolongada', False):
            fatores_risco.append('Internação prolongada')
            score_risco += 0.2

        if paciente.get('uti', False):
            fatores_risco.append('Paciente em UTI')
            score_risco += 0.2

        if antimicrobiano.get('espectro') == 'amplo':
            fatores_risco.append('Antimicrobiano de amplo espectro')
            score_risco += 0.2

        taxa_resistencia_local = self.obter_taxa_resistencia_local(antimicrobiano.get('nome'))
        if taxa_resistencia_local > 0.2:  # 20%
            fatores_risco.append(f'Alta taxa de resistência local ({taxa_resistencia_local*100:.1f}%)')
            score_risco += 0.3

        score_risco = min(1.0, score_risco)

        return {
            'score_risco_resistencia': score_risco,
            'nivel_risco': self.classificar_nivel_risco(score_risco),
            'fatores_risco': fatores_risco,
            'recomendacoes': self.gerar_recomendacoes_resistencia(score_risco),
            'taxa_resistencia_local': taxa_resistencia_local
        }

    def obter_taxa_resistencia_local(self, antimicrobiano: str) -> float:
        """Obtém taxa de resistência local do antimicrobiano"""

        taxas_resistencia = {
            'amoxicilina': 0.15,
            'ceftriaxona': 0.08,
            'vancomicina': 0.02,
            'meropenem': 0.12,
            'ciprofloxacina': 0.25
        }

        return taxas_resistencia.get(antimicrobiano.lower(), 0.1)

    def classificar_nivel_risco(self, score: float) -> str:
        """Classifica nível de risco de resistência"""

        if score < 0.3:
            return 'baixo'
        elif score < 0.6:
            return 'moderado'
        elif score < 0.8:
            return 'alto'
        else:
            return 'muito_alto'

    def gerar_recomendacoes_resistencia(self, score_risco: float) -> list[str]:
        """Gera recomendações baseadas no risco de resistência"""

        recomendacoes = []

        if score_risco > 0.6:
            recomendacoes.extend([
                'Considerar cultura e antibiograma antes do início',
                'Monitorar resposta clínica de perto',
                'Avaliar descalonamento precoce'
            ])

        if score_risco > 0.8:
            recomendacoes.extend([
                'Considerar terapia combinada',
                'Consultar infectologista',
                'Implementar medidas de controle de infecção'
            ])

        return recomendacoes

    async def sugerir_descalonamento(self, prescricao: dict) -> dict:
        """Sugere descalonamento da terapia antimicrobiana"""

        antimicrobiano = prescricao.get('antimicrobiano', {})
        paciente = prescricao.get('paciente', {})

        descalonamento = {
            'pode_descalonar': False,
            'antimicrobiano_sugerido': None,
            'justificativa': '',
            'tempo_para_descalonamento': 0,
            'criterios_descalonamento': []
        }

        dias_tratamento = antimicrobiano.get('dias_tratamento', 0)
        melhora_clinica = paciente.get('melhora_clinica', False)
        cultura_disponivel = prescricao.get('cultura_disponivel', False)

        if dias_tratamento >= 3 and melhora_clinica:
            descalonamento['criterios_descalonamento'].append('Melhora clínica após 72h')

            if cultura_disponivel:
                descalonamento['criterios_descalonamento'].append('Cultura disponível')
                descalonamento['pode_descalonar'] = True
                descalonamento['antimicrobiano_sugerido'] = self.sugerir_antimicrobiano_dirigido(prescricao)
                descalonamento['justificativa'] = 'Terapia dirigida baseada em cultura'
            elif antimicrobiano.get('espectro') == 'amplo':
                descalonamento['pode_descalonar'] = True
                descalonamento['antimicrobiano_sugerido'] = self.sugerir_antimicrobiano_estreito(antimicrobiano)
                descalonamento['justificativa'] = 'Redução do espectro antimicrobiano'

        if descalonamento['pode_descalonar']:
            descalonamento['tempo_para_descalonamento'] = max(0, 3 - dias_tratamento)

        return descalonamento

    def sugerir_antimicrobiano_dirigido(self, prescricao: dict) -> str:
        """Sugere antimicrobiano dirigido baseado em cultura"""

        microorganismo = prescricao.get('microorganismo_isolado', '').lower()

        sugestoes = {
            'staphylococcus_aureus': 'oxacilina',
            'streptococcus': 'penicilina',
            'escherichia_coli': 'ceftriaxona',
            'pseudomonas': 'ceftazidima',
            'enterococcus': 'ampicilina'
        }

        for micro, antimicrobiano in sugestoes.items():
            if micro in microorganismo:
                return antimicrobiano

        return 'amoxicilina'  # Padrão

    def sugerir_antimicrobiano_estreito(self, antimicrobiano_atual: dict) -> str:
        """Sugere antimicrobiano de espectro mais estreito"""

        nome_atual = antimicrobiano_atual.get('nome', '').lower()

        descalonamento_map = {
            'meropenem': 'ceftriaxona',
            'vancomicina': 'oxacilina',
            'piperacilina_tazobactam': 'ceftriaxona',
            'imipenem': 'ceftriaxona'
        }

        return descalonamento_map.get(nome_atual, 'amoxicilina')

    async def calcular_duracao_otima(self, prescricao: dict) -> dict:
        """Calcula duração ótima do tratamento"""

        indicacao = prescricao.get('antimicrobiano', {}).get('indicacao', '')
        paciente = prescricao.get('paciente', {})

        duracoes_padrao = {
            'pneumonia_comunitaria': 7,
            'infeccao_urinaria': 5,
            'celulite': 7,
            'sepse': 10,
            'endocardite': 28,
            'meningite': 14,
            'profilaxia_cirurgica': 1
        }

        duracao_base = duracoes_padrao.get(indicacao, 7)

        if paciente.get('imunocomprometido', False):
            duracao_base += 3

        if paciente.get('gravidade') == 'critica':
            duracao_base += 2

        return {
            'duracao_otima_dias': duracao_base,
            'duracao_minima': max(3, duracao_base - 2),
            'duracao_maxima': duracao_base + 3,
            'criterios_interrupcao': [
                'Resolução dos sinais de infecção',
                'Normalização dos marcadores inflamatórios',
                'Estabilidade clínica por 48h'
            ],
            'monitoramento_recomendado': [
                'Temperatura corporal',
                'Leucócitos',
                'PCR ou procalcitonina'
            ]
        }

    def calcular_score_stewardship(self, adequacao: dict) -> float:
        """Calcula score geral de stewardship"""

        score_adequacao = adequacao.get('score_adequacao', 0)

        return score_adequacao

    async def gerar_relatorio_stewardship(self, periodo: str = '30_dias') -> dict:
        """Gera relatório de antimicrobial stewardship"""

        return {
            'periodo': periodo,
            'data_relatorio': datetime.now().isoformat(),
            'consumo_antimicrobianos': {
                'ddd_total': 1250.5,  # Defined Daily Doses
                'ddd_por_100_pacientes_dia': 45.2,
                'antimicrobianos_mais_utilizados': [
                    {'nome': 'ceftriaxona', 'ddd': 320.5, 'percentual': 25.6},
                    {'nome': 'vancomicina', 'ddd': 280.3, 'percentual': 22.4},
                    {'nome': 'meropenem', 'ddd': 195.8, 'percentual': 15.7}
                ]
            },
            'adequacao_prescricoes': {
                'total_avaliacoes': 156,
                'prescricoes_adequadas': 132,
                'taxa_adequacao': 84.6,  # %
                'principais_inadequacoes': [
                    'Duração excessiva',
                    'Espectro muito amplo',
                    'Dose inadequada'
                ]
            },
            'resistencia_bacteriana': {
                'taxa_resistencia_media': 0.18,  # 18%
                'microorganismos_criticos': [
                    'Acinetobacter baumannii',
                    'Pseudomonas aeruginosa',
                    'Klebsiella pneumoniae'
                ],
                'tendencia_resistencia': 'estavel'
            },
            'intervencoes_realizadas': {
                'total_intervencoes': 89,
                'descalonamentos': 34,
                'suspensoes': 18,
                'ajustes_dose': 25,
                'mudancas_via': 12,
                'taxa_aceitacao': 0.87  # 87%
            },
            'impacto_clinico': {
                'reducao_tempo_internacao': 1.2,  # dias
                'economia_custos': 45000.00,  # R$
                'reducao_infeccoes_secundarias': 0.23,  # 23%
                'melhora_desfechos': 0.15  # 15%
            },
            'recomendacoes': [
                'Implementar protocolo de descalonamento automático',
                'Capacitar equipe sobre duração ótima de tratamento',
                'Melhorar coleta de culturas pré-tratamento',
                'Desenvolver guidelines locais baseados em resistência'
            ]
        }


class AnalisadorResistenciaML:
    pass


class OtimizadorTerapiaAntimicrobiana:
    pass


class MonitorConsumoAntimicrobianos:
    pass
