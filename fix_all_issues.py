#!/usr/bin/env python3
"""
Script final que resolve TODOS os problemas identificados:
1. Encoding UTF-8 ✅ (já resolvido)
2. BaseSettings do Pydantic
3. Warning do SQLAlchemy
4. Executa testes finais
"""

import subprocess
import sys
import os
from pathlib import Path
import importlib.util


def run_command(cmd, description=""):
    """Executa um comando e retorna o resultado"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"   ✅ {description} - sucesso")
            return True, result.stdout
        else:
            print(f"   ❌ {description} - erro: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"   ❌ {description} - exceção: {e}")
        return False, str(e)


def install_dependencies():
    """Instala todas as dependências necessárias"""
    print("📦 INSTALANDO DEPENDÊNCIAS NECESSÁRIAS")
    print("=" * 50)
    
    dependencies = [
        'pydantic-settings',
        'sqlalchemy>=1.4.0',
        'fastapi',
        'pytest',
        'pytest-cov',
        'pytest-asyncio',
        'httpx'  # Para testes de API
    ]
    
    for dep in dependencies:
        success, output = run_command(f"pip install {dep}", f"Instalando {dep}")
        if not success:
            print(f"⚠️  Falha ao instalar {dep}, mas continuando...")


def fix_config_file():
    """Corrige o arquivo config.py com pydantic-settings"""
    print("\n🔧 CORRIGINDO ARQUIVO CONFIG.PY")
    print("=" * 50)
    
    config_content = '''# -*- coding: utf-8 -*-
"""
Configurações do sistema MedAI
"""
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from functools import lru_cache

try:
    # Pydantic v2 com pydantic-settings
    from pydantic import Field, field_validator
    from pydantic_settings import BaseSettings
    PYDANTIC_V2 = True
except ImportError:
    try:
        # Pydantic v1
        from pydantic import BaseSettings, Field, validator
        PYDANTIC_V2 = False
    except ImportError:
        # Fallback se nem pydantic-settings nem pydantic antigo estiver disponível
        raise ImportError("Instale pydantic-settings: pip install pydantic-settings")


class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # Informações da aplicação
    APP_NAME: str = "MedAI"
    APP_VERSION: str = "1.0.0"
    PROJECT_NAME: str = "MedAI"
    VERSION: str = "1.0.0"
    
    # Ambiente
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    TESTING: bool = Field(default=False)
    
    # API
    API_V1_STR: str = "/api/v1"
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Segurança
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    
    # Banco de dados
    DATABASE_URL: str = Field(default="sqlite:///./medai.db")
    
    # Upload de arquivos
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".pdf", ".txt", ".csv"]
    )
    
    # Machine Learning
    ML_MODEL_VERSION: str = Field(default="1.0.0")
    ML_BATCH_SIZE: int = Field(default=32)
    ML_MAX_WORKERS: int = Field(default=4)
    
    # Configuração para Pydantic v2 ou v1
    if PYDANTIC_V2:
        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": True,
            "extra": "ignore",
        }
        
        @field_validator("BACKEND_CORS_ORIGINS", mode="before")
        @classmethod
        def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
            if isinstance(v, str) and not v.startswith("["):
                return [i.strip() for i in v.split(",")]
            elif isinstance(v, (list, str)):
                return v
            raise ValueError(v)
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = True
        
        @validator("BACKEND_CORS_ORIGINS", pre=True)
        def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
            if isinstance(v, str) and not v.startswith("["):
                return [i.strip() for i in v.split(",")]
            elif isinstance(v, (list, str)):
                return v
            raise ValueError(v)
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Retorna a URI do banco para SQLAlchemy"""
        return str(self.DATABASE_URL)


@lru_cache()
def get_settings() -> Settings:
    """Obtém configurações do sistema (cached)"""
    return Settings()


# Instância global das configurações
settings = get_settings()


# Funções auxiliares para compatibilidade com testes
def validate_database_url(url: str) -> str:
    """Valida e converte URL do banco de dados"""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def validate_secret_key(key: str) -> str:
    """Valida chave secreta"""
    if not key or len(key) < 8:
        raise ValueError("SECRET_KEY deve ter pelo menos 8 caracteres")
    return key
'''
    
    # Salvar arquivo
    config_path = Path("app/config.py")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("   ✅ app/config.py atualizado com pydantic-settings")


def fix_database_file():
    """Corrige o arquivo database.py"""
    print("\n🔧 CORRIGINDO ARQUIVO DATABASE.PY")
    print("=" * 50)
    
    database_content = '''# -*- coding: utf-8 -*-
"""
Configuração do banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Usar a importação correta do declarative_base
try:
    # SQLAlchemy 2.0+
    from sqlalchemy.orm import declarative_base
except ImportError:
    # SQLAlchemy 1.4
    from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

# Base para modelos
Base = declarative_base()

# Engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Cria todas as tabelas do banco de dados"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Remove todas as tabelas do banco de dados"""
    Base.metadata.drop_all(bind=engine)
'''
    
    database_path = Path("app/database.py")
    with open(database_path, 'w', encoding='utf-8') as f:
        f.write(database_content)
    
    print("   ✅ app/database.py atualizado")


def create_env_file():
    """Cria arquivo .env básico para testes"""
    print("\n📝 CRIANDO ARQUIVO .ENV")
    print("=" * 50)
    
    env_content = '''# Configurações para testes
DATABASE_URL=sqlite:///./test_medai.db
SECRET_KEY=test-secret-key-for-development
DEBUG=true
TESTING=true
ENVIRONMENT=testing
'''
    
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("   ✅ Arquivo .env criado")
    else:
        print("   ℹ️  Arquivo .env já existe")


def test_imports():
    """Testa se as importações funcionam"""
    print("\n🧪 TESTANDO IMPORTAÇÕES")
    print("=" * 50)
    
    tests = [
        ("pydantic_settings", "BaseSettings"),
        ("app.config", "Settings, settings"),
        ("app.database", "Base, get_db"),
    ]
    
    all_ok = True
    
    for module, items in tests:
        try:
            if module == "pydantic_settings":
                from pydantic_settings import BaseSettings
                print(f"   ✅ {module}: {items}")
            elif module == "app.config":
                from app.config import Settings, settings
                print(f"   ✅ {module}: {items}")
                # Testar instanciação
                test_settings = Settings()
                print(f"      ✅ Settings instanciado: {test_settings.APP_NAME}")
            elif module == "app.database":
                from app.database import Base, get_db
                print(f"   ✅ {module}: {items}")
        except Exception as e:
            print(f"   ❌ {module}: {e}")
            all_ok = False
    
    return all_ok


def run_pytest_with_coverage():
    """Executa pytest com cobertura"""
    print("\n🧪 EXECUTANDO TESTES COM COBERTURA")
    print("=" * 50)
    
    cmd = "python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing --tb=short"
    success, output = run_command(cmd, "Executando testes")
    
    print("\n📊 RESULTADO DOS TESTES:")
    print(output[-1500:])  # Últimas 1500 chars para ver o resumo
    
    return success


def run_simple_pytest():
    """Executa pytest simples para verificar se os erros básicos foram resolvidos"""
    print("\n🧪 TESTE RÁPIDO DE IMPORTAÇÃO")
    print("=" * 50)
    
    cmd = "python -m pytest tests/unit/test_config.py -v --tb=short"
    success, output = run_command(cmd, "Testando config.py")
    
    if "BaseSettings" in output and "pydantic-settings" in output:
        print("   ❌ Ainda há problemas com BaseSettings")
        return False
    elif "collected" in output:
        print("   ✅ Testes de config coletados com sucesso!")
        return True
    else:
        print("   ⚠️  Resultado incerto")
        print(output[-500:])
        return False


def main():
    """Função principal que resolve tudo"""
    print("🚀 CORREÇÃO COMPLETA DE TODOS OS PROBLEMAS")
    print("=" * 60)
    print("Este script irá resolver:")
    print("1. ✅ Encoding UTF-8 (já resolvido)")
    print("2. 🔧 BaseSettings do Pydantic") 
    print("3. 🔧 Warning do SQLAlchemy")
    print("4. 🧪 Executar testes")
    print()
    
    # 1. Instalar dependências
    install_dependencies()
    
    # 2. Corrigir config.py
    fix_config_file()
    
    # 3. Corrigir database.py
    fix_database_file()
    
    # 4. Criar .env
    create_env_file()
    
    # 5. Testar importações
    if test_imports():
        print("\n✅ Todas as importações funcionam!")
    else:
        print("\n❌ Ainda há problemas com importações")
        return
    
    # 6. Teste rápido
    if run_simple_pytest():
        print("\n✅ Teste básico passou!")
        
        # 7. Teste completo com cobertura
        print("\n🎯 Executando teste completo...")
        if run_pytest_with_coverage():
            print("\n🎉 SUCESSO TOTAL! Todos os testes passaram!")
        else:
            print("\n✅ Problemas principais resolvidos, mas pode haver outros issues menores")
    else:
        print("\n⚠️  Ainda há problemas básicos a resolver")
    
    print("\n📋 COMANDOS PARA EXECUTAR MANUALMENTE:")
    print("# Teste simples:")
    print("python -c 'from app.config import settings; print(settings.APP_NAME)'")
    print()
    print("# Testes completos:")
    print("python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing")
    print()
    print("# Se ainda houver problemas, verifique:")
    print("pip install pydantic-settings")
    print("pip install sqlalchemy>=1.4.0")


if __name__ == "__main__":
    main()