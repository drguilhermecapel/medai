#!/usr/bin/env python
"""
Script para executar os testes do projeto MedAI.
"""

import sys
import os
import subprocess
from pathlib import Path


def setup_environment():
    """Configura o ambiente para execução dos testes."""
    # Adiciona o diretório backend ao PYTHONPATH
    backend_dir = Path(__file__).parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    # Define variável de ambiente
    os.environ["PYTHONPATH"] = str(backend_dir)
    
    print(f"✓ PYTHONPATH configurado: {backend_dir}")


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    required_packages = ["pytest", "numpy", "scipy"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install " + " ".join(missing_packages))
        return False
    
    print("✓ Todas as dependências básicas estão instaladas")
    return True


def create_missing_directories():
    """Cria diretórios necessários se não existirem."""
    directories = [
        "app",
        "app/utils",
        "tests"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Diretório criado: {directory}")
            
            # Cria __init__.py
            init_file = path / "__init__.py"
            if not init_file.exists():
                init_file.write_text("""Package initialization.""")


def run_tests(args=None):
    """Executa os testes usando pytest."""
    if args is None:
        args = []
    
    # Comando básico do pytest
    cmd = [sys.executable, "-m", "pytest"]
    
    # Adiciona argumentos padrão
    default_args = [
        "-v",  # Verbose
        "--tb=short",  # Traceback curto
        "--color=yes",  # Saída colorida
    ]
    
    # Adiciona argumentos do usuário
    cmd.extend(default_args)
    cmd.extend(args)
    
    # Adiciona o arquivo de teste específico se não houver argumentos
    if not args:
        test_file = Path("tests/test_utilities.py")
        if test_file.exists():
            cmd.append(str(test_file))
    
    print(f"\n📋 Executando: {' '.join(cmd)}\n")
    
    # Executa os testes
    result = subprocess.run(cmd)
    
    return result.returncode


def main():
    """Função principal."""
    print("🧪 MedAI - Executando Testes\n")
    
    # Configura ambiente
    setup_environment()
    
    # Verifica dependências
    if not check_dependencies():
        print("\n❌ Instale as dependências antes de executar os testes.")
        return 1
    
    # Cria diretórios necessários
    create_missing_directories()
    
    # Argumentos da linha de comando
    args = sys.argv[1:]
    
    # Opções especiais
    if "--coverage" in args:
        args.remove("--coverage")
        args.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
        print("📊 Executando com análise de cobertura...\n")
    
    if "--markers" in args:
        # Lista marcadores disponíveis
        subprocess.run([sys.executable, "-m", "pytest", "--markers"])
        return 0
    
    if "--help" in args or "-h" in args:
        print("Uso: python run_tests.py [opções]")
        print("\nOpções:")
        print("  --coverage    Executa com análise de cobertura")
        print("  --markers     Lista marcadores disponíveis")
        print("  -k EXPR       Executa apenas testes que correspondem à expressão")
        print("  -m MARKER     Executa apenas testes com o marcador especificado")
        print("  -x            Para na primeira falha")
        print("  --pdb         Abre debugger em falhas")
        print("\nExemplos:")
        print("  python run_tests.py")
        print("  python run_tests.py -k test_normalize")
        print("  python run_tests.py -m unit")
        print("  python run_tests.py --coverage")
        return 0
    
    # Executa os testes
    exit_code = run_tests(args)
    
    if exit_code == 0:
        print("\n✅ Todos os testes passaram!")
    else:
        print("\n❌ Alguns testes falharam.")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

