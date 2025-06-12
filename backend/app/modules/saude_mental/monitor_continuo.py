"""
Monitor Contínuo de Saúde Mental
"""

import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('MedAI.SaudeMental.Monitor')

class MonitorSaudeMentalContinuo:
    """Monitoramento contínuo de saúde mental"""
    
    def __init__(self):
        self.coletor_dados_passivos = ColetorDadosPassivos()
        self.analisador_padroes = AnalisadorPadroesSaudeMental()
        self.detector_mudancas = DetectorMudancasComportamentais()
        
    async def monitorar_paciente_continuo(self, paciente_id: str) -> Dict:
        """Monitoramento contínuo e passivo de saúde mental"""
        
        try:
            dados_passivos = await self.coletar_dados_multifontes(paciente_id)
            
            padroes = await self.analisar_padroes_comportamentais(dados_passivos)
            
            mudancas = await self.detectar_mudancas_significativas(padroes)
            
            scores_bem_estar = {
                'sono': self.calcular_score_sono(dados_passivos.get('sono', {})),
                'atividade_fisica': self.calcular_score_atividade(dados_passivos.get('atividade', {})),
                'interacao_social': self.calcular_score_social(dados_passivos.get('social', {})),
                'humor': self.inferir_humor(padroes),
                'estresse': self.calcular_nivel_estresse(dados_passivos)
            }
            
            alertas = self.gerar_alertas_baseados_mudancas(mudancas)
            
            return {
                'dados_passivos': dados_passivos,
                'padroes': padroes,
                'mudancas': mudancas,
                'scores': scores_bem_estar,
                'alertas': alertas,
                'tendencias': self.analisar_tendencias_longo_prazo(paciente_id),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro no monitoramento contínuo: {e}")
            return {
                'error': str(e),
                'dados_passivos': {},
                'scores': {},
                'alertas': []
            }
    
    async def coletar_dados_multifontes(self, paciente_id: str) -> Dict:
        """Coleta de dados de múltiplas fontes"""
        
        dados = {
            'smartphone': await self.coletar_dados_smartphone(paciente_id),
            'wearables': await self.coletar_dados_wearables(paciente_id),
            'redes_sociais': await self.analisar_atividade_social(paciente_id),
            'ambiente': await self.coletar_dados_ambientais(paciente_id),
            'voz_passiva': await self.coletar_amostras_voz_passiva(paciente_id)
        }
        
        dados['uso_apps'] = await self.analisar_uso_aplicativos(dados['smartphone'])
        
        dados['digitacao'] = await self.analisar_padroes_digitacao(dados['smartphone'])
        
        dados['mobilidade'] = await self.analisar_padroes_mobilidade(dados['smartphone'])
        
        return dados

    async def analisar_padroes_comportamentais(self, dados_passivos: Dict) -> Dict:
        """Análise de padrões comportamentais"""
        
        return self.analisador_padroes.analisar(dados_passivos)

    async def detectar_mudancas_significativas(self, padroes: Dict) -> Dict:
        """Detecção de mudanças comportamentais significativas"""
        
        return self.detector_mudancas.detectar(padroes)

    def calcular_score_sono(self, dados_sono: Dict) -> float:
        """Calcula score de qualidade do sono"""
        
        if not dados_sono:
            return 0.5  # Score neutro quando não há dados
        
        duracao = dados_sono.get('duracao_horas', 7)
        qualidade = dados_sono.get('qualidade_subjetiva', 5)  # 1-10
        latencia = dados_sono.get('latencia_minutos', 15)
        interrupcoes = dados_sono.get('numero_interrupcoes', 2)
        
        score_duracao = 1.0 if 7 <= duracao <= 9 else max(0, 1 - abs(duracao - 8) * 0.2)
        score_qualidade = qualidade / 10.0
        score_latencia = max(0, 1 - (latencia - 15) * 0.02) if latencia > 15 else 1.0
        score_interrupcoes = max(0, 1 - interrupcoes * 0.1)
        
        score_final = (score_duracao + score_qualidade + score_latencia + score_interrupcoes) / 4
        
        return min(1.0, max(0.0, score_final))

    def calcular_score_atividade(self, dados_atividade: Dict) -> float:
        """Calcula score de atividade física"""
        
        if not dados_atividade:
            return 0.5
        
        passos_diarios = dados_atividade.get('passos_diarios', 5000)
        minutos_exercicio = dados_atividade.get('minutos_exercicio_semanal', 0)
        
        score_passos = min(1.0, passos_diarios / 10000)  # Meta: 10k passos
        score_exercicio = min(1.0, minutos_exercicio / 150)  # Meta: 150 min/semana
        
        return (score_passos + score_exercicio) / 2

    def calcular_score_social(self, dados_social: Dict) -> float:
        """Calcula score de interação social"""
        
        if not dados_social:
            return 0.5
        
        contatos_diarios = dados_social.get('contatos_diarios', 3)
        tempo_interacao = dados_social.get('tempo_interacao_horas', 2)
        qualidade_interacoes = dados_social.get('qualidade_media', 5)  # 1-10
        
        score_contatos = min(1.0, contatos_diarios / 5)  # Meta: 5 contatos/dia
        score_tempo = min(1.0, tempo_interacao / 3)  # Meta: 3 horas/dia
        score_qualidade = qualidade_interacoes / 10.0
        
        return (score_contatos + score_tempo + score_qualidade) / 3

    def inferir_humor(self, padroes: Dict) -> float:
        """Infere humor baseado nos padrões comportamentais"""
        
        indicadores = []
        
        sono_score = padroes.get('sono', {}).get('regularidade', 0.5)
        indicadores.append(sono_score)
        
        atividade_score = padroes.get('atividade', {}).get('nivel', 0.5)
        indicadores.append(atividade_score)
        
        social_score = padroes.get('social', {}).get('engajamento', 0.5)
        indicadores.append(social_score)
        
        smartphone_score = 1 - padroes.get('smartphone', {}).get('uso_excessivo', 0.5)
        indicadores.append(smartphone_score)
        
        return sum(indicadores) / len(indicadores) if indicadores else 0.5

    def calcular_nivel_estresse(self, dados_passivos: Dict) -> float:
        """Calcula nível de estresse baseado em dados passivos"""
        
        indicadores_estresse = []
        
        if 'wearables' in dados_passivos:
            hrv = dados_passivos['wearables'].get('hrv', 50)
            stress_hrv = max(0, 1 - hrv / 50)  # HRV baixo = mais estresse
            indicadores_estresse.append(stress_hrv)
        
        if 'sono' in dados_passivos:
            irregularidade_sono = dados_passivos['sono'].get('irregularidade', 0.3)
            indicadores_estresse.append(irregularidade_sono)
        
        if 'smartphone' in dados_passivos:
            uso_excessivo = dados_passivos['smartphone'].get('tempo_tela_horas', 4) / 12
            indicadores_estresse.append(min(1.0, uso_excessivo))
        
        return sum(indicadores_estresse) / len(indicadores_estresse) if indicadores_estresse else 0.5

    def gerar_alertas_baseados_mudancas(self, mudancas: Dict) -> List[Dict]:
        """Gera alertas baseados nas mudanças detectadas"""
        
        alertas = []
        
        if mudancas.get('sono', {}).get('deterioracao_significativa'):
            alertas.append({
                'tipo': 'sono',
                'nivel': 'moderado',
                'mensagem': 'Deterioração significativa na qualidade do sono detectada',
                'recomendacoes': ['Avaliar higiene do sono', 'Considerar consulta médica']
            })
        
        if mudancas.get('atividade', {}).get('reducao_significativa'):
            alertas.append({
                'tipo': 'atividade',
                'nivel': 'leve',
                'mensagem': 'Redução significativa na atividade física',
                'recomendacoes': ['Incentivar atividade física leve', 'Definir metas graduais']
            })
        
        if mudancas.get('social', {}).get('isolamento_crescente'):
            alertas.append({
                'tipo': 'social',
                'nivel': 'moderado',
                'mensagem': 'Padrão de isolamento social crescente',
                'recomendacoes': ['Ativar rede de apoio', 'Considerar intervenção psicossocial']
            })
        
        if mudancas.get('humor', {}).get('declinio_acentuado'):
            alertas.append({
                'tipo': 'humor',
                'nivel': 'alto',
                'mensagem': 'Declínio acentuado no humor detectado',
                'recomendacoes': ['Avaliação clínica urgente', 'Monitoramento intensificado']
            })
        
        return alertas

    def analisar_tendencias_longo_prazo(self, paciente_id: str) -> Dict:
        """Análise de tendências de longo prazo"""
        
        return {
            'tendencia_geral': 'estavel',
            'melhoria_areas': ['sono', 'atividade_fisica'],
            'areas_atencao': ['interacao_social'],
            'predicao_30_dias': 'estabilidade_mantida',
            'recomendacoes_longo_prazo': [
                'Manter rotina de exercícios',
                'Fortalecer vínculos sociais',
                'Continuar monitoramento'
            ]
        }

    async def coletar_dados_smartphone(self, paciente_id: str) -> Dict:
        """Simula coleta de dados do smartphone"""
        return {
            'tempo_tela_horas': 6.5,
            'numero_desbloqueios': 85,
            'uso_apps_sociais_horas': 2.3,
            'horario_primeiro_uso': '07:30',
            'horario_ultimo_uso': '23:15'
        }

    async def coletar_dados_wearables(self, paciente_id: str) -> Dict:
        """Simula coleta de dados de wearables"""
        return {
            'passos_diarios': 7500,
            'frequencia_cardiaca_media': 72,
            'hrv': 45,
            'calorias_queimadas': 2100,
            'minutos_atividade_moderada': 35
        }

    async def analisar_atividade_social(self, paciente_id: str) -> Dict:
        """Simula análise de atividade social"""
        return {
            'contatos_diarios': 4,
            'tempo_interacao_horas': 2.5,
            'qualidade_media': 6.5,
            'tipos_interacao': ['mensagens', 'chamadas', 'presencial']
        }

    async def coletar_dados_ambientais(self, paciente_id: str) -> Dict:
        """Simula coleta de dados ambientais"""
        return {
            'tempo_fora_casa_horas': 4.2,
            'exposicao_luz_natural_horas': 2.8,
            'nivel_ruido_medio': 45,
            'temperatura_ambiente': 22
        }

    async def coletar_amostras_voz_passiva(self, paciente_id: str) -> Dict:
        """Simula coleta de amostras de voz passiva"""
        return {
            'tempo_fala_diario_minutos': 45,
            'pitch_medio': 165,
            'variabilidade_pitch': 28,
            'pausas_por_minuto': 3.2
        }

    async def analisar_uso_aplicativos(self, dados_smartphone: Dict) -> Dict:
        """Análise de uso de aplicativos"""
        return {
            'apps_mais_usados': ['WhatsApp', 'Instagram', 'YouTube'],
            'tempo_por_categoria': {
                'social': 2.3,
                'entretenimento': 1.8,
                'produtividade': 0.9,
                'saude': 0.3
            }
        }

    async def analisar_padroes_digitacao(self, dados_smartphone: Dict) -> Dict:
        """Análise de padrões de digitação"""
        return {
            'velocidade_media': 45,  # palavras por minuto
            'pausas_entre_palavras': 0.8,
            'pressao_teclas': 'normal',
            'irregularidade': 0.3
        }

    async def analisar_padroes_mobilidade(self, dados_smartphone: Dict) -> Dict:
        """Análise de padrões de mobilidade"""
        return {
            'locais_visitados': 5,
            'tempo_em_casa_horas': 16,
            'distancia_percorrida_km': 12.5,
            'regularidade_rotina': 0.7
        }


class ColetorDadosPassivos:
    pass

class AnalisadorPadroesSaudeMental:
    def analisar(self, dados_passivos: Dict) -> Dict:
        """Análise de padrões comportamentais"""
        return {
            'sono': {
                'regularidade': 0.7,
                'qualidade_tendencia': 'estavel'
            },
            'atividade': {
                'nivel': 0.6,
                'consistencia': 0.5
            },
            'social': {
                'engajamento': 0.6,
                'qualidade_interacoes': 0.7
            },
            'smartphone': {
                'uso_excessivo': 0.4,
                'padroes_saudaveis': 0.6
            }
        }

class DetectorMudancasComportamentais:
    def detectar(self, padroes: Dict) -> Dict:
        """Detecção de mudanças comportamentais"""
        return {
            'sono': {
                'deterioracao_significativa': False,
                'melhoria_detectada': True
            },
            'atividade': {
                'reducao_significativa': False,
                'aumento_detectado': True
            },
            'social': {
                'isolamento_crescente': False,
                'engajamento_melhorado': True
            },
            'humor': {
                'declinio_acentuado': False,
                'estabilidade_mantida': True
            }
        }
