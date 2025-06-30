"""
Configuração do banco de dados para o MedAI
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from app.core.config import settings


# Configuração do engine baseada no ambiente
if settings.TESTING:
    # Para testes, usa SQLite em memória
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_medai.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # Produção/Desenvolvimento usa PostgreSQL
    SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URL)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Habilita foreign keys no SQLite
if settings.TESTING:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Configuração da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados
    
    Yields:
        Session: Sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas
    """
    # Importa todos os modelos para garantir que estão registrados
    from app.models import (
        user,
        patient,
        exam,
        diagnostic,
        prescription,
        appointment,
        notification
    )
    
    # Cria todas as tabelas
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Remove todas as tabelas do banco de dados
    Usar apenas em ambiente de desenvolvimento/teste!
    """
    if not settings.TESTING and settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot drop database tables in production!")
    
    Base.metadata.drop_all(bind=engine)


def reset_db() -> None:
    """
    Reseta o banco de dados (drop + create)
    Usar apenas em ambiente de desenvolvimento/teste!
    """
    if not settings.TESTING and settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot reset database in production!")
    
    drop_db()
    init_db()


class DatabaseSession:
    """Context manager para sessões de banco de dados"""
    
    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()
        self.db.close()


def get_db_context() -> DatabaseSession:
    """
    Retorna um context manager para sessão do banco
    
    Exemplo:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    return DatabaseSession()


# Funções auxiliares para testes
def create_test_database():
    """Cria banco de dados de teste"""
    if not settings.TESTING:
        raise RuntimeError("This function should only be used in tests!")
    
    init_db()


def cleanup_test_database():
    """Limpa banco de dados de teste"""
    if not settings.TESTING:
        raise RuntimeError("This function should only be used in tests!")
    
    drop_db()