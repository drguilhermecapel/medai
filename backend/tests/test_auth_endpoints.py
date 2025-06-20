import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from unittest.mock import MagicMock, patch
from app.services.user_service import UserService
from app.schemas.user import User, UserCreate
from datetime import datetime
from app.core.constants import UserRoles

client = TestClient(app)

@pytest.fixture
def mock_user_service():
    with patch("app.api.v1.endpoints.auth.UserService", autospec=True) as mock_service:
        yield mock_service.return_value

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0

@pytest.mark.asyncio
async def test_login_for_access_token(mock_user_service):
    # Create a User object with all required fields from UserBase and UserInDB
    mock_user_service.authenticate_user.return_value = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        username="testuser",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
        is_superuser=False,
        last_login=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        role=UserRoles.VIEWER
    )
    mock_user_service.update_last_login.return_value = None

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    mock_user_service.authenticate_user.assert_called_once_with("test@example.com", "password123")
    mock_user_service.update_last_login.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_login_for_access_token_invalid_credentials(mock_user_service):
    mock_user_service.authenticate_user.return_value = None

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "invalid@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
    mock_user_service.authenticate_user.assert_called_once_with("invalid@example.com", "wrongpassword")

@pytest.mark.asyncio
async def test_login_for_access_token_inactive_user(mock_user_service):
    # Create a User object with all required fields from UserBase and UserInDB
    mock_user_service.authenticate_user.return_value = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        username="testuser",
        first_name="Test",
        last_name="User",
        is_active=False,
        is_verified=True,
        is_superuser=False,
        last_login=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        role=UserRoles.VIEWER
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Inactive user"}
    mock_user_service.authenticate_user.assert_called_once_with("test@example.com", "password123")


