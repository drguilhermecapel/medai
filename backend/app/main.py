"""
FastAPI application with enhanced security
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware import setup_security_middleware

# Criar app
app = FastAPI(
    title="MedAI",
    version="1.0.0",
    description="Sistema de Análise Médica com IA - Segurança Aprimorada",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup security middleware first
setup_security_middleware(app)

# CORS with restricted origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "MedAI API", "status": "running", "security": "enabled"}

@app.get("/health")
async def health_check():
    """Health check with security status"""
    return {
        "status": "healthy",
        "security_features": [
            "PHI_encryption",
            "audit_logging", 
            "rate_limiting",
            "security_headers"
        ]
    }

# Tentar importar rotas, mas nao falhar se nao existirem
try:
    from app.api.endpoints import api_router
    app.include_router(api_router, prefix="/api/v1")
except ImportError:
    pass  # Rotas nao disponiveis ainda
