"""
Feature flags configuration for multi-specialty EHR system
Allows enabling/disabling specialties and features dynamically
"""
import os
from typing import Dict, List, Set
from pydantic import BaseSettings


class FeatureFlags(BaseSettings):
    """Feature flags configuration"""
    
    # === SPECIALTY FLAGS ===
    # Wave 1 specialties
    DERMATOLOGY_ENABLED: bool = True
    PEDIATRICS_ENABLED: bool = True
    FAMILY_MEDICINE_ENABLED: bool = False
    GYNECOLOGY_ENABLED: bool = False
    ORTHOPEDICS_ENABLED: bool = False
    OPHTHALMOLOGY_ENABLED: bool = False
    ENDOCRINOLOGY_ENABLED: bool = False
    PSYCHIATRY_ENABLED: bool = False
    OTOLARYNGOLOGY_ENABLED: bool = False
    
    # Wave 2 specialties
    NEUROLOGY_ENABLED: bool = False
    GASTROENTEROLOGY_ENABLED: bool = False
    PULMONOLOGY_ENABLED: bool = False
    NEPHROLOGY_ENABLED: bool = False
    RHEUMATOLOGY_ENABLED: bool = False
    UROLOGY_ENABLED: bool = False
    INFECTIOUS_DISEASE_ENABLED: bool = False
    HEMATOLOGY_ENABLED: bool = False
    ONCOLOGY_ENABLED: bool = False
    GERIATRICS_ENABLED: bool = False
    OCCUPATIONAL_MEDICINE_ENABLED: bool = False
    ANESTHESIOLOGY_ENABLED: bool = False
    GENERAL_SURGERY_ENABLED: bool = False
    
    # Legacy specialties (always enabled for backward compatibility)
    CARDIOLOGY_ENABLED: bool = True
    
    # === FEATURE FLAGS ===
    FHIR_COMPLIANCE_ENABLED: bool = True
    AI_ASSISTANCE_ENABLED: bool = True
    TELEMEDICINE_ENABLED: bool = True
    MOBILE_APP_ENABLED: bool = False
    ADVANCED_ANALYTICS_ENABLED: bool = True
    MULTI_LANGUAGE_ENABLED: bool = False
    VOICE_RECOGNITION_ENABLED: bool = False
    BLOCKCHAIN_AUDIT_ENABLED: bool = False
    
    # === SPECIALTY-SPECIFIC FEATURES ===
    # Dermatology
    DERMATOLOGY_ABCDE_ENABLED: bool = True
    DERMATOLOGY_PHOTO_MAPPING_ENABLED: bool = True
    DERMATOLOGY_AI_ANALYSIS_ENABLED: bool = False
    DERMATOLOGY_DERMOSCOPY_ENABLED: bool = True
    
    # Pediatrics
    PEDIATRICS_GROWTH_CHARTS_ENABLED: bool = True
    PEDIATRICS_VACCINATIONS_ENABLED: bool = True
    PEDIATRICS_DEVELOPMENT_TRACKING_ENABLED: bool = True
    PEDIATRICS_MILESTONE_ALERTS_ENABLED: bool = True
    
    # Cardiology
    CARDIOLOGY_ECG_ANALYSIS_ENABLED: bool = True
    CARDIOLOGY_RISK_SCORING_ENABLED: bool = True
    
    # === ENVIRONMENT-SPECIFIC FLAGS ===
    DEBUG_MODE_ENABLED: bool = False
    PERFORMANCE_MONITORING_ENABLED: bool = True
    DETAILED_LOGGING_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "MEDAI_"
        case_sensitive = True
    
    @property
    def enabled_specialties(self) -> List[str]:
        """Get list of enabled specialties"""
        specialties = []
        
        # Wave 1 specialties
        if self.DERMATOLOGY_ENABLED:
            specialties.append("dermatology")
        if self.PEDIATRICS_ENABLED:
            specialties.append("pediatrics")
        if self.FAMILY_MEDICINE_ENABLED:
            specialties.append("family_medicine")
        if self.GYNECOLOGY_ENABLED:
            specialties.append("gynecology")
        if self.ORTHOPEDICS_ENABLED:
            specialties.append("orthopedics")
        if self.OPHTHALMOLOGY_ENABLED:
            specialties.append("ophthalmology")
        if self.ENDOCRINOLOGY_ENABLED:
            specialties.append("endocrinology")
        if self.PSYCHIATRY_ENABLED:
            specialties.append("psychiatry")
        if self.OTOLARYNGOLOGY_ENABLED:
            specialties.append("otolaryngology")
        
        # Wave 2 specialties
        if self.NEUROLOGY_ENABLED:
            specialties.append("neurology")
        if self.GASTROENTEROLOGY_ENABLED:
            specialties.append("gastroenterology")
        if self.PULMONOLOGY_ENABLED:
            specialties.append("pulmonology")
        if self.NEPHROLOGY_ENABLED:
            specialties.append("nephrology")
        if self.RHEUMATOLOGY_ENABLED:
            specialties.append("rheumatology")
        if self.UROLOGY_ENABLED:
            specialties.append("urology")
        if self.INFECTIOUS_DISEASE_ENABLED:
            specialties.append("infectious_disease")
        if self.HEMATOLOGY_ENABLED:
            specialties.append("hematology")
        if self.ONCOLOGY_ENABLED:
            specialties.append("oncology")
        if self.GERIATRICS_ENABLED:
            specialties.append("geriatrics")
        if self.OCCUPATIONAL_MEDICINE_ENABLED:
            specialties.append("occupational_medicine")
        if self.ANESTHESIOLOGY_ENABLED:
            specialties.append("anesthesiology")
        if self.GENERAL_SURGERY_ENABLED:
            specialties.append("general_surgery")
        
        # Legacy specialties
        if self.CARDIOLOGY_ENABLED:
            specialties.append("cardiology")
        
        return specialties
    
    @property
    def wave1_specialties(self) -> List[str]:
        """Get Wave 1 specialties that are enabled"""
        wave1 = [
            "family_medicine", "pediatrics", "gynecology", "dermatology",
            "orthopedics", "ophthalmology", "endocrinology", "psychiatry", "otolaryngology"
        ]
        return [s for s in wave1 if s in self.enabled_specialties]
    
    @property
    def wave2_specialties(self) -> List[str]:
        """Get Wave 2 specialties that are enabled"""
        wave2 = [
            "neurology", "gastroenterology", "pulmonology", "nephrology", "rheumatology",
            "urology", "infectious_disease", "hematology", "oncology", "geriatrics",
            "occupational_medicine", "anesthesiology", "general_surgery"
        ]
        return [s for s in wave2 if s in self.enabled_specialties]
    
    def is_specialty_enabled(self, specialty: str) -> bool:
        """Check if a specific specialty is enabled"""
        return specialty in self.enabled_specialties
    
    def get_specialty_features(self, specialty: str) -> Dict[str, bool]:
        """Get enabled features for a specific specialty"""
        features = {}
        
        if specialty == "dermatology":
            features.update({
                "abcde_assessment": self.DERMATOLOGY_ABCDE_ENABLED,
                "photo_mapping": self.DERMATOLOGY_PHOTO_MAPPING_ENABLED,
                "ai_analysis": self.DERMATOLOGY_AI_ANALYSIS_ENABLED,
                "dermoscopy": self.DERMATOLOGY_DERMOSCOPY_ENABLED,
            })
        elif specialty == "pediatrics":
            features.update({
                "growth_charts": self.PEDIATRICS_GROWTH_CHARTS_ENABLED,
                "vaccinations": self.PEDIATRICS_VACCINATIONS_ENABLED,
                "development_tracking": self.PEDIATRICS_DEVELOPMENT_TRACKING_ENABLED,
                "milestone_alerts": self.PEDIATRICS_MILESTONE_ALERTS_ENABLED,
            })
        elif specialty == "cardiology":
            features.update({
                "ecg_analysis": self.CARDIOLOGY_ECG_ANALYSIS_ENABLED,
                "risk_scoring": self.CARDIOLOGY_RISK_SCORING_ENABLED,
            })
        
        return features
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for API responses"""
        return {
            "enabled_specialties": self.enabled_specialties,
            "wave1_specialties": self.wave1_specialties,
            "wave2_specialties": self.wave2_specialties,
            "features": {
                "fhir_compliance": self.FHIR_COMPLIANCE_ENABLED,
                "ai_assistance": self.AI_ASSISTANCE_ENABLED,
                "telemedicine": self.TELEMEDICINE_ENABLED,
                "mobile_app": self.MOBILE_APP_ENABLED,
                "advanced_analytics": self.ADVANCED_ANALYTICS_ENABLED,
                "multi_language": self.MULTI_LANGUAGE_ENABLED,
                "voice_recognition": self.VOICE_RECOGNITION_ENABLED,
                "blockchain_audit": self.BLOCKCHAIN_AUDIT_ENABLED,
            },
            "specialty_features": {
                specialty: self.get_specialty_features(specialty)
                for specialty in self.enabled_specialties
            }
        }


# Global feature flags instance
feature_flags = FeatureFlags()


def get_feature_flags() -> FeatureFlags:
    """Get the feature flags instance"""
    return feature_flags


def is_specialty_enabled(specialty: str) -> bool:
    """Quick check if specialty is enabled"""
    return feature_flags.is_specialty_enabled(specialty)


def require_specialty(specialty: str):
    """Decorator to require a specialty to be enabled"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_specialty_enabled(specialty):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=404,
                    detail=f"Specialty '{specialty}' is not enabled"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_feature(feature_flag: bool):
    """Decorator to require a feature to be enabled"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not feature_flag:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=404,
                    detail="Feature is not enabled"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator