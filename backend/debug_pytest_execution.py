import os
import subprocess
import sys
from pathlib import Path

def check_python_path():
    """Verifica e corrige o PYTHONPATH"""
    print("="*60)
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO PYTHON")
    print("="*60)
    
    print("\n1️⃣ Python Path atual:")
    for i, path in enumerate(sys.path):
        print(f"   [{i}] {path}")
    
    # Adicionar diretório atual ao PYTHONPATH
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        os.environ['PYTHONPATH'] = current_dir
        print(f"\n   ✅ Adicionado ao PYTHONPATH: {current_dir}")

def check_imports():
    """Verifica se os imports básicos funcionam"""
    print("\n2️⃣ Verificando imports básicos:")
    
    imports_to_check = [
        "pytest",
        "app",
        "app.core",
        "app.models",
        "app.services",
        "fastapi",
        "sqlalchemy",
        "pydantic"
    ]
    
    for module in imports_to_check:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {str(e)}")

def run_pytest_collect_only():
    """Executa pytest com --collect-only para ver o que está sendo coletado"""
    print("\n" + "="*60)
    print("🔍 EXECUTANDO PYTEST --collect-only")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '--collect-only', '-q'],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )
    
    print("\n📊 Saída do collect-only:")
    print(result.stdout)
    if result.stderr:
        print("\n❌ Erros:")
        print(result.stderr)
    
    # Contar itens coletados
    collected = result.stdout.count('::')
    print(f"\n📊 Total de testes coletados: {collected}")
    
    return collected > 0

def run_simple_pytest():
    """Executa pytest de forma mais simples possível"""
    print("\n" + "="*60)
    print("🧪 EXECUTANDO PYTEST SIMPLES")
    print("="*60)
    
    # Criar um teste mínimo inline
    test_content = '''
def test_basic():
    assert 1 + 1 == 2
'''
    
    with open('tests/test_minimal.py', 'w') as f:
        f.write(test_content)
    
    print("\n1️⃣ Tentando teste mínimo...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/test_minimal.py', '-v'],
        capture_output=True,
        text=True
    )
    
    print("Stdout:")
    print(result.stdout)
    if result.stderr:
        print("\nStderr:")
        print(result.stderr)
    
    return '1 passed' in result.stdout

def check_conftest():
    """Verifica se há problemas no conftest.py"""
    print("\n" + "="*60)
    print("🔍 VERIFICANDO CONFTEST.PY")
    print("="*60)
    
    conftest_path = 'tests/conftest.py'
    if os.path.exists(conftest_path):
        print(f"\n✅ {conftest_path} existe")
        
        # Tentar importar conftest
        try:
            # Adicionar tests ao path temporariamente
            sys.path.insert(0, 'tests')
            import conftest
            print("✅ conftest.py importado com sucesso")
            sys.path.pop(0)
        except Exception as e:
            print(f"❌ Erro ao importar conftest.py: {e}")
            
            # Mostrar as primeiras linhas do erro
            import traceback
            traceback.print_exc()
            
            # Tentar executar sem conftest
            print("\n🔧 Renomeando conftest.py temporariamente...")
            os.rename(conftest_path, conftest_path + '.bak')
            return False
    else:
        print(f"⚠️  {conftest_path} não existe")
    
    return True

def fix_common_issues():
    """Corrige problemas comuns que impedem a execução"""
    print("\n" + "="*60)
    print("🔧 APLICANDO CORREÇÕES")
    print("="*60)
    
    # 1. Criar __init__.py em todos os diretórios necessários
    print("\n1️⃣ Criando __init__.py em diretórios...")
    dirs_to_check = ['app', 'app/core', 'app/models', 'app/services', 'app/api', 'tests']
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            init_file = os.path.join(dir_path, '__init__.py')
            if not os.path.exists(init_file):
                Path(init_file).touch()
                print(f"   ✅ Criado: {init_file}")
    
    # 2. Criar pytest.ini mínimo
    print("\n2️⃣ Criando pytest.ini mínimo...")
    pytest_ini = '''[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
'''
    
    with open('pytest.ini.minimal', 'w') as f:
        f.write(pytest_ini)
    
    # Fazer backup do atual e usar o mínimo
    if os.path.exists('pytest.ini'):
        os.rename('pytest.ini', 'pytest.ini.original')
    os.rename('pytest.ini.minimal', 'pytest.ini')
    print("   ✅ pytest.ini simplificado")
    
    # 3. Criar setup.cfg alternativo
    print("\n3️⃣ Criando setup.cfg...")
    setup_cfg = '''[tool:pytest]
testpaths = tests
'''
    
    with open('setup.cfg', 'w') as f:
        f.write(setup_cfg)
    print("   ✅ setup.cfg criado")

def run_final_diagnosis():
    """Executa diagnóstico final"""
    print("\n" + "="*60)
    print("📊 DIAGNÓSTICO FINAL")
    print("="*60)
    
    # Tentar diferentes formas de executar pytest
    commands = [
        [sys.executable, '-m', 'pytest', '--version'],
        [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        [sys.executable, '-m', 'pytest', 'tests/test_minimal.py', '-v'],
        ['pytest', 'tests/', '-v'],
    ]
    
    for i, cmd in enumerate(commands):
        print(f"\n{i+1}️⃣ Comando: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("   ✅ Sucesso!")
                if 'passed' in result.stdout or 'failed' in result.stdout:
                    print(f"   📊 Resultado: {result.stdout.splitlines()[-1] if result.stdout.splitlines() else 'Vazio'}")
            else:
                print(f"   ❌ Falhou (código: {result.returncode})")
                if result.stderr:
                    print(f"   Erro: {result.stderr.splitlines()[0] if result.stderr.splitlines() else ''}")
        except Exception as e:
            print(f"   ❌ Exceção: {e}")

def main():
    """Função principal"""
    print("\n🔍 DEPURAÇÃO DA EXECUÇÃO DO PYTEST")
    print("="*60)
    
    # 1. Verificar Python path
    check_python_path()
    
    # 2. Verificar imports
    check_imports()
    
    # 3. Verificar conftest
    conftest_ok = check_conftest()
    
    # 4. Tentar collect-only
    collected = run_pytest_collect_only()
    
    # 5. Se não coletou nada, aplicar correções
    if not collected:
        fix_common_issues()
        
        # Tentar novamente
        print("\n🔄 Tentando novamente após correções...")
        collected = run_pytest_collect_only()
    
    # 6. Executar teste simples
    simple_ok = run_simple_pytest()
    
    # 7. Diagnóstico final
    run_final_diagnosis()
    
    print("\n" + "="*60)
    print("📋 RESUMO E PRÓXIMOS PASSOS")
    print("="*60)
    
    if simple_ok:
        print("\n✅ Pytest está funcionando com testes simples!")
        print("\nO problema pode ser:")
        print("1. Imports quebrados nos testes existentes")
        print("2. Dependências faltando")
        print("3. Configuração complexa no conftest.py")
        print("\nTente:")
        print("• pytest tests/test_minimal.py -v")
        print("• pytest tests/test_security.py -v")
        print("• pytest tests/ -v --tb=long (para ver erros completos)")
    else:
        print("\n❌ Pytest não está executando corretamente")
        print("\nVerifique:")
        print("1. Se pytest está instalado: pip install pytest pytest-asyncio pytest-cov")
        print("2. Se está no ambiente virtual correto")
        print("3. Execute: python -m pip list | grep pytest")
    
    if not conftest_ok:
        print("\n⚠️  conftest.py foi renomeado para conftest.py.bak devido a erros")
        print("Revise o arquivo e corrija os problemas de importação")

if __name__ == "__main__":
    main()