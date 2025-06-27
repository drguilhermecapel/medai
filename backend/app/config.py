"""
Configurações do sistema MedAI
"""
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from functools import lru_cache

from pydantic import BaseSettings, Field, validator, PostgresDsn, RedisDsn, AnyHttpUrl


class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # Informações da aplicação
    APP_NAME: str = "MedAI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema de Análise Médica com Inteligência Artificial"
    
    # Ambiente
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(False, env="DEBUG")
    TESTING: bool = Field(False, env="TESTING")
    
    # API
    API_V1_STR: str = "/api/v1"
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    
    # Segurança
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        ["http://localhost:3000", "http://localhost:8000"],
        env="BACKEND_CORS_ORIGINS"
    )
    
    # Banco de dados
    DATABASE_URL: PostgresDsn = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    DATABASE_ECHO: bool = Field(False, env="DATABASE_ECHO")
    
    # Redis
    REDIS_URL: RedisDsn = Field("redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    REDIS_POOL_SIZE: int = Field(10, env="REDIS_POOL_SIZE")
    CACHE_TTL: int = Field(3600, env="CACHE_TTL")  # 1 hora
    
    # Email
    SMTP_HOST: str = Field("smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(587, env="SMTP_PORT")
    SMTP_USER: str = Field(..., env="SMTP_USER")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: str = Field(..., env="SMTP_FROM_EMAIL")
    SMTP_FROM_NAME: str = Field("MedAI", env="SMTP_FROM_NAME")
    SMTP_TLS: bool = Field(True, env="SMTP_TLS")
    SMTP_SSL: bool = Field(False, env="SMTP_SSL")
    
    # OpenAI / IA
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(0.7, env="OPENAI_TEMPERATURE")
    OPENAI_MAX_TOKENS: int = Field(4000, env="OPENAI_MAX_TOKENS")
    
    # Armazenamento
    UPLOAD_DIR: str = Field("uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(52428800, env="MAX_UPLOAD_SIZE")  # 50MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        [".jpg", ".jpeg", ".png", ".pdf", ".dcm", ".nii", ".csv", ".txt"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # Armazenamento S3 (opcional)
    USE_S3: bool = Field(False, env="USE_S3")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field("us-east-1", env="AWS_REGION")
    S3_BUCKET_NAME: Optional[str] = Field(None, env="S3_BUCKET_NAME")
    
    # Logs
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = Field("logs", env="LOG_DIR")
    
    # Celery (tarefas assíncronas)
    CELERY_BROKER_URL: str = Field("redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field("redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    CELERY_TASK_TIME_LIMIT: int = Field(300, env="CELERY_TASK_TIME_LIMIT")  # 5 minutos
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(1000, env="RATE_LIMIT_PER_HOUR")
    
    # Configurações médicas
    ECG_SAMPLE_RATE: int = Field(500, env="ECG_SAMPLE_RATE")
    ECG_LEADS: int = Field(12, env="ECG_LEADS")
    MIN_ECG_QUALITY_SCORE: float = Field(0.7, env="MIN_ECG_QUALITY_SCORE")
    
    # Notificações
    ENABLE_PUSH_NOTIFICATIONS: bool = Field(False, env="ENABLE_PUSH_NOTIFICATIONS")
    FCM_SERVER_KEY: Optional[str] = Field(None, env="FCM_SERVER_KEY")
    
    # Integração com sistemas externos
    HL7_ENABLED: bool = Field(False, env="HL7_ENABLED")
    FHIR_ENABLED: bool = Field(False, env="FHIR_ENABLED")
    FHIR_SERVER_URL: Optional[str] = Field(None, env="FHIR_SERVER_URL")
    
    # Configurações de desenvolvimento
    RELOAD: bool = Field(False, env="RELOAD")
    DOCS_URL: Optional[str] = Field("/docs", env="DOCS_URL")
    REDOC_URL: Optional[str] = Field("/redoc", env="REDOC_URL")
    
    # Sentry (monitoramento de erros)
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")
    SENTRY_ENVIRONMENT: Optional[str] = Field(None, env="SENTRY_ENVIRONMENT")
    
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
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Retorna a URI do banco para SQLAlchemy"""
        return str(self.DATABASE_URL)
    
    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        """Retorna a URI assíncrona do banco para SQLAlchemy"""
        return self.SQLALCHEMY_DATABASE_URI.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
    
    def get_upload_path(self) -> Path:
        """Retorna o caminho completo para uploads"""
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_log_path(self) -> Path:
        """Retorna o caminho completo para logs"""
        path = Path(self.LOG_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.ENVIRONMENT == "development"
    
    def is_testing(self) -> bool:
        """Verifica se está em modo de teste"""
        return self.TESTING or self.ENVIRONMENT == "testing"


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações em cache.
    Usar lru_cache garante que as configurações sejam lidas apenas uma vez.
    """
    return Settings()


# Instância global das configurações
settings = get_settings()


# Configurações específicas por ambiente
class DevelopmentSettings(Settings):
    """Configurações para desenvolvimento"""
    DEBUG: bool = True
    RELOAD: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Configurações para produção"""
    DEBUG: bool = False
    DOCS_URL: Optional[str] = None
    REDOC_URL: Optional[str] = None
    LOG_LEVEL: str = "WARNING"


class TestingSettings(Settings):
    """Configurações para testes"""
    TESTING: bool = True
    DATABASE_URL: PostgresDsn = "sqlite:///:memory:"
    REDIS_URL: RedisDsn = "redis://localhost:6379/15"
    SECRET_KEY: str = "test-secret-key"
    JWT_SECRET_KEY: str = "test-jwt-secret"
    SMTP_USER: str = "test@test.com"
    SMTP_PASSWORD: str = "test"
    SMTP_FROM_EMAIL: str = "test@test.com"
    OPENAI_API_KEY: str = "test-key"


# Função para obter as configurações corretas baseadas no ambiente
def get_settings_by_environment(environment: str = None) -> Settings:
    """Retorna as configurações baseadas no ambiente"""
    env = environment or os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Configurações de logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": settings.LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "detailed",
            "filename": settings.get_log_path() / "medai.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "app": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sqlalchemy": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["console", "file"],
    },
}