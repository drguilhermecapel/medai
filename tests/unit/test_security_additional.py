# -*- coding: utf-8 -*-
"""Testes adicionais para cobrir linhas perdidas no módulo security."""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt, JWTError

from app.security import (
    create_access_token, create_refresh_token, decode_access_token,
    verify_password, get_password_hash, get_current_user,
    check_permissions, validate_token_claims,
    AuthenticationError, AuthorizationError,
    SECRET_KEY, ALGORITHM
)


class TestSecurityAdditional:
    """Testes adicionais para cobrir linhas perdidas"""
    
    def test_create_access_token_with_expiry(self):
        """Testa criação de token com expiração customizada"""
        token = create_access_token(
            data={"sub": "test@test.com"},
            expires_delta=timedelta(minutes=30)
        )
        assert token is not None
        assert isinstance(token, str)
        
        # Verificar se o token pode ser decodificado
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "test@test.com"
        assert "exp" in payload
    
    def test_create_access_token_without_expiry(self):
        """Testa criação de token sem expiração customizada (usa padrão)"""
        token = create_access_token(data={"sub": "test@test.com"})
        assert token is not None
        assert isinstance(token, str)
        
        # Verificar se o token pode ser decodificado
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "test@test.com"
    
    def test_create_refresh_token(self):
        """Testa criação de refresh token"""
        token = create_refresh_token(data={"sub": "test@test.com"})
        assert token is not None
        assert isinstance(token, str)
        
        # Verificar se o token pode ser decodificado
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "test@test.com"
        assert payload["type"] == "refresh"
    
    def test_decode_access_token_valid(self):
        """Testa decodificação de token válido"""
        # Criar token válido
        token = create_access_token({"sub": "test@test.com"})
        
        # Decodificar
        payload = decode_access_token(token)
        assert payload["sub"] == "test@test.com"
    
    def test_decode_access_token_invalid(self):
        """Testa decodificação de token inválido"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(invalid_token)
        
        assert exc_info.value.status_code == 401
    
    def test_decode_access_token_expired(self):
        """Testa decodificação de token expirado"""
        # Criar token com expiração no passado
        past_time = datetime.utcnow() - timedelta(minutes=30)
        expired_data = {
            "sub": "test@test.com",
            "exp": past_time
        }
        expired_token = jwt.encode(expired_data, SECRET_KEY, algorithm=ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(expired_token)
        
        assert exc_info.value.status_code == 401
    
    def test_hash_password_different_salts(self):
        """Testa que senhas iguais geram hashes diferentes"""
        password = "test123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2  # Salts diferentes
        assert len(hash1) > 0
        assert len(hash2) > 0
    
    def test_verify_password_correct(self):
        """Testa verificação com senha correta"""
        password = "correct123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_wrong_password(self):
        """Testa verificação com senha incorreta"""
        password = "correct123"
        wrong_password = "wrong123"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Testa obtenção de usuário com token válido"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_user = Mock()
        mock_user.email = "test@test.com"
        mock_user.is_active = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Criar token válido
        token = create_access_token({"sub": "test@test.com"})
        
        # Testar
        user = await get_current_user(token, mock_db)
        assert user == mock_user
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Testa obtenção de usuário com token inválido"""
        mock_db = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid_token", mock_db)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self):
        """Testa obtenção de usuário não encontrado"""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        token = create_access_token({"sub": "nonexistent@test.com"})
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, mock_db)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_inactive(self):
        """Testa obtenção de usuário inativo"""
        mock_db = Mock()
        mock_user = Mock()
        mock_user.email = "test@test.com"
        mock_user.is_active = False
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        token = create_access_token({"sub": "test@test.com"})
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "inativo" in str(exc_info.value.detail)
    
    def test_check_permissions_admin(self):
        """Testa verificação de permissões para admin"""
        mock_user = Mock()
        mock_user.role = "admin"
        
        result = check_permissions(mock_user, ["read", "write"])
        assert result is True
    
    def test_check_permissions_regular_user(self):
        """Testa verificação de permissões para usuário regular"""
        mock_user = Mock()
        mock_user.role = "user"
        
        # Por enquanto sempre retorna True conforme implementação atual
        result = check_permissions(mock_user, ["read"])
        assert result is True
    
    def test_validate_token_claims_valid(self):
        """Testa validação de claims válidos"""
        valid_claims = {"sub": "test@test.com", "exp": 1234567890}
        
        # Não deve levantar exceção
        validate_token_claims(valid_claims)
    
    def test_validate_token_claims_missing_sub(self):
        """Testa validação de claims sem 'sub'"""
        invalid_claims = {"exp": 1234567890}
        
        with pytest.raises(HTTPException) as exc_info:
            validate_token_claims(invalid_claims)
        
        assert exc_info.value.status_code == 401
    
    def test_authentication_error(self):
        """Testa exceção de autenticação"""
        error = AuthenticationError("Erro de autenticação")
        assert str(error) == "Erro de autenticação"
        assert isinstance(error, Exception)
    
    def test_authorization_error(self):
        """Testa exceção de autorização"""
        error = AuthorizationError("Erro de autorização")
        assert str(error) == "Erro de autorização"
        assert isinstance(error, Exception)
    
    def test_token_decode_error_handling(self):
        """Testa tratamento de erro na decodificação"""
        # Token malformado
        malformed_token = "not.a.valid.jwt.token"
        
        with pytest.raises(HTTPException):
            decode_access_token(malformed_token)
    
    def test_token_with_wrong_algorithm(self):
        """Testa token criado com algoritmo diferente"""
        # Criar token com algoritmo diferente
        wrong_token = jwt.encode({"sub": "test@test.com"}, SECRET_KEY, algorithm="HS512")
        
        with pytest.raises(HTTPException):
            decode_access_token(wrong_token)
    
    def test_token_with_wrong_secret(self):
        """Testa token criado com chave secreta diferente"""
        # Criar token com chave diferente
        wrong_token = jwt.encode({"sub": "test@test.com"}, "wrong-secret", algorithm=ALGORITHM)
        
        with pytest.raises(HTTPException):
            decode_access_token(wrong_token)

