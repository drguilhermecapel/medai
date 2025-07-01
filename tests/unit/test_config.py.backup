import pytest
from app.config import Settings, validate_database_url, validate_secret_key

def test_settings():
    settings = Settings()
    assert settings.app_name == "MedAI"
    assert settings.debug is False

def test_validate_database_url():
    assert validate_database_url("sqlite:///test.db")
    assert validate_database_url("postgresql://user:pass@localhost/db")
    assert not validate_database_url("")
    assert not validate_database_url("invalid")

def test_validate_secret_key():
    assert validate_secret_key("a" * 32)
    assert not validate_secret_key("short")
    assert not validate_secret_key("")

def test_config_classes():
    from app.config import DatabaseConfig, SecurityConfig, MLConfig
    
    db_config = DatabaseConfig("sqlite:///test.db")
    assert db_config.url == "sqlite:///test.db"
    
    sec_config = SecurityConfig()
    assert sec_config.algorithm == "HS256"
    
    ml_config = MLConfig()
    assert ml_config.model_path == "./models"
