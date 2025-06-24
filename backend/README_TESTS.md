# 🧪 Guia de Testes - MedAI Backend

## 📋 Visão Geral

Este documento explica como resolver o erro de importação e executar os testes do projeto MedAI.

## ❌ Erro Original

```
ModuleNotFoundError: No module named 'app.utils.data_processing'
```

## ✅ Soluções

### Solução 1: Usar o Script de Testes (Recomendado)

```bash
# Na pasta backend/
python run_tests.py
```

### Solução 2: Configurar PYTHONPATH Manualmente

#### Windows (Command Prompt):
```cmd
cd C:\Users\lucie\Documents\GitHub\medai\backend
set PYTHONPATH=%CD%
python -m pytest tests/test_utilities.py -v
```

#### Windows (PowerShell):
```powershell
cd C:\Users\lucie\Documents\GitHub\medai\backend
$env:PYTHONPATH = $PWD
python -m pytest tests/test_utilities.py -v
```

#### Linux/Mac:
```bash
cd /path/to/medai/backend
export PYTHONPATH=$PWD
python -m pytest tests/test_utilities.py -v
```

### Solução 3: Executar do Diretório Correto

```bash
# IMPORTANTE: Execute do diretório backend/
cd C:\Users\lucie\Documents\GitHub\medai\backend
python -m pytest tests/test_utilities.py -v
```

## 📁 Estrutura Necessária

```
medai/
└── backend/
    ├── app/
    │   ├── __init__.py          # OBRIGATÓRIO
    │   └── utils/
    │       ├── __init__.py      # OBRIGATÓRIO
    │       ├── data_processing.py
    │       ├── file_handlers.py
    │       ├── medical_calculations.py
    │       └── report_generator.py
    ├── tests/
    │   ├── __init__.py          # OBRIGATÓRIO
    │   ├── conftest.py
    │   └── test_utilities.py
    ├── run_tests.py
    └── pyproject.toml
```

## 🔧 Instalação de Dependências

```bash
# Instalar dependências básicas
pip install pytest numpy scipy pandas

# Instalar todas as dependências (se tiver requirements.txt)
pip install -r requirements.txt
```

## 🚀 Executando os Testes

### Teste Específico
```bash
python run_tests.py
```

### Com Cobertura
```bash
python run_tests.py --coverage
```

### Apenas Testes Unitários
```bash
python run_tests.py -m unit
```

### Teste Específico por Nome
```bash
python run_tests.py -k test_normalize
```

## 🔍 Diagnóstico de Problemas

### 1. Verificar se os arquivos __init__.py existem:
```python
# Execute este script de diagnóstico
import os
from pathlib import Path

dirs_to_check = ['app', 'app/utils', 'tests']
for dir_path in dirs_to_check:
    path = Path(dir_path)
    init_file = path / '__init__.py'
    if not init_file.exists():
        print(f"❌ Faltando: {init_file}")
        # Criar o arquivo
        init_file.parent.mkdir(parents=True, exist_ok=True)
        init_file.write_text('')
        print(f"✅ Criado: {init_file}")
    else:
        print(f"✅ Existe: {init_file}")
```

### 2. Verificar o Python Path:
```python
import sys
print("Python Path:")
for path in sys.path:
    print(f"  - {path}")
```

### 3. Verificar imports:
```python
try:
    import app
    print("✅ Módulo 'app' importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar 'app': {e}")
```

## 💡 Dicas

1. **Sempre execute os testes do diretório `backend/`**
2. **Certifique-se de que todos os `__init__.py` existem**
3. **Use ambientes virtuais para isolar dependências**

## 🐛 Problemas Comuns

### Erro: "No module named 'scipy'"
```bash
pip install scipy numpy pandas
```

### Erro: "pytest: command not found"
```bash
pip install pytest
# ou
python -m pip install pytest
```

### Erro persistente de importação
1. Verifique se está no diretório correto
2. Confirme que os arquivos `__init__.py` existem
3. Use o caminho absoluto no PYTHONPATH

## 📊 Interpretando os Resultados

- ✅ **PASSED**: Teste passou
- ❌ **FAILED**: Teste falhou
- ⚠️ **SKIPPED**: Teste pulado (geralmente por falta de dependências)
- 🔧 **XFAIL**: Falha esperada

## 🤝 Suporte

Se continuar com problemas:
1. Verifique a versão do Python: `python --version` (deve ser 3.8+)
2. Liste os pacotes instalados: `pip list`
3. Execute o diagnóstico completo: `python run_tests.py --help`

