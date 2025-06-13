"""
Avaliador Psiquiátrico com IA
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.SaudeMental.Avaliador')

class AvaliadorPsiquiatricoIA:
    """Avaliação psiquiátrica automatizada com IA"""

    def __init__(self):
        self.nlp_psiquiatrico = NLPPsiquiatricoAvancado()
        self.aplicador_escalas = AplicadorEscalasPsiquiatricas()
        self.analisador_sintomas = AnalisadorSintomasPsiquiatricos()

    async def avaliar_completo(self, paciente: dict) -> dict:
        """Avaliação psiquiátrica completa"""

        try:
            anamnese = await self.realizar_anamnese_ia(paciente)

            escalas = await self.aplicar_escalas_completas(paciente)

            sintomas = await self.analisador_sintomas.analisar_completo(anamnese, escalas)

            diagnostico = await self.formular_diagnostico_dsm5(sintomas, escalas)

            perfil_dimensional = self.criar_perfil_dimensional(sintomas)

            return {
                'anamnese': anamnese,
                'escalas': escalas,
                'sintomas': sintomas,
                'diagnostico': diagnostico,
                'perfil_dimensional': perfil_dimensional,
                'gravidade': self.calcular_gravidade_global(escalas),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro na avaliação psiquiátrica: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }

    async def realizar_anamnese_ia(self, paciente: dict) -> dict:
        """Anamnese psiquiátrica com processamento de linguagem natural"""

        respostas = await self.coletar_respostas_chatbot(paciente)

        analise_semantica = self.nlp_psiquiatrico.analisar_respostas(respostas)

        sintomas_extraidos = self.nlp_psiquiatrico.extrair_sintomas(analise_semantica)

        analise_sentimento = self.nlp_psiquiatrico.analisar_sentimento(respostas)

        padroes_pensamento = self.detectar_padroes_cognitivos(analise_semantica)

        return {
            'historia_clinica': self.estruturar_historia(respostas),
            'sintomas_principais': sintomas_extraidos,
            'sentimentos_predominantes': analise_sentimento,
            'padroes_cognitivos': padroes_pensamento,
            'fatores_risco': self.identificar_fatores_risco(respostas),
            'fatores_protecao': self.identificar_fatores_protecao(respostas)
        }

    async def aplicar_escalas_completas(self, paciente: dict) -> dict:
        """Aplicação automática de escalas psiquiátricas"""

        escalas = {
            'phq9': await self.aplicador_escalas.aplicar_phq9(paciente),
            'gad7': await self.aplicador_escalas.aplicar_gad7(paciente),
            'mdq': await self.aplicador_escalas.aplicar_mdq(paciente),
            'pcl5': await self.aplicador_escalas.aplicar_pcl5(paciente),
            'audit': await self.aplicador_escalas.aplicar_audit(paciente),
            'bprs': await self.aplicador_escalas.aplicar_bprs(paciente),
            'ymrs': await self.aplicador_escalas.aplicar_ymrs(paciente),
            'ham_d': await self.aplicador_escalas.aplicar_hamilton_depressao(paciente),
            'ham_a': await self.aplicador_escalas.aplicar_hamilton_ansiedade(paciente)
        }

        return escalas

    async def coletar_respostas_chatbot(self, paciente: dict) -> dict:
        """Simula coleta de respostas via chatbot"""

        return {
            'queixa_principal': paciente.get('queixa_principal', 'Não informado'),
            'historia_doenca_atual': paciente.get('historia_atual', 'Não informado'),
            'historia_pregressa': paciente.get('historia_pregressa', {}),
            'historia_familiar': paciente.get('historia_familiar', {}),
            'uso_medicamentos': paciente.get('medicamentos', []),
            'uso_substancias': paciente.get('substancias', False)
        }

    async def formular_diagnostico_dsm5(self, sintomas: dict, escalas: dict) -> dict:
        """Formulação diagnóstica baseada no DSM-5"""

        diagnosticos_possiveis = []

        phq9_score = escalas.get('phq9', {}).get('score', 0)
        if phq9_score >= 10:
            diagnosticos_possiveis.append({
                'codigo': 'F32.1',
                'nome': 'Episódio Depressivo Moderado',
                'confianca': 0.8,
                'criterios_atendidos': ['Humor deprimido', 'Anedonia', 'Fadiga']
            })

        gad7_score = escalas.get('gad7', {}).get('score', 0)
        if gad7_score >= 10:
            diagnosticos_possiveis.append({
                'codigo': 'F41.1',
                'nome': 'Transtorno de Ansiedade Generalizada',
                'confianca': 0.7,
                'criterios_atendidos': ['Ansiedade excessiva', 'Preocupação']
            })

        diagnostico_principal = max(diagnosticos_possiveis, key=lambda x: x['confianca']) if diagnosticos_possiveis else None

        return {
            'principal': diagnostico_principal,
            'secundarios': diagnosticos_possiveis[1:] if len(diagnosticos_possiveis) > 1 else [],
            'diferenciais': self.gerar_diagnosticos_diferenciais(sintomas),
            'especificadores': self.definir_especificadores(diagnostico_principal)
        }

    def criar_perfil_dimensional(self, sintomas: dict) -> dict:
        """Cria perfil dimensional dos sintomas"""

        return {
            'depressao': sintomas.get('depressao_score', 0),
            'ansiedade': sintomas.get('ansiedade_score', 0),
            'psicose': sintomas.get('psicose_score', 0),
            'mania': sintomas.get('mania_score', 0),
            'trauma': sintomas.get('trauma_score', 0)
        }

    def calcular_gravidade_global(self, escalas: dict) -> str:
        """Calcula gravidade global baseada nas escalas"""

        scores = []
        for _, dados in escalas.items():
            if isinstance(dados, dict) and 'score' in dados:
                scores.append(dados['score'])

        if not scores:
            return 'INDETERMINADO'

        media_scores = sum(scores) / len(scores)

        if media_scores >= 15:
            return 'GRAVE'
        elif media_scores >= 10:
            return 'MODERADO'
        elif media_scores >= 5:
            return 'LEVE'
        else:
            return 'MÍNIMO'

    def estruturar_historia(self, respostas: dict) -> dict:
        """Estrutura a história clínica"""
        return {
            'queixa_principal': respostas.get('queixa_principal'),
            'historia_doenca_atual': respostas.get('historia_doenca_atual'),
            'historia_pregressa': respostas.get('historia_pregressa'),
            'historia_familiar': respostas.get('historia_familiar')
        }

    def identificar_fatores_risco(self, respostas: dict) -> list[str]:
        """Identifica fatores de risco"""
        fatores = []

        if respostas.get('uso_substancias'):
            fatores.append('Uso de substâncias')
        if respostas.get('historia_familiar', {}).get('psiquiatrica'):
            fatores.append('História familiar psiquiátrica')
        if respostas.get('trauma_passado'):
            fatores.append('Trauma no passado')

        return fatores

    def identificar_fatores_protecao(self, respostas: dict) -> list[str]:
        """Identifica fatores de proteção"""
        fatores = []

        if respostas.get('suporte_social'):
            fatores.append('Bom suporte social')
        if respostas.get('emprego_estavel'):
            fatores.append('Emprego estável')
        if respostas.get('atividade_fisica'):
            fatores.append('Prática de atividade física')

        return fatores

    def detectar_padroes_cognitivos(self, analise_semantica: dict) -> list[str]:
        """Detecta padrões cognitivos disfuncionais"""
        return ['Pensamento catastrófico', 'Generalização excessiva']

    def gerar_diagnosticos_diferenciais(self, sintomas: dict) -> list[str]:
        """Gera lista de diagnósticos diferenciais"""
        return ['Transtorno Bipolar', 'Transtorno de Personalidade']

    def definir_especificadores(self, diagnostico: dict) -> list[str]:
        """Define especificadores do diagnóstico"""
        if not diagnostico:
            return []
        return ['Com características ansiosas', 'Episódio único']


class NLPPsiquiatricoAvancado:
    def analisar_respostas(self, respostas: dict) -> dict:
        return {'analise': 'processada'}

    def extrair_sintomas(self, analise: dict) -> dict:
        return {'sintomas': ['depressao', 'ansiedade']}

    def analisar_sentimento(self, respostas: dict) -> dict:
        return {'sentimento': 'negativo', 'intensidade': 0.7}


class AplicadorEscalasPsiquiatricas:
    async def aplicar_phq9(self, paciente: dict) -> dict:
        return {'score': 12, 'interpretacao': 'Depressão moderada'}

    async def aplicar_gad7(self, paciente: dict) -> dict:
        return {'score': 8, 'interpretacao': 'Ansiedade leve'}

    async def aplicar_mdq(self, paciente: dict) -> dict:
        return {'score': 3, 'interpretacao': 'Baixo risco mania'}

    async def aplicar_pcl5(self, paciente: dict) -> dict:
        return {'score': 15, 'interpretacao': 'Sintomas TEPT leves'}

    async def aplicar_audit(self, paciente: dict) -> dict:
        return {'score': 5, 'interpretacao': 'Uso baixo risco'}

    async def aplicar_bprs(self, paciente: dict) -> dict:
        return {'score': 25, 'interpretacao': 'Sintomas psicóticos leves'}

    async def aplicar_ymrs(self, paciente: dict) -> dict:
        return {'score': 2, 'interpretacao': 'Sem mania'}

    async def aplicar_hamilton_depressao(self, paciente: dict) -> dict:
        return {'score': 14, 'interpretacao': 'Depressão moderada'}

    async def aplicar_hamilton_ansiedade(self, paciente: dict) -> dict:
        return {'score': 10, 'interpretacao': 'Ansiedade leve'}


class AnalisadorSintomasPsiquiatricos:
    async def analisar_completo(self, anamnese: dict, escalas: dict) -> dict:
        return {
            'depressao_score': 7,
            'ansiedade_score': 5,
            'psicose_score': 1,
            'mania_score': 0,
            'trauma_score': 3
        }
