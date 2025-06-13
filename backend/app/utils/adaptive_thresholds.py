"""
Adaptive Thresholds Manager
Provides dynamic threshold management for ECG parameters
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np


class ThresholdType(Enum):
    HEART_RATE = "heart_rate"
    PR_INTERVAL = "pr_interval"
    QRS_DURATION = "qrs_duration"
    QT_INTERVAL = "qt_interval"
    ST_ELEVATION = "st_elevation"


class AdaptiveThresholdManager:
    """Manages adaptive thresholds for ECG parameters"""

    def __init__(self):
        self.thresholds = self._initialize_default_thresholds()
        self.learning_rate = 0.01
        self.confidence_threshold = 0.8
        self.population_adjustments = self._load_population_adjustments()
        self.contextual_rules = self._load_contextual_rules()

    def _initialize_default_thresholds(self) -> dict[str, dict[str, float]]:
        """Initialize default threshold values"""
        return {
            "heart_rate": {
                "lower": 60.0,
                "upper": 100.0,
                "critical_lower": 40.0,
                "critical_upper": 150.0,
            },
            "pr_interval": {
                "lower": 120.0,
                "upper": 200.0,
                "critical_lower": 80.0,
                "critical_upper": 300.0,
            },
            "qrs_duration": {
                "lower": 80.0,
                "upper": 120.0,
                "critical_lower": 60.0,
                "critical_upper": 180.0,
            },
            "qt_interval": {
                "lower": 350.0,
                "upper": 450.0,
                "critical_lower": 300.0,
                "critical_upper": 500.0,
            },
            "st_elevation": {
                "lower": -0.5,
                "upper": 0.5,
                "critical_lower": -2.0,
                "critical_upper": 2.0,
            },
        }

    def _load_population_adjustments(self) -> dict[str, dict[str, float]]:
        """Load population-specific threshold adjustments"""
        return {
            "pediatric": {
                "heart_rate_multiplier": 1.5,
                "pr_interval_multiplier": 0.8,
                "qrs_duration_multiplier": 0.9,
            },
            "geriatric": {
                "heart_rate_multiplier": 0.9,
                "pr_interval_multiplier": 1.1,
                "qrs_duration_multiplier": 1.1,
            },
            "athlete": {
                "heart_rate_multiplier": 0.7,
                "pr_interval_multiplier": 1.0,
                "qrs_duration_multiplier": 1.0,
            },
        }

    def _load_contextual_rules(self) -> dict[str, dict[str, Any]]:
        """Load contextual adjustment rules"""
        return {
            "medications": {
                "beta_blockers": {"heart_rate": {"upper_adjustment": -20}},
                "amiodarone": {"qt_interval": {"upper_adjustment": 50}},
                "digoxin": {"pr_interval": {"upper_adjustment": 20}},
            },
            "conditions": {
                "hypertension": {"heart_rate": {"upper_adjustment": 10}},
                "diabetes": {"qt_interval": {"upper_adjustment": 20}},
            },
        }

    def get_current_thresholds(self) -> dict[str, dict[str, float]]:
        """Get current threshold values"""
        import copy

        return copy.deepcopy(self.thresholds)

    def update_thresholds(self, historical_data: dict[str, np.ndarray]) -> None:
        """Update thresholds based on historical data"""
        for parameter, data in historical_data.items():
            if parameter in self.thresholds:
                mean_val = np.mean(data)
                std_val = np.std(data)

                current = self.thresholds[parameter]

                new_lower = mean_val - 2 * std_val
                new_upper = mean_val + 2 * std_val

                current["lower"] = (1 - self.learning_rate) * current[
                    "lower"
                ] + self.learning_rate * new_lower
                current["upper"] = (1 - self.learning_rate) * current[
                    "upper"
                ] + self.learning_rate * new_upper

    def get_adjusted_thresholds(
        self, patient_demographics: dict[str, Any]
    ) -> dict[str, dict[str, float]]:
        """Get thresholds adjusted for patient demographics"""
        adjusted = self.get_current_thresholds()

        age = patient_demographics.get("age", 50)
        population = None

        if age < 18:
            population = "pediatric"
        elif age > 65:
            population = "geriatric"

        activity_level = patient_demographics.get("activity_level", "normal")
        if activity_level == "high":
            population = "athlete"

        if population and population in self.population_adjustments:
            adjustments = self.population_adjustments[population]
            for param in adjusted:
                for threshold_type in ["lower", "upper"]:
                    multiplier_key = f"{param}_multiplier"
                    if multiplier_key in adjustments:
                        adjusted[param][threshold_type] *= adjustments[multiplier_key]

        return adjusted

    def learn_from_feedback(self, feedback: dict[str, Any]) -> None:
        """Learn from clinician feedback"""
        parameter = feedback.get("parameter")
        value = feedback.get("value")
        clinical_judgment = feedback.get("clinical_judgment")  # 'normal', 'abnormal'
        patient_context = feedback.get("patient_context", {})

        if parameter not in self.thresholds:
            return

        if clinical_judgment == "normal" and parameter in self.thresholds:
            current = self.thresholds[parameter]

            if value < current["lower"]:
                current["lower"] = (1 - self.learning_rate) * current[
                    "lower"
                ] + self.learning_rate * value
            elif value > current["upper"]:
                current["upper"] = (1 - self.learning_rate) * current[
                    "upper"
                ] + self.learning_rate * value

        self._update_contextual_rules(
            parameter, value, clinical_judgment, patient_context
        )

    def _update_contextual_rules(
        self, parameter: str, value: float, judgment: str, context: dict[str, Any]
    ) -> None:
        """Update contextual adjustment rules"""
        pass

    def get_contextual_thresholds(
        self, context: dict[str, Any]
    ) -> dict[str, dict[str, float]]:
        """Get thresholds adjusted for specific context"""
        adjusted = self.get_current_thresholds()

        medications = context.get("medications", [])
        if isinstance(medications, str):
            medications = [medications]

        for medication in medications:
            if medication in self.contextual_rules["medications"]:
                med_rules = self.contextual_rules["medications"][medication]
                for param, adjustments in med_rules.items():
                    if param in adjusted:
                        for adj_type, adj_value in adjustments.items():
                            if adj_type == "upper_adjustment":
                                adjusted[param]["upper"] += adj_value
                            elif adj_type == "lower_adjustment":
                                adjusted[param]["lower"] += adj_value

        conditions = context.get("conditions", [])
        if isinstance(conditions, str):
            conditions = [conditions]

        for condition in conditions:
            if condition in self.contextual_rules["conditions"]:
                cond_rules = self.contextual_rules["conditions"][condition]
                for param, adjustments in cond_rules.items():
                    if param in adjusted:
                        for adj_type, adj_value in adjustments.items():
                            if adj_type == "upper_adjustment":
                                adjusted[param]["upper"] += adj_value
                            elif adj_type == "lower_adjustment":
                                adjusted[param]["lower"] += adj_value

        return adjusted

    def detect_anomalies(
        self, measurements: dict[str, float], context: dict[str, Any] = None
    ) -> list[str]:
        """Detect anomalies based on current thresholds"""
        if context:
            thresholds = self.get_contextual_thresholds(context)
        else:
            thresholds = self.get_current_thresholds()

        anomalies = []

        for parameter, value in measurements.items():
            if parameter in thresholds:
                param_thresholds = thresholds[parameter]
                if (
                    value < param_thresholds["lower"]
                    or value > param_thresholds["upper"]
                ):
                    anomalies.append(parameter)

        return anomalies

    def calculate_confidence(
        self, parameter: str, value: float, context: dict[str, Any] = None
    ) -> float:
        """Calculate confidence that a value is normal"""
        if context:
            thresholds = self.get_contextual_thresholds(context)
        else:
            thresholds = self.get_current_thresholds()

        if parameter not in thresholds:
            return 0.5  # Neutral confidence

        param_thresholds = thresholds[parameter]
        lower = param_thresholds["lower"]
        upper = param_thresholds["upper"]

        if lower <= value <= upper:
            center = (lower + upper) / 2
            range_size = upper - lower
            distance_from_center = abs(value - center)
            confidence = 1.0 - (distance_from_center / (range_size / 2))
            return max(0.5, confidence)  # Minimum 50% confidence for normal values
        else:
            if value < lower:
                distance = lower - value
                max_distance = lower - param_thresholds.get(
                    "critical_lower", lower - 100
                )
            else:
                distance = value - upper
                max_distance = (
                    param_thresholds.get("critical_upper", upper + 100) - upper
                )

            confidence = max(0.0, 1.0 - (distance / max_distance))
            return confidence * 0.5  # Scale down confidence for abnormal values

    def export_thresholds(self) -> dict[str, Any]:
        """Export current thresholds for persistence"""
        return {
            "thresholds": self.thresholds,
            "learning_rate": self.learning_rate,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
        }

    def import_thresholds(self, threshold_data: dict[str, Any]) -> None:
        """Import thresholds from saved data"""
        if "thresholds" in threshold_data:
            self.thresholds = threshold_data["thresholds"]
        if "learning_rate" in threshold_data:
            self.learning_rate = threshold_data["learning_rate"]

    def get_threshold_history(
        self, parameter: str, days: int = 30
    ) -> list[dict[str, Any]]:
        """Get threshold history for a parameter (mock implementation)"""
        history = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            history.append(
                {
                    "date": date.isoformat(),
                    "lower": self.thresholds[parameter]["lower"]
                    + np.random.normal(0, 1),
                    "upper": self.thresholds[parameter]["upper"]
                    + np.random.normal(0, 1),
                }
            )
        return history

    def validate_thresholds(self) -> dict[str, list[str]]:
        """Validate current thresholds for consistency"""
        issues = {}

        for parameter, thresholds in self.thresholds.items():
            param_issues = []

            if thresholds["lower"] >= thresholds["upper"]:
                param_issues.append("Lower threshold >= upper threshold")

            if "critical_lower" in thresholds and "critical_upper" in thresholds:
                if thresholds["critical_lower"] >= thresholds["lower"]:
                    param_issues.append("Critical lower >= normal lower")
                if thresholds["critical_upper"] <= thresholds["upper"]:
                    param_issues.append("Critical upper <= normal upper")

            if param_issues:
                issues[parameter] = param_issues

        return issues

    def get_threshold(self, threshold_type: ThresholdType, age: int = None, gender: str = None) -> dict:
        """Get threshold for specific type with demographic adjustments"""
        param_name = threshold_type.value
        
        if param_name not in self.thresholds:
            return {"lower": 0.0, "upper": 100.0}
        
        base_thresholds = self.thresholds[param_name].copy()
        
        if age is not None:
            demographics = {"age": age}
            if gender:
                demographics["gender"] = gender
            adjusted = self.get_adjusted_thresholds(demographics)
            if param_name in adjusted:
                base_thresholds = adjusted[param_name]
        
        return base_thresholds

    def update_threshold(self, threshold_type: ThresholdType, age: int, gender: str, value: float) -> None:
        """Update threshold based on new data point"""
        param_name = threshold_type.value
        
        if param_name in self.thresholds:
            current = self.thresholds[param_name]
            if value < current["lower"]:
                current["lower"] = (1 - self.learning_rate) * current["lower"] + self.learning_rate * value
            elif value > current["upper"]:
                current["upper"] = (1 - self.learning_rate) * current["upper"] + self.learning_rate * value
