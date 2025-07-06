"""
Modelo de consulta/agendamento do sistema MedAI
Define consultas médicas agendadas entre pacientes e profissionais
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid_property import hybrid_property

from app.models.base import AuditableModel, StatusMixin, MetadataMixin
from app.core.constants import AppointmentStatus, Priority


class Appointment(AuditableModel, StatusMixin, MetadataMixin):
    """
    Modelo de consulta/agendamento médico
    
    Representa consultas agendadas entre pacientes e profissionais de saúde,
    incluindo informações de agendamento, motivo e resultado da consulta
    """
    
    __tablename__ = "appointments"
    
    # === RELACIONAMENTOS ===
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Paciente da consulta"
    )
    
    physician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        doc="Médico responsável"
    )
    
    scheduled_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Usuário que agendou"
    )
    
    # === INFORMAÇÕES BÁSICAS ===
    appointment_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Código único da consulta"
    )
    
    title = Column(
        String(255),
        nullable=False,
        doc="Título da consulta"
    )
    
    appointment_type = Column(
        String(50),
        nullable=False,
        doc="Tipo de consulta"
    )
    
    specialty = Column(
        String(100),
        nullable=True,
        doc="Especialidade médica"
    )
    
    # === AGENDAMENTO ===
    scheduled_datetime = Column(
        DateTime,
        nullable=False,
        index=True,
        doc="Data e hora agendadas"
    )
    
    duration_minutes = Column(
        Integer,
        default=30,
        doc="Duração prevista em minutos"
    )
    
    end_datetime = Column(
        DateTime,
        nullable=True,
        doc="Data e hora de término calculadas"
    )
    
    # === STATUS ===
    appointment_status = Column(
        String(50),
        default=AppointmentStatus.SCHEDULED.value,
        nullable=False,
        index=True,
        doc="Status da consulta"
    )
    
    priority = Column(
        String(20),
        default=Priority.NORMAL.value,
        nullable=False,
        doc="Prioridade da consulta"
    )
    
    urgent = Column(
        Boolean,
        default=False,
        doc="Consulta urgente"
    )
    
    # === MOTIVO E DESCRIÇÃO ===
    chief_complaint = Column(
        String(255),
        nullable=True,
        doc="Queixa principal"
    )
    
    reason_for_visit = Column(
        Text,
        nullable=True,
        doc="Motivo da consulta"
    )
    
    symptoms = Column(
        JSONB,
        default=list,
        doc="Sintomas relatados"
    )
    
    medical_history_relevant = Column(
        Text,
        nullable=True,
        doc="Histórico médico relevante"
    )
    
    current_medications = Column(
        JSONB,
        default=list,
        doc="Medicações atuais"
    )
    
    # === LOCALIZAÇÃO ===
    location_type = Column(
        String(50),
        default="presencial",
        doc="Tipo de atendimento"
    )
    
    room_number = Column(
        String(20),
        nullable=True,
        doc="Número da sala"
    )
    
    building = Column(
        String(100),
        nullable=True,
        doc="Prédio/clínica"
    )
    
    address = Column(
        Text,
        nullable=True,
        doc="Endereço do atendimento"
    )
    
    # Para consultas online
    virtual_meeting_url = Column(
        String(500),
        nullable=True,
        doc="URL da reunião virtual"
    )
    
    virtual_meeting_id = Column(
        String(100),
        nullable=True,
        doc="ID da reunião virtual"
    )
    
    virtual_meeting_password = Column(
        String(50),
        nullable=True,
        doc="Senha da reunião virtual"
    )
    
    # === EXECUÇÃO DA CONSULTA ===
    checked_in_at = Column(
        DateTime,
        nullable=True,
        doc="Horário de check-in"
    )
    
    started_at = Column(
        DateTime,
        nullable=True,
        doc="Horário de início efetivo"
    )
    
    completed_at = Column(
        DateTime,
        nullable=True,
        doc="Horário de conclusão"
    )
    
    actual_duration_minutes = Column(
        Integer,
        nullable=True,
        doc="Duração real em minutos"
    )
    
    # === RESULTADOS DA CONSULTA ===
    diagnosis = Column(
        String(255),
        nullable=True,
        doc="Diagnóstico da consulta"
    )
    
    treatment_plan = Column(
        Text,
        nullable=True,
        doc="Plano de tratamento"
    )
    
    prescriptions_issued = Column(
        JSONB,
        default=list,
        doc="Prescrições emitidas"
    )
    
    exams_requested = Column(
        JSONB,
        default=list,
        doc="Exames solicitados"
    )
    
    referrals_made = Column(
        JSONB,
        default=list,
        doc="Encaminhamentos realizados"
    )
    
    follow_up_needed = Column(
        Boolean,
        default=False,
        doc="Necessário retorno"
    )
    
    follow_up_timeframe = Column(
        String(50),
        nullable=True,
        doc="Prazo para retorno"
    )
    
    next_appointment_recommended = Column(
        DateTime,
        nullable=True,
        doc="Próxima consulta recomendada"
    )
    
    # === OBSERVAÇÕES E NOTAS ===
    physician_notes = Column(
        Text,
        nullable=True,
        doc="Observações do médico"
    )
    
    patient_concerns = Column(
        Text,
        nullable=True,
        doc="Preocupações do paciente"
    )
    
    family_present = Column(
        Boolean,
        default=False,
        doc="Familiares presentes"
    )
    
    interpreter_needed = Column(
        Boolean,
        default=False,
        doc="Necessário intérprete"
    )
    
    special_needs = Column(
        Text,
        nullable=True,
        doc="Necessidades especiais"
    )
    
    # === CANCELAMENTO E REAGENDAMENTO ===
    cancelled_at = Column(
        DateTime,
        nullable=True,
        doc="Data de cancelamento"
    )
    
    cancelled_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Quem cancelou"
    )
    
    cancellation_reason = Column(
        String(255),
        nullable=True,
        doc="Motivo do cancelamento"
    )
    
    rescheduled_from_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id"),
        nullable=True,
        doc="Reagendado de qual consulta"
    )
    
    rescheduled_to_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id"),
        nullable=True,
        doc="Reagendado para qual consulta"
    )
    
    no_show = Column(
        Boolean,
        default=False,
        doc="Paciente não compareceu"
    )
    
    no_show_reason = Column(
        String(255),
        nullable=True,
        doc="Motivo da ausência"
    )
    
    # === LEMBRETES E NOTIFICAÇÕES ===
    reminder_sent = Column(
        Boolean,
        default=False,
        doc="Lembrete enviado"
    )
    
    reminder_sent_at = Column(
        DateTime,
        nullable=True,
        doc="Data do envio do lembrete"
    )
    
    confirmation_required = Column(
        Boolean,
        default=False,
        doc="Requer confirmação"
    )
    
    confirmed_at = Column(
        DateTime,
        nullable=True,
        doc="Data de confirmação"
    )
    
    confirmed_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Quem confirmou"
    )
    
    # === FATURAMENTO ===
    billable = Column(
        Boolean,
        default=True,
        doc="Consulta faturável"
    )
    
    insurance_authorization = Column(
        String(100),
        nullable=True,
        doc="Autorização do plano"
    )
    
    copay_amount = Column(
        String(20),
        nullable=True,
        doc="Valor do copagamento"
    )
    
    billing_notes = Column(
        Text,
        nullable=True,
        doc="Observações de faturamento"
    )
    
    # === RELACIONAMENTOS ===
    patient = relationship("Patient", foreign_keys=[patient_id])
    physician = relationship("User", foreign_keys=[physician_id])
    scheduled_by = relationship("User", foreign_keys=[scheduled_by_id])
    cancelled_by = relationship("User", foreign_keys=[cancelled_by_id])
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id])
    
    # Self-referencing para reagendamentos
    rescheduled_from = relationship("Appointment", foreign_keys=[rescheduled_from_id], remote_side="Appointment.id")
    rescheduled_to = relationship("Appointment", foreign_keys=[rescheduled_to_id], remote_side="Appointment.id")
    
    # === ÍNDICES ===
    __table_args__ = (
        Index('ix_appointments_code', 'appointment_code'),
        Index('ix_appointments_patient_date', 'patient_id', 'scheduled_datetime'),
        Index('ix_appointments_physician_date', 'physician_id', 'scheduled_datetime'),
        Index('ix_appointments_status_date', 'appointment_status', 'scheduled_datetime'),
        Index('ix_appointments_datetime', 'scheduled_datetime'),
        Index('ix_appointments_type', 'appointment_type'),
        Index('ix_appointments_urgent', 'urgent'),
        Index('ix_appointments_location_type', 'location_type'),
    )
    
    # === PROPRIEDADES CALCULADAS ===
    
    @hybrid_property
    def is_upcoming(self) -> bool:
        """Verifica se a consulta é futura"""
        return self.scheduled_datetime > datetime.utcnow()
    
    @hybrid_property
    def is_today(self) -> bool:
        """Verifica se a consulta é hoje"""
        today = datetime.utcnow().date()
        return self.scheduled_datetime.date() == today
    
    @hybrid_property
    def is_completed(self) -> bool:
        """Verifica se a consulta foi concluída"""
        return self.appointment_status == AppointmentStatus.COMPLETED.value
    
    @hybrid_property
    def is_cancelled(self) -> bool:
        """Verifica se a consulta foi cancelada"""
        return self.appointment_status == AppointmentStatus.CANCELLED.value
    
    @hybrid_property
    def is_virtual(self) -> bool:
        """Verifica se é consulta virtual"""
        return self.location_type in ["virtual", "telemedicina", "online"]
    
    @hybrid_property
    def minutes_until_appointment(self) -> Optional[int]:
        """Minutos até a consulta"""
        if self.scheduled_datetime > datetime.utcnow():
            delta = self.scheduled_datetime - datetime.utcnow()
            return int(delta.total_seconds() / 60)
        return None
    
    @hybrid_property
    def is_late(self) -> bool:
        """Verifica se o paciente está atrasado"""
        if (self.appointment_status in [AppointmentStatus.SCHEDULED.value, AppointmentStatus.CONFIRMED.value] and
            datetime.utcnow() > self.scheduled_datetime and not self.started_at):
            return True
        return False
    
    @hybrid_property
    def delay_minutes(self) -> Optional[int]:
        """Minutos de atraso"""
        if self.is_late:
            delta = datetime.utcnow() - self.scheduled_datetime
            return int(delta.total_seconds() / 60)
        return None
    
    @hybrid_property
    def needs_reminder(self) -> bool:
        """Verifica se precisa de lembrete"""
        if (self.appointment_status == AppointmentStatus.SCHEDULED.value and
            not self.reminder_sent and
            self.scheduled_datetime > datetime.utcnow()):
            # Enviar lembrete 24h antes
            reminder_time = self.scheduled_datetime - timedelta(hours=24)
            return datetime.utcnow() >= reminder_time
        return False
    
    # === MÉTODOS DE GESTÃO DE STATUS ===
    
    def schedule(self, scheduled_datetime: datetime, duration: int = 30) -> None:
        """Agenda a consulta"""
        self.scheduled_datetime = scheduled_datetime
        self.duration_minutes = duration
        self.end_datetime = scheduled_datetime + timedelta(minutes=duration)
        self.appointment_status = AppointmentStatus.SCHEDULED.value
    
    def confirm(self, confirmed_by_id: uuid.UUID) -> None:
        """Confirma a consulta"""
        self.appointment_status = AppointmentStatus.CONFIRMED.value
        self.confirmed_at = datetime.utcnow()
        self.confirmed_by_id = confirmed_by_id
    
    def check_in(self) -> None:
        """Faz check-in do paciente"""
        self.checked_in_at = datetime.utcnow()
        self.appointment_status = AppointmentStatus.IN_PROGRESS.value
    
    def start_appointment(self) -> None:
        """Inicia a consulta"""
        self.started_at = datetime.utcnow()
        if not self.checked_in_at:
            self.checked_in_at = self.started_at
        self.appointment_status = AppointmentStatus.IN_PROGRESS.value
    
    def complete_appointment(self, diagnosis: str = None, notes: str = None) -> None:
        """Completa a consulta"""
        self.completed_at = datetime.utcnow()
        self.appointment_status = AppointmentStatus.COMPLETED.value
        
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.actual_duration_minutes = int(duration.total_seconds() / 60)
        
        if diagnosis:
            self.diagnosis = diagnosis
        if notes:
            self.physician_notes = notes
    
    def cancel_appointment(self, cancelled_by_id: uuid.UUID, reason: str) -> None:
        """Cancela a consulta"""
        self.appointment_status = AppointmentStatus.CANCELLED.value
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by_id = cancelled_by_id
        self.cancellation_reason = reason
    
    def mark_no_show(self, reason: str = None) -> None:
        """Marca como não compareceu"""
        self.appointment_status = AppointmentStatus.NO_SHOW.value
        self.no_show = True
        if reason:
            self.no_show_reason = reason
    
    def reschedule(self, new_datetime: datetime, rescheduled_by_id: uuid.UUID) -> 'Appointment':
        """
        Reagenda a consulta criando nova
        
        Args:
            new_datetime: Nova data/hora
            rescheduled_by_id: Quem reagendou
            
        Returns:
            Nova consulta criada
        """
        # Marcar atual como reagendada
        self.appointment_status = AppointmentStatus.RESCHEDULED.value
        
        # Criar nova consulta
        new_appointment = Appointment(
            patient_id=self.patient_id,
            physician_id=self.physician_id,
            scheduled_by_id=rescheduled_by_id,
            title=self.title,
            appointment_type=self.appointment_type,
            specialty=self.specialty,
            scheduled_datetime=new_datetime,
            duration_minutes=self.duration_minutes,
            chief_complaint=self.chief_complaint,
            reason_for_visit=self.reason_for_visit,
            location_type=self.location_type,
            room_number=self.room_number,
            building=self.building,
            rescheduled_from_id=self.id
        )
        
        # Atualizar referência
        self.rescheduled_to_id = new_appointment.id
        
        return new_appointment
    
    # === MÉTODOS DE GESTÃO DE DADOS ===
    
    def add_symptom(self, symptom: str, severity: str = None, duration: str = None) -> None:
        """Adiciona sintoma"""
        if not self.symptoms:
            self.symptoms = []
        
        symptom_data = {
            'description': symptom,
            'added_at': datetime.utcnow().isoformat()
        }
        
        if severity:
            symptom_data['severity'] = severity
        if duration:
            symptom_data['duration'] = duration
        
        self.symptoms.append(symptom_data)
    
    def add_current_medication(self, medication: str, dosage: str = None) -> None:
        """Adiciona medicação atual"""
        if not self.current_medications:
            self.current_medications = []
        
        med_data = {
            'name': medication,
            'added_at': datetime.utcnow().isoformat()
        }
        
        if dosage:
            med_data['dosage'] = dosage
        
        self.current_medications.append(med_data)
    
    def add_prescription_issued(self, prescription_id: str, medication: str) -> None:
        """Adiciona prescrição emitida"""
        if not self.prescriptions_issued:
            self.prescriptions_issued = []
        
        prescription_data = {
            'prescription_id': prescription_id,
            'medication': medication,
            'issued_at': datetime.utcnow().isoformat()
        }
        
        self.prescriptions_issued.append(prescription_data)
    
    def add_exam_requested(self, exam_type: str, urgency: str = "normal") -> None:
        """Adiciona exame solicitado"""
        if not self.exams_requested:
            self.exams_requested = []
        
        exam_data = {
            'type': exam_type,
            'urgency': urgency,
            'requested_at': datetime.utcnow().isoformat()
        }
        
        self.exams_requested.append(exam_data)
    
    def add_referral(self, specialist_type: str, reason: str, urgency: str = "normal") -> None:
        """Adiciona encaminhamento"""
        if not self.referrals_made:
            self.referrals_made = []
        
        referral_data = {
            'specialist_type': specialist_type,
            'reason': reason,
            'urgency': urgency,
            'referred_at': datetime.utcnow().isoformat()
        }
        
        self.referrals_made.append(referral_data)
    
    def send_reminder(self) -> None:
        """Marca lembrete como enviado"""
        self.reminder_sent = True
        self.reminder_sent_at = datetime.utcnow()
    
    def setup_virtual_meeting(self, meeting_url: str, meeting_id: str = None, password: str = None) -> None:
        """Configura reunião virtual"""
        self.location_type = "virtual"
        self.virtual_meeting_url = meeting_url
        self.virtual_meeting_id = meeting_id
        self.virtual_meeting_password = password
    
    # === MÉTODOS DE CONSULTA ===
    
    @classmethod
    def get_by_code(cls, db: Session, appointment_code: str) -> Optional['Appointment']:
        """Busca consulta por código"""
        return db.query(cls).filter(
            cls.appointment_code == appointment_code,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_patient(cls, db: Session, patient_id: uuid.UUID, 
                      upcoming_only: bool = False, limit: int = None) -> List['Appointment']:
        """Busca consultas de um paciente"""
        query = db.query(cls).filter(
            cls.patient_id == patient_id,
            cls.is_deleted.is_(False)
        )
        
        if upcoming_only:
            query = query.filter(cls.scheduled_datetime > datetime.utcnow())
        
        query = query.order_by(cls.scheduled_datetime.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_by_physician(cls, db: Session, physician_id: uuid.UUID,
                        date_start: datetime = None, date_end: datetime = None) -> List['Appointment']:
        """Busca consultas de um médico"""
        query = db.query(cls).filter(
            cls.physician_id == physician_id,
            cls.is_deleted.is_(False)
        )
        
        if date_start:
            query = query.filter(cls.scheduled_datetime >= date_start)
        if date_end:
            query = query.filter(cls.scheduled_datetime <= date_end)
        
        return query.order_by(cls.scheduled_datetime.asc()).all()
    
    @classmethod
    def get_today_appointments(cls, db: Session, physician_id: uuid.UUID = None) -> List['Appointment']:
        """Busca consultas de hoje"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        query = db.query(cls).filter(
            cls.scheduled_datetime.between(today_start, today_end),
            cls.is_deleted.is_(False)
        )
        
        if physician_id:
            query = query.filter(cls.physician_id == physician_id)
        
        return query.order_by(cls.scheduled_datetime.asc()).all()
    
    @classmethod
    def get_pending_confirmation(cls, db: Session) -> List['Appointment']:
        """Busca consultas pendentes de confirmação"""
        return db.query(cls).filter(
            cls.appointment_status == AppointmentStatus.SCHEDULED.value,
            cls.confirmation_required.is_(True),
            cls.confirmed_at.is_(None),
            cls.scheduled_datetime > datetime.utcnow(),
            cls.is_deleted.is_(False)
        ).order_by(cls.scheduled_datetime.asc()).all()
    
    @classmethod
    def get_need_reminder(cls, db: Session) -> List['Appointment']:
        """Busca consultas que precisam de lembrete"""
        reminder_threshold = datetime.utcnow() + timedelta(hours=24)
        
        return db.query(cls).filter(
            cls.appointment_status == AppointmentStatus.SCHEDULED.value,
            cls.reminder_sent.is_(False),
            cls.scheduled_datetime <= reminder_threshold,
            cls.scheduled_datetime > datetime.utcnow(),
            cls.is_deleted.is_(False)
        ).order_by(cls.scheduled_datetime.asc()).all()
    
    @classmethod
    def check_availability(cls, db: Session, physician_id: uuid.UUID, 
                          start_time: datetime, duration_minutes: int = 30) -> bool:
        """
        Verifica disponibilidade de horário
        
        Args:
            db: Sessão do banco
            physician_id: ID do médico
            start_time: Horário de início
            duration_minutes: Duração em minutos
            
        Returns:
            True se disponível
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Buscar consultas conflitantes
        conflicting = db.query(cls).filter(
            cls.physician_id == physician_id,
            cls.appointment_status.in_([
                AppointmentStatus.SCHEDULED.value,
                AppointmentStatus.CONFIRMED.value,
                AppointmentStatus.IN_PROGRESS.value
            ]),
            # Verificar sobreposição de horários
            cls.scheduled_datetime < end_time,
            cls.end_datetime > start_time,
            cls.is_deleted.is_(False)
        ).first()
        
        return conflicting is None
    
    # === MÉTODOS DE LIFECYCLE ===
    
    def __init__(self, **kwargs):
        """Inicialização da consulta"""
        super().__init__(**kwargs)
        
        # Gerar código se não fornecido
        if not self.appointment_code:
            self.appointment_code = self._generate_appointment_code()
        
        # Calcular horário de término
        if self.scheduled_datetime and self.duration_minutes:
            self.end_datetime = self.scheduled_datetime + timedelta(minutes=self.duration_minutes)
    
    def _generate_appointment_code(self) -> str:
        """Gera código único da consulta"""
        import random
        import string
        
        # Formato: APT + ano + mês + dia + 6 dígitos
        now = datetime.now()
        date_str = f"{now.year}{now.month:02d}{now.day:02d}"
        random_digits = ''.join(random.choices(string.digits, k=6))
        
        return f"APT{date_str}{random_digits}"
    
    def to_dict(self, exclude: Optional[List[str]] = None, include_relationships: bool = False):
        """
        Converte para dicionário
        
        Args:
            exclude: Campos para excluir
            include_relationships: Se deve incluir dados relacionados
            
        Returns:
            Dicionário com dados da consulta
        """
        result = super().to_dict(exclude)
        
        # Adicionar propriedades calculadas
        result.update({
            'is_upcoming': self.is_upcoming,
            'is_today': self.is_today,
            'is_completed': self.is_completed,
            'is_cancelled': self.is_cancelled,
            'is_virtual': self.is_virtual,
            'minutes_until_appointment': self.minutes_until_appointment,
            'is_late': self.is_late,
            'delay_minutes': self.delay_minutes,
            'needs_reminder': self.needs_reminder
        })
        
        # Incluir dados relacionados se solicitado
        if include_relationships:
            if hasattr(self, 'patient') and self.patient:
                result['patient_data'] = self.patient.to_dict()
            if hasattr(self, 'physician') and self.physician:
                result['physician_data'] = self.physician.to_dict(include_sensitive=False)
        
        return result