"""
Planejador de Reabilitação com IA
"""

import asyncio
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger('MedAI.Reabilitacao.PlanejadorReabilitacao')

class PlanejadorReabilitacaoIA:
    """Planejamento inteligente de reabilitação"""
    
    def __init__(self):
        self.gerador_exercicios = GeradorExerciciosIA()
        self.otimizador_progressao = OtimizadorProgressaoML()
        self.personalizador = PersonalizadorTerapiaIA()
        
    async def criar_plano_reabilitacao(self, avaliacao: Dict, objetivos: List[str]) -> Dict:
        """Criação de plano de reabilitação personalizado com IA"""
        
        try:
            objetivos_smart = self.definir_objetivos_smart(avaliacao, objetivos)
            
            exercicios = await self.selecionar_exercicios_otimos(
                condicao=avaliacao.get('diagnostico', ''),
                limitacoes=avaliacao.get('limitacoes', []),
                objetivos=objetivos_smart,
                preferencias=avaliacao.get('preferencias', {})
            )
            
            progressao = self.otimizador_progressao.criar_progressao(
                exercicios=exercicios,
                nivel_inicial=avaliacao.get('score_global', 0.5),
                velocidade_progressao='adaptativa'
            )
            
            plano_personalizado = self.personalizador.personalizar_plano(
                plano_base=progressao,
                perfil_paciente=avaliacao.get('perfil', {}),
                fatores_psicossociais=avaliacao.get('psicossocial', {})
            )
            
            return {
                'objetivos': objetivos_smart,
                'fases': plano_personalizado.get('fases', []),
                'exercicios': plano_personalizado.get('exercicios', []),
                'progressao': plano_personalizado.get('progressao', {}),
                'duracao_estimada': self.estimar_duracao_tratamento(avaliacao),
                'marcos_avaliacao': self.definir_marcos_reavaliacao(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na criação do plano de reabilitação: {e}")
            return {
                'error': str(e),
                'objetivos': [],
                'exercicios': []
            }
    
    async def selecionar_exercicios_otimos(self, **kwargs) -> List[Dict]:
        """Seleção de exercícios baseada em evidências e IA"""
        
        try:
            exercicios_disponiveis = await self.carregar_base_exercicios()
            
            exercicios_filtrados = self.filtrar_por_seguranca(
                exercicios_disponiveis,
                condicao=kwargs.get('condicao', ''),
                limitacoes=kwargs.get('limitacoes', [])
            )
            
            exercicios_rankeados = self.rankear_por_eficacia(
                exercicios_filtrados,
                objetivos=kwargs.get('objetivos', []),
                nivel_evidencia_minimo='B'
            )
            
            combinacao_otima = self.otimizar_combinacao_exercicios(
                exercicios_rankeados,
                tempo_sessao=kwargs.get('tempo_sessao', 60),
                frequencia_semanal=kwargs.get('frequencia', 3)
            )
            
            return combinacao_otima
            
        except Exception as e:
            logger.error(f"Erro na seleção de exercícios: {e}")
            return []

    def definir_objetivos_smart(self, avaliacao: Dict, objetivos_gerais: List[str]) -> List[Dict]:
        """Define objetivos SMART baseados na avaliação"""
        
        objetivos_smart = []
        
        for objetivo in objetivos_gerais:
            if 'mobilidade' in objetivo.lower():
                objetivos_smart.append({
                    'especifico': 'Melhorar amplitude de movimento de quadril',
                    'mensuravel': 'Aumentar flexão de quadril em 20 graus',
                    'atingivel': True,
                    'relevante': 'Essencial para AVDs',
                    'temporal': '8 semanas',
                    'prioridade': 'Alta'
                })
            elif 'força' in objetivo.lower():
                objetivos_smart.append({
                    'especifico': 'Fortalecer músculos extensores de joelho',
                    'mensuravel': 'Aumentar força em 30% na dinamometria',
                    'atingivel': True,
                    'relevante': 'Melhora estabilidade e função',
                    'temporal': '6 semanas',
                    'prioridade': 'Alta'
                })
            elif 'equilíbrio' in objetivo.lower():
                objetivos_smart.append({
                    'especifico': 'Melhorar equilíbrio estático e dinâmico',
                    'mensuravel': 'Aumentar score Berg Balance em 10 pontos',
                    'atingivel': True,
                    'relevante': 'Reduz risco de quedas',
                    'temporal': '4 semanas',
                    'prioridade': 'Moderada'
                })
        
        return objetivos_smart

    async def carregar_base_exercicios(self) -> List[Dict]:
        """Carrega base de dados de exercícios"""
        
        return [
            {
                'nome': 'Fortalecimento de quadríceps',
                'tipo': 'Fortalecimento',
                'grupo_muscular': 'Quadríceps',
                'nivel_evidencia': 'A',
                'indicacoes': ['Fraqueza de quadríceps', 'Instabilidade de joelho'],
                'contraindicacoes': ['Dor aguda de joelho'],
                'progressao': ['Isométrico', 'Isotônico', 'Funcional'],
                'tempo_sessao': 15
            },
            {
                'nome': 'Alongamento de isquiotibiais',
                'tipo': 'Flexibilidade',
                'grupo_muscular': 'Isquiotibiais',
                'nivel_evidencia': 'B',
                'indicacoes': ['Encurtamento de isquiotibiais', 'Limitação de ADM'],
                'contraindicacoes': ['Lesão muscular aguda'],
                'progressao': ['Passivo', 'Ativo-assistido', 'Ativo'],
                'tempo_sessao': 10
            },
            {
                'nome': 'Treino de marcha',
                'tipo': 'Funcional',
                'grupo_muscular': 'Múltiplos',
                'nivel_evidencia': 'A',
                'indicacoes': ['Alteração de marcha', 'Redução de velocidade'],
                'contraindicacoes': ['Instabilidade cardiovascular'],
                'progressao': ['Paralelas', 'Andador', 'Independente'],
                'tempo_sessao': 20
            },
            {
                'nome': 'Exercícios de equilíbrio',
                'tipo': 'Propriocepção',
                'grupo_muscular': 'Core',
                'nivel_evidencia': 'A',
                'indicacoes': ['Risco de quedas', 'Instabilidade postural'],
                'contraindicacoes': ['Vertigem aguda'],
                'progressao': ['Estático', 'Dinâmico', 'Perturbação'],
                'tempo_sessao': 15
            }
        ]

    def filtrar_por_seguranca(self, exercicios: List[Dict], condicao: str, limitacoes: List[str]) -> List[Dict]:
        """Filtra exercícios por segurança"""
        
        exercicios_seguros = []
        
        for exercicio in exercicios:
            contraindicado = False
            for contraindicacao in exercicio.get('contraindicacoes', []):
                if any(limitacao.lower() in contraindicacao.lower() for limitacao in limitacoes):
                    contraindicado = True
                    break
            
            if not contraindicado:
                exercicios_seguros.append(exercicio)
        
        return exercicios_seguros

    def rankear_por_eficacia(self, exercicios: List[Dict], objetivos: List[Dict], nivel_evidencia_minimo: str) -> List[Dict]:
        """Rankeia exercícios por eficácia"""
        
        niveis_evidencia = {'A': 3, 'B': 2, 'C': 1}
        minimo = niveis_evidencia.get(nivel_evidencia_minimo, 1)
        
        exercicios_rankeados = []
        
        for exercicio in exercicios:
            nivel = niveis_evidencia.get(exercicio.get('nivel_evidencia', 'C'), 1)
            
            if nivel >= minimo:
                score_relevancia = self.calcular_relevancia_exercicio(exercicio, objetivos)
                exercicio['score_total'] = nivel + score_relevancia
                exercicios_rankeados.append(exercicio)
        
        exercicios_rankeados.sort(key=lambda x: x['score_total'], reverse=True)
        
        return exercicios_rankeados

    def calcular_relevancia_exercicio(self, exercicio: Dict, objetivos: List[Dict]) -> float:
        """Calcula relevância do exercício para os objetivos"""
        
        score = 0
        
        for objetivo in objetivos:
            if exercicio['tipo'].lower() in objetivo.get('especifico', '').lower():
                score += 2
            
            if any(indicacao.lower() in objetivo.get('especifico', '').lower() 
                   for indicacao in exercicio.get('indicacoes', [])):
                score += 1
        
        return score

    def otimizar_combinacao_exercicios(self, exercicios: List[Dict], tempo_sessao: int, frequencia_semanal: int) -> List[Dict]:
        """Otimiza combinação de exercícios"""
        
        combinacao_otima = []
        tempo_total = 0
        tipos_incluidos = set()
        
        for exercicio in exercicios:
            tempo_exercicio = exercicio.get('tempo_sessao', 10)
            
            if tempo_total + tempo_exercicio <= tempo_sessao:
                if exercicio['tipo'] not in tipos_incluidos or len(combinacao_otima) < 3:
                    combinacao_otima.append(exercicio)
                    tempo_total += tempo_exercicio
                    tipos_incluidos.add(exercicio['tipo'])
        
        return combinacao_otima

    def estimar_duracao_tratamento(self, avaliacao: Dict) -> Dict:
        """Estima duração do tratamento"""
        
        score_funcional = avaliacao.get('score_global', 0.5)
        
        if score_funcional < 0.3:
            duracao_base = 16
        elif score_funcional < 0.6:
            duracao_base = 12
        else:
            duracao_base = 8
        
        fatores_ajuste = {
            'idade': avaliacao.get('idade', 50),
            'comorbidades': len(avaliacao.get('comorbidades', [])),
            'motivacao': avaliacao.get('motivacao', 0.7)
        }
        
        if fatores_ajuste['idade'] > 65:
            duracao_base *= 1.2
        if fatores_ajuste['comorbidades'] > 2:
            duracao_base *= 1.1
        if fatores_ajuste['motivacao'] > 0.8:
            duracao_base *= 0.9
        
        return {
            'duracao_semanas': int(duracao_base),
            'sessoes_por_semana': 3,
            'total_sessoes': int(duracao_base * 3),
            'fatores_considerados': fatores_ajuste
        }

    def definir_marcos_reavaliacao(self) -> List[Dict]:
        """Define marcos de reavaliação"""
        
        return [
            {
                'semana': 2,
                'tipo': 'Avaliação inicial de progresso',
                'instrumentos': ['Escala de dor', 'ADM básica'],
                'criterios_progressao': ['Redução de dor > 30%', 'Melhora ADM > 10%']
            },
            {
                'semana': 4,
                'tipo': 'Avaliação funcional intermediária',
                'instrumentos': ['Testes funcionais', 'Força muscular'],
                'criterios_progressao': ['Melhora força > 20%', 'Melhora funcional > 25%']
            },
            {
                'semana': 8,
                'tipo': 'Avaliação abrangente',
                'instrumentos': ['Bateria completa de testes'],
                'criterios_progressao': ['Objetivos 75% atingidos']
            }
        ]


class GeradorExerciciosIA:
    pass


class OtimizadorProgressaoML:
    def criar_progressao(self, exercicios: List[Dict], nivel_inicial: float, velocidade_progressao: str) -> Dict:
        """Cria progressão de exercícios"""
        
        fases = []
        
        fases.append({
            'nome': 'Fase Inicial',
            'semanas': [1, 2],
            'intensidade': 'Baixa',
            'foco': 'Adaptação e redução de sintomas',
            'exercicios': exercicios[:2]  # Primeiros 2 exercícios
        })
        
        fases.append({
            'nome': 'Fase Intermediária',
            'semanas': [3, 4, 5, 6],
            'intensidade': 'Moderada',
            'foco': 'Fortalecimento e melhora funcional',
            'exercicios': exercicios[:4]  # Primeiros 4 exercícios
        })
        
        fases.append({
            'nome': 'Fase Avançada',
            'semanas': [7, 8, 9, 10],
            'intensidade': 'Alta',
            'foco': 'Otimização e retorno funcional',
            'exercicios': exercicios  # Todos os exercícios
        })
        
        return {
            'fases': fases,
            'criterios_progressao': self.definir_criterios_progressao(),
            'ajustes_automaticos': True
        }

    def definir_criterios_progressao(self) -> Dict:
        """Define critérios para progressão entre fases"""
        
        return {
            'inicial_para_intermediaria': [
                'Redução de dor > 50%',
                'Tolerância aos exercícios básicos',
                'Melhora ADM > 15%'
            ],
            'intermediaria_para_avancada': [
                'Força muscular > 70% do normal',
                'Funcionalidade > 60%',
                'Ausência de dor durante exercícios'
            ],
            'criterios_alta': [
                'Objetivos funcionais atingidos',
                'Independência nas AVDs',
                'Confiança do paciente'
            ]
        }


class PersonalizadorTerapiaIA:
    def personalizar_plano(self, plano_base: Dict, perfil_paciente: Dict, fatores_psicossociais: Dict) -> Dict:
        """Personaliza plano baseado no perfil do paciente"""
        
        plano_personalizado = plano_base.copy()
        
        idade = perfil_paciente.get('idade', 50)
        if idade > 65:
            for fase in plano_personalizado.get('fases', []):
                if fase['intensidade'] == 'Alta':
                    fase['intensidade'] = 'Moderada'
        
        motivacao = fatores_psicossociais.get('motivacao', 0.7)
        if motivacao < 0.5:
            plano_personalizado['elementos_motivacionais'] = [
                'Gamificação dos exercícios',
                'Metas de curto prazo',
                'Feedback positivo frequente'
            ]
        
        return plano_personalizado
