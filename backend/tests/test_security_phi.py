"""
Security tests for PHI encryption and audit logging
"""
import pytest
from app.security import PHIEncryption, audit_log, AuditLogger
from app.models.patient import Patient
from app.models.user import User
from sqlalchemy.orm import Session


class TestPHIEncryption:
    """Test PHI encryption functionality"""
    
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
        assert phi.encrypt_phi(None) == ""
    
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


class TestPatientEncryption:
    """Test Patient model encryption features"""
    
    def test_set_cpf_encryption(self, db_session: Session):
        """Test CPF encryption in Patient model"""
        patient = Patient(
            medical_record_number="TEST001",
            birth_date="1990-01-01",
            gender="M"
        )
        
        cpf = "12345678901"
        patient.set_cpf(cpf)
        
        # CPF should be encrypted
        assert patient.cpf != cpf
        assert patient.cpf is not None
        
        # Hash should be created
        assert patient.cpf_hash is not None
        assert len(patient.cpf_hash) == 64
        
        # Should be able to decrypt
        assert patient.get_cpf() == cpf
    
    def test_find_by_cpf_hash(self, db_session: Session):
        """Test finding patient by CPF using hash"""
        # Create patient with encrypted CPF
        patient = Patient(
            medical_record_number="TEST002",
            birth_date="1990-01-01",
            gender="F"
        )
        patient.set_cpf("98765432100")
        
        db_session.add(patient)
        db_session.commit()
        
        # Should find by CPF
        found = Patient.find_by_cpf(db_session, "98765432100")
        assert found is not None
        assert found.id == patient.id
        
        # Should not find with wrong CPF
        not_found = Patient.find_by_cpf(db_session, "11111111111")
        assert not_found is None
    
    def test_name_hash_functionality(self, db_session: Session):
        """Test name hash for searchability"""
        patient = Patient(
            medical_record_number="TEST003",
            birth_date="1990-01-01",
            gender="M"
        )
        
        full_name = "João da Silva"
        patient.update_name_hash(full_name)
        
        assert patient.name_hash is not None
        assert len(patient.name_hash) == 64


class TestAuditLogging:
    """Test audit logging functionality"""
    
    @pytest.mark.asyncio
    async def test_audit_log_decorator(self):
        """Test audit log decorator"""
        log_entries = []
        
        # Mock the audit logger
        import logging
        audit_logger = logging.getLogger("medai.audit")
        
        # Create a handler to capture log entries
        class TestHandler(logging.Handler):
            def emit(self, record):
                log_entries.append(record.getMessage())
        
        test_handler = TestHandler()
        audit_logger.addHandler(test_handler)
        audit_logger.setLevel(logging.INFO)
        
        @audit_log("test_action", "patient")
        async def test_function(current_user_id="user123", resource_id="pat456"):
            return "success"
        
        result = await test_function()
        
        assert result == "success"
        assert len(log_entries) >= 2  # Start and success logs
        assert "AUDIT: action=test_action" in log_entries[0]
        assert "user_id=user123" in log_entries[0]
    
    def test_audit_logger_access_logging(self):
        """Test AuditLogger access logging"""
        log_entries = []
        
        # Mock the audit logger
        import logging
        audit_logger = logging.getLogger("medai.audit")
        
        class TestHandler(logging.Handler):
            def emit(self, record):
                log_entries.append(record.getMessage())
        
        test_handler = TestHandler()
        audit_logger.addHandler(test_handler)
        audit_logger.setLevel(logging.INFO)
        
        AuditLogger.log_access(
            user_id="user123",
            action="view_patient",
            resource_type="patient",
            resource_id="pat456",
            ip_address="192.168.1.1"
        )
        
        assert len(log_entries) == 1
        assert "DATA_ACCESS:" in log_entries[0]
        assert "user123" in log_entries[0]
        assert "view_patient" in log_entries[0]
    
    def test_phi_access_logging(self):
        """Test PHI access logging"""
        log_entries = []
        
        # Mock the audit logger
        import logging
        audit_logger = logging.getLogger("medai.audit")
        
        class TestHandler(logging.Handler):
            def emit(self, record):
                log_entries.append(record.getMessage())
        
        test_handler = TestHandler()
        audit_logger.addHandler(test_handler)
        audit_logger.setLevel(logging.WARNING)
        
        AuditLogger.log_phi_access(
            user_id="doctor123",
            patient_id="pat456",
            fields_accessed=["cpf", "name", "medical_record"],
            ip_address="10.0.0.1"
        )
        
        assert len(log_entries) == 1
        assert "PHI_ACCESS:" in log_entries[0]
        assert "doctor123" in log_entries[0]
        assert "severity" in log_entries[0]


@pytest.fixture
def db_session():
    """Mock database session for testing"""
    from unittest.mock import Mock
    session = Mock(spec=Session)
    session.add = Mock()
    session.commit = Mock()
    session.query = Mock()
    return session