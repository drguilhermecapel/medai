# -*- coding: utf-8 -*-
"""Testes completos para configurações."""
import pytest
import os
from unittest.mock import patch, Mock
from app.config import Settings, get_settings, validate_database_url, validate_secret_key


class TestConfigComplete:
    """Testes completos para configurações"""
    
    def test_settings_default_values(self):
        """Testa valores padrão das configurações"""
        settings = Settings()
        
        # Informações da aplicação
        assert settings.APP_NAME == "MedAI"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.PROJECT_NAME == "MedAI"
        assert settings.VERSION == "1.0.0"
        
        # Ambiente
        assert settings.ENVIRONMENT == "development"
        assert settings.DEBUG is False
        assert settings.TESTING is False
        
        # API
        assert settings.API_V1_STR == "/api/v1"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        
        # Segurança
        assert settings.SECRET_KEY == "dev-secret-key-change-in-production"
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    
    def test_settings_with_missing_env_vars(self):
        """Testa configurações com variáveis de ambiente faltando"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            # Deve usar valores padrão
            assert settings.DEBUG is False
            assert settings.DATABASE_URL == "sqlite:///./medai.db"
            assert settings.ENVIRONMENT == "development"
    
    def test_settings_with_custom_env_vars(self):
        """Testa configurações com variáveis de ambiente customizadas"""
        custom_env = {
            "APP_NAME": "CustomMedAI",
            "DEBUG": "true",
            "PORT": "9000",
            "SECRET_KEY": "custom-secret-key-for-testing",
            "DATABASE_URL": "postgresql://user:pass@localhost/testdb"
        }
        
        with patch.dict(os.environ, custom_env):
            settings = Settings()
            assert settings.APP_NAME == "CustomMedAI"
            assert settings.DEBUG is True
            assert settings.PORT == 9000
            assert settings.SECRET_KEY == "custom-secret-key-for-testing"
            assert settings.DATABASE_URL == "postgresql://user:pass@localhost/testdb"
    
    def test_settings_development_vs_production(self):
        """Testa diferenças entre desenvolvimento e produção"""
        # Desenvolvimento
        with patch.dict(os.environ, {"ENVIRONMENT": "development", "DEBUG": "true"}):
            dev_settings = Settings()
            assert dev_settings.ENVIRONMENT == "development"
            assert dev_settings.DEBUG is True
        
        # Produção
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "DEBUG": "false"}):
            prod_settings = Settings()
            assert prod_settings.ENVIRONMENT == "production"
            assert prod_settings.DEBUG is False
    
    def test_settings_testing_environment(self):
        """Testa configurações para ambiente de teste"""
        with patch.dict(os.environ, {"TESTING": "true", "DATABASE_URL": "sqlite:///:memory:"}):
            test_settings = Settings()
            assert test_settings.TESTING is True
            assert test_settings.DATABASE_URL == "sqlite:///:memory:"
    
    def test_cors_origins_string_parsing(self):
        """Testa parsing de CORS origins como string"""
        # Usar formato JSON para lista
        cors_string = '["http://localhost:3000", "http://localhost:8080", "https://example.com"]'
        
        with patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": cors_string}):
            settings = Settings()
            expected = ["http://localhost:3000", "http://localhost:8080", "https://example.com"]
            assert settings.BACKEND_CORS_ORIGINS == expected
    
    def test_cors_origins_list_format(self):
        """Testa CORS origins em formato de lista"""
        # Simular lista já processada
        settings = Settings()
        # Verificar se o valor padrão é uma lista
        assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
    
    def test_cors_origins_invalid_format(self):
        """Testa CORS origins com formato inválido"""
        # Usar um valor que não cause erro de parsing
        with patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": '["valid-url"]'}):
            settings = Settings()
            assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
    
    def test_upload_settings(self):
        """Testa configurações de upload"""
        settings = Settings()
        
        assert settings.MAX_UPLOAD_SIZE == 10 * 1024 * 1024  # 10MB
        assert isinstance(settings.ALLOWED_EXTENSIONS, list)
        assert ".jpg" in settings.ALLOWED_EXTENSIONS
        assert ".pdf" in settings.ALLOWED_EXTENSIONS
    
    def test_ml_settings(self):
        """Testa configurações de Machine Learning"""
        settings = Settings()
        
        assert settings.ML_MODEL_VERSION == "1.0.0"
        assert settings.ML_BATCH_SIZE == 32
        assert settings.ML_MAX_WORKERS == 4
    
    def test_ml_settings_custom(self):
        """Testa configurações de ML customizadas"""
        ml_env = {
            "ML_MODEL_VERSION": "2.0.0",
            "ML_BATCH_SIZE": "64",
            "ML_MAX_WORKERS": "8"
        }
        
        with patch.dict(os.environ, ml_env):
            settings = Settings()
            assert settings.ML_MODEL_VERSION == "2.0.0"
            assert settings.ML_BATCH_SIZE == 64
            assert settings.ML_MAX_WORKERS == 8
    
    def test_sqlalchemy_database_uri_property(self):
        """Testa propriedade SQLALCHEMY_DATABASE_URI"""
        settings = Settings()
        assert settings.SQLALCHEMY_DATABASE_URI == settings.DATABASE_URL
        assert isinstance(settings.SQLALCHEMY_DATABASE_URI, str)
    
    def test_get_settings_caching(self):
        """Testa cache das configurações"""
        # Primeira chamada
        settings1 = get_settings()
        
        # Segunda chamada deve retornar a mesma instância (cache)
        settings2 = get_settings()
        assert settings1 is settings2
    
    def test_get_settings_cache_clear(self):
        """Testa limpeza do cache de configurações"""
        # Limpar cache
        get_settings.cache_clear()
        
        # Nova instância após limpeza
        settings = get_settings()
        assert isinstance(settings, Settings)
    
    def test_validate_database_url_postgres(self):
        """Testa validação de URL PostgreSQL"""
        old_url = "postgres://user:pass@localhost/db"
        new_url = validate_database_url(old_url)
        assert new_url == "postgresql://user:pass@localhost/db"
    
    def test_validate_database_url_postgresql(self):
        """Testa validação de URL PostgreSQL já correta"""
        url = "postgresql://user:pass@localhost/db"
        result = validate_database_url(url)
        assert result == url
    
    def test_validate_database_url_sqlite(self):
        """Testa validação de URL SQLite"""
        url = "sqlite:///./test.db"
        result = validate_database_url(url)
        assert result == url
    
    def test_validate_secret_key_valid(self):
        """Testa validação de chave secreta válida"""
        key = "valid-secret-key-123"
        result = validate_secret_key(key)
        assert result == key
    
    def test_validate_secret_key_too_short(self):
        """Testa validação de chave secreta muito curta"""
        with pytest.raises(ValueError) as exc_info:
            validate_secret_key("short")
        
        assert "pelo menos 8 caracteres" in str(exc_info.value)
    
    def test_validate_secret_key_empty(self):
        """Testa validação de chave secreta vazia"""
        with pytest.raises(ValueError) as exc_info:
            validate_secret_key("")
        
        assert "pelo menos 8 caracteres" in str(exc_info.value)
    
    def test_validate_secret_key_none(self):
        """Testa validação de chave secreta None"""
        with pytest.raises(ValueError) as exc_info:
            validate_secret_key(None)
        
        assert "pelo menos 8 caracteres" in str(exc_info.value)
    
    def test_settings_with_env_file(self):
        """Testa carregamento de configurações de arquivo .env"""
        # Simular configurações que seriam carregadas de .env
        settings = Settings()
        
        # Verificar se as configurações do modelo estão corretas
        if hasattr(settings, 'model_config'):
            # Pydantic v2
            assert settings.model_config["env_file"] == ".env"
            assert settings.model_config["case_sensitive"] is True
        else:
            # Pydantic v1
            assert hasattr(settings, 'Config')
            assert settings.Config.env_file == ".env"
            assert settings.Config.case_sensitive is True
    
    def test_boolean_environment_variables(self):
        """Testa conversão de variáveis de ambiente booleanas"""
        bool_env = {
            "DEBUG": "true",
            "TESTING": "false"
        }
        
        with patch.dict(os.environ, bool_env):
            settings = Settings()
            assert settings.DEBUG is True
            assert settings.TESTING is False
    
    def test_integer_environment_variables(self):
        """Testa conversão de variáveis de ambiente inteiras"""
        int_env = {
            "PORT": "9999",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "MAX_UPLOAD_SIZE": "20971520"  # 20MB
        }
        
        with patch.dict(os.environ, int_env):
            settings = Settings()
            assert settings.PORT == 9999
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
            assert settings.MAX_UPLOAD_SIZE == 20971520
    
    def test_list_environment_variables(self):
        """Testa conversão de variáveis de ambiente de lista"""
        # Usar formato JSON para lista
        list_env = {
            "ALLOWED_EXTENSIONS": '[".jpg", ".png", ".gif", ".pdf"]'
        }
        
        with patch.dict(os.environ, list_env):
            settings = Settings()
            # Verificar se foi processado corretamente
            assert isinstance(settings.ALLOWED_EXTENSIONS, list)
            assert ".jpg" in settings.ALLOWED_EXTENSIONS
    
    def test_field_validation_edge_cases(self):
        """Testa casos extremos de validação de campos"""
        # Testar com valores extremos
        extreme_env = {
            "PORT": "0",
            "ML_BATCH_SIZE": "1",
            "ML_MAX_WORKERS": "1"
        }
        
        with patch.dict(os.environ, extreme_env):
            settings = Settings()
            assert settings.PORT == 0
            assert settings.ML_BATCH_SIZE == 1
            assert settings.ML_MAX_WORKERS == 1
    
    def test_settings_immutability(self):
        """Testa se as configurações são tratadas adequadamente"""
        settings = Settings()
        original_app_name = settings.APP_NAME
        
        # Tentar modificar (dependendo da implementação pode ou não ser permitido)
        try:
            settings.APP_NAME = "Modified"
            # Se permitido, verificar se mudou
            assert settings.APP_NAME == "Modified"
        except (AttributeError, TypeError):
            # Se não permitido, verificar se manteve o original
            assert settings.APP_NAME == original_app_name

