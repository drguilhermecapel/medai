import React, { useState } from 'react'
import {
  Activity,
  FileText,
  FlaskConical,
  Brain,
  AlertCircle,
  CheckCircle,
  TrendingUp,
  User,
  Pill,
  ClipboardList,
  Sparkles,
  ChevronRight,
  Download,
  Send,
  RefreshCw,
} from 'lucide-react'

interface Diagnostico {
  cid: string
  descricao: string
  probabilidade: number
  gravidade: string
  diasAfastamentoBase: number
}

interface Medicamento {
  nome: string
  dose: string
  via: string
  frequencia: string
  duracao: number
  orientacoes: string[]
}

interface Exame {
  nome: string
  justificativa: string
  prioridade: string
}

interface ResultadosIA {
  diagnosticos: Diagnostico[]
  prescricao: {
    medicamentos: Medicamento[]
    alertas: string[]
  }
  exames: {
    laboratoriais: Exame[]
    imagem: Exame[]
  }
  atestado: {
    dias: number
    dataInicio: Date
    dataFim: Date
    justificativa: string
    cid: string
  }
}

const InterfaceAutomacaoMedica = (): React.ReactElement => {
  const [resultadosIA, setResultadosIA] = useState<ResultadosIA | null>(null)
  const [processando, setProcessando] = useState(false)
  const [etapaProcessamento, setEtapaProcessamento] = useState('')
  const [tabAtiva, setTabAtiva] = useState('diagnosticos')

  const processarConsulta = async (): Promise<void> => {
    setProcessando(true)

    const etapas = [
      'Analisando sintomas com IA...',
      'Identificando diagnósticos possíveis...',
      'Gerando prescrição personalizada...',
      'Selecionando exames necessários...',
      'Calculando dias de afastamento...']

    for (const etapa of etapas) {
      setEtapaProcessamento(etapa)
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    setResultadosIA({
      diagnosticos: [
        {
          cid: 'J15.9',
          descricao: 'Pneumonia bacteriana não especificada',
          probabilidade: 0.87,
          gravidade: 'MODERADA',
          diasAfastamentoBase: 7,
        },
        {
          cid: 'J20.9',
          descricao: 'Bronquite aguda não especificada',
          probabilidade: 0.65,
          gravidade: 'LEVE',
          diasAfastamentoBase: 5,
        },
        {
          cid: 'J06.9',
          descricao: 'Infecção aguda das vias aéreas superiores',
          probabilidade: 0.43,
          gravidade: 'LEVE',
          diasAfastamentoBase: 3,
        }],
      prescricao: {
        medicamentos: [
          {
            nome: 'Amoxicilina + Clavulanato',
            dose: '875mg + 125mg',
            via: 'Oral',
            frequencia: '12/12h',
            duracao: 7,
            orientacoes: ['Tomar com alimentos', 'Completar todo o ciclo'],
          },
          {
            nome: 'Dipirona',
            dose: '500mg',
            via: 'Oral',
            frequencia: '6/6h se dor ou febre',
            duracao: 5,
            orientacoes: ['Máximo 4 doses/dia'],
          },
          {
            nome: 'Acetilcisteína',
            dose: '600mg',
            via: 'Oral',
            frequencia: '1x/dia',
            duracao: 7,
            orientacoes: ['Dissolver em água', 'Tomar pela manhã'],
          }],
        alertas: ['Paciente alérgico a Penicilina - Alternativa selecionada'],
      },
      exames: {
        laboratoriais: [
          {
            nome: 'Hemograma Completo',
            justificativa: 'Avaliação de processo infeccioso',
            prioridade: 'Normal',
          },
          {
            nome: 'PCR',
            justificativa: 'Marcador inflamatório',
            prioridade: 'Normal',
          }],
        imagem: [
          {
            nome: 'Radiografia de Tórax PA/Perfil',
            justificativa: 'Avaliação de consolidação pulmonar',
            prioridade: 'Urgente',
          }],
      },
      atestado: {
        dias: 10,
        dataInicio: new Date(),
        dataFim: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000),
        justificativa:
          'Período estendido devido a: idade avançada (45 anos), presença de comorbidades (hipertensão, diabetes), gravidade moderada do quadro respiratório. Necessário repouso para recuperação adequada.',
        cid: 'J15.9',
      },
    })

    setProcessando(false)
    setEtapaProcessamento('')
  }

  const ConsultaForm = (): React.ReactElement => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <User className="w-5 h-5 mr-2 text-blue-600" />
        Dados da Consulta
      </h3>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Paciente</label>
          <div className="p-3 bg-gray-50 rounded">
            <p className="font-medium">João Silva</p>
            <p className="text-sm text-gray-600">45 anos, Masculino</p>
            <p className="text-xs text-red-600 mt-1">⚠️ Alérgico: Penicilina</p>
            <p className="text-xs text-gray-600">Comorbidades: Hipertensão, Diabetes</p>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Sinais Vitais</label>
          <div className="p-3 bg-gray-50 rounded space-y-1 text-sm">
            <p>
              Temp: <span className="font-medium text-red-600">38.2°C</span>
            </p>
            <p>
              PA: <span className="font-medium">130/85 mmHg</span>
            </p>
            <p>
              FC: <span className="font-medium">95 bpm</span>
            </p>
            <p>
              SpO2: <span className="font-medium text-yellow-600">94%</span>
            </p>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Queixa Principal</label>
        <div className="p-3 bg-gray-50 rounded">
          <p className="text-sm">Tosse há 5 dias com febre</p>
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          História da Doença Atual
        </label>
        <div className="p-3 bg-gray-50 rounded">
          <p className="text-sm">
            Paciente relata tosse produtiva com expectoração amarelada, febre de 38.5°C, mal-estar
            geral. Nega dispneia importante.
          </p>
        </div>
      </div>

      <button
        onClick={processarConsulta}
        disabled={processando}
        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium py-3 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {processando ? (
          <>
            <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
            {etapaProcessamento}
          </>
        ) : (
          <>
            <Brain className="w-5 h-5 mr-2" />
            Processar com Inteligência Artificial
          </>
        )}
      </button>
    </div>
  )

  const ResultadosIA = (): React.ReactElement | null => {
    if (!resultadosIA) return null

    return (
      <div className="mt-6">
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <Sparkles className="w-6 h-6 text-purple-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-800">Análise Completa por IA</h3>
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Sistema processou automaticamente diagnósticos, prescrição, exames e atestado
          </p>
        </div>

        <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setTabAtiva('diagnosticos')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
              tabAtiva === 'diagnosticos'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Brain className="w-4 h-4 inline mr-1" />
            Diagnósticos
          </button>
          <button
            onClick={() => setTabAtiva('prescricao')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
              tabAtiva === 'prescricao'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Pill className="w-4 h-4 inline mr-1" />
            Prescrição
          </button>
          <button
            onClick={() => setTabAtiva('exames')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
              tabAtiva === 'exames'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <FlaskConical className="w-4 h-4 inline mr-1" />
            Exames
          </button>
          <button
            onClick={() => setTabAtiva('atestado')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
              tabAtiva === 'atestado'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-1" />
            Atestado
          </button>
        </div>

        {tabAtiva === 'diagnosticos' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h4 className="font-semibold mb-4 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-purple-600" />
              Diagnósticos Sugeridos por IA
            </h4>
            <div className="space-y-3">
              {resultadosIA.diagnosticos.map((diag, idx) => (
                <div key={idx} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <span className="font-medium text-gray-900">{diag.cid}</span>
                        <span className="mx-2 text-gray-400">|</span>
                        <span className="text-gray-700">{diag.descricao}</span>
                      </div>
                      <div className="mt-2 flex items-center space-x-4">
                        <div className="flex items-center">
                          <TrendingUp className="w-4 h-4 mr-1 text-blue-500" />
                          <span className="text-sm text-gray-600">
                            Probabilidade: {(diag.probabilidade * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="flex items-center">
                          <Activity className="w-4 h-4 mr-1 text-orange-500" />
                          <span
                            className={`text-sm font-medium ${
                              diag.gravidade === 'GRAVE'
                                ? 'text-red-600'
                                : diag.gravidade === 'MODERADA'
                                  ? 'text-orange-600'
                                  : 'text-green-600'
                            }`}
                          >
                            {diag.gravidade}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-center bg-gray-50 rounded px-3 py-2">
                        <p className="text-xs text-gray-500">Afastamento base</p>
                        <p className="text-lg font-semibold text-gray-800">
                          {diag.diasAfastamentoBase} dias
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-2 bg-blue-50 rounded p-2">
                    <p className="text-xs text-blue-700">
                      <span className="font-medium">IA analisou:</span> sintomas, sinais vitais,
                      histórico e padrões epidemiológicos
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {tabAtiva === 'prescricao' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h4 className="font-semibold mb-4 flex items-center">
              <Pill className="w-5 h-5 mr-2 text-blue-600" />
              Prescrição Gerada Automaticamente
            </h4>

            {resultadosIA.prescricao.alertas.length > 0 && (
              <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0" />
                  <div>
                    {resultadosIA.prescricao.alertas.map((alerta, idx) => (
                      <p key={idx} className="text-sm text-red-700">
                        {alerta}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-3">
              {resultadosIA.prescricao.medicamentos.map((med, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h5 className="font-medium text-gray-900">{med.nome}</h5>
                      <div className="mt-1 text-sm text-gray-600">
                        <p>
                          {med.dose} - {med.via}
                        </p>
                        <p className="font-medium text-blue-600">
                          {med.frequencia} por {med.duracao} dias
                        </p>
                      </div>
                      <div className="mt-2">
                        {med.orientacoes.map((orientacao, oIdx) => (
                          <p key={oIdx} className="text-xs text-gray-500 flex items-center">
                            <CheckCircle className="w-3 h-3 mr-1 text-green-500" />
                            {orientacao}
                          </p>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 bg-blue-50 rounded-lg p-3">
              <p className="text-sm text-blue-700">
                <span className="font-medium">IA considerou:</span> diagnóstico principal, alergias,
                função renal/hepática, interações medicamentosas e protocolos clínicos
              </p>
            </div>
          </div>
        )}

        {tabAtiva === 'exames' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h4 className="font-semibold mb-4 flex items-center">
              <FlaskConical className="w-5 h-5 mr-2 text-green-600" />
              Exames Selecionados por IA
            </h4>

            <div className="mb-4">
              <h5 className="font-medium text-gray-700 mb-2">Exames Laboratoriais</h5>
              <div className="space-y-2">
                {resultadosIA.exames.laboratoriais.map((exame, idx) => (
                  <div key={idx} className="border rounded-lg p-3">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">{exame.nome}</p>
                        <p className="text-sm text-gray-600">{exame.justificativa}</p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          exame.prioridade === 'Urgente'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {exame.prioridade}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h5 className="font-medium text-gray-700 mb-2">Exames de Imagem</h5>
              <div className="space-y-2">
                {resultadosIA.exames.imagem.map((exame, idx) => (
                  <div key={idx} className="border rounded-lg p-3">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">{exame.nome}</p>
                        <p className="text-sm text-gray-600">{exame.justificativa}</p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          exame.prioridade === 'Urgente'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {exame.prioridade}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 bg-green-50 rounded-lg p-3">
              <p className="text-sm text-green-700">
                <span className="font-medium">IA otimizou:</span> custo-benefício, protocolos
                clínicos e priorização por gravidade
              </p>
            </div>
          </div>
        )}

        {tabAtiva === 'atestado' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h4 className="font-semibold mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2 text-orange-600" />
              Atestado Médico Calculado por IA
            </h4>

            <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-4 mb-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">Dias de Afastamento</p>
                <p className="text-4xl font-bold text-orange-600 mt-1">
                  {resultadosIA.atestado.dias} dias
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  {resultadosIA.atestado.dataInicio.toLocaleDateString('pt-BR')} a{' '}
                  {resultadosIA.atestado.dataFim.toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-700">CID-10</p>
                <p className="text-gray-900">{resultadosIA.atestado.cid}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-700">Justificativa Médica</p>
                <div className="mt-1 p-3 bg-gray-50 rounded text-sm text-gray-800">
                  {resultadosIA.atestado.justificativa}
                </div>
              </div>

              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-sm text-blue-700">
                  <span className="font-medium">IA analisou:</span> gravidade do quadro, idade
                  (fator 1.2x), comorbidades (fator 1.4x), tipo de trabalho e protocolos de
                  afastamento por CID
                </p>
              </div>
            </div>

            <div className="mt-4 flex space-x-3">
              <button className="flex-1 bg-orange-600 text-white py-2 px-4 rounded-lg hover:bg-orange-700 transition-colors flex items-center justify-center">
                <Download className="w-4 h-4 mr-2" />
                Gerar PDF
              </button>
              <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center">
                <Send className="w-4 h-4 mr-2" />
                Enviar eSocial
              </button>
            </div>
          </div>
        )}

        <div className="mt-6 bg-gray-50 rounded-lg p-4">
          <h4 className="font-semibold mb-3 flex items-center">
            <ClipboardList className="w-5 h-5 mr-2 text-gray-600" />
            Próximos Passos Sugeridos
          </h4>
          <div className="space-y-2">
            <div className="flex items-center text-sm">
              <ChevronRight className="w-4 h-4 mr-2 text-gray-400" />
              <span>Retorno em 7-10 dias para avaliação da evolução</span>
            </div>
            <div className="flex items-center text-sm">
              <ChevronRight className="w-4 h-4 mr-2 text-gray-400" />
              <span>Avaliar resultado da Radiografia de Tórax (prioridade urgente)</span>
            </div>
            <div className="flex items-center text-sm">
              <ChevronRight className="w-4 h-4 mr-2 text-gray-400" />
              <span>Monitorar adesão ao tratamento antibiótico</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Brain className="w-8 h-8 mr-3 text-purple-600" />
            MedIA Pro - Automação Médica Inteligente
          </h1>
          <p className="text-gray-600 mt-2">
            Sistema integrado de diagnóstico, prescrição, exames e atestados por IA
          </p>
        </div>

        <ConsultaForm />

        <ResultadosIA />
      </div>
    </div>
  )
}

export default InterfaceAutomacaoMedica
