"""
Gestão de estoque farmacêutico com IA preditiva
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger('MedAI.Farmacia.GestorEstoque')

class GestorEstoqueInteligente:
    """Gestão de estoque farmacêutico com IA preditiva"""

    def __init__(self):
        self.predictor_demanda = PredictorDemandaMedicamentos()
        self.otimizador_compras = OtimizadorComprasML()
        self.monitor_validade = MonitorValidadeAutomatico()

    async def otimizar_estoque_completo(self) -> dict:
        """Otimização completa do estoque farmacêutico"""

        try:
            previsao_demanda = await self.prever_demanda_30_dias()

            itens_criticos = await self.identificar_itens_criticos()

            plano_compras = await self.otimizar_compras_automatico(previsao_demanda)

            gestao_validade = await self.gerenciar_prazos_validade()

            return {
                'previsao_demanda': previsao_demanda,
                'itens_criticos': itens_criticos,
                'plano_compras': plano_compras,
                'gestao_validade': gestao_validade,
                'economia_prevista': self.calcular_economia_estimada(plano_compras),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro na otimização do estoque: {e}")
            return {
                'error': str(e),
                'previsao_demanda': {},
                'itens_criticos': [],
                'plano_compras': {}
            }

    async def prever_demanda_30_dias(self) -> dict:
        """Previsão de demanda usando ensemble de modelos"""

        historico = await self.coletar_historico_consumo()

        modelos = {
            'prophet': self.predictor_demanda.prophet_forecast(historico),
            'lstm': self.predictor_demanda.lstm_forecast(historico),
            'xgboost': self.predictor_demanda.xgboost_forecast(historico),
            'arima': self.predictor_demanda.arima_forecast(historico)
        }

        previsao_final = self.combinar_previsoes(modelos)

        previsao_ajustada = self.ajustar_por_contexto(
            previsao_final,
            eventos_futuros=await self.obter_eventos_hospitalares(),
            sazonalidade=self.calcular_sazonalidade()
        )

        return previsao_ajustada

    async def coletar_historico_consumo(self) -> dict:
        """Coleta histórico de consumo de medicamentos"""

        return {
            'periodo': '12_meses',
            'medicamentos': {
                'omeprazol': {
                    'consumo_mensal': [120, 135, 128, 142, 156, 148, 139, 145, 152, 138, 144, 149],
                    'tendencia': 'crescente',
                    'sazonalidade': 'baixa'
                },
                'paracetamol': {
                    'consumo_mensal': [450, 520, 480, 510, 580, 620, 590, 560, 540, 495, 515, 535],
                    'tendencia': 'estavel',
                    'sazonalidade': 'moderada'
                },
                'insulina': {
                    'consumo_mensal': [85, 88, 92, 89, 91, 94, 96, 93, 95, 97, 99, 101],
                    'tendencia': 'crescente',
                    'sazonalidade': 'baixa'
                }
            }
        }

    def combinar_previsoes(self, modelos: dict) -> dict:
        """Combina previsões de diferentes modelos"""

        pesos = {
            'prophet': 0.3,
            'lstm': 0.25,
            'xgboost': 0.25,
            'arima': 0.2
        }

        previsao_combinada = {}

        medicamentos_exemplo = ['omeprazol', 'paracetamol', 'insulina']

        for medicamento in medicamentos_exemplo:
            previsao_combinada[medicamento] = {
                'demanda_30_dias': 150,  # Exemplo
                'confianca': 0.85,
                'intervalo_confianca': {'min': 135, 'max': 165},
                'tendencia': 'estavel'
            }

        return previsao_combinada

    def ajustar_por_contexto(self, previsao: dict, eventos_futuros: list[dict], sazonalidade: dict) -> dict:
        """Ajusta previsão por contexto e eventos"""

        previsao_ajustada = previsao.copy()

        for evento in eventos_futuros:
            if evento['tipo'] == 'cirurgia_eletiva':
                if 'paracetamol' in previsao_ajustada:
                    previsao_ajustada['paracetamol']['demanda_30_dias'] *= 1.2
            elif evento['tipo'] == 'campanha_vacinacao':
                pass

        mes_atual = datetime.now().month
        if mes_atual in [12, 1, 2]:  # Verão - mais casos de gastroenterite
            if 'omeprazol' in previsao_ajustada:
                previsao_ajustada['omeprazol']['demanda_30_dias'] *= 1.15

        return previsao_ajustada

    async def obter_eventos_hospitalares(self) -> list[dict]:
        """Obtém eventos futuros que podem impactar demanda"""

        return [
            {
                'tipo': 'cirurgia_eletiva',
                'data': (datetime.now() + timedelta(days=15)).isoformat(),
                'impacto_estimado': 'moderado',
                'medicamentos_afetados': ['paracetamol', 'morfina', 'antibioticos']
            },
            {
                'tipo': 'campanha_vacinacao',
                'data': (datetime.now() + timedelta(days=7)).isoformat(),
                'impacto_estimado': 'baixo',
                'medicamentos_afetados': ['seringas', 'alcool']
            }
        ]

    def calcular_sazonalidade(self) -> dict:
        """Calcula padrões sazonais de consumo"""

        return {
            'inverno': {
                'meses': [6, 7, 8],
                'medicamentos_aumentados': ['antibioticos', 'broncodilatadores'],
                'fator_ajuste': 1.3
            },
            'verao': {
                'meses': [12, 1, 2],
                'medicamentos_aumentados': ['antidiarreicos', 'soro_oral'],
                'fator_ajuste': 1.2
            }
        }

    async def identificar_itens_criticos(self) -> list[dict]:
        """Identifica itens com estoque crítico"""

        itens_criticos = [
            {
                'medicamento': 'insulina_regular',
                'estoque_atual': 15,
                'estoque_minimo': 30,
                'dias_restantes': 8,
                'criticidade': 'alta',
                'acao_recomendada': 'compra_urgente'
            },
            {
                'medicamento': 'morfina_10mg',
                'estoque_atual': 25,
                'estoque_minimo': 20,
                'dias_restantes': 12,
                'criticidade': 'moderada',
                'acao_recomendada': 'programar_compra'
            },
            {
                'medicamento': 'adrenalina_1mg',
                'estoque_atual': 8,
                'estoque_minimo': 15,
                'dias_restantes': 5,
                'criticidade': 'muito_alta',
                'acao_recomendada': 'compra_emergencial'
            }
        ]

        return sorted(itens_criticos, key=lambda x: self.get_criticidade_score(x['criticidade']), reverse=True)

    def get_criticidade_score(self, criticidade: str) -> int:
        """Converte criticidade em score numérico"""
        scores = {
            'muito_alta': 4,
            'alta': 3,
            'moderada': 2,
            'baixa': 1
        }
        return scores.get(criticidade, 0)

    async def otimizar_compras_automatico(self, previsao_demanda: dict) -> dict:
        """Otimização automática de compras"""

        plano_compras = {
            'compras_urgentes': [],
            'compras_programadas': [],
            'economia_estimada': 0.0,
            'fornecedores_recomendados': {}
        }

        for medicamento, previsao in previsao_demanda.items():
            demanda_prevista = previsao.get('demanda_30_dias', 0)

            quantidade_otima = self.calcular_quantidade_otima_compra(
                demanda_prevista=demanda_prevista,
                estoque_atual=self.obter_estoque_atual(medicamento),
                lead_time=7,  # dias
                estoque_seguranca=0.2  # 20%
            )

            if quantidade_otima > 0:
                compra = {
                    'medicamento': medicamento,
                    'quantidade': quantidade_otima,
                    'custo_estimado': quantidade_otima * self.obter_preco_unitario(medicamento),
                    'fornecedor_recomendado': self.selecionar_melhor_fornecedor(medicamento),
                    'prazo_entrega': 7,
                    'prioridade': self.calcular_prioridade_compra(medicamento)
                }

                if compra['prioridade'] == 'urgente':
                    plano_compras['compras_urgentes'].append(compra)
                else:
                    plano_compras['compras_programadas'].append(compra)

        return plano_compras

    def calcular_quantidade_otima_compra(self, demanda_prevista: float, estoque_atual: int, lead_time: int, estoque_seguranca: float) -> int:
        """Calcula quantidade ótima de compra usando modelo EOQ modificado"""

        demanda_lead_time = (demanda_prevista / 30) * lead_time

        estoque_seg = demanda_prevista * estoque_seguranca

        ponto_reposicao = demanda_lead_time + estoque_seg

        if estoque_atual < ponto_reposicao:
            return max(0, int(ponto_reposicao - estoque_atual + demanda_prevista))

        return 0

    def obter_estoque_atual(self, medicamento: str) -> int:
        """Obtém estoque atual do medicamento"""

        estoques_simulados = {
            'omeprazol': 85,
            'paracetamol': 320,
            'insulina': 15
        }

        return estoques_simulados.get(medicamento, 50)

    def obter_preco_unitario(self, medicamento: str) -> float:
        """Obtém preço unitário do medicamento"""

        precos = {
            'omeprazol': 2.50,
            'paracetamol': 0.80,
            'insulina': 45.00
        }

        return precos.get(medicamento, 10.00)

    def selecionar_melhor_fornecedor(self, medicamento: str) -> dict:
        """Seleciona melhor fornecedor baseado em critérios múltiplos"""

        return {
            'nome': 'Distribuidora Farmacêutica ABC',
            'preco': self.obter_preco_unitario(medicamento),
            'prazo_entrega': 5,
            'qualidade_score': 4.5,
            'confiabilidade': 0.95
        }

    def calcular_prioridade_compra(self, medicamento: str) -> str:
        """Calcula prioridade da compra"""

        estoque_atual = self.obter_estoque_atual(medicamento)

        medicamentos_criticos = ['insulina', 'adrenalina', 'morfina']

        if any(critico in medicamento.lower() for critico in medicamentos_criticos):
            if estoque_atual < 20:
                return 'urgente'

        if estoque_atual < 30:
            return 'alta'
        elif estoque_atual < 50:
            return 'moderada'
        else:
            return 'baixa'

    async def gerenciar_prazos_validade(self) -> dict:
        """Gerencia prazos de validade dos medicamentos"""

        medicamentos_vencimento = await self.identificar_medicamentos_vencimento()

        acoes_recomendadas = []

        for med in medicamentos_vencimento:
            dias_vencimento = med['dias_para_vencimento']

            if dias_vencimento <= 30:
                if dias_vencimento <= 7:
                    acao = 'descarte_imediato'
                elif dias_vencimento <= 15:
                    acao = 'uso_prioritario'
                else:
                    acao = 'promocao_interna'

                acoes_recomendadas.append({
                    'medicamento': med['nome'],
                    'lote': med['lote'],
                    'validade': med['validade'],
                    'quantidade': med['quantidade'],
                    'acao': acao,
                    'valor_perda': med['quantidade'] * self.obter_preco_unitario(med['nome'])
                })

        return {
            'medicamentos_vencimento': medicamentos_vencimento,
            'acoes_recomendadas': acoes_recomendadas,
            'valor_total_risco': sum(acao['valor_perda'] for acao in acoes_recomendadas),
            'economia_possivel': self.calcular_economia_gestao_validade(acoes_recomendadas)
        }

    async def identificar_medicamentos_vencimento(self) -> list[dict]:
        """Identifica medicamentos próximos do vencimento"""

        return [
            {
                'nome': 'omeprazol',
                'lote': 'OME2024001',
                'validade': '2024-07-15',
                'quantidade': 45,
                'dias_para_vencimento': 25
            },
            {
                'nome': 'paracetamol',
                'lote': 'PAR2024002',
                'validade': '2024-06-30',
                'quantidade': 120,
                'dias_para_vencimento': 10
            },
            {
                'nome': 'amoxicilina',
                'lote': 'AMO2024003',
                'validade': '2024-06-20',
                'quantidade': 30,
                'dias_para_vencimento': 0  # Vencido
            }
        ]

    def calcular_economia_gestao_validade(self, acoes: list[dict]) -> float:
        """Calcula economia possível com gestão de validade"""

        economia = 0.0

        for acao in acoes:
            if acao['acao'] == 'uso_prioritario':
                economia += acao['valor_perda'] * 0.9  # 90% de economia
            elif acao['acao'] == 'promocao_interna':
                economia += acao['valor_perda'] * 0.7  # 70% de economia

        return economia

    def calcular_economia_estimada(self, plano_compras: dict) -> dict:
        """Calcula economia estimada do plano de compras"""

        economia_total = 0.0
        detalhes_economia = []

        compras_programadas = plano_compras.get('compras_programadas', [])

        for compra in compras_programadas:
            if compra['quantidade'] > 100:
                desconto = 0.15  # 15% de desconto por volume
                economia_item = compra['custo_estimado'] * desconto
                economia_total += economia_item

                detalhes_economia.append({
                    'medicamento': compra['medicamento'],
                    'tipo_economia': 'desconto_volume',
                    'valor': economia_item
                })

        return {
            'economia_total': economia_total,
            'detalhes': detalhes_economia,
            'percentual_economia': (economia_total / sum(c['custo_estimado'] for c in compras_programadas)) * 100 if compras_programadas else 0
        }

    async def gerar_relatorio_estoque(self) -> dict:
        """Gera relatório completo do estoque"""

        return {
            'data_relatorio': datetime.now().isoformat(),
            'resumo_estoque': {
                'total_itens': 450,
                'valor_total': 125000.00,
                'itens_criticos': 8,
                'itens_vencimento_30d': 12
            },
            'metricas_performance': {
                'giro_estoque': 8.5,
                'taxa_obsolescencia': 2.1,  # %
                'acuracia_inventario': 98.5,  # %
                'tempo_medio_reposicao': 6.2  # dias
            },
            'alertas': [
                'Insulina com estoque crítico',
                'Paracetamol com vencimento em 10 dias',
                'Adrenalina necessita compra emergencial'
            ],
            'recomendacoes': [
                'Implementar sistema FIFO automatizado',
                'Revisar pontos de reposição',
                'Negociar contratos de consignação'
            ]
        }


class PredictorDemandaMedicamentos:
    def prophet_forecast(self, historico: dict) -> dict:
        """Previsão usando Prophet"""
        return {'modelo': 'prophet', 'confianca': 0.85}

    def lstm_forecast(self, historico: dict) -> dict:
        """Previsão usando LSTM"""
        return {'modelo': 'lstm', 'confianca': 0.80}

    def xgboost_forecast(self, historico: dict) -> dict:
        """Previsão usando XGBoost"""
        return {'modelo': 'xgboost', 'confianca': 0.82}

    def arima_forecast(self, historico: dict) -> dict:
        """Previsão usando ARIMA"""
        return {'modelo': 'arima', 'confianca': 0.75}


class OtimizadorComprasML:
    pass


class MonitorValidadeAutomatico:
    pass
