#!/usr/bin/env python
"""
Script para executar os testes do projeto MedAI.
Versão compatível com Windows (sem caracteres Unicode problemáticos).
"""

import sys
import os
import subprocess
from pathlib import Path

# Configura codificação UTF-8 para saída
if sys.platform == "win32":
    # Força UTF-8 no Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    """Função principal."""
    print("[TESTE] MedAI - Executando Testes\n")
    
    # Adiciona o diretório backend ao Python path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    os.environ['PYTHONPATH'] = str(backend_dir)
    
    print(f"[OK] PYTHONPATH configurado: {backend_dir}")
    
    # Verifica se pytest está instalado
    try:
        import pytest
        print("[OK] pytest encontrado")
    except ImportError:
        print("[ERRO] pytest nao esta instalado!")
        print("Execute: pip install pytest")
        return 1
    
    # Verifica se o arquivo de teste existe
    test_file = backend_dir / "tests" / "test_utilities.py"
    
    if test_file.exists():
        print(f"[OK] Arquivo de teste encontrado: {test_file}")
    else:
        print(f"[ERRO] Arquivo de teste nao encontrado: {test_file}")
        return 1
    
    # Executa os testes
    print("\n" + "="*60)
    print("EXECUTANDO TESTES")
    print("="*60 + "\n")
    
    # Argumentos do pytest
    pytest_args = [
        str(test_file),
        "-v",  # Verbose
        "--tb=short",  # Traceback curto
        "--no-header",  # Remove cabeçalho do pytest
    ]
    
    # Se a saída estiver sendo redirecionada, adiciona opções extras
    if not sys.stdout.isatty():
        pytest_args.extend([
            "--color=no",  # Desativa cores quando redireciona
            "-q",  # Modo mais silencioso
        ])
    
    # Executa pytest
    exit_code = pytest.main(pytest_args)
    
    # Resultado final
    print("\n" + "="*60)
    if exit_code == 0:
        print("[SUCESSO] Todos os testes passaram!")
    else:
        print("[FALHA] Alguns testes falharam.")
    print("="*60)
    
    return exit_code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERRO] Erro ao executar testes: {e}")
        sys.exit(1)