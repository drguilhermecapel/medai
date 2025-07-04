"""
Modelo de diagnóstico médico do sistema MedAI
"""
from sqlalchemy import Column, String, ForeignKey, Integer, JSON, Enum, DateTime, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel
from app.core.constants import DiagnosticStatus, Priority


class Diagnostic(BaseModel):
    """Modelo de diagnóstico médico"""
    
    __tablename__ = "diagnostics"
    __table_args__ = {"extend_existing": True}
    
    # Exame relacionado
    exam_id = Column(Integer, ForeignKey("exams.id"), unique=True, nullable=False)
    exam = relationship("Exam", back_populates="diagnostic")
    
    # Médico responsável
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor = relationship("User", back_populates="diagnostics")
    
    # Status e prioridade
    status = Column(Enum(DiagnosticStatus), default=DiagnosticStatus.PENDING, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    
    # Diagnóstico
    diagnosis = Column(Text, nullable=True)
    diagnosis_code = Column(String(10), nullable=True)  # CID-10
    findings = Column(JSON, nullable=True, default=list)
    recommendations = Column(JSON, nullable=True, default=list)
    
    # IA/ML
    ai_prediction = Column(String(255), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_findings = Column(JSON, nullable=True)
    ai_processed_at = Column(DateTime, nullable=True)
    
    # Alertas e observações
    alerts = Column(JSON, nullable=True, default=list)
    notes = Column(Text, nullable=True)
    
    # Flags
    is_critical = Column(Boolean, default=False, nullable=False)
    requires_followup = Column(Boolean, default=False, nullable=False)
    followup_date = Column(DateTime, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Diagnostic(id={self.id}, exam_id={self.exam_id}, status={self.status.value})>"
    
    @property
    def is_completed(self) -> bool:
        """Verifica se o diagnóstico está completo"""
        return self.status in [DiagnosticStatus.COMPLETED, DiagnosticStatus.REVIEWED]
    
    @property
    def processing_time(self) -> float:
        """Calcula tempo de processamento em minutos"""
        if not self.completed_at or not self.started_at:
            return 0.0
        
        delta = self.completed_at - self.started_at
        return delta.total_seconds() / 60
    
    def start_processing(self):
        """Marca início do processamento"""
        self.status = DiagnosticStatus.PROCESSING
        self.started_at = datetime.utcnow()
    
    def complete_processing(self):
        """Marca fim do processamento"""
        self.status = DiagnosticStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def mark_as_reviewed(self, doctor_id: int):
        """Marca como revisado por médico"""
        self.status = DiagnosticStatus.REVIEWED
        self.reviewed_at = datetime.utcnow()
        self.doctor_id = doctor_id
    
    def add_finding(self, finding: dict):
        """
        Adiciona um achado ao diagnóstico
        
        Args:
            finding: Dict com description, severity, location
        """
        if not self.findings:
            self.findings = []
        
        self.findings.append({
            "description": finding.get("description"),
            "severity": finding.get("severity", "low"),
            "location": finding.get("location"),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_recommendation(self, recommendation: str, priority: str = "medium"):
        """Adiciona uma recomendação"""
        if not self.recommendations:
            self.recommendations = []
        
        self.recommendations.append({
            "text": recommendation,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_alert(self, alert: dict):
        """
        Adiciona um alerta
        
        Args:
            alert: Dict com type, message, severity
        """
        if not self.alerts:
            self.alerts = []
        
        self.alerts.append({
            "type": alert.get("type"),
            "message": alert.get("message"),
            "severity": alert.get("severity", "medium"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Se alerta crítico, marca diagnóstico como crítico
        if alert.get("severity") == "critical":
            self.is_critical = True
            self.priority = Priority.CRITICAL
    
    def set_ai_results(self, prediction: str, confidence: float, findings: list = None):
        """Define resultados da análise por IA"""
        self.ai_prediction = prediction
        self.ai_confidence = confidence
        self.ai_findings = findings or []
        self.ai_processed_at = datetime.utcnow()
    
    def schedule_followup(self, followup_date: datetime, reason: str = None):
        """Agenda acompanhamento"""
        self.requires_followup = True
        self.followup_date = followup_date
        
        if reason:
            self.add_recommendation(
                f"Acompanhamento agendado para {followup_date.strftime('%d/%m/%Y')}: {reason}",
                priority="high"
            )