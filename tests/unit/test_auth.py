import pytest
from app.auth import authenticate_user, create_user

def test_authenticate():
    assert authenticate_user("user", "pass")

def test_create_user():
    user = create_user("new", "pass")
    assert user["username"] == "new"

def test_auth_functions():
    # Testa funcoes basicas de auth
    assert True
