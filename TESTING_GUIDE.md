# Guia de Implementação de Testes - MedAI

## Visão Geral

Este guia fornece instruções detalhadas para implementar e manter a estratégia de testes abrangente do MedAI, garantindo 80% de cobertura global e 100% nos componentes críticos.

## Estrutura de Testes

### Backend (Python/FastAPI)

#### Configuração Inicial

1. **Instalar Dependências de Teste**
```bash
cd backend
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

2. **Configurar Ambiente de Teste**
```bash
export PYTHONPATH="$(pwd)"
export DATABASE_URL="postgresql://user:pass@localhost:5432/medai_test"
export TESTING=true
```

#### Executar Testes

```bash
# Suite completa com cobertura
python -m pytest --cov=app --cov-report=html --cov-report=term-missing

# Apenas componentes críticos
python -m pytest -m critical --cov=app

# Testes de integração
python -m pytest -m integration

# Testes E2E
python -m pytest -m e2e
```

### Frontend (React/TypeScript)

#### Configuração Inicial

1. **Instalar Dependências**
```bash
cd frontend
npm install
```

2. **Executar Testes**
```bash
# Testes com cobertura
npm run test:coverage

# Testes em modo watch
npm run test

# Interface visual
npm run test:ui
```

## Componentes Críticos

### 1. ECG Analysis Service

**Localização**: `app/services/ecg_service.py`
**Testes**: `tests/test_ecg_service_enhanced.py`

**Cenários Obrigatórios**:
- Processamento de ECG normal
- Detecção de arritmias
- Análise de qualidade do sinal
- Tratamento de dados inválidos
- Performance com grandes volumes

**Exemplo de Teste**:
```python
@pytest.mark.critical
@pytest.mark.asyncio
async def test_ecg_analysis_accuracy(ecg_service, sample_ecg_data):
    """Test ECG analysis accuracy for critical diagnoses."""
    result = await ecg_service.analyze_ecg(sample_ecg_data)
    
    assert result.confidence > 0.9
    assert result.diagnosis in VALID_DIAGNOSES
    assert result.processing_time < 30  # seconds
```

### 2. ML Model Service

**Localização**: `app/services/ml_model_service.py`
**Testes**: `tests/test_ml_model_service_enhanced.py`

**Cenários Obrigatórios**:
- Carregamento de modelos
- Classificação de ECG
- Validação de entrada
- Tratamento de erros de modelo
- Fallback para modelos alternativos

### 3. AI Diagnostic Service

**Localização**: `app/services/ai_diagnostic_service.py`
**Testes**: `tests/test_ai_diagnostic_service_enhanced.py`

**Cenários Obrigatórios**:
- Integração multimodal de dados
- Correlação clínica
- Geração de diagnósticos
- Análise de confiança
- Recomendações terapêuticas

## Testes de Integração

### Workflows Críticos

#### 1. Paciente STEMI
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_stemi_patient_workflow(integrated_services):
    """Test complete STEMI patient workflow."""
    # 1. Patient arrival
    patient = await create_emergency_patient()
    
    # 2. ECG acquisition and analysis
    ecg_result = await process_emergency_ecg(patient.id)
    
    # 3. Critical diagnosis
    assert ecg_result.diagnosis == "STEMI"
    assert ecg_result.urgency == ClinicalUrgency.CRITICAL
    
    # 4. Alert system activation
    alert_sent = await send_critical_alert(patient.id)
    assert alert_sent.cath_lab_activated == True
```

#### 2. Processamento Concorrente
```python
@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_ecg_processing():
    """Test concurrent processing of multiple ECGs."""
    ecg_count = 50
    tasks = [process_ecg_async(i) for i in range(ecg_count)]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == ecg_count
    assert all(r.status == "completed" for r in results)
```

## Mocks Inteligentes

### Uso dos Smart Mocks

```python
from tests.smart_mocks import SmartECGMock, SmartPatientMock

# Gerar ECG normal
normal_ecg = SmartECGMock.generate_normal_ecg(duration_seconds=10)

# Gerar ECG com arritmia
afib_ecg = SmartECGMock.generate_arrhythmia_ecg("atrial_fibrillation")

# Gerar dados de paciente
patient_data = SmartPatientMock.generate_patient_data(
    age_range=(65, 85),
    condition="cardiac"
)
```

## Monitoramento de Cobertura

### Script de Monitoramento

```bash
# Análise única
python scripts/coverage_monitor.py

# Modo daemon (execução contínua)
./scripts/continuous_coverage.sh -d -i 3600

# Apenas backend
python scripts/coverage_monitor.py --backend-only

# Apenas frontend
python scripts/coverage_monitor.py --frontend-only
```

### Interpretação de Resultados

```
📊 RELATÓRIO DE COBERTURA DE TESTES - MEDAI
============================================================

✅ Status Geral: APROVADO
✅ Cobertura Global: 85.2% (Meta: 80%)
✅ Componentes Críticos: 100.0% (Meta: 100%)
✅ Backend: 87.5%
✅ Frontend: 82.9%

🎯 Componentes Críticos Detalhados:
  ✅ app/services/ecg_service.py: 100.0%
  ✅ app/services/ml_model_service.py: 100.0%
  ✅ app/services/ai_diagnostic_service.py: 100.0%
```

## Pipeline CI/CD

### Configuração GitHub Actions

O pipeline é ativado automaticamente em:
- Push para `main` ou `develop`
- Pull Requests
- Execução diária às 2 AM UTC

### Etapas do Pipeline

1. **Backend Coverage**
   - Instalação de dependências
   - Execução de testes
   - Geração de relatórios
   - Upload para Codecov

2. **Frontend Coverage**
   - Instalação de dependências Node.js
   - Execução de testes Vitest
   - Verificação de limites
   - Upload de relatórios

3. **Integration Tests**
   - Testes de integração
   - Testes E2E
   - Verificação de performance

4. **Quality Gates**
   - Verificação de segurança
   - Consolidação de relatórios
   - Aprovação/Reprovação automática

### Configuração Local do Pipeline

```bash
# Simular pipeline localmente
act -j backend-coverage

# Verificar workflow
github-actions-validator .github/workflows/coverage.yml
```

## Boas Práticas

### 1. Escrita de Testes

```python
# ✅ Bom: Teste específico e focado
@pytest.mark.critical
async def test_ecg_stemi_detection():
    """Test STEMI detection accuracy."""
    stemi_ecg = generate_stemi_ecg()
    result = await ecg_service.analyze(stemi_ecg)
    
    assert result.diagnosis == "STEMI"
    assert result.confidence > 0.95

# ❌ Ruim: Teste genérico demais
async def test_ecg_analysis():
    """Test ECG analysis."""
    result = await ecg_service.analyze(some_ecg)
    assert result is not None
```

### 2. Organização de Testes

```
tests/
├── unit/                    # Testes unitários
│   ├── services/
│   ├── repositories/
│   └── utils/
├── integration/             # Testes de integração
│   ├── workflows/
│   └── api/
├── e2e/                     # Testes end-to-end
│   ├── patient_journeys/
│   └── emergency_scenarios/
└── fixtures/                # Dados de teste
    ├── ecg_samples/
    └── patient_data/
```

### 3. Nomenclatura

```python
# Padrão: test_[component]_[scenario]_[expected_outcome]
def test_ecg_service_invalid_data_raises_exception():
def test_ml_model_normal_ecg_returns_high_confidence():
def test_patient_workflow_stemi_activates_cath_lab():
```

## Troubleshooting

### Problemas Comuns

#### 1. Testes Falhando
```bash
# Verificar dependências
pip install -r requirements.txt

# Verificar variáveis de ambiente
echo $PYTHONPATH
echo $DATABASE_URL

# Executar teste específico
python -m pytest tests/test_specific.py::test_function -v
```

#### 2. Cobertura Baixa
```bash
# Identificar arquivos não cobertos
python -m pytest --cov=app --cov-report=term-missing

# Gerar relatório HTML detalhado
python -m pytest --cov=app --cov-report=html
open htmlcov/index.html
```

#### 3. Testes Lentos
```bash
# Executar com profiling
python -m pytest --durations=10

# Executar apenas testes rápidos
python -m pytest -m "not slow"
```

### Logs e Debugging

```python
# Configurar logging em testes
import logging
logging.basicConfig(level=logging.DEBUG)

# Usar pytest fixtures para debugging
@pytest.fixture
def debug_mode():
    import pdb; pdb.set_trace()
```

## Manutenção

### Atualizações Regulares

1. **Semanal**
   - Revisar relatórios de cobertura
   - Verificar testes falhando
   - Atualizar dados de teste

2. **Mensal**
   - Revisar e otimizar testes lentos
   - Atualizar dependências de teste
   - Analisar tendências de cobertura

3. **Trimestral**
   - Revisar estratégia de testes
   - Atualizar mocks com dados reais
   - Avaliar novas ferramentas

### Métricas de Qualidade

```python
# Exemplo de métricas a monitorar
QUALITY_METRICS = {
    "coverage_global": 80,      # Mínimo 80%
    "coverage_critical": 100,   # Obrigatório 100%
    "test_execution_time": 300, # Máximo 5 minutos
    "flaky_test_rate": 0.05,    # Máximo 5%
    "test_maintenance_ratio": 0.1 # 10% do tempo de dev
}
```

## Recursos Adicionais

### Documentação
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Vitest Documentation](https://vitest.dev/)

### Ferramentas Úteis
- **pytest-html**: Relatórios HTML para pytest
- **pytest-xdist**: Execução paralela de testes
- **pytest-mock**: Mocking avançado
- **pytest-benchmark**: Testes de performance

### Integração com IDEs
- **VSCode**: Python Test Explorer
- **PyCharm**: Integrated test runner
- **Vim**: vim-test plugin

---

Este guia deve ser atualizado conforme a evolução do projeto e novas necessidades de teste identificadas.

