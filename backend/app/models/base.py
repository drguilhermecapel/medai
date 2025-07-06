"""
Modelo base para todos os modelos do banco de dados
Define campos comuns e funcionalidades compartilhadas
"""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, String, DateTime, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session

from app.core.database import Base


class TimestampMixin:
    """Mixin para campos de timestamp"""
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Data e hora de criação"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Data e hora da última atualização"
    )


class SoftDeleteMixin:
    """Mixin para soft delete (exclusão lógica)"""
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Indica se o registro foi excluído logicamente"
    )
    
    deleted_at = Column(
        DateTime,
        nullable=True,
        doc="Data e hora da exclusão lógica"
    )
    
    def soft_delete(self):
        """Marca o registro como excluído"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restaura um registro excluído logicamente"""
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """Mixin para auditoria (quem criou/modificou)"""
    
    created_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        doc="ID do usuário que criou o registro"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        doc="ID do usuário que fez a última atualização"
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """
    Modelo base para todas as entidades do sistema
    
    Inclui:
    - ID único UUID
    - Timestamps de criação e atualização
    - Soft delete
    - Métodos utilitários comuns
    """
    
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        doc="Identificador único do registro"
    )
    
    @declared_attr
    def __tablename__(cls):
        """Gera nome da tabela automaticamente baseado no nome da classe"""
        # Converte CamelCase para snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower() + 's'
    
    def __repr__(self) -> str:
        """Representação string do objeto"""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """
        Converte modelo para dicionário
        
        Args:
            exclude: Lista de campos para excluir
            
        Returns:
            Dicionário com os dados do modelo
        """
        exclude = exclude or []
        exclude.extend(['_sa_instance_state'])
        
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                
                # Serializar valores especiais
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    result[column.name] = str(value)
                else:
                    result[column.name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude: Optional[list] = None):
        """
        Atualiza modelo a partir de dicionário
        
        Args:
            data: Dados para atualização
            exclude: Campos para excluir da atualização
        """
        exclude = exclude or []
        exclude.extend(['id', 'created_at', 'updated_at'])
        
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def create(cls, db: Session, **kwargs):
        """
        Cria nova instância do modelo
        
        Args:
            db: Sessão do banco de dados
            **kwargs: Dados para criação
            
        Returns:
            Nova instância criada
        """
        instance = cls(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
    
    def save(self, db: Session):
        """
        Salva alterações no banco de dados
        
        Args:
            db: Sessão do banco de dados
        """
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
    
    def delete(self, db: Session, hard_delete: bool = False):
        """
        Exclui registro do banco de dados
        
        Args:
            db: Sessão do banco de dados
            hard_delete: Se True, exclui fisicamente; se False, soft delete
        """
        if hard_delete:
            db.delete(self)
        else:
            self.soft_delete()
            db.add(self)
        
        db.commit()
    
    @classmethod
    def get_by_id(cls, db: Session, id: uuid.UUID, include_deleted: bool = False):
        """
        Busca registro por ID
        
        Args:
            db: Sessão do banco de dados
            id: ID do registro
            include_deleted: Se deve incluir registros deletados
            
        Returns:
            Instância encontrada ou None
        """
        query = db.query(cls).filter(cls.id == id)
        
        if not include_deleted:
            query = query.filter(cls.is_deleted.is_(False))
        
        return query.first()
    
    @classmethod
    def get_all(cls, db: Session, include_deleted: bool = False, limit: int = None, offset: int = None):
        """
        Busca todos os registros
        
        Args:
            db: Sessão do banco de dados
            include_deleted: Se deve incluir registros deletados
            limit: Limite de registros
            offset: Offset para paginação
            
        Returns:
            Lista de instâncias
        """
        query = db.query(cls)
        
        if not include_deleted:
            query = query.filter(cls.is_deleted.is_(False))
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def count(cls, db: Session, include_deleted: bool = False) -> int:
        """
        Conta registros da tabela
        
        Args:
            db: Sessão do banco de dados
            include_deleted: Se deve incluir registros deletados
            
        Returns:
            Número de registros
        """
        query = db.query(cls)
        
        if not include_deleted:
            query = query.filter(cls.is_deleted.is_(False))
        
        return query.count()
    
    @classmethod
    def exists(cls, db: Session, id: uuid.UUID, include_deleted: bool = False) -> bool:
        """
        Verifica se registro existe
        
        Args:
            db: Sessão do banco de dados
            id: ID do registro
            include_deleted: Se deve incluir registros deletados
            
        Returns:
            True se existe, False caso contrário
        """
        return cls.get_by_id(db, id, include_deleted) is not None
    
    def is_owned_by(self, user_id: uuid.UUID) -> bool:
        """
        Verifica se o registro pertence ao usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se pertence ao usuário
        """
        # Implementação base - pode ser sobrescrita em modelos específicos
        return hasattr(self, 'user_id') and self.user_id == user_id
    
    def can_be_accessed_by(self, user_id: uuid.UUID, user_role: str) -> bool:
        """
        Verifica se o usuário pode acessar o registro
        
        Args:
            user_id: ID do usuário
            user_role: Role do usuário
            
        Returns:
            True se pode acessar
        """
        # Admins podem acessar tudo
        if user_role == 'admin':
            return True
        
        # Proprietário pode acessar
        if self.is_owned_by(user_id):
            return True
        
        # Implementação específica pode ser adicionada em subclasses
        return False


class AuditableModel(BaseModel, AuditMixin):
    """
    Modelo base com auditoria completa
    
    Inclui tudo do BaseModel mais:
    - Campos de auditoria (created_by, updated_by)
    """
    
    __abstract__ = True
    
    def set_created_by(self, user_id: uuid.UUID):
        """Define quem criou o registro"""
        self.created_by = user_id
    
    def set_updated_by(self, user_id: uuid.UUID):
        """Define quem atualizou o registro"""
        self.updated_by = user_id
    
    def save_with_audit(self, db: Session, user_id: uuid.UUID):
        """
        Salva com informações de auditoria
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário que está fazendo a alteração
        """
        # Se é um novo registro
        if not self.id:
            self.set_created_by(user_id)
        
        # Sempre atualizar o updated_by
        self.set_updated_by(user_id)
        
        return self.save(db)


class VersionedModel(AuditableModel):
    """
    Modelo base com versionamento
    
    Inclui tudo do AuditableModel mais:
    - Controle de versão
    """
    
    __abstract__ = True
    
    version = Column(
        String(50),
        default="1.0",
        nullable=False,
        doc="Versão do registro"
    )
    
    def increment_version(self):
        """Incrementa a versão do registro"""
        if self.version:
            try:
                major, minor = map(int, self.version.split('.'))
                self.version = f"{major}.{minor + 1}"
            except (ValueError, AttributeError):
                self.version = "1.1"
        else:
            self.version = "1.0"
    
    def save_with_version(self, db: Session, user_id: uuid.UUID):
        """
        Salva incrementando a versão
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário que está fazendo a alteração
        """
        # Incrementar versão se não é novo registro
        if self.id:
            self.increment_version()
        
        return self.save_with_audit(db, user_id)


# === MIXINS ADICIONAIS ===

class SlugMixin:
    """Mixin para campos slug (URL amigável)"""
    
    slug = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        doc="Slug para URL amigável"
    )
    
    def generate_slug(self, text: str):
        """
        Gera slug a partir de texto
        
        Args:
            text: Texto para gerar o slug
        """
        import re
        
        # Converter para minúsculas e remover caracteres especiais
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        # Substituir espaços e múltiplos hífens por hífen único
        slug = re.sub(r'[-\s]+', '-', slug)
        # Remover hífens do início e fim
        slug = slug.strip('-')
        
        self.slug = slug


class StatusMixin:
    """Mixin para campos de status"""
    
    status = Column(
        String(50),
        default="active",
        nullable=False,
        index=True,
        doc="Status do registro"
    )
    
    def activate(self):
        """Ativa o registro"""
        self.status = "active"
    
    def deactivate(self):
        """Desativa o registro"""
        self.status = "inactive"
    
    def is_active(self) -> bool:
        """Verifica se está ativo"""
        return self.status == "active"


class MetadataMixin:
    """Mixin para metadados adicionais"""
    
    from sqlalchemy.dialects.postgresql import JSONB
    
    metadata = Column(
        JSONB,
        default=dict,
        nullable=True,
        doc="Metadados adicionais em formato JSON"
    )
    
    def set_metadata(self, key: str, value: Any):
        """Define um valor nos metadados"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None):
        """Obtém um valor dos metadados"""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def update_metadata(self, data: Dict[str, Any]):
        """Atualiza múltiplos valores nos metadados"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata.update(data)


# === UTILITÁRIOS ===

def get_model_fields(model_class) -> list:
    """
    Retorna lista de campos de um modelo
    
    Args:
        model_class: Classe do modelo
        
    Returns:
        Lista com nomes dos campos
    """
    return [column.name for column in model_class.__table__.columns]


def model_to_dict(instance, exclude: Optional[list] = None) -> Dict[str, Any]:
    """
    Converte instância de modelo para dicionário (função utilitária)
    
    Args:
        instance: Instância do modelo
        exclude: Campos para excluir
        
    Returns:
        Dicionário com os dados
    """
    if hasattr(instance, 'to_dict'):
        return instance.to_dict(exclude)
    
    exclude = exclude or []
    result = {}
    
    for column in instance.__table__.columns:
        if column.name not in exclude:
            value = getattr(instance, column.name)
            
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
    
    return result