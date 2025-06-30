# Guia Completo de Testes MedAI

## 📋 Visão Geral

Este guia fornece instruções detalhadas para executar os testes do sistema MedAI e atingir as metas de cobertura estabelecidas:
- **80% de cobertura global**
- **100% de cobertura nos componentes críticos**

## 🔧 Preparação do Ambiente

### 1. Instalar Dependências de Teste

```bash
pip install -r requirements-test.txt
```

Se o arquivo não existir, instale manualmente:

```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-timeout httpx faker
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env.test`:

```env
DATABASE_URL=sqlite:///./test_medai.db
SECRET_KEY=test-secret-key-development
ENVIRONMENT=testing
DEBUG=True
TESTING=True
REDIS_URL=redis://localhost:6379/1
```

## 🚀 Executando os Testes

### Execução Rápida

```bash
# Executar todos os testes com cobertura
python run_tests.py

# Executar apenas testes unitários
python run_tests.py unit

# Executar apenas testes de integração
python run_tests.py integration

# Executar apenas testes E2E
python run_tests.py e2e
```

### Execução Manual com Pytest

```bash
# Todos os testes com relatório de cobertura
pytest -v --cov=app --cov-report=html --cov-report=term-missing

# Testes específicos
pytest tests/test_validation_service.py -v --cov=app.services.validation_service

# Testes com marcadores
pytest -m "not slow" -v  # Excluir testes lentos
pytest -m critical -v     # Apenas testes críticos
```

## 📊 Componentes Críticos

Os seguintes módulos devem ter 100% de cobertura:

1. **app.core.security** - Autenticação e segurança
2. **app.core.config** - Configurações do sistema
3. **app.services.validation_service** - Validação de dados médicos
4. **app.services.ml_model_service** - Serviços de Machine Learning
5. **app.services.patient_service** - Gerenciamento de pacientes
6. **app.services.exam_service** - Gerenciamento de exames
7. **app.services.diagnostic_service** - Serviços de diagnóstico
8. **app.api.v1.endpoints.auth** - Endpoints de autenticação

## 🔍 Verificando a Cobertura

### Relatório no Terminal

```bash
pytest --cov=app --cov-report=term-missing
```

### Relatório HTML Detalhado

```bash
pytest --cov=app --cov-report=html
# Abrir htmlcov/index.html no navegador
```

### Verificar Módulos Específicos

```bash
# Cobertura do serviço de validação
pytest tests/test_validation_service.py --cov=app.services.validation_service --cov-report=term-missing

# Cobertura do core de segurança
pytest tests/test_core_modules.py -k "TestSecurity" --cov=app.core.security --cov-report=term-missing
```

## 🎯 Estratégias para Atingir 100% de Cobertura

### 1. Identificar Linhas Não Cobertas

```bash
# Gerar relatório detalhado
pytest --cov=app --cov-report=html
# Verificar quais linhas estão em vermelho no relatório HTML
```

### 2. Adicionar Testes para Casos Extremos

```python
# Exemplo: Testar exceções
def test_service_error_handling():
    with pytest.raises(ValidationError):
        service.validate_invalid_data()
    
# Testar branches condicionais
def test_all_conditions():
    assert service.process(condition=True) == expected_true
    assert service.process(condition=False) == expected_false
```

### 3. Usar Mocks para Dependências Externas

```python
@patch('app.services.email_service.send_email')
def test_notification(mock_email):
    service.notify_user(user_id=1)
    mock_email.assert_called_once()
```

### 4. Testar Código Assíncrono

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await service.async_method()
    assert result is not None
```

## 📈 Monitoramento Contínuo

### GitHub Actions (CI/CD)

Crie `.github/workflows/tests.yml`:

```yaml
name: Tests and Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests with coverage
      run: |
        python run_tests.py
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

## 🐛 Solução de Problemas

### Erro: "No module named 'app'"

```bash
# Adicionar o projeto ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Erro: "Database is locked"

```bash
# Remover banco de testes
rm test_medai.db
```

### Testes Lentos

```bash
# Executar em paralelo
pytest -n auto  # Requer pytest-xdist
```

### Testes Falhando Aleatoriamente

```python
# Adicionar fixtures para isolar testes
@pytest.fixture(autouse=True)
def reset_db():
    # Setup
    yield
    # Teardown
    db.rollback()
```

## 📝 Checklist Final

- [ ] Todos os arquivos de erro foram corrigidos
- [ ] `run_tests.py` executa sem erros
- [ ] Cobertura global ≥ 80%
- [ ] Todos os módulos críticos com 100% de cobertura
- [ ] Relatório HTML gerado em `htmlcov/`
- [ ] Nenhum teste está falhando
- [ ] CI/CD configurado e passando

## 🎉 Conclusão

Seguindo este guia, você deve conseguir:
1. Executar todos os testes sem erros
2. Atingir 80% de cobertura global
3. Garantir 100% de cobertura nos componentes críticos
4. Gerar relatórios detalhados de cobertura

Execute `python run_tests.py` para verificar o status atual e siga as recomendações do relatório para melhorar a cobertura onde necessário.