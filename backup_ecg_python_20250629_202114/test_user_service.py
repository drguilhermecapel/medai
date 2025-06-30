import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User  # Importar o modelo SQLAlchemy, não o schema
from app.core.security import get_password_hash
from datetime import datetime
from app.core.constants import UserRole
from unittest.mock import ANY

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def user_service(mock_db_session):
    return UserService(db=mock_db_session)

@pytest.mark.asyncio
async def test_create_user(user_service, mock_db_session):
    user_data = UserCreate(
        email="test@example.com",
        password="Password123!",
        username="testuser",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        license_number="LIC123",
        specialty="Cardiology",
        institution="Test Hospital",
        experience_years=5
    )
    hashed_password = get_password_hash(user_data.password)
    
    mock_user_repo = MagicMock(spec=UserRepository)
    # Criar um objeto User do modelo SQLAlchemy
    mock_user = User(
        id=1,
        email=user_data.email,
        hashed_password=hashed_password,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=True,
        is_verified=False,
        is_superuser=False,
        role=UserRole.VIEWER,
        phone=user_data.phone,
        license_number=user_data.license_number,
        specialty=user_data.specialty,
        institution=user_data.institution,
        experience_years=user_data.experience_years
    )
    
    mock_user_repo.create_user.return_value = mock_user
    user_service.repository = mock_user_repo # Corrigido: usar .repository ao invés de .user_repository

    user = await user_service.create_user(user_data)

    mock_user_repo.create_user.assert_called_once()
    assert user.email == user_data.email

@pytest.mark.asyncio
async def test_get_user_by_email(user_service, mock_db_session):
    email = "test@example.com"
    
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user = User(
        id=1,
        email=email,
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
    
    mock_user_repo.get_user_by_email.return_value = mock_user
    user_service.repository = mock_user_repo

    user = await user_service.get_user_by_email(email)

    mock_user_repo.get_user_by_email.assert_called_once_with(email)
    assert user.email == email

