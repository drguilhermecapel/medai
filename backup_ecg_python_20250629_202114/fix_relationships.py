# check_passing_tests.py
import subprocess
import os

def run_test_file(test_file):
    """Executa um arquivo de teste e retorna estatísticas"""
    try:
        result = subprocess.run(
            ['pytest', test_file, '--tb=no', '-q'],
            capture_output=True,
            text=True
        )
        
        output = result.stdout + result.stderr
        
        # Extrair estatísticas
        passed = output.count('passed')
        failed = output.count('failed')
        errors = output.count('error')
        
        return {
            'file': test_file,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'total': passed + failed + errors
        }
    except Exception as e:
        return {
            'file': test_file,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'total': 0,
            'exception': str(e)
        }

def main():
    print("Verificando quais testes estão passando...\n")
    
    test_dir = 'tests'
    if not os.path.exists(test_dir):
        print(f"Diretório {test_dir} não encontrado!")
        return
    
    # Listar todos os arquivos de teste
    test_files = [
        os.path.join(test_dir, f) 
        for f in os.listdir(test_dir) 
        if f.startswith('test_') and f.endswith('.py')
    ]
    
    results = []
    total_passed = 0
    total_failed = 0
    total_errors = 0
    
    print("Executando testes...\n")
    
    for test_file in sorted(test_files):
        print(f"Testando {test_file}...", end='', flush=True)
        result = run_test_file(test_file)
        results.append(result)
        
        total_passed += result['passed']
        total_failed += result['failed']
        total_errors += result['errors']
        
        print(f" ✓ {result['passed']} passed, ✗ {result['failed']} failed, ⚠ {result['errors']} errors")
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    # Arquivos com mais testes passando
    print("\n📊 Arquivos com MAIS testes passando:")
    for r in sorted(results, key=lambda x: x['passed'], reverse=True)[:5]:
        if r['passed'] > 0:
            print(f"  {r['file']}: {r['passed']} passed")
    
    # Arquivos com todos os testes passando
    print("\n✅ Arquivos com TODOS os testes passando:")
    for r in results:
        if r['total'] > 0 and r['failed'] == 0 and r['errors'] == 0:
            print(f"  {r['file']}: {r['passed']} testes")
    
    # Estatísticas totais
    print(f"\n📈 TOTAIS:")
    print(f"  ✓ Passed: {total_passed}")
    print(f"  ✗ Failed: {total_failed}")
    print(f"  ⚠ Errors: {total_errors}")
    print(f"  📊 Taxa de sucesso: {total_passed / (total_passed + total_failed + total_errors) * 100:.1f}%")
    
    # Sugestões
    print("\n💡 SUGESTÕES:")
    if total_passed > 100:
        print("  ✓ Boa quantidade de testes passando!")
    
    problem_files = [r for r in results if r['failed'] > 5 or r['errors'] > 5]
    if problem_files:
        print("\n  Arquivos com muitos problemas:")
        for r in problem_files[:3]:
            print(f"    - {r['file']} ({r['failed']} failed, {r['errors']} errors)")
        print("\n  Execute esses arquivos individualmente para ver os erros:")
        print(f"    pytest {problem_files[0]['file']} -v --tb=short")

if __name__ == "__main__":
    main()