import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Executa um comando e mostra o resultado"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"📌 Comando: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print("\n📤 STDOUT:")
        if result.stdout:
            print(result.stdout)
        else:
            print("(vazio)")
            
        if result.stderr:
            print("\n📥 STDERR:")
            print(result.stderr)
            
        print(f"\n📊 Código de retorno: {result.returncode}")
        
        return result
    except Exception as e:
        print(f"\n❌ Erro ao executar: {e}")
        return None

def check_pytest_installation():
    """Verifica instalação do pytest"""
    print("\n" + "="*60)
    print("1️⃣ VERIFICANDO INSTALAÇÃO DO PYTEST")
    print("="*60)
    
    # Verificar versão do pytest
    run_command([sys.executable, '-m', 'pytest', '--version'], "Versão do pytest")
    
    # Verificar plugins do pytest
    run_command([sys.executable, '-m', 'pytest', '--trace-config'], "Configuração do pytest")
    
    # Listar plugins
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
    pytest_packages = [line for line in result.stdout.split('\n') if 'pytest' in line.lower()]
    
    print("\n📦 Pacotes pytest instalados:")
    for pkg in pytest_packages:
        print(f"   • {pkg}")

def check_directory_structure():
    """Verifica estrutura de diretórios"""
    print("\n" + "="*60)
    print("2️⃣ VERIFICANDO ESTRUTURA DE DIRETÓRIOS")
    print("="*60)
    
    print(f"\n📁 Diretório atual: {os.getcwd()}")
    
    # Verificar se estamos no diretório correto
    expected_dirs = ['app', 'tests']
    for dir_name in expected_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/ existe")
            # Listar alguns arquivos
            files = list(Path(dir_name).glob('*.py'))[:5]
            for f in files:
                print(f"      • {f.name}")
        else:
            print(f"   ❌ {dir_name}/ NÃO existe")

def test_pytest_discovery():
    """Testa descoberta de testes de várias formas"""
    print("\n" + "="*60)
    print("3️⃣ TESTANDO DESCOBERTA DE TESTES")
    print("="*60)
    
    # Diferentes formas de executar pytest
    commands = [
        # Forma 1: pytest direto
        ['pytest', '--collect-only', 'tests/'],
        
        # Forma 2: python -m pytest
        [sys.executable, '-m', 'pytest', '--collect-only', 'tests/'],
        
        # Forma 3: com arquivo específico
        [sys.executable, '-m', 'pytest', '--collect-only', 'tests/test_simple.py'],
        
        # Forma 4: verbose
        [sys.executable, '-m', 'pytest', '--collect-only', '-vv', 'tests/'],
        
        # Forma 5: com pythonpath
        [sys.executable, '-m', 'pytest', '--collect-only', '--pythonpath=.', 'tests/'],
    ]
    
    for i, cmd in enumerate(commands, 1):
        result = run_command(cmd, f"Tentativa {i}")
        
        if result and result.stdout:
            # Contar testes coletados
            collected = result.stdout.count('::')
            if collected > 0:
                print(f"\n✅ SUCESSO! {collected} testes coletados com este comando")
                return True
    
    return False

def check_test_files():
    """Verifica arquivos de teste individualmente"""
    print("\n" + "="*60)
    print("4️⃣ VERIFICANDO ARQUIVOS DE TESTE")
    print("="*60)
    
    test_files = list(Path('tests').glob('test_*.py'))
    print(f"\n📊 Total de arquivos de teste: {len(test_files)}")
    
    # Verificar cada arquivo
    for test_file in test_files[:3]:  # Apenas 3 primeiros
        print(f"\n📄 {test_file.name}:")
        
        # Tentar importar o arquivo
        try:
            # Adicionar tests ao path
            if 'tests' not in sys.path:
                sys.path.insert(0, 'tests')
            
            module_name = test_file.stem
            __import__(module_name)
            print(f"   ✅ Importação OK")
        except Exception as e:
            print(f"   ❌ Erro na importação: {str(e)[:100]}...")
        
        # Verificar conteúdo
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Contar elementos de teste
            test_functions = content.count('def test_')
            test_classes = content.count('class Test')
            
            print(f"   📊 Funções de teste: {test_functions}")
            print(f"   📊 Classes de teste: {test_classes}")
            
        except Exception as e:
            print(f"   ❌ Erro ao ler arquivo: {e}")

def create_diagnostic_test():
    """Cria um teste de diagnóstico super simples"""
    print("\n" + "="*60)
    print("5️⃣ CRIANDO TESTE DE DIAGNÓSTICO")
    print("="*60)
    
    test_content = '''# Test diagnostic - arquivo mais simples possível

def test_diagnostic():
    """Teste de diagnóstico"""
    assert 1 == 1
    print("TESTE EXECUTADO COM SUCESSO!")
'''
    
    with open('tests/test_diagnostic.py', 'w') as f:
        f.write(test_content)
    
    print("✅ Criado tests/test_diagnostic.py")
    
    # Tentar executar
    result = run_command(
        [sys.executable, '-m', 'pytest', 'tests/test_diagnostic.py', '-v', '-s'],
        "Executando teste de diagnóstico"
    )
    
    if result and 'passed' in result.stdout:
        print("\n✅ PYTEST ESTÁ FUNCIONANDO!")
    else:
        print("\n❌ PROBLEMA COM PYTEST")

def check_ini_files():
    """Verifica arquivos de configuração"""
    print("\n" + "="*60)
    print("6️⃣ VERIFICANDO ARQUIVOS DE CONFIGURAÇÃO")
    print("="*60)
    
    config_files = ['pytest.ini', 'setup.cfg', 'pyproject.toml', 'tox.ini']
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"\n📄 {config_file} encontrado:")
            with open(config_file, 'r') as f:
                content = f.read()
                # Mostrar apenas primeiras 10 linhas
                lines = content.split('\n')[:10]
                for line in lines:
                    print(f"   {line}")
        else:
            print(f"\n❌ {config_file} não existe")

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO PROFUNDO DO PYTEST")
    print("="*60)
    
    # 1. Verificar instalação
    check_pytest_installation()
    
    # 2. Verificar estrutura
    check_directory_structure()
    
    # 3. Verificar arquivos de configuração
    check_ini_files()
    
    # 4. Testar descoberta
    discovery_ok = test_pytest_discovery()
    
    # 5. Verificar arquivos de teste
    check_test_files()
    
    # 6. Criar e executar teste diagnóstico
    create_diagnostic_test()
    
    print("\n" + "="*60)
    print("📋 DIAGNÓSTICO COMPLETO")
    print("="*60)
    
    print("\n🔧 AÇÕES RECOMENDADAS:")
    
    if not discovery_ok:
        print("\n1. Reinstalar pytest:")
        print("   pip uninstall pytest pytest-asyncio pytest-cov -y")
        print("   pip install pytest pytest-asyncio pytest-cov")
        
        print("\n2. Verificar PYTHONPATH:")
        print("   set PYTHONPATH=%cd%")
        print("   echo %PYTHONPATH%")
        
        print("\n3. Executar teste simples:")
        print("   python -m pytest tests/test_diagnostic.py -v")
        
        print("\n4. Se nada funcionar, criar ambiente virtual novo:")
        print("   python -m venv venv_new")
        print("   venv_new\\Scripts\\activate")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()