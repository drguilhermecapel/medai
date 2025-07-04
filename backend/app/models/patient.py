"""
Modelo de paciente do sistema MedAI
"""
from sqlalchemy import Column, String, Date, ForeignKey, Integer, JSON, Float
from sqlalchemy.orm import relationship
from datetime import date, datetime

from app.models.base import BaseModel


class Patient(BaseModel):
    """Modelo de perfil de paciente"""
    
    __tablename__ = "patients"
    __table_args__ = {"extend_existing": True}
    
    # Relacionamento com usuário
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="patient_profile")
    
    # Informações pessoais
    cpf = Column(String(14), unique=True, index=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Endereço
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)
    
    # Informações médicas
    blood_type = Column(String(5), nullable=True)
    weight = Column(Float, nullable=True)  # em kg
    height = Column(Float, nullable=True)  # em metros
    
    # Histórico médico
    allergies = Column(JSON, nullable=True, default=list)
    chronic_conditions = Column(JSON, nullable=True, default=list)
    current_medications = Column(JSON, nullable=True, default=list)
    medical_history = Column(String, nullable=True)
    family_history = Column(String, nullable=True)
    
    # Contato de emergência
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)
    
    # Plano de saúde
    insurance_provider = Column(String(100), nullable=True)
    insurance_number = Column(String(50), nullable=True)
    insurance_validity = Column(Date, nullable=True)
    
    # Relacionamentos
    exams = relationship("Exam", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, cpf='{self.cpf}')>"
    
    @property
    def age(self) -> int:
        """Calcula a idade do paciente"""
        if not self.date_of_birth:
            return 0
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        # Ajusta se ainda não fez aniversário este ano
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
            
        return age
    
    @property
    def bmi(self) -> float:
        """Calcula o IMC do paciente"""
        if not self.weight or not self.height:
            return 0.0
        
        return round(self.weight / (self.height ** 2), 2)
    
    @property
    def full_address(self) -> str:
        """Retorna o endereço completo"""
        parts = []
        
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(f"CEP: {self.zip_code}")
            
        return ", ".join(parts)
    
    def add_allergy(self, allergy: str):
        """Adiciona uma alergia à lista"""
        if not self.allergies:
            self.allergies = []
        
        if allergy not in self.allergies:
            self.allergies.append(allergy)
    
    def remove_allergy(self, allergy: str):
        """Remove uma alergia da lista"""
        if self.allergies and allergy in self.allergies:
            self.allergies.remove(allergy)
    
    def add_chronic_condition(self, condition: str):
        """Adiciona uma condição crônica"""
        if not self.chronic_conditions:
            self.chronic_conditions = []
        
        if condition not in self.chronic_conditions:
            self.chronic_conditions.append(condition)
    
    def add_medication(self, medication: dict):
        """
        Adiciona um medicamento em uso
        
        Args:
            medication: Dict com nome, dosagem, frequência
        """
        if not self.current_medications:
            self.current_medications = []
        
        self.current_medications.append({
            "name": medication.get("name"),
            "dosage": medication.get("dosage"),
            "frequency": medication.get("frequency"),
            "start_date": medication.get("start_date", datetime.utcnow().isoformat())
        })