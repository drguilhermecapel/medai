"""
Application settings using Pydantic BaseSettings for configuration management.
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application Info
    APP_NAME: str = Field(default="MEDAI", description="Application name")
    VERSION: str = Field(default="1.0.0", description="Application version")
    DESCRIPTION: str = Field(
        default="Advanced Electronic Health Record System with AI",
        description="Application description"
    )
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")
    
    # API Configuration
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")
    
    # Security
    SECRET_KEY: str = Field(
        description="Secret key for encryption",
        min_length=32
    )
    JWT_SECRET_KEY: Optional[str] = Field(
        default=None,
        description="JWT secret key (defaults to SECRET_KEY if not provided)"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24 * 7,  # 7 days
        description="Access token expiration in minutes"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./medai.db",
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # Redis Configuration
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis connection URL"
    )
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        description="Maximum upload size in bytes"
    )
    UPLOAD_PATH: str = Field(
        default="./uploads",
        description="Upload directory path"
    )
    
    # Medical Compliance
    MEDICAL_COMPLIANCE_MODE: bool = Field(
        default=True,
        description="Enable medical compliance features"
    )
    AUDIT_LOGGING: bool = Field(
        default=True,
        description="Enable audit logging"
    )
    DATA_RETENTION_DAYS: int = Field(
        default=2555,  # 7 years
        description="Data retention period in days"
    )
    
    @validator("JWT_SECRET_KEY", always=True)
    def set_jwt_secret_key(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """Set JWT secret key to SECRET_KEY if not provided."""
        if v is None:
            return values.get("SECRET_KEY", "")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError("CORS_ORIGINS must be a list or string")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() in ("development", "dev", "local")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() in ("production", "prod")
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.ENVIRONMENT.lower() in ("testing", "test")
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()