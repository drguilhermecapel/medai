#!/usr/bin/env python3
"""
Corrige o warning do SQLAlchemy sobre declarative_base()
Atualiza para usar sqlalchemy.orm.declarative_base()
"""

import os
import re
from pathlib import Path


def update_database_file():
    """Atualiza o arquivo database.py para usar a importação correta"""
    print("🔧 Atualizando app/database.py...")
    
    database_content = '''# -*- coding: utf-8 -*-
"""
Configuração do banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base as orm_declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import Generator

from app.config import settings

# Usar a importação mais recente do SQLAlchemy
try:
    # SQLAlchemy 2.0+
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
except ImportError:
    # SQLAlchemy 1.4
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

# Engine síncrono
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session síncrona
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Engine assíncrono (se necessário)
async_engine = None
AsyncSessionLocal = None

if hasattr(settings, 'ASYNC_SQLALCHEMY_DATABASE_URI'):
    try:
        async_engine = create_async_engine(
            settings.ASYNC_SQLALCHEMY_DATABASE_URI,
            pool_pre_ping=True
        )
        AsyncSessionLocal = async_sessionmaker(
            async_engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    except Exception:
        # Fallback se não conseguir criar engine assíncrono
        async_engine = None
        AsyncSessionLocal = None


def get_db() -> Generator:
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """
    Dependency para obter sessão assíncrona do banco de dados
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database not configured")
    
    async with AsyncSessionLocal() as session:
        yield session


def create_tables():
    """Cria todas as tabelas do banco de dados"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Remove todas as tabelas do banco de dados"""
    Base.metadata.drop_all(bind=engine)


async def create_tables_async():
    """Cria todas as tabelas do banco de dados (versão assíncrona)"""
    if async_engine is None:
        raise RuntimeError("Async database not configured")
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables_async():
    """Remove todas as tabelas do banco de dados (versão assíncrona)"""
    if async_engine is None:
        raise RuntimeError("Async database not configured")
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
'''
    
    # Salvar o arquivo database.py atualizado
    database_path = Path("app/database.py")
    
    with open(database_path, 'w', encoding='utf-8') as f:
        f.write(database_content)
    
    print("   ✅ app/database.py atualizado")


def fix_all_import_issues():
    """Corrige problemas de importação em vários arquivos"""
    print("🔧 Corrigindo outros problemas de importação...")
    
    # Lista de arquivos e suas correções
    fixes = {
        "app/models.py": [
            (r"from sqlalchemy.ext.declarative import declarative_base", 
             "from sqlalchemy.orm import declarative_base"),
        ],
        "app/main.py": [
            (r"from app.config import settings", 
             "from app.config import settings"),
        ]
    }
    
    for file_path, replacements in fixes.items():
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Aplicar todas as substituições
                for old_pattern, new_pattern in replacements:
                    content = re.sub(old_pattern, new_pattern, content)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ {file_path} atualizado")
                
            except Exception as e:
                print(f"   ⚠️  Erro ao atualizar {file_path}: {e}")


def create_missing_directories():
    """Cria diretórios necessários se não existirem"""
    print("📁 Criando diretórios necessários...")
    
    directories = [
        "uploads",
        "ml_models", 
        "logs",
        "temp",
        "static"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Diretório criado: {directory}")
        else:
            print(f"   ℹ️  Diretório já existe: {directory}")


def check_installations():
    """Verifica se todas as dependências necessárias estão instaladas"""
    print("📦 Verificando instalações necessárias...")
    
    required_packages = [
        'pydantic-settings',
        'sqlalchemy',
        'fastapi',
        'pytest',
        'pytest-cov'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package} instalado")
        except ImportError:
            print(f"   ❌ {package} NÃO instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n📋 Para instalar pacotes faltantes:")
        for package in missing_packages:
            print(f"pip install {package}")
        return False
    
    return True


def test_imports():
    """Testa se todos os imports principais funcionam"""
    print("🧪 Testando importações principais...")
    
    imports_to_test = [
        ("app.config", "Settings, settings"),
        ("app.database", "Base, get_db"),
        ("sqlalchemy.orm", "declarative_base"),
    ]
    
    all_success = True
    
    for module, items in imports_to_test:
        try:
            exec(f"from {module} import {items}")
            print(f"   ✅ {module}: {items}")
        except Exception as e:
            print(f"   ❌ {module}: {e}")
            all_success = False
    
    return all_success


def main():
    """Função principal"""
    print("🛠️  CORREÇÃO COMPLETA DE PROBLEMAS DE CONFIGURAÇÃO")
    print("=" * 60)
    
    # 1. Verificar instalações
    if not check_installations():
        print("\n⚠️  Instale os pacotes faltantes antes de continuar")
        return
    
    # 2. Atualizar database.py
    update_database_file()
    
    # 3. Corrigir outros imports
    fix_all_import_issues()
    
    # 4. Criar diretórios necessários
    create_missing_directories()
    
    # 5. Testar importações
    print("\n" + "=" * 60)
    if test_imports():
        print("✅ Todas as importações funcionam!")
    else:
        print("❌ Ainda há problemas com algumas importações")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Execute: python fix_pydantic_config.py")
    print("2. Execute: python -m pytest tests/unit/ -v")
    print("3. Se ainda houver problemas, verifique os logs de erro")


if __name__ == "__main__":
    main()