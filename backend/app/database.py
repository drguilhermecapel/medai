"""
Configuração do banco de dados para o MedAI
"""
import os
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, event, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

# Metadata com naming convention
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# Base para os modelos
Base = declarative_base(metadata=metadata)

# Configurações do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medai")

# URLs para conexões síncronas e assíncronas
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL
    SYNC_DATABASE_URL = DATABASE_URL

# Configurações para testes
TESTING = os.getenv("TESTING", "false").lower() == "true"

if TESTING:
    # Para testes, usa SQLite em memória
    SYNC_DATABASE_URL = "sqlite:///:memory:"
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    
    # Engine síncrono para testes
    engine = create_engine(
        SYNC_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Engine assíncrono para testes
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # Engine síncrono para produção
    engine = create_engine(
        SYNC_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )
    
    # Engine assíncrono para produção
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# Session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# Dependency para obter sessão do banco (síncrona)
def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados síncrona
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency para obter sessão do banco (assíncrona)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obter sessão do banco de dados assíncrona
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Função para criar todas as tabelas
def create_tables():
    """Cria todas as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)


# Função para dropar todas as tabelas
def drop_tables():
    """Remove todas as tabelas do banco de dados"""
    Base.metadata.drop_all(bind=engine)


# Função para resetar o banco (útil para testes)
def reset_database():
    """Reseta o banco de dados (drop e create)"""
    drop_tables()
    create_tables()


# Event listeners para SQLite (necessário para foreign keys)
if "sqlite" in SYNC_DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Função para verificar conexão com o banco
def check_database_connection():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")
        return False


# Função assíncrona para verificar conexão
async def check_async_database_connection():
    """Verifica se a conexão assíncrona com o banco está funcionando"""
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Erro ao conectar no banco de dados (async): {e}")
        return False


# Configurações adicionais para produção
class DatabaseConfig:
    """Configurações do banco de dados"""
    
    # Pool de conexões
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600  # 1 hora
    
    # Timeouts
    STATEMENT_TIMEOUT = 30000  # 30 segundos em ms
    LOCK_TIMEOUT = 10000  # 10 segundos em ms
    
    # Configurações de retry
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # segundos
    
    # Batch operations
    BATCH_SIZE = 1000
    
    # Maintenance
    VACUUM_THRESHOLD = 100000  # registros
    ANALYZE_THRESHOLD = 10000  # registros


# Export das principais classes e funções
__all__ = [
    "Base",
    "engine",
    "async_engine",
    "SessionLocal",
    "AsyncSessionLocal",
    "get_db",
    "get_async_db",
    "create_tables",
    "drop_tables",
    "reset_database",
    "check_database_connection",
    "check_async_database_connection",
    "DatabaseConfig",
    "metadata"
]