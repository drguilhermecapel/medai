#!/usr/bin/env python3
"""
Script automático para executar testes do MedAI sem precisar ativar ambiente virtual
"""
import os
import sys
import subprocess
import platform


def get_python_executable():
    """Retorna o executável Python do ambiente virtual"""
    if platform.system() == "Windows":
        venv_paths = [
            "medai_env\\Scripts\\python.exe",
            "venv\\Scripts\\python.exe"
        ]
    else:
        venv_paths = [
            "medai_env/bin/python",
            "venv/bin/python"
        ]
    
    for path in venv_paths:
        if os.path.exists(path):
            return path
    
    return None


def check_and_install_dependencies():
    """Verifica e instala dependências se necessário"""
    python_exe = get_python_executable()
    
    if not python_exe:
        print("❌ Ambiente virtual não encontrado!")
        print("\nCriando ambiente virtual...")
        subprocess.run([sys.executable, "-m", "venv", "medai_env"])
        python_exe = get_python_executable()
    
    print("📦 Verificando dependências...")
    
    # Verifica se pytest está instalado
    try:
        subprocess.run(
            [python_exe, "-c", "import pytest"],
            check=True,
            capture_output=True
        )
        print("✅ Dependências já instaladas!")
    except:
        print("📦 Instalando dependências...")
        pip_exe = python_exe.replace("python.exe", "pip.exe") if platform.system() == "Windows" else python_exe.replace("python", "pip")
        
        # Instala dependências essenciais
        deps = [
            "pytest==7.4.3",
            "pytest-cov==4.1.0",
            "pytest-asyncio==0.21.1",
            "pytest-mock==3.12.0",
            "httpx==0.25.2",
            "faker==20.1.0",
            "sqlalchemy-utils==0.41.1",
            "coverage==7.3.4",
            "python-dotenv==1.0.0"
        ]
        
        for dep in deps:
            print(f"  Instalando {dep}...")
            subprocess.run([pip_exe, "install", dep])
        
        print("✅ Dependências instaladas!")
    
    return python_exe


def run_tests():
    """Executa os testes"""
    python_exe = check_and_install_dependencies()
    
    print("\n🚀 Executando testes...\n")
    print("="*60)
    
    # Executa run_tests.py com o Python do ambiente virtual
    if os.path.exists("run_tests.py"):
        subprocess.run([python_exe, "run_tests.py"])
    else:
        # Se não existir run_tests.py, executa pytest diretamente
        subprocess.run([
            python_exe, "-m", "pytest",
            "-v",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])
    
    print("\n="*60)
    print("✅ Testes concluídos!")
    print("\n📊 Relatório de cobertura disponível em: htmlcov/index.html")


def main():
    """Função principal"""
    # Verifica se está na pasta correta
    if not os.path.exists("app"):
        print("❌ Erro: Execute este script na pasta backend do projeto MedAI!")
        print("   Pasta atual:", os.getcwd())
        
        # Tenta navegar para a pasta correta
        backend_path = "C:\\Users\\lucie\\Documents\\GitHub\\medai\\backend"
        if os.path.exists(backend_path):
            print(f"\n📁 Mudando para: {backend_path}")
            os.chdir(backend_path)
        else:
            sys.exit(1)
    
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro ao executar testes: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()