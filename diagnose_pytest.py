#!/usr/bin/env python3
"""
Diagnóstico específico para descobrir exatamente qual é o problema com pytest
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command_detailed(cmd, description=""):
    """Executa comando e mostra output detalhado"""
    print(f"🔍 {description}")
    print(f"   Comando: {cmd}")
    print("   " + "-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        print(f"   Código de saída: {result.returncode}")
        
        if result.stdout:
            print("   STDOUT:")
            for line in result.stdout.split('\n')[:20]:  # Primeiras 20 linhas
                print(f"     {line}")
            if len(result.stdout.split('\n')) > 20:
                print("     ... (truncado)")
        
        if result.stderr:
            print("   STDERR:")
            for line in result.stderr.split('\n')[:20]:  # Primeiras 20 linhas
                print(f"     {line}")
            if len(result.stderr.split('\n')) > 20:
                print("     ... (truncado)")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("   ❌ Comando expirou (timeout)")
        return False, "", "Timeout"
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False, "", str(e)


def check_test_structure():
    """Verifica a estrutura dos arquivos de teste"""
    print("\n📁 VERIFICANDO ESTRUTURA DE TESTES")
    print("=" * 60)
    
    # Verificar se diretório tests existe
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ Diretório 'tests' não existe!")
        return False
    
    print(f"✅ Diretório tests existe: {tests_dir}")
    
    # Listar arquivos de teste
    test_files = list(tests_dir.glob("**/*.py"))
    print(f"\n📄 Arquivos de teste encontrados ({len(test_files)}):")
    
    for test_file in test_files:
        print(f"   • {test_file}")
        
        # Verificar se o arquivo pode ser lido
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"     ✅ Legível ({len(content)} chars)")
        except Exception as e:
            print(f"     ❌ Erro ao ler: {e}")
    
    return len(test_files) > 0


def check_specific_test_file():
    """Verifica um arquivo de teste específico"""
    print("\n🔍 VERIFICANDO ARQUIVO DE TESTE ESPECÍFICO")
    print("=" * 60)
    
    test_file = "tests/unit/test_config.py"
    
    if not Path(test_file).exists():
        print(f"❌ {test_file} não existe")
        # Listar o que existe em tests/
        print("\nArquivos em tests/:")
        if Path("tests").exists():
            for f in Path("tests").rglob("*.py"):
                print(f"   • {f}")
        return False
    
    print(f"✅ {test_file} existe")
    
    # Tentar importar o arquivo diretamente
    print(f"\n🧪 Tentando importar {test_file} diretamente...")
    
    try:
        # Adicionar paths necessários
        sys.path.insert(0, os.getcwd())
        sys.path.insert(0, os.path.join(os.getcwd(), 'tests'))
        
        # Importar o módulo
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_config", test_file)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        print("   ✅ Importação direta funcionou!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na importação direta: {e}")
        
        # Mostrar traceback completo
        import traceback
        print("\n   📋 Traceback completo:")
        traceback.print_exc()
        
        return False


def test_pytest_discovery():
    """Testa descoberta de testes pelo pytest"""
    print("\n🔍 TESTANDO DESCOBERTA DE TESTES")
    print("=" * 60)
    
    # Comando mais simples possível
    success, stdout, stderr = run_command_detailed(
        "python -m pytest --collect-only",
        "Descoberta de testes"
    )
    
    if "collected" in stdout:
        print("✅ Pytest conseguiu descobrir testes!")
        return True
    else:
        print("❌ Pytest não conseguiu descobrir testes")
        return False


def test_minimal_pytest():
    """Testa pytest com configuração mínima"""
    print("\n🔍 TESTANDO PYTEST MÍNIMO")
    print("=" * 60)
    
    # Criar arquivo de teste mínimo
    minimal_test = """
def test_basic():
    assert True

def test_import():
    import sys
    assert sys is not None
"""
    
    with open("test_minimal_temp.py", "w") as f:
        f.write(minimal_test)
    
    try:
        success, stdout, stderr = run_command_detailed(
            "python -m pytest test_minimal_temp.py -v",
            "Teste mínimo"
        )
        
        return success
        
    finally:
        # Remover arquivo temporário
        if Path("test_minimal_temp.py").exists():
            Path("test_minimal_temp.py").unlink()


def check_pytest_config():
    """Verifica configuração do pytest"""
    print("\n🔍 VERIFICANDO CONFIGURAÇÃO PYTEST")
    print("=" * 60)
    
    config_files = ["pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"📄 {config_file} encontrado")
            
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                
                # Mostrar linhas relevantes
                lines = content.split('\n')
                for i, line in enumerate(lines[:20]):  # Primeiras 20 linhas
                    if 'pytest' in line.lower() or 'test' in line.lower():
                        print(f"   {i+1:2}: {line}")
                        
            except Exception as e:
                print(f"   ❌ Erro ao ler {config_file}: {e}")
        else:
            print(f"   ❓ {config_file} não encontrado")


def create_simple_test():
    """Cria um teste super simples para verificar se pytest funciona"""
    print("\n🔧 CRIANDO TESTE SIMPLES")
    print("=" * 60)
    
    # Garantir que diretório tests existe
    Path("tests").mkdir(exist_ok=True)
    
    simple_test = '''# -*- coding: utf-8 -*-
"""
Teste simples para verificar se pytest funciona
"""

def test_true():
    """Teste mais básico possível"""
    assert True


def test_math():
    """Teste simples de matemática"""
    assert 2 + 2 == 4


def test_string():
    """Teste simples de string"""
    assert "hello" == "hello"


def test_list():
    """Teste simples de lista"""
    my_list = [1, 2, 3]
    assert len(my_list) == 3


class TestBasic:
    """Classe de teste básica"""
    
    def test_method(self):
        """Método de teste"""
        assert 1 == 1
'''
    
    test_file = "tests/test_simple_verification.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(simple_test)
    
    print(f"✅ Criado: {test_file}")
    
    # Testar este arquivo específico
    success, stdout, stderr = run_command_detailed(
        f"python -m pytest {test_file} -v",
        f"Executando {test_file}"
    )
    
    return success


def main():
    """Diagnóstico completo"""
    print("🔍 DIAGNÓSTICO COMPLETO DO PYTEST")
    print("=" * 60)
    print("Vamos descobrir exatamente qual é o problema...")
    print()
    
    results = {}
    
    # 1. Verificar estrutura
    results['structure'] = check_test_structure()
    
    # 2. Verificar configuração
    check_pytest_config()
    
    # 3. Teste mínimo
    results['minimal'] = test_minimal_pytest()
    
    # 4. Descoberta de testes
    results['discovery'] = test_pytest_discovery()
    
    # 5. Arquivo específico
    results['specific_file'] = check_specific_test_file()
    
    # 6. Criar e testar arquivo simples
    results['simple_test'] = create_simple_test()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}: {'OK' if result else 'PROBLEMA'}")
    
    # Recomendações
    print("\n📋 RECOMENDAÇÕES:")
    
    if results.get('minimal', False):
        print("✅ Pytest está funcionando básico")
        
        if not results.get('discovery', False):
            print("❌ Problema na descoberta de testes")
            print("   • Verifique a estrutura do diretório tests/")
            print("   • Verifique se há arquivos __init__.py")
            print("   • Verifique configuração do pytest")
        
        if not results.get('specific_file', False):
            print("❌ Problema em arquivo de teste específico")
            print("   • Verifique imports nos arquivos de teste")
            print("   • Execute: python -c 'from app.config import settings'")
    
    else:
        print("❌ Pytest não está funcionando nem em casos simples")
        print("   • Reinstale pytest: pip install --force-reinstall pytest")
        print("   • Verifique ambiente virtual")
        print("   • Verifique versão do Python")
    
    print("\n🎯 PRÓXIMO PASSO:")
    if results.get('simple_test', False):
        print("Execute: python -m pytest tests/test_simple_verification.py -v")
    else:
        print("Execute: pip install --force-reinstall pytest pytest-cov")


if __name__ == "__main__":
    main()