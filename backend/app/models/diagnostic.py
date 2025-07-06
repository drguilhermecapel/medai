"""
Modelo de diagnóstico do sistema MedAI
Define diagnósticos médicos gerados por IA e revisados por profissionais
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid_property import hybrid_property

from app.models.base import AuditableModel, StatusMixin, MetadataMixin
from app.core.constants import (
    DiagnosticStatus, DiagnosticCategory, Priority, 
    ClinicalUrgency, AnalysisStatus, ModelType
)


class Diagnostic(AuditableModel, StatusMixin, MetadataMixin):
    """
    Modelo de diagnóstico médico
    
    Representa diagnósticos gerados por IA e validados por profissionais médicos.
    Inclui confiança da IA, revisão médica e recomendações de tratamento.
    """
    
    __tablename__ = "diagnostics"
    
    # === RELACIONAMENTOS ===
    exam_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Exame que originou o diagnóstico"
    )
    
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Paciente do diagnóstico"
    )
    
    ai_physician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Médico responsável pela IA"
    )
    
    reviewing_physician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Médico revisor do diagnóstico"
    )
    
    approving_physician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Médico que aprovou o diagnóstico final"
    )
    
    # === INFORMAÇÕES BÁSICAS ===
    diagnostic_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Código único do diagnóstico"
    )
    
    title = Column(
        String(255),
        nullable=False,
        doc="Título do diagnóstico"
    )
    
    summary = Column(
        Text,
        nullable=True,
        doc="Resumo executivo do diagnóstico"
    )
    
    # === STATUS E CATEGORIA ===
    diagnostic_status = Column(
        String(50),
        default=DiagnosticStatus.PENDING.value,
        nullable=False,
        index=True,
        doc="Status atual do diagnóstico"
    )
    
    category = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Categoria do diagnóstico"
    )
    
    clinical_urgency = Column(
        String(20),
        default=ClinicalUrgency.ROUTINE.value,
        nullable=False,
        doc="Urgência clínica"
    )
    
    priority = Column(
        String(20),
        default=Priority.NORMAL.value,
        nullable=False,
        doc="Prioridade do diagnóstico"
    )
    
    # === ANÁLISE DE IA ===
    ai_model_used = Column(
        String(100),
        nullable=True,
        doc="Modelo de IA utilizado"
    )
    
    ai_model_version = Column(
        String(20),
        nullable=True,
        doc="Versão do modelo de IA"
    )
    
    ai_analysis_status = Column(
        String(50),
        default=AnalysisStatus.QUEUED.value,
        doc="Status da análise de IA"
    )
    
    ai_started_at = Column(
        DateTime,
        nullable=True,
        doc="Início da análise de IA"
    )
    
    ai_completed_at = Column(
        DateTime,
        nullable=True,
        doc="Conclusão da análise de IA"
    )
    
    ai_processing_time = Column(
        Numeric(8, 3),
        nullable=True,
        doc="Tempo de processamento em segundos"
    )
    
    # === RESULTADOS DA IA ===
    ai_primary_diagnosis = Column(
        String(255),
        nullable=True,
        doc="Diagnóstico principal da IA"
    )
    
    ai_confidence = Column(
        Numeric(5, 4),
        nullable=True,
        doc="Confiança da IA (0.0 a 1.0)"
    )
    
    ai_confidence_level = Column(
        String(20),
        nullable=True,
        doc="Nível de confiança (alta, média, baixa)"
    )
    
    ai_differential_diagnoses = Column(
        JSONB,
        default=list,
        doc="Diagnósticos diferenciais com probabilidades"
    )
    
    ai_findings = Column(
        JSONB,
        default=list,
        doc="Achados identificados pela IA"
    )
    
    ai_features_detected = Column(
        JSONB,
        default=list,
        doc="Características detectadas pela IA"
    )
    
    ai_anomalies = Column(
        JSONB,
        default=list,
        doc="Anomalias identificadas"
    )
    
    ai_measurements = Column(
        JSONB,
        default=dict,
        doc="Medições realizadas pela IA"
    )
    
    ai_interpretation = Column(
        Text,
        nullable=True,
        doc="Interpretação detalhada da IA"
    )
    
    ai_recommendations = Column(
        JSONB,
        default=list,
        doc="Recomendações da IA"
    )
    
    # === REVISÃO MÉDICA ===
    physician_reviewed_at = Column(
        DateTime,
        nullable=True,
        doc="Data da revisão médica"
    )
    
    physician_diagnosis = Column(
        String(255),
        nullable=True,
        doc="Diagnóstico do médico revisor"
    )
    
    physician_agrees_with_ai = Column(
        Boolean,
        nullable=True,
        doc="Médico concorda com a IA"
    )
    
    physician_confidence = Column(
        Numeric(5, 4),
        nullable=True,
        doc="Confiança do médico (0.0 a 1.0)"
    )
    
    physician_findings = Column(
        Text,
        nullable=True,
        doc="Achados adicionais do médico"
    )
    
    physician_interpretation = Column(
        Text,
        nullable=True,
        doc="Interpretação do médico"
    )
    
    physician_notes = Column(
        Text,
        nullable=True,
        doc="Observações do médico revisor"
    )
    
    discrepancy_notes = Column(
        Text,
        nullable=True,
        doc="Notas sobre discrepâncias entre IA e médico"
    )
    
    # === DIAGNÓSTICO FINAL ===
    final_diagnosis = Column(
        String(255),
        nullable=True,
        doc="Diagnóstico final aprovado"
    )
    
    final_confidence = Column(
        Numeric(5, 4),
        nullable=True,
        doc="Confiança final"
    )
    
    final_interpretation = Column(
        Text,
        nullable=True,
        doc="Interpretação final"
    )
    
    final_recommendations = Column(
        JSONB,
        default=list,
        doc="Recomendações finais"
    )
    
    approved_at = Column(
        DateTime,
        nullable=True,
        doc="Data de aprovação final"
    )
    
    # === CÓDIGOS MÉDICOS ===
    icd10_codes = Column(
        ARRAY(String),
        default=list,
        doc="Códigos CID-10"
    )
    
    snomed_codes = Column(
        ARRAY(String),
        default=list,
        doc="Códigos SNOMED CT"
    )
    
    medical_codes = Column(
        JSONB,
        default=dict,
        doc="Outros códigos médicos"
    )
    
    # === TRATAMENTO E FOLLOW-UP ===
    treatment_urgency = Column(
        String(20),
        nullable=True,
        doc="Urgência do tratamento"
    )
    
    requires_immediate_action = Column(
        Boolean,
        default=False,
        doc="Requer ação imediata"
    )
    
    requires_specialist = Column(
        Boolean,
        default=False,
        doc="Requer especialista"
    )
    
    specialist_type = Column(
        String(100),
        nullable=True,
        doc="Tipo de especialista necessário"
    )
    
    follow_up_required = Column(
        Boolean,
        default=False,
        doc="Requer acompanhamento"
    )
    
    follow_up_timeframe = Column(
        String(50),
        nullable=True,
        doc="Prazo para acompanhamento"
    )
    
    additional_tests_needed = Column(
        JSONB,
        default=list,
        doc="Exames adicionais necessários"
    )
    
    # === QUALIDADE E VALIDAÇÃO ===
    quality_score = Column(
        Numeric(3, 2),
        nullable=True,
        doc="Score de qualidade (0.0 a 1.0)"
    )
    
    validation_status = Column(
        String(50),
        nullable=True,
        doc="Status de validação"
    )
    
    validation_notes = Column(
        Text,
        nullable=True,
        doc="Notas de validação"
    )
    
    peer_reviewed = Column(
        Boolean,
        default=False,
        doc="Revisado por pares"
    )
    
    peer_review_notes = Column(
        Text,
        nullable=True,
        doc="Notas da revisão por pares"
    )
    
    # === EDUCAÇÃO E PESQUISA ===
    educational_case = Column(
        Boolean,
        default=False,
        doc="Caso educativo"
    )
    
    research_case = Column(
        Boolean,
        default=False,
        doc="Caso de pesquisa"
    )
    
    anonymized_data = Column(
        JSONB,
        default=dict,
        doc="Dados anonimizados para pesquisa"
    )
    
    # === RELACIONAMENTOS ===
    exam = relationship("Exam", foreign_keys=[exam_id])
    patient = relationship("Patient", foreign_keys=[patient_id])
    ai_physician = relationship("User", foreign_keys=[ai_physician_id])
    reviewing_physician = relationship("User", foreign_keys=[reviewing_physician_id])
    approving_physician = relationship("User", foreign_keys=[approving_physician_id])
    
    # === ÍNDICES ===
    __table_args__ = (
        Index('ix_diagnostics_code', 'diagnostic_code'),
        Index('ix_diagnostics_patient_status', 'patient_id', 'diagnostic_status'),
        Index('ix_diagnostics_exam_category', 'exam_id', 'category'),
        Index('ix_diagnostics_ai_confidence', 'ai_confidence'),
        Index('ix_diagnostics_urgency', 'clinical_urgency'),
        Index('ix_diagnostics_approved_date', 'approved_at'),
        Index('ix_diagnostics_ai_model', 'ai_model_used'),
        Index('ix_diagnostics_final_diagnosis', 'final_diagnosis'),
    )
    
    # === PROPRIEDADES CALCULADAS ===
    
    @hybrid_property
    def is_ai_completed(self) -> bool:
        """Verifica se a análise de IA foi concluída"""
        return self.ai_analysis_status == AnalysisStatus.COMPLETED.value
    
    @hybrid_property
    def is_physician_reviewed(self) -> bool:
        """Verifica se foi revisado por médico"""
        return self.physician_reviewed_at is not None
    
    @hybrid_property
    def is_approved(self) -> bool:
        """Verifica se está aprovado"""
        return self.diagnostic_status == DiagnosticStatus.CONFIRMED.value
    
    @hybrid_property
    def has_high_confidence(self) -> bool:
        """Verifica se tem alta confiança"""
        return self.ai_confidence and self.ai_confidence >= 0.8
    
    @hybrid_property
    def requires_urgent_action(self) -> bool:
        """Verifica se requer ação urgente"""
        return (
            self.clinical_urgency in [ClinicalUrgency.URGENT.value, ClinicalUrgency.EMERGENCY.value] or
            self.requires_immediate_action
        )
    
    @hybrid_property
    def ai_processing_duration(self) -> Optional[float]:
        """Retorna duração do processamento de IA em segundos"""
        if self.ai_processing_time:
            return float(self.ai_processing_time)
        elif self.ai_started_at and self.ai_completed_at:
            duration = self.ai_completed_at - self.ai_started_at
            return duration.total_seconds()
        return None
    
    @hybrid_property
    def physician_agreement_rate(self) -> Optional[bool]:
        """Taxa de concordância do médico com a IA"""
        return self.physician_agrees_with_ai
    
    @hybrid_property
    def days_to_review(self) -> Optional[int]:
        """Dias até a revisão médica"""
        if self.ai_completed_at and self.physician_reviewed_at:
            return (self.physician_reviewed_at - self.ai_completed_at).days
        return None
    
    # === MÉTODOS DE GESTÃO DE STATUS ===
    
    def start_ai_analysis(self, model_name: str, model_version: str) -> None:
        """Inicia análise de IA"""
        self.ai_analysis_status = AnalysisStatus.PROCESSING.value
        self.ai_model_used = model_name
        self.ai_model_version = model_version
        self.ai_started_at = datetime.utcnow()
        self.diagnostic_status = DiagnosticStatus.AI_ANALYSIS.value
    
    def complete_ai_analysis(self, results: Dict[str, Any]) -> None:
        """Completa análise de IA"""
        self.ai_completed_at = datetime.utcnow()
        self.ai_analysis_status = AnalysisStatus.COMPLETED.value
        self.diagnostic_status = DiagnosticStatus.AI_COMPLETED.value
        
        # Calcular tempo de processamento
        if self.ai_started_at:
            duration = self.ai_completed_at - self.ai_started_at
            self.ai_processing_time = duration.total_seconds()
        
        # Atualizar resultados da IA
        self.ai_primary_diagnosis = results.get('primary_diagnosis')
        self.ai_confidence = results.get('confidence')
        self.ai_differential_diagnoses = results.get('differential_diagnoses', [])
        self.ai_findings = results.get('findings', [])
        self.ai_features_detected = results.get('features', [])
        self.ai_anomalies = results.get('anomalies', [])
        self.ai_measurements = results.get('measurements', {})
        self.ai_interpretation = results.get('interpretation')
        self.ai_recommendations = results.get('recommendations', [])
        
        # Determinar nível de confiança
        if self.ai_confidence:
            if self.ai_confidence >= 0.9:
                self.ai_confidence_level = "alta"
            elif self.ai_confidence >= 0.7:
                self.ai_confidence_level = "média"
            else:
                self.ai_confidence_level = "baixa"
    
    def fail_ai_analysis(self, error_message: str) -> None:
        """Marca falha na análise de IA"""
        self.ai_analysis_status = AnalysisStatus.ERROR.value
        self.diagnostic_status = DiagnosticStatus.REQUIRES_REVISION.value
        self.physician_notes = f"Erro na análise de IA: {error_message}"
    
    def start_physician_review(self, physician_id: uuid.UUID) -> None:
        """Inicia revisão médica"""
        self.reviewing_physician_id = physician_id
        self.diagnostic_status = DiagnosticStatus.DOCTOR_REVIEW.value
    
    def complete_physician_review(
        self, 
        physician_diagnosis: str,
        agrees_with_ai: bool,
        confidence: float,
        notes: str = None
    ) -> None:
        """Completa revisão médica"""
        self.physician_reviewed_at = datetime.utcnow()
        self.physician_diagnosis = physician_diagnosis
        self.physician_agrees_with_ai = agrees_with_ai
        self.physician_confidence = confidence
        
        if notes:
            self.physician_notes = notes
        
        # Se não concorda com IA, adicionar notas de discrepância
        if not agrees_with_ai:
            self.discrepancy_notes = f"Discrepância identificada em {datetime.utcnow().isoformat()}"
    
    def approve_diagnostic(self, approving_physician_id: uuid.UUID) -> None:
        """Aprova diagnóstico final"""
        self.approving_physician_id = approving_physician_id
        self.approved_at = datetime.utcnow()
        self.diagnostic_status = DiagnosticStatus.CONFIRMED.value
        
        # Se médico concorda com IA, usar diagnóstico da IA
        if self.physician_agrees_with_ai:
            self.final_diagnosis = self.ai_primary_diagnosis
            self.final_confidence = self.ai_confidence
            self.final_interpretation = self.ai_interpretation
            self.final_recommendations = self.ai_recommendations
        else:
            # Usar diagnóstico do médico
            self.final_diagnosis = self.physician_diagnosis
            self.final_confidence = self.physician_confidence
            self.final_interpretation = self.physician_interpretation
    
    def reject_diagnostic(self, reason: str) -> None:
        """Rejeita diagnóstico"""
        self.diagnostic_status = DiagnosticStatus.REJECTED.value
        self.physician_notes = f"Rejeitado: {reason}"
    
    def require_revision(self, reason: str) -> None:
        """Marca como requerendo revisão"""
        self.diagnostic_status = DiagnosticStatus.REQUIRES_REVISION.value
        self.validation_notes = f"Requer revisão: {reason}"
    
    # === MÉTODOS DE GESTÃO DE DADOS ===
    
    def add_differential_diagnosis(self, diagnosis: str, probability: float) -> None:
        """Adiciona diagnóstico diferencial"""
        if not self.ai_differential_diagnoses:
            self.ai_differential_diagnoses = []
        
        differential = {
            "diagnosis": diagnosis,
            "probability": probability,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.ai_differential_diagnoses.append(differential)
    
    def add_finding(self, finding: str, confidence: float = None, location: str = None) -> None:
        """Adiciona achado"""
        if not self.ai_findings:
            self.ai_findings = []
        
        finding_data = {
            "description": finding,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if confidence:
            finding_data["confidence"] = confidence
        if location:
            finding_data["location"] = location
        
        self.ai_findings.append(finding_data)
    
    def add_recommendation(self, recommendation: str, urgency: str = "normal") -> None:
        """Adiciona recomendação"""
        if not self.ai_recommendations:
            self.ai_recommendations = []
        
        rec_data = {
            "description": recommendation,
            "urgency": urgency,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.ai_recommendations.append(rec_data)
    
    def add_icd10_code(self, code: str) -> None:
        """Adiciona código CID-10"""
        if not self.icd10_codes:
            self.icd10_codes = []
        if code not in self.icd10_codes:
            self.icd10_codes.append(code)
    
    def add_snomed_code(self, code: str) -> None:
        """Adiciona código SNOMED CT"""
        if not self.snomed_codes:
            self.snomed_codes = []
        if code not in self.snomed_codes:
            self.snomed_codes.append(code)
    
    def set_quality_metrics(self, accuracy: float, precision: float, recall: float) -> None:
        """Define métricas de qualidade"""
        quality_data = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Calcular score geral
        self.quality_score = (accuracy + precision + recall) / 3
        
        # Armazenar métricas detalhadas
        if not self.metadata:
            self.metadata = {}
        self.metadata["quality_metrics"] = quality_data
    
    # === MÉTODOS DE CONSULTA ===
    
    @classmethod
    def get_by_code(cls, db: Session, diagnostic_code: str) -> Optional['Diagnostic']:
        """Busca diagnóstico por código"""
        return db.query(cls).filter(
            cls.diagnostic_code == diagnostic_code,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_exam(cls, db: Session, exam_id: uuid.UUID) -> Optional['Diagnostic']:
        """Busca diagnóstico por exame"""
        return db.query(cls).filter(
            cls.exam_id == exam_id,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_patient(cls, db: Session, patient_id: uuid.UUID, limit: int = None) -> List['Diagnostic']:
        """Busca diagnósticos de um paciente"""
        query = db.query(cls).filter(
            cls.patient_id == patient_id,
            cls.is_deleted.is_(False)
        ).order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_pending_review(cls, db: Session) -> List['Diagnostic']:
        """Busca diagnósticos pendentes de revisão"""
        return db.query(cls).filter(
            cls.diagnostic_status == DiagnosticStatus.AI_COMPLETED.value,
            cls.is_deleted.is_(False)
        ).order_by(cls.ai_completed_at.asc()).all()
    
    @classmethod
    def get_high_confidence_ai(cls, db: Session, threshold: float = 0.9) -> List['Diagnostic']:
        """Busca diagnósticos com alta confiança da IA"""
        return db.query(cls).filter(
            cls.ai_confidence >= threshold,
            cls.is_deleted.is_(False)
        ).order_by(cls.ai_confidence.desc()).all()
    
    @classmethod
    def get_discrepant_cases(cls, db: Session) -> List['Diagnostic']:
        """Busca casos com discrepância entre IA e médico"""
        return db.query(cls).filter(
            cls.physician_agrees_with_ai.is_(False),
            cls.is_deleted.is_(False)
        ).order_by(cls.physician_reviewed_at.desc()).all()
    
    @classmethod
    def get_by_model(cls, db: Session, model_name: str, model_version: str = None) -> List['Diagnostic']:
        """Busca diagnósticos por modelo de IA"""
        query = db.query(cls).filter(
            cls.ai_model_used == model_name,
            cls.is_deleted.is_(False)
        )
        
        if model_version:
            query = query.filter(cls.ai_model_version == model_version)
        
        return query.order_by(cls.ai_completed_at.desc()).all()
    
    @classmethod
    def get_urgent_cases(cls, db: Session) -> List['Diagnostic']:
        """Busca casos urgentes"""
        return db.query(cls).filter(
            cls.clinical_urgency.in_([
                ClinicalUrgency.URGENT.value, 
                ClinicalUrgency.EMERGENCY.value, 
                ClinicalUrgency.IMMEDIATE.value
            ]),
            cls.diagnostic_status.in_([
                DiagnosticStatus.AI_COMPLETED.value,
                DiagnosticStatus.DOCTOR_REVIEW.value
            ]),
            cls.is_deleted.is_(False)
        ).order_by(cls.clinical_urgency.desc(), cls.ai_completed_at.asc()).all()
    
    # === MÉTODOS DE ANÁLISE ===
    
    @classmethod
    def get_accuracy_stats(cls, db: Session, model_name: str = None) -> Dict[str, Any]:
        """Calcula estatísticas de acurácia"""
        query = db.query(cls).filter(
            cls.physician_agrees_with_ai.isnot(None),
            cls.is_deleted.is_(False)
        )
        
        if model_name:
            query = query.filter(cls.ai_model_used == model_name)
        
        diagnostics = query.all()
        
        if not diagnostics:
            return {"total": 0, "accuracy": 0, "agreement_rate": 0}
        
        total = len(diagnostics)
        agreements = sum(1 for d in diagnostics if d.physician_agrees_with_ai)
        
        accuracy_scores = [float(d.quality_score) for d in diagnostics if d.quality_score]
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        
        return {
            "total": total,
            "agreements": agreements,
            "disagreements": total - agreements,
            "agreement_rate": agreements / total,
            "average_accuracy": avg_accuracy,
            "model_name": model_name
        }
    
    # === MÉTODOS DE LIFECYCLE ===
    
    def __init__(self, **kwargs):
        """Inicialização do diagnóstico"""
        super().__init__(**kwargs)
        
        # Gerar código do diagnóstico se não fornecido
        if not self.diagnostic_code:
            self.diagnostic_code = self._generate_diagnostic_code()
    
    def _generate_diagnostic_code(self) -> str:
        """Gera código único do diagnóstico"""
        import random
        import string
        
        # Formato: DG + ano + mês + 8 dígitos aleatórios
        now = datetime.now()
        year_month = f"{now.year}{now.month:02d}"
        random_digits = ''.join(random.choices(string.digits, k=8))
        
        return f"DG{year_month}{random_digits}"
    
    def to_dict(self, exclude: Optional[List[str]] = None, include_relationships: bool = False):
        """
        Converte para dicionário
        
        Args:
            exclude: Campos para excluir
            include_relationships: Se deve incluir dados relacionados
            
        Returns:
            Dicionário com dados do diagnóstico
        """
        result = super().to_dict(exclude)
        
        # Adicionar propriedades calculadas
        result.update({
            'is_ai_completed': self.is_ai_completed,
            'is_physician_reviewed': self.is_physician_reviewed,
            'is_approved': self.is_approved,
            'has_high_confidence': self.has_high_confidence,
            'requires_urgent_action': self.requires_urgent_action,
            'ai_processing_duration': self.ai_processing_duration,
            'physician_agreement_rate': self.physician_agreement_rate,
            'days_to_review': self.days_to_review
        })
        
        # Incluir dados relacionados se solicitado
        if include_relationships:
            if hasattr(self, 'exam') and self.exam:
                result['exam_data'] = self.exam.to_dict()
            if hasattr(self, 'patient') and self.patient:
                result['patient_data'] = self.patient.to_dict()
            if hasattr(self, 'reviewing_physician') and self.reviewing_physician:
                result['reviewing_physician_data'] = self.reviewing_physician.to_dict(include_sensitive=False)
        
        return result