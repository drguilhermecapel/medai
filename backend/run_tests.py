#!/usr/bin/env python
"""
Script simplificado para executar os testes do projeto MedAI.
"""

import sys
import os
import subprocess
from pathlib import Path


def main():
    """Função principal."""
    print("🧪 MedAI - Executando Testes\n")
    
    # Adiciona o diretório atual ao PYTHONPATH
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    os.environ['PYTHONPATH'] = str(current_dir)
    
    print(f"✓ PYTHONPATH configurado: {current_dir}")
    
    # Verifica se pytest está instalado
    try:
        import pytest
    except ImportError:
        print("❌ pytest não está instalado!")
        print("Execute: pip install pytest")
        return 1
    
    # Executa os testes
    test_file = current_dir / "tests" / "test_utilities.py"
    
    if test_file.exists():
        print(f"✓ Arquivo de teste encontrado: {test_file}")
        exit_code = pytest.main([str(test_file), "-v", "--tb=short"])
    else:
        print(f"❌ Arquivo de teste não encontrado: {test_file}")
        print("\nExecutando pytest em modo de descoberta...")
        exit_code = pytest.main(["tests/", "-v", "--tb=short"])
    
    if exit_code == 0:
        print("\n✅ Todos os testes passaram!")
    else:
        print("\n❌ Alguns testes falharam.")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
