"""
Modelo de exame médico do sistema MedAI
Define exames médicos realizados em pacientes (excluindo ECG)
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid_property import hybrid_property

from app.models.base import AuditableModel, StatusMixin, MetadataMixin
from app.core.constants import ExamType, ExamStatus, Priority


class Exam(AuditableModel, StatusMixin, MetadataMixin):
    """
    Modelo de exame médico
    
    Representa exames realizados em pacientes:
    - Raio-X
    - Tomografia
    - Ressonância Magnética
    - Ultrassom
    - Exames laboratoriais
    - Endoscopia
    - Mamografia
    - Densitometria óssea
    - Patologia
    - Dermatologia
    """
    
    __tablename__ = "exams"
    
    # === RELACIONAMENTOS ===
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Paciente que realizou o exame"
    )
    
    physician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        doc="Médico solicitante"
    )
    
    technician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Técnico responsável pela execução"
    )
    
    # === INFORMAÇÕES BÁSICAS DO EXAME ===
    exam_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Código único do exame"
    )
    
    exam_type = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Tipo do exame"
    )
    
    exam_subtype = Column(
        String(100),
        nullable=True,
        doc="Subtipo específico do exame"
    )
    
    title = Column(
        String(255),
        nullable=False,
        doc="Título/nome do exame"
    )
    
    description = Column(
        Text,
        nullable=True,
        doc="Descrição detalhada do exame"
    )
    
    # === DATAS E AGENDAMENTO ===
    scheduled_date = Column(
        DateTime,
        nullable=True,
        doc="Data agendada para o exame"
    )
    
    performed_date = Column(
        DateTime,
        nullable=True,
        doc="Data de execução do exame"
    )
    
    completed_date = Column(
        DateTime,
        nullable=True,
        doc="Data de conclusão do exame"
    )
    
    report_date = Column(
        DateTime,
        nullable=True,
        doc="Data do laudo"
    )
    
    # === STATUS E PRIORIDADE ===
    exam_status = Column(
        String(50),
        default=ExamStatus.PENDING.value,
        nullable=False,
        index=True,
        doc="Status atual do exame"
    )
    
    priority = Column(
        String(20),
        default=Priority.NORMAL.value,
        nullable=False,
        doc="Prioridade do exame"
    )
    
    urgent = Column(
        Boolean,
        default=False,
        doc="Exame urgente"
    )
    
    # === INFORMAÇÕES CLÍNICAS ===
    clinical_indication = Column(
        Text,
        nullable=True,
        doc="Indicação clínica para o exame"
    )
    
    suspected_diagnosis = Column(
        String(255),
        nullable=True,
        doc="Suspeita diagnóstica"
    )
    
    relevant_history = Column(
        Text,
        nullable=True,
        doc="História clínica relevante"
    )
    
    symptoms = Column(
        ARRAY(String),
        default=list,
        doc="Sintomas relacionados"
    )
    
    # === PREPARAÇÃO E INSTRUÇÕES ===
    preparation_instructions = Column(
        Text,
        nullable=True,
        doc="Instruções de preparo"
    )
    
    requires_fasting = Column(
        Boolean,
        default=False,
        doc="Requer jejum"
    )
    
    requires_sedation = Column(
        Boolean,
        default=False,
        doc="Requer sedação"
    )
    
    requires_contrast = Column(
        Boolean,
        default=False,
        doc="Requer contraste"
    )
    
    contrast_type = Column(
        String(100),
        nullable=True,
        doc="Tipo de contraste utilizado"
    )
    
    special_instructions = Column(
        Text,
        nullable=True,
        doc="Instruções especiais"
    )
    
    # === DADOS TÉCNICOS ===
    body_part = Column(
        String(100),
        nullable=True,
        doc="Parte do corpo examinada"
    )
    
    exam_position = Column(
        String(50),
        nullable=True,
        doc="Posição do paciente durante o exame"
    )
    
    exam_view = Column(
        String(50),
        nullable=True,
        doc="Projeção/vista do exame"
    )
    
    technique_parameters = Column(
        JSONB,
        default=dict,
        doc="Parâmetros técnicos do exame"
    )
    
    equipment_info = Column(
        JSONB,
        default=dict,
        doc="Informações do equipamento utilizado"
    )
    
    # === RESULTADOS E DADOS ===
    exam_data = Column(
        JSONB,
        default=dict,
        doc="Dados específicos do exame"
    )
    
    measurements = Column(
        JSONB,
        default=dict,
        doc="Medições realizadas"
    )
    
    findings = Column(
        Text,
        nullable=True,
        doc="Achados do exame"
    )
    
    preliminary_report = Column(
        Text,
        nullable=True,
        doc="Relatório preliminar"
    )
    
    final_report = Column(
        Text,
        nullable=True,
        doc="Laudo final"
    )
    
    conclusion = Column(
        Text,
        nullable=True,
        doc="Conclusão do exame"
    )
    
    # === ARQUIVOS E IMAGENS ===
    file_paths = Column(
        ARRAY(String),
        default=list,
        doc="Caminhos dos arquivos do exame"
    )
    
    image_paths = Column(
        ARRAY(String),
        default=list,
        doc="Caminhos das imagens"
    )
    
    dicom_files = Column(
        ARRAY(String),
        default=list,
        doc="Arquivos DICOM"
    )
    
    # === QUALIDADE E VALIDAÇÃO ===
    image_quality = Column(
        String(20),
        nullable=True,
        doc="Qualidade da imagem (boa, regular, ruim)"
    )
    
    technical_quality = Column(
        String(20),
        nullable=True,
        doc="Qualidade técnica do exame"
    )
    
    artifacts_present = Column(
        Boolean,
        default=False,
        doc="Presença de artefatos"
    )
    
    artifacts_description = Column(
        Text,
        nullable=True,
        doc="Descrição dos artefatos"
    )
    
    needs_repeat = Column(
        Boolean,
        default=False,
        doc="Necessita repetir o exame"
    )
    
    repeat_reason = Column(
        String(255),
        nullable=True,
        doc="Motivo para repetir"
    )
    
    # === CUSTOS E FATURAMENTO ===
    estimated_cost = Column(
        Numeric(10, 2),
        nullable=True,
        doc="Custo estimado"
    )
    
    actual_cost = Column(
        Numeric(10, 2),
        nullable=True,
        doc="Custo real"
    )
    
    insurance_covered = Column(
        Boolean,
        default=False,
        doc="Coberto pelo plano"
    )
    
    billing_info = Column(
        JSONB,
        default=dict,
        doc="Informações de faturamento"
    )
    
    # === OBSERVAÇÕES ===
    technician_notes = Column(
        Text,
        nullable=True,
        doc="Observações do técnico"
    )
    
    physician_notes = Column(
        Text,
        nullable=True,
        doc="Observações do médico"
    )
    
    patient_cooperation = Column(
        String(50),
        nullable=True,
        doc="Cooperação do paciente"
    )
    
    complications = Column(
        Text,
        nullable=True,
        doc="Complicações durante o exame"
    )
    
    # === RELACIONAMENTOS ===
    patient = relationship("Patient", foreign_keys=[patient_id])
    physician = relationship("User", foreign_keys=[physician_id])
    technician = relationship("User", foreign_keys=[technician_id])
    
    # Relacionamentos que serão definidos em outros modelos
    # diagnostics = relationship("Diagnostic", back_populates="exam")
    
    # === ÍNDICES ===
    __table_args__ = (
        Index('ix_exams_code', 'exam_code'),
        Index('ix_exams_patient_type', 'patient_id', 'exam_type'),
        Index('ix_exams_physician_date', 'physician_id', 'performed_date'),
        Index('ix_exams_status_priority', 'exam_status', 'priority'),
        Index('ix_exams_scheduled_date', 'scheduled_date'),
        Index('ix_exams_body_part', 'body_part'),
        Index('ix_exams_urgent', 'urgent'),
    )
    
    # === PROPRIEDADES CALCULADAS ===
    
    @hybrid_property
    def is_completed(self) -> bool:
        """Verifica se o exame está completo"""
        return self.exam_status == ExamStatus.COMPLETED.value
    
    @hybrid_property
    def is_urgent(self) -> bool:
        """Verifica se é urgente"""
        return self.urgent or self.priority in [Priority.URGENT.value, Priority.CRITICAL.value]
    
    @hybrid_property
    def duration_minutes(self) -> Optional[int]:
        """Calcula duração do exame em minutos"""
        if self.performed_date and self.completed_date:
            duration = self.completed_date - self.performed_date
            return int(duration.total_seconds() / 60)
        return None
    
    @hybrid_property
    def days_since_scheduled(self) -> Optional[int]:
        """Dias desde o agendamento"""
        if self.scheduled_date:
            return (datetime.utcnow() - self.scheduled_date).days
        return None
    
    @hybrid_property
    def has_files(self) -> bool:
        """Verifica se tem arquivos anexados"""
        return bool(self.file_paths or self.image_paths or self.dicom_files)
    
    @hybrid_property
    def file_count(self) -> int:
        """Conta total de arquivos"""
        count = 0
        if self.file_paths:
            count += len(self.file_paths)
        if self.image_paths:
            count += len(self.image_paths)
        if self.dicom_files:
            count += len(self.dicom_files)
        return count
    
    @hybrid_property
    def requires_preparation(self) -> bool:
        """Verifica se requer preparo"""
        return any([
            self.requires_fasting,
            self.requires_sedation,
            self.requires_contrast,
            self.preparation_instructions
        ])
    
    # === MÉTODOS DE GESTÃO DE STATUS ===
    
    def schedule(self, scheduled_date: datetime) -> None:
        """Agenda o exame"""
        self.scheduled_date = scheduled_date
        self.exam_status = ExamStatus.PENDING.value
    
    def start_exam(self, technician_id: Optional[uuid.UUID] = None) -> None:
        """Inicia o exame"""
        self.performed_date = datetime.utcnow()
        self.exam_status = ExamStatus.IN_PROGRESS.value
        if technician_id:
            self.technician_id = technician_id
    
    def complete_exam(self) -> None:
        """Completa o exame"""
        self.completed_date = datetime.utcnow()
        self.exam_status = ExamStatus.COMPLETED.value
    
    def analyze_exam(self) -> None:
        """Marca como analisado"""
        self.exam_status = ExamStatus.ANALYZED.value
    
    def review_exam(self) -> None:
        """Marca como revisado"""
        self.exam_status = ExamStatus.REVIEWED.value
        self.report_date = datetime.utcnow()
    
    def cancel_exam(self, reason: str) -> None:
        """Cancela o exame"""
        self.exam_status = ExamStatus.CANCELLED.value
        self.physician_notes = f"Cancelado: {reason}"
    
    def mark_failed(self, reason: str) -> None:
        """Marca como falhado"""
        self.exam_status = ExamStatus.FAILED.value
        self.technician_notes = f"Falhou: {reason}"
        self.needs_repeat = True
        self.repeat_reason = reason
    
    # === MÉTODOS DE GESTÃO DE ARQUIVOS ===
    
    def add_file(self, file_path: str, file_type: str = "general") -> None:
        """
        Adiciona arquivo ao exame
        
        Args:
            file_path: Caminho do arquivo
            file_type: Tipo do arquivo (general, image, dicom)
        """
        if file_type == "image":
            if not self.image_paths:
                self.image_paths = []
            if file_path not in self.image_paths:
                self.image_paths.append(file_path)
        elif file_type == "dicom":
            if not self.dicom_files:
                self.dicom_files = []
            if file_path not in self.dicom_files:
                self.dicom_files.append(file_path)
        else:
            if not self.file_paths:
                self.file_paths = []
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
    
    def remove_file(self, file_path: str) -> None:
        """Remove arquivo do exame"""
        for file_list in [self.file_paths, self.image_paths, self.dicom_files]:
            if file_list and file_path in file_list:
                file_list.remove(file_path)
    
    def get_all_files(self) -> List[str]:
        """Retorna todos os arquivos do exame"""
        all_files = []
        if self.file_paths:
            all_files.extend(self.file_paths)
        if self.image_paths:
            all_files.extend(self.image_paths)
        if self.dicom_files:
            all_files.extend(self.dicom_files)
        return all_files
    
    # === MÉTODOS DE GESTÃO DE DADOS ===
    
    def add_measurement(self, name: str, value: Any, unit: str = None) -> None:
        """
        Adiciona medição ao exame
        
        Args:
            name: Nome da medição
            value: Valor medido
            unit: Unidade de medida
        """
        if not self.measurements:
            self.measurements = {}
        
        measurement_data = {"value": value}
        if unit:
            measurement_data["unit"] = unit
        measurement_data["timestamp"] = datetime.utcnow().isoformat()
        
        self.measurements[name] = measurement_data
    
    def get_measurement(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém medição específica"""
        if self.measurements:
            return self.measurements.get(name)
        return None
    
    def set_equipment_info(self, equipment_data: Dict[str, Any]) -> None:
        """Define informações do equipamento"""
        if not self.equipment_info:
            self.equipment_info = {}
        self.equipment_info.update(equipment_data)
    
    def set_technique_parameters(self, params: Dict[str, Any]) -> None:
        """Define parâmetros técnicos"""
        if not self.technique_parameters:
            self.technique_parameters = {}
        self.technique_parameters.update(params)
    
    def add_symptom(self, symptom: str) -> None:
        """Adiciona sintoma à lista"""
        if not self.symptoms:
            self.symptoms = []
        if symptom not in self.symptoms:
            self.symptoms.append(symptom)
    
    def remove_symptom(self, symptom: str) -> None:
        """Remove sintoma da lista"""
        if self.symptoms and symptom in self.symptoms:
            self.symptoms.remove(symptom)
    
    # === MÉTODOS DE CONSULTA ===
    
    @classmethod
    def get_by_code(cls, db: Session, exam_code: str) -> Optional['Exam']:
        """Busca exame por código"""
        return db.query(cls).filter(
            cls.exam_code == exam_code,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_patient(cls, db: Session, patient_id: uuid.UUID, limit: int = None) -> List['Exam']:
        """Busca exames de um paciente"""
        query = db.query(cls).filter(
            cls.patient_id == patient_id,
            cls.is_deleted.is_(False)
        ).order_by(cls.performed_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_by_physician(cls, db: Session, physician_id: uuid.UUID, limit: int = None) -> List['Exam']:
        """Busca exames de um médico"""
        query = db.query(cls).filter(
            cls.physician_id == physician_id,
            cls.is_deleted.is_(False)
        ).order_by(cls.scheduled_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_by_status(cls, db: Session, status: ExamStatus) -> List['Exam']:
        """Busca exames por status"""
        return db.query(cls).filter(
            cls.exam_status == status.value,
            cls.is_deleted.is_(False)
        ).order_by(cls.scheduled_date.asc()).all()
    
    @classmethod
    def get_urgent_exams(cls, db: Session) -> List['Exam']:
        """Busca exames urgentes"""
        return db.query(cls).filter(
            cls.urgent.is_(True),
            cls.exam_status.in_([ExamStatus.PENDING.value, ExamStatus.IN_PROGRESS.value]),
            cls.is_deleted.is_(False)
        ).order_by(cls.scheduled_date.asc()).all()
    
    @classmethod
    def get_exams_by_type(cls, db: Session, exam_type: ExamType, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List['Exam']:
        """
        Busca exames por tipo e período
        
        Args:
            db: Sessão do banco
            exam_type: Tipo do exame
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            
        Returns:
            Lista de exames
        """
        query = db.query(cls).filter(
            cls.exam_type == exam_type.value,
            cls.is_deleted.is_(False)
        )
        
        if start_date:
            query = query.filter(cls.performed_date >= start_date)
        if end_date:
            query = query.filter(cls.performed_date <= end_date)
        
        return query.order_by(cls.performed_date.desc()).all()
    
    @classmethod
    def get_pending_reports(cls, db: Session) -> List['Exam']:
        """Busca exames com laudos pendentes"""
        return db.query(cls).filter(
            cls.exam_status == ExamStatus.COMPLETED.value,
            cls.final_report.is_(None),
            cls.is_deleted.is_(False)
        ).order_by(cls.completed_date.asc()).all()
    
    # === MÉTODOS DE VALIDAÇÃO ===
    
    def validate_exam_data(self) -> List[str]:
        """
        Valida dados do exame
        
        Returns:
            Lista de erros de validação
        """
        errors = []
        
        # Validações obrigatórias
        if not self.patient_id:
            errors.append("Paciente é obrigatório")
        
        if not self.physician_id:
            errors.append("Médico solicitante é obrigatório")
        
        if not self.exam_type:
            errors.append("Tipo de exame é obrigatório")
        
        if not self.title:
            errors.append("Título do exame é obrigatório")
        
        # Validações de datas
        if self.scheduled_date and self.performed_date:
            if self.performed_date < self.scheduled_date:
                errors.append("Data de execução não pode ser anterior ao agendamento")
        
        if self.performed_date and self.completed_date:
            if self.completed_date < self.performed_date:
                errors.append("Data de conclusão não pode ser anterior à execução")
        
        # Validações de status
        if self.exam_status == ExamStatus.COMPLETED.value and not self.performed_date:
            errors.append("Exame completo deve ter data de execução")
        
        if self.exam_status == ExamStatus.ANALYZED.value and not self.findings:
            errors.append("Exame analisado deve ter achados")
        
        return errors
    
    # === MÉTODOS DE LIFECYCLE ===
    
    def __init__(self, **kwargs):
        """Inicialização do exame"""
        super().__init__(**kwargs)
        
        # Gerar código do exame se não fornecido
        if not self.exam_code:
            self.exam_code = self._generate_exam_code()
    
    def _generate_exam_code(self) -> str:
        """Gera código único do exame"""
        import random
        import string
        
        # Formato: EX + ano + mês + 6 dígitos aleatórios
        now = datetime.now()
        year_month = f"{now.year}{now.month:02d}"
        random_digits = ''.join(random.choices(string.digits, k=6))
        
        return f"EX{year_month}{random_digits}"
    
    def to_dict(self, exclude: Optional[List[str]] = None, include_relationships: bool = False):
        """
        Converte para dicionário
        
        Args:
            exclude: Campos para excluir
            include_relationships: Se deve incluir dados relacionados
            
        Returns:
            Dicionário com dados do exame
        """
        result = super().to_dict(exclude)
        
        # Adicionar propriedades calculadas
        result.update({
            'is_completed': self.is_completed,
            'is_urgent': self.is_urgent,
            'duration_minutes': self.duration_minutes,
            'days_since_scheduled': self.days_since_scheduled,
            'has_files': self.has_files,
            'file_count': self.file_count,
            'requires_preparation': self.requires_preparation
        })
        
        # Incluir dados relacionados se solicitado
        if include_relationships:
            if hasattr(self, 'patient') and self.patient:
                result['patient_data'] = self.patient.to_dict(include_user_data=True)
            if hasattr(self, 'physician') and self.physician:
                result['physician_data'] = self.physician.to_dict(include_sensitive=False)
            if hasattr(self, 'technician') and self.technician:
                result['technician_data'] = self.technician.to_dict(include_sensitive=False)
        
        return result