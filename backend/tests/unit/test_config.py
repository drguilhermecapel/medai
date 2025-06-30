# tests/unit/test_config.py
"""
Testes unitários para o módulo de configuração do MedAI.
Cobre validação de configurações, variáveis de ambiente e settings.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from app.config import (
    Settings,
    get_settings,
    DatabaseConfig,
    SecurityConfig,
    MLConfig,
    EmailConfig,
    StorageConfig,
    validate_database_url,
    validate_secret_key,
    load_environment_config
)


class TestSettings:
    """Testes para a classe Settings principal."""
    
    def test_default_settings_creation(self):
        """Testa criação de settings com valores padrão."""
        settings = Settings()
        
        assert settings.app_name == "MedAI"
        assert settings.debug is False
        assert settings.api_v1_prefix == "/api/v1"
        assert settings.cors_origins == ["http://localhost:3000"]
    
    def test_settings_from_env_vars(self):
        """Testa carregamento de settings de variáveis de ambiente."""
        with patch.dict(os.environ, {
            "APP_NAME": "MedAI Test",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://user:pass@localhost/medai_test",
            "SECRET_KEY": "test-secret-key-123",
            "ML_MODEL_PATH": "/models/test"
        }):
            settings = Settings()
            
            assert settings.app_name == "MedAI Test"
            assert settings.debug is True
            assert settings.database_url == "postgresql://user:pass@localhost/medai_test"
            assert settings.secret_key == "test-secret-key-123"
            assert settings.ml_model_path == "/models/test"
    
    def test_settings_validation_error(self):
        """Testa erro de validação em configurações inválidas."""
        with patch.dict(os.environ, {
            "API_V1_PREFIX": "invalid-prefix",  # Sem barra inicial
            "CORS_ORIGINS": "not-a-list"
        }):
            with pytest.raises(ValidationError):
                Settings()
    
    def test_settings_singleton(self):
        """Testa que get_settings retorna singleton."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    @patch('app.config.get_settings')
    def test_settings_cache_reset(self, mock_get_settings):
        """Testa reset do cache de settings."""
        # Limpa cache
        get_settings.cache_clear()
        
        # Primeira chamada
        settings1 = get_settings()
        
        # Segunda chamada deve usar cache
        settings2 = get_settings()
        
        assert settings1 is settings2


class TestDatabaseConfig:
    """Testes para configuração de banco de dados."""
    
    def test_database_config_postgresql(self):
        """Testa configuração para PostgreSQL."""
        config = DatabaseConfig(
            url="postgresql://user:password@localhost:5432/medai",
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            echo=False
        )
        
        assert config.url.startswith("postgresql://")
        assert config.pool_size == 10
        assert config.max_overflow == 20
    
    def test_database_config_sqlite(self):
        """Testa configuração para SQLite."""
        config = DatabaseConfig(
            url="sqlite:///./medai.db",
            check_same_thread=False
        )
        
        assert config.url.startswith("sqlite://")
        assert config.check_same_thread is False
    
    def test_validate_database_url_valid(self):
        """Testa validação de URLs de banco válidas."""
        valid_urls = [
            "postgresql://user:pass@localhost/db",
            "postgresql+asyncpg://user:pass@host:5432/db",
            "mysql://root:pass@localhost/medai",
            "sqlite:///./test.db",
            "sqlite:///:memory:"
        ]
        
        for url in valid_urls:
            assert validate_database_url(url) is True
    
    def test_validate_database_url_invalid(self):
        """Testa validação de URLs de banco inválidas."""
        invalid_urls = [
            "invalid://url",
            "http://not-a-database",
            "postgresql://missing-database",
            "",
            None
        ]
        
        for url in invalid_urls:
            assert validate_database_url(url) is False
    
    def test_database_config_connection_string_parsing(self):
        """Testa parsing de string de conexão."""
        url = "postgresql://medai_user:secure_pass@db.medai.com:5432/medai_prod?sslmode=require"
        config = DatabaseConfig(url=url)
        
        # Verifica se a URL é mantida corretamente
        assert "medai_user" in config.url
        assert "db.medai.com" in config.url
        assert "5432" in config.url
        assert "sslmode=require" in config.url


class TestSecurityConfig:
    """Testes para configuração de segurança."""
    
    def test_security_config_defaults(self):
        """Testa valores padrão de segurança."""
        config = SecurityConfig()
        
        assert config.algorithm == "HS256"
        assert config.access_token_expire_minutes == 30
        assert config.refresh_token_expire_days == 7
        assert config.password_min_length == 8
        assert config.password_require_uppercase is True
        assert config.password_require_numbers is True
        assert config.password_require_special is True
    
    def test_security_config_custom(self):
        """Testa configuração customizada de segurança."""
        config = SecurityConfig(
            secret_key="ultra-secret-key-456",
            algorithm="HS512",
            access_token_expire_minutes=15,
            password_min_length=12,
            bcrypt_rounds=14
        )
        
        assert config.secret_key == "ultra-secret-key-456"
        assert config.algorithm == "HS512"
        assert config.access_token_expire_minutes == 15
        assert config.password_min_length == 12
        assert config.bcrypt_rounds == 14
    
    def test_validate_secret_key_valid(self):
        """Testa validação de chaves secretas válidas."""
        valid_keys = [
            "a" * 32,  # 32 caracteres
            "super-secret-key-with-special-chars-123!@#",
            "0123456789abcdef" * 2
        ]
        
        for key in valid_keys:
            assert validate_secret_key(key) is True
    
    def test_validate_secret_key_invalid(self):
        """Testa validação de chaves secretas inválidas."""
        invalid_keys = [
            "short",  # Muito curta
            "",
            None,
            "a" * 31  # Um caractere a menos
        ]
        
        for key in invalid_keys:
            assert validate_secret_key(key) is False
    
    def test_security_config_rate_limiting(self):
        """Testa configuração de rate limiting."""
        config = SecurityConfig(
            rate_limit_enabled=True,
            rate_limit_requests=100,
            rate_limit_window=60,
            rate_limit_burst=10
        )
        
        assert config.rate_limit_enabled is True
        assert config.rate_limit_requests == 100
        assert config.rate_limit_window == 60


class TestMLConfig:
    """Testes para configuração de Machine Learning."""
    
    def test_ml_config_defaults(self):
        """Testa configuração padrão de ML."""
        config = MLConfig()
        
        assert config.model_path == "./models"
        assert config.model_version == "latest"
        assert config.batch_size == 32
        assert config.max_sequence_length == 512
        assert config.confidence_threshold == 0.7
    
    def test_ml_config_custom(self):
        """Testa configuração customizada de ML."""
        config = MLConfig(
            model_path="/opt/medai/models",
            model_version="v2.1.0",
            use_gpu=True,
            gpu_device_id=0,
            batch_size=64,
            confidence_threshold=0.85
        )
        
        assert config.model_path == "/opt/medai/models"
        assert config.model_version == "v2.1.0"
        assert config.use_gpu is True
        assert config.confidence_threshold == 0.85
    
    def test_ml_config_model_types(self):
        """Testa configuração de diferentes tipos de modelos."""
        config = MLConfig(
            diagnostic_model="bert-medical-v3",
            risk_assessment_model="xgboost-risk-v2",
            image_analysis_model="resnet50-medical",
            nlp_model="bioclinicalbert"
        )
        
        assert config.diagnostic_model == "bert-medical-v3"
        assert config.risk_assessment_model == "xgboost-risk-v2"
        assert config.image_analysis_model == "resnet50-medical"
    
    def test_ml_config_preprocessing(self):
        """Testa configuração de pré-processamento."""
        config = MLConfig(
            normalize_inputs=True,
            remove_outliers=True,
            outlier_threshold=3.0,
            missing_value_strategy="mean",
            feature_scaling="standard"
        )
        
        assert config.normalize_inputs is True
        assert config.outlier_threshold == 3.0
        assert config.missing_value_strategy == "mean"


class TestEmailConfig:
    """Testes para configuração de email."""
    
    def test_email_config_smtp(self):
        """Testa configuração SMTP."""
        config = EmailConfig(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="medai@gmail.com",
            smtp_password="app-specific-password",
            use_tls=True,
            from_email="noreply@medai.com"
        )
        
        assert config.smtp_host == "smtp.gmail.com"
        assert config.smtp_port == 587
        assert config.use_tls is True
    
    def test_email_config_templates(self):
        """Testa configuração de templates de email."""
        config = EmailConfig(
            template_dir="./templates/emails",
            welcome_template="welcome.html",
            password_reset_template="reset_password.html",
            diagnostic_report_template="diagnostic_report.html"
        )
        
        assert config.template_dir == "./templates/emails"
        assert config.welcome_template == "welcome.html"
    
    def test_email_config_validation(self):
        """Testa validação de configuração de email."""
        # Porta inválida
        with pytest.raises(ValidationError):
            EmailConfig(smtp_port=99999)
        
        # Email inválido
        with pytest.raises(ValidationError):
            EmailConfig(from_email="invalid-email")


class TestStorageConfig:
    """Testes para configuração de armazenamento."""
    
    def test_storage_config_local(self):
        """Testa configuração de armazenamento local."""
        config = StorageConfig(
            storage_type="local",
            local_path="/var/medai/uploads",
            max_file_size=10485760,  # 10MB
            allowed_extensions=[".pdf", ".jpg", ".png", ".dcm"]
        )
        
        assert config.storage_type == "local"
        assert config.local_path == "/var/medai/uploads"
        assert config.max_file_size == 10485760
    
    def test_storage_config_s3(self):
        """Testa configuração de armazenamento S3."""
        config = StorageConfig(
            storage_type="s3",
            s3_bucket="medai-uploads",
            s3_region="us-east-1",
            s3_access_key="AKIAIOSFODNN7EXAMPLE",
            s3_secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            s3_endpoint_url="https://s3.amazonaws.com"
        )
        
        assert config.storage_type == "s3"
        assert config.s3_bucket == "medai-uploads"
        assert config.s3_region == "us-east-1"
    
    def test_storage_config_file_organization(self):
        """Testa configuração de organização de arquivos."""
        config = StorageConfig(
            organize_by_date=True,
            organize_by_type=True,
            date_format="%Y/%m/%d",
            create_thumbnails=True,
            thumbnail_sizes=[(150, 150), (300, 300)]
        )
        
        assert config.organize_by_date is True
        assert config.date_format == "%Y/%m/%d"
        assert len(config.thumbnail_sizes) == 2


class TestEnvironmentConfig:
    """Testes para carregamento de configuração de ambiente."""
    
    def test_load_environment_config_development(self):
        """Testa carregamento de config de desenvolvimento."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            config = load_environment_config()
            
            assert config["debug"] is True
            assert config["log_level"] == "DEBUG"
            assert "sqlite" in config.get("database_url", "")
    
    def test_load_environment_config_production(self):
        """Testa carregamento de config de produção."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            config = load_environment_config()
            
            assert config["debug"] is False
            assert config["log_level"] == "INFO"
            assert config["use_https"] is True
    
    def test_load_environment_config_testing(self):
        """Testa carregamento de config de teste."""
        with patch.dict(os.environ, {"ENVIRONMENT": "testing"}):
            config = load_environment_config()
            
            assert config["testing"] is True
            assert ":memory:" in config.get("database_url", "")
    
    def test_environment_specific_overrides(self):
        """Testa overrides específicos por ambiente."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "staging",
            "DATABASE_URL": "postgresql://staging-db",
            "DEBUG": "false"
        }):
            config = load_environment_config()
            
            assert config["database_url"] == "postgresql://staging-db"
            assert config["debug"] is False


class TestConfigValidation:
    """Testes para validação geral de configurações."""
    
    def test_required_settings_validation(self):
        """Testa que configurações obrigatórias são validadas."""
        with patch.dict(os.environ, {
            "SECRET_KEY": "",  # Vazio
            "DATABASE_URL": ""  # Vazio
        }):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert any(e["loc"] == ("secret_key",) for e in errors)
    
    def test_config_type_coercion(self):
        """Testa conversão automática de tipos."""
        with patch.dict(os.environ, {
            "DEBUG": "True",  # String
            "API_PORT": "8080",  # String para int
            "CORS_ORIGINS": '["http://localhost:3000","http://localhost:3001"]'  # JSON string
        }):
            settings = Settings()
            
            assert settings.debug is True  # Convertido para bool
            assert settings.api_port == 8080  # Convertido para int
            assert len(settings.cors_origins) == 2  # Parseado de JSON
    
    def test_config_with_secrets_file(self):
        """Testa carregamento de secrets de arquivo."""
        with patch("builtins.open", MagicMock()) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = '''
            SECRET_KEY=file-secret-key
            DATABASE_PASSWORD=file-db-password
            '''
            
            # Simula carregamento de arquivo .env
            settings = Settings(_env_file=".env.secrets")
            
            # Verifica que tentou abrir o arquivo
            mock_file.assert_called()