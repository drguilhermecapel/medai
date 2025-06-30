"""
Sistema de Diretrizes Médicas com Inteligência Artificial
Integração otimizada para o sistema medai seguindo as diretrizes médicas mais atuais
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

class GuidelineSource(Enum):
    """Fontes de diretrizes médicas integradas"""
    AMB = "Associação Médica Brasileira"
    CFM = "Conselho Federal de Medicina"
    SBC = "Sociedade Brasileira de Cardiologia"
    SBD = "Sociedade Brasileira de Diabetes"
    SBOC = "Sociedade Brasileira de Oncologia Clínica"
    SBP = "Sociedade Brasileira de Pediatria"
    FEBRASGO = "Federação Brasileira de Ginecologia e Obstetrícia"
    MS_PCDT = "Protocolos Clínicos MS"

    WHO = "World Health Organization"
    UPTODATE = "UpToDate"
    COCHRANE = "Cochrane Database"
    NICE = "National Institute for Health and Care Excellence"
    AHA = "American Heart Association"
    ADA = "American Diabetes Association"
    NCCN = "National Comprehensive Cancer Network"
    KDIGO = "Kidney Disease Improving Global Outcomes"

@dataclass
class DiretrizMedica:
    """Estrutura de uma diretriz médica"""
    id: str
    titulo: str
    especialidade: str
    fonte: GuidelineSource
    versao: str
    data_atualizacao: datetime
    nivel_evidencia: str
    grau_recomendacao: str
    conteudo: dict[str, Any]
    referencias: list[str]
    conflitos_interesse: str | None = None

class MotorDiretrizesMedicasIA:
    """Motor principal de diretrizes médicas com IA para medai"""

    def __init__(self):
        self.diretrizes_cache: dict[str, DiretrizMedica] = {}
        self.diretrizes_por_condicao: dict[str, list[str]] = {}
        self._inicializar_diretrizes_basicas()

    def _inicializar_diretrizes_basicas(self):
        """Inicializa diretrizes básicas para condições comuns"""

        diabetes_diretriz = DiretrizMedica(
            id="DM2_SBD_2023",
            titulo="Diretrizes da Sociedade Brasileira de Diabetes 2023-2024",
            especialidade="endocrinologia",
            fonte=GuidelineSource.SBD,
            versao="2023-2024",
            data_atualizacao=datetime(2023, 12, 1),
            nivel_evidencia="A",
            grau_recomendacao="I",
            conteudo={
                "primeira_linha": {
                    "medicamentos": ["metformina"],
                    "dose_inicial": "500mg 2x/dia",
                    "titulacao": "Aumentar 500mg/semana até 2000mg/dia",
                    "meta_hba1c": "<7%",
                    "contraindicacoes": ["TFG <30 mL/min/1.73m²", "acidose metabólica"]
                },
                "segunda_linha": {
                    "opcoes": ["sulfoniluréia", "iDPP4", "iSGLT2", "agonista_GLP1"],
                    "criterios_escolha": {
                        "cardiovascular_alto_risco": "iSGLT2 ou agonista_GLP1",
                        "insuficiencia_cardiaca": "iSGLT2",
                        "doenca_renal_cronica": "iSGLT2 ou agonista_GLP1"
                    }
                },
                "monitoramento": {
                    "hba1c": "3-6 meses",
                    "funcao_renal": "anual ou conforme indicação",
                    "lipidograma": "anual",
                    "microalbuminuria": "anual"
                }
            },
            referencias=[
                "Diretrizes da Sociedade Brasileira de Diabetes 2023-2024",
                "Posicionamento Oficial SBD nº 01/2023"
            ]
        )

        has_diretriz = DiretrizMedica(
            id="HAS_SBC_2020",
            titulo="7ª Diretriz Brasileira de Hipertensão Arterial",
            especialidade="cardiologia",
            fonte=GuidelineSource.SBC,
            versao="2020",
            data_atualizacao=datetime(2020, 9, 1),
            nivel_evidencia="A",
            grau_recomendacao="I",
            conteudo={
                "primeira_linha": {
                    "medicamentos": ["IECA", "BRA", "diurético_tiazídico", "bloqueador_canal_cálcio"],
                    "monoterapia": "PA <150/90 mmHg em idosos, <140/90 em adultos",
                    "terapia_combinada": "PA ≥160/100 ou PA ≥140/90 com risco cardiovascular alto"
                },
                "combinacoes_preferenciais": [
                    "IECA + diurético",
                    "BRA + diurético",
                    "IECA + bloqueador_canal_cálcio",
                    "BRA + bloqueador_canal_cálcio"
                ],
                "metas": {
                    "adultos": "<140/90 mmHg",
                    "idosos": "<150/90 mmHg",
                    "diabetes": "<130/80 mmHg",
                    "doenca_renal": "<130/80 mmHg"
                }
            },
            referencias=[
                "Arq Bras Cardiol. 2021; 116(4):635-659",
                "7ª Diretriz Brasileira de Hipertensão Arterial"
            ]
        )

        self.diretrizes_cache["DM2_SBD_2023"] = diabetes_diretriz
        self.diretrizes_cache["HAS_SBC_2020"] = has_diretriz

        self.diretrizes_por_condicao = {
            "diabetes_mellitus_tipo_2": ["DM2_SBD_2023"],
            "diabetes_tipo_2": ["DM2_SBD_2023"],
            "dm2": ["DM2_SBD_2023"],
            "hipertensao_arterial": ["HAS_SBC_2020"],
            "hipertensao": ["HAS_SBC_2020"],
            "has": ["HAS_SBC_2020"]
        }

    async def obter_diretriz_para_condicao(self,
                                          condicao: str,
                                          contexto_paciente: dict[str, Any]) -> DiretrizMedica | None:
        """Obtém a melhor diretriz para uma condição específica"""
        try:
            condicao_normalizada = condicao.lower().replace(" ", "_")

            if condicao_normalizada in self.diretrizes_por_condicao:
                diretriz_ids = self.diretrizes_por_condicao[condicao_normalizada]

                if diretriz_ids:
                    return self.diretrizes_cache.get(diretriz_ids[0])

            logger.warning(f"Nenhuma diretriz encontrada para condição: {condicao}")
            return None

        except Exception as e:
            logger.error(f"Erro ao obter diretriz para condição {condicao}: {str(e)}")
            return None

    async def validar_prescricao_contra_diretrizes(self,
                                                  prescricao: dict[str, Any],
                                                  diagnostico: str) -> dict[str, Any]:
        """Valida prescrição contra diretrizes médicas"""
        try:
            diretriz = await self.obter_diretriz_para_condicao(diagnostico, {})

            if not diretriz:
                return {
                    "conformidade": 0.0,
                    "status": "sem_diretriz",
                    "alertas": [f"Nenhuma diretriz encontrada para {diagnostico}"],
                    "recomendacoes": []
                }

            medicamentos_prescritos = [med.get("name", "").lower() for med in prescricao.get("medications", [])]

            primeira_linha = diretriz.conteudo.get("primeira_linha", {})
            medicamentos_primeira_linha = primeira_linha.get("medicamentos", [])

            conformidade_score = 0.0
            alertas = []
            recomendacoes = []

            medicamentos_conformes = []
            for med_prescrito in medicamentos_prescritos:
                for med_diretriz in medicamentos_primeira_linha:
                    if med_diretriz.lower() in med_prescrito or med_prescrito in med_diretriz.lower():
                        medicamentos_conformes.append(med_prescrito)
                        break

            if medicamentos_conformes:
                conformidade_score = len(medicamentos_conformes) / len(medicamentos_prescritos)
            else:
                alertas.append("Nenhum medicamento de primeira linha conforme diretrizes foi prescrito")
                recomendacoes.append(f"Considerar medicamentos de primeira linha: {', '.join(medicamentos_primeira_linha)}")

            if conformidade_score >= 0.8:
                status = "conforme"
            elif conformidade_score >= 0.5:
                status = "parcialmente_conforme"
            else:
                status = "nao_conforme"

            return {
                "conformidade": round(conformidade_score * 100, 1),
                "status": status,
                "alertas": alertas,
                "recomendacoes": recomendacoes,
                "diretriz_aplicada": {
                    "id": diretriz.id,
                    "titulo": diretriz.titulo,
                    "fonte": diretriz.fonte.value,
                    "nivel_evidencia": diretriz.nivel_evidencia
                },
                "medicamentos_conformes": medicamentos_conformes
            }

        except Exception as e:
            logger.error(f"Erro na validação contra diretrizes: {str(e)}")
            return {
                "conformidade": 0.0,
                "status": "erro",
                "alertas": [f"Erro na validação: {str(e)}"],
                "recomendacoes": []
            }

class SolicitacaoExamesBaseadaDiretrizes:
    """Sistema para solicitar exames seguindo protocolos atualizados"""

    def __init__(self):
        self.protocolos_exames = self._inicializar_protocolos()

    def _inicializar_protocolos(self) -> dict[str, dict[str, Any]]:
        """Inicializa protocolos de exames por condição"""
        return {
            "diabetes_mellitus_tipo_2": {
                "exames_iniciais": [
                    {
                        "nome": "Hemoglobina Glicada (HbA1c)",
                        "justificativa": "Avaliação do controle glicêmico nos últimos 2-3 meses",
                        "periodicidade": "3-6 meses",
                        "meta": "<7% para maioria dos adultos"
                    },
                    {
                        "nome": "Glicemia de Jejum",
                        "justificativa": "Avaliação complementar do controle glicêmico",
                        "periodicidade": "Conforme indicação clínica"
                    },
                    {
                        "nome": "Creatinina e TFG",
                        "justificativa": "Avaliação da função renal",
                        "periodicidade": "Anual ou conforme indicação"
                    },
                    {
                        "nome": "Microalbuminúria",
                        "justificativa": "Rastreamento de nefropatia diabética",
                        "periodicidade": "Anual"
                    }
                ],
                "exames_complementares": [
                    {
                        "nome": "Lipidograma",
                        "justificativa": "Avaliação do risco cardiovascular",
                        "periodicidade": "Anual"
                    },
                    {
                        "nome": "Fundoscopia",
                        "justificativa": "Rastreamento de retinopatia diabética",
                        "periodicidade": "Anual"
                    }
                ]
            },
            "hipertensao_arterial": {
                "exames_iniciais": [
                    {
                        "nome": "ECG de Repouso",
                        "justificativa": "Avaliação de lesão de órgão-alvo cardíaco",
                        "periodicidade": "Inicial e conforme indicação"
                    },
                    {
                        "nome": "Creatinina e TFG",
                        "justificativa": "Avaliação da função renal",
                        "periodicidade": "Anual"
                    },
                    {
                        "nome": "Potássio sérico",
                        "justificativa": "Avaliação eletrolítica, especialmente com diuréticos",
                        "periodicidade": "Conforme medicação"
                    }
                ],
                "exames_complementares": [
                    {
                        "nome": "Ecocardiograma",
                        "justificativa": "Avaliação de hipertrofia ventricular esquerda",
                        "periodicidade": "Conforme indicação clínica"
                    },
                    {
                        "nome": "Microalbuminúria",
                        "justificativa": "Avaliação de lesão renal precoce",
                        "periodicidade": "Anual em casos selecionados"
                    }
                ]
            }
        }

    async def sugerir_exames(self,
                            diagnostico: str,
                            contexto_clinico: dict[str, Any]) -> dict[str, Any]:
        """Sugere exames baseados em protocolos atualizados"""
        try:
            diagnostico_normalizado = diagnostico.lower().replace(" ", "_")

            if diagnostico_normalizado not in self.protocolos_exames:
                return {
                    "exames_essenciais": [],
                    "exames_complementares": [],
                    "justificativas": [],
                    "alertas": [f"Protocolo não encontrado para {diagnostico}"]
                }

            protocolo = self.protocolos_exames[diagnostico_normalizado]

            return {
                "exames_essenciais": protocolo.get("exames_iniciais", []),
                "exames_complementares": protocolo.get("exames_complementares", []),
                "justificativas": self._gerar_justificativas_baseadas_evidencia(protocolo),
                "alertas": [],
                "protocolo_aplicado": diagnostico_normalizado
            }

        except Exception as e:
            logger.error(f"Erro ao sugerir exames: {str(e)}")
            return {
                "exames_essenciais": [],
                "exames_complementares": [],
                "justificativas": [],
                "alertas": [f"Erro ao processar sugestão: {str(e)}"]
            }

    def _gerar_justificativas_baseadas_evidencia(self, protocolo: dict[str, Any]) -> list[str]:
        """Gera justificativas baseadas em evidências"""
        justificativas = []

        for exame in protocolo.get("exames_iniciais", []):
            justificativas.append(f"{exame['nome']}: {exame['justificativa']}")

        return justificativas

class ValidadorConformidadeDiretrizes:
    """Valida se as ações médicas seguem diretrizes atualizadas"""

    def __init__(self):
        self.motor_diretrizes = MotorDiretrizesMedicasIA()

    async def validar_acao_medica(self,
                                  acao: dict[str, Any],
                                  tipo_acao: str,
                                  diagnostico: str = "") -> dict[str, Any]:
        """Valida qualquer ação médica contra diretrizes"""
        try:
            if tipo_acao == "prescricao":
                return await self.motor_diretrizes.validar_prescricao_contra_diretrizes(
                    acao, diagnostico
                )

            return {
                "conformidade": 100.0,
                "status": "nao_implementado",
                "alertas": [f"Validação para {tipo_acao} ainda não implementada"],
                "recomendacoes": []
            }

        except Exception as e:
            logger.error(f"Erro na validação de ação médica: {str(e)}")
            return {
                "conformidade": 0.0,
                "status": "erro",
                "alertas": [f"Erro na validação: {str(e)}"],
                "recomendacoes": []
            }

MedicalGuidelinesEngine = MotorDiretrizesMedicasIA
