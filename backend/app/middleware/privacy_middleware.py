"""
Privacy Middleware for MedAI
Handles PHI redaction, structured logging with trace correlation
"""
import json
import re
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

logger = logging.getLogger("privacy.audit")


class PrivacyMiddleware(BaseHTTPMiddleware):
    """Middleware for PHI redaction and privacy-aware logging"""
    
    def __init__(self, app):
        super().__init__(app)
        self.phi_patterns = {
            'cpf': r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
            'phone': r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'medical_record': r'[Mm][Rr]\d{6,}',
            'cns': r'\d{15}',  # Cartão Nacional de Saúde
            'rg': r'\d{1,2}\.?\d{3}\.?\d{3}-?[\dxX]'
        }
        
        # Additional PII patterns
        self.pii_patterns = {
            'credit_card': r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
            'bank_account': r'\d{4,6}-?\d{1,2}',
            'brazilian_phone': r'\+55\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}'
        }
        
        self.all_patterns = {**self.phi_patterns, **self.pii_patterns}
    
    async def dispatch(self, request: Request, call_next):
        """Process request with privacy protection"""
        
        # Generate trace ID for correlation
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        
        # Start time for performance tracking
        start_time = datetime.utcnow()
        
        # Extract user context safely
        user_id = getattr(request.state, 'user_id', 'anonymous')
        if hasattr(request, 'user') and request.user:
            user_id = getattr(request.user, 'id', 'authenticated')
        
        # Create privacy-safe log data
        log_data = {
            "trace_id": trace_id,
            "method": request.method,
            "path": self._redact_path(str(request.url.path)),
            "user_id": user_id,
            "timestamp": start_time.isoformat(),
            "client_ip": self._anonymize_ip(request.client.host if request.client else None),
            "user_agent": self._redact_user_agent(request.headers.get("user-agent", ""))
        }
        
        # Log request start
        logger.info("request_start", extra=log_data)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Log request completion
            log_data.update({
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "response_size": len(response.body) if hasattr(response, 'body') else 0
            })
            
            # Add privacy headers
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Privacy-Protected"] = "true"
            
            logger.info("request_end", extra=log_data)
            
            return response
            
        except Exception as e:
            # Log error with privacy protection
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            error_log_data = log_data.copy()
            error_log_data.update({
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": self._redact_error_message(str(e)),
                "duration_ms": round(duration_ms, 2)
            })
            
            logger.error("request_error", extra=error_log_data)
            raise
    
    def _redact_path(self, path: str) -> str:
        """Redact PHI/PII from URL paths"""
        redacted_path = path
        
        for pattern_name, pattern in self.all_patterns.items():
            redacted_path = re.sub(
                pattern, 
                f"[REDACTED_{pattern_name.upper()}]", 
                redacted_path,
                flags=re.IGNORECASE
            )
        
        return redacted_path
    
    def _redact_error_message(self, message: str) -> str:
        """Redact PHI/PII from error messages"""
        redacted_message = message
        
        for pattern_name, pattern in self.all_patterns.items():
            redacted_message = re.sub(
                pattern,
                f"[REDACTED_{pattern_name.upper()}]",
                redacted_message,
                flags=re.IGNORECASE
            )
        
        return redacted_message
    
    def _anonymize_ip(self, ip_address: Optional[str]) -> Optional[str]:
        """Anonymize IP address for privacy"""
        if not ip_address:
            return None
            
        # IPv4 anonymization (zero out last octet)
        if '.' in ip_address and ':' not in ip_address:
            parts = ip_address.split('.')
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
        
        # IPv6 anonymization (zero out last 64 bits)
        elif ':' in ip_address:
            parts = ip_address.split(':')
            if len(parts) >= 4:
                return ':'.join(parts[:4]) + '::0'
        
        return "[REDACTED_IP]"
    
    def _redact_user_agent(self, user_agent: str) -> str:
        """Redact potentially identifying information from user agent"""
        if not user_agent:
            return ""
        
        # Keep only browser and OS info, remove version details that could be identifying
        redacted = re.sub(r'\d+\.\d+\.\d+', 'X.X.X', user_agent)
        
        # Limit length to prevent information leakage
        if len(redacted) > 100:
            redacted = redacted[:97] + "..."
        
        return redacted
    
    def redact_response_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact PHI/PII from response data
        Used for API responses that might contain sensitive data
        """
        if not isinstance(data, dict):
            return data
        
        redacted_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                redacted_data[key] = self._redact_string_value(key, value)
            elif isinstance(value, dict):
                redacted_data[key] = self.redact_response_data(value)
            elif isinstance(value, list):
                redacted_data[key] = [
                    self.redact_response_data(item) if isinstance(item, dict)
                    else self._redact_string_value(key, str(item)) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                redacted_data[key] = value
        
        return redacted_data
    
    def _redact_string_value(self, field_name: str, value: str) -> str:
        """Redact string values based on field name and content"""
        if not isinstance(value, str):
            return value
        
        # Field-specific redaction
        sensitive_fields = {
            'cpf', 'ssn', 'social_security', 'tax_id',
            'phone', 'mobile', 'telephone',
            'email', 'email_address',
            'medical_record', 'patient_id', 'mrn',
            'address', 'street', 'zipcode', 'postal_code'
        }
        
        if any(field in field_name.lower() for field in sensitive_fields):
            return "[REDACTED]"
        
        # Pattern-based redaction
        redacted_value = value
        for pattern_name, pattern in self.all_patterns.items():
            redacted_value = re.sub(
                pattern,
                f"[REDACTED_{pattern_name.upper()}]",
                redacted_value,
                flags=re.IGNORECASE
            )
        
        return redacted_value