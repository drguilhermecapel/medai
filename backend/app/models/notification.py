"""
Modelo de notificação do sistema MedAI
Define notificações enviadas aos usuários sobre eventos do sistema
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid_property import hybrid_property

from app.models.base import AuditableModel, StatusMixin, MetadataMixin
from app.core.constants import NotificationType, NotificationPriority


class Notification(AuditableModel, StatusMixin, MetadataMixin):
    """
    Modelo de notificação do sistema
    
    Representa notificações enviadas aos usuários sobre:
    - Diagnósticos prontos
    - Exames concluídos
    - Lembretes de consultas
    - Alertas do sistema
    - Resultados de análises
    """
    
    __tablename__ = "notifications"
    
    # === RELACIONAMENTOS ===
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Usuário destinatário"
    )
    
    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Usuário remetente (se aplicável)"
    )
    
    # Relacionamentos opcionais com entidades específicas
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id"),
        nullable=True,
        doc="Paciente relacionado"
    )
    
    exam_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exams.id"),
        nullable=True,
        doc="Exame relacionado"
    )
    
    diagnostic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("diagnostics.id"),
        nullable=True,
        doc="Diagnóstico relacionado"
    )
    
    appointment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id"),
        nullable=True,
        doc="Consulta relacionada"
    )
    
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id"),
        nullable=True,
        doc="Prescrição relacionada"
    )
    
    # === INFORMAÇÕES BÁSICAS ===
    notification_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Código único da notificação"
    )
    
    title = Column(
        String(255),
        nullable=False,
        doc="Título da notificação"
    )
    
    message = Column(
        Text,
        nullable=False,
        doc="Mensagem da notificação"
    )
    
    summary = Column(
        String(500),
        nullable=True,
        doc="Resumo da notificação"
    )
    
    # === TIPO E PRIORIDADE ===
    notification_type = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Tipo da notificação"
    )
    
    category = Column(
        String(50),
        nullable=True,
        doc="Categoria da notificação"
    )
    
    priority = Column(
        String(20),
        default=NotificationPriority.NORMAL.value,
        nullable=False,
        index=True,
        doc="Prioridade da notificação"
    )
    
    urgent = Column(
        Boolean,
        default=False,
        doc="Notificação urgente"
    )
    
    # === CANAIS DE ENTREGA ===
    channels = Column(
        ARRAY(String),
        default=list,
        doc="Canais de entrega (email, sms, push, in-app)"
    )
    
    # === EMAIL ===
    email_sent = Column(
        Boolean,
        default=False,
        doc="Email enviado"
    )
    
    email_sent_at = Column(
        DateTime,
        nullable=True,
        doc="Data de envio do email"
    )
    
    email_opened = Column(
        Boolean,
        default=False,
        doc="Email aberto"
    )
    
    email_opened_at = Column(
        DateTime,
        nullable=True,
        doc="Data de abertura do email"
    )
    
    email_error = Column(
        Text,
        nullable=True,
        doc="Erro no envio do email"
    )
    
    # === SMS ===
    sms_sent = Column(
        Boolean,
        default=False,
        doc="SMS enviado"
    )
    
    sms_sent_at = Column(
        DateTime,
        nullable=True,
        doc="Data de envio do SMS"
    )
    
    sms_delivered = Column(
        Boolean,
        default=False,
        doc="SMS entregue"
    )
    
    sms_error = Column(
        Text,
        nullable=True,
        doc="Erro no envio do SMS"
    )
    
    # === PUSH NOTIFICATION ===
    push_sent = Column(
        Boolean,
        default=False,
        doc="Push notification enviada"
    )
    
    push_sent_at = Column(
        DateTime,
        nullable=True,
        doc="Data de envio da push"
    )
    
    push_opened = Column(
        Boolean,
        default=False,
        doc="Push notification aberta"
    )
    
    push_error = Column(
        Text,
        nullable=True,
        doc="Erro no envio da push"
    )
    
    # === IN-APP NOTIFICATION ===
    in_app_read = Column(
        Boolean,
        default=False,
        doc="Lida no app"
    )
    
    in_app_read_at = Column(
        DateTime,
        nullable=True,
        doc="Data de leitura no app"
    )
    
    in_app_dismissed = Column(
        Boolean,
        default=False,
        doc="Dispensada no app"
    )
    
    in_app_dismissed_at = Column(
        DateTime,
        nullable=True,
        doc="Data de dispensa no app"
    )
    
    # === AGENDAMENTO ===
    scheduled_for = Column(
        DateTime,
        nullable=True,
        doc="Agendada para envio"
    )
    
    sent_at = Column(
        DateTime,
        nullable=True,
        doc="Data de envio"
    )
    
    expires_at = Column(
        DateTime,
        nullable=True,
        doc="Data de expiração"
    )
    
    # === DADOS ADICIONAIS ===
    template_name = Column(
        String(100),
        nullable=True,
        doc="Template utilizado"
    )
    
    template_variables = Column(
        JSONB,
        default=dict,
        doc="Variáveis do template"
    )
    
    action_required = Column(
        Boolean,
        default=False,
        doc="Requer ação do usuário"
    )
    
    action_url = Column(
        String(500),
        nullable=True,
        doc="URL para ação"
    )
    
    action_text = Column(
        String(100),
        nullable=True,
        doc="Texto do botão de ação"
    )
    
    action_taken = Column(
        Boolean,
        default=False,
        doc="Ação executada"
    )
    
    action_taken_at = Column(
        DateTime,
        nullable=True,
        doc="Data da ação"
    )
    
    # === DADOS DE RASTREAMENTO ===
    tracking_data = Column(
        JSONB,
        default=dict,
        doc="Dados de rastreamento"
    )
    
    delivery_attempts = Column(
        ARRAY(DateTime),
        default=list,
        doc="Tentativas de entrega"
    )
    
    retry_count = Column(
        String(5),
        default="0",
        doc="Contador de tentativas"
    )
    
    max_retries = Column(
        String(5),
        default="3",
        doc="Máximo de tentativas"
    )
    
    # === PERSONALIZAÇÃO ===
    personalized = Column(
        Boolean,
        default=False,
        doc="Notificação personalizada"
    )
    
    user_preferences_applied = Column(
        Boolean,
        default=False,
        doc="Preferências do usuário aplicadas"
    )
    
    locale = Column(
        String(10),
        default="pt-BR",
        doc="Localização/idioma"
    )
    
    timezone = Column(
        String(50),
        default="America/Sao_Paulo",
        doc="Fuso horário"
    )
    
    # === RELACIONAMENTOS ===
    user = relationship("User", foreign_keys=[user_id])
    sender = relationship("User", foreign_keys=[sender_id])
    patient = relationship("Patient", foreign_keys=[patient_id])
    exam = relationship("Exam", foreign_keys=[exam_id])
    diagnostic = relationship("Diagnostic", foreign_keys=[diagnostic_id])
    appointment = relationship("Appointment", foreign_keys=[appointment_id])
    prescription = relationship("Prescription", foreign_keys=[prescription_id])
    
    # === ÍNDICES ===
    __table_args__ = (
        Index('ix_notifications_code', 'notification_code'),
        Index('ix_notifications_user_type', 'user_id', 'notification_type'),
        Index('ix_notifications_user_read', 'user_id', 'in_app_read'),
        Index('ix_notifications_priority_date', 'priority', 'created_at'),
        Index('ix_notifications_scheduled', 'scheduled_for'),
        Index('ix_notifications_urgent', 'urgent'),
        Index('ix_notifications_action_required', 'action_required'),
        Index('ix_notifications_expires', 'expires_at'),
    )
    
    # === PROPRIEDADES CALCULADAS ===
    
    @hybrid_property
    def is_read(self) -> bool:
        """Verifica se foi lida"""
        return self.in_app_read
    
    @hybrid_property
    def is_sent(self) -> bool:
        """Verifica se foi enviada"""
        return self.sent_at is not None
    
    @hybrid_property
    def is_expired(self) -> bool:
        """Verifica se expirou"""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    @hybrid_property
    def is_scheduled(self) -> bool:
        """Verifica se está agendada"""
        return self.scheduled_for and self.scheduled_for > datetime.utcnow()
    
    @hybrid_property
    def should_send_now(self) -> bool:
        """Verifica se deve ser enviada agora"""
        if self.is_sent or self.is_expired:
            return False
        
        if self.scheduled_for:
            return self.scheduled_for <= datetime.utcnow()
        
        return True
    
    @hybrid_property
    def delivery_status(self) -> str:
        """Status de entrega geral"""
        if self.is_expired:
            return "expired"
        if not self.is_sent:
            return "pending"
        
        # Verificar status por canal
        statuses = []
        if "email" in (self.channels or []):
            if self.email_error:
                statuses.append("email_failed")
            elif self.email_sent:
                statuses.append("email_sent")
        
        if "sms" in (self.channels or []):
            if self.sms_error:
                statuses.append("sms_failed")
            elif self.sms_delivered:
                statuses.append("sms_delivered")
            elif self.sms_sent:
                statuses.append("sms_sent")
        
        if "push" in (self.channels or []):
            if self.push_error:
                statuses.append("push_failed")
            elif self.push_sent:
                statuses.append("push_sent")
        
        if any("failed" in status for status in statuses):
            return "partially_failed"
        elif statuses:
            return "delivered"
        
        return "sent"
    
    @hybrid_property
    def engagement_score(self) -> float:
        """Score de engajamento (0.0 a 1.0)"""
        score = 0.0
        actions = 0
        
        # Email
        if self.email_sent:
            actions += 1
            if self.email_opened:
                score += 1.0
        
        # Push
        if self.push_sent:
            actions += 1
            if self.push_opened:
                score += 1.0
        
        # In-app
        if not self.is_expired:
            actions += 1
            if self.in_app_read:
                score += 1.0
        
        # Ação específica
        if self.action_required:
            actions += 1
            if self.action_taken:
                score += 1.0
        
        return score / actions if actions > 0 else 0.0
    
    @hybrid_property
    def days_since_sent(self) -> Optional[int]:
        """Dias desde o envio"""
        if self.sent_at:
            return (datetime.utcnow() - self.sent_at).days
        return None
    
    # === MÉTODOS DE ENVIO ===
    
    def schedule(self, send_datetime: datetime) -> None:
        """Agenda o envio da notificação"""
        self.scheduled_for = send_datetime
    
    def send_now(self) -> None:
        """Marca como enviada agora"""
        self.sent_at = datetime.utcnow()
        if not self.delivery_attempts:
            self.delivery_attempts = []
        self.delivery_attempts.append(self.sent_at)
    
    def mark_email_sent(self, success: bool = True, error: str = None) -> None:
        """Marca status do envio por email"""
        self.email_sent = success
        self.email_sent_at = datetime.utcnow()
        if error:
            self.email_error = error
    
    def mark_email_opened(self) -> None:
        """Marca email como aberto"""
        self.email_opened = True
        self.email_opened_at = datetime.utcnow()
    
    def mark_sms_sent(self, success: bool = True, error: str = None) -> None:
        """Marca status do envio por SMS"""
        self.sms_sent = success
        self.sms_sent_at = datetime.utcnow()
        if error:
            self.sms_error = error
    
    def mark_sms_delivered(self) -> None:
        """Marca SMS como entregue"""
        self.sms_delivered = True
    
    def mark_push_sent(self, success: bool = True, error: str = None) -> None:
        """Marca status do envio de push"""
        self.push_sent = success
        self.push_sent_at = datetime.utcnow()
        if error:
            self.push_error = error
    
    def mark_push_opened(self) -> None:
        """Marca push como aberta"""
        self.push_opened = True
    
    def mark_read(self) -> None:
        """Marca como lida no app"""
        self.in_app_read = True
        self.in_app_read_at = datetime.utcnow()
    
    def mark_dismissed(self) -> None:
        """Marca como dispensada no app"""
        self.in_app_dismissed = True
        self.in_app_dismissed_at = datetime.utcnow()
    
    def mark_action_taken(self) -> None:
        """Marca ação como executada"""
        self.action_taken = True
        self.action_taken_at = datetime.utcnow()
    
    def retry_delivery(self) -> bool:
        """
        Tenta reenvio da notificação
        
        Returns:
            True se pode tentar novamente
        """
        current_retries = int(self.retry_count or "0")
        max_retries = int(self.max_retries or "3")
        
        if current_retries < max_retries:
            self.retry_count = str(current_retries + 1)
            if not self.delivery_attempts:
                self.delivery_attempts = []
            self.delivery_attempts.append(datetime.utcnow())
            return True
        
        return False
    
    # === MÉTODOS DE GESTÃO DE DADOS ===
    
    def set_template_variables(self, variables: Dict[str, Any]) -> None:
        """Define variáveis do template"""
        if not self.template_variables:
            self.template_variables = {}
        self.template_variables.update(variables)
    
    def add_tracking_data(self, key: str, value: Any) -> None:
        """Adiciona dados de rastreamento"""
        if not self.tracking_data:
            self.tracking_data = {}
        self.tracking_data[key] = value
        self.tracking_data['updated_at'] = datetime.utcnow().isoformat()
    
    def set_action(self, url: str, text: str) -> None:
        """Define ação da notificação"""
        self.action_required = True
        self.action_url = url
        self.action_text = text
    
    def add_channel(self, channel: str) -> None:
        """Adiciona canal de entrega"""
        if not self.channels:
            self.channels = []
        if channel not in self.channels:
            self.channels.append(channel)
    
    def remove_channel(self, channel: str) -> None:
        """Remove canal de entrega"""
        if self.channels and channel in self.channels:
            self.channels.remove(channel)
    
    def set_expiry(self, hours: int = 24) -> None:
        """Define expiração da notificação"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
    
    # === MÉTODOS DE CONSULTA ===
    
    @classmethod
    def get_by_code(cls, db: Session, notification_code: str) -> Optional['Notification']:
        """Busca notificação por código"""
        return db.query(cls).filter(
            cls.notification_code == notification_code,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_user(cls, db: Session, user_id: uuid.UUID, 
                   unread_only: bool = False, limit: int = None) -> List['Notification']:
        """Busca notificações de um usuário"""
        query = db.query(cls).filter(
            cls.user_id == user_id,
            cls.is_deleted.is_(False)
        )
        
        if unread_only:
            query = query.filter(cls.in_app_read.is_(False))
        
        query = query.order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_pending_send(cls, db: Session) -> List['Notification']:
        """Busca notificações pendentes de envio"""
        now = datetime.utcnow()
        
        return db.query(cls).filter(
            cls.sent_at.is_(None),
            cls.expires_at > now,
            ((cls.scheduled_for.is_(None)) | (cls.scheduled_for <= now)),
            cls.is_deleted.is_(False)
        ).order_by(cls.priority.desc(), cls.created_at.asc()).all()
    
    @classmethod
    def get_by_type(cls, db: Session, notification_type: NotificationType,
                   start_date: datetime = None, end_date: datetime = None) -> List['Notification']:
        """Busca notificações por tipo"""
        query = db.query(cls).filter(
            cls.notification_type == notification_type.value,
            cls.is_deleted.is_(False)
        )
        
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_urgent(cls, db: Session) -> List['Notification']:
        """Busca notificações urgentes não lidas"""
        return db.query(cls).filter(
            cls.urgent.is_(True),
            cls.in_app_read.is_(False),
            cls.is_deleted.is_(False)
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_failed_deliveries(cls, db: Session) -> List['Notification']:
        """Busca notificações com falha na entrega"""
        return db.query(cls).filter(
            ((cls.email_error.isnot(None)) | 
             (cls.sms_error.isnot(None)) | 
             (cls.push_error.isnot(None))),
            cls.is_deleted.is_(False)
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_for_retry(cls, db: Session) -> List['Notification']:
        """Busca notificações elegíveis para retry"""
        now = datetime.utcnow()
        
        query = db.query(cls).filter(
            cls.sent_at.is_(None),
            cls.expires_at > now,
            cls.is_deleted.is_(False)
        )
        
        # Filtrar por tentativas
        results = []
        for notification in query.all():
            current_retries = int(notification.retry_count or "0")
            max_retries = int(notification.max_retries or "3")
            if current_retries < max_retries:
                results.append(notification)
        
        return results
    
    @classmethod
    def get_expiring_soon(cls, db: Session, hours: int = 2) -> List['Notification']:
        """Busca notificações que expiram em breve"""
        expiry_threshold = datetime.utcnow() + timedelta(hours=hours)
        
        return db.query(cls).filter(
            cls.expires_at <= expiry_threshold,
            cls.expires_at > datetime.utcnow(),
            cls.in_app_read.is_(False),
            cls.is_deleted.is_(False)
        ).order_by(cls.expires_at.asc()).all()
    
    # === MÉTODOS DE ANÁLISE ===
    
    @classmethod
    def get_engagement_stats(cls, db: Session, days: int = 30) -> Dict[str, Any]:
        """Calcula estatísticas de engajamento"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        notifications = db.query(cls).filter(
            cls.sent_at >= start_date,
            cls.is_deleted.is_(False)
        ).all()
        
        if not notifications:
            return {"total": 0, "engagement_rate": 0}
        
        total = len(notifications)
        read_count = sum(1 for n in notifications if n.in_app_read)
        action_count = sum(1 for n in notifications if n.action_taken)
        email_opened = sum(1 for n in notifications if n.email_opened)
        
        return {
            "total": total,
            "read_count": read_count,
            "action_count": action_count,
            "email_opened": email_opened,
            "read_rate": read_count / total,
            "action_rate": action_count / total if total > 0 else 0,
            "email_open_rate": email_opened / total if total > 0 else 0,
            "period_days": days
        }
    
    # === MÉTODOS DE LIFECYCLE ===
    
    def __init__(self, **kwargs):
        """Inicialização da notificação"""
        super().__init__(**kwargs)
        
        # Gerar código se não fornecido
        if not self.notification_code:
            self.notification_code = self._generate_notification_code()
        
        # Definir expiração padrão
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Canais padrão
        if not self.channels:
            self.channels = ["in-app"]
    
    def _generate_notification_code(self) -> str:
        """Gera código único da notificação"""
        import random
        import string
        
        # Formato: NOT + ano + mês + 8 dígitos
        now = datetime.now()
        year_month = f"{now.year}{now.month:02d}"
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        return f"NOT{year_month}{random_chars}"
    
    def to_dict(self, exclude: Optional[List[str]] = None, include_relationships: bool = False):
        """
        Converte para dicionário
        
        Args:
            exclude: Campos para excluir
            include_relationships: Se deve incluir dados relacionados
            
        Returns:
            Dicionário com dados da notificação
        """
        result = super().to_dict(exclude)
        
        # Adicionar propriedades calculadas
        result.update({
            'is_read': self.is_read,
            'is_sent': self.is_sent,
            'is_expired': self.is_expired,
            'is_scheduled': self.is_scheduled,
            'should_send_now': self.should_send_now,
            'delivery_status': self.delivery_status,
            'engagement_score': self.engagement_score,
            'days_since_sent': self.days_since_sent
        })
        
        # Incluir dados relacionados se solicitado
        if include_relationships:
            if hasattr(self, 'user') and self.user:
                result['user_data'] = self.user.to_dict(include_sensitive=False)
            if hasattr(self, 'sender') and self.sender:
                result['sender_data'] = self.sender.to_dict(include_sensitive=False)
        
        return result