"""
Configurações do sistema MedAI
"""
import os
from typing import Any, Dict, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # Configurações básicas
    APP_NAME: str = "MedAI"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Configurações do servidor
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Configurações de segurança
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Configurações do banco de dados
    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(default="medai", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="medai123", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="medai_db", env="POSTGRES_DB")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Configurações do Redis
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_URL: Optional[RedisDsn] = None
    
    # Configurações de email
    SMTP_HOST: str = Field(default="localhost", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    EMAIL_FROM: str = Field(default="noreply@medai.com", env="EMAIL_FROM")
    EMAIL_FROM_NAME: str = Field(default="MedAI", env="EMAIL_FROM_NAME")
    
    # Configurações de CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Configurações de upload
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".pdf", ".dcm", ".txt", ".csv"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # Configurações de ML/AI
    ML_MODELS_DIR: str = Field(default="ml_models", env="ML_MODELS_DIR")
    ML_MODEL_VERSION: str = Field(default="1.0.0", env="ML_MODEL_VERSION")
    ML_BATCH_SIZE: int = Field(default=32, env="ML_BATCH_SIZE")
    ML_MAX_WORKERS: int = Field(default=4, env="ML_MAX_WORKERS")
    
    # Configurações de logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Configurações de testes
    TESTING: bool = Field(default=False, env="TESTING")
    TEST_DATABASE_URL: Optional[str] = Field(default=None, env="TEST_DATABASE_URL")
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=str(values.get("POSTGRES_PORT")),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        # Construir URL do Redis
        auth = ""
        if values.get("REDIS_PASSWORD"):
            auth = f":{values.get('REDIS_PASSWORD')}@"
        
        redis_url = (
            f"redis://{auth}{values.get('REDIS_HOST')}:"
            f"{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
        )
        return redis_url
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global das configurações
settings = Settings()