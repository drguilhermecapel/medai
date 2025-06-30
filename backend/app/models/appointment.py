"""
Modelo de prescrição médica do sistema MedAI
"""
from sqlalchemy import Column, String, ForeignKey, Integer, JSON, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class Prescription(BaseModel):
    """Modelo de prescrição médica"""
    
    __tablename__ = "prescriptions"
    
    # Paciente
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    patient = relationship("Patient", back_populates="prescriptions")
    
    # Médico
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor = relationship("User", back_populates="prescriptions")
    
    # Código da prescrição
    prescription_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Medicamentos
    medications = Column(JSON, nullable=False, default=list)
    
    # Validade
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    
    # Observações
    notes = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_dispensed = Column(Boolean, default=False, nullable=False)
    dispensed_at = Column(DateTime, nullable=True)
    dispensed_by = Column(String(255), nullable=True)  # Farmácia
    
    def __repr__(self):
        return f"<Prescription(id={self.id}, code='{self.prescription_code}')>"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.prescription_code:
            self.prescription_code = self.generate_prescription_code()
    
    def generate_prescription_code(self) -> str:
        """Gera código único para a prescrição"""
        import uuid
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:6]
        return f"RX-{timestamp}-{unique_id}"
    
    def add_medication(self, medication: dict):
        """
        Adiciona um medicamento à prescrição
        
        Args:
            medication: Dict com name, dosage, frequency, duration, instructions
        """
        if not self.medications:
            self.medications = []
        
        self.medications.append({
            "name": medication.get("name"),
            "dosage": medication.get("dosage"),
            "frequency": medication.get("frequency"),
            "duration": medication.get("duration"),
            "instructions": medication.get("instructions", ""),
            "generic_allowed": medication.get("generic_allowed", True)
        })
    
    @property
    def is_valid(self) -> bool:
        """Verifica se a prescrição ainda é válida"""
        return self.is_active and datetime.utcnow() <= self.valid_until
    
    @property
    def days_until_expiry(self) -> int:
        """Calcula dias até expirar"""
        if not self.is_valid:
            return 0
        
        delta = self.valid_until - datetime.utcnow()
        return delta.days
    
    def mark_as_dispensed(self, pharmacy: str):
        """Marca prescrição como dispensada"""
        self.is_dispensed = True
        self.dispensed_at = datetime.utcnow()
        self.dispensed_by = pharmacy
    
    def deactivate(self):
        """Desativa a prescrição"""
        self.is_active = False