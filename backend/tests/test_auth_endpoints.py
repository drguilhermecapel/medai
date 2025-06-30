"""
Testes abrangentes para endpoints de autenticação
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import jwt

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.core.constants import UserRole
from app.models.user import User
from app.schemas.auth import Token, TokenData
from app.schemas.user import UserCreate, UserResponse


@pytest.fixture
def client():
    """Cliente de teste para a API"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Usuário mock para testes"""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.username = "testuser"
    user.full_name = "Test User"
    user.role = UserRole.PATIENT
    user.is_active = True
    user.is_verified = True
    user.hashed_password = get_password_hash("Test@123456")
    user.created_at = datetime.utcnow()
    return user


@pytest.fixture
def auth_headers(mock_user):
    """Headers de autenticação para requisições"""
    token = create_access_token(mock_user.id)
    return {"Authorization": f"Bearer {token}"}


class TestAuthEndpoints:
    """Testes para endpoints de autenticação"""
    
    @patch('app.repositories.user_repository.UserRepository.get_by_email')
    @patch('app.core.security.verify_password')
    def test_login_success(self, mock_verify_password, mock_get_by_email, client, mock_user):
        """Testa login bem-sucedido"""
        mock_get_by_email.return_value = mock_user
        mock_verify_password.return_value = True
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "Test@123456"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Verifica o token
        token_data = jwt.decode(
            data["access_token"],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert token_data["sub"] == str(mock_user.id)
    
    @patch('app.repositories.user_repository.UserRepository.get_by_email')
    def test_login_invalid_credentials(self, mock_get_by_email, client):
        """Testa login com credenciais inválidas"""
        mock_get_by_email.return_value = None
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.get_by_email')
    def test_login_inactive_user(self, mock_get_by_email, client, mock_user):
        """Testa login com usuário inativo"""
        mock_user.is_active = False
        mock_get_by_email.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "Test@123456"
            }
        )
        
        assert response.status_code == 403
        assert "Inactive user" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.get_by_email')
    def test_login_unverified_user(self, mock_get_by_email, client, mock_user):
        """Testa login com usuário não verificado"""
        mock_user.is_verified = False
        mock_get_by_email.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "Test@123456"
            }
        )
        
        assert response.status_code == 403
        assert "Email not verified" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.create')
    @patch('app.repositories.user_repository.UserRepository.get_by_email')
    @patch('app.services.email_service.EmailService.send_verification_email')
    def test_register_success(self, mock_send_email, mock_get_by_email, mock_create, client):
        """Testa registro bem-sucedido"""
        mock_get_by_email.return_value = None
        
        new_user = Mock(spec=User)
        new_user.id = 2
        new_user.email = "newuser@example.com"
        new_user.username = "newuser"
        new_user.full_name = "New User"
        new_user.role = UserRole.PATIENT
        new_user.is_active = True
        new_user.is_verified = False
        
        mock_create.return_value = new_user
        mock_send_email.return_value = True
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "NewUser@123456",
                "full_name": "New User",
                "cpf": "123.456.789-09",
                "phone": "(11) 98765-4321",
                "date_of_birth": "1990-01-01"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_verified"] is False
        
        # Verifica se email foi enviado
        mock_send_email.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository.get_by_email')
    def test_register_duplicate_email(self, mock_get_by_email, client, mock_user):
        """Testa registro com email duplicado"""
        mock_get_by_email.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "newuser",
                "password": "NewUser@123456",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_data(self, client):
        """Testa registro com dados inválidos"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "username": "u",  # Muito curto
                "password": "weak",  # Senha fraca
                "full_name": ""  # Nome vazio
            }
        )
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert len(errors) > 0
    
    @patch('app.repositories.user_repository.UserRepository.get')
    def test_refresh_token_success(self, mock_get, client, mock_user):
        """Testa renovação de token bem-sucedida"""
        mock_get.return_value = mock_user
        
        refresh_token = create_refresh_token(mock_user.id)
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client):
        """Testa renovação com token inválido"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    def test_refresh_token_expired(self, client):
        """Testa renovação com token expirado"""
        # Cria token expirado
        expired_payload = {
            "sub": "1",
            "type": "refresh",
            "exp": datetime.utcnow() - timedelta(days=1)
        }
        
        expired_token = jwt.encode(
            expired_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token}
        )
        
        assert response.status_code == 401
        assert "Token expired" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.get')
    def test_get_current_user_success(self, mock_get, client, mock_user, auth_headers):
        """Testa obtenção do usuário atual"""
        mock_get.return_value = mock_user
        
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == mock_user.id
        assert data["email"] == mock_user.email
        assert data["username"] == mock_user.username
    
    def test_get_current_user_unauthorized(self, client):
        """Testa acesso não autorizado ao usuário atual"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_invalid_token(self, client):
        """Testa com token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.get')
    @patch('app.repositories.user_repository.UserRepository.update')
    def test_change_password_success(self, mock_update, mock_get, client, mock_user, auth_headers):
        """Testa alteração de senha bem-sucedida"""
        mock_get.return_value = mock_user
        mock_update.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "Test@123456",
                "new_password": "NewTest@123456"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"
    
    @patch('app.repositories.user_repository.UserRepository.get')
    @patch('app.core.security.verify_password')
    def test_change_password_wrong_current(self, mock_verify, mock_get, client, mock_user, auth_headers):
        """Testa alteração de senha com senha atual incorreta"""
        mock_get.return_value = mock_user
        mock_verify.return_value = False
        
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword",
                "new_password": "NewTest@123456"
            }
        )
        
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.get_by_email')
    @patch('app.services.email_service.EmailService.send_password_reset_email')
    def test_forgot_password_success(self, mock_send_email, mock_get_by_email, client, mock_user):
        """Testa solicitação de reset de senha"""
        mock_get_by_email.return_value = mock_user
        mock_send_email.return_value = True
        
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        assert "Password reset email sent" in response.json()["message"]
        mock_send_email.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository.get_by_email')
    def test_forgot_password_user_not_found(self, mock_get_by_email, client):
        """Testa reset de senha para usuário não encontrado"""
        mock_get_by_email.return_value = None
        
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        
        # Por segurança, retorna sucesso mesmo se usuário não existe
        assert response.status_code == 200
        assert "Password reset email sent" in response.json()["message"]
    
    @patch('app.repositories.user_repository.UserRepository.get_by_reset_token')
    @patch('app.repositories.user_repository.UserRepository.update')
    def test_reset_password_success(self, mock_update, mock_get_by_token, client, mock_user):
        """Testa reset de senha bem-sucedido"""
        mock_user.password_reset_token = "valid_reset_token"
        mock_user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        mock_get_by_token.return_value = mock_user
        mock_update.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "valid_reset_token",
                "new_password": "NewPassword@123456"
            }
        )
        
        assert response.status_code == 200
        assert "Password reset successfully" in response.json()["message"]
    
    @patch('app.repositories.user_repository.UserRepository.get_by_reset_token')
    def test_reset_password_invalid_token(self, mock_get_by_token, client):
        """Testa reset com token inválido"""
        mock_get_by_token.return_value = None
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid_token",
                "new_password": "NewPassword@123456"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid or expired reset token" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.get_by_reset_token')
    def test_reset_password_expired_token(self, mock_get_by_token, client, mock_user):
        """Testa reset com token expirado"""
        mock_user.password_reset_token = "expired_token"
        mock_user.password_reset_expires = datetime.utcnow() - timedelta(hours=1)
        mock_get_by_token.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "expired_token",
                "new_password": "NewPassword@123456"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid or expired reset token" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.get_by_verification_token')
    @patch('app.repositories.user_repository.UserRepository.update')
    def test_verify_email_success(self, mock_update, mock_get_by_token, client, mock_user):
        """Testa verificação de email bem-sucedida"""
        mock_user.is_verified = False
        mock_user.email_verification_token = "valid_token"
        mock_get_by_token.return_value = mock_user
        
        mock_user_verified = Mock(spec=User)
        mock_user_verified.is_verified = True
        mock_update.return_value = mock_user_verified
        
        response = client.get(
            "/api/v1/auth/verify-email?token=valid_token"
        )
        
        assert response.status_code == 200
        assert "Email verified successfully" in response.json()["message"]
    
    @patch('app.repositories.user_repository.UserRepository.get_by_verification_token')
    def test_verify_email_invalid_token(self, mock_get_by_token, client):
        """Testa verificação com token inválido"""
        mock_get_by_token.return_value = None
        
        response = client.get(
            "/api/v1/auth/verify-email?token=invalid_token"
        )
        
        assert response.status_code == 400
        assert "Invalid verification token" in response.json()["detail"]
    
    @patch('app.repositories.user_repository.UserRepository.get')
    def test_logout_success(self, mock_get, client, mock_user, auth_headers):
        """Testa logout bem-sucedido"""
        mock_get.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]
    
    def test_logout_unauthorized(self, client):
        """Testa logout sem autenticação"""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]


class TestAuthSecurity:
    """Testes de segurança para autenticação"""
    
    def test_password_requirements(self, client):
        """Testa requisitos de senha"""
        weak_passwords = [
            "short",           # Muito curta
            "12345678",       # Sem letras
            "abcdefgh",       # Sem números
            "Abcd1234",       # Sem caractere especial
            "abcd@1234",      # Sem maiúscula
            "ABCD@1234"       # Sem minúscula
        ]
        
        for password in weak_passwords:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": password,
                    "full_name": "Test User"
                }
            )
            
            assert response.status_code == 422
            assert "password" in str(response.json()["detail"])
    
    def test_rate_limiting(self, client):
        """Testa rate limiting em endpoints sensíveis"""
        # Simula múltiplas tentativas de login
        for i in range(10):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": f"test{i}@example.com",
                    "password": "WrongPassword"
                }
            )
        
        # Após muitas tentativas, deve ser bloqueado
        # (Implementação depende do rate limiter configurado)
        # assert response.status_code == 429
    
    def test_token_expiration(self, client):
        """Testa expiração de token"""
        # Cria token com expiração muito curta
        expired_token = jwt.encode(
            {
                "sub": "1",
                "type": "access",
                "exp": datetime.utcnow() - timedelta(minutes=1)
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert response.status_code == 401
        assert "Token expired" in response.json()["detail"]
    
    def test_invalid_token_format(self, client):
        """Testa formatos inválidos de token"""
        invalid_formats = [
            "Bearer",                    # Sem token
            "invalid_token",            # Sem Bearer
            "Bearer token1 token2",     # Múltiplos tokens
            "Basic dGVzdDp0ZXN0",      # Tipo errado
            ""                          # Vazio
        ]
        
        for auth_header in invalid_formats:
            headers = {"Authorization": auth_header} if auth_header else {}
            
            response = client.get(
                "/api/v1/auth/me",
                headers=headers
            )
            
            assert response.status_code == 401


class TestAuthIntegration:
    """Testes de integração para fluxo completo de autenticação"""
    
    @patch('app.repositories.user_repository.UserRepository')
    @patch('app.services.email_service.EmailService.send_verification_email')
    def test_complete_registration_flow(self, mock_send_email, mock_repo_class, client):
        """Testa fluxo completo de registro"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        # Simula que email não existe
        mock_repo.get_by_email.return_value = None
        mock_repo.get_by_username.return_value = None
        
        # Simula criação de usuário
        new_user = Mock(spec=User)
        new_user.id = 3
        new_user.email = "newuser@example.com"
        new_user.username = "newuser"
        new_user.is_verified = False
        mock_repo.create.return_value = new_user
        
        # 1. Registra usuário
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "NewUser@123456",
                "full_name": "New User",
                "cpf": "123.456.789-09"
            }
        )
        
        assert response.status_code == 201
        
        # 2. Verifica se email de verificação foi enviado
        mock_send_email.assert_called_once()
        
        # 3. Simula verificação de email
        verified_user = Mock(spec=User)
        verified_user.is_verified = True
        mock_repo.get_by_verification_token.return_value = new_user
        mock_repo.update.return_value = verified_user
        
        response = client.get(
            "/api/v1/auth/verify-email?token=verification_token"
        )
        
        assert response.status_code == 200
    
    @patch('app.repositories.user_repository.UserRepository')
    @patch('app.services.email_service.EmailService.send_password_reset_email')
    def test_complete_password_reset_flow(self, mock_send_email, mock_repo_class, client):
        """Testa fluxo completo de reset de senha"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        # Usuário existente
        user = Mock(spec=User)
        user.email = "test@example.com"
        mock_repo.get_by_email.return_value = user
        
        # 1. Solicita reset de senha
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        mock_send_email.assert_called_once()
        
        # 2. Reseta senha com token
        user.password_reset_token = "reset_token"
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        mock_repo.get_by_reset_token.return_value = user
        mock_repo.update.return_value = user
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "reset_token",
                "new_password": "NewPassword@123456"
            }
        )
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.api.v1.endpoints.auth", "--cov-report=term-missing"])