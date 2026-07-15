# -*- coding: utf-8 -*-
"""
Aplicação principal do MedAI - FastAPI
Configuração central da API, middlewares, rotas e inicialização
"""
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import create_tables
from app.exceptions import AuthenticationError, AuthorizationError, ValidationError
from app.health import HealthChecker, HealthCheckResult
from app.routers import auth, diagnostics, exams, patients

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    logger.info("🚀 Starting MedAI application...")
    create_tables()
    logger.info("✅ Database initialized")
    yield
    logger.info("👋 MedAI application shut down")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições com ID único e tempo de resposta."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Request failed: %s %s [%s]", request.method, request.url.path, request_id)
            raise
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


def create_application() -> FastAPI:
    """Factory function para criar a aplicação FastAPI."""
    is_production = settings.ENVIRONMENT == "production"

    app = FastAPI(
        title=settings.APP_NAME,
        description="Sistema de prontuário eletrônico com análise automática de exames",
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
    )

    configure_middlewares(app)
    configure_routes(app)
    configure_exception_handlers(app)
    return app


def configure_middlewares(app: FastAPI) -> None:
    """Configura middlewares da aplicação."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)


def configure_routes(app: FastAPI) -> None:
    """Configura rotas da aplicação."""
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(patients.router, prefix=settings.API_V1_STR)
    app.include_router(exams.router, prefix=settings.API_V1_STR)
    app.include_router(diagnostics.router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Root"])
    async def root():
        """Endpoint raiz da API."""
        return {
            "message": "Bem-vindo ao MedAI API",
            "version": settings.VERSION,
            "docs_url": "/docs" if settings.ENVIRONMENT != "production" else None,
            "health_url": "/health",
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Endpoint básico de health check."""
        return {"status": "healthy", "service": "MedAI"}

    @app.get("/health/detailed", tags=["Health"])
    async def detailed_health_check():
        """Health check detalhado com status de componentes."""
        result = HealthChecker().check_health()
        checks = {
            name: {"status": check.status, "message": check.message}
            if isinstance(check, HealthCheckResult) else check
            for name, check in result.get("checks", {}).items()
        }
        return {**result, "checks": checks}

    @app.get("/info", tags=["Info"])
    async def app_info():
        """Informações da aplicação."""
        return {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
        }


def configure_exception_handlers(app: FastAPI) -> None:
    """Configura handlers de exceção."""

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error_code": "AUTHENTICATION_ERROR", "message": str(exc) or "Não autenticado"},
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(request: Request, exc: AuthorizationError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error_code": "AUTHORIZATION_ERROR", "message": str(exc) or "Acesso negado"},
        )

    @app.exception_handler(ValidationError)
    async def app_validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error_code": "VALIDATION_ERROR", "message": str(exc) or "Dados inválidos"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": "Erro de validação nos dados enviados",
                "details": {"field_errors": errors},
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": {},
            },
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        detail = "Erro interno do servidor" if settings.ENVIRONMENT == "production" else str(exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error_code": "INTERNAL_SERVER_ERROR", "message": detail, "details": {}},
        )


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
