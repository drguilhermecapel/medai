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


def test_validate_date_edge_cases():
    """Testa casos extremos de validação de data"""
    from app.services.validation_service import ValidationService
    from datetime import date, timedelta
    
    service = ValidationService()
    
    # Mesma data (válido)
    today = date.today()
    assert service.validate_date_range(today, today) is True
    
    # Data no futuro
    future = today + timedelta(days=30)
    assert service.validate_date_range(today, future) is True
    
    # Data muito no passado
    past = today - timedelta(days=365 * 10)  # 10 anos atrás
    assert service.validate_date_range(past, today) is True


def test_file_validation_comprehensive():
    """Testa validação de arquivos de forma abrangente"""
    from app.services.validation_service import ValidationService
    
    service = ValidationService()
    
    # Extensões permitidas
    allowed_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"]
    
    # Arquivos válidos
    valid_files = ["report.pdf", "image.jpg", "photo.PNG", "document.docx"]
    for file in valid_files:
        assert service.validate_file_type(file, allowed_extensions) is True
    
    # Arquivos inválidos
    invalid_files = ["virus.exe", "script.bat", "hack.sh", "malware.com"]
    for file in invalid_files:
        assert service.validate_file_type(file, allowed_extensions) is False


def test_medical_data_validation():
    """Testa validação de dados médicos específicos"""
    from app.services.validation_service import ValidationService
    
    service = ValidationService()
    
    # Dados médicos válidos
    valid_medical_data = {
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "heart_rate": 72,
        "temperature": 36.5,
        "weight": 70.5,
        "height": 175
    }
    
    assert service.validate_medical_data(valid_medical_data) is True
    
    # Dados médicos inválidos
    invalid_medical_data = {
        "blood_pressure_systolic": 300,  # Muito alto
        "blood_pressure_diastolic": 200,  # Muito alto
        "heart_rate": -10,  # Negativo
        "temperature": 50,  # Impossível
        "weight": -5,  # Negativo
        "height": 0  # Zero
    }
    
    assert service.validate_medical_data(invalid_medical_data) is False


def test_validation_error_handling():
    """Testa tratamento de erros de validação"""
    from app.services.validation_service import ValidationService, ValidationError
    
    service = ValidationService()
    
    # Campo obrigatório vazio
    with pytest.raises(ValidationError) as exc_info:
        service.validate_required_field("", "nome_paciente")
    
    assert "nome_paciente" in str(exc_info.value)
    assert "obrigatório" in str(exc_info.value).lower()
    
    # CPF inválido
    with pytest.raises(ValidationError):
        service.validate_cpf("123.456.789-00")  # CPF inválido
    
    # Email inválido
    with pytest.raises(ValidationError):
        service.validate_email("email_invalido")


def test_batch_validation():
    """Testa validação em lote"""
    from app.services.validation_service import ValidationService
    
    service = ValidationService()
    
    # Lista de CPFs para validar
    cpfs = ["11144477735", "12345678901", "00000000000"]  # Mix de válidos e inválidos
    
    results = service.batch_validate_cpf(cpfs)
    
    assert isinstance(results, list)
    assert len(results) == len(cpfs)
    
    # Primeiro CPF deve ser válido, outros inválidos
    assert results[0] is True
    assert results[1] is False
    assert results[2] is False


def test_complex_validation_rules():
    """Testa regras de validação complexas"""
    from app.services.validation_service import ValidationService
    
    service = ValidationService()
    
    # Validação de senha complexa
    password_rules = {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special": True
    }
    
    # Senha que atende todos os critérios
    strong_password = "MyStr0ng!Pass"
    assert service.validate_password_complexity(strong_password, password_rules) is True
    
    # Senha que não atende critérios
    weak_password = "123456"
    assert service.validate_password_complexity(weak_password, password_rules) is False
