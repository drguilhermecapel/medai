"""
Testes abrangentes para módulos core do MedAI
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import os

from app.core.config import Settings, settings
from app.core.constants import (
    UserRole, ExamType, ExamStatus, DiagnosticStatus,
    Priority, Gender, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
    ERROR_MESSAGES, NOTIFICATION_TYPES
)
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, decode_token, get_current_user
)
from app.core.database import get_db, engine, SessionLocal
from app.core.exceptions import (
    MedAIException, AuthenticationError, AuthorizationError,
    ValidationError, NotFoundError, DuplicateError
)


class TestConfig:
    """Testes para configurações do sistema"""
    
    def test_settings_initialization(self):
        """Testa inicialização das configurações"""
        assert settings.APP_NAME == "MedAI"
        assert settings.VERSION == "1.0.0"
        assert isinstance(settings.DEBUG, bool)
        assert settings.ENVIRONMENT in ["development", "staging", "production"]
    
    def test_database_url_assembly(self):
        """Testa montagem da URL do banco de dados"""
        test_settings = Settings(
            POSTGRES_SERVER="localhost",
            POSTGRES_USER="test",
            POSTGRES_PASSWORD="test123",
            POSTGRES_DB="test_db",
            POSTGRES_PORT=5432
        )
        
        expected_url = "postgresql://test:test123@localhost:5432/test_db"
        assert str(test_settings.DATABASE_URL) == expected_url
    
    def test_redis_url_assembly(self):
        """Testa montagem da URL do Redis"""
        # Sem senha
        test_settings = Settings(
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            REDIS_DB=0
        )
        assert test_settings.REDIS_URL == "redis://localhost:6379/0"
        
        # Com senha
        test_settings_with_password = Settings(
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            REDIS_PASSWORD="redis123",
            REDIS_DB=1
        )
        assert test_settings_with_password.REDIS_URL == "redis://:redis123@localhost:6379/1"
    
    def test_cors_origins_parsing(self):
        """Testa parsing de origens CORS"""
        # String única
        test_settings = Settings(
            CORS_ORIGINS="http://localhost:3000"
        )
        assert test_settings.CORS_ORIGINS == ["http://localhost:3000"]
        
        # String múltipla
        test_settings = Settings(
            CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
        )
        assert test_settings.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:8080"]
        
        # Lista
        test_settings = Settings(
            CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
        )
        assert test_settings.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:8080"]
    
    def test_environment_variables_override(self):
        """Testa sobrescrita por variáveis de ambiente"""
        with patch.dict(os.environ, {
            "DEBUG": "true",
            "SECRET_KEY": "test-secret-key",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60"
        }):
            test_settings = Settings()
            assert test_settings.DEBUG is True
            assert test_settings.SECRET_KEY == "test-secret-key"
            assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    
    def test_file_size_limits(self):
        """Testa limites de tamanho de arquivo"""
        assert settings.MAX_UPLOAD_SIZE == 10 * 1024 * 1024  # 10MB
        assert isinstance(settings.ALLOWED_EXTENSIONS, list)
        assert ".jpg" in settings.ALLOWED_EXTENSIONS
    
    def test_ml_settings(self):
        """Testa configurações de ML"""
        assert settings.ML_MODEL_VERSION == "1.0.0"
        assert settings.ML_BATCH_SIZE > 0
        assert settings.ML_MAX_WORKERS > 0


class TestConstants:
    """Testes para constantes do sistema"""
    
    def test_user_roles(self):
        """Testa enum de papéis de usuário"""
        assert UserRole.ADMIN == "admin"
        assert UserRole.DOCTOR == "doctor"
        assert UserRole.NURSE == "nurse"
        assert UserRole.PATIENT == "patient"
        assert UserRole.TECHNICIAN == "technician"
        
        # Testa conversão
        assert UserRole("admin") == UserRole.ADMIN
        assert UserRole.ADMIN.value == "admin"
    
    def test_exam_types(self):
        """Testa tipos de exames"""
        exam_types = [ExamType.ECG, ExamType.BLOOD_TEST, ExamType.XRAY,
                     ExamType.MRI, ExamType.CT_SCAN, ExamType.ULTRASOUND]
        
        assert len(exam_types) == 6
        
        for exam_type in exam_types:
            assert isinstance(exam_type.value, str)
            assert exam_type.value.islower()
    
    def test_exam_status(self):
        """Testa status de exames"""
        statuses = [ExamStatus.PENDING, ExamStatus.IN_PROGRESS,
                   ExamStatus.COMPLETED, ExamStatus.CANCELLED, ExamStatus.FAILED]
        
        assert len(statuses) == 5
        
        # Testa transições válidas
        valid_transitions = {
            ExamStatus.PENDING: [ExamStatus.IN_PROGRESS, ExamStatus.CANCELLED],
            ExamStatus.IN_PROGRESS: [ExamStatus.COMPLETED, ExamStatus.FAILED, ExamStatus.CANCELLED],
            ExamStatus.COMPLETED: [],
            ExamStatus.CANCELLED: [],
            ExamStatus.FAILED: []
        }
        
        # Verifica que todas as transições são cobertas
        for status in statuses:
            assert status in valid_transitions
    
    def test_priority_levels(self):
        """Testa níveis de prioridade"""
        priorities = [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL]
        
        assert len(priorities) == 4
        
        # Testa ordenação
        priority_order = {
            Priority.LOW: 1,
            Priority.MEDIUM: 2,
            Priority.HIGH: 3,
            Priority.CRITICAL: 4
        }
        
        sorted_priorities = sorted(priorities, key=lambda p: priority_order[p])
        assert sorted_priorities == priorities
    
    def test_validation_constants(self):
        """Testa constantes de validação"""
        assert MIN_PASSWORD_LENGTH == 8
        assert MAX_PASSWORD_LENGTH == 128
        assert MIN_PASSWORD_LENGTH < MAX_PASSWORD_LENGTH
        
        # Testa limites de paginação
        from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
        assert DEFAULT_PAGE_SIZE == 20
        assert MAX_PAGE_SIZE == 100
        assert DEFAULT_PAGE_SIZE <= MAX_PAGE_SIZE
    
    def test_ecg_constants(self):
        """Testa constantes de ECG"""
        from app.core.constants import (
            ECG_SAMPLE_RATE, ECG_DURATION, ECG_LEADS,
            MIN_HEART_RATE, MAX_HEART_RATE
        )
        
        assert ECG_SAMPLE_RATE == 500
        assert ECG_DURATION == 10
        assert ECG_LEADS == 12
        assert MIN_HEART_RATE == 40
        assert MAX_HEART_RATE == 200
        assert MIN_HEART_RATE < MAX_HEART_RATE
    
    def test_error_messages(self):
        """Testa mensagens de erro"""
        required_messages = [
            "INVALID_CREDENTIALS", "USER_NOT_FOUND", "UNAUTHORIZED",
            "FORBIDDEN", "NOT_FOUND", "INTERNAL_ERROR"
        ]
        
        for msg_key in required_messages:
            assert msg_key in ERROR_MESSAGES
            assert isinstance(ERROR_MESSAGES[msg_key], str)
            assert len(ERROR_MESSAGES[msg_key]) > 0
    
    def test_notification_types(self):
        """Testa tipos de notificação"""
        required_types = [
            "EXAM_READY", "DIAGNOSIS_COMPLETE",
            "APPOINTMENT_REMINDER", "CRITICAL_RESULT"
        ]
        
        for type_key in required_types:
            assert type_key in NOTIFICATION_TYPES
            assert isinstance(NOTIFICATION_TYPES[type_key], str)


class TestSecurity:
    """Testes para módulo de segurança"""
    
    def test_password_hashing(self):
        """Testa hash de senha"""
        password = "Test@123456"
        
        # Testa criação de hash
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 20
        
        # Testa verificação
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_password_hash_uniqueness(self):
        """Testa unicidade do hash"""
        password = "Test@123456"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Hashes devem ser diferentes devido ao salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_create_access_token(self):
        """Testa criação de token de acesso"""
        user_id = 123
        token = create_access_token(user_id)
        
        assert isinstance(token, str)
        assert len(token) > 20
        
        # Decodifica token
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        assert "exp" in payload
    
    def test_create_refresh_token(self):
        """Testa criação de token de refresh"""
        user_id = 456
        token = create_refresh_token(user_id)
        
        assert isinstance(token, str)
        assert len(token) > 20
        
        # Decodifica token
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_token_expiration(self):
        """Testa expiração de token"""
        user_id = 789
        
        # Token com expiração curta
        with patch('app.core.security.settings.ACCESS_TOKEN_EXPIRE_MINUTES', 0):
            token = create_access_token(user_id)
            
            # Deve estar expirado
            with pytest.raises(Exception):  # Token expirado deve lançar exceção
                decode_token(token)
    
    def test_token_with_additional_claims(self):
        """Testa token com claims adicionais"""
        user_id = 999
        additional_claims = {
            "role": UserRole.DOCTOR.value,
            "permissions": ["read", "write"]
        }
        
        token = create_access_token(user_id, additional_claims)
        payload = decode_token(token)
        
        assert payload["role"] == UserRole.DOCTOR.value
        assert payload["permissions"] == ["read", "write"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self):
        """Testa obtenção do usuário atual"""
        # Mock do repositório de usuário
        mock_user = Mock()
        mock_user.id = 123
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        with patch('app.repositories.user_repository.UserRepository.get') as mock_get:
            mock_get.return_value = mock_user
            
            # Token válido
            token = create_access_token(123)
            
            # Mock da sessão do banco
            mock_db = Mock()
            
            user = await get_current_user(token, mock_db)
            assert user.id == 123
            assert user.email == "test@example.com"
    
    def test_invalid_token_format(self):
        """Testa formato de token inválido"""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid",
            "",
            None
        ]
        
        for token in invalid_tokens:
            with pytest.raises(Exception):
                decode_token(token)


class TestDatabase:
    """Testes para configuração de banco de dados"""
    
    def test_database_session(self):
        """Testa sessão do banco de dados"""
        session = SessionLocal()
        assert session is not None
        session.close()
    
    def test_get_db_generator(self):
        """Testa gerador de sessão do banco"""
        db_gen = get_db()
        db = next(db_gen)
        
        assert db is not None
        
        # Cleanup
        try:
            next(db_gen)
        except StopIteration:
            pass
    
    def test_database_url_format(self):
        """Testa formato da URL do banco"""
        from app.core.config import settings
        
        assert settings.DATABASE_URL is not None
        db_url = str(settings.DATABASE_URL)
        assert db_url.startswith("postgresql://")
        assert "@" in db_url
        assert ":" in db_url


class TestExceptions:
    """Testes para exceções customizadas"""
    
    def test_medai_exception(self):
        """Testa exceção base MedAI"""
        with pytest.raises(MedAIException) as exc_info:
            raise MedAIException("Erro teste", status_code=400)
        
        assert exc_info.value.detail == "Erro teste"
        assert exc_info.value.status_code == 400
    
    def test_authentication_error(self):
        """Testa erro de autenticação"""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Credenciais inválidas")
        
        assert exc_info.value.status_code == 401
        assert "Credenciais inválidas" in str(exc_info.value.detail)
    
    def test_authorization_error(self):
        """Testa erro de autorização"""
        with pytest.raises(AuthorizationError) as exc_info:
            raise AuthorizationError("Sem permissão")
        
        assert exc_info.value.status_code == 403
        assert "Sem permissão" in str(exc_info.value.detail)
    
    def test_validation_error(self):
        """Testa erro de validação"""
        errors = {
            "email": "Email inválido",
            "password": "Senha muito curta"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(errors)
        
        assert exc_info.value.status_code == 422
        assert exc_info.value.errors == errors
    
    def test_not_found_error(self):
        """Testa erro de não encontrado"""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("Usuário", 123)
        
        assert exc_info.value.status_code == 404
        assert "Usuário" in str(exc_info.value.detail)
        assert "123" in str(exc_info.value.detail)
    
    def test_duplicate_error(self):
        """Testa erro de duplicação"""
        with pytest.raises(DuplicateError) as exc_info:
            raise DuplicateError("email", "test@example.com")
        
        assert exc_info.value.status_code == 409
        assert "email" in str(exc_info.value.detail)
        assert "test@example.com" in str(exc_info.value.detail)


class TestLogging:
    """Testes para configuração de logging"""
    
    def test_log_configuration(self):
        """Testa configuração de logs"""
        from app.core.config import settings
        import logging
        
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert isinstance(settings.LOG_FORMAT, str)
        assert "%(asctime)s" in settings.LOG_FORMAT
    
    def test_logger_creation(self):
        """Testa criação de logger"""
        import logging
        
        logger = logging.getLogger("test_logger")
        assert logger is not None
        
        # Testa níveis de log
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        for name, level in log_levels.items():
            assert hasattr(logging, name)
            assert getattr(logging, name) == level


class TestMiddleware:
    """Testes para middleware do sistema"""
    
    def test_cors_configuration(self):
        """Testa configuração CORS"""
        from app.core.config import settings
        
        assert isinstance(settings.CORS_ORIGINS, list)
        assert len(settings.CORS_ORIGINS) > 0
        assert settings.CORS_ALLOW_CREDENTIALS in [True, False]
        assert "*" in settings.CORS_ALLOW_METHODS or isinstance(settings.CORS_ALLOW_METHODS, list)
    
    def test_request_id_generation(self):
        """Testa geração de ID de requisição"""
        import uuid
        
        request_id = str(uuid.uuid4())
        assert len(request_id) == 36
        assert request_id.count("-") == 4


class TestCache:
    """Testes para configuração de cache"""
    
    def test_cache_configuration(self):
        """Testa configuração de cache"""
        from app.core.constants import CACHE_TTL, CACHE_KEY_PREFIX
        
        assert CACHE_TTL == 3600  # 1 hora
        assert CACHE_KEY_PREFIX == "medai:"
    
    def test_cache_key_generation(self):
        """Testa geração de chaves de cache"""
        from app.core.constants import CACHE_KEY_PREFIX
        
        user_id = 123
        cache_key = f"{CACHE_KEY_PREFIX}user:{user_id}"
        
        assert cache_key == "medai:user:123"
        assert cache_key.startswith(CACHE_KEY_PREFIX)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])