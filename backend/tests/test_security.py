"""
Comprehensive tests for security module - Critical component requiring 100% coverage.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
    generate_password_reset_token,
    verify_password_reset_token,
    generate_api_key,
    hash_api_key,
    verify_api_key,
    generate_digital_signature,
    verify_digital_signature,
    generate_file_hash,
    constant_time_compare,
    RateLimiter,
    rate_limiter,
    get_current_user
)
from app.core.exceptions import AuthenticationException


class TestTokenOperations:
    """Test token creation and verification."""

    def test_create_access_token_default_expiry(self):
        """Test access token creation with default expiry."""
        token = create_access_token("test_user")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """Test access token creation with custom expiry."""
        expires_delta = timedelta(minutes=30)
        token = create_access_token("test_user", expires_delta=expires_delta)
        assert token is not None
        assert isinstance(token, str)

    def test_create_access_token_with_additional_claims(self):
        """Test access token creation with additional claims."""
        additional_claims = {"role": "admin", "permissions": ["read", "write"]}
        token = create_access_token("test_user", additional_claims=additional_claims)
        
        # Verify token contains additional claims
        payload = verify_token(token)
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        token = create_refresh_token("test_user")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_access_token(self):
        """Test verification of valid access token."""
        token = create_access_token("test_user")
        payload = verify_token(token, "access")
        
        assert payload["sub"] == "test_user"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_verify_valid_refresh_token(self):
        """Test verification of valid refresh token."""
        token = create_refresh_token("test_user")
        payload = verify_token(token, "refresh")
        
        assert payload["sub"] == "test_user"
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_verify_token_wrong_type(self):
        """Test verification fails with wrong token type."""
        access_token = create_access_token("test_user")
        
        with pytest.raises(AuthenticationException, match="Invalid token type"):
            verify_token(access_token, "refresh")

    def test_verify_invalid_token(self):
        """Test verification fails with invalid token."""
        with pytest.raises(AuthenticationException, match="Invalid token"):
            verify_token("invalid_token", "access")

    def test_verify_expired_token(self):
        """Test verification fails with expired token."""
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token("test_user", expires_delta=expires_delta)
        
        with pytest.raises(AuthenticationException, match="Invalid token"):
            verify_token(token, "access")


class TestPasswordOperations:
    """Test password hashing and verification."""

    def test_get_password_hash(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_password_hash_uniqueness(self):
        """Test that same password generates different hashes."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestPasswordResetTokens:
    """Test password reset token operations."""

    def test_generate_password_reset_token(self):
        """Test password reset token generation."""
        email = "test@example.com"
        token = generate_password_reset_token(email)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_password_reset_token(self):
        """Test verification of valid password reset token."""
        email = "test@example.com"
        token = generate_password_reset_token(email)
        
        verified_email = verify_password_reset_token(token)
        assert verified_email == email

    def test_verify_invalid_password_reset_token(self):
        """Test verification of invalid password reset token."""
        result = verify_password_reset_token("invalid_token")
        assert result is None

    def test_verify_wrong_type_password_reset_token(self):
        """Test verification fails for wrong token type."""
        # Create access token instead of password reset token
        access_token = create_access_token("test@example.com")
        result = verify_password_reset_token(access_token)
        assert result is None


class TestAPIKeyOperations:
    """Test API key operations."""

    def test_generate_api_key(self):
        """Test API key generation."""
        api_key = generate_api_key()
        
        assert api_key is not None
        assert isinstance(api_key, str)
        assert len(api_key) > 0

    def test_api_key_uniqueness(self):
        """Test that generated API keys are unique."""
        key1 = generate_api_key()
        key2 = generate_api_key()
        
        assert key1 != key2

    def test_hash_api_key(self):
        """Test API key hashing."""
        api_key = generate_api_key()
        hashed = hash_api_key(api_key)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != api_key
        assert len(hashed) == 64  # SHA256 hex digest length

    def test_verify_correct_api_key(self):
        """Test API key verification with correct key."""
        api_key = generate_api_key()
        hashed = hash_api_key(api_key)
        
        assert verify_api_key(api_key, hashed) is True

    def test_verify_incorrect_api_key(self):
        """Test API key verification with incorrect key."""
        api_key = generate_api_key()
        wrong_key = generate_api_key()
        hashed = hash_api_key(api_key)
        
        assert verify_api_key(wrong_key, hashed) is False


class TestDigitalSignature:
    """Test digital signature operations."""

    def test_generate_digital_signature(self):
        """Test digital signature generation."""
        data = "test_medical_data"
        private_key = "test_private_key"
        
        signature = generate_digital_signature(data, private_key)
        
        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex digest length

    def test_verify_valid_digital_signature(self):
        """Test verification of valid digital signature."""
        data = "test_medical_data"
        private_key = "test_private_key"
        public_key = "test_private_key"  # Same for this test
        timestamp = datetime.utcnow()
        
        # Generate signature with current timestamp
        with patch('app.core.security.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = timestamp
            signature = generate_digital_signature(data, private_key)
        
        # Verify signature
        result = verify_digital_signature(data, signature, public_key, timestamp)
        assert result is True

    def test_verify_invalid_digital_signature(self):
        """Test verification of invalid digital signature."""
        data = "test_medical_data"
        wrong_signature = "invalid_signature"
        public_key = "test_public_key"
        timestamp = datetime.utcnow()
        
        result = verify_digital_signature(data, wrong_signature, public_key, timestamp)
        assert result is False


class TestFileOperations:
    """Test file-related security operations."""

    def test_generate_file_hash(self):
        """Test file hash generation."""
        file_content = b"test file content"
        file_hash = generate_file_hash(file_content)
        
        assert file_hash is not None
        assert isinstance(file_hash, str)
        assert len(file_hash) == 64  # SHA256 hex digest length

    def test_file_hash_consistency(self):
        """Test that same content generates same hash."""
        file_content = b"test file content"
        hash1 = generate_file_hash(file_content)
        hash2 = generate_file_hash(file_content)
        
        assert hash1 == hash2

    def test_file_hash_uniqueness(self):
        """Test that different content generates different hashes."""
        content1 = b"test file content 1"
        content2 = b"test file content 2"
        
        hash1 = generate_file_hash(content1)
        hash2 = generate_file_hash(content2)
        
        assert hash1 != hash2


class TestConstantTimeCompare:
    """Test constant time comparison function."""

    def test_constant_time_compare_equal_strings(self):
        """Test constant time comparison with equal strings."""
        str1 = "test_string"
        str2 = "test_string"
        
        assert constant_time_compare(str1, str2) is True

    def test_constant_time_compare_different_strings(self):
        """Test constant time comparison with different strings."""
        str1 = "test_string_1"
        str2 = "test_string_2"
        
        assert constant_time_compare(str1, str2) is False

    def test_constant_time_compare_different_lengths(self):
        """Test constant time comparison with different length strings."""
        str1 = "short"
        str2 = "much_longer_string"
        
        assert constant_time_compare(str1, str2) is False


class TestRateLimiter:
    """Test rate limiter functionality."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter()
        assert limiter.requests == {}

    def test_rate_limiter_allows_initial_requests(self):
        """Test rate limiter allows initial requests."""
        limiter = RateLimiter()
        key = "test_user"
        
        assert limiter.check_rate_limit(key, limit=10, window=60) is True

    def test_rate_limiter_blocks_excess_requests(self):
        """Test rate limiter blocks requests exceeding limit."""
        limiter = RateLimiter()
        key = "test_user"
        limit = 3
        
        # Make requests up to limit
        for _ in range(limit):
            assert limiter.check_rate_limit(key, limit=limit, window=60) is True
        
        # Next request should be blocked
        assert limiter.check_rate_limit(key, limit=limit, window=60) is False

    def test_rate_limiter_is_allowed_alias(self):
        """Test is_allowed method works as alias."""
        limiter = RateLimiter()
        key = "test_user"
        
        assert limiter.is_allowed(key, limit=10, window=60) is True

    def test_rate_limiter_get_remaining_requests(self):
        """Test getting remaining requests."""
        limiter = RateLimiter()
        key = "test_user"
        limit = 5
        
        # Initially should have full limit
        assert limiter.get_remaining_requests(key, limit=limit, window=60) == limit
        
        # After one request, should have limit-1
        limiter.check_rate_limit(key, limit=limit, window=60)
        assert limiter.get_remaining_requests(key, limit=limit, window=60) == limit - 1

    def test_rate_limiter_window_expiry(self):
        """Test rate limiter window expiry."""
        limiter = RateLimiter()
        key = "test_user"
        
        # Mock time to test window expiry
        with patch('app.core.security.datetime') as mock_datetime:
            # Set initial time
            initial_time = datetime.utcnow()
            mock_datetime.utcnow.return_value = initial_time
            
            # Make request
            assert limiter.check_rate_limit(key, limit=1, window=1) is True
            
            # Should be blocked immediately
            assert limiter.check_rate_limit(key, limit=1, window=1) is False
            
            # Move time forward past window
            future_time = initial_time + timedelta(seconds=2)
            mock_datetime.utcnow.return_value = future_time
            
            # Should be allowed again
            assert limiter.check_rate_limit(key, limit=1, window=1) is True

    def test_global_rate_limiter_instance(self):
        """Test global rate limiter instance."""
        assert rate_limiter is not None
        assert isinstance(rate_limiter, RateLimiter)


class TestGetCurrentUser:
    """Test get_current_user function."""

    def test_get_current_user_without_token(self):
        """Test get_current_user without token returns default user."""
        user = get_current_user()
        
        assert user["id"] == "test_user"
        assert user["email"] == "test@example.com"
        assert user["role"] == "physician"
        assert user["is_active"] is True

    def test_get_current_user_with_valid_token(self):
        """Test get_current_user with valid token."""
        token = create_access_token("user_123")
        user = get_current_user(token)
        
        assert user["id"] == "user_123"
        assert user["email"] == "test@example.com"
        assert user["role"] == "physician"
        assert user["is_active"] is True

    def test_get_current_user_with_invalid_token(self):
        """Test get_current_user with invalid token returns default."""
        user = get_current_user("invalid_token")
        
        assert user["id"] == "test_user"
        assert user["email"] == "test@example.com"
        assert user["role"] == "physician"
        assert user["is_active"] is True

    def test_get_current_user_with_none_token(self):
        """Test get_current_user with None token."""
        user = get_current_user(None)
        
        assert user["id"] == "test_user"
        assert user["email"] == "test@example.com"
        assert user["role"] == "physician"
        assert user["is_active"] is True

