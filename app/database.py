# -*- coding: utf-8 -*-
"""
Configuração do banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Usar a importação correta do declarative_base
try:
    # SQLAlchemy 2.0+
    from sqlalchemy.orm import declarative_base
except ImportError:
    # SQLAlchemy 1.4
    from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

# Base para modelos
Base = declarative_base()

# Engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Cria todas as tabelas do banco de dados"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Remove todas as tabelas do banco de dados"""
    Base.metadata.drop_all(bind=engine)
