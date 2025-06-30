"""
Modelo de perfil médico do sistema MedAI
"""
from sqlalchemy import Column, String, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DoctorProfile(BaseModel):
    """Modelo de perfil médico"""
    
    __tablename__ = "doctor_profiles"
    
    # Relacionamento com usuário
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="doctor_profile")
    
    # Registro profissional
    crm = Column(String(20), unique=True, index=True, nullable=False)
    crm_state = Column(String(2), nullable=False)
    
    # Especialidades
    specialties = Column(JSON, nullable=True, default=list)
    subspecialties = Column(JSON, nullable=True, default=list)
    
    # Formação
    education = Column(JSON, nullable=True, default=list)
    residency = Column(JSON, nullable=True, default=list)
    fellowships = Column(JSON, nullable=True, default=list)
    
    # Experiência
    years_of_experience = Column(Integer, nullable=True)
    current_hospital = Column(String(255), nullable=True)
    other_affiliations = Column(JSON, nullable=True, default=list)
    
    # Informações adicionais
    bio = Column(Text, nullable=True)
    languages = Column(JSON, nullable=True, default=list)
    
    # Atendimento
    consultation_duration = Column(Integer, default=30)  # minutos
    accepts_health_insurance = Column(JSON, nullable=True, default=list)
    consultation_fee = Column(String(50), nullable=True)
    
    # Horários de atendimento
    working_hours = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<DoctorProfile(id={self.id}, crm='{self.crm}')>"
    
    def add_specialty(self, specialty: str):
        """Adiciona uma especialidade"""
        if not self.specialties:
            self.specialties = []
        
        if specialty not in self.specialties:
            self.specialties.append(specialty)
    
    def add_education(self, education: dict):
        """
        Adiciona formação acadêmica
        
        Args:
            education: Dict com institution, degree, year
        """
        if not self.education:
            self.education = []
        
        self.education.append({
            "institution": education.get("institution"),
            "degree": education.get("degree"),
            "year": education.get("year"),
            "field": education.get("field")
        })
    
    def set_working_hours(self, day: str, hours: list):
        """
        Define horários de trabalho
        
        Args:
            day: Dia da semana
            hours: Lista de horários [{"start": "08:00", "end": "12:00"}]
        """
        if not self.working_hours:
            self.working_hours = {}
        
        self.working_hours[day] = hours
    
    def is_available_on(self, day: str) -> bool:
        """Verifica se atende em determinado dia"""
        if not self.working_hours:
            return False
        
        return day in self.working_hours and len(self.working_hours[day]) > 0