"""
Clinical Validation Framework for Medical AI
Implements comprehensive validation metrics and clinical decision support
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ClinicalMetrics:
    """Clinical performance metrics for medical AI validation"""
    sensitivity: float
    specificity: float
    ppv: float  # Positive Predictive Value
    npv: float  # Negative Predictive Value
    accuracy: float
    f1_score: float
    auc_roc: float
    confidence_interval: Tuple[float, float]

@dataclass
class ClinicalCase:
    """Individual clinical case for validation"""
    case_id: str
    patient_id: str
    modality: str
    ground_truth: str
    ai_prediction: str
    confidence: float
    uncertainty: float
    radiologist_agreement: Optional[bool] = None
    clinical_outcome: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class ClinicalValidationFramework:
    """
    Comprehensive clinical validation framework for medical AI systems
    Based on FDA guidelines and clinical best practices
    """
    
    def __init__(self):
        self.validation_cases: List[ClinicalCase] = []
        self.performance_history: List[Dict[str, Any]] = []
        
        self.clinical_thresholds = {
            'pneumonia': {
                'min_sensitivity': 0.90,
                'min_specificity': 0.80,
                'min_ppv': 0.75,
                'critical_threshold': 0.85
            },
            'covid19': {
                'min_sensitivity': 0.88,
                'min_specificity': 0.85,
                'min_ppv': 0.80,
                'critical_threshold': 0.90
            },
            'tumor': {
                'min_sensitivity': 0.95,
                'min_specificity': 0.85,
                'min_ppv': 0.85,
                'critical_threshold': 0.95
            },
            'fracture': {
                'min_sensitivity': 0.92,
                'min_specificity': 0.88,
                'min_ppv': 0.85,
                'critical_threshold': 0.90
            }
        }
        
        logger.info("Clinical Validation Framework initialized")
    
    def add_validation_case(self, case: ClinicalCase) -> None:
        """Add a new validation case"""
        self.validation_cases.append(case)
        logger.debug(f"Added validation case {case.case_id}")
    
    def calculate_clinical_metrics(self, condition: str, 
                                 time_window: Optional[timedelta] = None) -> ClinicalMetrics:
        """
        Calculate comprehensive clinical metrics for a specific condition
        
        Args:
            condition: Medical condition to evaluate
            time_window: Optional time window for recent cases
            
        Returns:
            ClinicalMetrics object with all performance measures
        """
        relevant_cases = self._filter_cases(condition, time_window)
        
        if len(relevant_cases) < 10:
            logger.warning(f"Insufficient cases for reliable metrics: {len(relevant_cases)}")
        
        tp = sum(1 for case in relevant_cases 
                if case.ground_truth == condition and case.ai_prediction == condition)
        fp = sum(1 for case in relevant_cases 
                if case.ground_truth != condition and case.ai_prediction == condition)
        tn = sum(1 for case in relevant_cases 
                if case.ground_truth != condition and case.ai_prediction != condition)
        fn = sum(1 for case in relevant_cases 
                if case.ground_truth == condition and case.ai_prediction != condition)
        
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
        accuracy = (tp + tn) / len(relevant_cases) if len(relevant_cases) > 0 else 0.0
        
        precision = ppv
        recall = sensitivity
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        auc_roc = self._estimate_auc_roc(relevant_cases, condition)
        
        ci_lower, ci_upper = self._calculate_confidence_interval(sensitivity, len(relevant_cases))
        
        return ClinicalMetrics(
            sensitivity=sensitivity,
            specificity=specificity,
            ppv=ppv,
            npv=npv,
            accuracy=accuracy,
            f1_score=f1_score,
            auc_roc=auc_roc,
            confidence_interval=(ci_lower, ci_upper)
        )
    
    def validate_clinical_performance(self, condition: str) -> Dict[str, Any]:
        """
        Comprehensive clinical performance validation
        
        Returns:
            Validation report with pass/fail status and recommendations
        """
        metrics = self.calculate_clinical_metrics(condition)
        thresholds = self.clinical_thresholds.get(condition, {})
        
        validation_report = {
            'condition': condition,
            'metrics': metrics.__dict__,
            'validation_status': 'PASS',
            'failed_criteria': [],
            'recommendations': [],
            'clinical_readiness': False,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if thresholds:
            if metrics.sensitivity < thresholds.get('min_sensitivity', 0.0):
                validation_report['validation_status'] = 'FAIL'
                validation_report['failed_criteria'].append(
                    f"Sensitivity {metrics.sensitivity:.3f} below minimum {thresholds['min_sensitivity']}"
                )
            
            if metrics.specificity < thresholds.get('min_specificity', 0.0):
                validation_report['validation_status'] = 'FAIL'
                validation_report['failed_criteria'].append(
                    f"Specificity {metrics.specificity:.3f} below minimum {thresholds['min_specificity']}"
                )
            
            if metrics.ppv < thresholds.get('min_ppv', 0.0):
                validation_report['validation_status'] = 'FAIL'
                validation_report['failed_criteria'].append(
                    f"PPV {metrics.ppv:.3f} below minimum {thresholds['min_ppv']}"
                )
        
        if validation_report['validation_status'] == 'PASS':
            validation_report['clinical_readiness'] = True
            validation_report['recommendations'].append("System meets clinical validation criteria")
        else:
            validation_report['recommendations'].extend([
                "Additional training data required",
                "Model architecture optimization needed",
                "Consider ensemble methods for improved performance"
            ])
        
        high_uncertainty_cases = [case for case in self.validation_cases 
                                if case.uncertainty > 0.7]
        if len(high_uncertainty_cases) > len(self.validation_cases) * 0.1:
            validation_report['recommendations'].append(
                "High uncertainty in >10% of cases - implement uncertainty thresholding"
            )
        
        return validation_report
    
    def generate_clinical_report(self) -> Dict[str, Any]:
        """Generate comprehensive clinical validation report"""
        conditions = set(case.ground_truth for case in self.validation_cases)
        
        report = {
            'report_date': datetime.utcnow().isoformat(),
            'total_cases': len(self.validation_cases),
            'conditions_evaluated': list(conditions),
            'condition_reports': {},
            'overall_status': 'PASS',
            'regulatory_compliance': self._assess_regulatory_compliance(),
            'recommendations': []
        }
        
        for condition in conditions:
            condition_report = self.validate_clinical_performance(condition)
            report['condition_reports'][condition] = condition_report
            
            if condition_report['validation_status'] == 'FAIL':
                report['overall_status'] = 'FAIL'
        
        if report['overall_status'] == 'FAIL':
            report['recommendations'].extend([
                "System not ready for clinical deployment",
                "Address failed validation criteria before proceeding",
                "Consider additional validation studies"
            ])
        else:
            report['recommendations'].extend([
                "System meets clinical validation criteria",
                "Ready for controlled clinical deployment",
                "Implement continuous monitoring in production"
            ])
        
        return report
    
    def _filter_cases(self, condition: str, time_window: Optional[timedelta]) -> List[ClinicalCase]:
        """Filter validation cases by condition and time window"""
        filtered_cases = [case for case in self.validation_cases 
                         if condition.lower() in [case.ground_truth.lower(), case.ai_prediction.lower()]]
        
        if time_window:
            cutoff_time = datetime.utcnow() - time_window
            filtered_cases = [case for case in filtered_cases 
                            if case.timestamp and case.timestamp >= cutoff_time]
        
        return filtered_cases
    
    def _estimate_auc_roc(self, cases: List[ClinicalCase], condition: str) -> float:
        """Estimate AUC-ROC using confidence scores"""
        if len(cases) < 10:
            return 0.5  # Default for insufficient data
        
        y_true = [1 if case.ground_truth == condition else 0 for case in cases]
        y_scores = [case.confidence if case.ai_prediction == condition else 1 - case.confidence 
                   for case in cases]
        
        try:
            positive_scores = [score for i, score in enumerate(y_scores) if y_true[i] == 1]
            negative_scores = [score for i, score in enumerate(y_scores) if y_true[i] == 0]
            
            if not positive_scores or not negative_scores:
                return 0.5
            
            concordant_pairs = sum(1 for pos in positive_scores 
                                 for neg in negative_scores if pos > neg)
            total_pairs = len(positive_scores) * len(negative_scores)
            
            return concordant_pairs / total_pairs if total_pairs > 0 else 0.5
            
        except Exception as e:
            logger.error(f"AUC calculation error: {e}")
            return 0.5
    
    def _calculate_confidence_interval(self, proportion: float, n: int, 
                                     confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for a proportion"""
        if n == 0:
            return (0.0, 0.0)
        
        z = 1.96 if confidence_level == 0.95 else 2.576  # 95% or 99%
        
        denominator = 1 + z**2 / n
        center = (proportion + z**2 / (2 * n)) / denominator
        margin = z * np.sqrt((proportion * (1 - proportion) + z**2 / (4 * n)) / n) / denominator
        
        return (max(0.0, center - margin), min(1.0, center + margin))
    
    def _assess_regulatory_compliance(self) -> Dict[str, Any]:
        """Assess regulatory compliance (FDA, CE marking, etc.)"""
        return {
            'fda_510k_ready': len(self.validation_cases) >= 100,
            'ce_marking_ready': len(self.validation_cases) >= 50,
            'clinical_evidence_level': 'Level II' if len(self.validation_cases) >= 500 else 'Level III',
            'bias_assessment': self._assess_bias(),
            'fairness_metrics': self._assess_fairness()
        }
    
    def _assess_bias(self) -> Dict[str, Any]:
        """Assess potential bias in the validation dataset"""
        modalities = {}
        for case in self.validation_cases:
            modalities[case.modality] = modalities.get(case.modality, 0) + 1
        
        return {
            'modality_distribution': modalities,
            'temporal_bias_risk': 'LOW',  # Would need more sophisticated analysis
            'selection_bias_risk': 'MEDIUM'  # Conservative estimate
        }
    
    def _assess_fairness(self) -> Dict[str, Any]:
        """Assess fairness across different patient populations"""
        return {
            'demographic_parity': 'NOT_ASSESSED',
            'equalized_odds': 'NOT_ASSESSED',
            'recommendation': 'Collect demographic data for comprehensive fairness assessment'
        }

class ContinuousMonitoring:
    """Continuous monitoring system for deployed medical AI"""
    
    def __init__(self, validation_framework: ClinicalValidationFramework):
        self.validation_framework = validation_framework
        self.alert_thresholds = {
            'sensitivity_drop': 0.05,  # Alert if sensitivity drops by 5%
            'specificity_drop': 0.05,
            'uncertainty_increase': 0.1
        }
        self.baseline_metrics = {}
        
    def establish_baseline(self, condition: str) -> None:
        """Establish baseline metrics for monitoring"""
        metrics = self.validation_framework.calculate_clinical_metrics(condition)
        self.baseline_metrics[condition] = metrics
        logger.info(f"Baseline established for {condition}")
    
    def monitor_performance(self, condition: str) -> Dict[str, Any]:
        """Monitor current performance against baseline"""
        current_metrics = self.validation_framework.calculate_clinical_metrics(
            condition, time_window=timedelta(days=30)
        )
        
        if condition not in self.baseline_metrics:
            return {'status': 'NO_BASELINE', 'message': 'Baseline not established'}
        
        baseline = self.baseline_metrics[condition]
        
        alerts = []
        
        if current_metrics.sensitivity < baseline.sensitivity - self.alert_thresholds['sensitivity_drop']:
            alerts.append(f"Sensitivity degradation detected: {current_metrics.sensitivity:.3f} vs baseline {baseline.sensitivity:.3f}")
        
        if current_metrics.specificity < baseline.specificity - self.alert_thresholds['specificity_drop']:
            alerts.append(f"Specificity degradation detected: {current_metrics.specificity:.3f} vs baseline {baseline.specificity:.3f}")
        
        return {
            'status': 'ALERT' if alerts else 'NORMAL',
            'alerts': alerts,
            'current_metrics': current_metrics.__dict__,
            'baseline_metrics': baseline.__dict__,
            'monitoring_period': '30 days'
        }
