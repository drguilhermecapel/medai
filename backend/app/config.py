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
    # Pydantic v1
    from pydantic import BaseSettings, Field, validator
    from pydantic import PostgresDsn, RedisDsn, AnyHttpUrl
    PYDANTIC_V2 = False
class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    # Informações da aplicação
    APP_NAME: str = "MedAI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema de Análise Médica com Inteligência Artificial"
    # Ambiente
    ENVIRONMENT: str = Field(default="development", alias="ENVIRONMENT")
    DEBUG: bool = Field(default=False, alias="DEBUG")
    TESTING: bool = Field(default=False, alias="TESTING")
    # API
    API_V1_STR: str = "/api/v1"
    API_HOST: str = Field(default="0.0.0.0", alias="API_HOST")
    API_PORT: int = Field(default=8000, alias="API_PORT")
    # Segurança
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="dev-jwt-secret-key-change-in-production", alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        alias="BACKEND_CORS_ORIGINS"
    )
    # Banco de dados
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/medai", alias="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, alias="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, alias="DATABASE_MAX_OVERFLOW")
    DATABASE_ECHO: bool = Field(default=False, alias="DATABASE_ECHO")
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    REDIS_POOL_SIZE: int = Field(default=10, alias="REDIS_POOL_SIZE")
    CACHE_TTL: int = Field(default=3600, alias="CACHE_TTL")  # 1 hora
    # Email
    SMTP_HOST: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, alias="SMTP_PORT")
    SMTP_USER: str = Field(default="test@test.com", alias="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="test-password", alias="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: str = Field(default="noreply@medai.com", alias="SMTP_FROM_EMAIL")
    SMTP_FROM_NAME: str = Field(default="MedAI", alias="SMTP_FROM_NAME")
    SMTP_TLS: bool = Field(default=True, alias="SMTP_TLS")
    SMTP_SSL: bool = Field(default=False, alias="SMTP_SSL")
    # OpenAI / IA
    OPENAI_API_KEY: str = Field(default="test-openai-key", alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", alias="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")
    OPENAI_MAX_TOKENS: int = Field(default=4000, alias="OPENAI_MAX_TOKENS")
    # Armazenamento
    UPLOAD_DIR: str = Field(default="uploads", alias="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=52428800, alias="MAX_UPLOAD_SIZE")  # 50MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".pdf", ".dcm", ".nii", ".csv", ".txt"],
        alias="ALLOWED_EXTENSIONS"
    )
    # Armazenamento S3 (opcional)
    USE_S3: bool = Field(default=False, alias="USE_S3")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", alias="AWS_REGION")
    S3_BUCKET_NAME: Optional[str] = Field(default=None, alias="S3_BUCKET_NAME")
    # Logs
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = Field(default="logs", alias="LOG_DIR")
    # Celery (tarefas assíncronas)
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")
    CELERY_TASK_TIME_LIMIT: int = Field(default=300, alias="CELERY_TASK_TIME_LIMIT")  # 5 minutos
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, alias="RATE_LIMIT_PER_HOUR")
    
    # Notificações
    ENABLE_PUSH_NOTIFICATIONS: bool = Field(default=False, alias="ENABLE_PUSH_NOTIFICATIONS")
    FCM_SERVER_KEY: Optional[str] = Field(default=None, alias="FCM_SERVER_KEY")
    # Integração com sistemas externos
    HL7_ENABLED: bool = Field(default=False, alias="HL7_ENABLED")
    FHIR_ENABLED: bool = Field(default=False, alias="FHIR_ENABLED")
    FHIR_SERVER_URL: Optional[str] = Field(default=None, alias="FHIR_SERVER_URL")
    # Configurações de desenvolvimento
    RELOAD: bool = Field(default=False, alias="RELOAD")
    DOCS_URL: Optional[str] = Field(default="/docs", alias="DOCS_URL")
    REDOC_URL: Optional[str] = Field(default="/redoc", alias="REDOC_URL")
    # Sentry (monitoramento de erros)
    SENTRY_DSN: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    SENTRY_ENVIRONMENT: Optional[str] = Field(default=None, alias="SENTRY_ENVIRONMENT")
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
    DATABASE_URL: str = "sqlite:///:memory:"
    REDIS_URL: str = "redis://localhost:6379/15"
    SECRET_KEY: str = "test-secret-key"
    JWT_SECRET_KEY: str = "test-jwt-secret"
    SMTP_USER: str = "test@test.com"
    SMTP_PASSWORD: str = "test"
    SMTP_FROM_EMAIL: str = "test@test.com"
    OPENAI_API_KEY: str = "test-key"
@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações em cache.
    Usar lru_cache garante que as configurações sejam lidas apenas uma vez.
    """
    # Se estiver em modo de teste, usa configurações de teste
    if os.getenv("TESTING", "false").lower() == "true":
        return TestingSettings()
    # Caso contrário, usa as configurações padrão
    return Settings()
# Instância global das configurações
settings = get_settings()
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