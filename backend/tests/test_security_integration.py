"""
Integration tests for MedAI security system
Tests PHI encryption, audit logging, and RBAC working together
"""
import pytest
from unittest.mock import Mock, patch
from app.security import PHIEncryption, AuditLogger
from app.rbac import MedicalRole, Permission, RBACManager, require_permission


class TestSecurityIntegration:
    """Integration tests for complete security system"""
    
    def test_phi_encryption_with_audit_logging(self, caplog):
        """Test PHI encryption with audit logging"""
        import logging
        
        with caplog.at_level(logging.INFO, logger="medai.audit"):
            # Simulate patient data encryption
            phi = PHIEncryption()
            
            # Encrypt sensitive data
            original_cpf = "12345678901"
            encrypted_cpf = phi.encrypt_phi(original_cpf)
            cpf_hash = phi.create_searchable_hash(original_cpf)
            
            # Log PHI access
            AuditLogger.log_phi_access(
                user_id="doctor123",
                patient_id="patient456",
                fields_accessed=["cpf", "name"],
                ip_address="192.168.1.100"
            )
            
            # Verify encryption worked
            assert encrypted_cpf != original_cpf
            assert len(cpf_hash) == 64
            
            # Verify audit logging worked
            assert len(caplog.records) == 1
            assert "PHI_ACCESS:" in caplog.records[0].message
            assert "doctor123" in caplog.records[0].message
    
    @pytest.mark.asyncio
    async def test_rbac_with_phi_access(self):
        """Test RBAC controlling PHI access"""
        
        @require_permission(Permission.READ_ANY_PATIENT_DATA)
        async def access_patient_phi(
            patient_id: str,
            current_user_role=None,
            current_user_id=None
        ):
            # Simulate accessing encrypted PHI
            phi = PHIEncryption()
            encrypted_data = phi.encrypt_phi("sensitive_medical_data")
            decrypted_data = phi.decrypt_phi(encrypted_data)
            return {"patient_id": patient_id, "data": decrypted_data}
        
        # Doctor should have access
        result = await access_patient_phi(
            patient_id="patient123",
            current_user_role=MedicalRole.DOCTOR,
            current_user_id="doctor456"
        )
        assert result["data"] == "sensitive_medical_data"
        
        # Patient should not have access to other's data
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await access_patient_phi(
                patient_id="patient123",
                current_user_role=MedicalRole.PATIENT,
                current_user_id="patient789"  # Different patient
            )
        assert exc_info.value.status_code == 403
    
    def test_emergency_access_with_audit(self, caplog):
        """Test emergency access with audit logging"""
        import logging
        from app.rbac import EmergencyAccess
        
        with caplog.at_level(logging.INFO, logger="medai.audit"):
            # Grant emergency access
            token = EmergencyAccess.grant_emergency_access(
                user_id="doctor123",
                user_role=MedicalRole.DOCTOR,
                justification="Patient cardiac arrest - immediate access needed"
            )
            
            assert token is not None
            assert "emergency_doctor123_" in token
            
            # Verify audit log was created
            assert len(caplog.records) == 1
            assert "EMERGENCY_ACCESS_GRANTED" in caplog.records[0].message
    
    def test_role_hierarchy_permissions(self):
        """Test role hierarchy and permission inheritance"""
        # Test that higher roles have appropriate permissions
        roles_hierarchy = [
            MedicalRole.PATIENT,
            MedicalRole.NURSE, 
            MedicalRole.DOCTOR,
            MedicalRole.ADMIN
        ]
        
        for i, role in enumerate(roles_hierarchy):
            permissions = RBACManager.get_user_permissions(role)
            
            # Each higher role should have more or equal permissions
            if i > 0:
                prev_role = roles_hierarchy[i-1]
                prev_permissions = RBACManager.get_user_permissions(prev_role)
                
                # Admin has all permissions, others follow specific rules
                if role == MedicalRole.ADMIN:
                    all_permissions = set(Permission.__members__.values())
                    assert permissions == all_permissions
                
                # Doctor should have more permissions than nurse
                elif role == MedicalRole.DOCTOR and prev_role == MedicalRole.NURSE:
                    assert len(permissions) > len(prev_permissions)
                    assert Permission.APPROVE_DIAGNOSTICS in permissions
                    assert Permission.APPROVE_DIAGNOSTICS not in prev_permissions
    
    def test_searchable_hash_security(self):
        """Test searchable hash prevents data leakage"""
        phi = PHIEncryption()
        
        # Create hashes for similar data
        cpf1 = "12345678901"
        cpf2 = "12345678902"  # One digit different
        
        hash1 = phi.create_searchable_hash(cpf1)
        hash2 = phi.create_searchable_hash(cpf2)
        
        # Hashes should be completely different
        assert hash1 != hash2
        assert len(hash1) == len(hash2) == 64
        
        # Hash should not reveal original data
        assert cpf1 not in hash1
        assert cpf2 not in hash2


class TestSecurityCompliance:
    """Test security compliance features"""
    
    def test_phi_encryption_standards(self):
        """Test PHI encryption meets medical standards"""
        phi = PHIEncryption()
        
        # Test with various medical data types
        test_data = [
            "12345678901",  # CPF
            "João da Silva",  # Patient name
            "AB+",  # Blood type
            "Diabetes Type 2",  # Medical condition
            "192.168.1.100",  # IP address (for audit)
        ]
        
        for data in test_data:
            encrypted = phi.encrypt_phi(data)
            decrypted = phi.decrypt_phi(encrypted)
            hash_value = phi.create_searchable_hash(data)
            
            # Verify encryption is working
            assert encrypted != data
            assert decrypted == data
            assert len(hash_value) == 64
            
            # Verify no data leakage in encrypted form
            assert data.lower() not in encrypted.lower()
    
    def test_audit_log_hipaa_compliance(self, caplog):
        """Test audit logging meets HIPAA requirements"""
        import logging
        
        with caplog.at_level(logging.INFO, logger="medai.audit"):
            # Test various audit scenarios
            audit_scenarios = [
                {
                    "action": "view_patient_record",
                    "user_id": "doctor123", 
                    "resource_type": "patient",
                    "resource_id": "patient456",
                    "ip_address": "10.0.0.1"
                },
                {
                    "action": "modify_prescription",
                    "user_id": "doctor123",
                    "resource_type": "prescription", 
                    "resource_id": "rx789",
                    "ip_address": "10.0.0.1"
                },
                {
                    "action": "access_diagnostic_report",
                    "user_id": "nurse456",
                    "resource_type": "diagnostic",
                    "resource_id": "diag101", 
                    "ip_address": "10.0.0.2"
                }
            ]
            
            for scenario in audit_scenarios:
                AuditLogger.log_access(**scenario)
            
            # Verify all actions were logged
            assert len(caplog.records) == len(audit_scenarios)
            
            # Check each log contains required HIPAA elements
            for i, record in enumerate(caplog.records):
                message = record.getMessage()
                scenario = audit_scenarios[i]
                
                # Must contain: timestamp, user, action, resource
                assert "DATA_ACCESS:" in message
                assert scenario["user_id"] in message
                assert scenario["action"] in message
                assert scenario["resource_type"] in message
                assert scenario["ip_address"] in message
    
    def test_access_control_matrix(self):
        """Test complete access control matrix"""
        # Define test scenarios for each role
        test_matrix = {
            MedicalRole.PATIENT: {
                Permission.READ_OWN_PATIENT_DATA: True,
                Permission.READ_ANY_PATIENT_DATA: False,
                Permission.CREATE_DIAGNOSTICS: False,
                Permission.MANAGE_USERS: False,
            },
            MedicalRole.NURSE: {
                Permission.READ_ANY_PATIENT_DATA: True,
                Permission.WRITE_PATIENT_DATA: True,
                Permission.CREATE_DIAGNOSTICS: False,
                Permission.APPROVE_PRESCRIPTIONS: False,
                Permission.MANAGE_USERS: False,
            },
            MedicalRole.DOCTOR: {
                Permission.READ_ANY_PATIENT_DATA: True,
                Permission.CREATE_DIAGNOSTICS: True,
                Permission.APPROVE_PRESCRIPTIONS: True,
                Permission.EMERGENCY_ACCESS: True,
                Permission.MANAGE_USERS: False,
            },
            MedicalRole.ADMIN: {
                Permission.MANAGE_USERS: True,
                Permission.VIEW_AUDIT_LOGS: True,
                Permission.MANAGE_SYSTEM_CONFIG: True,
                Permission.READ_ANY_PATIENT_DATA: True,
            },
            MedicalRole.VIEWER: {
                Permission.READ_ANY_PATIENT_DATA: True,  # Anonymized
                Permission.VIEW_AUDIT_LOGS: True,
                Permission.WRITE_PATIENT_DATA: False,
                Permission.CREATE_DIAGNOSTICS: False,
            }
        }
        
        # Test each role-permission combination
        for role, permissions in test_matrix.items():
            role_perms = RBACManager.get_user_permissions(role)
            
            for permission, should_have in permissions.items():
                has_permission = permission in role_perms
                assert has_permission == should_have, \
                    f"Role {role.value} permission {permission.value} failed: " \
                    f"expected {should_have}, got {has_permission}"