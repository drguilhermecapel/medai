#!/usr/bin/env python3
"""
Script para analisar a queda na cobertura de testes
"""

import os
import json
import subprocess
from pathlib import Path
from collections import defaultdict

def analyze_current_coverage():
    """Analisa a cobertura atual detalhadamente"""
    print("🔍 EXECUTANDO ANÁLISE DETALHADA DA COBERTURA")
    print("=" * 60)
    
    # Executar testes com cobertura completa
    result = subprocess.run([
        "python", "-m", "pytest", "tests/",
        "--cov=app",
        "--cov-report=json:coverage_detailed.json",
        "--cov-report=html:htmlcov_detailed",
        "--cov-report=term-missing",
        "-v"
    ], capture_output=True, text=True)
    
    print("📤 OUTPUT DO PYTEST:")
    print(result.stdout[-1000:])  # Últimas 1000 chars
    
    if result.stderr:
        print("\n⚠️ ERROS/WARNINGS:")
        print(result.stderr[-500:])
    
    # Analisar arquivo JSON de cobertura
    if os.path.exists('coverage_detailed.json'):
        analyze_coverage_json()
    
    return result.returncode == 0

def analyze_coverage_json():
    """Analisa detalhes do arquivo JSON de cobertura"""
    print("\n📊 ANÁLISE DETALHADA POR ARQUIVO:")
    print("=" * 60)
    
    with open('coverage_detailed.json', 'r') as f:
        coverage_data = json.load(f)
    
    total_coverage = coverage_data['totals']['percent_covered']
    print(f"📈 Cobertura Total Atual: {total_coverage:.2f}%")
    
    files_by_coverage = []
    
    for file_path, file_data in coverage_data['files'].items():
        if 'app/' in file_path and not file_path.endswith('__init__.py'):
            coverage_percent = file_data['summary']['percent_covered']
            statements = file_data['summary']['num_statements']
            missing_lines = file_data['summary']['missing_lines']
            
            files_by_coverage.append({
                'file': file_path.replace('app/', ''),
                'coverage': coverage_percent,
                'statements': statements,
                'missing': missing_lines
            })
    
    # Ordenar por cobertura (pior primeiro)
    files_by_coverage.sort(key=lambda x: x['coverage'])
    
    print(f"\n🔴 TOP 15 ARQUIVOS COM MENOR COBERTURA:")
    print("-" * 60)
    for i, file_info in enumerate(files_by_coverage[:15], 1):
        print(f"{i:2}. {file_info['file']:<40} {file_info['coverage']:5.1f}% "
              f"({file_info['missing']:3} linhas faltando)")
    
    print(f"\n✅ TOP 10 ARQUIVOS COM MELHOR COBERTURA:")
    print("-" * 60)
    for i, file_info in enumerate(files_by_coverage[-10:], 1):
        print(f"{i:2}. {file_info['file']:<40} {file_info['coverage']:5.1f}%")
    
    # Calcular impacto para chegar a 93%
    calculate_impact_to_93_percent(coverage_data)

def calculate_impact_to_93_percent(coverage_data):
    """Calcula o que precisa ser feito para chegar a 93%"""
    print(f"\n🎯 CÁLCULO PARA ATINGIR 93% DE COBERTURA:")
    print("=" * 60)
    
    totals = coverage_data['totals']
    current_coverage = totals['percent_covered']
    total_statements = totals['num_statements']
    covered_lines = totals['covered_lines']
    
    # Calcular linhas necessárias para 93%
    target_coverage = 93.0
    lines_needed_for_93 = (target_coverage / 100 * total_statements) - covered_lines
    
    print(f"📊 Situação Atual:")
    print(f"   • Cobertura atual: {current_coverage:.2f}%")
    print(f"   • Total de linhas: {total_statements:,}")
    print(f"   • Linhas cobertas: {covered_lines:,}")
    print(f"   • Gap para 93%: {target_coverage - current_coverage:.2f} pontos percentuais")
    print(f"   • Linhas adicionais necessárias: {int(lines_needed_for_93):,}")
    
    # Identificar arquivos de maior impacto
    files_impact = []
    for file_path, file_data in coverage_data['files'].items():
        if 'app/' in file_path:
            missing = file_data['summary']['missing_lines']
            if missing > 0:
                impact = (missing / total_statements) * 100
                files_impact.append({
                    'file': file_path.replace('app/', ''),
                    'missing_lines': missing,
                    'impact_percent': impact
                })
    
    files_impact.sort(key=lambda x: x['impact_percent'], reverse=True)
    
    print(f"\n🎯 TOP 10 ARQUIVOS DE MAIOR IMPACTO PARA 93%:")
    print("-" * 60)
    cumulative_impact = 0
    for i, file_info in enumerate(files_impact[:10], 1):
        cumulative_impact += file_info['impact_percent']
        print(f"{i:2}. {file_info['file']:<35} "
              f"{file_info['missing_lines']:3} linhas "
              f"(+{file_info['impact_percent']:.2f}%)")
        
        if cumulative_impact >= (target_coverage - current_coverage):
            print(f"\n✅ Cobrindo os primeiros {i} arquivos atingiria a meta de 93%!")
            break

def identify_new_files():
    """Identifica arquivos novos que podem estar causando a queda"""
    print(f"\n🆕 IDENTIFICANDO ARQUIVOS POTENCIALMENTE NOVOS:")
    print("=" * 60)
    
    app_files = list(Path('app').rglob('*.py'))
    
    # Arquivos por diretório
    dirs_count = defaultdict(int)
    for file in app_files:
        if not file.name.startswith('__'):
            dir_name = str(file.parent).replace('app/', '') or 'root'
            dirs_count[dir_name] += 1
    
    print("📁 Distribuição de arquivos por diretório:")
    for dir_name, count in sorted(dirs_count.items()):
        print(f"   • {dir_name}: {count} arquivos")
    
    # Arquivos grandes (potenciais problemas)
    large_files = []
    for file in app_files:
        if file.exists():
            size = file.stat().st_size
            if size > 5000:  # Maior que 5KB
                lines = len(file.read_text(encoding='utf-8', errors='ignore').splitlines())
                large_files.append((str(file), lines, size))
    
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n📏 ARQUIVOS GRANDES (>5KB) - Possíveis Novos:")
    print("-" * 60)
    for file_path, lines, size in large_files[:10]:
        file_name = file_path.replace('app/', '')
        print(f"   • {file_name:<40} {lines:4} linhas ({size:,} bytes)")

def main():
    """Executa análise completa"""
    print("🚨 DIAGNÓSTICO COMPLETO DA QUEDA DE COBERTURA")
    print("=" * 60)
    print("Objetivo: Identificar causas da queda de 93% → 73%")
    print("=" * 60)
    
    # 1. Verificar se estamos na pasta correta
    if not os.path.exists('app') or not os.path.exists('tests'):
        print("❌ Execute este script na pasta 'backend' do projeto MEDAI!")
        return
    
    # 2. Identificar arquivos novos/grandes
    identify_new_files()
    
    # 3. Analisar cobertura atual
    analyze_current_coverage()
    
    print(f"\n🎯 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("=" * 60)
    print("1. Verifique o relatório HTML: abra 'htmlcov_detailed/index.html'")
    print("2. Foque nos arquivos de maior impacto listados acima")
    print("3. Execute o próximo script de correção")
    print("4. Verifique se há arquivos de migração/config sendo incluídos")

if __name__ == "__main__":
    main()

