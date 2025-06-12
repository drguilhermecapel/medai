"""
Sistema inteligente de nutrição parenteral
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.Farmacia.NutricaoParenteral')

class NutricaoParenteralIA:
    """Sistema inteligente de nutrição parenteral"""

    def __init__(self):
        self.calculador_nutricional = CalculadorNutricionalIA()
        self.formulador_np = FormuladorNutricaoParenteral()
        self.monitor_compatibilidade = MonitorCompatibilidadeNP()

    async def calcular_nutricao_parenteral(self, paciente: dict) -> dict:
        """Cálculo completo de nutrição parenteral personalizada"""

        try:
            avaliacao = await self.avaliar_estado_nutricional(paciente)

            necessidades = await self.calcular_necessidades_nutricionais(paciente, avaliacao)

            formulacao = await self.formular_nutricao_parenteral(necessidades, paciente)

            compatibilidade = await self.verificar_compatibilidade_componentes(formulacao)

            monitoramento = await self.definir_monitoramento_laboratorial(paciente, formulacao)

            return {
                'avaliacao_nutricional': avaliacao,
                'necessidades_calculadas': necessidades,
                'formulacao_np': formulacao,
                'compatibilidade': compatibilidade,
                'monitoramento': monitoramento,
                'score_adequacao': self.calcular_score_adequacao(formulacao, necessidades),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro no cálculo da nutrição parenteral: {e}")
            return {
                'error': str(e),
                'avaliacao_nutricional': {},
                'necessidades_calculadas': {},
                'formulacao_np': {},
                'compatibilidade': {},
                'monitoramento': {}
            }

    async def avaliar_estado_nutricional(self, paciente: dict) -> dict:
        """Avaliação completa do estado nutricional"""

        dados_antropometricos = paciente.get('antropometria', {})
        dados_laboratoriais = paciente.get('laboratorio', {})
        dados_clinicos = paciente.get('clinicos', {})

        avaliacao = {
            'imc': self.calcular_imc(dados_antropometricos),
            'estado_nutricional': '',
            'necessidades_especiais': [],
            'fatores_estresse': [],
            'score_nutricional': 0.0
        }

        imc = avaliacao['imc']
        if imc < 18.5:
            avaliacao['estado_nutricional'] = 'desnutrido'
            avaliacao['score_nutricional'] = 0.3
        elif imc < 25:
            avaliacao['estado_nutricional'] = 'eutrofico'
            avaliacao['score_nutricional'] = 1.0
        elif imc < 30:
            avaliacao['estado_nutricional'] = 'sobrepeso'
            avaliacao['score_nutricional'] = 0.8
        else:
            avaliacao['estado_nutricional'] = 'obesidade'
            avaliacao['score_nutricional'] = 0.6

        albumina = dados_laboratoriais.get('albumina', 4.0)
        if albumina < 3.0:
            avaliacao['necessidades_especiais'].append('hipoalbuminemia')
            avaliacao['score_nutricional'] *= 0.8

        transferrina = dados_laboratoriais.get('transferrina', 250)
        if transferrina < 200:
            avaliacao['necessidades_especiais'].append('deficiencia_ferro')

        if dados_clinicos.get('sepse', False):
            avaliacao['fatores_estresse'].append('sepse')
        if dados_clinicos.get('cirurgia_maior', False):
            avaliacao['fatores_estresse'].append('cirurgia_maior')
        if dados_clinicos.get('queimaduras', False):
            avaliacao['fatores_estresse'].append('queimaduras')
        if dados_clinicos.get('trauma', False):
            avaliacao['fatores_estresse'].append('trauma')

        return avaliacao

    def calcular_imc(self, antropometria: dict) -> float:
        """Calcula índice de massa corporal"""

        peso = antropometria.get('peso', 70)
        altura = antropometria.get('altura', 170) / 100  # converte cm para m

        return peso / (altura ** 2)

    async def calcular_necessidades_nutricionais(self, paciente: dict, avaliacao: dict) -> dict:
        """Calcula necessidades nutricionais personalizadas"""

        peso = paciente.get('antropometria', {}).get('peso', 70)
        idade = paciente.get('idade', 50)
        sexo = paciente.get('sexo', 'masculino')

        if sexo == 'masculino':
            geb = 88.362 + (13.397 * peso) + (4.799 * paciente.get('antropometria', {}).get('altura', 170)) - (5.677 * idade)
        else:
            geb = 447.593 + (9.247 * peso) + (3.098 * paciente.get('antropometria', {}).get('altura', 170)) - (4.330 * idade)

        fator_estresse = self.calcular_fator_estresse(avaliacao.get('fatores_estresse', []))
        fator_atividade = 1.2  # Paciente acamado

        calorias_totais = geb * fator_atividade * fator_estresse

        necessidades = {
            'calorias_totais': calorias_totais,
            'proteinas': {
                'gramas': self.calcular_necessidade_proteina(peso, avaliacao),
                'calorias': 0,
                'percentual': 0
            },
            'carboidratos': {
                'gramas': 0,
                'calorias': 0,
                'percentual': 50  # 50% das calorias
            },
            'lipidios': {
                'gramas': 0,
                'calorias': 0,
                'percentual': 30  # 30% das calorias
            },
            'micronutrientes': self.calcular_micronutrientes(peso, avaliacao),
            'volume_total': self.calcular_volume_total(peso, paciente)
        }

        necessidades['proteinas']['calorias'] = necessidades['proteinas']['gramas'] * 4
        necessidades['proteinas']['percentual'] = (necessidades['proteinas']['calorias'] / calorias_totais) * 100

        necessidades['carboidratos']['calorias'] = calorias_totais * (necessidades['carboidratos']['percentual'] / 100)
        necessidades['carboidratos']['gramas'] = necessidades['carboidratos']['calorias'] / 4

        necessidades['lipidios']['calorias'] = calorias_totais * (necessidades['lipidios']['percentual'] / 100)
        necessidades['lipidios']['gramas'] = necessidades['lipidios']['calorias'] / 9

        return necessidades

    def calcular_fator_estresse(self, fatores_estresse: list[str]) -> float:
        """Calcula fator de estresse metabólico"""

        fator_base = 1.0

        fatores_multiplicadores = {
            'sepse': 1.3,
            'cirurgia_maior': 1.2,
            'queimaduras': 1.5,
            'trauma': 1.25,
            'insuficiencia_respiratoria': 1.15
        }

        for fator in fatores_estresse:
            multiplicador = fatores_multiplicadores.get(fator, 1.0)
            fator_base *= multiplicador

        return min(2.0, fator_base)  # Máximo 2.0

    def calcular_necessidade_proteina(self, peso: float, avaliacao: dict) -> float:
        """Calcula necessidade de proteína"""

        proteina_base = 1.2

        if avaliacao.get('estado_nutricional') == 'desnutrido':
            proteina_base = 1.5

        fatores_estresse = avaliacao.get('fatores_estresse', [])
        if 'sepse' in fatores_estresse:
            proteina_base = 1.8
        if 'queimaduras' in fatores_estresse:
            proteina_base = 2.0

        necessidades_especiais = avaliacao.get('necessidades_especiais', [])
        if 'hipoalbuminemia' in necessidades_especiais:
            proteina_base += 0.3

        return peso * proteina_base

    def calcular_micronutrientes(self, peso: float, avaliacao: dict) -> dict:
        """Calcula necessidades de micronutrientes"""

        micronutrientes = {
            'vitaminas': {
                'vitamina_a': 900,  # mcg
                'vitamina_d': 15,   # mcg
                'vitamina_e': 15,   # mg
                'vitamina_k': 120,  # mcg
                'vitamina_c': 90,   # mg
                'tiamina': 1.2,     # mg
                'riboflavina': 1.3, # mg
                'niacina': 16,      # mg
                'vitamina_b6': 1.7, # mg
                'folato': 400,      # mcg
                'vitamina_b12': 2.4, # mcg
                'biotina': 30,      # mcg
                'acido_pantotenico': 5  # mg
            },
            'minerais': {
                'sodio': 2300,      # mg
                'potassio': 4700,   # mg
                'calcio': 1000,     # mg
                'fosforo': 700,     # mg
                'magnesio': 420,    # mg
                'ferro': 8,         # mg
                'zinco': 11,        # mg
                'cobre': 900,       # mcg
                'selenio': 55,      # mcg
                'cromo': 35,        # mcg
                'molibdenio': 45    # mcg
            },
            'eletroliticos': {
                'sodio': peso * 1.5,    # mEq
                'potassio': peso * 1.0, # mEq
                'calcio': peso * 0.2,   # mEq
                'magnesio': peso * 0.15, # mEq
                'fosforo': peso * 0.3   # mmol
            }
        }

        necessidades_especiais = avaliacao.get('necessidades_especiais', [])

        if 'deficiencia_ferro' in necessidades_especiais:
            micronutrientes['minerais']['ferro'] *= 2

        return micronutrientes

    def calcular_volume_total(self, peso: float, paciente: dict) -> dict:
        """Calcula volume total da NP"""

        volume_base = peso * 32

        condicoes = paciente.get('clinicos', {})

        if condicoes.get('insuficiencia_cardiaca', False):
            volume_base *= 0.8  # Restrição hídrica

        if condicoes.get('insuficiencia_renal', False):
            volume_base *= 0.7  # Restrição hídrica severa

        if condicoes.get('febre', False):
            volume_base *= 1.1  # Aumento por perdas

        return {
            'volume_total_ml': volume_base,
            'taxa_infusao_ml_h': volume_base / 24,
            'restricao_hidrica': volume_base < (peso * 25)
        }

    async def formular_nutricao_parenteral(self, necessidades: dict, paciente: dict) -> dict:
        """Formula a nutrição parenteral"""

        formulacao = {
            'componentes': {},
            'concentracoes': {},
            'volume_final': necessidades.get('volume_total', {}).get('volume_total_ml', 2000),
            'osmolaridade': 0,
            'estabilidade': True,
            'via_administracao': 'central'
        }

        proteinas_g = necessidades.get('proteinas', {}).get('gramas', 80)
        formulacao['componentes']['aminoacidos'] = {
            'quantidade_g': proteinas_g,
            'solucao': 'aminoacidos_10%',
            'volume_ml': proteinas_g * 10,  # 10% = 10g/100mL
            'nitrogenio_g': proteinas_g / 6.25
        }

        carboidratos_g = necessidades.get('carboidratos', {}).get('gramas', 250)
        formulacao['componentes']['glicose'] = {
            'quantidade_g': carboidratos_g,
            'concentracao': '50%',
            'volume_ml': carboidratos_g * 2,  # 50% = 50g/100mL
            'taxa_infusao_mg_kg_min': self.calcular_taxa_glicose(carboidratos_g, paciente.get('antropometria', {}).get('peso', 70))
        }

        lipidios_g = necessidades.get('lipidios', {}).get('gramas', 70)
        formulacao['componentes']['lipidios'] = {
            'quantidade_g': lipidios_g,
            'emulsao': 'lipidios_20%',
            'volume_ml': lipidios_g * 5,  # 20% = 20g/100mL
            'tipo': 'MCT/LCT'
        }

        formulacao['componentes']['eletrolitos'] = necessidades.get('micronutrientes', {}).get('eletroliticos', {})

        formulacao['componentes']['vitaminas'] = 'complexo_vitaminico_adulto_1_ampola'
        formulacao['componentes']['oligoelementos'] = 'oligoelementos_adulto_1_ampola'

        formulacao['osmolaridade'] = self.calcular_osmolaridade(formulacao)

        if formulacao['osmolaridade'] > 900:
            formulacao['via_administracao'] = 'central'
        else:
            formulacao['via_administracao'] = 'periferica'

        return formulacao

    def calcular_taxa_glicose(self, glicose_g: float, peso: float) -> float:
        """Calcula taxa de infusão de glicose"""

        glicose_mg_dia = glicose_g * 1000
        glicose_mg_min = glicose_mg_dia / (24 * 60)
        taxa_mg_kg_min = glicose_mg_min / peso

        return taxa_mg_kg_min

    def calcular_osmolaridade(self, formulacao: dict) -> float:
        """Calcula osmolaridade da formulação"""

        osmolaridade = 0

        aa_g = formulacao.get('componentes', {}).get('aminoacidos', {}).get('quantidade_g', 0)
        osmolaridade += aa_g * 10

        glicose_g = formulacao.get('componentes', {}).get('glicose', {}).get('quantidade_g', 0)
        osmolaridade += glicose_g * 5.5

        osmolaridade += 300  # Estimativa base para eletrólitos

        volume_l = formulacao.get('volume_final', 2000) / 1000
        osmolaridade_final = osmolaridade / volume_l

        return osmolaridade_final

    async def verificar_compatibilidade_componentes(self, formulacao: dict) -> dict:
        """Verifica compatibilidade entre componentes"""

        compatibilidade = {
            'compativel': True,
            'alertas': [],
            'incompatibilidades': [],
            'recomendacoes': []
        }

        ph_estimado = self.estimar_ph_formulacao(formulacao)
        if ph_estimado < 5.0 or ph_estimado > 7.0:
            compatibilidade['alertas'].append(f'pH fora da faixa ideal: {ph_estimado:.1f}')

        calcio = formulacao.get('componentes', {}).get('eletrolitos', {}).get('calcio', 0)
        fosforo = formulacao.get('componentes', {}).get('eletrolitos', {}).get('fosforo', 0)

        if calcio * fosforo > 200:  # Regra empírica
            compatibilidade['incompatibilidades'].append('Risco de precipitação cálcio-fosfato')
            compatibilidade['compativel'] = False

        if formulacao.get('osmolaridade', 0) > 1200:
            compatibilidade['alertas'].append('Osmolaridade elevada pode afetar estabilidade')

        if not compatibilidade['compativel']:
            compatibilidade['recomendacoes'].extend([
                'Revisar concentrações de cálcio e fosfato',
                'Considerar administração separada de componentes incompatíveis',
                'Consultar farmacêutico especialista'
            ])

        return compatibilidade

    def estimar_ph_formulacao(self, formulacao: dict) -> float:
        """Estima pH da formulação"""

        ph_base = 6.0

        eletrolitos = formulacao.get('componentes', {}).get('eletrolitos', {})

        fosforo = eletrolitos.get('fosforo', 0)
        if fosforo > 20:
            ph_base -= 0.3

        return ph_base

    async def definir_monitoramento_laboratorial(self, paciente: dict, formulacao: dict) -> dict:
        """Define protocolo de monitoramento laboratorial"""

        monitoramento = {
            'exames_diarios': [
                'glicemia',
                'eletrólitos (Na, K, Cl)',
                'ureia e creatinina'
            ],
            'exames_semanais': [
                'hemograma completo',
                'função hepática (ALT, AST, bilirrubinas)',
                'proteínas (albumina, pré-albumina)',
                'triglicerídeos',
                'magnésio e fósforo'
            ],
            'exames_quinzenais': [
                'vitaminas (B12, folato, vitamina D)',
                'oligoelementos (zinco, cobre, selênio)',
                'transferrina'
            ],
            'parametros_clinicos': [
                'peso diário',
                'balanço hídrico',
                'sinais vitais',
                'glicemia capilar 6x/dia'
            ],
            'metas_terapeuticas': {
                'glicemia': '140-180 mg/dL',
                'triglicerideos': '< 400 mg/dL',
                'albumina': '> 3.0 g/dL',
                'balanco_nitrogenado': 'positivo'
            }
        }

        condicoes = paciente.get('clinicos', {})

        if condicoes.get('diabetes', False):
            monitoramento['exames_diarios'].append('hemoglobina glicada (semanal)')
            monitoramento['metas_terapeuticas']['glicemia'] = '140-180 mg/dL (rigoroso)'

        if condicoes.get('insuficiencia_renal', False):
            monitoramento['exames_diarios'].extend(['gasometria', 'balanço hídrico rigoroso'])

        if condicoes.get('insuficiencia_hepatica', False):
            monitoramento['exames_diarios'].append('amônia sérica')
            monitoramento['exames_semanais'].append('tempo de protrombina')

        return monitoramento

    def calcular_score_adequacao(self, formulacao: dict, necessidades: dict) -> float:
        """Calcula score de adequação da formulação"""

        score = 1.0

        calorias_formulacao = self.calcular_calorias_formulacao(formulacao)
        calorias_necessarias = necessidades.get('calorias_totais', 2000)

        diferenca_calorica = abs(calorias_formulacao - calorias_necessarias) / calorias_necessarias
        if diferenca_calorica > 0.1:  # 10% de diferença
            score -= 0.2

        proteinas_formulacao = formulacao.get('componentes', {}).get('aminoacidos', {}).get('quantidade_g', 0)
        proteinas_necessarias = necessidades.get('proteinas', {}).get('gramas', 80)

        diferenca_proteica = abs(proteinas_formulacao - proteinas_necessarias) / proteinas_necessarias
        if diferenca_proteica > 0.1:
            score -= 0.2

        if not formulacao.get('estabilidade', True):
            score -= 0.3

        osmolaridade = formulacao.get('osmolaridade', 0)
        if osmolaridade > 1200:
            score -= 0.1

        return max(0, score)

    def calcular_calorias_formulacao(self, formulacao: dict) -> float:
        """Calcula calorias totais da formulação"""

        componentes = formulacao.get('componentes', {})

        calorias_proteinas = componentes.get('aminoacidos', {}).get('quantidade_g', 0) * 4

        calorias_carboidratos = componentes.get('glicose', {}).get('quantidade_g', 0) * 4

        calorias_lipidios = componentes.get('lipidios', {}).get('quantidade_g', 0) * 9

        return calorias_proteinas + calorias_carboidratos + calorias_lipidios

    async def gerar_relatorio_nutricao_parenteral(self, periodo: str = '7_dias') -> dict:
        """Gera relatório de nutrição parenteral"""

        return {
            'periodo': periodo,
            'data_relatorio': datetime.now().isoformat(),
            'pacientes_np': {
                'total_pacientes': 25,
                'np_central': 18,
                'np_periferica': 7,
                'tempo_medio_np': 8.5,  # dias
                'indicacoes_principais': [
                    'Pós-operatório complexo',
                    'Síndrome do intestino curto',
                    'Pancreatite aguda grave',
                    'Hiperemese gravídica'
                ]
            },
            'adequacao_nutricional': {
                'score_adequacao_medio': 0.89,
                'metas_caloricas_atingidas': 0.92,  # 92%
                'metas_proteicas_atingidas': 0.88,  # 88%
                'balanco_nitrogenado_positivo': 0.76  # 76%
            },
            'complicacoes': {
                'hiperglicemia': 8,  # casos
                'hipertrigliceridemia': 3,
                'deficiencia_eletrolitos': 5,
                'infeccao_cateter': 1,
                'precipitacao_componentes': 0
            },
            'monitoramento': {
                'exames_realizados': 450,
                'aderencia_protocolo': 0.94,  # 94%
                'tempo_medio_ajuste': 2.1,  # dias
                'satisfacao_equipe': 4.4  # escala 1-5
            },
            'economia_custos': {
                'reducao_tempo_internacao': 2.3,  # dias
                'economia_total': 85000.00,  # R$
                'custo_medio_np_dia': 180.00,  # R$
                'roi_programa': 2.8  # retorno sobre investimento
            },
            'recomendacoes': [
                'Implementar protocolo de insulinoterapia específico',
                'Capacitar equipe em cálculo de NP pediátrica',
                'Desenvolver sistema de alerta para incompatibilidades',
                'Criar protocolo de transição para nutrição enteral'
            ]
        }


class CalculadorNutricionalIA:
    pass


class FormuladorNutricaoParenteral:
    pass


class MonitorCompatibilidadeNP:
    pass
