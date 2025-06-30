"""
Tests for validators
"""
import pytest
from app.standalone.validators import (
    validate_cpf, validate_email, validate_phone,
    format_cpf, format_phone
)

class TestValidators:
    """Test validator functions"""
    
    def test_validate_cpf_valid(self):
        # Valid CPFs
        assert validate_cpf("11144477735") == True
        assert validate_cpf("111.444.777-35") == True
        
    def test_validate_cpf_invalid(self):
        # Invalid CPFs
        assert validate_cpf("00000000000") == False
        assert validate_cpf("11111111111") == False
        assert validate_cpf("12345678901") == False
        assert validate_cpf("123") == False
        assert validate_cpf("") == False
        assert validate_cpf(None) == False
    
    def test_validate_email(self):
        # Valid emails
        assert validate_email("user@example.com") == True
        assert validate_email("test.user@domain.co.uk") == True
        
        # Invalid emails
        assert validate_email("invalid") == False
        assert validate_email("@domain.com") == False
        assert validate_email("user@") == False
        assert validate_email("") == False
        assert validate_email(None) == False
    
    def test_validate_phone(self):
        # Valid phones
        assert validate_phone("1234567890") == True
        assert validate_phone("12345678901") == True
        assert validate_phone("(11) 98765-4321") == True
        
        # Invalid phones
        assert validate_phone("123") == False
        assert validate_phone("") == False
        assert validate_phone(None) == False
    
    def test_format_cpf(self):
        assert format_cpf("11144477735") == "111.444.777-35"
        assert format_cpf("111.444.777-35") == "111.444.777-35"
        assert format_cpf("123") == "123"  # Invalid length
    
    def test_format_phone(self):
        assert format_phone("11987654321") == "(11) 98765-4321"
        assert format_phone("1134567890") == "(11) 3456-7890"
        assert format_phone("123") == "123"  # Invalid length
