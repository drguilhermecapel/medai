import subprocess
import sys
import re
import json
import os

def run_all_tests_with_coverage():
    """Executa todos os testes com análise de cobertura"""
    print("🚀 EXECUTANDO TODOS OS TESTES COM COBERTURA")
    print("="*60)
    
    # Executar com cobertura
    print("\n📊 Executando pytest com cobertura...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/', 
         '-v',
         '--tb=short',
         '--cov=app',
         '--cov-report=term',
         '--cov-report=html',
         '--cov-report=json',
         '-x',  # Para no primeiro erro para não demorar muito
         '--maxfail=50'  # Máximo de 50 falhas
        ],
        capture_output=True,
        text=True
    )
    
    # Analisar resultados
    print("\n" + "="*60)
    print("📊 RESULTADOS DOS TESTES")
    print("="*60)
    
    # Extrair estatísticas do output
    output_lines = result.stdout.split('\n')
    
    # Procurar linha de resumo
    for line in output_lines:
        if 'passed' in line and ('failed' in line or 'error' in line or 'skipped' in line):
            print(f"\n📊 {line.strip()}")
            
            # Extrair números usando regex
            passed = re.search(r'(\d+) passed', line)
            failed = re.search(r'(\d+) failed', line)
            errors = re.search(r'(\d+) error', line)
            skipped = re.search(r'(\d+) skipped', line)
            
            total_passed = int(passed.group(1)) if passed else 0
            total_failed = int(failed.group(1)) if failed else 0
            total_errors = int(errors.group(1)) if errors else 0
            total_skipped = int(skipped.group(1)) if skipped else 0
            
            total = total_passed + total_failed + total_errors
            
            print(f"\n📈 Análise:")
            print(f"   ✅ Passou: {total_passed}")
            print(f"   ❌ Falhou: {total_failed}")
            print(f"   ⚠️  Erros: {total_errors}")
            print(f"   ⏭️  Pulados: {total_skipped}")
            print(f"   📊 Total executado: {total}")
            
            if total > 0:
                success_rate = (total_passed / total) * 100
                print(f"   🎯 Taxa de sucesso: {success_rate:.1f}%")
            
            break
    
    # Analisar cobertura
    print("\n" + "="*60)
    print("📊 ANÁLISE DE COBERTURA")
    print("="*60)
    
    # Procurar linha de cobertura total
    for line in output_lines:
        if 'TOTAL' in line and '%' in line:
            print(f"\n📊 {line.strip()}")
            
            # Extrair porcentagem
            coverage_match = re.search(r'(\d+)%', line)
            if coverage_match:
                coverage = int(coverage_match.group(1))
                print(f"\n🎯 Cobertura Total: {coverage}%")
                
                if coverage >= 80:
                    print("   ✅ Meta de 80% ATINGIDA!")
                else:
                    print(f"   ⚠️  Faltam {80 - coverage}% para atingir a meta")
            break
    
    # Analisar arquivo JSON de cobertura se existir
    if os.path.exists('coverage.json'):
        analyze_coverage_details()
    
    return result

def analyze_coverage_details():
    """Analisa detalhes da cobertura do arquivo JSON"""
    print("\n" + "="*60)
    print("📊 DETALHES DA COBERTURA")
    print("="*60)
    
    try:
        with open('coverage.json', 'r') as f:
            coverage_data = json.load(f)
        
        # Estatísticas gerais
        total_percent = coverage_data.get('totals', {}).get('percent_covered', 0)
        total_lines = coverage_data.get('totals', {}).get('num_statements', 0)
        covered_lines = coverage_data.get('totals', {}).get('covered_lines', 0)
        missing_lines = coverage_data.get('totals', {}).get('missing_lines', 0)
        
        print(f"\n📈 Estatísticas Gerais:")
        print(f"   • Cobertura Total: {total_percent:.1f}%")
        print(f"   • Linhas Totais: {total_lines}")
        print(f"   • Linhas Cobertas: {covered_lines}")
        print(f"   • Linhas Não Cobertas: {missing_lines}")
        
        # Arquivos com menor cobertura
        print("\n📊 Arquivos com MENOR cobertura (<50%):")
        files = []
        for file_path, file_data in coverage_data.get('files', {}).items():
            if 'app/' in file_path:
                percent = file_data['summary']['percent_covered']
                if percent < 50:
                    files.append((file_path, percent))
        
        # Ordenar por cobertura
        files.sort(key=lambda x: x[1])
        
        for file_path, percent in files[:10]:  # Top 10 piores
            file_name = file_path.replace('app/', '')
            print(f"   • {file_name}: {percent:.1f}%")
        
        # Arquivos com maior cobertura
        print("\n✅ Arquivos com MAIOR cobertura (>80%):")
        good_files = []
        for file_path, file_data in coverage_data.get('files', {}).items():
            if 'app/' in file_path:
                percent = file_data['summary']['percent_covered']
                if percent > 80:
                    good_files.append((file_path, percent))
        
        # Ordenar por cobertura (decrescente)
        good_files.sort(key=lambda x: x[1], reverse=True)
        
        for file_path, percent in good_files[:10]:  # Top 10 melhores
            file_name = file_path.replace('app/', '')
            print(f"   • {file_name}: {percent:.1f}%")
            
    except Exception as e:
        print(f"❌ Erro ao analisar coverage.json: {e}")

def show_failed_tests(result):
    """Mostra os testes que falharam"""
    print("\n" + "="*60)
    print("❌ TESTES QUE FALHARAM")
    print("="*60)
    
    lines = result.stdout.split('\n')
    failed_tests = []
    
    for line in lines:
        if 'FAILED' in line and '::' in line:
            # Extrair nome do teste
            test_name = line.split(' ')[0]
            if test_name.startswith('tests/'):
                failed_tests.append(test_name)
    
    if failed_tests:
        print(f"\nTotal de testes falhando: {len(failed_tests)}")
        print("\nPrimeiros 10 testes que falharam:")
        for test in failed_tests[:10]:
            print(f"   • {test}")
        
        if len(failed_tests) > 10:
            print(f"   ... e mais {len(failed_tests) - 10} testes")
    else:
        print("\n✅ Nenhum teste falhou!")

def generate_recommendations():
    """Gera recomendações baseadas nos resultados"""
    print("\n" + "="*60)
    print("📋 RECOMENDAÇÕES")
    print("="*60)
    
    print("\n1. Para aumentar a cobertura:")
    print("   • Foque nos arquivos com menos de 50% de cobertura")
    print("   • Escreva testes unitários para funções não testadas")
    print("   • Use: pytest tests/ --cov=app --cov-report=html")
    print("   • Abra: htmlcov/index.html no navegador")
    
    print("\n2. Para corrigir testes falhando:")
    print("   • Execute um teste específico: pytest tests/test_file.py::test_name -vvs")
    print("   • Veja o erro completo: pytest tests/ --tb=long")
    print("   • Pule testes problemáticos: pytest tests/ -k 'not nome_do_teste'")
    
    print("\n3. Para melhorar a qualidade:")
    print("   • Adicione mais asserções nos testes existentes")
    print("   • Teste casos extremos (edge cases)")
    print("   • Adicione testes de integração")
    
    print("\n4. Próximo comando útil:")
    print("   pytest tests/ --cov=app --cov-report=html --cov-report=term-missing")

def main():
    """Função principal"""
    # Executar testes
    result = run_all_tests_with_coverage()
    
    # Mostrar testes que falharam
    show_failed_tests(result)
    
    # Gerar recomendações
    generate_recommendations()
    
    print("\n" + "="*60)
    print("✅ ANÁLISE COMPLETA FINALIZADA")
    print("="*60)

if __name__ == "__main__":
    main()