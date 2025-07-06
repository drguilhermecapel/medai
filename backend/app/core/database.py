"""
Configuração e gerenciamento do banco de dados PostgreSQL
Sistema de conexão, sessões e monitoramento de saúde do banco
"""
from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any, List
import logging
import time
from datetime import datetime, timedelta

from app.core.config import settings, database_config
from app.core.constants import CACHE_TTL_MEDIUM


# === CONFIGURAÇÃO DO LOGGER ===
logger = logging.getLogger(__name__)


# === BASE DECLARATIVA ===
Base = declarative_base()


# === CONFIGURAÇÃO DO ENGINE ===

def create_database_engine() -> Engine:
    """
    Cria engine do banco de dados com configurações otimizadas
    
    Returns:
        Engine configurado do SQLAlchemy
    """
    engine_options = database_config.engine_options
    
    # Configurações específicas por ambiente
    if settings.is_production:
        engine_options.update({
            "poolclass": QueuePool,
            "pool_size": 20,
            "max_overflow": 30,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "echo": False
        })
    elif settings.is_development:
        engine_options.update({
            "poolclass": StaticPool,
            "pool_size": 5,
            "max_overflow": 10,
            "echo": True
        })
    else:  # testing
        engine_options.update({
            "poolclass": StaticPool,
            "pool_size": 1,
            "max_overflow": 0,
            "echo": False
        })
    
    engine = create_engine(
        settings.DATABASE_URL,
        **engine_options
    )
    
    # Configurar eventos do engine
    configure_engine_events(engine)
    
    return engine


def configure_engine_events(engine: Engine) -> None:
    """
    Configura eventos do engine para monitoramento e otimização
    
    Args:
        engine: Engine do SQLAlchemy
    """
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Configura pragmas do SQLite se necessário"""
        if "sqlite" in str(engine.url):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Log de queries em desenvolvimento"""
        if settings.is_development:
            context._query_start_time = time.time()
    
    @event.listens_for(engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Log de performance de queries"""
        if settings.is_development and hasattr(context, '_query_start_time'):
            total = time.time() - context._query_start_time
            if total > 0.1:  # Log queries que demoram mais de 100ms
                logger.warning(f"Slow query: {total:.3f}s - {statement[:100]}...")


# === INSTÂNCIAS GLOBAIS ===

# Engine global
engine = create_database_engine()

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# === DEPENDÊNCIAS FASTAPI ===

def get_db() -> Generator[Session, None, None]:
    """
    Dependência FastAPI para obter sessão do banco de dados
    
    Yields:
        Sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager para sessão do banco de dados
    
    Yields:
        Sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database context error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# === CLASSES DE GERENCIAMENTO ===

class DatabaseManager:
    """Gerenciador de operações do banco de dados"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self._health_cache = {}
        self._cache_timeout = CACHE_TTL_MEDIUM
    
    def create_all_tables(self) -> None:
        """Cria todas as tabelas do banco de dados"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("All database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def drop_all_tables(self) -> None:
        """Remove todas as tabelas do banco de dados"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("All database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            raise
    
    def check_connection(self) -> bool:
        """
        Verifica conectividade com o banco de dados
        
        Returns:
            True se a conexão estiver ok
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Retorna status de saúde do banco de dados
        
        Returns:
            Dict com informações de saúde
        """
        # Verificar cache
        cache_key = "database_health"
        cached_result = self._health_cache.get(cache_key)
        
        if cached_result and datetime.now() - cached_result["timestamp"] < timedelta(seconds=60):
            return cached_result["data"]
        
        health_status = {
            "status": "healthy",
            "connection": False,
            "pool_status": {},
            "table_count": 0,
            "last_check": datetime.utcnow().isoformat(),
            "errors": []
        }
        
        try:
            # Verificar conexão
            health_status["connection"] = self.check_connection()
            
            if health_status["connection"]:
                # Informações do pool de conexões
                pool = self.engine.pool
                health_status["pool_status"] = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow()
                }
                
                # Contar tabelas
                inspector = inspect(self.engine)
                health_status["table_count"] = len(inspector.get_table_names())
            else:
                health_status["status"] = "unhealthy"
                health_status["errors"].append("Database connection failed")
                
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["errors"].append(f"Health check error: {str(e)}")
            logger.error(f"Database health check error: {e}")
        
        # Armazenar no cache
        self._health_cache[cache_key] = {
            "data": health_status,
            "timestamp": datetime.now()
        }
        
        return health_status
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Retorna informações detalhadas do banco de dados
        
        Returns:
            Dict com informações do banco
        """
        try:
            with self.engine.connect() as conn:
                # Informações básicas
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                
                # Informações de tabelas
                inspector = inspect(self.engine)
                tables = inspector.get_table_names()
                
                info = {
                    "database_url": str(self.engine.url).split('@')[1] if '@' in str(self.engine.url) else str(self.engine.url),
                    "driver": self.engine.driver,
                    "version": version,
                    "tables": tables,
                    "table_count": len(tables),
                    "pool_info": {
                        "class": self.engine.pool.__class__.__name__,
                        "size": self.engine.pool.size(),
                        "overflow": self.engine.pool.overflow()
                    }
                }
                
                return info
                
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}
    
    def execute_raw_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Executa query SQL bruta
        
        Args:
            query: Query SQL para executar
            params: Parâmetros da query
            
        Returns:
            Lista de resultados
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    return [{"affected_rows": result.rowcount}]
                    
        except Exception as e:
            logger.error(f"Error executing raw query: {e}")
            raise


class DatabaseHealthChecker:
    """Verificador de saúde específico do banco de dados"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.name = "database"
    
    def perform_check(self) -> Dict[str, Any]:
        """
        Realiza verificação de saúde completa
        
        Returns:
            Resultado da verificação
        """
        start_time = time.time()
        
        try:
            # Teste de conexão básica
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Teste de transação
            with self.engine.begin() as conn:
                conn.execute(text("SELECT 1"))
            
            response_time = (time.time() - start_time) * 1000  # em ms
            
            status = "healthy"
            if response_time > 1000:  # mais de 1 segundo
                status = "warning"
            elif response_time > 5000:  # mais de 5 segundos
                status = "unhealthy"
            
            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "connection_test": "passed",
                    "transaction_test": "passed"
                }
            }
            
        except OperationalError as e:
            return {
                "status": "unhealthy",
                "error": "Database connection failed",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": "Database health check failed",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# === UTILITÁRIOS DE MIGRAÇÃO ===

class MigrationUtils:
    """Utilitários para migrações do banco de dados"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def backup_database(self, backup_name: str) -> bool:
        """
        Cria backup do banco de dados
        
        Args:
            backup_name: Nome do backup
            
        Returns:
            True se o backup foi criado com sucesso
        """
        try:
            # Implementar backup específico por tipo de banco
            logger.info(f"Creating database backup: {backup_name}")
            # Aqui implementar lógica específica de backup
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_database(self, backup_name: str) -> bool:
        """
        Restaura banco de dados de backup
        
        Args:
            backup_name: Nome do backup para restaurar
            
        Returns:
            True se a restauração foi bem-sucedida
        """
        try:
            logger.info(f"Restoring database from backup: {backup_name}")
            # Implementar lógica de restauração
            return True
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Retorna status das migrações
        
        Returns:
            Dict com status das migrações
        """
        try:
            # Verificar tabela alembic_version se existir
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            if "alembic_version" in tables:
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT version_num FROM alembic_version"))
                    current_version = result.scalar()
                    
                    return {
                        "has_migrations": True,
                        "current_version": current_version,
                        "tables_count": len(tables)
                    }
            else:
                return {
                    "has_migrations": False,
                    "current_version": None,
                    "tables_count": len(tables)
                }
                
        except Exception as e:
            logger.error(f"Error getting migration status: {e}")
            return {"error": str(e)}


# === INSTÂNCIAS GLOBAIS DE GERENCIAMENTO ===

# Manager global do banco
db_manager = DatabaseManager(engine)

# Health checker
db_health_checker = DatabaseHealthChecker(engine)

# Migration utils
migration_utils = MigrationUtils(engine)


# === FUNÇÕES DE INICIALIZAÇÃO ===

def init_database():
    """Inicializa o banco de dados"""
    try:
        logger.info("Initializing database...")
        
        # Verificar conexão
        if not db_manager.check_connection():
            raise Exception("Cannot connect to database")
        
        # Criar tabelas se necessário
        if settings.ENVIRONMENT == "development":
            db_manager.create_all_tables()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def close_database():
    """Fecha conexões do banco de dados"""
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# === DECORADORES PARA TRANSAÇÕES ===

def with_transaction(func):
    """
    Decorator para executar função em transação
    
    Args:
        func: Função para executar
        
    Returns:
        Wrapper da função
    """
    def wrapper(*args, **kwargs):
        with get_db_context() as db:
            try:
                result = func(db, *args, **kwargs)
                db.commit()
                return result
            except Exception as e:
                db.rollback()
                logger.error(f"Transaction failed: {e}")
                raise
    
    return wrapper


# === CONSTANTES DE CONFIGURAÇÃO ===

# Timeout para operações de banco
DATABASE_TIMEOUT = 30

# Configurações de retry
RETRY_CONFIG = {
    "max_attempts": 3,
    "backoff_factor": 2,
    "exceptions": (OperationalError, SQLAlchemyError)
}

# Pool de conexões - configurações por ambiente
POOL_CONFIGS = {
    "development": {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 3600
    },
    "production": {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_recycle": 3600
    },
    "testing": {
        "pool_size": 1,
        "max_overflow": 0,
        "pool_recycle": -1
    }
}