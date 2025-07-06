"""
Aplicação principal do MedAI - FastAPI
Configuração central da API, middlewares, rotas e inicialização
"""
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import logging
from typing import Callable
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.exceptions import (
    MedAIException, 
    MedAIHTTPException,
    create_http_exception,
    log_exception
)
from app.api.v1.api import api_router
from app.utils.logging_config import setup_logging
from app.utils.health_checker import HealthChecker


# === CONFIGURAÇÃO DE LOGGING ===
setup_logging()
logger = logging.getLogger(__name__)


# === GERENCIAMENTO DO CICLO DE VIDA ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    
    Args:
        app: Instância do FastAPI
    """
    # Startup
    logger.info("🚀 Starting MedAI application...")
    
    try:
        # Inicializar banco de dados
        init_database()
        logger.info("✅ Database initialized")
        
        # Inicializar outros serviços
        # Aqui podem ser adicionados outros serviços como Redis, etc.
        
        logger.info("🎉 MedAI application started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MedAI application...")
    
    try:
        # Fechar conexões do banco
        close_database()
        logger.info("✅ Database connections closed")
        
        # Cleanup de outros recursos
        
        logger.info("👋 MedAI application shut down successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


# === MIDDLEWARES CUSTOMIZADOS ===

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Gerar ID único para a requisição
        request_id = str(uuid.uuid4())
        
        # Adicionar ID da requisição ao contexto
        request.state.request_id = request_id
        
        # Log da requisição de entrada
        start_time = time.time()
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calcular tempo de processamento
            process_time = time.time() - start_time
            
            # Log da resposta
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4)
                }
            )
            
            # Adicionar headers de response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": round(process_time, 4)
                }
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Headers de segurança
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        # Adicionar apenas em produção
        if settings.is_production:
            security_headers.update({
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Content-Security-Policy": "default-src 'self'"
            })
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


# === CRIAÇÃO DA APLICAÇÃO ===

def create_application() -> FastAPI:
    """
    Factory function para criar aplicação FastAPI
    
    Returns:
        Instância configurada do FastAPI
    """
    
    # Metadados da aplicação
    app_kwargs = {
        "title": settings.APP_NAME,
        "description": settings.DESCRIPTION,
        "version": settings.VERSION,
        "debug": settings.DEBUG,
        "lifespan": lifespan
    }
    
    # Configurações específicas por ambiente
    if settings.is_production:
        app_kwargs.update({
            "docs_url": None,  # Desabilitar docs em produção
            "redoc_url": None,
            "openapi_url": None
        })
    else:
        app_kwargs.update({
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json"
        })
    
    app = FastAPI(**app_kwargs)
    
    # Configurar middlewares
    configure_middlewares(app)
    
    # Configurar rotas
    configure_routes(app)
    
    # Configurar handlers de exceção
    configure_exception_handlers(app)
    
    return app


def configure_middlewares(app: FastAPI) -> None:
    """
    Configura middlewares da aplicação
    
    Args:
        app: Instância do FastAPI
    """
    
    # Middleware de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware de compressão
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Middleware de hosts confiáveis (apenas em produção)
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.medai.com", "medai.com"]
        )
    
    # Middlewares customizados
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)


def configure_routes(app: FastAPI) -> None:
    """
    Configura rotas da aplicação
    
    Args:
        app: Instância do FastAPI
    """
    
    # Router principal da API
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Rotas de saúde e monitoramento
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Endpoint básico de health check"""
        return {"status": "healthy", "service": "MedAI"}
    
    @app.get("/health/detailed", tags=["Health"])
    async def detailed_health_check():
        """Health check detalhado com status de componentes"""
        health_checker = HealthChecker()
        return await health_checker.get_detailed_health()
    
    @app.get("/", tags=["Root"])
    async def root():
        """Endpoint raiz da API"""
        return {
            "message": "Bem-vindo ao MedAI API",
            "version": settings.VERSION,
            "docs_url": "/docs" if not settings.is_production else None,
            "health_url": "/health"
        }
    
    @app.get("/info", tags=["Info"])
    async def app_info():
        """Informações da aplicação"""
        return {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "description": settings.DESCRIPTION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        }


def configure_exception_handlers(app: FastAPI) -> None:
    """
    Configura handlers de exceção
    
    Args:
        app: Instância do FastAPI
    """
    
    @app.exception_handler(MedAIException)
    async def medai_exception_handler(request: Request, exc: MedAIException):
        """Handler para exceções customizadas do MedAI"""
        
        # Log da exceção
        log_exception(exc, {
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "url": str(request.url)
        })
        
        # Converter para HTTP exception
        http_exc = create_http_exception(exc)
        
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail,
            headers=http_exc.headers
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handler para erros de validação do Pydantic"""
        
        # Formatar erros de validação
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        log_exception(exc, {
            "request_id": getattr(request.state, "request_id", None),
            "validation_errors": errors
        })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": "Erro de validação nos dados enviados",
                "details": {
                    "field_errors": errors
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handler para exceções HTTP do Starlette"""
        
        log_exception(exc, {
            "request_id": getattr(request.state, "request_id", None),
            "status_code": exc.status_code
        })
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": {}
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handler geral para exceções não tratadas"""
        
        log_exception(exc, {
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "url": str(request.url)
        })
        
        # Em produção, não expor detalhes da exceção
        if settings.is_production:
            detail = "Erro interno do servidor"
        else:
            detail = str(exc)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": detail,
                "details": {}
            }
        )


# === INSTÂNCIA DA APLICAÇÃO ===

# Criar aplicação
app = create_application()


# === EVENTOS DE STARTUP/SHUTDOWN ADICIONAIS ===

@app.on_event("startup")
async def startup_event():
    """Eventos adicionais de startup"""
    logger.info("🔄 Running additional startup tasks...")
    
    # Aqui podem ser adicionadas tarefas de inicialização específicas
    # Como carregamento de modelos ML, configuração de cache, etc.
    
    logger.info("✅ Additional startup tasks completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos adicionais de shutdown"""
    logger.info("🔄 Running additional shutdown tasks...")
    
    # Aqui podem ser adicionadas tarefas de cleanup específicas
    
    logger.info("✅ Additional shutdown tasks completed")


# === CONFIGURAÇÃO PARA DESENVOLVIMENTO ===

if __name__ == "__main__":
    import uvicorn
    
    # Configurações para desenvolvimento
    uvicorn_config = {
        "app": "app.main:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.is_development,
        "log_level": settings.LOG_LEVEL.lower(),
        "access_log": True,
        "use_colors": True
    }
    
    # Workers apenas em produção
    if settings.is_production and settings.WORKERS > 1:
        uvicorn_config["workers"] = settings.WORKERS
    
    logger.info(f"🚀 Starting MedAI server on {settings.HOST}:{settings.PORT}")
    logger.info(f"📝 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🐛 Debug mode: {settings.DEBUG}")
    
    uvicorn.run(**uvicorn_config)