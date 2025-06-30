"""
FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Criar app
app = FastAPI(
    title="CardioAI Pro",
    version="1.0.0",
    description="Sistema de analise de ECG com IA"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "CardioAI Pro API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}

# Tentar importar rotas, mas nao falhar se nao existirem
try:
    from app.api.endpoints import api_router
    app.include_router(api_router, prefix="/api/v1")
except ImportError:
    pass  # Rotas nao disponiveis ainda
