"""
Security utilities for CardioAI Pro.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AuthenticationException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Create access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
    }

    if additional_claims:
        to_encode.update(additional_claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    """Create refresh token."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """Verify and decode token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != token_type:
            raise AuthenticationException("Invalid token type")

        return payload

    except JWTError as e:
        raise AuthenticationException("Invalid token") from e


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_password_reset_token(email: str) -> str:
    """Generate password reset token."""
    delta = timedelta(hours=24)  # Token valid for 24 hours
    now = datetime.utcnow()
    expires = now + delta

    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "password_reset"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    """Verify password reset token."""
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        if decoded_token.get("type") != "password_reset":
            return None

        sub = decoded_token.get("sub")
        return str(sub) if sub is not None else None

    except JWTError:
        return None


def generate_api_key() -> str:
    """Generate API key."""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify API key."""
    return hash_api_key(api_key) == hashed_key


def generate_digital_signature(data: str, private_key: str) -> str:
    """Generate digital signature for medical validation."""
    combined = f"{data}{private_key}{datetime.utcnow().isoformat()}"
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_digital_signature(
    data: str, signature: str, public_key: str, timestamp: datetime
) -> bool:
    """Verify digital signature."""
    combined = f"{data}{public_key}{timestamp.isoformat()}"
    expected_signature = hashlib.sha256(combined.encode()).hexdigest()
    return signature == expected_signature


def generate_file_hash(file_content: bytes) -> str:
    """Generate file hash for integrity verification."""
    return hashlib.sha256(file_content).hexdigest()


def constant_time_compare(val1: str, val2: str) -> bool:
    """Constant time string comparison to prevent timing attacks."""
    return secrets.compare_digest(val1, val2)
