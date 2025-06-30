#!/usr/bin/env python3
"""
Instala todas as dependências necessárias usando pip como módulo
"""
import subprocess
import sys

def install_package(package):
    """Instala um pacote usando pip como módulo"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("📦 Instalando dependências do MedAI...\n")
    
    # Primeiro, atualizar pip
    print("📦 Atualizando pip...")
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Pacotes essenciais (versão reduzida para começar)
    essential_packages = [
        "sqlalchemy==2.0.23",
        "fastapi==0.104.1",
        "pydantic==2.5.0",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "python-dotenv",
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "httpx"
    ]
    
    print("\n📦 Instalando pacotes essenciais...\n")
    
    failed = []
    
    for package in essential_packages:
        print(f"Instalando {package}...")
        if install_package(package):
            print(f"✅ {package} instalado!\n")
        else:
            print(f"❌ Falha ao instalar {package}\n")
            failed.append(package)
    
    if failed:
        print("\n❌ Alguns pacotes falharam:")
        for pkg in failed:
            print(f"  - {pkg}")
    else:
        print("\n✅ Todos os pacotes foram instalados com sucesso!")
        print("\n🚀 Execute os testes com:")
        print("medai_env\\Scripts\\python.exe run_tests.py")

if __name__ == "__main__":
    main()