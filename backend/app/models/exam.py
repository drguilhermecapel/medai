"""
Modelo de exame médico do sistema MedAI
"""
from sqlalchemy import Column, String, ForeignKey, Integer, JSON, Enum, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel
from app.core.constants import ExamType, ExamStatus, Priority


class Exam(BaseModel):
    """Modelo de exame médico"""
    
    __tablename__ = "exams"
    
    # Paciente
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    patient = relationship("Patient", back_populates="exams")
    
    # Médico solicitante
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    doctor = relationship("User", back_populates="requested_exams")
    
    # Tipo e status
    exam_type = Column(Enum(ExamType), nullable=False)
    status = Column(Enum(ExamStatus), default=ExamStatus.PENDING, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    
    # Datas
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    performed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Informações do exame
    exam_code = Column(String(50), unique=True, index=True, nullable=False)
    notes = Column(Text, nullable=True)
    clinical_indication = Column(Text, nullable=True)
    
    # Resultados
    results = Column(JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)
    report = Column(Text, nullable=True)
    
    # Arquivos
    files = Column(JSON, nullable=True, default=list)
    
    # Técnico responsável
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    technician = relationship("User", foreign_keys=[technician_id])
    
    # Flags
    is_urgent = Column(Boolean, default=False, nullable=False)
    requires_fasting = Column(Boolean, default=False, nullable=False)
    requires_preparation = Column(Boolean, default=False, nullable=False)
    preparation_instructions = Column(Text, nullable=True)
    
    # Relacionamentos
    diagnostic = relationship("Diagnostic", back_populates="exam", uselist=False)
    
    def __repr__(self):
        return f"<Exam(id={self.id}, type={self.exam_type.value}, status={self.status.value})>"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.exam_code:
            self.exam_code = self.generate_exam_code()
    
    def generate_exam_code(self) -> str:
        """Gera código único para o exame"""
        import uuid
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"EX-{timestamp}-{unique_id}"
    
    @property
    def is_completed(self) -> bool:
        """Verifica se o exame está completo"""
        return self.status == ExamStatus.COMPLETED
    
    @property
    def is_pending(self) -> bool:
        """Verifica se o exame está pendente"""
        return self.status == ExamStatus.PENDING
    
    @property
    def days_since_request(self) -> int:
        """Calcula dias desde a solicitação"""
        if not self.requested_at:
            return 0
        
        delta = datetime.utcnow() - self.requested_at
        return delta.days
    
    @property
    def turnaround_time(self) -> float:
        """Calcula tempo de resposta em horas"""
        if not self.completed_at or not self.performed_at:
            return 0.0
        
        delta = self.completed_at - self.performed_at
        return delta.total_seconds() / 3600
    
    def update_status(self, new_status: ExamStatus, user_id: int = None):
        """
        Atualiza o status do exame
        
        Args:
            new_status: Novo status
            user_id: ID do usuário que está atualizando
        """
        old_status = self.status
        self.status = new_status
        
        # Atualiza timestamps baseado no status
        if new_status == ExamStatus.IN_PROGRESS:
            self.performed_at = datetime.utcnow()
            if user_id:
                self.technician_id = user_id
                
        elif new_status == ExamStatus.COMPLETED:
            self.completed_at = datetime.utcnow()
            
        elif new_status == ExamStatus.CANCELLED:
            self.completed_at = datetime.utcnow()
    
    def add_result(self, key: str, value: any):
        """Adiciona um resultado ao exame"""
        if not self.results:
            self.results = {}
        
        self.results[key] = value
    
    def add_file(self, file_info: dict):
        """
        Adiciona informação de arquivo ao exame
        
        Args:
            file_info: Dict com filename, path, size, mime_type
        """
        if not self.files:
            self.files = []
        
        self.files.append({
            "filename": file_info.get("filename"),
            "path": file_info.get("path"),
            "size": file_info.get("size"),
            "mime_type": file_info.get("mime_type"),
            "uploaded_at": datetime.utcnow().isoformat()
        })
    
    def set_preparation_required(self, instructions: str):
        """Define que o exame requer preparação"""
        self.requires_preparation = True
        self.preparation_instructions = instructions
    
    def get_status_history(self) -> list:
        """Retorna histórico de mudanças de status"""
        history = []
        
        if self.requested_at:
            history.append({
                "status": "requested",
                "timestamp": self.requested_at.isoformat()
            })
        
        if self.scheduled_at:
            history.append({
                "status": "scheduled",
                "timestamp": self.scheduled_at.isoformat()
            })
        
        if self.performed_at:
            history.append({
                "status": "in_progress",
                "timestamp": self.performed_at.isoformat()
            })
        
        if self.completed_at:
            history.append({
                "status": self.status.value,
                "timestamp": self.completed_at.isoformat()
            })
        
        return history