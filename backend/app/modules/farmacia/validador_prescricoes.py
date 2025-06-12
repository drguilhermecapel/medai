"""
Validação inteligente de prescrições com múltiplas checagens
"""

import logging
from datetime import datetime

logger = logging.getLogger('MedAI.Farmacia.ValidadorPrescricoes')

class ValidadorPrescricoesIA:
    """Validação inteligente de prescrições com múltiplas checagens"""

    def __init__(self):
        self.modelo_interacoes = ModeloInteracoesMedicamentosas()
        self.verificador_doses = VerificadorDosesIA()
        self.analisador_contraindicacoes = AnalisadorContraindicacoes()

    async def validar_prescricao_completa(self, prescricao: dict) -> dict:
        """Validação completa com IA de prescrições médicas"""

        try:
            validacoes = {
                'dose_apropriada': await self.verificar_doses_personalizadas(prescricao),
                'interacoes': await self.detectar_interacoes_graves(prescricao),
                'contraindicacoes': await self.verificar_contraindicacoes(prescricao),
                'duplicidade_terapeutica': await self.detectar_duplicidades(prescricao),
                'alergias': await self.verificar_alergias_cruzadas(prescricao),
                'ajuste_renal': await self.calcular_ajuste_renal(prescricao),
                'ajuste_hepatico': await self.calcular_ajuste_hepatico(prescricao),
                'farmacogenetica': await self.analisar_polimorfismos_geneticos(prescricao)
            }

            score_seguranca = self.calcular_score_seguranca(validacoes)

            recomendacoes = await self.gerar_recomendacoes_farmaceuticas(validacoes)

            return {
                'validacoes': validacoes,
                'score_seguranca': score_seguranca,
                'recomendacoes': recomendacoes,
                'aprovacao_automatica': score_seguranca > 0.85,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erro na validação da prescrição: {e}")
            return {
                'error': str(e),
                'validacoes': {},
                'score_seguranca': 0.0,
                'aprovacao_automatica': False
            }

    async def verificar_doses_personalizadas(self, prescricao: dict) -> dict:
        """Verificação de doses com personalização por paciente"""

        paciente = prescricao.get('paciente', {})
        medicamentos = prescricao.get('medicamentos', [])

        verificacoes = []
        for med in medicamentos:
            dose_ideal = self.verificador_doses.calcular_dose_ideal(
                medicamento=med,
                peso=paciente.get('peso', 70),
                idade=paciente.get('idade', 50),
                clearance_creatinina=paciente.get('clearance', 90),
                superficie_corporal=self.calcular_superficie_corporal(paciente)
            )

            dose_prescrita = med.get('dose', 0)
            if dose_ideal > 0:
                variacao = abs(dose_prescrita - dose_ideal) / dose_ideal
            else:
                variacao = 0

            verificacoes.append({
                'medicamento': med.get('nome', ''),
                'dose_prescrita': dose_prescrita,
                'dose_ideal': dose_ideal,
                'variacao_percentual': variacao * 100,
                'dentro_limite': variacao < 0.2,  # 20% de variação aceitável
                'alerta': 'Dose fora do range terapêutico' if variacao > 0.2 else None
            })

        return {
            'verificacoes': verificacoes,
            'aprovado': all(v['dentro_limite'] for v in verificacoes)
        }

    def calcular_superficie_corporal(self, paciente: dict) -> float:
        """Calcula superfície corporal usando fórmula de Mosteller"""

        peso = paciente.get('peso', 70)
        altura = paciente.get('altura', 170)  # cm

        return ((peso * altura) / 3600) ** 0.5

    async def detectar_interacoes_graves(self, prescricao: dict) -> dict:
        """Detecta interações medicamentosas graves"""

        medicamentos = prescricao.get('medicamentos', [])
        interacoes_graves = []

        interacoes_db = {
            ('warfarina', 'aspirina'): 'Risco aumentado de sangramento',
            ('digoxina', 'amiodarona'): 'Aumento dos níveis de digoxina',
            ('varfarina', 'fluconazol'): 'Potencialização do efeito anticoagulante',
            ('enalapril', 'espironolactona'): 'Risco de hipercalemia',
            ('metformina', 'contraste_iodado'): 'Risco de acidose láctica',
            ('inibidores_ace', 'aines'): 'Redução da eficácia anti-hipertensiva',
            ('estatinas', 'fibratos'): 'Aumento do risco de miopatia',
            ('warfarina', 'antibioticos_macrolideos'): 'Potencialização anticoagulante',
            ('digoxina', 'diureticos_tiazidicos'): 'Hipocalemia aumenta toxicidade',
            ('litio', 'diureticos'): 'Aumento dos níveis de lítio',
            ('fenitoina', 'fluconazol'): 'Aumento dos níveis de fenitoína',
            ('ciclosporina', 'estatinas'): 'Aumento do risco de rabdomiólise',
            ('carbamazepina', 'claritromicina'): 'Aumento dos níveis de carbamazepina',
            ('teofilina', 'ciprofloxacino'): 'Aumento dos níveis de teofilina',
            ('metotrexato', 'aines'): 'Aumento da toxicidade do metotrexato',
            ('varfarina', 'amiodarona'): 'Potencialização significativa do efeito anticoagulante',
            ('insulina', 'beta_bloqueadores'): 'Mascaramento dos sintomas de hipoglicemia',
            ('digoxina', 'verapamil'): 'Aumento significativo dos níveis de digoxina',
            ('quinidina', 'digoxina'): 'Duplicação dos níveis de digoxina',
            ('rifampicina', 'varfarina'): 'Redução do efeito anticoagulante'
        }

        for i, med1 in enumerate(medicamentos):
            for med2 in medicamentos[i+1:]:
                nome1 = med1.get('nome', '').lower()
                nome2 = med2.get('nome', '').lower()

                chave = (nome1, nome2) if (nome1, nome2) in interacoes_db else (nome2, nome1)

                if chave in interacoes_db:
                    interacoes_graves.append({
                        'medicamento_1': med1.get('nome'),
                        'medicamento_2': med2.get('nome'),
                        'descricao': interacoes_db[chave],
                        'gravidade': 'alta'
                    })

        return {
            'interacoes_detectadas': interacoes_graves,
            'numero_interacoes': len(interacoes_graves),
            'aprovado': len(interacoes_graves) == 0
        }

    async def verificar_contraindicacoes(self, prescricao: dict) -> dict:
        """Verifica contraindicações baseadas no perfil do paciente"""

        paciente = prescricao.get('paciente', {})
        medicamentos = prescricao.get('medicamentos', [])

        contraindicacoes = []

        condicoes = paciente.get('condicoes_clinicas', [])

        for med in medicamentos:
            nome_med = med.get('nome', '').lower()

            if 'insuficiencia_renal' in condicoes and nome_med in ['metformina', 'atenolol']:
                contraindicacoes.append({
                    'medicamento': med.get('nome'),
                    'contraindicacao': 'Insuficiência renal',
                    'gravidade': 'alta',
                    'recomendacao': 'Ajustar dose ou substituir medicamento'
                })

            if 'asma' in condicoes and 'propranolol' in nome_med:
                contraindicacoes.append({
                    'medicamento': med.get('nome'),
                    'contraindicacao': 'Asma brônquica',
                    'gravidade': 'alta',
                    'recomendacao': 'Evitar beta-bloqueadores não seletivos'
                })

            if 'gravidez' in condicoes and nome_med in ['enalapril', 'warfarina']:
                contraindicacoes.append({
                    'medicamento': med.get('nome'),
                    'contraindicacao': 'Gravidez',
                    'gravidade': 'muito_alta',
                    'recomendacao': 'Substituir por alternativa segura na gravidez'
                })

        return {
            'contraindicacoes_detectadas': contraindicacoes,
            'numero_contraindicacoes': len(contraindicacoes),
            'aprovado': len(contraindicacoes) == 0
        }

    async def detectar_duplicidades(self, prescricao: dict) -> dict:
        """Detecta duplicidade terapêutica"""

        medicamentos = prescricao.get('medicamentos', [])
        duplicidades = []

        classes_terapeuticas = {}

        for med in medicamentos:
            classe = self.identificar_classe_terapeutica(med.get('nome', ''))
            if classe not in classes_terapeuticas:
                classes_terapeuticas[classe] = []
            classes_terapeuticas[classe].append(med)

        for classe, meds in classes_terapeuticas.items():
            if len(meds) > 1 and classe != 'outros':
                duplicidades.append({
                    'classe_terapeutica': classe,
                    'medicamentos': [med.get('nome') for med in meds],
                    'recomendacao': f'Revisar necessidade de múltiplos {classe}'
                })

        return {
            'duplicidades_detectadas': duplicidades,
            'numero_duplicidades': len(duplicidades),
            'aprovado': len(duplicidades) == 0
        }

    def identificar_classe_terapeutica(self, nome_medicamento: str) -> str:
        """Identifica classe terapêutica do medicamento"""

        nome = nome_medicamento.lower()

        classes = {
            'ieca': ['enalapril', 'captopril', 'lisinopril'],
            'bra': ['losartana', 'valsartana', 'telmisartana'],
            'beta_bloqueador': ['propranolol', 'atenolol', 'metoprolol'],
            'diuretico': ['furosemida', 'hidroclorotiazida', 'espironolactona'],
            'estatina': ['atorvastatina', 'sinvastatina', 'rosuvastatina'],
            'ibp': ['omeprazol', 'pantoprazol', 'esomeprazol'],
            'anticoagulante': ['warfarina', 'heparina', 'rivaroxabana']
        }

        for classe, medicamentos in classes.items():
            if any(med in nome for med in medicamentos):
                return classe

        return 'outros'

    async def verificar_alergias_cruzadas(self, prescricao: dict) -> dict:
        """Verifica alergias e reações cruzadas"""

        paciente = prescricao.get('paciente', {})
        medicamentos = prescricao.get('medicamentos', [])
        alergias = paciente.get('alergias', [])

        alertas_alergia = []

        for med in medicamentos:
            nome_med = med.get('nome', '').lower()

            for alergia in alergias:
                if alergia.lower() in nome_med:
                    alertas_alergia.append({
                        'medicamento': med.get('nome'),
                        'alergia': alergia,
                        'tipo': 'alergia_direta',
                        'gravidade': 'muito_alta'
                    })

            reacoes_cruzadas = self.verificar_reacoes_cruzadas(nome_med, alergias)
            alertas_alergia.extend(reacoes_cruzadas)

        return {
            'alertas_alergia': alertas_alergia,
            'numero_alertas': len(alertas_alergia),
            'aprovado': len(alertas_alergia) == 0
        }

    def verificar_reacoes_cruzadas(self, medicamento: str, alergias: list[str]) -> list[dict]:
        """Verifica reações cruzadas conhecidas"""

        reacoes_cruzadas = []

        if 'penicilina' in alergias:
            if any(beta_lactam in medicamento for beta_lactam in ['amoxicilina', 'ampicilina']):
                reacoes_cruzadas.append({
                    'medicamento': medicamento,
                    'alergia': 'penicilina',
                    'tipo': 'reacao_cruzada',
                    'gravidade': 'alta',
                    'descricao': 'Possível reação cruzada com beta-lactâmicos'
                })

        return reacoes_cruzadas

    async def calcular_ajuste_renal(self, prescricao: dict) -> dict:
        """Calcula ajustes de dose para função renal"""

        paciente = prescricao.get('paciente', {})
        medicamentos = prescricao.get('medicamentos', [])
        clearance = paciente.get('clearance_creatinina', 90)

        ajustes_necessarios = []

        medicamentos_ajuste_renal = {
            'metformina': {'clearance_minimo': 30, 'ajuste': 'contraindicado se < 30'},
            'atenolol': {'clearance_minimo': 50, 'ajuste': 'reduzir dose 50% se < 50'},
            'digoxina': {'clearance_minimo': 60, 'ajuste': 'reduzir dose 25% se < 60'},
            'gabapentina': {'clearance_minimo': 60, 'ajuste': 'ajustar conforme clearance'}
        }

        for med in medicamentos:
            nome_med = med.get('nome', '').lower()

            for med_ajuste, criterios in medicamentos_ajuste_renal.items():
                if med_ajuste in nome_med:
                    if clearance < criterios['clearance_minimo']:
                        ajustes_necessarios.append({
                            'medicamento': med.get('nome'),
                            'clearance_atual': clearance,
                            'clearance_minimo': criterios['clearance_minimo'],
                            'ajuste_recomendado': criterios['ajuste']
                        })

        return {
            'ajustes_necessarios': ajustes_necessarios,
            'numero_ajustes': len(ajustes_necessarios),
            'aprovado': len(ajustes_necessarios) == 0
        }

    async def calcular_ajuste_hepatico(self, prescricao: dict) -> dict:
        """Calcula ajustes de dose para função hepática"""

        paciente = prescricao.get('paciente', {})
        medicamentos = prescricao.get('medicamentos', [])

        tem_hepatopatia = 'hepatopatia' in paciente.get('condicoes_clinicas', [])

        ajustes_hepaticos = []

        if tem_hepatopatia:
            medicamentos_hepatotoxicos = ['paracetamol', 'sinvastatina', 'fluconazol']

            for med in medicamentos:
                nome_med = med.get('nome', '').lower()

                if any(hepato in nome_med for hepato in medicamentos_hepatotoxicos):
                    ajustes_hepaticos.append({
                        'medicamento': med.get('nome'),
                        'motivo': 'Hepatopatia presente',
                        'recomendacao': 'Reduzir dose ou monitorar função hepática'
                    })

        return {
            'ajustes_hepaticos': ajustes_hepaticos,
            'numero_ajustes': len(ajustes_hepaticos),
            'aprovado': len(ajustes_hepaticos) == 0
        }

    async def analisar_polimorfismos_geneticos(self, prescricao: dict) -> dict:
        """Análise farmacogenética baseada em diretrizes CPIC atualizadas"""

        paciente = prescricao.get('paciente', {})
        medicamentos = prescricao.get('medicamentos', [])

        polimorfismos = paciente.get('polimorfismos_geneticos', {})

        recomendacoes_geneticas = []

        for med in medicamentos:
            nome_med = med.get('nome', '').lower()

            if 'warfarina' in nome_med:
                if polimorfismos.get('CYP2C9') == 'metabolizador_lento':
                    recomendacoes_geneticas.append({
                        'medicamento': med.get('nome'),
                        'gene': 'CYP2C9',
                        'polimorfismo': 'metabolizador_lento',
                        'recomendacao': 'Iniciar com dose reduzida (2.5mg/dia) - CPIC Guidelines',
                        'evidencia': 'Nível 1A'
                    })
                if polimorfismos.get('VKORC1') == 'AA':
                    recomendacoes_geneticas.append({
                        'medicamento': med.get('nome'),
                        'gene': 'VKORC1',
                        'polimorfismo': 'AA',
                        'recomendacao': 'Paciente sensível à warfarina, iniciar com 2.5mg/dia',
                        'evidencia': 'Nível 1A'
                    })

            if 'clopidogrel' in nome_med:
                if polimorfismos.get('CYP2C19') == 'metabolizador_lento':
                    recomendacoes_geneticas.append({
                        'medicamento': med.get('nome'),
                        'gene': 'CYP2C19',
                        'polimorfismo': 'metabolizador_lento',
                        'recomendacao': 'Considerar alternativa (prasugrel ou ticagrelor) - ESC/AHA Guidelines',
                        'evidencia': 'Nível 1A'
                    })

            if 'abacavir' in nome_med:
                if polimorfismos.get('HLA_B5701') == 'positivo':
                    recomendacoes_geneticas.append({
                        'medicamento': med.get('nome'),
                        'gene': 'HLA-B*5701',
                        'polimorfismo': 'positivo',
                        'recomendacao': 'CONTRAINDICAÇÃO ABSOLUTA - risco de reação de hipersensibilidade',
                        'evidencia': 'Nível 1A',
                        'gravidade': 'muito_alta'
                    })

            if 'carbamazepina' in nome_med:
                if polimorfismos.get('HLA_B1502') == 'positivo':
                    recomendacoes_geneticas.append({
                        'medicamento': med.get('nome'),
                        'gene': 'HLA-B*1502',
                        'polimorfismo': 'positivo',
                        'recomendacao': 'Risco de síndrome de Stevens-Johnson, evitar carbamazepina',
                        'evidencia': 'Nível 1A',
                        'gravidade': 'alta'
                    })

            if 'simvastatina' in nome_med:
                if polimorfismos.get('SLCO1B1') == '*5/*5':
                    recomendacoes_geneticas.append({
                        'medicamento': med.get('nome'),
                        'gene': 'SLCO1B1',
                        'polimorfismo': '*5/*5',
                        'recomendacao': 'Risco aumentado de miopatia, considerar atorvastatina - CPIC Guidelines',
                        'evidencia': 'Nível 1A'
                    })

        return {
            'recomendacoes_geneticas': recomendacoes_geneticas,
            'numero_recomendacoes': len(recomendacoes_geneticas),
            'aprovado': not any(rec.get('gravidade') == 'muito_alta' for rec in recomendacoes_geneticas),
            'diretrizes_aplicadas': ['CPIC', 'PharmGKB', 'ESC', 'AHA']
        }

    def calcular_score_seguranca(self, validacoes: dict) -> float:
        """Calcula score global de segurança da prescrição"""

        scores = []
        pesos = {
            'dose_apropriada': 0.2,
            'interacoes': 0.2,
            'contraindicacoes': 0.25,
            'duplicidade_terapeutica': 0.1,
            'alergias': 0.15,
            'ajuste_renal': 0.05,
            'ajuste_hepatico': 0.05
        }

        for categoria, validacao in validacoes.items():
            if categoria in pesos:
                aprovado = validacao.get('aprovado', False)
                score_categoria = 1.0 if aprovado else 0.0
                scores.append(score_categoria * pesos[categoria])

        return sum(scores)

    async def gerar_recomendacoes_farmaceuticas(self, validacoes: dict) -> list[str]:
        """Gera recomendações farmacêuticas baseadas nas validações"""

        recomendacoes = []

        if not validacoes.get('dose_apropriada', {}).get('aprovado', True):
            recomendacoes.append('Revisar doses prescritas conforme peso e função renal')

        if not validacoes.get('interacoes', {}).get('aprovado', True):
            recomendacoes.append('Monitorar paciente para sinais de interações medicamentosas')

        if not validacoes.get('contraindicacoes', {}).get('aprovado', True):
            recomendacoes.append('Avaliar contraindicações identificadas antes da dispensação')

        if not validacoes.get('alergias', {}).get('aprovado', True):
            recomendacoes.append('ATENÇÃO: Possível alergia ou reação cruzada identificada')

        if validacoes.get('ajuste_renal', {}).get('numero_ajustes', 0) > 0:
            recomendacoes.append('Ajustar doses conforme função renal do paciente')

        return recomendacoes


class ModeloInteracoesMedicamentosas:
    pass


class VerificadorDosesIA:
    def calcular_dose_ideal(self, medicamento: dict, peso: float, idade: int, clearance_creatinina: float, superficie_corporal: float) -> float:
        """Calcula dose ideal baseada nos parâmetros do paciente"""

        nome = medicamento.get('nome', '').lower()
        dose_base = medicamento.get('dose', 0)

        if 'digoxina' in nome:
            dose_ideal = 0.25 if idade > 65 else 0.5
            if clearance_creatinina < 60:
                dose_ideal *= 0.75
        elif 'warfarina' in nome:
            dose_ideal = 5.0 if idade < 65 else 2.5
        elif 'atenolol' in nome:
            dose_ideal = peso * 0.5  # 0.5mg/kg
            if clearance_creatinina < 50:
                dose_ideal *= 0.5
        else:
            dose_ideal = dose_base
            if peso < 50:
                dose_ideal *= 0.8
            elif peso > 100:
                dose_ideal *= 1.2

        return max(0, dose_ideal)


class AnalisadorContraindicacoes:
    pass
