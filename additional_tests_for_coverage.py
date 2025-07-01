#!/usr/bin/env python3
"""
Testes adicionais para melhorar cobertura para 80%+
Execute após adicionar aos arquivos de teste correspondentes
"""

# ========================================
# TESTES ADICIONAIS PARA app/security.py
# ========================================

# Adicionar ao tests/unit/test_security.py

def test_verify_token_invalid():
    """Testa verificação de token inválido"""
    from app.security import verify_token
    
    # Token inválido
    result = verify_token("invalid_token")
    assert result is None

def test_verify_token_expired():
    """Testa token expirado"""
    from app.security import create_access_token, verify_token
    from datetime import timedelta
    
    # Criar token que expira imediatamente
    token = create_access_token(
        data={"sub": "test"},
        expires_delta=timedelta(seconds=-1)  # Já expirado
    )
    
    result = verify_token(token)
    assert result is None

def test_get_current_user_no_token():
    """Testa get_current_user sem token"""
    from app.security import get_current_user
    from fastapi import HTTPException
    
    with pytest.raises(HTTPException) as exc:
        get_current_user(None)
    assert exc.value.status_code == 401

def test_password_requirements():
    """Testa requisitos de senha"""
    from app.security import validate_password_strength
    
    # Senha fraca
    assert not validate_password_strength("123")
    
    # Senha forte
    assert validate_password_strength("MyStr0ngP@ssw0rd!")

def test_token_refresh():
    """Testa refresh de token"""
    from app.security import create_refresh_token, verify_refresh_token
    
    refresh_token = create_refresh_token({"sub": "test_user"})
    payload = verify_refresh_token(refresh_token)
    
    assert payload["sub"] == "test_user"


# ========================================
# TESTES ADICIONAIS PARA app/services/ml_model_service.py
# ========================================

# Adicionar ao tests/unit/test_ml_model_service.py

def test_model_prediction_error_handling():
    """Testa tratamento de erros na predição"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    
    # Dados inválidos
    result = service.predict_risk(invalid_data={})
    assert "error" in result

def test_model_loading_failure():
    """Testa falha no carregamento de modelo"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    result = service.load_model("non_existent_model")
    assert result is False

def test_batch_prediction():
    """Testa predição em lote"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    batch_data = [{"feature1": 1}, {"feature1": 2}]
    
    results = service.batch_predict(batch_data)
    assert isinstance(results, list)
    assert len(results) == 2

def test_model_metrics():
    """Testa métricas do modelo"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    metrics = service.get_model_metrics("default")
    
    assert "accuracy" in metrics
    assert "precision" in metrics

def test_feature_importance():
    """Testa importância das features"""
    from app.services.ml_model_service import MLModelService
    
    service = MLModelService()
    importance = service.get_feature_importance()
    
    assert isinstance(importance, dict)


# ========================================
# TESTES ADICIONAIS PARA app/services/validation_service.py
# ========================================

# Adicionar ao tests/unit/test_validation_service.py

def test_validate_date_range():
    """Testa validação de intervalo de datas"""
    from app.services.validation_service import ValidationService
    from datetime import date, timedelta
    
    service = ValidationService()
    
    # Data válida
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    assert service.validate_date_range(yesterday, today) is True
    
    # Data inválida (fim antes do início)
    assert service.validate_date_range(today, yesterday) is False

def test_validate_medical_data():
    """Testa validação de dados médicos"""
    from app.services.validation_service import ValidationService
    
    service = ValidationService()
    
    valid_data = {
        "blood_pressure": "120/80",
        "heart_rate": 75,
        "temperature": 36.5
    }
    
    assert service.validate_medical_data(valid_data) is True

def test_validate_exam_file():
    """Testa validação de arquivo de exame"""
    from app.services.validation_service import ValidationService
    
    service = ValidationService()
    
    # Arquivo válido
    assert service.validate_file_type("exam.pdf", [".pdf", ".jpg"]) is True
    
    # Arquivo inválido
    assert service.validate_file_type("exam.exe", [".pdf", ".jpg"]) is False

def test_validation_error_messages():
    """Testa mensagens de erro de validação"""
    from app.services.validation_service import ValidationService, ValidationError
    
    service = ValidationService()
    
    try:
        service.validate_required_field("", "nome")
        assert False, "Deveria ter lançado ValidationError"
    except ValidationError as e:
        assert "nome" in str(e)
        assert "obrigatório" in str(e).lower()


# ========================================
# TESTES ADICIONAIS PARA app/config.py
# ========================================

# Adicionar ao tests/unit/test_config.py

def test_config_validation_errors():
    """Testa erros de validação na configuração"""
    from app.config import Settings
    import pytest
    
    # Testar configuração inválida
    with pytest.raises(ValueError):
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=-1)

def test_async_database_uri():
    """Testa URI assíncrona do banco"""
    from app.config import Settings
    
    # PostgreSQL
    postgres_settings = Settings(DATABASE_URL="postgresql://user:pass@host/db")
    async_uri = postgres_settings.ASYNC_SQLALCHEMY_DATABASE_URI
    assert "postgresql+asyncpg://" in async_uri
    
    # SQLite
    sqlite_settings = Settings(DATABASE_URL="sqlite:///test.db")
    async_uri = sqlite_settings.ASYNC_SQLALCHEMY_DATABASE_URI
    assert "sqlite+aiosqlite://" in async_uri

def test_environment_specific_config():
    """Testa configurações específicas por ambiente"""
    from app.config import Settings
    
    # Desenvolvimento
    dev_settings = Settings(ENVIRONMENT="development", DEBUG=True)
    assert dev_settings.DEBUG is True
    
    # Produção
    prod_settings = Settings(ENVIRONMENT="production", DEBUG=False)
    assert prod_settings.DEBUG is False

def test_settings_repr():
    """Testa representação string das configurações"""
    from app.config import Settings
    
    settings = Settings()
    repr_str = repr(settings)
    assert "Settings" in repr_str


# ========================================
# TESTES ADICIONAIS PARA app/health.py
# ========================================

# Adicionar ao tests/unit/test_health.py

def test_database_health_check():
    """Testa verificação de saúde do banco de dados"""
    from app.health import check_database_health
    
    result = check_database_health()
    assert "status" in result
    assert result["status"] in ["healthy", "unhealthy"]

def test_redis_health_check():
    """Testa verificação de saúde do Redis"""
    from app.health import check_redis_health
    
    result = check_redis_health()
    assert "status" in result

def test_ml_models_health_check():
    """Testa verificação de saúde dos modelos ML"""
    from app.health import check_ml_models_health
    
    result = check_ml_models_health()
    assert "status" in result
    assert "models" in result

def test_system_resources_check():
    """Testa verificação de recursos do sistema"""
    from app.health import check_system_resources
    
    result = check_system_resources()
    assert "memory" in result
    assert "disk" in result

def test_health_check_aggregation():
    """Testa agregação de verificações de saúde"""
    from app.health import aggregate_health_checks
    
    checks = {
        "database": {"status": "healthy"},
        "redis": {"status": "unhealthy"},
        "ml_models": {"status": "healthy"}
    }
    
    result = aggregate_health_checks(checks)
    assert result["overall_status"] == "degraded"  # Porque Redis está unhealthy


print("✅ Todos os testes adicionais foram definidos!")
print("📋 Para implementar:")
print("1. Copie os testes relevantes para os arquivos correspondentes")
print("2. Execute: python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing")
print("3. Meta: atingir 80%+ de cobertura")
