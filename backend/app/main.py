# app/main.py - CORREÇÃO COMPLETA
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importações locais
from app.core.config import settings
from app.api.v1.endpoints import health

# Lifecycle manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up CardioAI Pro API...")
    yield
    # Shutdown
    print("Shutting down CardioAI Pro API...")

# Criar aplicação
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, prefix="/api/v1")

# Importar outros routers quando estiverem prontos
try:
    from app.api.v1.endpoints import auth, users, patients, ecg_analysis, validations, notifications
    
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(patients.router, prefix="/api/v1")
    app.include_router(ecg_analysis.router, prefix="/api/v1")
    app.include_router(validations.router, prefix="/api/v1")
    app.include_router(notifications.router, prefix="/api/v1")
except ImportError as e:
    print(f"Warning: Could not import all routers: {e}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to CardioAI Pro API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Health endpoints diretos para testes
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Websocket endpoints para testes
@app.websocket("/ws/ecg/{client_id}")
async def ecg_websocket(websocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except:
        pass

@app.websocket("/ws/notifications/{user_id}")
async def notifications_websocket(websocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Notification: {data}")
    except:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)