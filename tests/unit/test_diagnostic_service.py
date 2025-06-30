import pytest
from app.services.diagnostic_service import DiagnosticService

def test_create_diagnostic():
    service = DiagnosticService()
    result = service.create_diagnostic({"text": "Test"})
    assert result["text"] == "Test"

def test_analyze_symptoms():
    service = DiagnosticService()
    result = service.analyze_symptoms(["fever"])
    assert "possible_conditions" in result

def test_suggest_treatments():
    service = DiagnosticService()
    treatments = service.suggest_treatments(1)
    assert len(treatments) > 0

def test_generate_report():
    service = DiagnosticService()
    report = service.generate_report(1)
    assert isinstance(report, bytes)
