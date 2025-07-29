"""
Enhanced Role-Based Access Control (RBAC) for MedAI
Implements granular permissions for healthcare roles
"""
from enum import Enum
from typing import Dict, List, Set, Optional
from functools import wraps
from fastapi import HTTPException, status

class MedicalRole(Enum):
    """Medical system roles with hierarchy"""
    PATIENT = "patient"
    NURSE = "nurse" 
    DOCTOR = "doctor"
    ADMIN = "admin"
    VIEWER = "viewer"  # Read-only access for auditors/researchers


class Permission(Enum):
    """Granular permissions for medical operations"""
    # Patient data permissions
    READ_OWN_PATIENT_DATA = "read_own_patient_data"
    READ_ANY_PATIENT_DATA = "read_any_patient_data"
    WRITE_PATIENT_DATA = "write_patient_data"
    DELETE_PATIENT_DATA = "delete_patient_data"
    
    # Medical record permissions
    READ_MEDICAL_RECORDS = "read_medical_records"
    WRITE_MEDICAL_RECORDS = "write_medical_records"
    SIGN_MEDICAL_RECORDS = "sign_medical_records"
    
    # Diagnostic permissions
    VIEW_DIAGNOSTICS = "view_diagnostics"
    CREATE_DIAGNOSTICS = "create_diagnostics"
    APPROVE_DIAGNOSTICS = "approve_diagnostics"
    
    # Prescription permissions
    VIEW_PRESCRIPTIONS = "view_prescriptions"
    CREATE_PRESCRIPTIONS = "create_prescriptions"
    APPROVE_PRESCRIPTIONS = "approve_prescriptions"
    
    # Administrative permissions
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM_CONFIG = "manage_system_config"
    
    # Emergency permissions
    EMERGENCY_ACCESS = "emergency_access"
    BREAK_GLASS_ACCESS = "break_glass_access"


# Role-to-Permission mapping
ROLE_PERMISSIONS: Dict[MedicalRole, Set[Permission]] = {
    MedicalRole.PATIENT: {
        Permission.READ_OWN_PATIENT_DATA,
        Permission.VIEW_DIAGNOSTICS,  # Own diagnostics only
        Permission.VIEW_PRESCRIPTIONS,  # Own prescriptions only
    },
    
    MedicalRole.NURSE: {
        Permission.READ_ANY_PATIENT_DATA,
        Permission.WRITE_PATIENT_DATA,  # Limited scope
        Permission.READ_MEDICAL_RECORDS,
        Permission.WRITE_MEDICAL_RECORDS,  # Notes, observations
        Permission.VIEW_DIAGNOSTICS,
        Permission.VIEW_PRESCRIPTIONS,
    },
    
    MedicalRole.DOCTOR: {
        Permission.READ_ANY_PATIENT_DATA,
        Permission.WRITE_PATIENT_DATA,
        Permission.READ_MEDICAL_RECORDS,
        Permission.WRITE_MEDICAL_RECORDS,
        Permission.SIGN_MEDICAL_RECORDS,
        Permission.VIEW_DIAGNOSTICS,
        Permission.CREATE_DIAGNOSTICS,
        Permission.APPROVE_DIAGNOSTICS,
        Permission.VIEW_PRESCRIPTIONS,
        Permission.CREATE_PRESCRIPTIONS,
        Permission.APPROVE_PRESCRIPTIONS,
        Permission.EMERGENCY_ACCESS,
    },
    
    MedicalRole.ADMIN: {
        # Admins have all permissions
        *Permission.__members__.values()
    },
    
    MedicalRole.VIEWER: {
        Permission.READ_ANY_PATIENT_DATA,  # Anonymized only
        Permission.READ_MEDICAL_RECORDS,  # Anonymized only
        Permission.VIEW_DIAGNOSTICS,
        Permission.VIEW_PRESCRIPTIONS,
        Permission.VIEW_AUDIT_LOGS,
    }
}


class RBACManager:
    """Role-Based Access Control Manager"""
    
    @staticmethod
    def has_permission(user_role: MedicalRole, permission: Permission) -> bool:
        """Check if role has specific permission"""
        role_perms = ROLE_PERMISSIONS.get(user_role, set())
        return permission in role_perms
    
    @staticmethod
    def check_resource_access(
        user_role: MedicalRole, 
        user_id: str,
        resource_owner_id: str,
        permission: Permission,
        is_emergency: bool = False
    ) -> bool:
        """Check access to specific resource with context"""
        
        # Emergency access for doctors
        if is_emergency and user_role == MedicalRole.DOCTOR:
            if Permission.EMERGENCY_ACCESS in ROLE_PERMISSIONS[user_role]:
                return True
        
        # Check basic permission
        if not RBACManager.has_permission(user_role, permission):
            return False
        
        # Own resource access for patients
        if user_role == MedicalRole.PATIENT:
            if permission == Permission.READ_OWN_PATIENT_DATA:
                return user_id == resource_owner_id
            return False
        
        # Medical professionals can access any patient data they have permission for
        if user_role in [MedicalRole.NURSE, MedicalRole.DOCTOR]:
            return True
        
        # Admin has full access
        if user_role == MedicalRole.ADMIN:
            return True
        
        # Viewer has read-only access (should be anonymized)
        if user_role == MedicalRole.VIEWER:
            read_permissions = {
                Permission.READ_ANY_PATIENT_DATA,
                Permission.READ_MEDICAL_RECORDS,
                Permission.VIEW_DIAGNOSTICS,
                Permission.VIEW_PRESCRIPTIONS,
                Permission.VIEW_AUDIT_LOGS
            }
            return permission in read_permissions
        
        return False
    
    @staticmethod
    def get_user_permissions(user_role: MedicalRole) -> Set[Permission]:
        """Get all permissions for a role"""
        return ROLE_PERMISSIONS.get(user_role, set())
    
    @staticmethod
    def can_delegate_permission(
        delegator_role: MedicalRole,
        delegatee_role: MedicalRole,
        permission: Permission
    ) -> bool:
        """Check if one role can delegate permission to another"""
        # Only admins can delegate permissions
        if delegator_role != MedicalRole.ADMIN:
            return False
        
        # Can only delegate permissions the delegator has
        delegator_perms = ROLE_PERMISSIONS[delegator_role]
        if permission not in delegator_perms:
            return False
        
        # Cannot delegate admin-only permissions to non-admins
        admin_only_perms = {
            Permission.MANAGE_USERS,
            Permission.MANAGE_SYSTEM_CONFIG,
            Permission.BREAK_GLASS_ACCESS
        }
        
        if permission in admin_only_perms and delegatee_role != MedicalRole.ADMIN:
            return False
        
        return True


def require_permission(permission: Permission, allow_emergency: bool = False):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user context from kwargs
            user_role = kwargs.get('current_user_role')
            user_id = kwargs.get('current_user_id')
            resource_owner_id = kwargs.get('resource_owner_id', user_id)
            is_emergency = kwargs.get('is_emergency', False) and allow_emergency
            
            if not user_role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User role not provided"
                )
            
            # Convert string role to enum
            if isinstance(user_role, str):
                try:
                    user_role = MedicalRole(user_role)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Invalid role: {user_role}"
                    )
            
            # Check access
            has_access = RBACManager.check_resource_access(
                user_role=user_role,
                user_id=user_id,
                resource_owner_id=resource_owner_id,
                permission=permission,
                is_emergency=is_emergency
            )
            
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(*allowed_roles: MedicalRole):
    """Decorator to require specific roles"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_role = kwargs.get('current_user_role')
            
            if not user_role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User role not provided"
                )
            
            # Convert string role to enum
            if isinstance(user_role, str):
                try:
                    user_role = MedicalRole(user_role)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Invalid role: {user_role}"
                    )
            
            if user_role not in allowed_roles:
                allowed_names = [role.value for role in allowed_roles]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: one of {allowed_names}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class EmergencyAccess:
    """Emergency access management for critical situations"""
    
    @staticmethod
    def grant_emergency_access(
        user_id: str,
        user_role: MedicalRole,
        justification: str,
        duration_minutes: int = 60
    ) -> Optional[str]:
        """Grant temporary emergency access"""
        from datetime import datetime, timedelta
        from app.security import AuditLogger
        
        if user_role != MedicalRole.DOCTOR:
            return None
        
        # Log emergency access grant
        AuditLogger.log_access(
            user_id=user_id,
            action="EMERGENCY_ACCESS_GRANTED",
            resource_type="system",
            resource_id="emergency_access",
            ip_address="system"
        )
        
        # Create emergency token (in real implementation, store in cache/DB)
        emergency_token = f"emergency_{user_id}_{datetime.utcnow().timestamp()}"
        
        return emergency_token
    
    @staticmethod
    def validate_emergency_access(
        user_id: str,
        emergency_token: str
    ) -> bool:
        """Validate emergency access token"""
        # In real implementation, check token validity from cache/DB
        return emergency_token.startswith(f"emergency_{user_id}_")


# Global RBAC manager instance
rbac_manager = RBACManager()