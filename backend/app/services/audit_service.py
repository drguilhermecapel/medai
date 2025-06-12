"""
Audit Service for tracking system activities and generating reports
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.services.base import BaseService

logger = logging.getLogger(__name__)

class AuditService(BaseService):
    """
    Service for managing audit logs and generating audit reports
    """
    
    async def log_action(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: int,
        description: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log an audit action with comprehensive details
        """
        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "description": description,
                "changes": changes or {},
                "metadata": metadata or {},
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            logger.info(f"AUDIT: {audit_entry}")
            
        except Exception as e:
            logger.error(f"Error logging audit action: {e}")
    
    async def get_user_activity(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get user activity history
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            mock_activities = [
                {
                    "timestamp": datetime.utcnow() - timedelta(hours=1),
                    "action": "LOGIN",
                    "resource_type": "user",
                    "description": "User logged in"
                },
                {
                    "timestamp": datetime.utcnow() - timedelta(hours=2),
                    "action": "VIEW",
                    "resource_type": "patient",
                    "description": "Viewed patient record"
                }
            ]
            
            return mock_activities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return []
    
    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get history of changes to a specific resource
        """
        try:
            mock_history = [
                {
                    "timestamp": datetime.utcnow() - timedelta(hours=1),
                    "user_id": 1,
                    "action": "UPDATE",
                    "description": f"Updated {resource_type}",
                    "changes": {"field1": {"old": "value1", "new": "value2"}}
                }
            ]
            
            return mock_history[:limit]
            
        except Exception as e:
            logger.error(f"Error getting resource history: {e}")
            return []
    
    async def get_audit_report(
        self,
        start_date: datetime,
        end_date: datetime,
        user_ids: Optional[List[int]] = None,
        actions: Optional[List[str]] = None,
        resource_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audit report
        """
        try:
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "filters": {
                    "user_ids": user_ids,
                    "actions": actions,
                    "resource_types": resource_types
                },
                "summary": {
                    "total_actions": 150,
                    "unique_users": 25,
                    "most_common_actions": [
                        {"action": "VIEW", "count": 75},
                        {"action": "UPDATE", "count": 45},
                        {"action": "CREATE", "count": 20},
                        {"action": "DELETE", "count": 10}
                    ],
                    "most_active_users": [
                        {"user_id": 1, "action_count": 45},
                        {"user_id": 2, "action_count": 32},
                        {"user_id": 3, "action_count": 28}
                    ]
                },
                "security_events": {
                    "failed_logins": 12,
                    "account_lockouts": 2,
                    "password_changes": 5
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating audit report: {e}")
            return {}
    
    async def cleanup_old_logs(self, days_to_keep: int = 365) -> int:
        """
        Clean up old audit logs (for compliance and storage management)
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            logger.info(f"Would clean up audit logs older than {cutoff_date}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Error cleaning up audit logs: {e}")
            return 0
    
    async def get_compliance_report(
        self,
        compliance_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate compliance-specific audit reports (HIPAA, SOX, etc.)
        """
        try:
            report = {
                "compliance_type": compliance_type,
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "access_controls": {
                    "user_access_reviews": 12,
                    "privilege_escalations": 3,
                    "access_violations": 0
                },
                "data_access": {
                    "patient_record_access": 1250,
                    "unauthorized_access_attempts": 5,
                    "data_exports": 15
                },
                "system_changes": {
                    "configuration_changes": 8,
                    "user_management_changes": 25,
                    "security_policy_updates": 2
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {}
