"""
Modelo de paciente do sistema MedAI
Define informações específicas de pacientes médicos
"""
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid_property import hybrid_property

from app.models.base import AuditableModel, StatusMixin, MetadataMixin
from app.core.constants import Gender, Priority


class Patient(AuditableModel, StatusMixin, MetadataMixin):
    """
    Modelo de paciente do sistema
    
    Contém informações médicas específicas de pacientes,
    histórico médico, informações de contato e emergência
    """
    
    __tablename__ = "patients"
    
    # === RELACIONAMENTO COM USUÁRIO ===
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referência ao usuário do sistema"
    )
    
    # === INFORMAÇÕES PESSOAIS ===
    medical_record_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Número do prontuário médico"
    )
    
    cpf = Column(
        String(14),
        unique=True,
        nullable=True,
        index=True,
        doc="CPF do paciente"
    )
    
    rg = Column(
        String(20),
        nullable=True,
        doc="RG do paciente"
    )
    
    birth_date = Column(
        Date,
        nullable=False,
        doc="Data de nascimento"
    )
    
    gender = Column(
        String(20),
        nullable=False,
        doc="Gênero do paciente"
    )
    
    nationality = Column(
        String(50),
        default="Brasileira",
        doc="Nacionalidade"
    )
    
    profession = Column(
        String(100),
        nullable=True,
        doc="Profissão do paciente"
    )
    
    education_level = Column(
        String(50),
        nullable=True,
        doc="Nível de escolaridade"
    )
    
    marital_status = Column(
        String(20),
        nullable=True,
        doc="Estado civil"
    )
    
    # === INFORMAÇÕES DE CONTATO ===
    phone_primary = Column(
        String(20),
        nullable=True,
        doc="Telefone principal"
    )
    
    phone_secondary = Column(
        String(20),
        nullable=True,
        doc="Telefone secundário"
    )
    
    email = Column(
        String(255),
        nullable=True,
        doc="Email do paciente"
    )
    
    # === ENDEREÇO ===
    address_street = Column(
        String(255),
        nullable=True,
        doc="Rua/Avenida"
    )
    
    address_number = Column(
        String(20),
        nullable=True,
        doc="Número"
    )
    
    address_complement = Column(
        String(100),
        nullable=True,
        doc="Complemento"
    )
    
    address_neighborhood = Column(
        String(100),
        nullable=True,
        doc="Bairro"
    )
    
    address_city = Column(
        String(100),
        nullable=True,
        doc="Cidade"
    )
    
    address_state = Column(
        String(2),
        nullable=True,
        doc="Estado (UF)"
    )
    
    address_zipcode = Column(
        String(10),
        nullable=True,
        doc="CEP"
    )
    
    address_country = Column(
        String(50),
        default="Brasil",
        doc="País"
    )
    
    # === CONTATO DE EMERGÊNCIA ===
    emergency_contact_name = Column(
        String(255),
        nullable=True,
        doc="Nome do contato de emergência"
    )
    
    emergency_contact_relationship = Column(
        String(50),
        nullable=True,
        doc="Relacionamento com o contato de emergência"
    )
    
    emergency_contact_phone = Column(
        String(20),
        nullable=True,
        doc="Telefone do contato de emergência"
    )
    
    emergency_contact_email = Column(
        String(255),
        nullable=True,
        doc="Email do contato de emergência"
    )
    
    # === INFORMAÇÕES MÉDICAS BÁSICAS ===
    blood_type = Column(
        String(5),
        nullable=True,
        doc="Tipo sanguíneo (A+, B-, O+, etc.)"
    )
    
    height = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Altura em metros"
    )
    
    weight = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Peso em quilogramas"
    )
    
    # === HISTÓRICO MÉDICO ===
    allergies = Column(
        ARRAY(String),
        default=list,
        doc="Lista de alergias"
    )
    
    chronic_conditions = Column(
        ARRAY(String),
        default=list,
        doc="Condições crônicas"
    )
    
    current_medications = Column(
        JSONB,
        default=list,
        doc="Medicações atuais com dosagem"
    )
    
    previous_surgeries = Column(
        JSONB,
        default=list,
        doc="Cirurgias anteriores com datas"
    )
    
    family_history = Column(
        JSONB,
        default=dict,
        doc="Histórico familiar de doenças"
    )
    
    social_history = Column(
        JSONB,
        default=dict,
        doc="Histórico social (fumo, álcool, etc.)"
    )
    
    # === INFORMAÇÕES CLÍNICAS ===
    primary_physician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Médico responsável principal"
    )
    
    insurance_info = Column(
        JSONB,
        default=dict,
        doc="Informações do plano de saúde"
    )
    
    medical_notes = Column(
        Text,
        nullable=True,
        doc="Observações médicas gerais"
    )
    
    clinical_priority = Column(
        String(20),
        default=Priority.NORMAL.value,
        doc="Prioridade clínica do paciente"
    )
    
    # === STATUS E CONFIGURAÇÕES ===
    is_active_patient = Column(
        Boolean,
        default=True,
        doc="Paciente ativo no sistema"
    )
    
    consent_data_use = Column(
        Boolean,
        default=False,
        doc="Consentimento para uso de dados"
    )
    
    consent_research = Column(
        Boolean,
        default=False,
        doc="Consentimento para pesquisa"
    )
    
    consent_date = Column(
        DateTime,
        nullable=True,
        doc="Data do consentimento"
    )
    
    # === CAMPOS DE AUDITORIA MÉDICA ===
    last_visit_date = Column(
        DateTime,
        nullable=True,
        doc="Data da última consulta"
    )
    
    next_appointment_date = Column(
        DateTime,
        nullable=True,
        doc="Data da próxima consulta"
    )
    
    registration_date = Column(
        DateTime,
        default=datetime.utcnow,
        doc="Data de cadastro no sistema"
    )
    
    # === RELACIONAMENTOS ===
    user = relationship("User", foreign_keys=[user_id])
    primary_physician = relationship("User", foreign_keys=[primary_physician_id])
    
    # Relacionamentos que serão definidos em outros modelos
    # exams = relationship("Exam", back_populates="patient")
    # appointments = relationship("Appointment", back_populates="patient")
    # prescriptions = relationship("Prescription", back_populates="patient")
    
    # === ÍNDICES ===
    __table_args__ = (
        Index('ix_patients_medical_record', 'medical_record_number'),
        Index('ix_patients_cpf', 'cpf'),
        Index('ix_patients_user_id', 'user_id'),
        Index('ix_patients_primary_physician', 'primary_physician_id'),
        Index('ix_patients_birth_date', 'birth_date'),
        Index('ix_patients_active', 'is_active_patient'),
        Index('ix_patients_priority', 'clinical_priority'),
    )
    
    # === PROPRIEDADES CALCULADAS ===
    
    @hybrid_property
    def age(self) -> int:
        """Calcula idade baseada na data de nascimento"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return 0
    
    @hybrid_property
    def age_group(self) -> str:
        """Retorna grupo etário"""
        age = self.age
        if age < 2:
            return "Bebê"
        elif age < 12:
            return "Criança"
        elif age < 18:
            return "Adolescente"
        elif age < 60:
            return "Adulto"
        else:
            return "Idoso"
    
    @hybrid_property
    def bmi(self) -> Optional[float]:
        """Calcula IMC (Índice de Massa Corporal)"""
        if self.height and self.weight and self.height > 0:
            return round(float(self.weight) / (float(self.height) ** 2), 2)
        return None
    
    @hybrid_property
    def bmi_category(self) -> Optional[str]:
        """Retorna categoria do IMC"""
        bmi = self.bmi
        if not bmi:
            return None
        
        if bmi < 18.5:
            return "Abaixo do peso"
        elif bmi < 25:
            return "Peso normal"
        elif bmi < 30:
            return "Sobrepeso"
        else:
            return "Obesidade"
    
    @hybrid_property
    def full_address(self) -> str:
        """Retorna endereço completo formatado"""
        parts = []
        
        if self.address_street:
            street_part = self.address_street
            if self.address_number:
                street_part += f", {self.address_number}"
            if self.address_complement:
                street_part += f", {self.address_complement}"
            parts.append(street_part)
        
        if self.address_neighborhood:
            parts.append(self.address_neighborhood)
        
        if self.address_city:
            city_part = self.address_city
            if self.address_state:
                city_part += f", {self.address_state}"
            parts.append(city_part)
        
        if self.address_zipcode:
            parts.append(f"CEP: {self.address_zipcode}")
        
        return " - ".join(parts)
    
    @hybrid_property
    def has_high_priority(self) -> bool:
        """Verifica se o paciente tem alta prioridade"""
        return self.clinical_priority in [Priority.HIGH.value, Priority.URGENT.value, Priority.CRITICAL.value]
    
    @hybrid_property
    def risk_factors(self) -> List[str]:
        """Lista fatores de risco baseados no perfil"""
        factors = []
        
        # Idade
        if self.age >= 65:
            factors.append("Idade avançada")
        
        # IMC
        bmi = self.bmi
        if bmi and bmi >= 30:
            factors.append("Obesidade")
        
        # Condições crônicas
        if self.chronic_conditions:
            factors.extend([f"Condição crônica: {condition}" for condition in self.chronic_conditions])
        
        # Histórico social
        if self.social_history:
            if self.social_history.get("smoking"):
                factors.append("Tabagismo")
            if self.social_history.get("alcohol_abuse"):
                factors.append("Abuso de álcool")
        
        return factors
    
    # === MÉTODOS DE GESTÃO DE DADOS ===
    
    def add_allergy(self, allergy: str) -> None:
        """Adiciona alergia à lista"""
        if not self.allergies:
            self.allergies = []
        if allergy not in self.allergies:
            self.allergies.append(allergy)
    
    def remove_allergy(self, allergy: str) -> None:
        """Remove alergia da lista"""
        if self.allergies and allergy in self.allergies:
            self.allergies.remove(allergy)
    
    def add_chronic_condition(self, condition: str) -> None:
        """Adiciona condição crônica"""
        if not self.chronic_conditions:
            self.chronic_conditions = []
        if condition not in self.chronic_conditions:
            self.chronic_conditions.append(condition)
    
    def remove_chronic_condition(self, condition: str) -> None:
        """Remove condição crônica"""
        if self.chronic_conditions and condition in self.chronic_conditions:
            self.chronic_conditions.remove(condition)
    
    def add_medication(self, medication: Dict[str, Any]) -> None:
        """
        Adiciona medicação atual
        
        Args:
            medication: Dict com nome, dosagem, frequência, etc.
        """
        if not self.current_medications:
            self.current_medications = []
        
        # Verificar se medicação já existe
        for med in self.current_medications:
            if med.get("name") == medication.get("name"):
                med.update(medication)
                return
        
        self.current_medications.append(medication)
    
    def remove_medication(self, medication_name: str) -> None:
        """Remove medicação da lista atual"""
        if self.current_medications:
            self.current_medications = [
                med for med in self.current_medications 
                if med.get("name") != medication_name
            ]
    
    def add_surgery(self, surgery: Dict[str, Any]) -> None:
        """
        Adiciona cirurgia ao histórico
        
        Args:
            surgery: Dict com tipo, data, hospital, etc.
        """
        if not self.previous_surgeries:
            self.previous_surgeries = []
        self.previous_surgeries.append(surgery)
    
    def update_insurance_info(self, insurance_data: Dict[str, Any]) -> None:
        """Atualiza informações do plano de saúde"""
        if not self.insurance_info:
            self.insurance_info = {}
        self.insurance_info.update(insurance_data)
    
    def update_social_history(self, social_data: Dict[str, Any]) -> None:
        """Atualiza histórico social"""
        if not self.social_history:
            self.social_history = {}
        self.social_history.update(social_data)
    
    def update_family_history(self, family_data: Dict[str, Any]) -> None:
        """Atualiza histórico familiar"""
        if not self.family_history:
            self.family_history = {}
        self.family_history.update(family_data)
    
    # === MÉTODOS DE CONSENTIMENTO ===
    
    def give_consent(self, data_use: bool = True, research: bool = False) -> None:
        """
        Registra consentimento do paciente
        
        Args:
            data_use: Consentimento para uso de dados
            research: Consentimento para pesquisa
        """
        self.consent_data_use = data_use
        self.consent_research = research
        self.consent_date = datetime.utcnow()
    
    def revoke_consent(self) -> None:
        """Revoga consentimentos"""
        self.consent_data_use = False
        self.consent_research = False
        self.consent_date = datetime.utcnow()
    
    # === MÉTODOS DE CONSULTA ===
    
    @classmethod
    def get_by_medical_record(cls, db: Session, medical_record: str) -> Optional['Patient']:
        """Busca paciente por número do prontuário"""
        return db.query(cls).filter(
            cls.medical_record_number == medical_record,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_cpf(cls, db: Session, cpf: str) -> Optional['Patient']:
        """Busca paciente por CPF"""
        return db.query(cls).filter(
            cls.cpf == cpf,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_user_id(cls, db: Session, user_id: uuid.UUID) -> Optional['Patient']:
        """Busca paciente por ID do usuário"""
        return db.query(cls).filter(
            cls.user_id == user_id,
            cls.is_deleted.is_(False)
        ).first()
    
    @classmethod
    def get_by_physician(cls, db: Session, physician_id: uuid.UUID) -> List['Patient']:
        """Busca pacientes de um médico específico"""
        return db.query(cls).filter(
            cls.primary_physician_id == physician_id,
            cls.is_active_patient.is_(True),
            cls.is_deleted.is_(False)
        ).all()
    
    @classmethod
    def search_patients(cls, db: Session, search_term: str, limit: int = 50) -> List['Patient']:
        """
        Busca pacientes por termo
        
        Args:
            db: Sessão do banco
            search_term: Termo para buscar
            limit: Limite de resultados
            
        Returns:
            Lista de pacientes encontrados
        """
        # Buscar no prontuário, CPF, nome (via relacionamento)
        query = db.query(cls).join(cls.user).filter(
            cls.is_deleted.is_(False)
        )
        
        # Filtros de busca
        search_filter = (
            cls.medical_record_number.ilike(f"%{search_term}%") |
            cls.cpf.ilike(f"%{search_term}%") |
            cls.user.has(
                cls.user.first_name.ilike(f"%{search_term}%") |
                cls.user.last_name.ilike(f"%{search_term}%") |
                cls.user.email.ilike(f"%{search_term}%")
            )
        )
        
        return query.filter(search_filter).limit(limit).all()
    
    @classmethod
    def get_high_priority_patients(cls, db: Session) -> List['Patient']:
        """Retorna pacientes de alta prioridade"""
        return db.query(cls).filter(
            cls.clinical_priority.in_([Priority.HIGH.value, Priority.URGENT.value, Priority.CRITICAL.value]),
            cls.is_active_patient.is_(True),
            cls.is_deleted.is_(False)
        ).all()
    
    @classmethod
    def get_patients_by_age_group(cls, db: Session, min_age: int, max_age: int) -> List['Patient']:
        """
        Busca pacientes por faixa etária
        
        Args:
            db: Sessão do banco
            min_age: Idade mínima
            max_age: Idade máxima
            
        Returns:
            Lista de pacientes na faixa etária
        """
        from datetime import date, timedelta
        
        today = date.today()
        max_birth_date = today - timedelta(days=min_age * 365)
        min_birth_date = today - timedelta(days=(max_age + 1) * 365)
        
        return db.query(cls).filter(
            cls.birth_date.between(min_birth_date, max_birth_date),
            cls.is_deleted.is_(False)
        ).all()
    
    # === MÉTODOS DE VALIDAÇÃO ===
    
    def validate_patient_data(self) -> List[str]:
        """
        Valida dados do paciente
        
        Returns:
            Lista de erros de validação
        """
        errors = []
        
        # Validações obrigatórias
        if not self.medical_record_number:
            errors.append("Número do prontuário é obrigatório")
        
        if not self.birth_date:
            errors.append("Data de nascimento é obrigatória")
        
        if not self.gender:
            errors.append("Gênero é obrigatório")
        
        # Validações de formato
        if self.cpf and len(self.cpf.replace(".", "").replace("-", "")) != 11:
            errors.append("CPF deve ter 11 dígitos")
        
        if self.email and "@" not in self.email:
            errors.append("Email inválido")
        
        # Validações de valores
        if self.height and (self.height < 0.3 or self.height > 3.0):
            errors.append("Altura deve estar entre 30cm e 3m")
        
        if self.weight and (self.weight < 0.5 or self.weight > 500):
            errors.append("Peso deve estar entre 0.5kg e 500kg")
        
        return errors
    
    # === MÉTODOS DE LIFECYCLE ===
    
    def __init__(self, **kwargs):
        """Inicialização do paciente"""
        super().__init__(**kwargs)
        
        # Gerar número do prontuário se não fornecido
        if not self.medical_record_number:
            self.medical_record_number = self._generate_medical_record_number()
    
    def _generate_medical_record_number(self) -> str:
        """Gera número único do prontuário"""
        import random
        import string
        
        # Formato: MED + ano + 6 dígitos aleatórios
        year = datetime.now().year
        random_digits = ''.join(random.choices(string.digits, k=6))
        
        return f"MED{year}{random_digits}"
    
    def to_dict(self, exclude: Optional[List[str]] = None, include_user_data: bool = False):
        """
        Converte para dicionário
        
        Args:
            exclude: Campos para excluir
            include_user_data: Se deve incluir dados do usuário
            
        Returns:
            Dicionário com dados do paciente
        """
        result = super().to_dict(exclude)
        
        # Adicionar propriedades calculadas
        result.update({
            'age': self.age,
            'age_group': self.age_group,
            'bmi': self.bmi,
            'bmi_category': self.bmi_category,
            'full_address': self.full_address,
            'has_high_priority': self.has_high_priority,
            'risk_factors': self.risk_factors
        })
        
        # Incluir dados do usuário se solicitado
        if include_user_data and hasattr(self, 'user') and self.user:
            result['user_data'] = self.user.to_dict(include_sensitive=False)
        
        return result