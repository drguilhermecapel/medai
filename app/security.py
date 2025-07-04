# -*- coding: utf-8 -*-
"""Security module."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException

SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decode access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invÃƒÆ’Ã‚Â¡lido")

async def get_current_user(token: str, db) -> Any:
    """Get current user from token."""
    from app.models import User
    payload = decode_access_token(token)
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="UsuÃƒÆ’Ã‚Â¡rio nÃƒÆ’Ã‚Â£o encontrado")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="UsuÃƒÆ’Ã‚Â¡rio inativo")
    return user

def check_permissions(user: Any, required_permissions: list) -> bool:
    """Check user permissions."""
    if user.role == "admin":
        return True
    # Implementar lÃƒÆ’Ã‚Â³gica de permissÃƒÆ’Ã‚Âµes
    return True

def validate_token_claims(claims: dict) -> None:
    """Validate token claims."""
    if "sub" not in claims:
        raise HTTPException(status_code=401, detail="Token invÃƒÆ’Ã‚Â¡lido")

class AuthenticationError(Exception):
    pass

class AuthorizationError(Exception):
    pass
