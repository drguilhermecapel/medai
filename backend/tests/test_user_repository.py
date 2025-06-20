import pytest
from unittest.mock import MagicMock, AsyncMock
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, User
from datetime import datetime
from app.core.constants import UserRoles
from sqlalchemy.future import select

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def user_repository(mock_db_session):
    return UserRepository(db=mock_db_session)

@pytest.mark.asyncio
async def test_create_user_repository(user_repository, mock_db_session):
    user_data = UserCreate(email="test@example.com", password="password123", username="testuser", first_name="Test", last_name="User", phone="1234567890", license_number="LIC123", specialty="Cardiology", institution="Test Hospital", experience_years=5)
    fixed_datetime = datetime(2023, 1, 1, 10, 0, 0)
    user_model = User(
        id=1, 
        email=user_data.email, 
        hashed_password="hashed_password", 
        username=user_data.username, 
        first_name=user_data.first_name, 
        last_name=user_data.last_name, 
        is_active=True, 
        is_verified=True, 
        is_superuser=False, 
        last_login=fixed_datetime, 
        created_at=fixed_datetime, 
        updated_at=fixed_datetime, 
        role=UserRoles.VIEWER, 
        phone=user_data.phone, 
        license_number=user_data.license_number, 
        specialty=user_data.specialty, 
        institution=user_data.institution, 
        experience_years=user_data.experience_years
    )
    
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    created_user = await user_repository.create_user(user_model)

    mock_db_session.add.assert_called_once_with(user_model)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(user_model)
    assert created_user.email == user_data.email

@pytest.mark.asyncio
async def test_get_user_by_email_repository(user_repository, mock_db_session):
    email = "test@example.com"
    fixed_datetime = datetime(2023, 1, 1, 10, 0, 0)
    expected_user = User(id=1, email=email, hashed_password="hashed_password", username="testuser", first_name="Test", last_name="User", is_active=True, is_verified=True, is_superuser=False, last_login=fixed_datetime, created_at=fixed_datetime, updated_at=fixed_datetime, role=UserRoles.VIEWER, phone="1234567890", license_number="LIC123", specialty="Cardiology", institution="Test Hospital", experience_years=5)
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db_session.execute.return_value = mock_result

    user = await user_repository.get_user_by_email(email)

    mock_db_session.execute.assert_called_once()
    assert user.email == email



