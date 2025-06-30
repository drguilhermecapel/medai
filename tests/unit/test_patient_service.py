import pytest
from app.services.patient_service import PatientService

def test_create_patient():
    service = PatientService()
    result = service.create_patient({"name": "Test"})
    assert result["name"] == "Test"
    assert "id" in result

def test_get_patient():
    service = PatientService()
    result = service.get_patient(1)
    assert result["id"] == 1

def test_update_patient():
    service = PatientService()
    result = service.update_patient(1, {"phone": "123"})
    assert result["phone"] == "123"

def test_list_patients():
    service = PatientService()
    result = service.list_patients()
    assert isinstance(result, list)
