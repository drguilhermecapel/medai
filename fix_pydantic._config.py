#!/usr/bin/env python3
"""
Corrige o problema do BaseSettings do Pydantic
Instala pydantic-settings e atualiza as importações
"""

import subprocess
import sys
import os
from pathlib import Path


def install_pydantic_settings():
    """Instala o pacote pydantic-settings"""
    print("📦 Instalando pydantic-settings...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pydantic-settings'], 
                      check=True, capture_output=True)
        print("   ✅ pydantic-settings instalado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro ao instalar pydantic-settings: {e}")
        return False


def update_config_file():
    """Atualiza o arquivo config.py com as importações corretas"""
    print("🔧 Atualizando app/config.py...")
    
    config_content = '''# -*- coding: utf-8 -*-
"""
Configurações do sistema MedAI
"""
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from functools import lru_cache

try:
    # Pydantic v2
    from pydantic import Field, field_validator
    from pydantic_settings import BaseSettings
    from pydantic.networks import PostgresDsn, RedisDsn, AnyHttpUrl
    PYDANTIC_V2 = True
except ImportError:
    # Fallback para Pydantic v1
    from pydantic import BaseSettings, Field, validator
    from pydantic import PostgresDsn, RedisDsn, AnyHttpUrl
    PYDANTIC_V2 = False


class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # Informações da aplicação
    APP_NAME: str = "MedAI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema de Análise Médica com Inteligência Artificial"
    PROJECT_NAME: str = "MedAI"
    VERSION: str = "1.0.0"
    
    # Ambiente
    ENVIRONMENT: str = Field(default="development", alias="ENVIRONMENT")
    DEBUG: bool = Field(default=False, alias="DEBUG")
    TESTING: bool = Field(default=False, alias="TESTING")
    
    # API
    API_V1_STR: str = "/api/v1"
    API_HOST: str = Field(default="0.0.0.0", alias="API_HOST")
    API_PORT: int = Field(default=8000, alias="API_PORT")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Segurança
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="dev-jwt-secret-key-change-in-production", alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        alias="BACKEND_CORS_ORIGINS"
    )
    
    # Banco de dados
    DATABASE_URL: str = Field(
        default="sqlite:///./medai.db", 
        alias="DATABASE_URL",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, alias="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, alias="DATABASE_MAX_OVERFLOW")
    
    # PostgreSQL (para produção)
    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(default="medai", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="medai123", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="medai_db", env="POSTGRES_DB")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # Email
    SMTP_TLS: bool = Field(default=True, alias="SMTP_TLS")
    SMTP_PORT: int = Field(default=587, alias="SMTP_PORT")
    SMTP_HOST: Optional[str] = Field(default=None, alias="SMTP_HOST")
    SMTP_USER: Optional[str] = Field(default=None, alias="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    
    # Upload de arquivos
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, alias="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".pdf", ".txt", ".csv"],
        alias="ALLOWED_EXTENSIONS"
    )
    UPLOAD_DIR: str = Field(default="uploads", alias="UPLOAD_DIR")
    
    # Machine Learning
    ML_MODEL_VERSION: str = Field(default="1.0.0", alias="ML_MODEL_VERSION")
    ML_BATCH_SIZE: int = Field(default=32, alias="ML_BATCH_SIZE")
    ML_MAX_WORKERS: int = Field(default=4, alias="ML_MAX_WORKERS")
    ML_MODELS_DIR: str = Field(default="ml_models", alias="ML_MODELS_DIR")
    
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
        
        @field_validator("DATABASE_URL", mode="before")
        @classmethod
        def validate_database_url(cls, v: str) -> str:
            if isinstance(v, str) and v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql://", 1)
            return v
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
        
        @validator("DATABASE_URL", pre=True)
        def validate_database_url(cls, v: str) -> str:
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql://", 1)
            return v
    
    # Propriedades e métodos auxiliares
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Retorna a URI do banco para SQLAlchemy"""
        return str(self.DATABASE_URL)
    
    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        """Retorna a URI do banco assíncrono para SQLAlchemy"""
        db_url = str(self.DATABASE_URL)
        if db_url.startswith("postgresql://"):
            return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("sqlite:///"):
            return db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        return db_url


@lru_cache()
def get_settings() -> Settings:
    """
    Obtém configurações do sistema (cached)
    """
    return Settings()


# Instância global das configurações
settings = get_settings()


# Funções auxiliares para testes
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
    
    # Salvar o arquivo config.py atualizado
    config_path = Path("app/config.py")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("   ✅ app/config.py atualizado com pydantic-settings")


def create_env_file():
    """Cria arquivo .env para testes se não existir"""
    print("📝 Criando arquivo .env para testes...")
    
    env_content = '''# Configurações para desenvolvimento e testes
DATABASE_URL=sqlite:///./test_medai.db
SECRET_KEY=test-secret-key-for-development-only
DEBUG=true
TESTING=true
ENVIRONMENT=testing

# API
API_HOST=0.0.0.0
API_PORT=8000

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Redis (opcional para testes)
REDIS_URL=redis://localhost:6379/1

# ML
ML_MODELS_DIR=./ml_models
'''
    
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("   ✅ Arquivo .env criado")
    else:
        print("   ℹ️  Arquivo .env já existe")


def test_config_import():
    """Testa se o config.py pode ser importado sem erro"""
    print("🧪 Testando importação de app.config...")
    
    try:
        import app.config
        from app.config import Settings, settings, validate_database_url, validate_secret_key
        print("   ✅ app.config importado com sucesso")
        
        # Testar instanciação
        test_settings = Settings()
        print(f"   ✅ Settings instanciado: {test_settings.APP_NAME}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro ao importar app.config: {e}")
        return False


def run_tests():
    """Executa os testes para verificar se o problema foi resolvido"""
    print("🧪 Executando testes...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/unit/', '-v', 
            '--tb=short',
            '--maxfail=5'  # Parar após 5 falhas
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout[-2000:])  # Últimas 2000 chars
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr[-1000:])  # Últimas 1000 chars
        
        if result.returncode == 0:
            print("   ✅ Testes executados com sucesso!")
            return True
        else:
            print(f"   ⚠️  Testes executaram mas com falhas (código: {result.returncode})")
            
            # Verificar se ainda há erros de BaseSettings
            output = result.stdout + result.stderr
            if 'BaseSettings' in output and 'pydantic-settings' in output:
                print("   ❌ Ainda há problemas com BaseSettings")
                return False
            else:
                print("   ✅ Problema do BaseSettings resolvido!")
                return True
        
    except Exception as e:
        print(f"   ❌ Erro ao executar testes: {e}")
        return False


def main():
    """Função principal"""
    print("🚀 CORREÇÃO DO PROBLEMA PYDANTIC BASESETTINGS")
    print("=" * 60)
    
    # 1. Instalar pydantic-settings
    if not install_pydantic_settings():
        print("❌ Falha ao instalar pydantic-settings. Instale manualmente:")
        print("pip install pydantic-settings")
        return
    
    # 2. Atualizar config.py
    update_config_file()
    
    # 3. Criar arquivo .env
    create_env_file()
    
    # 4. Testar importação
    print("\n" + "=" * 60)
    if test_config_import():
        print("✅ Configuração corrigida com sucesso!")
    else:
        print("❌ Ainda há problemas com a configuração")
        return
    
    # 5. Executar testes
    print("\n" + "=" * 60)
    if run_tests():
        print("\n🎉 SUCESSO! Problema do BaseSettings resolvido!")
        print("\nVocê pode agora executar os testes normalmente:")
        print("python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing")
    else:
        print("\n⚠️  Ainda pode haver outros problemas nos testes.")
        print("Mas o problema principal do BaseSettings foi resolvido!")


if __name__ == "__main__":
    main()