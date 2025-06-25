"""
Medical AI System Constants and Enumerations
"""

from enum import Enum, IntEnum


class DiagnosisCategory(str, Enum):
    """Categories for medical diagnoses."""
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"
    ARRHYTHMIA = "arrhythmia"
    ISCHEMIA = "ischemia"
    INFARCTION = "infarction"
    CONDUCTION_DISORDER = "conduction_disorder"
    HYPERTROPHY = "hypertrophy"
    OTHER = "other"


class ClinicalUrgency(IntEnum):
    """Clinical urgency levels for medical conditions."""
    ROUTINE = 1      # Non-urgent, routine follow-up
    LOW = 2          # Low urgency, schedule appointment
    MEDIUM = 3       # Medium urgency, see within days
    HIGH = 4         # High urgency, see within hours
    CRITICAL = 5     # Critical, immediate attention required
    
    @classmethod
    def from_diagnosis(cls, diagnosis: str, confidence: float) -> 'ClinicalUrgency':
        """Determine urgency based on diagnosis and confidence."""
        critical_conditions = ['stemi', 'vtach', 'vfib', 'complete_heart_block']
        high_urgency_conditions = ['nstemi', 'unstable_angina', 'afib_rvr', 'svt']
        
        diagnosis_lower = diagnosis.lower()
        
        if any(condition in diagnosis_lower for condition in critical_conditions):
            return cls.CRITICAL
        elif any(condition in diagnosis_lower for condition in high_urgency_conditions):
            return cls.HIGH if confidence > 0.7 else cls.MEDIUM
        elif 'abnormal' in diagnosis_lower:
            return cls.MEDIUM
        else:
            return cls.LOW


class ConfidenceLevel(str, Enum):
    """Confidence levels for AI diagnostic predictions."""
    LOW = "low"              # < 60% confidence
    MEDIUM = "medium"        # 60-80% confidence
    HIGH = "high"            # 80-95% confidence
    VERY_HIGH = "very_high"  # > 95% confidence
    
    @classmethod
    def from_score(cls, score: float) -> 'ConfidenceLevel':
        """Convert numerical confidence score to level."""
        if score < 0.6:
            return cls.LOW
        elif score < 0.8:
            return cls.MEDIUM
        elif score < 0.95:
            return cls.HIGH
        else:
            return cls.VERY_HIGH
    
    @property
    def requires_review(self) -> bool:
        """Determine if this confidence level requires human review."""
        return self in [self.LOW, self.MEDIUM]


class ECGLeads(str, Enum):
    """Standard 12-lead ECG leads."""
    I = "I"
    II = "II"
    III = "III"
    AVR = "aVR"
    AVL = "aVL"
    AVF = "aVF"
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V5 = "V5"
    V6 = "V6"
    
    @classmethod
    def limb_leads(cls):
        """Return limb leads."""
        return [cls.I, cls.II, cls.III, cls.AVR, cls.AVL, cls.AVF]
    
    @classmethod
    def precordial_leads(cls):
        """Return precordial (chest) leads."""
        return [cls.V1, cls.V2, cls.V3, cls.V4, cls.V5, cls.V6]


class HeartRhythm(str, Enum):
    """Types of heart rhythms."""
    NSR = "normal_sinus_rhythm"
    SINUS_BRADY = "sinus_bradycardia"
    SINUS_TACHY = "sinus_tachycardia"
    AFIB = "atrial_fibrillation"
    AFLUTTER = "atrial_flutter"
    SVT = "supraventricular_tachycardia"
    VTACH = "ventricular_tachycardia"
    VFIB = "ventricular_fibrillation"
    HEART_BLOCK_1 = "first_degree_av_block"
    HEART_BLOCK_2_1 = "second_degree_av_block_type1"
    HEART_BLOCK_2_2 = "second_degree_av_block_type2"
    HEART_BLOCK_3 = "third_degree_av_block"
    PACED = "paced_rhythm"


class MedicalTestType(str, Enum):
    """Types of medical tests."""
    ECG = "electrocardiogram"
    ECHO = "echocardiogram"
    STRESS_TEST = "stress_test"
    HOLTER = "holter_monitor"
    LAB_CARDIAC = "cardiac_biomarkers"
    LAB_GENERAL = "general_labs"
    IMAGING_CT = "ct_scan"
    IMAGING_MRI = "mri"


class PatientRiskLevel(str, Enum):
    """Patient risk stratification levels."""
    LOW = "low_risk"
    MODERATE = "moderate_risk"
    HIGH = "high_risk"
    VERY_HIGH = "very_high_risk"


class TreatmentRecommendation(str, Enum):
    """Types of treatment recommendations."""
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    LIFESTYLE = "lifestyle_modification"
    MONITORING = "monitoring"
    REFERRAL = "specialist_referral"
    EMERGENCY = "emergency_intervention"


# Clinical Constants
class ClinicalParameters:
    """Standard clinical parameters and thresholds."""
    
    # Heart Rate Thresholds (bpm)
    HR_BRADY_THRESHOLD = 60
    HR_TACHY_THRESHOLD = 100
    HR_CRITICAL_LOW = 40
    HR_CRITICAL_HIGH = 150
    
    # Blood Pressure Thresholds (mmHg)
    BP_SYSTOLIC_NORMAL_MAX = 120
    BP_DIASTOLIC_NORMAL_MAX = 80
    BP_HYPERTENSIVE_CRISIS = 180  # Systolic
    BP_HYPOTENSIVE_THRESHOLD = 90  # Systolic
    
    # ECG Intervals (milliseconds)
    PR_NORMAL_MIN = 120
    PR_NORMAL_MAX = 200
    QRS_NORMAL_MAX = 120
    QT_NORMAL_MAX = 440
    
    # Cardiac Biomarkers
    TROPONIN_NORMAL_MAX = 0.04  # ng/mL (varies by assay)
    BNP_NORMAL_MAX = 100  # pg/mL
    
    # Risk Score Thresholds
    CHADS2_HIGH_RISK = 2
    CHA2DS2_VASC_HIGH_RISK = 3
    HASBLED_HIGH_RISK = 3


class AnalysisStatus(str, Enum):
    """Status of ECG analysis processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"
    VALIDATED = "validated"
    REJECTED = "rejected"
    
    @property
    def is_final(self) -> bool:
        """Check if status is final (no more processing needed)."""
        return self in [self.COMPLETED, self.FAILED, self.VALIDATED, self.REJECTED]


class QualityLevel(str, Enum):
    """Signal quality levels for ECG recordings."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"
    
    @classmethod
    def from_score(cls, score: float) -> 'QualityLevel':
        """Convert quality score to level."""
        if score >= 0.9:
            return cls.EXCELLENT
        elif score >= 0.8:
            return cls.GOOD
        elif score >= 0.6:
            return cls.ACCEPTABLE
        elif score >= 0.4:
            return cls.POOR
        else:
            return cls.UNACCEPTABLE


class AnnotationType(str, Enum):
    """Types of ECG annotations."""
    BEAT = "beat"
    RHYTHM = "rhythm"
    MORPHOLOGY = "morphology"
    ARTIFACT = "artifact"
    COMMENT = "comment"
    MEASUREMENT = "measurement"


class ValidationStatus(str, Enum):
    """Clinical validation status."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CLARIFICATION = "requires_clarification"


class ReportType(str, Enum):
    """Types of clinical reports."""
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    ADDENDUM = "addendum"


class UserRole(str, Enum):
    """User roles in the system."""
    PATIENT = "patient"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    PHYSICIAN = "physician"
    CARDIOLOGIST = "cardiologist"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class DeviceType(str, Enum):
    """Types of ECG recording devices."""
    STANDARD_12_LEAD = "standard_12_lead"
    HOLTER = "holter"
    MOBILE_ECG = "mobile_ecg"
    WEARABLE = "wearable"
    IMPLANTABLE = "implantable"
    TELEMETRY = "telemetry"


class FileFormat(str, Enum):
    """Supported file formats."""
    DICOM = "dicom"
    HL7 = "hl7"
    PDF = "pdf"
    XML = "xml"
    JSON = "json"
    CSV = "csv"
    PROPRIETARY = "proprietary"


# System Configuration Constants
class SystemConfig:
    """System-wide configuration constants."""
    
    # ML Model Thresholds
    MIN_CONFIDENCE_FOR_DIAGNOSIS = 0.6
    MIN_SIGNAL_QUALITY = 0.5
    
    # Processing Limits
    MAX_ECG_DURATION_SECONDS = 30
    MAX_BATCH_SIZE = 100
    
    # Time Limits (seconds)
    EMERGENCY_PROCESSING_TIME_LIMIT = 5
    STANDARD_PROCESSING_TIME_LIMIT = 30
    
    # Clinical Validation
    REQUIRE_VALIDATION_BELOW_CONFIDENCE = 0.8
    AUTO_APPROVE_ABOVE_CONFIDENCE = 0.95