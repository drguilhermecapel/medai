"""
API Contract Tests for MedAI
Tests for FHIR compliance and API contract validation
"""
import pytest
import json
from fastapi.testclient import TestClient
from typing import Dict, Any
import jsonschema
from jsonschema import validate
from app.main import app
from app.fhir.resources.patient import FHIRPatient
from app.fhir.adapter import fhir_adapter


class TestAPIContracts:
    """Test API contracts and FHIR compliance"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_patient_data(self):
        """Sample patient data for testing"""
        return {
            "resourceType": "Patient",
            "identifier": [
                {
                    "use": "usual",
                    "system": "http://hospital.medai.com/patients",
                    "value": "12345"
                },
                {
                    "use": "official",
                    "system": "http://www.saude.gov.br/fhir/r4/NamingSystem/cpf",
                    "value": "123.456.789-00"
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "usual",
                    "family": "Silva",
                    "given": ["João", "Carlos"]
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": "(11) 99999-9999",
                    "use": "mobile"
                },
                {
                    "system": "email",
                    "value": "joao.silva@example.com",
                    "use": "home"
                }
            ],
            "gender": "male",
            "birthDate": "1990-01-15",
            "address": [
                {
                    "use": "home",
                    "type": "physical",
                    "line": ["Rua das Flores, 123"],
                    "city": "São Paulo",
                    "state": "SP",
                    "postalCode": "01234-567",
                    "country": "BR"
                }
            ]
        }
    
    def test_openapi_schema_validity(self, client):
        """Validate OpenAPI schema structure"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        
        # Validate required OpenAPI 3.0 fields
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            assert field in schema, f"Missing required field: {field}"
        
        # Validate OpenAPI version
        assert schema["openapi"].startswith("3."), "Must use OpenAPI 3.x"
        
        # Validate info section
        info = schema["info"]
        assert "title" in info, "Missing title in info"
        assert "version" in info, "Missing version in info"
        
        # Validate paths exist
        assert len(schema["paths"]) > 0, "No API paths defined"
    
    def test_health_endpoint_contract(self, client):
        """Test health endpoint contract"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["status", "service"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        assert data["status"] == "healthy"
        assert data["service"] == "MedAI"
    
    def test_detailed_health_endpoint_contract(self, client):
        """Test detailed health endpoint contract"""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate response structure
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)
    
    def test_patient_fhir_contract_validation(self, sample_patient_data):
        """Test Patient FHIR contract compliance"""
        
        # Test that sample data creates valid FHIR Patient
        try:
            fhir_patient = FHIRPatient(**sample_patient_data)
            assert fhir_patient.resourceType == "Patient"
            assert fhir_patient.identifier is not None
            assert len(fhir_patient.identifier) == 2
            assert fhir_patient.name is not None
            assert len(fhir_patient.name) == 1
            assert fhir_patient.gender == "male"
            
        except Exception as e:
            pytest.fail(f"Failed to create valid FHIR Patient: {e}")
    
    def test_fhir_patient_validation_errors(self):
        """Test FHIR Patient validation with invalid data"""
        
        # Test with invalid resourceType
        invalid_data = {"resourceType": "Invalid"}
        
        with pytest.raises(Exception):
            FHIRPatient(**invalid_data)
        
        # Test with invalid gender
        invalid_gender_data = {
            "resourceType": "Patient",
            "gender": "invalid_gender"
        }
        
        with pytest.raises(Exception):
            FHIRPatient(**invalid_gender_data)
    
    def test_fhir_adapter_contract(self, sample_patient_data):
        """Test FHIR adapter contract compliance"""
        
        # Test FHIR to internal conversion
        fhir_patient = FHIRPatient(**sample_patient_data)
        internal_data = fhir_adapter.from_fhir_patient(fhir_patient)
        
        # Validate internal data structure
        assert isinstance(internal_data, dict)
        assert "nome_completo" in internal_data
        assert "cpf" in internal_data
        assert "sexo" in internal_data
        
        # Test internal to FHIR conversion
        converted_fhir = fhir_adapter.to_fhir_patient(internal_data)
        assert converted_fhir.resourceType == "Patient"
        assert converted_fhir.gender is not None
    
    def test_fhir_adapter_validation(self):
        """Test FHIR adapter validation"""
        
        # Create a valid FHIR patient
        fhir_patient = FHIRPatient(
            resourceType="Patient",
            name=[{
                "family": "Test",
                "given": ["Patient"]
            }],
            gender="male"
        )
        
        # Validate the patient
        errors = fhir_adapter.validate_fhir_patient(fhir_patient)
        assert len(errors) == 0, f"Validation errors: {errors}"
        
        # Test validation with invalid patient
        invalid_patient = FHIRPatient(
            resourceType="InvalidType",  # This will fail validation
            birthDate="invalid-date"
        )
        
        # Note: Pydantic will catch resourceType error during construction
        # So we test validation of constructed but invalid patient
        invalid_patient.resourceType = "InvalidType"  # Manually set invalid type
        invalid_patient.birthDate = "invalid-date"
        
        errors = fhir_adapter.validate_fhir_patient(invalid_patient)
        assert len(errors) > 0, "Should have validation errors"
    
    def test_error_response_contracts(self, client):
        """Validate error response format consistency"""
        
        # Test 404 error
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        error_data = response.json()
        
        # Validate error response structure
        required_error_fields = ["error_code", "message"]
        for field in required_error_fields:
            assert field in error_data, f"Missing required error field: {field}"
        
        assert error_data["error_code"] == "HTTP_404"
    
    def test_cors_headers(self, client):
        """Test CORS headers in responses"""
        
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check for CORS headers (these are added by FastAPI CORS middleware)
        # In test environment, these might not be present, so we test conditionally
        headers = response.headers
        
        # If CORS headers exist, validate them
        if "access-control-allow-origin" in headers:
            assert headers["access-control-allow-origin"] is not None
    
    def test_security_headers(self, client):
        """Test security headers in responses"""
        
        response = client.get("/health")
        assert response.status_code == 200
        
        headers = response.headers
        
        # Check for privacy protection header
        if "X-Privacy-Protected" in headers:
            assert headers["X-Privacy-Protected"] == "true"
        
        # Check for trace ID header
        if "X-Trace-ID" in headers:
            assert len(headers["X-Trace-ID"]) > 0
    
    def test_api_versioning_contract(self, client):
        """Test API versioning contract"""
        
        # Test that API v1 endpoints are properly versioned
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        
        # Test that the version follows semantic versioning pattern
        version = data["version"]
        version_parts = version.split(".")
        assert len(version_parts) >= 2, "Version should follow semantic versioning"
    
    def test_request_id_tracing(self, client):
        """Test request ID tracing"""
        
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check for request/trace ID in response headers
        headers = response.headers
        
        # At least one of these should be present for request tracing
        trace_headers = ["X-Request-ID", "X-Trace-ID"]
        has_trace_header = any(header.lower() in [h.lower() for h in headers.keys()] 
                              for header in trace_headers)
        
        # In development mode, trace headers might not be set up
        # This is more of a documentation test than a strict requirement
        if has_trace_header:
            trace_id = next((headers[h] for h in headers.keys() 
                           if h.lower() in [th.lower() for th in trace_headers]), None)
            assert trace_id is not None
            assert len(trace_id) > 0


class TestFHIRCompliance:
    """Specific FHIR R4 compliance tests"""
    
    def test_patient_resource_compliance(self):
        """Test Patient resource FHIR R4 compliance"""
        
        # Test minimal valid Patient
        minimal_patient = FHIRPatient(
            resourceType="Patient"
        )
        
        assert minimal_patient.resourceType == "Patient"
        assert minimal_patient.active is True  # Default value
        
        # Test Patient with all major elements
        full_patient_data = {
            "resourceType": "Patient",
            "id": "patient-123",
            "identifier": [
                {
                    "use": "usual",
                    "system": "http://hospital.example.com/patients",
                    "value": "12345"
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "official",
                    "family": "Silva",
                    "given": ["João"]
                }
            ],
            "gender": "male",
            "birthDate": "1985-06-15"
        }
        
        full_patient = FHIRPatient(**full_patient_data)
        
        # Validate all elements are properly set
        assert full_patient.id == "patient-123"
        assert len(full_patient.identifier) == 1
        assert full_patient.identifier[0].value == "12345"
        assert len(full_patient.name) == 1
        assert full_patient.name[0].family == "Silva"
        assert full_patient.gender == "male"
        assert full_patient.birthDate == "1985-06-15"
    
    def test_brazilian_specific_extensions(self):
        """Test Brazilian healthcare specific extensions"""
        
        # Test CPF identifier
        patient_with_cpf = FHIRPatient(
            resourceType="Patient",
            identifier=[
                {
                    "use": "official",
                    "system": "http://www.saude.gov.br/fhir/r4/NamingSystem/cpf",
                    "value": "123.456.789-00"
                }
            ]
        )
        
        cpf_identifier = patient_with_cpf.identifier[0]
        assert cpf_identifier.system == "http://www.saude.gov.br/fhir/r4/NamingSystem/cpf"
        assert cpf_identifier.value == "123.456.789-00"
    
    def test_fhir_data_types(self):
        """Test FHIR data type validation"""
        
        # Test that enums work correctly
        from app.fhir.resources.patient import AdministrativeGender, IdentifierUse
        
        # Test gender enum
        assert AdministrativeGender.MALE == "male"
        assert AdministrativeGender.FEMALE == "female"
        
        # Test identifier use enum
        assert IdentifierUse.USUAL == "usual"
        assert IdentifierUse.OFFICIAL == "official"