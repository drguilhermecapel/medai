# app/models/base.py - CORREÇÃO
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

# app/core/database.py - NOVO ARQUIVO (não confundir com app/database.py)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from typing import AsyncGenerator

# URL do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/medai"
)

# Criar engine assíncrona
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,  # Para evitar problemas com conexões em testes
)

# Criar session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency para FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Criar todas as tabelas (usado apenas em desenvolvimento)
async def create_all_tables():
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dropar todas as tabelas (usado apenas em testes)
async def drop_all_tables():
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)