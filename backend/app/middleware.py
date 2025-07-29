"""
Security middleware for MedAI application
Implements rate limiting, security headers, and audit middleware
"""
import time
import logging
from typing import Dict, Any
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.security import security_headers, AuditLogger

# Configure logger
logger = logging.getLogger("medai.middleware")

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for API protection"""
    
    def __init__(self, app, calls: int = 60, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(deque)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old entries
        client_calls = self.clients[client_ip]
        while client_calls and client_calls[0] <= now - self.period:
            client_calls.popleft()
        
        # Check rate limit
        if len(client_calls) >= self.calls:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Add current request
        client_calls.append(now)
        
        # Process request
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        headers = security_headers.get_headers()
        for name, value in headers.items():
            response.headers[name] = value
        
        return response


class AuditMiddleware(BaseHTTPMiddleware):
    """Audit middleware for logging API access"""
    
    def __init__(self, app, log_all_requests: bool = False):
        super().__init__(app)
        self.log_all_requests = log_all_requests
        self.sensitive_paths = {
            "/api/v1/patients",
            "/api/v1/appointments", 
            "/api/v1/exams",
            "/api/v1/prescriptions"
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "unknown")
        path = request.url.path
        method = request.method
        
        # Extract user from token if available
        user_id = "anonymous"
        auth_header = request.headers.get("authorization")
        if auth_header:
            try:
                from app.core.security import TokenManager
                token = auth_header.replace("Bearer ", "")
                payload = TokenManager.decode_token(token)
                user_id = payload.get("sub", "unknown")
            except Exception:
                pass
        
        # Log sensitive path access
        if any(sensitive_path in path for sensitive_path in self.sensitive_paths):
            AuditLogger.log_access(
                user_id=user_id,
                action=f"{method}:{path}",
                resource_type="api_endpoint",
                resource_id=path,
                ip_address=client_ip,
                user_agent=user_agent
            )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log slow requests
            if process_time > 2.0:  # Slower than 2 seconds
                logger.warning(
                    f"Slow request: {method} {path} took {process_time:.2f}s "
                    f"from {client_ip}"
                )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log failed requests
            logger.error(
                f"Request failed: {method} {path} error={str(e)} "
                f"time={process_time:.2f}s from {client_ip}"
            )
            raise


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Basic request validation and security checks"""
    
    def __init__(self, app, max_content_length: int = 50 * 1024 * 1024):  # 50MB
        super().__init__(app)
        self.max_content_length = max_content_length
        self.blocked_user_agents = [
            "sqlmap",
            "nikto", 
            "nmap",
            "masscan",
            "curl/7.0"  # Block old curl versions
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_content_length:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request too large"}
            )
        
        # Check user agent
        user_agent = request.headers.get("user-agent", "").lower()
        if any(blocked in user_agent for blocked in self.blocked_user_agents):
            logger.warning(f"Blocked suspicious user agent: {user_agent}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied"}
            )
        
        # Check for common attack patterns in URL
        path = request.url.path.lower()
        attack_patterns = [
            "../",
            "..\\",
            "union select",
            "<script",
            "javascript:",
            "eval(",
            "base64_decode"
        ]
        
        if any(pattern in path for pattern in attack_patterns):
            logger.warning(f"Blocked suspicious path: {path}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request"}
            )
        
        return await call_next(request)


def setup_security_middleware(app):
    """Setup all security middleware"""
    
    # Add middleware in reverse order (last added is executed first)
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(AuditMiddleware, log_all_requests=False)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, calls=60, period=60)  # 60 calls per minute
    
    logger.info("Security middleware configured successfully")