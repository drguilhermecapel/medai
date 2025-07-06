"""
Repositório base para acesso a dados no MedAI
Implementa padrão Repository com operações CRUD genéricas
"""
import uuid
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc, func, text
from datetime import datetime

from app.models.base import BaseModel
from app.core.exceptions import (
    NotFoundError, DatabaseError, ValidationError, 
    DuplicateError, DatabaseIntegrityError
)
from app.utils.logging_config import get_logger

# Type variable para o modelo
ModelType = TypeVar("ModelType", bound=BaseModel)

logger = get_logger(__name__)


class BaseRepository(Generic[ModelType], ABC):
    """
    Repositório base genérico para operações CRUD
    
    Fornece operações padrão para qualquer modelo que herde de BaseModel
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Inicializa repositório
        
        Args:
            model: Classe do modelo SQLAlchemy
            db: Sessão do banco de dados
        """
        self.model = model
        self.db = db
        self.logger = logger
    
    # === OPERAÇÕES BÁSICAS CRUD ===
    
    def create(self, obj_in: Union[Dict[str, Any], ModelType], **kwargs) -> ModelType:
        """
        Cria novo registro
        
        Args:
            obj_in: Dados para criação (dict ou instância do modelo)
            **kwargs: Dados adicionais
            
        Returns:
            Instância criada
            
        Raises:
            DatabaseError: Erro na criação
            DuplicateError: Registro duplicado
        """
        try:
            if isinstance(obj_in, dict):
                obj_in.update(kwargs)
                db_obj = self.model(**obj_in)
            else:
                db_obj = obj_in
                for key, value in kwargs.items():
                    setattr(db_obj, key, value)
            
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            self.logger.info(
                f"Created {self.model.__name__} with ID: {db_obj.id}",
                extra={'model': self.model.__name__, 'action': 'create', 'id': str(db_obj.id)}
            )
            
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateError(self.model.__name__, "unknown", "unknown")
            raise DatabaseError(f"Error creating {self.model.__name__}: {str(e)}")
    
    def get(self, id: uuid.UUID, include_deleted: bool = False) -> Optional[ModelType]:
        """
        Busca registro por ID
        
        Args:
            id: ID do registro
            include_deleted: Se deve incluir registros deletados
            
        Returns:
            Instância encontrada ou None
        """
        try:
            query = self.db.query(self.model).filter(self.model.id == id)
            
            if not include_deleted and hasattr(self.model, 'is_deleted'):
                query = query.filter(self.model.is_deleted.is_(False))
            
            return query.first()
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error fetching {self.model.__name__}: {str(e)}")
    
    def get_or_404(self, id: uuid.UUID, include_deleted: bool = False) -> ModelType:
        """
        Busca registro por ID ou levanta exceção
        
        Args:
            id: ID do registro
            include_deleted: Se deve incluir registros deletados
            
        Returns:
            Instância encontrada
            
        Raises:
            NotFoundError: Registro não encontrado
        """
        obj = self.get(id, include_deleted)
        if not obj:
            raise NotFoundError(self.model.__name__, str(id))
        return obj
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_deleted: bool = False,
        order_by: str = None,
        desc_order: bool = False
    ) -> List[ModelType]:
        """
        Busca múltiplos registros
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            include_deleted: Se deve incluir registros deletados
            order_by: Campo para ordenação
            desc_order: Se ordenação é descendente
            
        Returns:
            Lista de instâncias
        """
        try:
            query = self.db.query(self.model)
            
            if not include_deleted and hasattr(self.model, 'is_deleted'):
                query = query.filter(self.model.is_deleted.is_(False))
            
            # Ordenação
            if order_by and hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                if desc_order:
                    query = query.order_by(desc(order_field))
                else:
                    query = query.order_by(asc(order_field))
            elif hasattr(self.model, 'created_at'):
                query = query.order_by(desc(self.model.created_at))
            
            return query.offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error fetching {self.model.__name__} list: {str(e)}")
    
    def update(
        self, 
        id: uuid.UUID, 
        obj_in: Union[Dict[str, Any], ModelType],
        **kwargs
    ) -> ModelType:
        """
        Atualiza registro
        
        Args:
            id: ID do registro
            obj_in: Dados para atualização
            **kwargs: Dados adicionais
            
        Returns:
            Instância atualizada
            
        Raises:
            NotFoundError: Registro não encontrado
        """
        try:
            db_obj = self.get_or_404(id)
            
            if isinstance(obj_in, dict):
                update_data = obj_in.copy()
                update_data.update(kwargs)
                
                for field, value in update_data.items():
                    if hasattr(db_obj, field):
                        setattr(db_obj, field, value)
            else:
                for field in obj_in.__dict__:
                    if not field.startswith('_') and hasattr(db_obj, field):
                        setattr(db_obj, field, getattr(obj_in, field))
                
                for key, value in kwargs.items():
                    if hasattr(db_obj, key):
                        setattr(db_obj, key, value)
            
            # Atualizar timestamp se existir
            if hasattr(db_obj, 'updated_at'):
                db_obj.updated_at = datetime.utcnow()
            
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            self.logger.info(
                f"Updated {self.model.__name__} with ID: {db_obj.id}",
                extra={'model': self.model.__name__, 'action': 'update', 'id': str(db_obj.id)}
            )
            
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error updating {self.model.__name__}: {str(e)}")
    
    def delete(self, id: uuid.UUID, hard_delete: bool = False) -> bool:
        """
        Remove registro
        
        Args:
            id: ID do registro
            hard_delete: Se deve deletar fisicamente
            
        Returns:
            True se removido com sucesso
            
        Raises:
            NotFoundError: Registro não encontrado
        """
        try:
            db_obj = self.get_or_404(id)
            
            if hard_delete or not hasattr(db_obj, 'is_deleted'):
                # Remoção física
                self.db.delete(db_obj)
                self.logger.info(
                    f"Hard deleted {self.model.__name__} with ID: {id}",
                    extra={'model': self.model.__name__, 'action': 'hard_delete', 'id': str(id)}
                )
            else:
                # Soft delete
                db_obj.soft_delete()
                self.db.add(db_obj)
                self.logger.info(
                    f"Soft deleted {self.model.__name__} with ID: {id}",
                    extra={'model': self.model.__name__, 'action': 'soft_delete', 'id': str(id)}
                )
            
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error deleting {self.model.__name__}: {str(e)}")
    
    def restore(self, id: uuid.UUID) -> ModelType:
        """
        Restaura registro soft-deleted
        
        Args:
            id: ID do registro
            
        Returns:
            Instância restaurada
            
        Raises:
            NotFoundError: Registro não encontrado
        """
        try:
            db_obj = self.get(id, include_deleted=True)
            if not db_obj:
                raise NotFoundError(self.model.__name__, str(id))
            
            if hasattr(db_obj, 'restore'):
                db_obj.restore()
                self.db.add(db_obj)
                self.db.commit()
                self.db.refresh(db_obj)
                
                self.logger.info(
                    f"Restored {self.model.__name__} with ID: {id}",
                    extra={'model': self.model.__name__, 'action': 'restore', 'id': str(id)}
                )
            
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error restoring {self.model.__name__}: {str(e)}")
    
    # === OPERAÇÕES DE CONSULTA AVANÇADAS ===
    
    def count(self, include_deleted: bool = False) -> int:
        """
        Conta registros
        
        Args:
            include_deleted: Se deve incluir registros deletados
            
        Returns:
            Número de registros
        """
        try:
            query = self.db.query(func.count(self.model.id))
            
            if not include_deleted and hasattr(self.model, 'is_deleted'):
                query = query.filter(self.model.is_deleted.is_(False))
            
            return query.scalar()
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error counting {self.model.__name__}: {str(e)}")
    
    def exists(self, id: uuid.UUID, include_deleted: bool = False) -> bool:
        """
        Verifica se registro existe
        
        Args:
            id: ID do registro
            include_deleted: Se deve incluir registros deletados
            
        Returns:
            True se existe
        """
        return self.get(id, include_deleted) is not None
    
    def filter_by(self, include_deleted: bool = False, **filters) -> List[ModelType]:
        """
        Filtra registros por campos específicos
        
        Args:
            include_deleted: Se deve incluir registros deletados
            **filters: Filtros de campo=valor
            
        Returns:
            Lista de instâncias filtradas
        """
        try:
            query = self.db.query(self.model)
            
            if not include_deleted and hasattr(self.model, 'is_deleted'):
                query = query.filter(self.model.is_deleted.is_(False))
            
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
            
            return query.all()
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error filtering {self.model.__name__}: {str(e)}")
    
    def find_by(self, include_deleted: bool = False, **filters) -> Optional[ModelType]:
        """
        Encontra primeiro registro que corresponde aos filtros
        
        Args:
            include_deleted: Se deve incluir registros deletados
            **filters: Filtros de campo=valor
            
        Returns:
            Primeira instância encontrada ou None
        """
        results = self.filter_by(include_deleted, **filters)
        return results[0] if results else None
    
    def search(
        self, 
        search_term: str, 
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        Busca textual em campos específicos
        
        Args:
            search_term: Termo para buscar
            search_fields: Lista de campos para buscar
            skip: Registros para pular
            limit: Limite de registros
            include_deleted: Se deve incluir registros deletados
            
        Returns:
            Lista de instâncias encontradas
        """
        try:
            query = self.db.query(self.model)
            
            if not include_deleted and hasattr(self.model, 'is_deleted'):
                query = query.filter(self.model.is_deleted.is_(False))
            
            # Criar condições de busca
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    field_attr = getattr(self.model, field)
                    search_conditions.append(
                        field_attr.ilike(f"%{search_term}%")
                    )
            
            if search_conditions:
                query = query.filter(or_(*search_conditions))
            
            return query.offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error searching {self.model.__name__}: {str(e)}")
    
    # === OPERAÇÕES EM LOTE ===
    
    def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Criação em lote
        
        Args:
            objects: Lista de dicionários com dados
            
        Returns:
            Lista de instâncias criadas
        """
        try:
            db_objects = [self.model(**obj_data) for obj_data in objects]
            
            self.db.add_all(db_objects)
            self.db.commit()
            
            for obj in db_objects:
                self.db.refresh(obj)
            
            self.logger.info(
                f"Bulk created {len(db_objects)} {self.model.__name__} records",
                extra={'model': self.model.__name__, 'action': 'bulk_create', 'count': len(db_objects)}
            )
            
            return db_objects
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error bulk creating {self.model.__name__}: {str(e)}")
    
    def bulk_update(self, updates: List[Dict[str, Any]], id_field: str = 'id') -> int:
        """
        Atualização em lote
        
        Args:
            updates: Lista de dicionários com dados de atualização
            id_field: Campo usado como identificador
            
        Returns:
            Número de registros atualizados
        """
        try:
            updated_count = 0
            
            for update_data in updates:
                if id_field not in update_data:
                    continue
                
                query = self.db.query(self.model).filter(
                    getattr(self.model, id_field) == update_data[id_field]
                )
                
                if not hasattr(self.model, 'is_deleted') or not update_data.get('include_deleted', False):
                    query = query.filter(self.model.is_deleted.is_(False))
                
                # Remover id_field dos dados de atualização
                clean_data = {k: v for k, v in update_data.items() if k != id_field}
                
                updated_count += query.update(clean_data, synchronize_session=False)
            
            self.db.commit()
            
            self.logger.info(
                f"Bulk updated {updated_count} {self.model.__name__} records",
                extra={'model': self.model.__name__, 'action': 'bulk_update', 'count': updated_count}
            )
            
            return updated_count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error bulk updating {self.model.__name__}: {str(e)}")
    
    def bulk_delete(self, ids: List[uuid.UUID], hard_delete: bool = False) -> int:
        """
        Remoção em lote
        
        Args:
            ids: Lista de IDs para remover
            hard_delete: Se deve deletar fisicamente
            
        Returns:
            Número de registros removidos
        """
        try:
            query = self.db.query(self.model).filter(self.model.id.in_(ids))
            
            if hard_delete or not hasattr(self.model, 'is_deleted'):
                deleted_count = query.delete(synchronize_session=False)
                action = 'bulk_hard_delete'
            else:
                # Soft delete em lote
                deleted_count = query.update(
                    {
                        'is_deleted': True,
                        'deleted_at': datetime.utcnow()
                    },
                    synchronize_session=False
                )
                action = 'bulk_soft_delete'
            
            self.db.commit()
            
            self.logger.info(
                f"Bulk deleted {deleted_count} {self.model.__name__} records",
                extra={'model': self.model.__name__, 'action': action, 'count': deleted_count}
            )
            
            return deleted_count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error bulk deleting {self.model.__name__}: {str(e)}")
    
    # === OPERAÇÕES DE AGREGAÇÃO ===
    
    def aggregate(self, aggregations: Dict[str, str]) -> Dict[str, Any]:
        """
        Operações de agregação
        
        Args:
            aggregations: Dict de {alias: 'func(field)'} 
                         Ex: {'total_users': 'count(id)', 'avg_age': 'avg(age)'}
            
        Returns:
            Resultado das agregações
        """
        try:
            select_items = []
            
            for alias, expression in aggregations.items():
                select_items.append(text(f"{expression} as {alias}"))
            
            query = self.db.query(*select_items).select_from(self.model)
            
            if hasattr(self.model, 'is_deleted'):
                query = query.filter(self.model.is_deleted.is_(False))
            
            result = query.first()
            
            return dict(result._mapping) if result else {}
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error aggregating {self.model.__name__}: {str(e)}")
    
    # === MÉTODOS UTILITÁRIOS ===
    
    def get_model_name(self) -> str:
        """Retorna nome do modelo"""
        return self.model.__name__
    
    def get_table_name(self) -> str:
        """Retorna nome da tabela"""
        return self.model.__tablename__
    
    def get_primary_key(self) -> str:
        """Retorna nome da chave primária"""
        return 'id'  # Padrão para nossos modelos
    
    def refresh(self, obj: ModelType) -> ModelType:
        """
        Atualiza objeto com dados do banco
        
        Args:
            obj: Instância para atualizar
            
        Returns:
            Instância atualizada
        """
        self.db.refresh(obj)
        return obj
    
    def flush(self) -> None:
        """Força envio de operações pendentes para o banco"""
        self.db.flush()
    
    def commit(self) -> None:
        """Confirma transação"""
        self.db.commit()
    
    def rollback(self) -> None:
        """Desfaz transação"""
        self.db.rollback()