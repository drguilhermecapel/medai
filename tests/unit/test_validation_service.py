import pytest
from app.services.validation_service import (
    validate_cpf, validate_phone, validate_email,
    PatientValidator, ValidationService
)

def test_validate_cpf():
    assert validate_cpf("11111111111")
    assert validate_cpf("12345678909")
    assert not validate_cpf("123")
    assert not validate_cpf("")

def test_validate_phone():
    assert validate_phone("11999999999")
    assert validate_phone("1199999999")
    assert not validate_phone("123")

def test_validate_email():
    assert validate_email("test@test.com")
    assert not validate_email("invalid")

def test_patient_validator():
    validator = PatientValidator()
    result = validator.validate({"name": "Test User"})
    assert result.is_valid

def test_validation_service():
    service = ValidationService()
    result = service.validate_patient_record({})
    assert result.is_valid
