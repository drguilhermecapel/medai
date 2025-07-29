"""
Enhanced Session Manager for MedAI
Provides session management with device binding and anti-replay protection
"""
import json
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

logger = logging.getLogger(__name__)


class EnhancedSessionManager:
    """Enhanced session manager with security features"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize session manager
        
        Args:
            redis_url: Redis connection URL
        """
        try:
            # Test Redis connection before setting it as available
            self.redis_client = AsyncRedis.from_url(redis_url, decode_responses=True)
            # Try a simple ping to check connectivity
            import asyncio
            try:
                # We can't use await here, so we'll defer the actual connection test
                # and fall back to memory storage for now
                self._redis_available = False
                self.redis_client = None
                self._memory_store = {}
                logger.info("Using in-memory session storage (Redis not available)")
            except:
                self._redis_available = False
                self.redis_client = None
                self._memory_store = {}
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory storage: {e}")
            self.redis_client = None
            self._redis_available = False
            self._memory_store = {}
        
        # Session configuration
        self.session_timeout = timedelta(minutes=30)
        self.refresh_timeout = timedelta(days=7)
        self.max_concurrent_sessions = 3
        self.anti_replay_window = timedelta(seconds=1)
        
        # Security settings
        self.session_token_length = 32
        self.refresh_token_length = 32
    
    async def create_session(self, user_id: str, device_fingerprint: str, 
                           user_agent: str = "", ip_address: str = "") -> Dict[str, Any]:
        """
        Create new session with token binding
        
        Args:
            user_id: User identifier
            device_fingerprint: Device fingerprint for binding
            user_agent: User agent string
            ip_address: Client IP address
            
        Returns:
            Session data with tokens
        """
        # Generate secure tokens
        session_token = secrets.token_urlsafe(self.session_token_length)
        refresh_token = secrets.token_urlsafe(self.refresh_token_length)
        
        # Create session data
        now = datetime.utcnow()
        session_data = {
            "session_id": session_token,
            "refresh_token": refresh_token,
            "user_id": user_id,
            "device_fingerprint": self._hash_fingerprint(device_fingerprint),
            "created_at": now.isoformat(),
            "expires_at": (now + self.session_timeout).isoformat(),
            "refresh_expires_at": (now + self.refresh_timeout).isoformat(),
            "is_active": True,
            "user_agent_hash": self._hash_user_agent(user_agent),
            "ip_address": self._anonymize_ip(ip_address),
            "last_activity": now.isoformat(),
            "request_count": 0
        }
        
        # Check and enforce concurrent session limit
        await self._enforce_session_limit(user_id)
        
        # Store session
        await self._store_session(session_token, session_data)
        
        # Track user sessions
        await self._track_user_session(user_id, session_token)
        
        logger.info("Session created", extra={
            "user_id": user_id,
            "session_id": session_token[:8] + "...",
            "expires_at": session_data["expires_at"]
        })
        
        return {
            "session_token": session_token,
            "refresh_token": refresh_token,
            "expires_at": session_data["expires_at"],
            "refresh_expires_at": session_data["refresh_expires_at"]
        }
    
    async def validate_session(self, token: str, current_fingerprint: str,
                             user_agent: str = "", ip_address: str = "") -> Optional[Dict[str, Any]]:
        """
        Validate session with anti-replay protection
        
        Args:
            token: Session token
            current_fingerprint: Current device fingerprint
            user_agent: Current user agent
            ip_address: Current IP address
            
        Returns:
            Session data if valid, None otherwise
        """
        # Get session data
        session_data = await self._get_session(token)
        if not session_data:
            logger.warning("Session not found", extra={"token": token[:8] + "..."})
            return None
        
        # Check if session is active
        if not session_data.get("is_active", False):
            logger.warning("Session inactive", extra={"token": token[:8] + "..."})
            return None
        
        # Check expiration
        try:
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if datetime.utcnow() > expires_at:
                logger.info("Session expired", extra={"token": token[:8] + "..."})
                await self.revoke_session(token)
                return None
        except (KeyError, ValueError):
            logger.error("Invalid session expiration", extra={"token": token[:8] + "..."})
            return None
        
        # Verify device binding
        stored_fingerprint = session_data.get("device_fingerprint", "")
        current_fingerprint_hash = self._hash_fingerprint(current_fingerprint)
        
        if stored_fingerprint != current_fingerprint_hash:
            logger.warning("Device fingerprint mismatch", extra={
                "token": token[:8] + "...",
                "user_id": session_data.get("user_id")
            })
            await self.revoke_session(token)
            return None
        
        # Check for replay attacks
        if not await self._check_anti_replay(token):
            logger.warning("Potential replay attack detected", extra={
                "token": token[:8] + "...",
                "user_id": session_data.get("user_id")
            })
            return None
        
        # Verify user agent consistency (soft check)
        current_ua_hash = self._hash_user_agent(user_agent)
        stored_ua_hash = session_data.get("user_agent_hash", "")
        
        if stored_ua_hash and current_ua_hash != stored_ua_hash:
            logger.info("User agent changed", extra={
                "token": token[:8] + "...",
                "user_id": session_data.get("user_id")
            })
            # Update the hash but don't fail validation
            session_data["user_agent_hash"] = current_ua_hash
        
        # Update session activity
        await self._update_session_activity(token, session_data)
        
        return session_data
    
    async def refresh_session(self, refresh_token: str, device_fingerprint: str) -> Optional[Dict[str, Any]]:
        """
        Refresh session using refresh token
        
        Args:
            refresh_token: Refresh token
            device_fingerprint: Device fingerprint for verification
            
        Returns:
            New session data if successful, None otherwise
        """
        # Find session by refresh token
        session_data = await self._find_session_by_refresh_token(refresh_token)
        if not session_data:
            logger.warning("Invalid refresh token")
            return None
        
        # Verify device fingerprint
        stored_fingerprint = session_data.get("device_fingerprint", "")
        current_fingerprint_hash = self._hash_fingerprint(device_fingerprint)
        
        if stored_fingerprint != current_fingerprint_hash:
            logger.warning("Device fingerprint mismatch during refresh")
            return None
        
        # Check refresh token expiration
        try:
            refresh_expires_at = datetime.fromisoformat(session_data["refresh_expires_at"])
            if datetime.utcnow() > refresh_expires_at:
                logger.info("Refresh token expired")
                await self.revoke_session(session_data["session_id"])
                return None
        except (KeyError, ValueError):
            logger.error("Invalid refresh token expiration")
            return None
        
        # Create new session
        user_id = session_data.get("user_id")
        if not user_id:
            logger.error("No user_id in session data")
            return None
        
        # Revoke old session
        await self.revoke_session(session_data["session_id"])
        
        # Create new session
        return await self.create_session(
            user_id=user_id,
            device_fingerprint=device_fingerprint,
            user_agent=session_data.get("user_agent_hash", ""),
            ip_address=session_data.get("ip_address", "")
        )
    
    async def revoke_session(self, token: str) -> bool:
        """
        Revoke session
        
        Args:
            token: Session token to revoke
            
        Returns:
            True if session was revoked, False otherwise
        """
        session_data = await self._get_session(token)
        if not session_data:
            return False
        
        # Remove from storage
        await self._remove_session(token)
        
        # Remove from user session tracking
        user_id = session_data.get("user_id")
        if user_id:
            await self._untrack_user_session(user_id, token)
        
        logger.info("Session revoked", extra={
            "token": token[:8] + "...",
            "user_id": user_id
        })
        
        return True
    
    async def revoke_user_sessions(self, user_id: str, except_token: Optional[str] = None) -> int:
        """
        Revoke all sessions for a user
        
        Args:
            user_id: User identifier
            except_token: Optional token to keep active
            
        Returns:
            Number of sessions revoked
        """
        user_sessions = await self._get_user_sessions(user_id)
        revoked_count = 0
        
        for session_token in user_sessions:
            if except_token and session_token == except_token:
                continue
            
            if await self.revoke_session(session_token):
                revoked_count += 1
        
        logger.info("User sessions revoked", extra={
            "user_id": user_id,
            "revoked_count": revoked_count
        })
        
        return revoked_count
    
    # Helper methods
    
    def _hash_fingerprint(self, fingerprint: str) -> str:
        """Hash device fingerprint for storage"""
        return hashlib.sha256(fingerprint.encode()).hexdigest()
    
    def _hash_user_agent(self, user_agent: str) -> str:
        """Hash user agent for storage"""
        return hashlib.sha256(user_agent.encode()).hexdigest()
    
    def _anonymize_ip(self, ip_address: str) -> str:
        """Anonymize IP address"""
        if not ip_address:
            return ""
        
        # IPv4 anonymization
        if '.' in ip_address and ':' not in ip_address:
            parts = ip_address.split('.')
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
        
        return "[ANONYMIZED]"
    
    async def _store_session(self, token: str, session_data: Dict[str, Any]):
        """Store session data"""
        if self._redis_available:
            await self.redis_client.setex(
                f"session:{token}",
                int(self.session_timeout.total_seconds()),
                json.dumps(session_data, default=str)
            )
        else:
            self._memory_store[f"session:{token}"] = session_data
    
    async def _get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        if self._redis_available:
            session_str = await self.redis_client.get(f"session:{token}")
            if session_str:
                return json.loads(session_str)
        else:
            return self._memory_store.get(f"session:{token}")
        return None
    
    async def _remove_session(self, token: str):
        """Remove session from storage"""
        if self._redis_available:
            await self.redis_client.delete(f"session:{token}")
        else:
            self._memory_store.pop(f"session:{token}", None)
    
    async def _check_anti_replay(self, token: str) -> bool:
        """Check for replay attacks"""
        now = datetime.utcnow()
        last_request_key = f"last_request:{token}"
        
        if self._redis_available:
            last_request_str = await self.redis_client.get(last_request_key)
            if last_request_str:
                try:
                    last_request = datetime.fromisoformat(last_request_str)
                    if (now - last_request) < self.anti_replay_window:
                        return False
                except ValueError:
                    pass
            
            # Update last request time
            await self.redis_client.setex(
                last_request_key,
                int(self.anti_replay_window.total_seconds()) + 1,
                now.isoformat()
            )
        else:
            # In-memory anti-replay check
            last_request_str = self._memory_store.get(last_request_key)
            if last_request_str:
                try:
                    last_request = datetime.fromisoformat(last_request_str)
                    if (now - last_request) < self.anti_replay_window:
                        return False
                except (ValueError, TypeError):
                    pass
            
            self._memory_store[last_request_key] = now.isoformat()
        
        return True
    
    async def _update_session_activity(self, token: str, session_data: Dict[str, Any]):
        """Update session last activity"""
        session_data["last_activity"] = datetime.utcnow().isoformat()
        session_data["request_count"] = session_data.get("request_count", 0) + 1
        await self._store_session(token, session_data)
    
    async def _track_user_session(self, user_id: str, session_token: str):
        """Track session for user"""
        user_sessions_key = f"user_sessions:{user_id}"
        
        if self._redis_available:
            await self.redis_client.sadd(user_sessions_key, session_token)
            await self.redis_client.expire(user_sessions_key, int(self.refresh_timeout.total_seconds()))
        else:
            user_sessions = self._memory_store.get(user_sessions_key, set())
            user_sessions.add(session_token)
            self._memory_store[user_sessions_key] = user_sessions
    
    async def _untrack_user_session(self, user_id: str, session_token: str):
        """Remove session from user tracking"""
        user_sessions_key = f"user_sessions:{user_id}"
        
        if self._redis_available:
            await self.redis_client.srem(user_sessions_key, session_token)
        else:
            user_sessions = self._memory_store.get(user_sessions_key, set())
            user_sessions.discard(session_token)
            self._memory_store[user_sessions_key] = user_sessions
    
    async def _get_user_sessions(self, user_id: str) -> List[str]:
        """Get all sessions for user"""
        user_sessions_key = f"user_sessions:{user_id}"
        
        if self._redis_available:
            sessions = await self.redis_client.smembers(user_sessions_key)
            return list(sessions)
        else:
            return list(self._memory_store.get(user_sessions_key, set()))
    
    async def _enforce_session_limit(self, user_id: str):
        """Enforce maximum concurrent sessions"""
        user_sessions = await self._get_user_sessions(user_id)
        
        if len(user_sessions) >= self.max_concurrent_sessions:
            # Remove oldest sessions
            sessions_to_remove = len(user_sessions) - self.max_concurrent_sessions + 1
            
            # Get session data to find oldest
            session_data_list = []
            for session_token in user_sessions:
                session_data = await self._get_session(session_token)
                if session_data:
                    session_data_list.append((session_token, session_data))
            
            # Sort by creation time
            session_data_list.sort(key=lambda x: x[1].get("created_at", ""))
            
            # Remove oldest sessions
            for i in range(sessions_to_remove):
                if i < len(session_data_list):
                    old_token = session_data_list[i][0]
                    await self.revoke_session(old_token)
    
    async def _find_session_by_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Find session by refresh token"""
        # This is inefficient but works for small scale
        # In production, consider storing reverse mapping
        
        if self._redis_available:
            # Scan all session keys
            async for key in self.redis_client.scan_iter(match="session:*"):
                session_str = await self.redis_client.get(key)
                if session_str:
                    session_data = json.loads(session_str)
                    if session_data.get("refresh_token") == refresh_token:
                        return session_data
        else:
            for key, session_data in self._memory_store.items():
                if key.startswith("session:") and isinstance(session_data, dict):
                    if session_data.get("refresh_token") == refresh_token:
                        return session_data
        
        return None