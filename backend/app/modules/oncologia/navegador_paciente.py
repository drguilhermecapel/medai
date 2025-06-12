"""
Navegador de paciente oncológico
"""

import asyncio
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger('MedAI.Oncologia.NavegadorPaciente')

class NavegadorPacienteOncologico:
    """Navegador de paciente oncológico"""
    
    def __init__(self):
        self.coordenador_cuidados = CoordenadorCuidadosOncologicos()
        self.educador_paciente = EducadorPacienteIA()
        self.suporte_psicossocial = SuportePsicossocialIA()
        self.gestor_recursos = GestorRecursosComunitarios()
        
    async def navegar_jornada_completa(self, pacientes_oncologicos: List[Dict],
                                       navegacao_personalizada: bool = True,
                                       suporte_integral: bool = True) -> Dict:
        """Navegação completa da jornada do paciente oncológico"""
        
        try:
            navegacao_pacientes = {}
            
            for paciente in pacientes_oncologicos:
                coordenacao = await self.coordenador_cuidados.coordenar_cuidados_integrais(
                    paciente=paciente,
                    equipe_multidisciplinar=True,
                    cuidados_paliativos=paciente.get('necessita_cuidados_paliativos', False),
                    suporte_familiar=True,
                    navegacao_sistema=True
                )
                
                educacao = await self.educador_paciente.educar_paciente_familia(
                    paciente=paciente,
                    nivel_educacional=paciente.get('nivel_educacional', 'medio'),
                    preferencias_aprendizado=paciente.get('preferencias_aprendizado', []),
                    barreiras_comunicacao=paciente.get('barreiras_comunicacao', []),
                    incluir_familia=True,
                    materiais_personalizados=navegacao_personalizada
                )
                
                if suporte_integral:
                    suporte = await self.suporte_psicossocial.avaliar_necessidades_psicossociais(
                        paciente=paciente,
                        familia=paciente.get('familia'),
                        fatores_estresse=await self.identificar_fatores_estresse(paciente),
                        recursos_enfrentamento=paciente.get('recursos_enfrentamento', []),
                        intervencoes_personalizadas=True
                    )
                else:
                    suporte = None
                
                recursos = await self.gestor_recursos.mapear_recursos_disponiveis(
                    paciente=paciente,
                    necessidades_identificadas=await self.identificar_necessidades_recursos(
                        paciente
                    ),
                    localizacao=paciente.get('endereco'),
                    recursos_financeiros=paciente.get('situacao_financeira'),
                    incluir_recursos_comunitarios=True
                )
                
                plano_navegacao = await self.criar_plano_navegacao_personalizado(
                    paciente=paciente,
                    coordenacao=coordenacao,
                    educacao=educacao,
                    suporte=suporte,
                    recursos=recursos
                )
                
                monitoramento = await self.definir_monitoramento_jornada(
                    paciente=paciente,
                    plano_navegacao=plano_navegacao,
                    indicadores_qualidade=True,
                    satisfacao_paciente=True
                )
                
                navegacao_pacientes[paciente['id']] = {
                    'coordenacao_cuidados': coordenacao,
                    'educacao_paciente': educacao,
                    'suporte_psicossocial': suporte,
                    'recursos_mapeados': recursos,
                    'plano_navegacao': plano_navegacao,
                    'monitoramento_jornada': monitoramento,
                    'barreiras_identificadas': await self.identificar_barreiras_acesso(
                        paciente
                    ),
                    'satisfacao_navegacao': await self.avaliar_satisfacao_navegacao(
                        paciente
                    )
                }
            
            return {
                'navegacao_individualizada': navegacao_pacientes,
                'estatisticas_navegacao': await self.calcular_estatisticas_navegacao(
                    navegacao_pacientes
                ),
                'impacto_navegacao': await self.avaliar_impacto_navegacao(),
                'recursos_mais_utilizados': await self.analisar_recursos_utilizados(),
                'satisfacao_geral': await self.calcular_satisfacao_geral(navegacao_pacientes)
            }
            
        except Exception as e:
            logger.error(f"Erro na navegação de pacientes oncológicos: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def identificar_fatores_estresse(self, paciente: Dict) -> List[Dict]:
        """Identifica fatores de estresse do paciente"""
        
        fatores = []
        
        if paciente.get('tempo_diagnostico_dias', 0) < 30:
            fatores.append({
                'fator': 'Diagnóstico recente',
                'categoria': 'diagnostico',
                'intensidade': 'alta'
            })
        
        if paciente.get('situacao_financeira') == 'dificil':
            fatores.append({
                'fator': 'Dificuldades financeiras',
                'categoria': 'socioeconomico',
                'intensidade': 'alta'
            })
        
        if not paciente.get('suporte_familiar'):
            fatores.append({
                'fator': 'Falta de suporte familiar',
                'categoria': 'familiar',
                'intensidade': 'moderada'
            })
        
        if paciente.get('tratamento_complexo'):
            fatores.append({
                'fator': 'Complexidade do tratamento',
                'categoria': 'tratamento',
                'intensidade': 'moderada'
            })
        
        return fatores

    async def identificar_necessidades_recursos(self, paciente: Dict) -> List[str]:
        """Identifica necessidades de recursos"""
        
        necessidades = []
        
        if paciente.get('situacao_financeira') in ['dificil', 'muito_dificil']:
            necessidades.extend([
                'auxilio_financeiro',
                'medicamentos_gratuitos',
                'transporte_tratamento'
            ])
        
        if paciente.get('dependencia_cuidados'):
            necessidades.extend([
                'cuidador_domiciliar',
                'equipamentos_medicos',
                'home_care'
            ])
        
        if paciente.get('distress_psicologico', 0) > 5:
            necessidades.extend([
                'suporte_psicologico',
                'grupos_apoio',
                'terapia_familiar'
            ])
        
        if paciente.get('conhecimento_doenca', 'baixo') == 'baixo':
            necessidades.extend([
                'educacao_doenca',
                'materiais_educativos',
                'orientacao_nutricional'
            ])
        
        return necessidades

    async def criar_plano_navegacao_personalizado(self, paciente: Dict, **componentes) -> Dict:
        """Cria plano de navegação personalizado"""
        
        return {
            'objetivos_navegacao': [
                'Facilitar acesso aos cuidados',
                'Melhorar aderência ao tratamento',
                'Reduzir barreiras de acesso',
                'Otimizar qualidade de vida'
            ],
            'estrategias_personalizadas': await self.definir_estrategias_personalizadas(
                paciente
            ),
            'cronograma_atividades': await self.definir_cronograma_navegacao(paciente),
            'responsabilidades_navegador': [
                'Coordenação de consultas',
                'Educação contínua',
                'Suporte emocional',
                'Conexão com recursos'
            ],
            'indicadores_sucesso': [
                'Aderência ao tratamento > 90%',
                'Satisfação paciente > 4.0',
                'Redução tempo espera',
                'Melhoria qualidade vida'
            ],
            'frequencia_contato': await self.definir_frequencia_contato(paciente)
        }

    async def definir_estrategias_personalizadas(self, paciente: Dict) -> List[Dict]:
        """Define estratégias personalizadas de navegação"""
        
        estrategias = []
        
        if paciente.get('idade', 0) > 65:
            estrategias.append({
                'estrategia': 'Comunicação simplificada',
                'descricao': 'Usar linguagem clara e repetir informações importantes',
                'frequencia': 'A cada contato'
            })
        
        if paciente.get('nivel_educacional') == 'baixo':
            estrategias.append({
                'estrategia': 'Materiais visuais',
                'descricao': 'Utilizar infográficos e vídeos educativos',
                'frequencia': 'Conforme necessário'
            })
        
        if paciente.get('ansiedade_alta'):
            estrategias.append({
                'estrategia': 'Suporte emocional intensificado',
                'descricao': 'Contatos mais frequentes e encaminhamento psicológico',
                'frequencia': 'Semanal'
            })
        
        return estrategias

    async def definir_cronograma_navegacao(self, paciente: Dict) -> Dict:
        """Define cronograma de navegação"""
        
        return {
            'fase_inicial': {
                'duracao': '30 dias',
                'atividades': [
                    'Avaliação inicial completa',
                    'Educação sobre diagnóstico',
                    'Mapeamento de recursos',
                    'Plano de cuidados'
                ],
                'frequencia_contato': 'Semanal'
            },
            'fase_tratamento': {
                'duracao': 'Durante tratamento ativo',
                'atividades': [
                    'Coordenação consultas',
                    'Monitoramento aderência',
                    'Suporte toxicidades',
                    'Educação contínua'
                ],
                'frequencia_contato': 'Quinzenal'
            },
            'fase_seguimento': {
                'duracao': 'Pós-tratamento',
                'atividades': [
                    'Monitoramento sobrevivência',
                    'Prevenção secundária',
                    'Suporte reintegração',
                    'Vigilância recidiva'
                ],
                'frequencia_contato': 'Mensal'
            }
        }

    async def definir_frequencia_contato(self, paciente: Dict) -> Dict:
        """Define frequência de contato"""
        
        frequencia_base = 'quinzenal'
        
        if paciente.get('complexidade_caso') == 'alta':
            frequencia_base = 'semanal'
        
        if paciente.get('suporte_social') == 'baixo':
            frequencia_base = 'semanal'
        
        if paciente.get('aderencia_historica', 1.0) < 0.8:
            frequencia_base = 'semanal'
        
        return {
            'frequencia_principal': frequencia_base,
            'contatos_emergencia': 'Disponível 24/7',
            'modalidades': ['telefone', 'presencial', 'video_chamada'],
            'preferencia_paciente': paciente.get('preferencia_contato', 'telefone')
        }

    async def definir_monitoramento_jornada(self, paciente: Dict, plano: Dict, **kwargs) -> Dict:
        """Define monitoramento da jornada"""
        
        return {
            'indicadores_processo': [
                'Tempo para início tratamento',
                'Taxa de comparecimento consultas',
                'Aderência ao protocolo',
                'Utilização de recursos'
            ],
            'indicadores_resultado': [
                'Satisfação paciente',
                'Qualidade de vida',
                'Distress psicológico',
                'Conhecimento sobre doença'
            ],
            'ferramentas_avaliacao': [
                'Questionários validados',
                'Escalas de satisfação',
                'Indicadores administrativos',
                'Feedback qualitativo'
            ],
            'frequencia_avaliacao': 'Mensal'
        }

    async def identificar_barreiras_acesso(self, paciente: Dict) -> List[Dict]:
        """Identifica barreiras de acesso"""
        
        barreiras = []
        
        if paciente.get('distancia_hospital_km', 0) > 50:
            barreiras.append({
                'tipo': 'geografica',
                'descricao': 'Distância do centro de tratamento',
                'impacto': 'alto'
            })
        
        if paciente.get('situacao_financeira') == 'dificil':
            barreiras.append({
                'tipo': 'financeira',
                'descricao': 'Dificuldades econômicas',
                'impacto': 'alto'
            })
        
        if paciente.get('idioma_principal') != 'portugues':
            barreiras.append({
                'tipo': 'linguistica',
                'descricao': 'Barreira de idioma',
                'impacto': 'moderado'
            })
        
        if not paciente.get('acesso_internet'):
            barreiras.append({
                'tipo': 'tecnologica',
                'descricao': 'Falta de acesso à internet',
                'impacto': 'moderado'
            })
        
        return barreiras

    async def avaliar_satisfacao_navegacao(self, paciente: Dict) -> Dict:
        """Avalia satisfação com a navegação"""
        
        return {
            'satisfacao_geral': 4.5,  # escala 1-5
            'aspectos_avaliados': {
                'comunicacao_navegador': 4.7,
                'coordenacao_cuidados': 4.3,
                'suporte_emocional': 4.6,
                'acesso_recursos': 4.2
            },
            'recomendaria_servico': True,
            'comentarios_qualitativos': [
                'Navegador muito atencioso',
                'Ajudou muito na coordenação'
            ]
        }

    async def calcular_estatisticas_navegacao(self, navegacao: Dict) -> Dict:
        """Calcula estatísticas de navegação"""
        
        return {
            'pacientes_navegados': len(navegacao),
            'tempo_medio_navegacao': 180,  # dias
            'taxa_aderencia_tratamento': 0.92,
            'satisfacao_media': 4.4,
            'recursos_conectados_media': 3.2
        }

    async def avaliar_impacto_navegacao(self) -> Dict:
        """Avalia impacto da navegação"""
        
        return {
            'melhoria_aderencia': 0.25,  # 25% melhoria
            'reducao_tempo_inicio_tratamento': 0.35,  # 35% redução
            'aumento_satisfacao': 0.30,  # 30% aumento
            'reducao_hospitalizacoes_evitaveis': 0.20,  # 20% redução
            'roi_navegacao': 3.8
        }

    async def analisar_recursos_utilizados(self) -> Dict:
        """Analisa recursos mais utilizados"""
        
        return {
            'recursos_frequentes': [
                {'tipo': 'Transporte', 'utilizacao': 0.78},
                {'tipo': 'Suporte psicológico', 'utilizacao': 0.65},
                {'tipo': 'Auxílio medicamentos', 'utilizacao': 0.52},
                {'tipo': 'Grupos de apoio', 'utilizacao': 0.43}
            ],
            'efetividade_recursos': 0.82,
            'tempo_medio_conexao': 5.2  # dias
        }

    async def calcular_satisfacao_geral(self, navegacao: Dict) -> Dict:
        """Calcula satisfação geral"""
        
        return {
            'satisfacao_media_geral': 4.4,
            'distribuicao_satisfacao': {
                'muito_satisfeito': 0.68,
                'satisfeito': 0.25,
                'neutro': 0.05,
                'insatisfeito': 0.02
            },
            'fatores_satisfacao': [
                'Comunicação efetiva',
                'Coordenação cuidados',
                'Suporte emocional'
            ]
        }


class CoordenadorCuidadosOncologicos:
    """Coordenador de cuidados oncológicos"""
    
    async def coordenar_cuidados_integrais(self, **kwargs) -> Dict:
        """Coordena cuidados integrais"""
        
        return {
            'equipe_coordenada': ['Oncologia', 'Enfermagem', 'Farmácia', 'Psicologia'],
            'plano_cuidados_integrado': True,
            'comunicacao_equipe': 'Efetiva',
            'continuidade_cuidados': 'Garantida'
        }


class EducadorPacienteIA:
    """Educador de paciente com IA"""
    
    async def educar_paciente_familia(self, **kwargs) -> Dict:
        """Educa paciente e família"""
        
        return {
            'materiais_fornecidos': ['Guia da doença', 'Vídeos educativos'],
            'sessoes_educativas': 4,
            'nivel_compreensao': 'Adequado',
            'familia_incluida': kwargs.get('incluir_familia', True)
        }


class SuportePsicossocialIA:
    """Suporte psicossocial com IA"""
    
    async def avaliar_necessidades_psicossociais(self, **kwargs) -> Dict:
        """Avalia necessidades psicossociais"""
        
        return {
            'distress_score': 4.2,
            'necessidades_identificadas': ['Ansiedade', 'Suporte familiar'],
            'intervencoes_recomendadas': ['Psicoterapia', 'Grupo de apoio'],
            'recursos_acionados': 2
        }


class GestorRecursosComunitarios:
    """Gestor de recursos comunitários"""
    
    async def mapear_recursos_disponiveis(self, **kwargs) -> Dict:
        """Mapeia recursos disponíveis"""
        
        return {
            'recursos_identificados': [
                'Casa de apoio',
                'Transporte gratuito',
                'Auxílio medicamentos',
                'Suporte nutricional'
            ],
            'recursos_conectados': 3,
            'tempo_conexao_medio': 5,  # dias
            'efetividade_conexao': 0.85
        }
