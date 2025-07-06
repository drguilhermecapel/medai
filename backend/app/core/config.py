"""
Configurações centrais do sistema MedAI - Versão 1.0
Configuração baseada em Pydantic Settings para máxima flexibilidade
"""
import os
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import Field, validator, AnyHttpUrl
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações principais da aplicação MedAI"""
    
    # === CONFIGURAÇÕES BÁSICAS ===
    APP_NAME: str = "MedAI - Sistema de IA Médica"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sistema avançado de inteligência artificial para diagnóstico médico"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # === CONFIGURAÇÕES DO SERVIDOR ===
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    API_V1_STR: str = "/api/v1"
    
    # === CONFIGURAÇÕES DE SEGURANÇA ===
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    
    # === CONFIGURAÇÕES DO BANCO DE DADOS ===
    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(default="medai", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="medai123", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="medai_db", env="POSTGRES_DB")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    
    # === CONFIGURAÇÕES DO REDIS ===
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # === CONFIGURAÇÕES DE EMAIL ===
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    
    # === CONFIGURAÇÕES DE CORS ===
    CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    # === CONFIGURAÇÕES DE IA/ML ===
    MODEL_PATH: str = Field(default="/app/models", env="MODEL_PATH")
    MODEL_VERSION: str = Field(default="1.0.0", env="MODEL_VERSION")
    INFERENCE_TIMEOUT: int = Field(default=30, env="INFERENCE_TIMEOUT")
    MAX_BATCH_SIZE: int = Field(default=32, env="MAX_BATCH_SIZE")
    MODEL_CACHE_TTL: int = Field(default=3600, env="MODEL_CACHE_TTL")
    
    # === CONFIGURAÇÕES DE ARQUIVOS ===
    UPLOAD_PATH: str = Field(default="/app/uploads", env="UPLOAD_PATH")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "pdf", "dicom"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # === CONFIGURAÇÕES DE LOGGING ===
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    LOG_FILE: str = Field(default="/app/logs/medai.log", env="LOG_FILE")
    
    # === CONFIGURAÇÕES DE RATE LIMITING ===
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # === CONFIGURAÇÕES DE MONITORAMENTO ===
    MONITORING_ENABLED: bool = Field(default=True, env="MONITORING_ENABLED")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    HEALTH_CHECK_TIMEOUT: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")
    
    # === VALIDADORES ===
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # === PROPRIEDADES CALCULADAS ===
    @property
    def DATABASE_URL(self) -> str:
        """Monta URL completa do banco de dados PostgreSQL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def REDIS_URL(self) -> str:
        """Monta URL completa do Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def SMTP_URL(self) -> str:
        """Monta URL completa do SMTP"""
        return f"smtp://{self.SMTP_USER}:{self.SMTP_PASSWORD}@{self.SMTP_HOST}:{self.SMTP_PORT}"
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        """Verifica se está em ambiente de testes"""
        return self.ENVIRONMENT == "testing"
    
    # === CONFIGURAÇÕES ESPECÍFICAS POR AMBIENTE ===
    def get_database_config(self) -> Dict[str, Any]:
        """Retorna configurações específicas do banco para o ambiente"""
        base_config = {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 3600
        }
        
        if self.is_production:
            base_config.update({
                "pool_size": 20,
                "max_overflow": 30,
                "echo": False
            })
        elif self.is_development:
            base_config.update({
                "echo": True,
                "pool_size": 2,
                "max_overflow": 5
            })
        
        return base_config
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Retorna configurações específicas do Redis para o ambiente"""
        base_config = {
            "encoding": "utf-8",
            "decode_responses": True,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
        
        if self.is_production:
            base_config.update({
                "max_connections": 50,
                "socket_keepalive": True,
                "socket_keepalive_options": {}
            })
        
        return base_config
    
    def get_ml_config(self) -> Dict[str, Any]:
        """Retorna configurações específicas de ML para o ambiente"""
        return {
            "diagnostic_model": {
                "path": f"{self.MODEL_PATH}/diagnostic_v{self.MODEL_VERSION}.pkl",
                "type": "classification",
                "threshold": 0.8,
                "batch_size": self.MAX_BATCH_SIZE
            },
            "multi_pathology_model": {
                "path": f"{self.MODEL_PATH}/multi_pathology_v{self.MODEL_VERSION}.pkl",
                "type": "multi_label",
                "threshold": 0.7,
                "batch_size": self.MAX_BATCH_SIZE // 2
            },
            "validation_model": {
                "path": f"{self.MODEL_PATH}/validation_v{self.MODEL_VERSION}.pkl",
                "type": "binary_classification",
                "threshold": 0.9,
                "batch_size": self.MAX_BATCH_SIZE
            }
        }
    
    class Config:
        """Configuração do Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DatabaseConfig:
    """Configurações específicas do banco de dados"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @property
    def sqlalchemy_database_url(self) -> str:
        return self.settings.DATABASE_URL
    
    @property
    def engine_options(self) -> Dict[str, Any]:
        return self.settings.get_database_config()


class RedisConfig:
    """Configurações específicas do Redis"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @property
    def connection_options(self) -> Dict[str, Any]:
        return self.settings.get_redis_config()


class SecurityConfig:
    """Configurações de segurança"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @property
    def jwt_config(self) -> Dict[str, Any]:
        return {
            "secret_key": self.settings.SECRET_KEY,
            "algorithm": self.settings.ALGORITHM,
            "access_token_expire_minutes": self.settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": self.settings.REFRESH_TOKEN_EXPIRE_DAYS
        }
    
    @property
    def password_config(self) -> Dict[str, Any]:
        return {
            "min_length": self.settings.PASSWORD_MIN_LENGTH,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": True
        }


@lru_cache()
def get_settings() -> Settings:
    """Factory function para obter configurações com cache"""
    return Settings()


# Instância global das configurações
settings = get_settings()

# Configurações específicas
database_config = DatabaseConfig(settings)
redis_config = RedisConfig(settings)
security_config = SecurityConfig(settings)


# === CONSTANTES DERIVADAS ===
# Configurações de validação
VALIDATION_CONFIG = {
    "max_file_size": settings.MAX_FILE_SIZE,
    "allowed_extensions": settings.ALLOWED_EXTENSIONS,
    "upload_path": settings.UPLOAD_PATH
}

# Configurações de AI/ML
ML_CONFIG = settings.get_ml_config()

# Configurações de monitoramento
MONITORING_CONFIG = {
    "enabled": settings.MONITORING_ENABLED,
    "metrics_port": settings.METRICS_PORT,
    "health_check_timeout": settings.HEALTH_CHECK_TIMEOUT
}

# Configurações de rate limiting
RATE_LIMIT_CONFIG = {
    "enabled": settings.RATE_LIMIT_ENABLED,
    "requests": settings.RATE_LIMIT_REQUESTS,
    "window": settings.RATE_LIMIT_WINDOW
}
