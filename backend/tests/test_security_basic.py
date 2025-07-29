"""
Simple security tests for PHI encryption functionality
"""
import pytest
from app.security import PHIEncryption, AuditLogger
import logging


class TestPHIEncryption:
    """Test PHI encryption functionality without database dependencies"""
    
    def test_phi_encryption_basic(self):
        """Test basic PHI encryption/decryption"""
        phi = PHIEncryption()
        original_data = "12345678901"  # CPF
        
        # Encrypt
        encrypted = phi.encrypt_phi(original_data)
        assert encrypted != original_data
        assert len(encrypted) > len(original_data)
        
        # Decrypt
        decrypted = phi.decrypt_phi(encrypted)
        assert decrypted == original_data
    
    def test_phi_encryption_empty_data(self):
        """Test encryption with empty data"""
        phi = PHIEncryption()
        
        assert phi.encrypt_phi("") == ""
        assert phi.decrypt_phi("") == ""
    
    def test_searchable_hash_consistency(self):
        """Test searchable hash creates consistent results"""
        phi = PHIEncryption()
        data = "João Silva"
        
        hash1 = phi.create_searchable_hash(data)
        hash2 = phi.create_searchable_hash(data)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length
    
    def test_searchable_hash_case_insensitive(self):
        """Test hash is case insensitive"""
        phi = PHIEncryption()
        
        hash1 = phi.create_searchable_hash("João Silva")
        hash2 = phi.create_searchable_hash("joão silva")
        
        assert hash1 == hash2


class TestAuditLogging:
    """Test audit logging functionality"""
    
    def test_audit_logger_access_logging(self, caplog):
        """Test AuditLogger access logging"""
        with caplog.at_level(logging.INFO, logger="medai.audit"):
            AuditLogger.log_access(
                user_id="user123",
                action="view_patient", 
                resource_type="patient",
                resource_id="pat456",
                ip_address="192.168.1.1"
            )
        
        assert len(caplog.records) == 1
        assert "DATA_ACCESS:" in caplog.records[0].message
        assert "user123" in caplog.records[0].message
        assert "view_patient" in caplog.records[0].message
    
    def test_phi_access_logging(self, caplog):
        """Test PHI access logging"""
        with caplog.at_level(logging.WARNING, logger="medai.audit"):
            AuditLogger.log_phi_access(
                user_id="doctor123",
                patient_id="pat456", 
                fields_accessed=["cpf", "name", "medical_record"],
                ip_address="10.0.0.1"
            )
        
        assert len(caplog.records) == 1
        assert "PHI_ACCESS:" in caplog.records[0].message
        assert "doctor123" in caplog.records[0].message
        assert "severity" in caplog.records[0].message


class TestSecurityMiddleware:
    """Test security middleware components"""
    
    def test_security_headers_creation(self):
        """Test security headers are properly configured"""
        from app.security import security_headers
        
        headers = security_headers.get_headers()
        
        # Check for critical security headers
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in headers
        assert headers["X-Frame-Options"] == "DENY"
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        
    def test_phi_encryption_different_keys(self):
        """Test PHI encryption with different keys produces different results"""
        phi1 = PHIEncryption("key1")
        phi2 = PHIEncryption("key2")
        
        data = "sensitive data"
        
        encrypted1 = phi1.encrypt_phi(data)
        encrypted2 = phi2.encrypt_phi(data)
        
        # Different keys should produce different encrypted results
        assert encrypted1 != encrypted2
        
        # But each should decrypt correctly with their own key
        assert phi1.decrypt_phi(encrypted1) == data
        assert phi2.decrypt_phi(encrypted2) == data
        
        # Cross-decryption should fail silently
        assert phi1.decrypt_phi(encrypted2) == ""
        assert phi2.decrypt_phi(encrypted1) == ""