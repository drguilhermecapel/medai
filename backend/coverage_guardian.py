#!/usr/bin/env python3
"""
Guardian de Cobertura - Previne quedas futuras
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

def create_coverage_baseline():
    """Cria baseline de cobertura para monitoramento"""
    print("📊 Criando baseline de cobertura...")
    
    result = subprocess.run([
        "python", "-m", "pytest", "tests/",
        "--cov=app",
        "--cov-report=json:baseline_93.json"
    ], capture_output=True)
    
    if os.path.exists('baseline_93.json'):
        with open('baseline_93.json', 'r') as f:
            baseline = json.load(f)
        
        # Salvar baseline com timestamp
        baseline['timestamp'] = datetime.now().isoformat()
        baseline['target_coverage'] = 93.0
        
        with open('coverage_baseline.json', 'w') as f:
            json.dump(baseline, f, indent=2)
        
        print(f"✅ Baseline salvo com {baseline['totals']['percent_covered']:.2f}% de cobertura")

def create_pre_commit_hook():
    """Cria hook de pre-commit para verificar cobertura"""
    hook_content = '''#!/bin/sh
# Pre-commit hook para verificar cobertura

echo "🔍 Verificando cobertura de testes..."

# Executar testes com cobertura
python -m pytest tests/ --cov=app --cov-report=json:pre_commit_coverage.json --quiet

if [ ! -f "pre_commit_coverage.json" ]; then
    echo "❌ Erro: Não foi possível gerar relatório de cobertura"
    exit 1
fi

# Extrair cobertura atual
CURRENT_COVERAGE=$(python -c "
import json
with open('pre_commit_coverage.json', 'r') as f:
    data = json.load(f)
print(data['totals']['percent_covered'])
")

# Verificar se caiu abaixo de 90%
if [ $(echo "$CURRENT_COVERAGE < 90" | bc -l) -eq 1 ]; then
    echo "🚨 ALERTA: Cobertura caiu para $CURRENT_COVERAGE%"
    echo "Mínimo requerido: 90%"
    echo "Execute 'python target_93_percent.py' para corrigir"
    exit 1
fi

echo "✅ Cobertura OK: $CURRENT_COVERAGE%"
rm -f pre_commit_coverage.json
exit 0
'''
    
    # Criar diretório .git/hooks se não existir
    hooks_dir = Path('.git/hooks')
    if hooks_dir.exists():
        hook_file = hooks_dir / 'pre-commit'
        hook_file.write_text(hook_content)
        hook_file.chmod(0o755)
        print("✅ Hook de pre-commit instalado")
    else:
        print("⚠️ Diretório .git/hooks não encontrado. Execute 'git init' primeiro.")

def main():
    """Configura sistema de proteção"""
    print("🛡️ CONFIGURANDO PROTEÇÃO CONTRA QUEDAS DE COBERTURA")
    print("=" * 60)
    
    create_coverage_baseline()
    create_pre_commit_hook()
    
    print("\n✅ PROTEÇÕES ATIVADAS:")
    print("   • Baseline de 93% estabelecido")
    print("   • Hook de pre-commit instalado")
    print("   • Alerta automático para quedas abaixo de 90%")

if __name__ == "__main__":
    main()

