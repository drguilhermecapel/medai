import pytest
from app.security import get_password_hash, verify_password, create_access_token

def test_password_hash():
    password = "test123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)

def test_wrong_password():
    password = "test123"
    hashed = get_password_hash(password)
    assert not verify_password("wrong", hashed)

def test_create_token():
    token = create_access_token({"sub": "test@test.com"})
    assert isinstance(token, str)
    assert len(token) > 20

def test_token_with_data():
    data = {"sub": "user@test.com", "id": 1}
    token = create_access_token(data)
    assert token is not None
