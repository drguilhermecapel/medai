import os
import subprocess
import sys
from pathlib import Path

def diagnose_test_discovery():
    """Diagnostica por que os testes não estão sendo encontrados"""
    print("="*60)
    print("🔍 DIAGNOSTICANDO DESCOBERTA DE TESTES")
    print("="*60)
    
    # 1. Verificar se o diretório de testes existe
    print("\n1️⃣ Verificando diretório de testes...")
    if os.path.exists('tests'):
        print("   ✅ Diretório 'tests' existe")
        
        # Listar arquivos de teste
        test_files = list(Path('tests').glob('test_*.py'))
        print(f"   📁 Encontrados {len(test_files)} arquivos de teste:")
        for f in test_files[:5]:  # Mostrar apenas os 5 primeiros
            print(f"      • {f.name}")
        if len(test_files) > 5:
            print(f"      ... e mais {len(test_files) - 5} arquivos")
    else:
        print("   ❌ Diretório 'tests' NÃO existe!")
        return False
    
    # 2. Verificar __init__.py no diretório tests
    print("\n2️⃣ Verificando __init__.py...")
    init_file = Path('tests/__init__.py')
    if init_file.exists():
        print("   ✅ tests/__init__.py existe")
    else:
        print("   ❌ tests/__init__.py NÃO existe - criando...")
        init_file.write_text("")
        print("   ✅ Criado!")
    
    # 3. Verificar pytest.ini
    print("\n3️⃣ Verificando pytest.ini...")
    if os.path.exists('pytest.ini'):
        with open('pytest.ini', 'r') as f:
            content = f.read()
        print("   ✅ pytest.ini existe")
        print(f"   📄 Conteúdo:\n{content}")
    else:
        print("   ❌ pytest.ini NÃO existe - criando...")
        create_pytest_ini()
    
    # 4. Verificar se os testes têm a estrutura correta
    print("\n4️⃣ Verificando estrutura dos testes...")
    check_test_structure()
    
    # 5. Tentar executar um teste específico
    print("\n5️⃣ Tentando executar um teste específico...")
    test_specific_file()
    
    return True

def create_pytest_ini():
    """Cria arquivo pytest.ini com configuração correta"""
    pytest_ini_content = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
"""
    
    with open('pytest.ini', 'w') as f:
        f.write(pytest_ini_content)
    print("   ✅ pytest.ini criado!")

def check_test_structure():
    """Verifica se os testes têm a estrutura correta"""
    test_files = list(Path('tests').glob('test_*.py'))
    
    issues_found = False
    for test_file in test_files[:3]:  # Verificar apenas os 3 primeiros
        print(f"\n   📄 Verificando {test_file.name}...")
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar imports básicos
            if 'import pytest' not in content and 'from pytest' not in content:
                print(f"      ⚠️  Falta import do pytest")
                issues_found = True
            
            # Verificar se tem classes ou funções de teste
            if 'def test_' not in content and 'class Test' not in content:
                print(f"      ⚠️  Não encontradas funções test_* ou classes Test*")
                issues_found = True
            else:
                # Contar testes
                test_count = content.count('def test_') + content.count('async def test_')
                print(f"      ✅ {test_count} testes encontrados")
        
        except Exception as e:
            print(f"      ❌ Erro ao ler arquivo: {e}")
            issues_found = True
    
    return not issues_found

def test_specific_file():
    """Tenta executar um arquivo de teste específico"""
    # Procurar um arquivo de teste simples
    simple_tests = ['test_security.py', 'test_utilities.py', 'test_auth.py']
    
    for test_name in simple_tests:
        test_path = f'tests/{test_name}'
        if os.path.exists(test_path):
            print(f"\n   🧪 Tentando executar {test_name}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', test_path, '-v'],
                capture_output=True,
                text=True
            )
            
            if 'collected 0 items' in result.stdout:
                print(f"      ❌ Nenhum teste coletado em {test_name}")
            else:
                print(f"      ✅ Testes encontrados em {test_name}")
                # Mostrar um pouco da saída
                lines = result.stdout.split('\n')
                for line in lines[:10]:
                    if line.strip():
                        print(f"         {line}")
            break

def create_simple_test():
    """Cria um teste simples para verificar se o pytest está funcionando"""
    simple_test_content = '''"""
Teste simples para verificar configuração do pytest
"""
import pytest

def test_pytest_is_working():
    """Teste básico para verificar se o pytest está funcionando"""
    assert True
    
def test_basic_math():
    """Teste de matemática básica"""
    assert 2 + 2 == 4
    
class TestBasicFunctionality:
    """Classe de teste básica"""
    
    def test_string_operations(self):
        """Teste de operações com strings"""
        assert "hello".upper() == "HELLO"
    
    def test_list_operations(self):
        """Teste de operações com listas"""
        my_list = [1, 2, 3]
        my_list.append(4)
        assert len(my_list) == 4
        assert my_list[-1] == 4

@pytest.mark.asyncio
async def test_async_function():
    """Teste de função assíncrona"""
    import asyncio
    await asyncio.sleep(0.01)
    assert True

# Teste parametrizado
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    """Teste parametrizado de quadrado"""
    assert input ** 2 == expected
'''
    
    with open('tests/test_simple.py', 'w', encoding='utf-8') as f:
        f.write(simple_test_content)
    
    print("\n✅ Criado teste simples: tests/test_simple.py")

def fix_existing_tests():
    """Corrige problemas comuns nos testes existentes"""
    print("\n🔧 Corrigindo testes existentes...")
    
    # Padrão para encontrar arquivos de teste
    test_files = list(Path('tests').glob('test_*.py'))
    
    fixed_count = 0
    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. Garantir que tem imports necessários
            if 'import pytest' not in content:
                content = 'import pytest\n' + content
            
            # 2. Corrigir classes de teste sem herança
            content = re.sub(
                r'class\s+Test(\w+)(?:\s*:)',
                r'class Test\1:',
                content
            )
            
            # 3. Garantir que métodos de teste em classes tenham self
            content = re.sub(
                r'(\s+)def\s+test_(\w+)\(\)(\s*):',
                r'\1def test_\2(self)\3:',
                content
            )
            
            # 4. Remover decoradores problemáticos temporariamente
            content = re.sub(
                r'@pytest\.mark\.skip.*?\n',
                '',
                content
            )
            
            if content != original_content:
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                print(f"   ✅ Corrigido: {test_file.name}")
        
        except Exception as e:
            print(f"   ⚠️  Erro ao processar {test_file.name}: {e}")
    
    print(f"\n   📊 {fixed_count} arquivos corrigidos")

def run_final_test():
    """Executa teste final para verificar se tudo está funcionando"""
    print("\n" + "="*60)
    print("🧪 EXECUTANDO TESTE FINAL")
    print("="*60)
    
    # Primeiro, tentar o teste simples
    print("\n1️⃣ Testando arquivo simples...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/test_simple.py', '-v'],
        capture_output=True,
        text=True
    )
    
    if '6 passed' in result.stdout:
        print("   ✅ Teste simples passou! Pytest está funcionando.")
    else:
        print("   ❌ Problema com o teste simples")
        print(result.stdout)
    
    # Agora tentar todos os testes
    print("\n2️⃣ Executando todos os testes...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        capture_output=True,
        text=True
    )
    
    # Contar resultados
    lines = result.stdout.split('\n')
    for line in lines:
        if 'passed' in line and 'failed' in line:
            print(f"\n   📊 {line}")
            break
    
    # Mostrar alguns testes que passaram/falharam
    passed_tests = [line for line in lines if 'PASSED' in line]
    failed_tests = [line for line in lines if 'FAILED' in line]
    
    if passed_tests:
        print(f"\n   ✅ Exemplos de testes que passaram:")
        for test in passed_tests[:3]:
            print(f"      • {test.strip()}")
    
    if failed_tests:
        print(f"\n   ❌ Exemplos de testes que falharam:")
        for test in failed_tests[:3]:
            print(f"      • {test.strip()}")

def main():
    """Função principal"""
    print("\n🚀 CORRIGINDO DESCOBERTA DE TESTES")
    print("="*60)
    
    # Adicionar diretório atual ao PYTHONPATH
    sys.path.insert(0, os.getcwd())
    os.environ['PYTHONPATH'] = os.getcwd()
    
    # 1. Diagnosticar problemas
    if not diagnose_test_discovery():
        print("\n❌ Problemas críticos encontrados. Abortando.")
        return
    
    # 2. Criar teste simples
    create_simple_test()
    
    # 3. Corrigir testes existentes
    # fix_existing_tests()
    
    # 4. Executar teste final
    run_final_test()
    
    print("\n" + "="*60)
    print("📋 PRÓXIMOS PASSOS:")
    print("="*60)
    print("1. Se os testes ainda não estão sendo encontrados:")
    print("   • Verifique se você está no diretório correto (backend)")
    print("   • Execute: python -m pytest tests/ -v")
    print("\n2. Se os testes estão falhando por imports:")
    print("   • Execute: pip install -r requirements.txt")
    print("   • Verifique se todas as dependências estão instaladas")
    print("\n3. Para ver mais detalhes:")
    print("   • Execute: pytest tests/test_simple.py -vvs")
    print("   • Isso mostrará a saída completa do teste simples")

if __name__ == "__main__":
    import re  # Adicionar import que faltou
    main()