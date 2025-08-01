"""
Pediatrics specialty models extending FHIR base models
Supports growth charts, vaccinations, developmental assessments, etc.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.fhir_base import FHIRObservation, FHIRProcedure
from app.models.base import AuditableModel


class PediatricsGrowthChart(FHIRObservation):
    """
    Pediatric growth chart data extending FHIR Observation
    Tracks height, weight, BMI, head circumference over time
    """
    
    __tablename__ = "pediatrics_growth_charts"
    
    # Reference to parent FHIR Observation
    fhir_observation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_observations.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Reference to FHIR Observation"
    )
    
    # Measurement date and age
    measurement_date = Column(
        Date,
        nullable=False,
        doc="Date of measurement"
    )
    
    age_at_measurement_days = Column(
        Numeric(6, 0),
        nullable=False,
        doc="Age in days at time of measurement"
    )
    
    age_at_measurement_months = Column(
        Numeric(5, 2),
        nullable=False,
        doc="Age in months at time of measurement"
    )
    
    # Growth measurements
    weight_kg = Column(
        Numeric(5, 3),
        nullable=True,
        doc="Weight in kilograms"
    )
    
    weight_percentile = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Weight percentile (0-100)"
    )
    
    weight_z_score = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Weight Z-score"
    )
    
    height_cm = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Height/length in centimeters"
    )
    
    height_percentile = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Height percentile (0-100)"
    )
    
    height_z_score = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Height Z-score"
    )
    
    head_circumference_cm = Column(
        Numeric(4, 2),
        nullable=True,
        doc="Head circumference in centimeters"
    )
    
    head_circumference_percentile = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Head circumference percentile (0-100)"
    )
    
    head_circumference_z_score = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Head circumference Z-score"
    )
    
    bmi = Column(
        Numeric(4, 2),
        nullable=True,
        doc="Body Mass Index"
    )
    
    bmi_percentile = Column(
        Numeric(5, 2),
        nullable=True,
        doc="BMI percentile (0-100)"
    )
    
    bmi_z_score = Column(
        Numeric(5, 2),
        nullable=True,
        doc="BMI Z-score"
    )
    
    # Growth chart type and references
    chart_type = Column(
        String(50),
        nullable=True,
        doc="Growth chart type (WHO | CDC | specialized)"
    )
    
    reference_population = Column(
        String(50),
        nullable=True,
        doc="Reference population used for percentiles"
    )
    
    # Growth velocity assessments
    weight_velocity_kg_per_month = Column(
        Numeric(4, 3),
        nullable=True,
        doc="Weight velocity in kg per month"
    )
    
    height_velocity_cm_per_month = Column(
        Numeric(4, 2),
        nullable=True,
        doc="Height velocity in cm per month"
    )
    
    # Nutritional status indicators
    nutritional_status = Column(
        String(50),
        nullable=True,
        doc="Nutritional status (normal | underweight | overweight | obese | wasted | stunted)"
    )
    
    feeding_method = Column(
        String(50),
        nullable=True,
        doc="Feeding method (breastfeeding | formula | mixed | solid_foods)"
    )
    
    # Clinical concerns
    growth_concerns = Column(
        JSONB,
        default=list,
        doc="Growth-related concerns or flags"
    )
    
    intervention_needed = Column(
        Boolean,
        default=False,
        doc="Whether intervention is needed"
    )
    
    intervention_type = Column(
        JSONB,
        default=list,
        doc="Types of interventions recommended"
    )
    
    # Additional measurements
    mid_upper_arm_circumference_cm = Column(
        Numeric(4, 2),
        nullable=True,
        doc="Mid-upper arm circumference in centimeters"
    )
    
    triceps_skinfold_mm = Column(
        Numeric(4, 1),
        nullable=True,
        doc="Triceps skinfold thickness in millimeters"
    )
    
    @hybrid_property
    def calculated_bmi(self) -> Optional[float]:
        """Calculate BMI if height and weight are available"""
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = float(self.height_cm) / 100
            return float(self.weight_kg) / (height_m ** 2)
        return None
    
    @hybrid_property
    def is_growth_concerning(self) -> bool:
        """Determine if growth measurements are concerning"""
        # Check for extreme percentiles
        if self.weight_percentile and (self.weight_percentile < 3 or self.weight_percentile > 97):
            return True
        if self.height_percentile and (self.height_percentile < 3 or self.height_percentile > 97):
            return True
        if self.bmi_percentile and (self.bmi_percentile < 5 or self.bmi_percentile > 95):
            return True
        
        # Check for extreme Z-scores
        if self.weight_z_score and abs(self.weight_z_score) > 2:
            return True
        if self.height_z_score and abs(self.height_z_score) > 2:
            return True
        if self.bmi_z_score and abs(self.bmi_z_score) > 2:
            return True
            
        return False


class PediatricsVaccination(FHIRProcedure):
    """
    Pediatric vaccination record extending FHIR Procedure
    Tracks immunization history and schedules
    """
    
    __tablename__ = "pediatrics_vaccinations"
    
    # Reference to parent FHIR Procedure
    fhir_procedure_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_procedures.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Reference to FHIR Procedure"
    )
    
    # Vaccine identification
    vaccine_name = Column(
        String(100),
        nullable=False,
        doc="Name of the vaccine"
    )
    
    vaccine_code = Column(
        String(20),
        nullable=True,
        doc="CVX (vaccine administered) code"
    )
    
    vaccine_group = Column(
        String(50),
        nullable=True,
        doc="Vaccine group (e.g., DTaP, MMR, IPV)"
    )
    
    # Administration details
    administration_date = Column(
        Date,
        nullable=False,
        doc="Date vaccine was administered"
    )
    
    dose_number = Column(
        Numeric(2, 0),
        nullable=True,
        doc="Dose number in series (1, 2, 3, etc.)"
    )
    
    series_doses_total = Column(
        Numeric(2, 0),
        nullable=True,
        doc="Total doses required in series"
    )
    
    age_at_administration_days = Column(
        Numeric(6, 0),
        nullable=False,
        doc="Age in days when vaccine was administered"
    )
    
    age_at_administration_months = Column(
        Numeric(5, 2),
        nullable=False,
        doc="Age in months when vaccine was administered"
    )
    
    # Vaccine product details
    manufacturer = Column(
        String(100),
        nullable=True,
        doc="Vaccine manufacturer"
    )
    
    lot_number = Column(
        String(50),
        nullable=True,
        doc="Vaccine lot number"
    )
    
    expiration_date = Column(
        Date,
        nullable=True,
        doc="Vaccine expiration date"
    )
    
    # Administration site and route
    administration_site = Column(
        String(50),
        nullable=True,
        doc="Site of administration (left_deltoid, right_deltoid, left_thigh, etc.)"
    )
    
    administration_route = Column(
        String(20),
        nullable=True,
        doc="Route of administration (IM, SubQ, oral, nasal)"
    )
    
    dose_volume_ml = Column(
        Numeric(3, 2),
        nullable=True,
        doc="Dose volume in milliliters"
    )
    
    # Provider information
    administering_provider = Column(
        String(100),
        nullable=True,
        doc="Name of administering provider"
    )
    
    administering_facility = Column(
        String(200),
        nullable=True,
        doc="Facility where vaccine was administered"
    )
    
    # Schedule compliance
    schedule_compliance = Column(
        String(20),
        nullable=True,
        doc="Schedule compliance (on_time | early | late | catch_up)"
    )
    
    days_early_late = Column(
        Numeric(4, 0),
        nullable=True,
        doc="Days early (negative) or late (positive) from recommended schedule"
    )
    
    catch_up_vaccine = Column(
        Boolean,
        default=False,
        doc="Whether this is a catch-up vaccination"
    )
    
    # Adverse events
    adverse_events_reported = Column(
        Boolean,
        default=False,
        doc="Whether adverse events were reported"
    )
    
    adverse_events = Column(
        JSONB,
        default=list,
        doc="List of adverse events if any"
    )
    
    # Contraindications and precautions
    contraindications = Column(
        JSONB,
        default=list,
        doc="Contraindications noted at time of administration"
    )
    
    precautions = Column(
        JSONB,
        default=list,
        doc="Precautions noted at time of administration"
    )
    
    # Next dose information
    next_dose_due_date = Column(
        Date,
        nullable=True,
        doc="Date next dose is due"
    )
    
    series_complete = Column(
        Boolean,
        default=False,
        doc="Whether the vaccine series is complete"
    )
    
    @hybrid_property
    def is_overdue_for_next_dose(self) -> bool:
        """Check if next dose is overdue"""
        if self.next_dose_due_date and not self.series_complete:
            return date.today() > self.next_dose_due_date
        return False


class PediatricsDevelopmentAssessment(FHIRObservation):
    """
    Pediatric developmental assessment extending FHIR Observation
    Tracks developmental milestones and screening results
    """
    
    __tablename__ = "pediatrics_development_assessments"
    
    # Reference to parent FHIR Observation
    fhir_observation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fhir_observations.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Reference to FHIR Observation"
    )
    
    # Assessment details
    assessment_date = Column(
        Date,
        nullable=False,
        doc="Date of developmental assessment"
    )
    
    age_at_assessment_months = Column(
        Numeric(5, 2),
        nullable=False,
        doc="Age in months at time of assessment"
    )
    
    assessment_type = Column(
        String(50),
        nullable=False,
        doc="Type of assessment (milestone_check | formal_screening | diagnostic)"
    )
    
    screening_tool = Column(
        String(100),
        nullable=True,
        doc="Screening tool used (ASQ, M-CHAT, PEDS, etc.)"
    )
    
    # Developmental domains
    gross_motor_status = Column(
        String(20),
        nullable=True,
        doc="Gross motor development status (on_track | concern | delay)"
    )
    
    gross_motor_milestones = Column(
        JSONB,
        default=list,
        doc="Gross motor milestones achieved"
    )
    
    fine_motor_status = Column(
        String(20),
        nullable=True,
        doc="Fine motor development status (on_track | concern | delay)"
    )
    
    fine_motor_milestones = Column(
        JSONB,
        default=list,
        doc="Fine motor milestones achieved"
    )
    
    language_status = Column(
        String(20),
        nullable=True,
        doc="Language development status (on_track | concern | delay)"
    )
    
    language_milestones = Column(
        JSONB,
        default=list,
        doc="Language milestones achieved"
    )
    
    social_emotional_status = Column(
        String(20),
        nullable=True,
        doc="Social-emotional development status (on_track | concern | delay)"
    )
    
    social_emotional_milestones = Column(
        JSONB,
        default=list,
        doc="Social-emotional milestones achieved"
    )
    
    cognitive_status = Column(
        String(20),
        nullable=True,
        doc="Cognitive development status (on_track | concern | delay)"
    )
    
    cognitive_milestones = Column(
        JSONB,
        default=list,
        doc="Cognitive milestones achieved"
    )
    
    # Screening scores
    total_score = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Total assessment score"
    )
    
    domain_scores = Column(
        JSONB,
        default=dict,
        doc="Scores by developmental domain"
    )
    
    percentile_ranking = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Percentile ranking if applicable"
    )
    
    # Risk assessment
    overall_development_status = Column(
        String(20),
        nullable=True,
        doc="Overall development status (typical | at_risk | delayed)"
    )
    
    risk_factors = Column(
        JSONB,
        default=list,
        doc="Identified risk factors for developmental delay"
    )
    
    protective_factors = Column(
        JSONB,
        default=list,
        doc="Identified protective factors"
    )
    
    # Red flags and concerns
    red_flags = Column(
        JSONB,
        default=list,
        doc="Developmental red flags identified"
    )
    
    parental_concerns = Column(
        JSONB,
        default=list,
        doc="Parental concerns reported"
    )
    
    provider_concerns = Column(
        JSONB,
        default=list,
        doc="Provider concerns noted"
    )
    
    # Recommendations and follow-up
    recommendations = Column(
        JSONB,
        default=list,
        doc="Clinical recommendations"
    )
    
    referrals_made = Column(
        JSONB,
        default=list,
        doc="Referrals made (early intervention, speech therapy, etc.)"
    )
    
    follow_up_recommended = Column(
        Boolean,
        default=False,
        doc="Whether follow-up assessment is recommended"
    )
    
    follow_up_interval_months = Column(
        Numeric(3, 1),
        nullable=True,
        doc="Recommended follow-up interval in months"
    )
    
    # Environmental factors
    home_environment_assessment = Column(
        JSONB,
        default=dict,
        doc="Home environment assessment results"
    )
    
    childcare_information = Column(
        JSONB,
        default=dict,
        doc="Childcare or preschool information"
    )
    
    @hybrid_property
    def needs_referral(self) -> bool:
        """Determine if child needs referral for further evaluation"""
        delay_statuses = ['concern', 'delay']
        
        if self.overall_development_status in ['at_risk', 'delayed']:
            return True
        if self.gross_motor_status in delay_statuses:
            return True
        if self.fine_motor_status in delay_statuses:
            return True
        if self.language_status in delay_statuses:
            return True
        if self.social_emotional_status in delay_statuses:
            return True
        if self.cognitive_status in delay_statuses:
            return True
        if self.red_flags:
            return True
            
        return False
    
    @hybrid_property
    def domains_with_concerns(self) -> List[str]:
        """List developmental domains with concerns"""
        domains = []
        delay_statuses = ['concern', 'delay']
        
        if self.gross_motor_status in delay_statuses:
            domains.append('gross_motor')
        if self.fine_motor_status in delay_statuses:
            domains.append('fine_motor')
        if self.language_status in delay_statuses:
            domains.append('language')
        if self.social_emotional_status in delay_statuses:
            domains.append('social_emotional')
        if self.cognitive_status in delay_statuses:
            domains.append('cognitive')
            
        return domains


# Index definitions for pediatrics tables
Index('ix_pediatrics_growth_age_months', PediatricsGrowthChart.age_at_measurement_months)
Index('ix_pediatrics_growth_measurement_date', PediatricsGrowthChart.measurement_date)
Index('ix_pediatrics_vaccinations_vaccine_name', PediatricsVaccination.vaccine_name)
Index('ix_pediatrics_vaccinations_administration_date', PediatricsVaccination.administration_date)
Index('ix_pediatrics_vaccinations_next_due_date', PediatricsVaccination.next_dose_due_date)
Index('ix_pediatrics_development_assessment_date', PediatricsDevelopmentAssessment.assessment_date)
Index('ix_pediatrics_development_age_months', PediatricsDevelopmentAssessment.age_at_assessment_months)
Index('ix_pediatrics_development_overall_status', PediatricsDevelopmentAssessment.overall_development_status)