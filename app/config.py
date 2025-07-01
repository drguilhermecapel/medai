# -*- coding: utf-8 -*-
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
