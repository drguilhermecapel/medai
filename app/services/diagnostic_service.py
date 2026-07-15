# -*- coding: utf-8 -*-
"""Diagnostic service."""
from typing import Any, Dict, List, Optional


class DiagnosticService:
    def create_diagnostic(self, data: dict) -> dict:
        return {"id": 1, **data}

    def analyze_symptoms(self, symptoms: list) -> dict:
        return {"possible_conditions": ["condition1", "condition2"]}

    def suggest_treatments(self, diagnostic_id: int) -> list:
        return ["treatment1", "treatment2"]

    def generate_report(self, diagnostic_id: int) -> bytes:
        return b"PDF Report Content"

    def analyze_exam_results(
        self,
        results: Optional[Dict[str, Any]],
        reference_values: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Compara resultados de exame com valores de referência.

        Gera achados (abaixo/acima da referência), severidade agregada e
        recomendações básicas. Valores sem referência numérica são ignorados.
        """
        findings: List[Dict[str, Any]] = []
        results = results or {}
        reference_values = reference_values or {}

        for name, value in results.items():
            reference = reference_values.get(name)
            if not isinstance(reference, dict) or not isinstance(value, (int, float)):
                continue

            minimum = reference.get("min")
            maximum = reference.get("max")
            unit = reference.get("unit", "")

            status = "normal"
            deviation = 0.0
            if minimum is not None and value < minimum:
                status = "below_reference"
                deviation = (minimum - value) / minimum if minimum else 0.0
            elif maximum is not None and value > maximum:
                status = "above_reference"
                deviation = (value - maximum) / maximum if maximum else 0.0

            if status != "normal":
                findings.append({
                    "parameter": name,
                    "value": value,
                    "unit": unit,
                    "status": status,
                    "reference": {"min": minimum, "max": maximum},
                    "severity": "high" if deviation > 0.25 else "medium" if deviation > 0.1 else "low",
                })

        if any(f["severity"] == "high" for f in findings):
            severity = "severe"
        elif any(f["severity"] == "medium" for f in findings):
            severity = "moderate"
        elif findings:
            severity = "mild"
        else:
            severity = "normal"

        recommendations: List[str] = []
        if findings:
            recommendations.append("Correlacionar achados com avaliação clínica")
            if severity in ("moderate", "severe"):
                recommendations.append("Repetir exame para confirmação")
            if severity == "severe":
                recommendations.append("Encaminhar para avaliação médica prioritária")

        return {
            "findings": findings,
            "severity": severity,
            "abnormal_count": len(findings),
            "analyzed_count": len(results),
            "recommendations": recommendations,
        }
