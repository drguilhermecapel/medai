import subprocess
import sys
import json
import os

def run_coverage_report():
    """Executa relatório de cobertura completo"""
    print("EXECUTANDO RELATORIO DE COBERTURA")
    print("="*60)
    
    # Executar pytest com cobertura
    print("\nGerando relatorio...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/', 
         '--cov=app',
         '--cov-report=term-missing',
         '--cov-report=json',
         '-q'
        ],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    # Mostrar output completo
    print("\nRESULTADO DA COBERTURA:")
    print("-"*60)
    print(result.stdout)
    
    return result

def analyze_json_coverage():
    """Analisa o arquivo JSON de cobertura"""
    print("\n" + "="*60)
    print("ANALISE DETALHADA DO JSON")
    print("="*60)
    
    if not os.path.exists('coverage.json'):
        print("Arquivo coverage.json nao encontrado!")
        return
    
    with open('coverage.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Coletar todos os arquivos
    files = []
    for filepath, filedata in data['files'].items():
        if filepath.startswith('app/'):
            files.append({
                'path': filepath,
                'percent': filedata['summary']['percent_covered'],
                'missing': filedata['summary']['missing_lines'],
                'statements': filedata['summary']['num_statements']
            })
    
    # Ordenar por percentual de cobertura
    files.sort(key=lambda x: (x['percent'], -x['missing']))
    
    # Mostrar arquivos com 0% de cobertura
    print("\nARQUIVOS COM 0% DE COBERTURA:")
    print("-"*60)
    zero_coverage = [f for f in files if f['percent'] == 0]
    
    total_missing_zero = 0
    for i, f in enumerate(zero_coverage, 1):
        filepath = f['path'].replace('app/', '')
        print(f"{i:3d}. {filepath:<50} | {f['statements']:4d} linhas")
        total_missing_zero += f['statements']
    
    print(f"\nTotal: {len(zero_coverage)} arquivos, {total_missing_zero} linhas para cobrir")
    
    # Mostrar arquivos entre 1-50%
    print("\nARQUIVOS COM 1-50% DE COBERTURA:")
    print("-"*60)
    low_coverage = [f for f in files if 0 < f['percent'] <= 50]
    
    for i, f in enumerate(low_coverage[:20], 1):
        filepath = f['path'].replace('app/', '')
        print(f"{i:3d}. {filepath:<50} | {f['percent']:5.1f}% | {f['missing']:4d} linhas faltando")
    
    if len(low_coverage) > 20:
        print(f"... e mais {len(low_coverage) - 20} arquivos")

def create_simple_test():
    """Cria um teste simples como exemplo"""
    print("\n" + "="*60)
    print("CRIANDO TESTE DE EXEMPLO")
    print("="*60)
    
    # Criar diretorio se nao existir
    os.makedirs('app/utils', exist_ok=True)
    
    # Criar arquivo simples para testar
    simple_file = """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""
    
    with open('app/utils/math_utils.py', 'w', encoding='utf-8') as f:
        f.write(simple_file)
    
    # Criar teste
    test_file = """import pytest
from app.utils.math_utils import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6
    assert multiply(0, 100) == 0

def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5
    
    with pytest.raises(ValueError):
        divide(10, 0)
"""
    
    with open('tests/test_math_utils.py', 'w', encoding='utf-8') as f:
        f.write(test_file)
    
    print("Criado: app/utils/math_utils.py")
    print("Criado: tests/test_math_utils.py")
    
    # Executar o teste
    print("\nExecutando teste de exemplo...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/test_math_utils.py', '-v', '--cov=app.utils.math_utils'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    print(result.stdout)

def show_quick_actions():
    """Mostra acoes rapidas para aumentar cobertura"""
    print("\n" + "="*60)
    print("ACOES RAPIDAS PARA AUMENTAR COBERTURA")
    print("="*60)
    
    print("\n1. EXECUTAR TESTE DE EXEMPLO:")
    print("   pytest tests/test_math_utils.py -v --cov=app.utils.math_utils")
    
    print("\n2. VER RELATORIO HTML:")
    print("   pytest tests/ --cov=app --cov-report=html")
    print("   Depois abra: htmlcov/index.html")
    
    print("\n3. TESTAR ARQUIVO ESPECIFICO:")
    print("   pytest tests/ --cov=app.utils -v")
    
    print("\n4. CRIAR MAIS TESTES:")
    print("   - Copie o padrao de tests/test_math_utils.py")
    print("   - Escolha um arquivo com 0% de cobertura")
    print("   - Crie testes para suas funcoes")

def main():
    """Funcao principal"""
    # Executar relatorio
    run_coverage_report()
    
    # Analisar JSON
    analyze_json_coverage()
    
    # Criar exemplo
    create_simple_test()
    
    # Mostrar acoes
    show_quick_actions()

if __name__ == "__main__":
    main()