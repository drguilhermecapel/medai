import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, User
from app.core.security import get_password_hash
from datetime import datetime
from app.core.constants import UserRoles
from unittest.mock import ANY

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def user_service(mock_db_session):
    return UserService(db=mock_db_session)

@pytest.mark.asyncio
async def test_create_user(user_service, mock_db_session):
    user_data = UserCreate(email="test@example.com", password="password123", username="testuser", first_name="Test", last_name="User", phone="1234567890", license_number="LIC123", specialty="Cardiology", institution="Test Hospital", experience_years=5)
    hashed_password = get_password_hash(user_data.password)
    
    mock_user_repo = MagicMock(spec=UserRepository)
    # Mock the create_user method to return a User instance with all required fields
    mock_user_repo.create_user.return_value = User(
        id=1, 
        email=user_data.email, 
        hashed_password=hashed_password, 
        username=user_data.username, 
        first_name=user_data.first_name, 
        last_name=user_data.last_name, 
        is_active=True, 
        is_verified=True, 
        is_superuser=False, 
        last_login=datetime.now(), 
        created_at=datetime.now(), 
        updated_at=datetime.now(), 
        role=UserRoles.VIEWER, 
        phone=user_data.phone, 
        license_number=user_data.license_number, 
        specialty=user_data.specialty, 
        institution=user_data.institution, 
        experience_years=user_data.experience_years
    )
    
    user_service.user_repository = mock_user_repo

    user = await user_service.create_user(user_data)

    # Assert that create_user was called with an instance of User, not UserCreate
    mock_user_repo.create_user.assert_called_once_with(ANY)
    assert isinstance(mock_user_repo.create_user.call_args.args[0], User)
    assert user.email == user_data.email
    assert user.hashed_password == hashed_password

@pytest.mark.asyncio
async def test_get_user_by_email(user_service, mock_db_session):
    email = "test@example.com"
    
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_user_by_email.return_value = User(id=1, email=email, hashed_password="hashed_password", username="testuser", first_name="Test", last_name="User", is_active=True, is_verified=True, is_superuser=False, last_login=datetime.now(), created_at=datetime.now(), updated_at=datetime.now(), role=UserRoles.VIEWER, phone="1234567890", license_number="LIC123", specialty="Cardiology", institution="Test Hospital", experience_years=5)
    
    user_service.user_repository = mock_user_repo

    user = await user_service.get_user_by_email(email)

    mock_user_repo.get_user_by_email.assert_called_once_with(email)
    assert user.email == email

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(user_service, mock_db_session):
    email = "nonexistent@example.com"
    
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_user_by_email.return_value = None
    
    user_service.user_repository = mock_user_repo

    user = await user_service.get_user_by_email(email)

    mock_user_repo.get_user_by_email.assert_called_once_with(email)
    assert user is None



