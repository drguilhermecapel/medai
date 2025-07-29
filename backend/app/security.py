"""
Security middleware and utilities for medical data protection
Enhanced security features for HIPAA/LGPD compliance
"""
import os
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from functools import wraps
import secrets
import base64

from app.core.config import settings

# Configure audit logger
audit_logger = logging.getLogger("medai.audit")
audit_logger.setLevel(logging.INFO)

class PHIEncryption:
    """AES-256 encryption for Protected Health Information"""
    
    def __init__(self, password: Optional[str] = None):
        """Initialize encryption with password-derived key"""
        if password is None:
            password = settings.SECRET_KEY
        
        salt = b'medai_phi_salt_v1'  # In production, use unique salt per deployment
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)
    
    def encrypt_phi(self, data: str) -> str:
        """Encrypt PHI data"""
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_phi(self, encrypted_data: str) -> str:
        """Decrypt PHI data"""
        if not encrypted_data:
            return ""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            # Log but don't expose decryption errors
            audit_logger.error("PHI decryption failed - possible data corruption")
            return ""
    
    def create_searchable_hash(self, data: str) -> str:
        """Create searchable hash for encrypted data"""
        if not data:
            return ""
        return hashlib.sha256(f"{data.lower()}{settings.SECRET_KEY}".encode()).hexdigest()

# Global PHI encryption instance
phi_encryption = PHIEncryption()

def audit_log(action: str, resource_type: str = "unknown"):
    """Decorator for HIPAA audit logging"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('current_user_id', 'unknown')
            resource_id = kwargs.get('resource_id', 'unknown')
            
            # Log the action
            audit_logger.info(
                f"AUDIT: action={action} user_id={user_id} resource_type={resource_type} "
                f"resource_id={resource_id} timestamp={datetime.utcnow().isoformat()}"
            )
            
            try:
                result = await func(*args, **kwargs)
                audit_logger.info(f"AUDIT_SUCCESS: action={action} user_id={user_id}")
                return result
            except Exception as e:
                audit_logger.error(f"AUDIT_FAILED: action={action} user_id={user_id} error={str(e)}")
                raise
        return wrapper
    return decorator

class SecurityHeaders:
    """Security headers for medical application"""
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
        }

class AuditLogger:
    """Enhanced audit logging for medical data access"""
    
    @staticmethod
    def log_access(user_id: str, action: str, resource_type: str, resource_id: str, 
                   ip_address: str = "unknown", user_agent: str = "unknown"):
        """Log data access for audit compliance"""
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "session_id": secrets.token_hex(16)
        }
        
        audit_logger.info(f"DATA_ACCESS: {audit_data}")
    
    @staticmethod
    def log_phi_access(user_id: str, patient_id: str, fields_accessed: list, 
                       ip_address: str = "unknown"):
        """Log PHI access specifically"""
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": "PHI_ACCESS",
            "patient_id": patient_id,
            "fields_accessed": fields_accessed,
            "ip_address": ip_address,
            "severity": "HIGH"
        }
        
        audit_logger.warning(f"PHI_ACCESS: {audit_data}")

# Global instances
security_headers = SecurityHeaders()
audit_log_manager = AuditLogger()