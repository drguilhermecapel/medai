import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from unittest.mock import MagicMock, patch
from app.services.user_service import UserService
from app.models.user import User as UserModel
from datetime import datetime
from app.core.constants import UserRole

client = TestClient(app)

@pytest.fixture
def mock_user_service():
    with patch("app.api.v1.endpoints.auth.UserService", autospec=True) as mock_service:
        yield mock_service.return_value

@pytest.mark.asyncio
async def test_login_for_access_token(mock_user_service):
    # Criar modelo de usuário SQLAlchemy
    mock_user = UserModel(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        username="testuser",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
        is_superuser=False,
        role=UserRole.VIEWER,
        phone="1234567890",
        license_number="LIC123",
        specialty="Cardiology",
        institution="Test Hospital",
        experience_years=5
    )
    
    mock_user_service.authenticate_user.return_value = mock_user
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

