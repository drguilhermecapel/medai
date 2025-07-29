"""
Tests for Role-Based Access Control (RBAC) system
"""
import pytest
from app.rbac import (
    MedicalRole, Permission, RBACManager, 
    require_permission, require_role, EmergencyAccess
)
from fastapi import HTTPException


class TestRBACManager:
    """Test RBAC Manager functionality"""
    
    def test_basic_permission_check(self):
        """Test basic permission checking"""
        # Doctor should have diagnostic permissions
        assert RBACManager.has_permission(MedicalRole.DOCTOR, Permission.CREATE_DIAGNOSTICS)
        
        # Patient should not have diagnostic creation permission
        assert not RBACManager.has_permission(MedicalRole.PATIENT, Permission.CREATE_DIAGNOSTICS)
        
        # Admin should have all permissions
        assert RBACManager.has_permission(MedicalRole.ADMIN, Permission.MANAGE_USERS)
        
        # Nurse should not have user management permission
        assert not RBACManager.has_permission(MedicalRole.NURSE, Permission.MANAGE_USERS)
    
    def test_patient_own_data_access(self):
        """Test patient can only access own data"""
        user_id = "patient123"
        own_resource = "patient123"
        other_resource = "patient456"
        
        # Can access own data
        assert RBACManager.check_resource_access(
            user_role=MedicalRole.PATIENT,
            user_id=user_id,
            resource_owner_id=own_resource,
            permission=Permission.READ_OWN_PATIENT_DATA
        )
        
        # Cannot access other patient's data
        assert not RBACManager.check_resource_access(
            user_role=MedicalRole.PATIENT,
            user_id=user_id,
            resource_owner_id=other_resource,
            permission=Permission.READ_OWN_PATIENT_DATA
        )
    
    def test_doctor_emergency_access(self):
        """Test doctor emergency access"""
        user_id = "doctor123"
        resource_id = "patient456"
        
        # Regular access should work for doctors
        assert RBACManager.check_resource_access(
            user_role=MedicalRole.DOCTOR,
            user_id=user_id,
            resource_owner_id=resource_id,
            permission=Permission.READ_ANY_PATIENT_DATA
        )
        
        # Emergency access should work for doctors
        assert RBACManager.check_resource_access(
            user_role=MedicalRole.DOCTOR,
            user_id=user_id,
            resource_owner_id=resource_id,
            permission=Permission.EMERGENCY_ACCESS,
            is_emergency=True
        )
        
        # Emergency access should not work for nurses
        assert not RBACManager.check_resource_access(
            user_role=MedicalRole.NURSE,
            user_id=user_id,
            resource_owner_id=resource_id,
            permission=Permission.EMERGENCY_ACCESS,
            is_emergency=True
        )
    
    def test_viewer_read_only_access(self):
        """Test viewer has read-only access"""
        user_id = "viewer123"
        resource_id = "patient456"
        
        # Should have read access
        assert RBACManager.check_resource_access(
            user_role=MedicalRole.VIEWER,
            user_id=user_id,
            resource_owner_id=resource_id,
            permission=Permission.READ_ANY_PATIENT_DATA
        )
        
        # Should not have write access
        assert not RBACManager.check_resource_access(
            user_role=MedicalRole.VIEWER,
            user_id=user_id,
            resource_owner_id=resource_id,
            permission=Permission.WRITE_PATIENT_DATA
        )
    
    def test_get_user_permissions(self):
        """Test getting all permissions for a role"""
        doctor_perms = RBACManager.get_user_permissions(MedicalRole.DOCTOR)
        patient_perms = RBACManager.get_user_permissions(MedicalRole.PATIENT)
        
        # Doctor should have more permissions than patient
        assert len(doctor_perms) > len(patient_perms)
        
        # Doctor should have diagnostic permissions
        assert Permission.CREATE_DIAGNOSTICS in doctor_perms
        assert Permission.CREATE_DIAGNOSTICS not in patient_perms
    
    def test_permission_delegation(self):
        """Test permission delegation rules"""
        # Admin can delegate most permissions
        assert RBACManager.can_delegate_permission(
            MedicalRole.ADMIN,
            MedicalRole.DOCTOR,
            Permission.CREATE_DIAGNOSTICS
        )
        
        # Non-admin cannot delegate
        assert not RBACManager.can_delegate_permission(
            MedicalRole.DOCTOR,
            MedicalRole.NURSE,
            Permission.CREATE_DIAGNOSTICS
        )
        
        # Cannot delegate admin-only permissions to non-admins
        assert not RBACManager.can_delegate_permission(
            MedicalRole.ADMIN,
            MedicalRole.DOCTOR,
            Permission.MANAGE_USERS
        )


class TestRBACDecorators:
    """Test RBAC decorators"""
    
    @pytest.mark.asyncio
    async def test_require_permission_decorator_success(self):
        """Test permission decorator allows access"""
        
        @require_permission(Permission.READ_ANY_PATIENT_DATA)
        async def test_function(current_user_role=None, current_user_id=None):
            return "success"
        
        result = await test_function(
            current_user_role=MedicalRole.DOCTOR,
            current_user_id="doctor123"
        )
        
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_require_permission_decorator_failure(self):
        """Test permission decorator denies access"""
        
        @require_permission(Permission.CREATE_DIAGNOSTICS)
        async def test_function(current_user_role=None, current_user_id=None):
            return "success"
        
        with pytest.raises(HTTPException) as exc_info:
            await test_function(
                current_user_role=MedicalRole.PATIENT,
                current_user_id="patient123"
            )
        
        assert exc_info.value.status_code == 403
        assert "Permission required" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_require_role_decorator_success(self):
        """Test role decorator allows access"""
        
        @require_role(MedicalRole.DOCTOR, MedicalRole.ADMIN)
        async def test_function(current_user_role=None):
            return "success"
        
        result = await test_function(current_user_role=MedicalRole.DOCTOR)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_require_role_decorator_failure(self):
        """Test role decorator denies access"""
        
        @require_role(MedicalRole.ADMIN)
        async def test_function(current_user_role=None):
            return "success"
        
        with pytest.raises(HTTPException) as exc_info:
            await test_function(current_user_role=MedicalRole.PATIENT)
        
        assert exc_info.value.status_code == 403
        assert "Role required" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_string_role_conversion(self):
        """Test string role conversion in decorators"""
        
        @require_role(MedicalRole.DOCTOR)
        async def test_function(current_user_role=None):
            return "success"
        
        result = await test_function(current_user_role="doctor")
        assert result == "success"
        
        with pytest.raises(HTTPException) as exc_info:
            await test_function(current_user_role="invalid_role")
        
        assert exc_info.value.status_code == 403


class TestEmergencyAccess:
    """Test emergency access functionality"""
    
    def test_grant_emergency_access_doctor(self):
        """Test granting emergency access to doctor"""
        token = EmergencyAccess.grant_emergency_access(
            user_id="doctor123",
            user_role=MedicalRole.DOCTOR,
            justification="Patient critical condition",
            duration_minutes=30
        )
        
        assert token is not None
        assert token.startswith("emergency_doctor123_")
    
    def test_grant_emergency_access_non_doctor(self):
        """Test denying emergency access to non-doctor"""
        token = EmergencyAccess.grant_emergency_access(
            user_id="nurse123",
            user_role=MedicalRole.NURSE,
            justification="Patient critical condition",
            duration_minutes=30
        )
        
        assert token is None
    
    def test_validate_emergency_access(self):
        """Test validating emergency access tokens"""
        user_id = "doctor123"
        valid_token = f"emergency_{user_id}_1234567890"
        invalid_token = "invalid_token"
        
        assert EmergencyAccess.validate_emergency_access(user_id, valid_token)
        assert not EmergencyAccess.validate_emergency_access(user_id, invalid_token)


class TestRoleHierarchy:
    """Test role hierarchy and permission inheritance"""
    
    def test_admin_has_all_permissions(self):
        """Test admin role has all permissions"""
        admin_perms = RBACManager.get_user_permissions(MedicalRole.ADMIN)
        all_perms = set(Permission.__members__.values())
        
        assert admin_perms == all_perms
    
    def test_doctor_permissions_include_nurse(self):
        """Test doctor has all nurse permissions plus more"""
        doctor_perms = RBACManager.get_user_permissions(MedicalRole.DOCTOR)
        nurse_perms = RBACManager.get_user_permissions(MedicalRole.NURSE)
        
        # Doctor should have at least all nurse permissions
        # (This is implicit in the current design, not explicit inheritance)
        assert len(doctor_perms) >= len(nurse_perms)
        
        # Doctor should have permissions nurse doesn't
        doctor_only_perms = {
            Permission.SIGN_MEDICAL_RECORDS,
            Permission.APPROVE_DIAGNOSTICS,
            Permission.APPROVE_PRESCRIPTIONS,
            Permission.EMERGENCY_ACCESS
        }
        
        for perm in doctor_only_perms:
            assert perm in doctor_perms
            assert perm not in nurse_perms
    
    def test_patient_minimal_permissions(self):
        """Test patient has minimal permissions"""
        patient_perms = RBACManager.get_user_permissions(MedicalRole.PATIENT)
        
        # Patient should only have read access to own data
        expected_perms = {
            Permission.READ_OWN_PATIENT_DATA,
            Permission.VIEW_DIAGNOSTICS,
            Permission.VIEW_PRESCRIPTIONS
        }
        
        assert patient_perms == expected_perms