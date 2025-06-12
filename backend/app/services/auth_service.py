"""
Enhanced Authentication Service with audit logging and security features
"""

import logging
from datetime import datetime, timedelta

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.services.base import BaseService

logger = logging.getLogger(__name__)

class AuthService(BaseService):
    """
    Service for managing authentication and authorization
    """

    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> User | None:
        """
        Authenticate user with enhanced security checks
        """
        try:
            user = self.db.query(User).filter(
                User.username == username
            ).first()

            if not user:
                await self._record_failed_login_attempt(username, "user_not_found")
                return None

            if user.locked_until and user.locked_until > datetime.utcnow():
                await self._record_failed_login_attempt(username, "account_locked")
                return None

            if not verify_password(password, user.hashed_password):
                await self._record_failed_login_attempt(username, "invalid_password")
                return None

            if not user.is_active:
                await self._record_failed_login_attempt(username, "account_inactive")
                return None

            await self.record_login(user.id)
            return user

        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return None

    async def record_login(self, user_id: int):
        """
        Record successful login
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
                user.failed_login_attempts = 0
                user.locked_until = None
                self.db.commit()

                await self.log_audit(
                    user_id=user_id,
                    action="LOGIN",
                    resource_type="user",
                    resource_id=user_id,
                    description="Successful login"
                )

        except Exception as e:
            logger.error(f"Error recording login: {e}")

    async def _record_failed_login_attempt(self, username: str, reason: str):
        """
        Record failed login attempt
        """
        try:
            user = self.db.query(User).filter(
                User.username == username
            ).first()

            if user:
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                    logger.warning(f"Account locked for user {username} due to failed login attempts")

                self.db.commit()

                await self.log_audit(
                    user_id=user.id,
                    action="FAILED_LOGIN",
                    resource_type="user",
                    resource_id=user.id,
                    description=f"Failed login attempt: {reason}",
                    metadata={"reason": reason, "attempts": user.failed_login_attempts}
                )

        except Exception as e:
            logger.error(f"Error recording failed login: {e}")

    async def record_logout(self, user_id: int):
        """
        Record user logout
        """
        try:
            await self.log_audit(
                user_id=user_id,
                action="LOGOUT",
                resource_type="user",
                resource_id=user_id,
                description="User logout"
            )

        except Exception as e:
            logger.error(f"Error recording logout: {e}")

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password with validation
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            if not verify_password(current_password, user.hashed_password):
                return False

            user.hashed_password = get_password_hash(new_password)
            user.password_changed_at = datetime.utcnow()
            self.db.commit()

            await self.log_audit(
                user_id=user_id,
                action="PASSWORD_CHANGE",
                resource_type="user",
                resource_id=user_id,
                description="Password changed successfully"
            )

            return True

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

    async def reset_password(
        self,
        user_id: int,
        new_password: str,
        reset_by: int
    ) -> bool:
        """
        Reset user password (admin function)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.hashed_password = get_password_hash(new_password)
            user.password_changed_at = datetime.utcnow()
            user.must_change_password = True
            self.db.commit()

            await self.log_audit(
                user_id=reset_by,
                action="PASSWORD_RESET",
                resource_type="user",
                resource_id=user_id,
                description=f"Password reset for user {user.username}",
                metadata={"target_user": user.username}
            )

            return True

        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False

    async def unlock_user_account(self, user_id: int, unlocked_by: int) -> bool:
        """
        Unlock a locked user account
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.locked_until = None
            user.failed_login_attempts = 0
            self.db.commit()

            await self.log_audit(
                user_id=unlocked_by,
                action="ACCOUNT_UNLOCK",
                resource_type="user",
                resource_id=user_id,
                description=f"Account unlocked for user {user.username}",
                metadata={"target_user": user.username}
            )

            return True

        except Exception as e:
            logger.error(f"Error unlocking account: {e}")
            return False
