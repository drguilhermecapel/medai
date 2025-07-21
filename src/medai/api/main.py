"""
FastAPI application main entry point for MEDAI.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from medai.database import get_session, init_database, close_database
from medai.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan management.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    await init_database()
    yield
    # Shutdown
    await close_database()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


# Create application instance
app = create_app()


@app.get("/healthz", tags=["Health"])
async def health_check(
    session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    """
    Health check endpoint.
    
    Args:
        session: Database session dependency
        
    Returns:
        dict: Health status
    """
    try:
        # Test database connection
        await session.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "database": db_status,
    }


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """
    Root endpoint.
    
    Returns:
        dict: Welcome message and basic info
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/healthz",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "medai.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )