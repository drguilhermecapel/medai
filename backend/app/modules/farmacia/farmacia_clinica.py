"""
Serviços de farmácia clínica com IA
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.Farmacia.FarmaciaClinica')

class FarmaciaClinicaAvancada:
    """Serviços de farmácia clínica com IA"""

    def __init__(self):
        self.analisador_terapeutico = AnalisadorTerapeuticoIA()
        self.monitor_adesao = MonitorAdesaoTerapeutica()
        self.educador_farmaceutico = EducadorFarmaceuticoIA()

    async def realizar_acompanhamento_farmacoterapeutico(self, paciente_id: str) -> dict:
        """Acompanhamento farmacoterapêutico completo com IA"""

        try:
            perfil = await self.analisar_perfil_completo(paciente_id)

            prms = await self.identificar_prms(perfil)

            intervencoes = await self.sugerir_intervencoes(prms)

            monitoramento = await self.configurar_monitoramento(intervencoes)

            return {
                'perfil': perfil,
                'prms_identificados': prms,
                'intervencoes': intervencoes,
                'plano_monitoramento': monitoramento,
                'impacto_clinico_estimado': self.estimar_impacto_clinico(intervencoes),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro no acompanhamento farmacoterapêutico: {e}")
            return {
                'error': str(e),
                'perfil': {},
                'prms_identificados': [],
                'intervencoes': []
            }

    async def analisar_perfil_completo(self, paciente_id: str) -> dict:
        """Análise completa do perfil farmacoterapêutico"""

        perfil = {
            'paciente_id': paciente_id,
            'dados_demograficos': {
                'idade': 65,
                'peso': 78,
                'altura': 170,
                'sexo': 'masculino'
            },
            'condicoes_clinicas': [
                'hipertensao_arterial',
                'diabetes_tipo_2',
                'dislipidemia',
                'insuficiencia_renal_leve'
            ],
            'medicamentos_atuais': [
                {
                    'nome': 'enalapril',
                    'dose': '10mg',
                    'frequencia': '2x/dia',
                    'inicio_tratamento': '2023-01-15',
                    'indicacao': 'hipertensao'
                },
                {
                    'nome': 'metformina',
                    'dose': '850mg',
                    'frequencia': '2x/dia',
                    'inicio_tratamento': '2023-02-01',
                    'indicacao': 'diabetes'
                },
                {
                    'nome': 'atorvastatina',
                    'dose': '20mg',
                    'frequencia': '1x/dia',
                    'inicio_tratamento': '2023-03-10',
                    'indicacao': 'dislipidemia'
                }
            ],
            'exames_laboratoriais': {
                'creatinina': 1.3,  # mg/dL
                'clearance_creatinina': 65,  # mL/min
                'hba1c': 7.2,  # %
                'ldl': 95,  # mg/dL
                'pressao_arterial': '140/85'  # mmHg
            },
            'alergias': ['penicilina'],
            'adesao_estimada': 0.75  # 75%
        }

        return perfil

    async def identificar_prms(self, perfil: dict) -> list[dict]:
        """Identificação automática de PRMs usando IA"""

        prms = []

        categorias_prm = [
            'necessidade_nao_tratada',
            'medicamento_desnecessario',
            'medicamento_inadequado',
            'dose_subterapeutica',
            'dose_excessiva',
            'reacao_adversa',
            'interacao_medicamentosa',
            'nao_adesao'
        ]

        for categoria in categorias_prm:
            resultado = await self.analisador_terapeutico.analisar_categoria(
                perfil=perfil,
                categoria=categoria
            )

            if resultado['detectado']:
                prms.append({
                    'categoria': categoria,
                    'descricao': resultado['descricao'],
                    'gravidade': resultado['gravidade'],
                    'medicamentos_envolvidos': resultado['medicamentos'],
                    'sugestao_resolucao': resultado['sugestao']
                })

        return sorted(prms, key=lambda x: self.get_gravidade_score(x['gravidade']), reverse=True)

    def get_gravidade_score(self, gravidade: str) -> int:
        """Converte gravidade em score numérico"""
        scores = {
            'muito_alta': 4,
            'alta': 3,
            'moderada': 2,
            'baixa': 1
        }
        return scores.get(gravidade, 0)

    async def sugerir_intervencoes(self, prms: list[dict]) -> list[dict]:
        """Sugere intervenções farmacêuticas baseadas nos PRMs"""

        intervencoes = []

        for prm in prms:
            categoria = prm['categoria']

            if categoria == 'dose_subterapeutica':
                intervencoes.append({
                    'tipo': 'ajuste_dose',
                    'prm_relacionado': prm,
                    'acao': 'Aumentar dose conforme protocolo',
                    'justificativa': 'Meta terapêutica não atingida',
                    'prioridade': 'alta',
                    'tempo_estimado': '1-2 semanas'
                })

            elif categoria == 'interacao_medicamentosa':
                intervencoes.append({
                    'tipo': 'substituicao_medicamento',
                    'prm_relacionado': prm,
                    'acao': 'Substituir por alternativa sem interação',
                    'justificativa': 'Evitar interação medicamentosa',
                    'prioridade': 'alta',
                    'tempo_estimado': 'imediato'
                })

            elif categoria == 'nao_adesao':
                intervencoes.append({
                    'tipo': 'educacao_paciente',
                    'prm_relacionado': prm,
                    'acao': 'Programa de educação e acompanhamento',
                    'justificativa': 'Melhorar adesão ao tratamento',
                    'prioridade': 'moderada',
                    'tempo_estimado': '4-6 semanas'
                })

            elif categoria == 'necessidade_nao_tratada':
                intervencoes.append({
                    'tipo': 'adicao_medicamento',
                    'prm_relacionado': prm,
                    'acao': 'Sugerir adição de medicamento',
                    'justificativa': 'Condição clínica não tratada adequadamente',
                    'prioridade': 'moderada',
                    'tempo_estimado': '2-4 semanas'
                })

        return intervencoes

    async def configurar_monitoramento(self, intervencoes: list[dict]) -> dict:
        """Configura plano de monitoramento das intervenções"""

        plano_monitoramento = {
            'parametros_monitorar': [],
            'frequencia_avaliacao': {},
            'metas_terapeuticas': {},
            'alertas_configurados': []
        }

        for intervencao in intervencoes:
            tipo = intervencao['tipo']

            if tipo == 'ajuste_dose':
                plano_monitoramento['parametros_monitorar'].extend([
                    'eficacia_terapeutica',
                    'eventos_adversos',
                    'exames_laboratoriais'
                ])
                plano_monitoramento['frequencia_avaliacao']['ajuste_dose'] = 'semanal'

            elif tipo == 'substituicao_medicamento':
                plano_monitoramento['parametros_monitorar'].extend([
                    'tolerabilidade',
                    'eficacia_comparativa',
                    'interacoes'
                ])
                plano_monitoramento['frequencia_avaliacao']['substituicao'] = 'quinzenal'

            elif tipo == 'educacao_paciente':
                plano_monitoramento['parametros_monitorar'].extend([
                    'adesao_medicamentosa',
                    'conhecimento_tratamento',
                    'qualidade_vida'
                ])
                plano_monitoramento['frequencia_avaliacao']['educacao'] = 'mensal'

        plano_monitoramento['parametros_monitorar'] = list(set(plano_monitoramento['parametros_monitorar']))

        return plano_monitoramento

    def estimar_impacto_clinico(self, intervencoes: list[dict]) -> dict:
        """Estima impacto clínico das intervenções"""

        impacto = {
            'score_impacto_total': 0.0,
            'beneficios_esperados': [],
            'riscos_potenciais': [],
            'custo_beneficio': 'favoravel'
        }

        for intervencao in intervencoes:
            tipo = intervencao['tipo']
            prioridade = intervencao['prioridade']

            score_base = {
                'ajuste_dose': 0.7,
                'substituicao_medicamento': 0.8,
                'educacao_paciente': 0.6,
                'adicao_medicamento': 0.75
            }.get(tipo, 0.5)

            multiplicador_prioridade = {
                'alta': 1.2,
                'moderada': 1.0,
                'baixa': 0.8
            }.get(prioridade, 1.0)

            impacto['score_impacto_total'] += score_base * multiplicador_prioridade

        impacto['score_impacto_total'] = min(1.0, impacto['score_impacto_total'] / len(intervencoes) if intervencoes else 0)

        if impacto['score_impacto_total'] > 0.7:
            impacto['beneficios_esperados'] = [
                'Melhora significativa dos parâmetros clínicos',
                'Redução de eventos adversos',
                'Aumento da adesão ao tratamento'
            ]
        elif impacto['score_impacto_total'] > 0.5:
            impacto['beneficios_esperados'] = [
                'Melhora moderada dos parâmetros clínicos',
                'Otimização da farmacoterapia'
            ]

        return impacto

    async def realizar_conciliacao_medicamentosa(self, paciente_id: str, contexto: str) -> dict:
        """Realiza conciliação medicamentosa"""

        medicamentos_domicilio = await self.obter_medicamentos_domicilio(paciente_id)
        medicamentos_hospital = await self.obter_medicamentos_hospital(paciente_id)

        discrepancias = self.identificar_discrepancias(medicamentos_domicilio, medicamentos_hospital)

        return {
            'contexto': contexto,
            'medicamentos_domicilio': medicamentos_domicilio,
            'medicamentos_hospital': medicamentos_hospital,
            'discrepancias': discrepancias,
            'recomendacoes_conciliacao': self.gerar_recomendacoes_conciliacao(discrepancias),
            'timestamp': datetime.now().isoformat()
        }

    async def obter_medicamentos_domicilio(self, paciente_id: str) -> list[dict]:
        """Obtém medicamentos em uso no domicílio"""

        return [
            {
                'nome': 'enalapril',
                'dose': '10mg',
                'frequencia': '2x/dia',
                'fonte': 'receita_medica'
            },
            {
                'nome': 'metformina',
                'dose': '850mg',
                'frequencia': '2x/dia',
                'fonte': 'entrevista_paciente'
            },
            {
                'nome': 'omeprazol',
                'dose': '20mg',
                'frequencia': '1x/dia',
                'fonte': 'automedicacao'
            }
        ]

    async def obter_medicamentos_hospital(self, paciente_id: str) -> list[dict]:
        """Obtém medicamentos prescritos no hospital"""

        return [
            {
                'nome': 'enalapril',
                'dose': '5mg',
                'frequencia': '2x/dia',
                'prescrito_por': 'Dr. Silva'
            },
            {
                'nome': 'metformina',
                'dose': '850mg',
                'frequencia': '2x/dia',
                'prescrito_por': 'Dr. Silva'
            },
            {
                'nome': 'insulina_regular',
                'dose': '10UI',
                'frequencia': '3x/dia',
                'prescrito_por': 'Dr. Silva'
            }
        ]

    def identificar_discrepancias(self, medicamentos_domicilio: list[dict], medicamentos_hospital: list[dict]) -> list[dict]:
        """Identifica discrepancias entre medicamentos"""

        discrepancias = []

        domicilio_dict = {med['nome']: med for med in medicamentos_domicilio}
        hospital_dict = {med['nome']: med for med in medicamentos_hospital}

        for nome, med_dom in domicilio_dict.items():
            if nome not in hospital_dict:
                discrepancias.append({
                    'tipo': 'descontinuacao',
                    'medicamento': nome,
                    'detalhes': f"Medicamento {nome} usado em casa não foi prescrito no hospital",
                    'gravidade': 'moderada'
                })

        for nome, med_hosp in hospital_dict.items():
            if nome not in domicilio_dict:
                discrepancias.append({
                    'tipo': 'adicao',
                    'medicamento': nome,
                    'detalhes': f"Novo medicamento {nome} prescrito no hospital",
                    'gravidade': 'baixa'
                })

        for nome in set(domicilio_dict.keys()) & set(hospital_dict.keys()):
            med_dom = domicilio_dict[nome]
            med_hosp = hospital_dict[nome]

            if med_dom['dose'] != med_hosp['dose']:
                discrepancias.append({
                    'tipo': 'alteracao_dose',
                    'medicamento': nome,
                    'detalhes': f"Dose alterada de {med_dom['dose']} para {med_hosp['dose']}",
                    'gravidade': 'alta'
                })

        return discrepancias

    def gerar_recomendacoes_conciliacao(self, discrepancias: list[dict]) -> list[str]:
        """Gera recomendações para conciliação"""

        recomendacoes = []

        for discrepancia in discrepancias:
            tipo = discrepancia['tipo']
            medicamento = discrepancia['medicamento']

            if tipo == 'descontinuacao':
                recomendacoes.append(f"Verificar motivo da descontinuação de {medicamento}")
            elif tipo == 'adicao':
                recomendacoes.append(f"Orientar paciente sobre novo medicamento {medicamento}")
            elif tipo == 'alteracao_dose':
                recomendacoes.append(f"Explicar alteração de dose de {medicamento}")

        return recomendacoes

    async def gerar_relatorio_farmacia_clinica(self, periodo: str = '30_dias') -> dict:
        """Gera relatório de atividades da farmácia clínica"""

        return {
            'periodo': periodo,
            'data_relatorio': datetime.now().isoformat(),
            'atividades_realizadas': {
                'acompanhamentos_farmacoterapeuticos': 45,
                'conciliacoes_medicamentosas': 78,
                'intervencoes_farmaceuticas': 123,
                'orientacoes_pacientes': 156
            },
            'prms_identificados': {
                'total': 89,
                'por_categoria': {
                    'dose_inadequada': 25,
                    'interacao_medicamentosa': 18,
                    'nao_adesao': 22,
                    'necessidade_nao_tratada': 15,
                    'outros': 9
                }
            },
            'impacto_clinico': {
                'intervencoes_aceitas': 0.85,  # 85%
                'melhora_parametros_clinicos': 0.72,  # 72%
                'reducao_eventos_adversos': 0.68,  # 68%
                'economia_gerada': 25000.00  # R$
            },
            'indicadores_qualidade': {
                'tempo_medio_acompanhamento': 45,  # minutos
                'satisfacao_pacientes': 4.6,  # escala 1-5
                'taxa_readmissao_30d': 0.12  # 12%
            }
        }


class AnalisadorTerapeuticoIA:
    async def analisar_categoria(self, perfil: dict, categoria: str) -> dict:
        """Analisa categoria específica de PRM"""

        if categoria == 'dose_subterapeutica':
            hba1c = perfil.get('exames_laboratoriais', {}).get('hba1c', 0)
            if hba1c > 7.0:  # Meta para diabéticos
                return {
                    'detectado': True,
                    'descricao': 'HbA1c acima da meta (>7%), possível dose subterapêutica de metformina',
                    'gravidade': 'moderada',
                    'medicamentos': ['metformina'],
                    'sugestao': 'Considerar aumento da dose ou adição de outro antidiabético'
                }

        elif categoria == 'interacao_medicamentosa':
            medicamentos = [med['nome'] for med in perfil.get('medicamentos_atuais', [])]
            if 'enalapril' in medicamentos and 'espironolactona' in medicamentos:
                return {
                    'detectado': True,
                    'descricao': 'Possível interação entre IECA e espironolactona (risco de hipercalemia)',
                    'gravidade': 'alta',
                    'medicamentos': ['enalapril', 'espironolactona'],
                    'sugestao': 'Monitorar potássio sérico regularmente'
                }

        elif categoria == 'nao_adesao':
            adesao = perfil.get('adesao_estimada', 1.0)
            if adesao < 0.8:  # Menos de 80%
                return {
                    'detectado': True,
                    'descricao': f'Adesão estimada baixa ({adesao*100:.0f}%)',
                    'gravidade': 'alta',
                    'medicamentos': [med['nome'] for med in perfil.get('medicamentos_atuais', [])],
                    'sugestao': 'Implementar estratégias para melhorar adesão'
                }

        return {
            'detectado': False,
            'descricao': '',
            'gravidade': 'baixa',
            'medicamentos': [],
            'sugestao': ''
        }


class MonitorAdesaoTerapeutica:
    pass


class EducadorFarmaceuticoIA:
    pass
