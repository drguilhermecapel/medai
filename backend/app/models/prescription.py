"""
Modelo de prescrição médica do sistema MedAI
Define prescrições digitais com medicamentos e instruções
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid_property import hybrid_property

from app.models.base import AuditableModel, StatusMixin, MetadataMixin
from app.core.constants import PrescriptionStatus, Priority


class Prescription(AuditableModel, StatusMixin, MetadataMixin):
    """
    Modelo de prescrição médica digital
    
    Representa prescrições emitidas por médicos com medicamentos,
    dosagens, instruções e controle de validade
    """
    
    __tablename__ = "prescriptions"
    
    # === RELACIONAMENTOS ===
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Paciente da prescrição"
    )
    
    physician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        doc="Médico prescritor"
    )
    
    diagnostic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("diagnostics.id"),
        nullable=True,
        doc="Diagnóstico relacionado"
    )
    
    exam_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exams.id"),
        nullable=True,
        doc="Exame relacionado"
    )
    
    # === INFORMAÇÕES BÁSICAS ===
    prescription_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Código único da prescrição"
    )
    
    prescription_number = Column(
        String(30),
        unique=True,
        nullable=False,
        doc="Número sequencial da prescrição"
    )
    
    title = Column(
        String(255),
        nullable=False,
        doc="Título da prescrição"
    )
    
    description = Column(
        Text,
        nullable=True,
        doc="Descrição/observações gerais"
    )
    
    # === STATUS E VALIDADE ===
    prescription_status = Column(
        String(50),
        default=PrescriptionStatus.DRAFT.value,
        nullable=False,
        index=True,
        doc="Status da prescrição"
    )
    
    priority = Column(
        String(20),
        default=Priority.NORMAL.value,
        nullable=False,
        doc="Prioridade da prescrição"
    )
    
    # === DATAS ===
    prescribed_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Data de prescrição"
    )
    
    valid_until = Column(
        DateTime,
        nullable=False,
        doc="Válida até"
    )
    
    dispensed_date = Column(
        DateTime,
        nullable=True,
        doc="Data de dispensação"
    )
    
    completed_date = Column(
        DateTime,
        nullable=True,
        doc="Data de conclusão do tratamento"
    )
    
    cancelled_date = Column(
        DateTime,
        nullable=True,
        doc="Data de cancelamento"
    )
    
    # === INFORMAÇÕES CLÍNICAS ===
    diagnosis = Column(
        String(255),
        nullable=True,
        doc="Diagnóstico que motivou a prescrição"
    )
    
    clinical_indication = Column(
        Text,
        nullable=True,
        doc="Indicação clínica"
    )
    
    treatment_goal = Column(
        Text,
        nullable=True,
        doc="Objetivo do tratamento"
    )
    
    contraindications = Column(
        ARRAY(String),
        default=list,
        doc="Contraindicações"
    )
    
    allergies_considered = Column(
        ARRAY(String),
        default=list,
        doc="Alergias consideradas"
    )
    
    drug_interactions = Column(
        JSONB,
        default=list,
        doc="Interações medicamentosas identificadas"
    )
    
    # === MEDICAMENTOS ===
    medications = Column(
        JSONB,
        default=list,
        doc="Lista de medicamentos prescritos"
    )
    
    total_medications = Column(
        Integer,
        default=0,
        doc="Total de medicamentos"
    )
    
    controlled_substances = Column(
        Boolean,
        default=False,
        doc="Contém substâncias controladas"
    )
    
    generic_allowed = Column(
        Boolean,
        default=True,
        doc="Permite medicamentos genéricos"
    )
    
    # === INSTRUÇÕES GERAIS ===
    general_instructions = Column(
        Text,
        nullable=True,
        doc="Instruções gerais ao paciente"
    )
    
    diet_recommendations = Column(
        Text,
        nullable=True,
        doc="Recomendações dietéticas"
    )
    
    lifestyle_recommendations = Column(
        Text,
        nullable=True,
        doc="Recomendações de estilo de vida"
    )
    
    warning_signs = Column(
        ARRAY(String),
        default=list,
        doc="Sinais de alerta"
    )
    
    emergency_instructions = Column(
        Text,
        nullable=True,
        doc="Instruções em caso de emergência"
    )
    
    # === ACOMPANHAMENTO ===
    follow_up_required = Column(
        Boolean,
        default=False,
        doc="Requer acompanhamento"
    )
    
    follow_up_date = Column(
        DateTime,
        nullable=True,
        doc="Data de retorno"
    )
    
    follow_up_instructions = Column(
        Text,
        nullable=True,
        doc="Instruções para o retorno"
    )
    
    monitoring_parameters = Column(
        JSONB,
        default=list,
        doc="Parâmetros a serem monitorados"
    )
    
    lab_tests_required = Column(
        ARRAY(String),
        default=list,
        doc="Exames laboratoriais necessários"
    )
    
    # === CUSTOS E COBERTURA ===
    estimated_cost = Column(
        Numeric(10, 2),
        nullable=True,
        doc="Custo estimado total"
    )
    
    insurance_coverage = Column(
        Boolean,
        nullable=True,
        doc="Cobertura pelo plano de saúde"
    )
    
    insurance_notes = Column(
        Text,
        nullable=True,
        doc="Observações sobre cobertura"
    )
    
    # === ASSINATURA DIGITAL ===
    digital_signature = Column(
        Text,
        nullable=True,
        doc="Assinatura digital do médico"
    )
    
    signature_timestamp = Column(
        DateTime,
        nullable=True,
        doc="Timestamp da assinatura"
    )
    
    certificate_info = Column(
        JSONB,
        default=dict,
        doc="Informações do certificado digital"
    )
    
    # === FARMÁCIA E DISPENSAÇÃO ===
    preferred_pharmacy = Column(
        String(255),
        nullable=True,
        doc="Farmácia preferencial"
    )
    
    pharmacy_contact = Column(
        String(255),
        nullable=True,
        doc="Contato da farmácia"
    )
    
    dispensed_by = Column(
        String(255),
        nullable=True,
        doc="Dispensado por (farmacêutico)"
    )
    
    dispensing_notes = Column(
        Text,
        nullable=True,
        doc="Observações da dispensação"
    )
    
    # === COMPLIANCE E ADESÃO ===
    adherence_monitoring = Column(
        Boolean,
        default=False,
        doc="Monitoramento de adesão"
    )
    
    adherence_score = Column(
        Numeric(3, 2),
        nullable=True,
        doc="Score de adesão (0.0 a 1.0)"
    )
    
    missed_doses = Column(
        Integer,
        default=0,
        doc="Doses perdidas reportadas"
    )
    
    patient_feedback = Column(
        Text,
        nullable=True,
        doc="Feedback do paciente"
    )
    
    # === OBSERVAÇÕES ===
    physician_notes = Column(
        Text,
        nullable=True,
        doc="Observações do médico"
    )
    
    pharmacist_notes = Column(
        Text,
        nullable=True,
        doc="Observações do farmacêutico"
    )
    
    patient_questions = Column(
        Text,
        nullable=True,
        doc="Dúvidas do paciente"
    )
    
    # === RELACIONAMENTOS ===
    patient = relationship("Patient", foreign_keys=[patient_id])
    physician = relationship("User", foreign_keys=[physician_id])
    diagnostic = relationship("Diagnostic", foreign_keys=[diagnostic_id])
    exam = relationship("Exam", foreign_keys=[exam_id])
    
    # === ÍNDICES ===
    __table_args__ = (
        Index('ix_prescriptions_code', 'prescription_code'),
        Index('ix_prescriptions_number', 'prescription_number'),
        Index('ix_prescriptions_patient_status', 'patient_id', 'prescription_status'),
        Index('ix_prescriptions_physician_date', 'physician_id', 'prescribed_date'),
        Index('ix_prescriptions_validity', 'valid_until'),
        Index('ix_prescriptions_controlled', 'controlled_substances'),
        Index('ix_prescriptions_follow_up', 'follow_up_date'),
    )
    
    # === PROPRIEDADES CALCULADAS ===
    
    @hybrid_property
    def is_active(self) -> bool:
        """Verifica se a prescrição está ativa"""
        return self.prescription_status == PrescriptionStatus.ACTIVE.value
    
    @hybrid_property
    def is_expired(self) -> bool:
        """Verifica se a prescrição expirou"""
        return datetime.utcnow() > self.valid_until
    
    @hybrid_property
    def is_dispensed(self) -> bool:
        """Verifica se foi dispensada"""
        return self.dispensed_date is not None
    
    @hybrid_property
    def days_until_expiry(self) -> int:
        """Dias até expirar"""
        if self.valid_until:
            delta = self.valid_until - datetime.utcnow()
            return max(0, delta.days)
        return 0
    
    @hybrid_property
    def days_since_prescribed(self) -> int:
        """Dias desde a prescrição"""
        delta = datetime.utcnow() - self.prescribed_date
        return delta.days
    
    @hybrid_property
    def has_interactions(self) -> bool:
        """Verifica se tem interações medicamentosas"""
        return bool(self.drug_interactions)
    
    @hybrid_property
    def requires_monitoring(self) -> bool:
        """Verifica se requer monitoramento"""
        return bool(self.monitoring_parameters or self.lab_tests_required)
    
    @hybrid_property
    def medication_names(self) -> List[str]:
        """Lista nomes dos medicamentos"""
        if self.medications:
            return [med.get('name', '') for med in self.medications]
        return []
    
    # === MÉTODOS DE GESTÃO DE STATUS ===
    
    def activate(self) -> None:
        """Ativa a prescrição"""
        self.prescription_status = PrescriptionStatus.ACTIVE.value
        if not self.prescribed_date:
            self.prescribed_date = datetime.utcnow()
        
        # Definir validade padrão se não definida
        if not self.valid_until:
            self.valid_until = datetime.utcnow() + timedelta(days=30)
    
    def dispense(self, pharmacist: str, pharmacy: str = None) -> None:
        """Marca como dispensada"""
        self.dispensed_date = datetime.utcnow()
        self.dispensed_by = pharmacist
        if pharmacy:
            self.preferred_pharmacy = pharmacy
    
    def complete(self) -> None:
        """Marca como completa"""
        self.prescription_status = PrescriptionStatus.COMPLETED.value
        self.completed_date = datetime.utcnow()
    
    def cancel(self, reason: str) -> None:
        """Cancela a prescrição"""
        self.prescription_status = PrescriptionStatus.CANCELLED.value
        self.cancelled_date = datetime.utcnow()
        self.physician_notes = f"Cancelada: {reason}"
    
    def expire(self) -> None:
        """Marca como expirada"""
        self.prescription_status = PrescriptionStatus.EXPIRED.value
    
    def sign_digitally(self, signature: str, certificate_data: Dict[str, Any]) -> None:
        """Assina digitalmente a prescrição"""
        self.digital_signature = signature
        self.signature_timestamp = datetime.utcnow()
        self.certificate_info = certificate_data
    
    # === MÉTODOS DE GESTÃO DE MEDICAMENTOS ===
    
    def add_medication(self, medication_data: Dict[str, Any]) -> None:
        """
        Adiciona medicamento à prescrição
        
        Args:
            medication_data: Dados do medicamento
        """
        if not self.medications:
            self.medications = []
        
        # Validar dados obrigatórios
        required_fields = ['name', 'dosage', 'frequency', 'duration']
        for field in required_fields:
            if field not in medication_data:
                raise ValueError(f"Campo obrigatório: {field}")
        
        # Adicionar timestamp e ID único
        medication_data.update({
            'id': str(uuid.uuid4()),
            'added_at': datetime.utcnow().isoformat(),
            'status': 'active'
        })
        
        self.medications.append(medication_data)
        self.total_medications = len(self.medications)
        
        # Verificar se é substância controlada
        if medication_data.get('controlled_substance', False):
            self.controlled_substances = True
    
    def remove_medication(self, medication_id: str) -> bool:
        """
        Remove medicamento da prescrição
        
        Args:
            medication_id: ID do medicamento
            
        Returns:
            True se removido com sucesso
        """
        if self.medications:
            original_count = len(self.medications)
            self.medications = [
                med for med in self.medications 
                if med.get('id') != medication_id
            ]
            
            if len(self.medications) < original_count:
                self.total_medications = len(self.medications)
                
                # Revalidar substâncias controladas
                self.controlled_substances = any(
                    med.get('controlled_substance', False) 
                    for med in self.medications
                )
                return True
        
        return False
    
    def update_medication(self, medication_id: str, updates: Dict[str, Any]) -> bool:
        """
        Atualiza medicamento na prescrição
        
        Args:
            medication_id: ID do medicamento
            updates: Atualizações a aplicar
            
        Returns:
            True se atualizado com sucesso
        """
        if self.medications:
            for med in self.medications:
                if med.get('id') == medication_id:
                    med.update(updates)
                    med['updated_at'] = datetime.utcnow().isoformat()
                    return True
        
        return False
    
    def get_medication(self, medication_id: str) -> Optional[Dict[str, Any]]:
        """Obtém medicamento específico"""
        if self.medications:
            return next(
                (med for med in self.medications if med.get('id') == medication_id),
                None
            )
        return None
    
    # === MÉTODOS DE INTERAÇÕES ===
    
    def check_drug_interactions(self) -> List[Dict[str, Any]]:
        """Verifica interações medicamentosas"""
        interactions = []
        
        if not self.medications or len(self.medications) < 2:
            return interactions
        
        # Implementar lógica de verificação de interações
        # Aqui seria integrado com base de dados de interações
        
        medication_names = [med.get('name', '').lower() for med in self.medications]
        
        # Exemplo de interações conhecidas (implementar com base real)
        known_interactions = {
            ('warfarina', 'aspirina'): 'Risco aumentado de sangramento',
            ('digoxina', 'furosemida'): 'Risco de toxicidade da digoxina',
        }
        
        for i, med1 in enumerate(medication_names):
            for med2 in medication_names[i+1:]:
                interaction_key = tuple(sorted([med1, med2]))
                if interaction_key in known_interactions:
                    interactions.append({
                        'medication_1': med1,
                        'medication_2': med2,
                        'severity': 'moderate',
                        'description': known_interactions[interaction_key],
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        self.drug_interactions = interactions
        return interactions
    
    def add_contraindication(self, contraindication: str) -> None:
        """Adiciona contraindicação"""
        if not self.contraindications:
            self.contraindications = []
        if contraindication not in self.contraindications:
            self.contraindications.append(contraindication)
    
    def add_allergy_consideration(self, allergy: str) -> None:
        """Adiciona alergia considerada"""
        if not self.allergies_considered:
            self.allergies_considered = []
        if allergy not in self.allergies_considered:
            self.allergies_considered.append(allergy)
    
    # === MÉTODOS DE MONITORAMENTO ===
    
    def add_monitoring_parameter(self, parameter: str, frequency: str, target_range: str = None) -> None:
        """Adiciona parâmetro de monitoramento"""
        if not self.monitoring_parameters:
            self.monitoring_parameters = []
        
        monitor_data = {
            'parameter': parameter,
            'frequency': frequency,
            'added_at': datetime.utcnow().isoformat()
        }
        
        if target_range:
            monitor_data['target_range'] = target_range
        
        self.monitoring_parameters.append(monitor_data)
    
    def add_lab_test(self, test_name: str) -> None:
        """Adiciona exame laboratorial necessário"""
        if not self.lab_tests_required:
            self.lab_tests_required = []
        if test_name not in self.lab_tests_required:
            self.lab_tests_required.append(test_name)
    
    def update_adherence(self, score: float, missed_doses: int = 0, feedback: str = None) -> None:
        """Atualiza dados de adesão"""
        self.adherence_score = max(0.0, min(1.0, score))
        self.missed_doses = missed_doses
        if feedback:
            self.patient_feedback = feedback
        self.adherence_monitoring = True
    
    # === MÉTODOS DE CONSULTA ===
    
    @classmethod
    def get_by_code(cls, db: Session, prescription_code: str) -> Optional['Prescription']:
        """Busca prescrição por código"""
        return db.query(cls).filter(
            cls.prescription_code == prescription_code,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_patient(cls, db: Session, patient_id: uuid.UUID, active_only: bool = False) -> List['Prescription']:
        """Busca prescrições de um paciente"""
        query = db.query(cls).filter(
            cls.patient_id == patient_id,
            cls.is_deleted.is_(False)
        )
        
        if active_only:
            query = query.filter(cls.prescription_status == PrescriptionStatus.ACTIVE.value)
        
        return query.order_by(cls.prescribed_date.desc()).all()
    
    @classmethod
    def get_by_physician(cls, db: Session, physician_id: uuid.UUID, limit: int = None) -> List['Prescription']:
        """Busca prescrições de um médico"""
        query = db.query(cls).filter(
            cls.physician_id == physician_id,
            cls.is_deleted.is_(False)
        ).order_by(cls.prescribed_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_expiring_soon(cls, db: Session, days: int = 7) -> List['Prescription']:
        """Busca prescrições que expiram em breve"""
        expiry_threshold = datetime.utcnow() + timedelta(days=days)
        
        return db.query(cls).filter(
            cls.prescription_status == PrescriptionStatus.ACTIVE.value,
            cls.valid_until <= expiry_threshold,
            cls.valid_until > datetime.utcnow(),
            cls.is_deleted.is_(False)
        ).order_by(cls.valid_until.asc()).all()
    
    @classmethod
    def get_controlled_substances(cls, db: Session) -> List['Prescription']:
        """Busca prescrições com substâncias controladas"""
        return db.query(cls).filter(
            cls.controlled_substances.is_(True),
            cls.is_deleted.is_(False)
        ).order_by(cls.prescribed_date.desc()).all()
    
    @classmethod
    def get_requiring_follow_up(cls, db: Session) -> List['Prescription']:
        """Busca prescrições que requerem acompanhamento"""
        return db.query(cls).filter(
            cls.follow_up_required.is_(True),
            cls.follow_up_date <= datetime.utcnow(),
            cls.prescription_status == PrescriptionStatus.ACTIVE.value,
            cls.is_deleted.is_(False)
        ).order_by(cls.follow_up_date.asc()).all()
    
    # === MÉTODOS DE VALIDAÇÃO ===
    
    def validate_prescription(self) -> List[str]:
        """
        Valida dados da prescrição
        
        Returns:
            Lista de erros de validação
        """
        errors = []
        
        # Validações obrigatórias
        if not self.patient_id:
            errors.append("Paciente é obrigatório")
        
        if not self.physician_id:
            errors.append("Médico prescritor é obrigatório")
        
        if not self.medications:
            errors.append("Pelo menos um medicamento é obrigatório")
        
        # Validar medicamentos
        for i, med in enumerate(self.medications or []):
            required_fields = ['name', 'dosage', 'frequency']
            for field in required_fields:
                if not med.get(field):
                    errors.append(f"Medicamento {i+1}: {field} é obrigatório")
        
        # Validar datas
        if self.valid_until and self.valid_until <= self.prescribed_date:
            errors.append("Data de validade deve ser posterior à prescrição")
        
        if self.follow_up_date and self.follow_up_date <= self.prescribed_date:
            errors.append("Data de retorno deve ser posterior à prescrição")
        
        return errors
    
    # === MÉTODOS DE LIFECYCLE ===
    
    def __init__(self, **kwargs):
        """Inicialização da prescrição"""
        super().__init__(**kwargs)
        
        # Gerar código se não fornecido
        if not self.prescription_code:
            self.prescription_code = self._generate_prescription_code()
        
        # Gerar número se não fornecido
        if not self.prescription_number:
            self.prescription_number = self._generate_prescription_number()
        
        # Definir validade padrão
        if not self.valid_until:
            self.valid_until = datetime.utcnow() + timedelta(days=30)
    
    def _generate_prescription_code(self) -> str:
        """Gera código único da prescrição"""
        import random
        import string
        
        # Formato: RX + ano + mês + 8 dígitos
        now = datetime.now()
        year_month = f"{now.year}{now.month:02d}"
        random_digits = ''.join(random.choices(string.digits, k=8))
        
        return f"RX{year_month}{random_digits}"
    
    def _generate_prescription_number(self) -> str:
        """Gera número sequencial da prescrição"""
        import random
        
        # Formato simples: YYYYMMDD + 6 dígitos
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        random_digits = ''.join(random.choices("0123456789", k=6))
        
        return f"{date_str}{random_digits}"
    
    def to_dict(self, exclude: Optional[List[str]] = None, include_medications_detail: bool = True):
        """
        Converte para dicionário
        
        Args:
            exclude: Campos para excluir
            include_medications_detail: Se deve incluir detalhes dos medicamentos
            
        Returns:
            Dicionário com dados da prescrição
        """
        result = super().to_dict(exclude)
        
        # Adicionar propriedades calculadas
        result.update({
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'is_dispensed': self.is_dispensed,
            'days_until_expiry': self.days_until_expiry,
            'days_since_prescribed': self.days_since_prescribed,
            'has_interactions': self.has_interactions,
            'requires_monitoring': self.requires_monitoring,
            'medication_names': self.medication_names
        })
        
        # Simplificar medicamentos se solicitado
        if not include_medications_detail and self.medications:
            result['medications_summary'] = [
                {
                    'name': med.get('name'),
                    'dosage': med.get('dosage'),
                    'frequency': med.get('frequency')
                }
                for med in self.medications
            ]
        
        return result