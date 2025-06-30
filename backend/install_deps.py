#!/usr/bin/env python3
"""
Instala todas as dependências necessárias para o MedAI
"""
import subprocess
import sys
import os

def install_packages():
    """Instala todos os pacotes necessários"""
    
    # Lista de pacotes essenciais
    packages = [
        # Database
        "sqlalchemy==2.0.23",
        "alembic==1.13.0",
        "psycopg2-binary==2.9.9",
        
        # FastAPI
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "python-multipart==0.0.6",
        
        # Security
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "email-validator==2.1.0",
        
        # Redis
        "redis==5.0.1",
        "aioredis==2.0.1",
        
        # ML/Data Science
        "numpy==1.26.2",
        "pandas==2.1.4",
        "scikit-learn==1.3.2",
        
        # Utils
        "python-dotenv==1.0.0",
        
        # Testing (já instaladas mas garantindo)
        "pytest==7.4.3",
        "pytest-cov==4.1.0",
        "pytest-asyncio==0.21.1",
        "pytest-mock==3.12.0",
        "httpx==0.25.2",
        "faker==20.1.0",
        "sqlalchemy-utils==0.41.1",
        "coverage==7.3.4"
    ]
    
    print("📦 Instalando dependências do MedAI...\n")
    
    # Determinar o executável pip
    if os.path.exists("medai_env\\Scripts\\pip.exe"):
        pip_cmd = "medai_env\\Scripts\\pip.exe"
    elif os.path.exists("venv\\Scripts\\pip.exe"):
        pip_cmd = "venv\\Scripts\\pip.exe"
    else:
        pip_cmd = "pip"
    
    # Atualizar pip primeiro
    print("📦 Atualizando pip...")
    subprocess.run([pip_cmd, "install", "--upgrade", "pip"])
    
    # Instalar pacotes
    failed_packages = []
    
    for package in packages:
        print(f"\n📦 Instalando {package}...")
        result = subprocess.run([pip_cmd, "install", package], capture_output=True)
        
        if result.returncode != 0:
            print(f"❌ Erro ao instalar {package}")
            failed_packages.append(package)
        else:
            print(f"✅ {package} instalado com sucesso!")
    
    print("\n" + "="*60)
    
    if failed_packages:
        print("❌ Alguns pacotes falharam na instalação:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        print("\nTente instalar manualmente com:")
        print(f"{pip_cmd} install {' '.join(failed_packages)}")
    else:
        print("✅ Todas as dependências foram instaladas com sucesso!")
        print("\n🚀 Agora você pode executar os testes com:")
        print("medai_env\\Scripts\\python.exe run_tests.py")
    
    print("="*60)

if __name__ == "__main__":
    # Verificar se está na pasta correta
    if not os.path.exists("app"):
        print("❌ Erro: Execute este script na pasta backend do MedAI!")
        sys.exit(1)
    
    install_packages()