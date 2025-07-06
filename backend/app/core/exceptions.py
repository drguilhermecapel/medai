"""
Exceções customizadas do sistema MedAI
Sistema hierárquico de exceções para tratamento de erros específicos
"""
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
import logging


# === LOGGER ===
logger = logging.getLogger(__name__)


# === EXCEÇÕES BASE ===

class MedAIException(Exception):
    """Exceção base do sistema MedAI"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte exceção para dicionário"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }
    
    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"


class MedAIHTTPException(HTTPException):
    """Exceção HTTP customizada do MedAI"""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.error_code = error_code
        self.details = details or {}
        
        detail = {
            "error_code": error_code,
            "message": message,
            "details": self.details
        }
        
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )


# === EXCEÇÕES DE AUTENTICAÇÃO E AUTORIZAÇÃO ===

class AuthenticationError(MedAIException):
    """Erro de autenticação"""
    pass


class AuthorizationError(MedAIException):
    """Erro de autorização"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Credenciais inválidas"""
    
    def __init__(self, message: str = "Credenciais inválidas"):
        super().__init__(message, "INVALID_CREDENTIALS")


class TokenExpiredError(AuthenticationError):
    """Token expirado"""
    
    def __init__(self, message: str = "Token expirado"):
        super().__init__(message, "TOKEN_EXPIRED")


class InvalidTokenError(AuthenticationError):
    """Token inválido"""
    
    def __init__(self, message: str = "Token inválido"):
        super().__init__(message, "INVALID_TOKEN")


class InsufficientPermissionsError(AuthorizationError):
    """Permissões insuficientes"""
    
    def __init__(self, required_permission: str):
        message = f"Permissão necessária: {required_permission}"
        super().__init__(message, "INSUFFICIENT_PERMISSIONS", {
            "required_permission": required_permission
        })


class AccessDeniedError(AuthorizationError):
    """Acesso negado"""
    
    def __init__(self, resource: str = "recurso"):
        message = f"Acesso negado ao {resource}"
        super().__init__(message, "ACCESS_DENIED", {"resource": resource})


# === EXCEÇÕES DE VALIDAÇÃO ===

class ValidationError(MedAIException):
    """Erro de validação"""
    
    def __init__(
        self,
        message: str = "Erro de validação",
        field_errors: Optional[Dict[str, List[str]]] = None
    ):
        self.field_errors = field_errors or {}
        super().__init__(message, "VALIDATION_ERROR", {
            "field_errors": self.field_errors
        })


class InvalidInputError(ValidationError):
    """Entrada inválida"""
    
    def __init__(self, field: str, value: Any, reason: str):
        message = f"Valor inválido para {field}: {reason}"
        field_errors = {field: [reason]}
        super().__init__(message, field_errors)


class RequiredFieldError(ValidationError):
    """Campo obrigatório ausente"""
    
    def __init__(self, field: str):
        message = f"Campo obrigatório ausente: {field}"
        field_errors = {field: ["Campo obrigatório"]}
        super().__init__(message, field_errors)


class InvalidFormatError(ValidationError):
    """Formato inválido"""
    
    def __init__(self, field: str, expected_format: str):
        message = f"Formato inválido para {field}. Esperado: {expected_format}"
        field_errors = {field: [f"Formato esperado: {expected_format}"]}
        super().__init__(message, field_errors)


class WeakPasswordError(ValidationError):
    """Senha muito fraca"""
    
    def __init__(self, requirements: List[str]):
        message = "Senha não atende aos requisitos de segurança"
        field_errors = {"password": requirements}
        super().__init__(message, field_errors)


# === EXCEÇÕES DE RECURSOS ===

class ResourceError(MedAIException):
    """Erro relacionado a recursos"""
    pass


class NotFoundError(ResourceError):
    """Recurso não encontrado"""
    
    def __init__(self, resource_type: str, resource_id: str = None):
        if resource_id:
            message = f"{resource_type} com ID {resource_id} não encontrado"
        else:
            message = f"{resource_type} não encontrado"
        
        super().__init__(message, "RESOURCE_NOT_FOUND", {
            "resource_type": resource_type,
            "resource_id": resource_id
        })


class DuplicateError(ResourceError):
    """Recurso duplicado"""
    
    def __init__(self, resource_type: str, field: str, value: str):
        message = f"{resource_type} com {field} '{value}' já existe"
        super().__init__(message, "DUPLICATE_RESOURCE", {
            "resource_type": resource_type,
            "field": field,
            "value": value
        })


class ResourceConflictError(ResourceError):
    """Conflito de recursos"""
    
    def __init__(self, message: str, conflicting_resource: Optional[str] = None):
        super().__init__(message, "RESOURCE_CONFLICT", {
            "conflicting_resource": conflicting_resource
        })


class ResourceLimitExceededError(ResourceError):
    """Limite de recursos excedido"""
    
    def __init__(self, resource_type: str, limit: int, current: int):
        message = f"Limite de {resource_type} excedido: {current}/{limit}"
        super().__init__(message, "RESOURCE_LIMIT_EXCEEDED", {
            "resource_type": resource_type,
            "limit": limit,
            "current": current
        })


# === EXCEÇÕES DE BANCO DE DADOS ===

class DatabaseError(MedAIException):
    """Erro de banco de dados"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Erro de conexão com banco de dados"""
    
    def __init__(self, message: str = "Erro de conexão com banco de dados"):
        super().__init__(message, "DATABASE_CONNECTION_ERROR")


class DatabaseTransactionError(DatabaseError):
    """Erro de transação no banco de dados"""
    
    def __init__(self, message: str = "Erro de transação no banco de dados"):
        super().__init__(message, "DATABASE_TRANSACTION_ERROR")


class DatabaseIntegrityError(DatabaseError):
    """Erro de integridade do banco de dados"""
    
    def __init__(self, constraint: str, message: str = None):
        message = message or f"Violação de integridade: {constraint}"
        super().__init__(message, "DATABASE_INTEGRITY_ERROR", {
            "constraint": constraint
        })


# === EXCEÇÕES DE IA E MODELOS ===

class AIError(MedAIException):
    """Erro relacionado a IA"""
    pass


class ModelNotFoundError(AIError):
    """Modelo não encontrado"""
    
    def __init__(self, model_name: str):
        message = f"Modelo {model_name} não encontrado"
        super().__init__(message, "MODEL_NOT_FOUND", {
            "model_name": model_name
        })


class ModelLoadError(AIError):
    """Erro ao carregar modelo"""
    
    def __init__(self, model_name: str, reason: str):
        message = f"Erro ao carregar modelo {model_name}: {reason}"
        super().__init__(message, "MODEL_LOAD_ERROR", {
            "model_name": model_name,
            "reason": reason
        })


class InferenceError(AIError):
    """Erro durante inferência"""
    
    def __init__(self, model_name: str, reason: str):
        message = f"Erro na inferência do modelo {model_name}: {reason}"
        super().__init__(message, "INFERENCE_ERROR", {
            "model_name": model_name,
            "reason": reason
        })


class InsufficientDataError(AIError):
    """Dados insuficientes para análise"""
    
    def __init__(self, required_data: str):
        message = f"Dados insuficientes: {required_data}"
        super().__init__(message, "INSUFFICIENT_DATA", {
            "required_data": required_data
        })


class LowConfidenceError(AIError):
    """Confiança baixa na predição"""
    
    def __init__(self, confidence: float, threshold: float):
        message = f"Confiança baixa: {confidence:.2f} (mínimo: {threshold:.2f})"
        super().__init__(message, "LOW_CONFIDENCE", {
            "confidence": confidence,
            "threshold": threshold
        })


# === EXCEÇÕES DE ARQUIVOS ===

class FileError(MedAIException):
    """Erro relacionado a arquivos"""
    pass


class FileNotFoundError(FileError):
    """Arquivo não encontrado"""
    
    def __init__(self, filename: str):
        message = f"Arquivo não encontrado: {filename}"
        super().__init__(message, "FILE_NOT_FOUND", {
            "filename": filename
        })


class InvalidFileTypeError(FileError):
    """Tipo de arquivo inválido"""
    
    def __init__(self, filename: str, allowed_types: List[str]):
        message = f"Tipo de arquivo inválido: {filename}. Tipos permitidos: {', '.join(allowed_types)}"
        super().__init__(message, "INVALID_FILE_TYPE", {
            "filename": filename,
            "allowed_types": allowed_types
        })


class FileSizeExceededError(FileError):
    """Tamanho de arquivo excedido"""
    
    def __init__(self, filename: str, size: int, max_size: int):
        message = f"Arquivo muito grande: {filename} ({size} bytes, máximo: {max_size} bytes)"
        super().__init__(message, "FILE_SIZE_EXCEEDED", {
            "filename": filename,
            "size": size,
            "max_size": max_size
        })


class FileProcessingError(FileError):
    """Erro no processamento de arquivo"""
    
    def __init__(self, filename: str, reason: str):
        message = f"Erro processando arquivo {filename}: {reason}"
        super().__init__(message, "FILE_PROCESSING_ERROR", {
            "filename": filename,
            "reason": reason
        })


# === EXCEÇÕES DE SISTEMA ===

class SystemError(MedAIException):
    """Erro de sistema"""
    pass


class ConfigurationError(SystemError):
    """Erro de configuração"""
    
    def __init__(self, setting: str, reason: str):
        message = f"Erro de configuração em {setting}: {reason}"
        super().__init__(message, "CONFIGURATION_ERROR", {
            "setting": setting,
            "reason": reason
        })


class ServiceUnavailableError(SystemError):
    """Serviço indisponível"""
    
    def __init__(self, service_name: str):
        message = f"Serviço indisponível: {service_name}"
        super().__init__(message, "SERVICE_UNAVAILABLE", {
            "service_name": service_name
        })


class RateLimitExceededError(SystemError):
    """Limite de taxa excedido"""
    
    def __init__(self, limit: int, window: int):
        message = f"Limite de requisições excedido: {limit} por {window} segundos"
        super().__init__(message, "RATE_LIMIT_EXCEEDED", {
            "limit": limit,
            "window": window
        })


class MaintenanceModeError(SystemError):
    """Sistema em manutenção"""
    
    def __init__(self, message: str = "Sistema em manutenção"):
        super().__init__(message, "MAINTENANCE_MODE")


# === EXCEÇÕES DE EXAMES E DIAGNÓSTICOS ===

class ExamError(MedAIException):
    """Erro relacionado a exames"""
    pass


class InvalidExamDataError(ExamError):
    """Dados de exame inválidos"""
    
    def __init__(self, reason: str):
        message = f"Dados de exame inválidos: {reason}"
        super().__init__(message, "INVALID_EXAM_DATA", {
            "reason": reason
        })


class ExamProcessingError(ExamError):
    """Erro no processamento de exame"""
    
    def __init__(self, exam_id: str, reason: str):
        message = f"Erro processando exame {exam_id}: {reason}"
        super().__init__(message, "EXAM_PROCESSING_ERROR", {
            "exam_id": exam_id,
            "reason": reason
        })


class DiagnosticError(MedAIException):
    """Erro relacionado a diagnósticos"""
    pass


class DiagnosticNotReadyError(DiagnosticError):
    """Diagnóstico não está pronto"""
    
    def __init__(self, diagnostic_id: str, current_status: str):
        message = f"Diagnóstico {diagnostic_id} não está pronto (status: {current_status})"
        super().__init__(message, "DIAGNOSTIC_NOT_READY", {
            "diagnostic_id": diagnostic_id,
            "current_status": current_status
        })


# === MAPEAMENTO DE EXCEÇÕES PARA STATUS HTTP ===

EXCEPTION_STATUS_MAP = {
    # Autenticação e Autorização
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    TokenExpiredError: status.HTTP_401_UNAUTHORIZED,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    InsufficientPermissionsError: status.HTTP_403_FORBIDDEN,
    AccessDeniedError: status.HTTP_403_FORBIDDEN,
    
    # Validação
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InvalidInputError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    RequiredFieldError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InvalidFormatError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    WeakPasswordError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    
    # Recursos
    NotFoundError: status.HTTP_404_NOT_FOUND,
    DuplicateError: status.HTTP_409_CONFLICT,
    ResourceConflictError: status.HTTP_409_CONFLICT,
    ResourceLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
    
    # Arquivos
    FileNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidFileTypeError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    FileSizeExceededError: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    FileProcessingError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    
    # Sistema
    ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ServiceUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
    RateLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
    MaintenanceModeError: status.HTTP_503_SERVICE_UNAVAILABLE,
    
    # IA e Modelos
    ModelNotFoundError: status.HTTP_404_NOT_FOUND,
    ModelLoadError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    InferenceError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    InsufficientDataError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    LowConfidenceError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    
    # Banco de Dados
    DatabaseConnectionError: status.HTTP_503_SERVICE_UNAVAILABLE,
    DatabaseTransactionError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    DatabaseIntegrityError: status.HTTP_409_CONFLICT,
    
    # Exames e Diagnósticos
    InvalidExamDataError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ExamProcessingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    DiagnosticNotReadyError: status.HTTP_409_CONFLICT,
}


# === FUNÇÕES UTILITÁRIAS ===

def get_http_status_for_exception(exc: Exception) -> int:
    """
    Retorna status HTTP apropriado para exceção
    
    Args:
        exc: Exceção
        
    Returns:
        Código de status HTTP
    """
    return EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_http_exception(exc: MedAIException) -> MedAIHTTPException:
    """
    Converte exceção MedAI para exceção HTTP
    
    Args:
        exc: Exceção MedAI
        
    Returns:
        Exceção HTTP correspondente
    """
    status_code = get_http_status_for_exception(exc)
    
    return MedAIHTTPException(
        status_code=status_code,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )


def log_exception(exc: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Registra exceção no log
    
    Args:
        exc: Exceção para registrar
        context: Contexto adicional
    """
    context = context or {}
    
    log_data = {
        "exception_type": type(exc).__name__,
        "message": str(exc),
        "context": context
    }
    
    if isinstance(exc, MedAIException):
        log_data.update({
            "error_code": exc.error_code,
            "details": exc.details
        })
    
    # Log diferente baseado no tipo de exceção
    if isinstance(exc, (SystemError, DatabaseError, AIError)):
        logger.error("System exception occurred", extra=log_data)
    elif isinstance(exc, (AuthenticationError, AuthorizationError)):
        logger.warning("Security exception occurred", extra=log_data)
    elif isinstance(exc, ValidationError):
        logger.info("Validation exception occurred", extra=log_data)
    else:
        logger.error("Unhandled exception occurred", extra=log_data)


# === CONSTANTES DE CÓDIGOS DE ERRO ===

ERROR_CODES = {
    # Autenticação
    "INVALID_CREDENTIALS": "AUTH001",
    "TOKEN_EXPIRED": "AUTH002",
    "INVALID_TOKEN": "AUTH003",
    "INSUFFICIENT_PERMISSIONS": "AUTH004",
    "ACCESS_DENIED": "AUTH005",
    
    # Validação
    "VALIDATION_ERROR": "VAL001",
    "INVALID_INPUT": "VAL002",
    "REQUIRED_FIELD": "VAL003",
    "INVALID_FORMAT": "VAL004",
    "WEAK_PASSWORD": "VAL005",
    
    # Recursos
    "RESOURCE_NOT_FOUND": "RES001",
    "DUPLICATE_RESOURCE": "RES002",
    "RESOURCE_CONFLICT": "RES003",
    "RESOURCE_LIMIT_EXCEEDED": "RES004",
    
    # Sistema
    "CONFIGURATION_ERROR": "SYS001",
    "SERVICE_UNAVAILABLE": "SYS002",
    "RATE_LIMIT_EXCEEDED": "SYS003",
    "MAINTENANCE_MODE": "SYS004",
    
    # IA
    "MODEL_NOT_FOUND": "AI001",
    "MODEL_LOAD_ERROR": "AI002",
    "INFERENCE_ERROR": "AI003",
    "INSUFFICIENT_DATA": "AI004",
    "LOW_CONFIDENCE": "AI005",
    
    # Arquivos
    "FILE_NOT_FOUND": "FILE001",
    "INVALID_FILE_TYPE": "FILE002",
    "FILE_SIZE_EXCEEDED": "FILE003",
    "FILE_PROCESSING_ERROR": "FILE004"
}