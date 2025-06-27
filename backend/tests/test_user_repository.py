import pytest
from unittest.mock import MagicMock, AsyncMock
from app.repositories.user_repository import UserRepository
from app.models.user import User as UserModel  # Modelo SQLAlchemy
from app.schemas.user import UserCreate
from datetime import datetime
from app.core.constants import UserRole
from sqlalchemy.future import select

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def user_repository(mock_db_session):
    return UserRepository(db=mock_db_session)

@pytest.mark.asyncio
async def test_create_user_repository(user_repository, mock_db_session):
    user_data = UserCreate(
        email="test@example.com",
        password="Password123!", # Corrigido: Adicionado caractere especial
        username="testuser",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        license_number="LIC123",
        specialty="Cardiology",
        institution="Test Hospital",
        experience_years=5
    )
    
    # Criar modelo SQLAlchemy ao invés de schema Pydantic
    user_model = UserModel(
        email=user_data.email,
        hashed_password="hashed_password",
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
    
    # mock_db_session.add.return_value = None # Removido, pois add não retorna nada
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)

    created_user = await user_repository.create_user(user_model)

    mock_db_session.add.assert_called_once_with(user_model)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(user_model)
    assert created_user.email == user_data.email

@pytest.mark.asyncio
async def test_get_user_by_email_repository(user_repository, mock_db_session):
    email = "test@example.com"
    
    mock_user = UserModel(
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
    
    # Mockando o resultado da execução da query
    # mock_execute_result = AsyncMock()
    # mock_execute_result.scalar_one_or_none.return_value = mock_user
    # mock_db_session.execute.return_value = mock_execute_result

    # O método get_user_by_email já retorna o resultado de scalar_one_or_none
    # então o mock_db_session.execute.return_value deve ser um mock que tenha
    # o método scalar_one_or_none que retorna o mock_user.
    mock_db_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user))

    user = await user_repository.get_user_by_email(email)

    mock_db_session.execute.assert_called_once()
    assert user.email == email


