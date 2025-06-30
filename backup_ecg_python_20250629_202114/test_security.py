"""
Core security module for MedAI system.
Implements authentication, authorization, encryption, and security controls.
"""

import hashlib
import hmac
import secrets
import time
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from functools import wraps

import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import redis

# Configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENCRYPTION_KEY = b"your-32-byte-encryption-key-here"  # In production, use secure key management
MAX_CONCURRENT_SESSIONS = 3

# Initialize Redis for distributed operations (mock for now)
redis_client = None  # In production, initialize with: redis.Redis(host='localhost', port=6379, db=0)

# Rate limiting storage (in-memory for simplicity, use Redis in production)
rate_limit_storage = {}

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validate_token(token: str) -> Dict[str, Any]:
    """
    Validate and decode a JWT token.
    
    Args:
        token: JWT token to validate
        
    Returns:
        Decoded token data
        
    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.JWTError:
        raise jwt.InvalidTokenError("Invalid token")

def check_permissions(
    user: Dict[str, Any],
    action: str,
    resource: str,
    resource_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Check if user has permission to perform action on resource.
    
    Args:
        user: User object with role and id
        action: Action to perform (read, write, delete, etc.)
        resource: Resource type
        resource_data: Optional resource data for ownership checks
        
    Returns:
        True if permitted, False otherwise
    """
    role = user.get("role", "viewer")
    user_id = user.get("id")
    
    # Admin has all permissions
    if role == "admin":
        return True
    
    # Role-based permissions
    permissions = {
        "physician": {
            "read": ["ecg_analysis", "patient_data", "department_data"],
            "write": ["ecg_analysis", "patient_data"],
            "edit": ["ecg_analysis"],  # Only own resources
            "delete": []
        },
        "cardiologist": {
            "read": ["ecg_analysis", "patient_data", "department_data"],
            "write": ["ecg_analysis", "patient_data"],
            "edit": ["ecg_analysis"],
            "validate": ["ecg_analysis"],
            "delete": []
        },
        "viewer": {
            "read": ["ecg_analysis"],
            "write": [],
            "delete": []
        }
    }
    
    # Check basic role permissions
    role_perms = permissions.get(role, {})
    allowed_resources = role_perms.get(action, [])
    
    if resource == "all" or resource in allowed_resources:
        # Check ownership for edit actions
        if action == "edit" and resource_data:
            return resource_data.get("owner_id") == user_id
        
        # Check department access
        if resource == "department_data" and resource_data:
            return resource_data.get("department") == user.get("department")
        
        return True
    
    return False

def encrypt_sensitive_data(data: Union[str, dict], key_version: int = 1) -> bytes:
    """
    Encrypt sensitive data using Fernet encryption.
    
    Args:
        data: Data to encrypt
        key_version: Encryption key version
        
    Returns:
        Encrypted data
    """
    # Get encryption key based on version
    encryption_key = get_encryption_key(key_version)
    
    # Convert data to bytes
    if isinstance(data, dict):
        data_bytes = str(data).encode('utf-8')
    else:
        data_bytes = str(data).encode('utf-8')
    
    # Encrypt
    f = Fernet(encryption_key)
    encrypted = f.encrypt(data_bytes)
    
    return encrypted

def decrypt_sensitive_data(encrypted_data: bytes, key_version: int = 1) -> Union[str, dict]:
    """
    Decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted data
        key_version: Encryption key version
        
    Returns:
        Decrypted data
    """
    # Get encryption key based on version
    encryption_key = get_encryption_key(key_version)
    
    # Decrypt
    f = Fernet(encryption_key)
    decrypted = f.decrypt(encrypted_data)
    
    # Try to eval as dict, otherwise return string
    decrypted_str = decrypted.decode('utf-8')
    try:
        return eval(decrypted_str)
    except:
        return decrypted_str

def get_encryption_key(version: int = 1) -> bytes:
    """
    Get encryption key by version.
    
    Args:
        version: Key version
        
    Returns:
        Encryption key
    """
    # In production, retrieve from secure key management service
    if version == 1:
        return ENCRYPTION_KEY
    elif version == 2:
        return b"new_encryption_key_v2_32bytes!!!"
    else:
        return ENCRYPTION_KEY

def validate_api_key(api_key: str) -> bool:
    """
    Validate an API key.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    # In production, check against database
    stored_key = get_api_key_from_db(api_key)
    return stored_key == api_key

def get_api_key_from_db(api_key: str) -> Optional[str]:
    """
    Mock function to get API key from database.
    
    Args:
        api_key: API key to look up
        
    Returns:
        Stored API key or None
    """
    # In production, query database
    return api_key  # Mock implementation

def rate_limit_check(
    identifier: str,
    endpoint: str,
    limit: int = 100,
    window: int = 3600
) -> bool:
    """
    Check rate limit for identifier/endpoint combination.
    
    Args:
        identifier: Client IP, username, or API key
        endpoint: API endpoint or action
        limit: Maximum requests allowed
        window: Time window in seconds
        
    Returns:
        True if within limit, False if exceeded
    """
    key = f"{identifier}:{endpoint}"
    current_time = time.time()
    
    # Clean old entries
    if key in rate_limit_storage:
        rate_limit_storage[key] = [
            t for t in rate_limit_storage[key]
            if current_time - t < window
        ]
    
    # Check limit
    if key not in rate_limit_storage:
        rate_limit_storage[key] = []
    
    if len(rate_limit_storage[key]) >= limit:
        return False
    
    # Add current request
    rate_limit_storage[key].append(current_time)
    return True

def sanitize_input(input_str: str, input_type: str = "text") -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        input_str: Input string to sanitize
        input_type: Type of input (text, html, filepath)
        
    Returns:
        Sanitized string
    """
    if input_type == "text":
        # Remove SQL injection attempts
        dangerous_sql = ["DROP", "DELETE", "--", "'", ";"]
        sanitized = input_str
        for pattern in dangerous_sql:
            sanitized = sanitized.replace(pattern, "")
        return sanitized
    
    elif input_type == "html":
        # Remove XSS attempts
        dangerous_html = [
            "<script>", "</script>", "javascript:",
            "onerror=", "<iframe", "onclick="
        ]
        sanitized = input_str
        for pattern in dangerous_html:
            sanitized = sanitized.replace(pattern, "")
        return sanitized
    
    elif input_type == "filepath":
        # Remove path traversal attempts
        sanitized = input_str.replace("..", "")
        sanitized = sanitized.replace("\\", "/")
        # Ensure path starts with safe directory
        if not sanitized.startswith(("uploads/", "data/")):
            sanitized = "uploads/" + sanitized.split("/")[-1]
        return sanitized
    
    return input_str

def validate_file_upload(file_data: Dict[str, Any]) -> bool:
    """
    Validate file upload for security.
    
    Args:
        file_data: File metadata
        
    Returns:
        True if valid, False otherwise
    """
    # Check file type
    allowed_types = [
        "application/xml", "text/xml", "application/json",
        "text/csv", "application/pdf"
    ]
    
    if file_data.get("content_type") not in allowed_types:
        return False
    
    # Check file extension
    filename = file_data.get("filename", "")
    allowed_extensions = [".xml", ".json", ".csv", ".pdf", ".txt"]
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return False
    
    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024
    if file_data.get("size", 0) > max_size:
        return False
    
    return True

def check_session_timeout(session: Dict[str, Any], timeout_minutes: int = 30) -> bool:
    """
    Check if session has timed out.
    
    Args:
        session: Session data
        timeout_minutes: Timeout period in minutes
        
    Returns:
        True if session is valid, False if timed out
    """
    last_activity = session.get("last_activity")
    if not last_activity:
        return False
    
    timeout_delta = timedelta(minutes=timeout_minutes)
    return datetime.now() - last_activity < timeout_delta

def regenerate_session(old_session_id: str) -> str:
    """
    Regenerate session ID to prevent fixation attacks.
    
    Args:
        old_session_id: Current session ID
        
    Returns:
        New session ID
    """
    return secrets.token_urlsafe(32)

def get_user_sessions(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all active sessions for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List of active sessions
    """
    # Mock implementation
    return []

def can_create_session(user_id: int) -> bool:
    """
    Check if user can create a new session.
    
    Args:
        user_id: User ID
        
    Returns:
        True if allowed, False otherwise
    """
    sessions = get_user_sessions(user_id)
    return len(sessions) < MAX_CONCURRENT_SESSIONS

def generate_audit_log(
    event_type: str,
    success: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate audit log entry.
    
    Args:
        event_type: Type of event
        success: Whether event was successful
        **kwargs: Additional event data
        
    Returns:
        Audit log entry
    """
    audit_log = {
        "event_type": event_type,
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": secrets.token_urlsafe(16)
    }
    audit_log.update(kwargs)
    return audit_log

def store_audit_log(audit_log: Dict[str, Any]) -> None:
    """
    Store audit log entry.
    
    Args:
        audit_log: Audit log data
    """
    # In production, store in database or SIEM
    pass

def validate_cors_origin(origin: str, allowed_origins: List[str]) -> bool:
    """
    Validate CORS origin.
    
    Args:
        origin: Request origin
        allowed_origins: List of allowed origins
        
    Returns:
        True if allowed, False otherwise
    """
    # Prevent wildcard
    if origin == "*" or "*" in allowed_origins:
        return False
    
    # Check exact match
    return origin in allowed_origins

def get_security_headers() -> Dict[str, str]:
    """
    Get security headers for HTTP responses.
    
    Returns:
        Dictionary of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }

def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        Generated API key
    """
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage.
    
    Args:
        api_key: API key to hash
        
    Returns:
        Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """
    Verify an API key against stored hash.
    
    Args:
        api_key: API key to verify
        stored_hash: Stored hash
        
    Returns:
        True if valid, False otherwise
    """
    return hash_api_key(api_key) == stored_hash

def generate_digital_signature(data: str, private_key: str) -> str:
    """
    Generate digital signature for data.
    
    Args:
        data: Data to sign
        private_key: Private key for signing
        
    Returns:
        Digital signature
    """
    # Create HMAC signature
    signature = hmac.new(
        private_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_digital_signature(
    data: str,
    signature: str,
    public_key: str,
    timestamp: datetime
) -> bool:
    """
    Verify digital signature.
    
    Args:
        data: Original data
        signature: Signature to verify
        public_key: Public key for verification
        timestamp: Timestamp of signature
        
    Returns:
        True if valid, False otherwise
    """
    # For HMAC, public and private keys are the same
    expected_signature = generate_digital_signature(data, public_key)
    return signature == expected_signature

def generate_file_hash(file_content: bytes) -> str:
    """
    Generate hash of file content.
    
    Args:
        file_content: File content
        
    Returns:
        File hash
    """
    return hashlib.sha256(file_content).hexdigest()