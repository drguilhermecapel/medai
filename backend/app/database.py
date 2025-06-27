"""
Database configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/cardioai")
ASYNC_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/cardioai")

# Para testes, usar SQLite em memória
if os.getenv("TESTING") == "1":
    DATABASE_URL = "sqlite:///./test.db"
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Criar engine
engine = create_engine(DATABASE_URL, echo=False)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para os modelos
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
