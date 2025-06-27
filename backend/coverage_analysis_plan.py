import json
import os
import subprocess
import sys
from pathlib import Path

def get_detailed_coverage():
    """Obtém cobertura detalhada por arquivo"""
    print("📊 ANALISANDO COBERTURA DETALHADA")
    print("="*60)
    
    # Executar pytest com relatório detalhado
    print("\n🔄 Gerando relatório de cobertura detalhado...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/', 
         '--cov=app',
         '--cov-report=term-missing',
         '--cov-report=json',
         '-q'  # Quiet mode
        ],
        capture_output=True,
        text=True
    )
    
    # Analisar coverage.json
    if not os.path.exists('coverage.json'):
        print("❌ coverage.json não encontrado")
        return None
    
    with open('coverage.json', 'r') as f:
        coverage_data = json.load(f)
    
    return coverage_data

def analyze_coverage_by_module(coverage_data):
    """Analisa cobertura por módulo"""
    print("\n📊 COBERTURA POR MÓDULO")
    print("="*60)
    
    modules = {
        'services': [],
        'models': [],
        'api': [],
        'repositories': [],
        'schemas': [],
        'core': [],
        'utils': [],
        'modules': []
    }
    
    # Categorizar arquivos
    for file_path, file_data in coverage_data.get('files', {}).items():
        if not file_path.startswith('app/'):
            continue
            
        percent = file_data['summary']['percent_covered']
        statements = file_data['summary']['num_statements']
        missing = file_data['summary']['missing_lines']
        
        # Determinar categoria
        for category in modules.keys():
            if f'/{category}/' in file_path or f'\\{category}\\' in file_path:
                modules[category].append({
                    'file': file_path,
                    'percent': percent,
                    'statements': statements,
                    'missing': missing
                })
                break
    
    # Mostrar resumo por módulo
    for module, files in modules.items():
        if files:
            avg_coverage = sum(f['percent'] for f in files) / len(files)
            total_statements = sum(f['statements'] for f in files)
            total_missing = sum(f['missing'] for f in files)
            
            print(f"\n📁 {module.upper()}:")
            print(f"   • Arquivos: {len(files)}")
            print(f"   • Cobertura média: {avg_coverage:.1f}%")
            print(f"   • Linhas totais: {total_statements}")
            print(f"   • Linhas não cobertas: {total_missing}")
            
            # Mostrar piores arquivos do módulo
            worst_files = sorted(files, key=lambda x: x['percent'])[:3]
            if worst_files:
                print("   • Arquivos com menor cobertura:")
                for f in worst_files:
                    file_name = os.path.basename(f['file'])
                    print(f"     - {file_name}: {f['percent']:.1f}% ({f['missing']} linhas faltando)")

def identify_priority_files(coverage_data):
    """Identifica arquivos prioritários para testes"""
    print("\n" + "="*60)
    print("🎯 ARQUIVOS PRIORITÁRIOS PARA TESTES")
    print("="*60)
    
    # Coletar todos os arquivos com suas métricas
    files_metrics = []
    
    for file_path, file_data in coverage_data.get('files', {}).items():
        if not file_path.startswith('app/'):
            continue
            
        percent = file_data['summary']['percent_covered']
        statements = file_data['summary']['num_statements']
        missing = file_data['summary']['missing_lines']
        
        # Calcular score de prioridade (quanto maior, mais prioritário)
        # Considera: tamanho do arquivo, cobertura atual e tipo de arquivo
        priority_score = missing  # Linhas não cobertas
        
        # Boost para arquivos importantes
        if 'service' in file_path:
            priority_score *= 2
        elif 'api' in file_path:
            priority_score *= 1.8
        elif 'core' in file_path:
            priority_score *= 1.5
        
        files_metrics.append({
            'file': file_path,
            'percent': percent,
            'statements': statements,
            'missing': missing,
            'priority_score': priority_score
        })
    
    # Ordenar por prioridade
    files_metrics.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Mostrar top 20 arquivos prioritários
    print("\n🔝 TOP 20 ARQUIVOS PARA ADICIONAR TESTES:")
    print("(Ordenados por impacto potencial na cobertura)\n")
    
    total_missing = sum(f['missing'] for f in files_metrics)
    cumulative_missing = 0
    
    for i, file_info in enumerate(files_metrics[:20], 1):
        file_name = file_info['file'].replace('app/', '')
        cumulative_missing += file_info['missing']
        impact = (file_info['missing'] / total_missing) * 100 if total_missing > 0 else 0
        cumulative_impact = (cumulative_missing / total_missing) * 100 if total_missing > 0 else 0
        
        print(f"{i:2d}. {file_name}")
        print(f"    • Cobertura atual: {file_info['percent']:.1f}%")
        print(f"    • Linhas faltando: {file_info['missing']}")
        print(f"    • Impacto na cobertura: +{impact:.1f}%")
        print(f"    • Impacto acumulado: {cumulative_impact:.1f}%")
        print()

def create_test_templates():
    """Cria templates de teste para os arquivos prioritários"""
    print("\n" + "="*60)
    print("🔧 CRIANDO TEMPLATES DE TESTE")
    print("="*60)
    
    # Template para serviços
    service_template = '''"""
Tests for {service_name}
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.{module_path} import {class_name}

class Test{class_name}:
    """Test cases for {class_name}"""
    
    @pytest.fixture
    def service(self):
        """Create service instance with mocked dependencies"""
        # TODO: Add mock dependencies
        return {class_name}()
    
    @pytest.mark.asyncio
    async def test_example_method(self, service):
        """Test example method"""
        # Arrange
        expected = "expected_result"
        
        # Act
        result = await service.example_method()
        
        # Assert
        assert result == expected
    
    # TODO: Add more test methods
'''
    
    # Criar diretório para novos testes
    new_tests_dir = Path('tests/new_tests')
    new_tests_dir.mkdir(exist_ok=True)
    
    print(f"\n✅ Criado diretório: {new_tests_dir}")
    print("\n📝 Para começar a aumentar a cobertura:")
    print("1. Escolha um arquivo da lista de prioridades acima")
    print("2. Crie um arquivo de teste correspondente")
    print("3. Use o template apropriado como base")
    print("4. Execute: pytest tests/test_novo_arquivo.py -v")

def generate_action_plan(coverage_data):
    """Gera plano de ação para atingir 80% de cobertura"""
    print("\n" + "="*60)
    print("📋 PLANO DE AÇÃO PARA ATINGIR 80% DE COBERTURA")
    print("="*60)
    
    current_coverage = coverage_data['totals']['percent_covered']
    total_statements = coverage_data['totals']['num_statements']
    covered_lines = coverage_data['totals']['covered_lines']
    missing_lines = coverage_data['totals']['missing_lines']
    
    # Calcular quantas linhas precisamos cobrir
    target_coverage = 80.0
    lines_needed = (target_coverage / 100 * total_statements) - covered_lines
    
    print(f"\n📊 Situação Atual:")
    print(f"   • Cobertura: {current_coverage:.1f}%")
    print(f"   • Linhas cobertas: {covered_lines:,}")
    print(f"   • Linhas não cobertas: {missing_lines:,}")
    
    print(f"\n🎯 Meta:")
    print(f"   • Cobertura alvo: {target_coverage}%")
    print(f"   • Linhas adicionais necessárias: {int(lines_needed):,}")
    print(f"   • Percentual de linhas faltantes a cobrir: {(lines_needed/missing_lines*100):.1f}%")
    
    print(f"\n📈 Estratégia Recomendada:")
    print(f"\n1. FASE 1 - Quick Wins (1-2 dias):")
    print(f"   • Focar nos arquivos pequenos com 0% de cobertura")
    print(f"   • Adicionar testes para funções utilitárias simples")
    print(f"   • Meta: Alcançar 35-40% de cobertura")
    
    print(f"\n2. FASE 2 - Serviços Core (3-5 dias):")
    print(f"   • Testar os serviços principais (ECG, Patient, User)")
    print(f"   • Mockar dependências externas")
    print(f"   • Meta: Alcançar 50-60% de cobertura")
    
    print(f"\n3. FASE 3 - APIs e Integrações (3-5 dias):")
    print(f"   • Testar endpoints da API")
    print(f"   • Adicionar testes de integração")
    print(f"   • Meta: Alcançar 70-75% de cobertura")
    
    print(f"\n4. FASE 4 - Finalização (2-3 dias):")
    print(f"   • Cobrir casos extremos")
    print(f"   • Adicionar testes para error handling")
    print(f"   • Meta: Ultrapassar 80% de cobertura")

def main():
    """Função principal"""
    # Obter dados de cobertura
    coverage_data = get_detailed_coverage()
    
    if not coverage_data:
        print("❌ Não foi possível obter dados de cobertura")
        return
    
    # Análises
    analyze_coverage_by_module(coverage_data)
    identify_priority_files(coverage_data)
    create_test_templates()
    generate_action_plan(coverage_data)
    
    print("\n" + "="*60)
    print("✅ ANÁLISE COMPLETA")
    print("="*60)
    
    print("\n🚀 PRÓXIMO COMANDO RECOMENDADO:")
    print("pytest tests/ --cov=app --cov-report=html && start htmlcov/index.html")

if __name__ == "__main__":
    main()