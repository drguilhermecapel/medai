"""
Base service with common functionality
Enhanced with audit logging and security features
"""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class BaseService:
    """
    Base class for all services with common functionality
    """

    def __init__(self, db: Session):
        self.db = db

    async def log_audit(
        self,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        description: str | None = None,
        changes: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None
    ):
        """
        Register action in audit log
        """
        try:
            logger.info(
                f"Audit: user_id={user_id}, action={action}, "
                f"resource_type={resource_type}, resource_id={resource_id}, "
                f"description={description}"
            )

        except Exception as e:
            logger.error(f"Error registering audit: {e}")

    def get_entity_changes(self, entity, update_data: dict[str, Any]) -> dict[str, Any]:
        """
        Capture changes in an entity
        """
        changes = {}

        for field, new_value in update_data.items():
            old_value = getattr(entity, field, None)
            if old_value != new_value:
                changes[field] = {
                    "old": old_value,
                    "new": new_value
                }

        return changes

    def validate_required_fields(self, data: dict[str, Any], required_fields: list) -> None:
        """
        Validate that required fields are present
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    def sanitize_input(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize input data
        """
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value

        return sanitized
