# app/core/database.py - ARQUIVO CORRETO
"""
Core database configuration
Este arquivo deve conter apenas imports do database principal
"""
from app.database import (
    engine,
    AsyncSessionLocal,
    SessionLocal,
    get_db,
    get_async_db,
    create_all_tables,
    drop_all_tables
)

# Re-exportar tudo para compatibilidade
__all__ = [
    "engine",
    "AsyncSessionLocal",
    "SessionLocal",
    "get_db",
    "get_async_db",
    "create_all_tables",
    "drop_all_tables"
]