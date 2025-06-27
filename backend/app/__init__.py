"""
MedAI - Sistema de Análise Médica com IA
"""

__version__ = "1.0.0"
__author__ = "MedAI Team"
__email__ = "support@medai.com"

# Imports principais para facilitar o acesso
from app.database import Base, get_db, get_async_db, SessionLocal, AsyncSessionLocal

__all__ = [
    "Base",
    "get_db", 
    "get_async_db",
    "SessionLocal",
    "AsyncSessionLocal"
]