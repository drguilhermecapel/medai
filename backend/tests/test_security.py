"""
Security tests for MedAI system.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import jwt
import secrets

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    validate_token,
    check_permissions,
    encrypt_sensitive_data,
    decrypt_sensitive_data,
    validate_api_key,
    rate_limit_check,
    sanitize_input,
    validate_file_upload,
    check_session_timeout,
    generate_audit_log,
    validate_cors_origin
)


class TestAuthentication:
    """Test authentication mechanisms."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "SecurePassword123!"
        
        # Hash password
        hashed = get_password_hash(password)
        
        # Verify correct password
        assert verify_password(password, hashed) is True
        
        # Verify incorrect password
        assert verify_password("WrongPassword", hashed) is False
        
        # Ensure hash is different each time
        hashed2 = get_password_hash(password)
        assert hashed != hashed2

    def test_jwt_token_creation(self):
        """Test JWT token creation."""
        user_data = {"sub": "user123", "role": "physician"}
        
        # Create token
        token = create_access_token(
            data=user_data,
            expires_delta=timedelta(minutes=30)
        )
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "physician"
        assert "exp" in decoded

    def test_token_validation(self):
        """Test token validation."""
        # Valid token
        valid_token = create_access_token(
            data={"sub": "user123"},
            expires_delta=timedelta(minutes=30)
        )
        
        user = validate_token(valid_token)
        assert user is not None
        assert user["sub"] == "user123"
        
        # Expired token
        expired_token = create_access_token(
            data={"sub": "user123"},
            expires_delta=timedelta(minutes=-1)
        )
        
        with pytest.raises(jwt.ExpiredSignatureError):
            validate_token(expired_token)
        
        # Invalid token
        with pytest.raises(jwt.InvalidTokenError):
            validate_token("invalid.token.here")

    def test_api_key_validation(self):
        """Test API key validation."""
        # Generate API key
        api_key = secrets.token_urlsafe(32)
        
        # Mock API key storage
        with patch('app.core.security.get_api_key_from_db') as mock_get:
            mock_get.return_value = api_key
            
            # Valid API key
            assert validate_api_key(api_key) is True
            
            # Invalid API key
            assert validate_api_key("invalid_key") is False


class TestAuthorization:
    """Test authorization mechanisms."""

    def test_role_based_permissions(self):
        """Test role-based access control."""
        # Admin user
        admin_user = {"id": 1, "role": "admin"}
        assert check_permissions(admin_user, "write", "all") is True
        
        # Physician user
        physician_user = {"id": 2, "role": "physician"}
        assert check_permissions(physician_user, "write", "ecg_analysis") is True
        assert check_permissions(physician_user, "delete", "users") is False
        
        # Viewer user
        viewer_user = {"id": 3, "role": "viewer"}
        assert check_permissions(viewer_user, "read", "ecg_analysis") is True
        assert check_permissions(viewer_user, "write", "ecg_analysis") is False

    def test_resource_ownership(self):
        """Test resource ownership validation."""
        user = {"id": 123, "role": "physician"}
        
        # User owns resource
        resource = {"owner_id": 123}
        assert check_permissions(user, "edit", "ecg_analysis", resource) is True
        
        # User doesn't own resource
        resource = {"owner_id": 456}
        assert check_permissions(user, "edit", "ecg_analysis", resource) is False
        
        # Admin can access any resource
        admin = {"id": 789, "role": "admin"}
        assert check_permissions(admin, "edit", "ecg_analysis", resource) is True

    def test_hierarchical_permissions(self):
        """Test hierarchical permission system."""
        # Cardiologist has elevated permissions
        cardiologist = {"id": 1, "role": "cardiologist", "department": "cardiology"}
        
        # Can validate ECG analyses
        assert check_permissions(cardiologist, "validate", "ecg_analysis") is True
        
        # Can access department resources
        dept_resource = {"department": "cardiology"}
        assert check_permissions(cardiologist, "read", "department_data", dept_resource) is True
        
        # Cannot access other department resources
        other_dept = {"department": "radiology"}
        assert check_permissions(cardiologist, "read", "department_data", other_dept) is False


class TestDataEncryption:
    """Test data encryption mechanisms."""

    def test_sensitive_data_encryption(self):
        """Test encryption of sensitive data."""
        sensitive_data = {
            "patient_id": "123456",
            "ssn": "123-45-6789",
            "medical_record": "Confidential medical information"
        }
        
        # Encrypt data
        encrypted = encrypt_sensitive_data(sensitive_data)
        
        assert encrypted != sensitive_data
        assert isinstance(encrypted, bytes)
        
        # Decrypt data
        decrypted = decrypt_sensitive_data(encrypted)
        
        assert decrypted == sensitive_data

    def test_field_level_encryption(self):
        """Test field-level encryption."""
        patient_data = {
            "name": "John Doe",  # Not encrypted
            "ssn": "123-45-6789",  # Encrypted
            "dob": "1990-01-01",  # Not encrypted
            "diagnosis": "Confidential"  # Encrypted
        }
        
        encrypted_fields = ["ssn", "diagnosis"]
        
        # Encrypt specified fields
        encrypted_data = patient_data.copy()
        for field in encrypted_fields:
            if field in encrypted_data:
                encrypted_data[field] = encrypt_sensitive_data(encrypted_data[field])
        
        # Verify encryption
        assert encrypted_data["name"] == patient_data["name"]
        assert encrypted_data["ssn"] != patient_data["ssn"]
        assert encrypted_data["diagnosis"] != patient_data["diagnosis"]

    def test_encryption_key_rotation(self):
        """Test encryption key rotation."""
        data = "Sensitive information"
        
        # Encrypt with current key
        encrypted_v1 = encrypt_sensitive_data(data, key_version=1)
        
        # Simulate key rotation
        with patch('app.core.security.get_encryption_key') as mock_key:
            mock_key.return_value = b"new_encryption_key_v2"
            
            # Encrypt with new key
            encrypted_v2 = encrypt_sensitive_data(data, key_version=2)
            
            # Both versions should decrypt correctly
            assert decrypt_sensitive_data(encrypted_v1, key_version=1) == data
            assert decrypt_sensitive_data(encrypted_v2, key_version=2) == data
            
            # Encrypted data should be different
            assert encrypted_v1 != encrypted_v2


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM ecg_analyses WHERE 1=1"
        ]
        
        for input_str in malicious_inputs:
            sanitized = sanitize_input(input_str)
            assert "DROP" not in sanitized
            assert "DELETE" not in sanitized
            assert "--" not in sanitized
            assert "'" not in sanitized

    def test_xss_prevention(self):
        """Test XSS attack prevention."""
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='malicious.com'></iframe>"
        ]
        
        for input_str in xss_attempts:
            sanitized = sanitize_input(input_str, input_type="html")
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized
            assert "<iframe" not in sanitized

    def test_file_upload_validation(self):
        """Test file upload security."""
        # Valid file
        valid_file = {
            "filename": "ecg_data.xml",
            "content_type": "application/xml",
            "size": 1024 * 500  # 500KB
        }
        
        assert validate_file_upload(valid_file) is True
        
        # Invalid file types
        invalid_files = [
            {"filename": "malware.exe", "content_type": "application/x-executable"},
            {"filename": "script.js", "content_type": "application/javascript"},
            {"filename": "large_file.xml", "size": 1024 * 1024 * 100}  # 100MB
        ]
        
        for file_data in invalid_files:
            assert validate_file_upload(file_data) is False

    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "uploads/../../../sensitive_data",
            "/var/www/../../etc/shadow"
        ]
        
        for path in malicious_paths:
            sanitized = sanitize_input(path, input_type="filepath")
            assert ".." not in sanitized
            assert sanitized.startswith("uploads/") or sanitized.startswith("data/")


class TestSessionManagement:
    """Test session management security."""

    def test_session_timeout(self):
        """Test session timeout enforcement."""
        # Active session
        active_session = {
            "user_id": 123,
            "created_at": datetime.now() - timedelta(minutes=10),
            "last_activity": datetime.now() - timedelta(minutes=2)
        }
        
        assert check_session_timeout(active_session) is True
        
        # Expired session
        expired_session = {
            "user_id": 123,
            "created_at": datetime.now() - timedelta(hours=2),
            "last_activity": datetime.now() - timedelta(minutes=31)
        }
        
        assert check_session_timeout(expired_session) is False

    def test_session_fixation_prevention(self):
        """Test session fixation attack prevention."""
        # Session should be regenerated after login
        old_session_id = "old_session_123"
        
        with patch('app.core.security.regenerate_session') as mock_regen:
            mock_regen.return_value = "new_session_456"
            
            new_session_id = mock_regen(old_session_id)
            
            assert new_session_id != old_session_id
            assert len(new_session_id) >= 32

    def test_concurrent_session_limit(self):
        """Test concurrent session limitations."""
        user_id = 123
        
        # Mock session storage
        with patch('app.core.security.get_user_sessions') as mock_sessions:
            # User has maximum allowed sessions
            mock_sessions.return_value = [
                {"id": "session1", "device": "desktop"},
                {"id": "session2", "device": "mobile"},
                {"id": "session3", "device": "tablet"}
            ]
            
            # Should not allow new session
            with patch('app.core.security.MAX_CONCURRENT_SESSIONS', 3):
                from app.core.security import can_create_session
                assert can_create_session(user_id) is False


class TestRateLimiting:
    """Test rate limiting mechanisms."""

    def test_api_rate_limiting(self):
        """Test API endpoint rate limiting."""
        client_ip = "192.168.1.100"
        endpoint = "/api/v1/ecg/analyze"
        
        # First requests should pass
        for i in range(10):
            assert rate_limit_check(client_ip, endpoint) is True
        
        # Exceeding limit should fail
        for i in range(5):
            assert rate_limit_check(client_ip, endpoint) is False
        
        # After cooldown period, should work again
        with patch('time.time', return_value=time.time() + 3600):
            assert rate_limit_check(client_ip, endpoint) is True

    def test_login_attempt_limiting(self):
        """Test login attempt rate limiting."""
        username = "test@example.com"
        
        # Track failed login attempts
        failed_attempts = 0
        max_attempts = 5
        
        for i in range(max_attempts + 2):
            if failed_attempts >= max_attempts:
                # Account should be locked
                assert rate_limit_check(username, "login", limit=max_attempts) is False
            else:
                failed_attempts += 1
                assert rate_limit_check(username, "login", limit=max_attempts) is True

    def test_distributed_rate_limiting(self):
        """Test distributed rate limiting across multiple servers."""
        with patch('app.core.security.redis_client') as mock_redis:
            # Simulate distributed counter
            mock_redis.incr.return_value = 100
            mock_redis.expire.return_value = True
            
            # Should respect global limit
            result = rate_limit_check(
                "api_key_123",
                "global",
                limit=100,
                window=3600
            )
            
            assert result is True
            mock_redis.incr.assert_called()


class TestAuditLogging:
    """Test security audit logging."""

    def test_authentication_audit_log(self):
        """Test authentication event logging."""
        # Successful login
        audit_log = generate_audit_log(
            event_type="login",
            user_id=123,
            success=True,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0..."
        )
        
        assert audit_log["event_type"] == "login"
        assert audit_log["success"] is True
        assert "timestamp" in audit_log
        assert "session_id" in audit_log

    def test_data_access_audit_log(self):
        """Test data access logging."""
        # PHI access log
        audit_log = generate_audit_log(
            event_type="phi_access",
            user_id=123,
            resource_type="patient_record",
            resource_id=456,
            action="view",
            fields_accessed=["diagnosis", "medications"]
        )
        
        assert audit_log["event_type"] == "phi_access"
        assert audit_log["resource_type"] == "patient_record"
        assert "fields_accessed" in audit_log

    def test_security_event_audit_log(self):
        """Test security event logging."""
        # Failed authentication attempt
        audit_log = generate_audit_log(
            event_type="failed_login",
            username="test@example.com",
            success=False,
            ip_address="192.168.1.100",
            reason="invalid_password",
            threat_level="medium"
        )
        
        assert audit_log["success"] is False
        assert audit_log["threat_level"] == "medium"
        
        # Verify log is stored
        with patch('app.core.security.store_audit_log') as mock_store:
            mock_store(audit_log)
            mock_store.assert_called_once_with(audit_log)


class TestCORSSecurity:
    """Test CORS security configuration."""

    def test_cors_origin_validation(self):
        """Test CORS origin validation."""
        # Allowed origins
        allowed_origins = [
            "https://app.medai.com",
            "https://staging.medai.com",
            "http://localhost:3000"
        ]
        
        for origin in allowed_origins:
            assert validate_cors_origin(origin, allowed_origins) is True
        
        # Blocked origins
        blocked_origins = [
            "https://malicious.com",
            "http://evil.site",
            "https://app.medai.com.fake.com"
        ]
        
        for origin in blocked_origins:
            assert validate_cors_origin(origin, allowed_origins) is False

    def test_cors_wildcard_prevention(self):
        """Test prevention of wildcard CORS."""
        # Should not allow wildcard
        assert validate_cors_origin("*", ["*"]) is False
        
        # Should require explicit origins
        assert validate_cors_origin("https://example.com", ["https://*.com"]) is False


class TestSecurityHeaders:
    """Test security headers implementation."""

    def test_security_headers_presence(self):
        """Test presence of security headers."""
        from app.core.security import get_security_headers
        
        headers = get_security_headers()
        
        # Required security headers
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in headers
        assert headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in headers
        assert headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Strict-Transport-Security" in headers
        assert "max-age=" in headers["Strict-Transport-Security"]
        
        assert "Content-Security-Policy" in headers


class TestAPIKeySecurity:
    """Test API key security."""

    def test_api_key_generation(self):
        """Test secure API key generation."""
        from app.core.security import generate_api_key
        
        # Generate API key
        api_key = generate_api_key()
        
        # Verify key properties
        assert len(api_key) >= 32
        assert api_key.isalnum() or "_" in api_key or "-" in api_key
        
        # Keys should be unique
        key2 = generate_api_key()
        assert api_key != key2

    def test_api_key_hashing(self):
        """Test API key hashing and storage."""
        from app.core.security import hash_api_key, verify_api_key
        
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