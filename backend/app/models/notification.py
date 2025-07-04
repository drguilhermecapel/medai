"""
Modelo de notificação do sistema MedAI
"""
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import BaseModel
from app.core.constants import Priority


class NotificationType(str, enum.Enum):
    """Tipos de notificação"""
    EXAM_READY = "exam_ready"
    APPOINTMENT_REMINDER = "appointment_reminder"
    PRESCRIPTION_REMINDER = "prescription_reminder"
    DIAGNOSTIC_COMPLETE = "diagnostic_complete"
    CRITICAL_RESULT = "critical_result"
    SYSTEM_MESSAGE = "system_message"
    HEALTH_TIP = "health_tip"


class NotificationChannel(str, enum.Enum):
    """Canais de notificação"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class Notification(BaseModel):
    """Modelo de notificação"""
    
    __tablename__ = "notifications"
    __table_args__ = {"extend_existing": True}
    
    # Usuário destinatário
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="notifications")
    
    # Tipo e canal
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.IN_APP, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    
    # Conteúdo
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    action_url = Column(String(255), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Tentativas de envio
    send_attempts = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Agendamento
    scheduled_for = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type.value}, user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Verifica se a notificação expirou"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente de envio"""
        return not self.is_sent and not self.is_expired
    
    @property
    def should_send_now(self) -> bool:
        """Verifica se deve ser enviada agora"""
        if self.is_sent or self.is_expired:
            return False
        
        if self.scheduled_for:
            return datetime.utcnow() >= self.scheduled_for
        
        return True
    
    def mark_as_read(self):
        """Marca como lida"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def mark_as_sent(self):
        """Marca como enviada"""
        self.is_sent = True
        self.sent_at = datetime.utcnow()
    
    def increment_send_attempt(self, error: str = None):
        """Incrementa tentativa de envio"""
        self.send_attempts += 1
        self.last_attempt_at = datetime.utcnow()
        
        if error:
            self.error_message = error
    
    @classmethod
    def create_exam_ready_notification(cls, user_id: int, exam_id: int, exam_type: str) -> 'Notification':
        """Cria notificação de exame pronto"""
        return cls(
            user_id=user_id,
            notification_type=NotificationType.EXAM_READY,
            title="Exame Disponível",
            message=f"Seu exame de {exam_type} está pronto para visualização.",
            action_url=f"/exams/{exam_id}/result",
            priority=Priority.HIGH,
            metadata={"exam_id": exam_id, "exam_type": exam_type}
        )
    
    @classmethod
    def create_appointment_reminder(cls, user_id: int, appointment_id: int, appointment_time: datetime) -> 'Notification':
        """Cria lembrete de consulta"""
        return cls(
            user_id=user_id,
            notification_type=NotificationType.APPOINTMENT_REMINDER,
            title="Lembrete de Consulta",
            message=f"Você tem uma consulta agendada para {appointment_time.strftime('%d/%m/%Y às %H:%M')}.",
            action_url=f"/appointments/{appointment_id}",
            priority=Priority.HIGH,
            metadata={"appointment_id": appointment_id},
            scheduled_for=appointment_time
        )
    
    @classmethod
    def create_critical_result_notification(cls, doctor_id: int, patient_name: str, exam_type: str) -> 'Notification':
        """Cria notificação de resultado crítico"""
        return cls(
            user_id=doctor_id,
            notification_type=NotificationType.CRITICAL_RESULT,
            title="Resultado Crítico Detectado",
            message=f"Resultado crítico detectado no exame de {exam_type} do paciente {patient_name}.",
            priority=Priority.CRITICAL,
            channel=NotificationChannel.PUSH
        )