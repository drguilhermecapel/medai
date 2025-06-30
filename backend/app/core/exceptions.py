"""
Exceções customizadas do sistema MedAI
"""
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, status


class MedAIException(HTTPException):
    """Exceção base do sistema MedAI"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationError(MedAIException):
    """Erro de autenticação"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(MedAIException):
    """Erro de autorização"""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ValidationError(MedAIException):
    """Erro de validação de dados"""
    
    def __init__(self, errors: Union[str, Dict[str, Any]]):
        if isinstance(errors, str):
            detail = errors
        else:
            detail = {"validation_errors": errors}
            
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.errors = errors


class NotFoundError(MedAIException):
    """Erro de recurso não encontrado"""
    
    def __init__(self, resource: str, identifier: Any):
        detail = f"{resource} with identifier {identifier} not found"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND
        )


class DuplicateError(MedAIException):
    """Erro de recurso duplicado"""
    
    def __init__(self, field: str, value: Any):
        detail = f"{field} '{value}' already exists"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT
        )


class BusinessLogicError(MedAIException):
    """Erro de lógica de negócio"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ExternalServiceError(MedAIException):
    """Erro de serviço externo"""
    
    def __init__(self, service: str, detail: str):
        super().__init__(
            detail=f"Error communicating with {service}: {detail}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class RateLimitError(MedAIException):
    """Erro de limite de taxa"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": "60"}
        )


class FileUploadError(MedAIException):
    """Erro de upload de arquivo"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=f"File upload error: {detail}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class MLModelError(MedAIException):
    """Erro relacionado a modelo de ML"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=f"ML Model error: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DatabaseError(MedAIException):
    """Erro de banco de dados"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=f"Database error: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ConfigurationError(MedAIException):
    """Erro de configuração"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=f"Configuration error: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TokenError(MedAIException):
    """Erro relacionado a tokens"""
    
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class PermissionError(MedAIException):
    """Erro de permissão"""
    
    def __init__(self, action: str, resource: str):
        detail = f"Permission denied to {action} {resource}"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN
        )


class LGPDComplianceError(MedAIException):
    """Erro de compliance com LGPD"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=f"LGPD compliance error: {detail}",
            status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
        )