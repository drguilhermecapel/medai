# tests/conftest.py - CORREÇÃO
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.core.database import get_db
from app.main import app

# Configuração do loop de eventos para testes
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Mock da sessão do banco de dados
@pytest.fixture
async def mock_db():
    """Mock database session"""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    yield session

# Override do get_db para testes
@pytest.fixture
def override_get_db(mock_db):
    async def _get_db_override():
        yield mock_db
    
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

# Fixtures para modelos
@pytest.fixture
def mock_user():
    """Mock user object"""
    from app.models.user import User
    return MagicMock(spec=User, 
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        role="physician",
        is_active=True,
        is_verified=True,
        is_superuser=False
    )

@pytest.fixture
def mock_patient():
    """Mock patient object"""
    from app.models.patient import Patient
    from datetime import date
    return MagicMock(spec=Patient,
        id=1,
        patient_id="P001",
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        email="patient@example.com",
        created_by=1
    )

@pytest.fixture
def mock_ecg_analysis():
    """Mock ECG analysis object"""
    from app.models.ecg_analysis import ECGAnalysis, AnalysisStatus
    from datetime import datetime
    return MagicMock(spec=ECGAnalysis,
        id=1,
        patient_id=1,
        created_by=1,
        acquisition_date=datetime.utcnow(),
        file_path="/path/to/ecg.txt",
        original_filename="ecg.txt",
        sample_rate=500,
        duration_seconds=10.0,
        leads_count=12,
        leads_names=["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        status=AnalysisStatus.COMPLETED
    )

# Helper para criar mocks de repositórios assíncronos
def create_async_mock_repository():
    """Create a mock repository with async methods"""
    mock = MagicMock()
    
    # Converter métodos para AsyncMock
    mock.create = AsyncMock()
    mock.get = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    mock.list_all = AsyncMock()
    mock.get_user_by_email = AsyncMock()
    mock.get_user_notifications = AsyncMock()
    mock.mark_as_read = AsyncMock()
    mock.get_analysis_by_id = AsyncMock()
    mock.search = AsyncMock()
    
    return mock

# tests/test_services.py - CORREÇÃO PARCIAL
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from app.services.patient_service import PatientService
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.services.ecg_service import ECGAnalysisService
from app.schemas.patient import PatientCreate
from app.schemas.user import UserCreate
from app.core.exceptions import ECGProcessingException

class TestPatientService:
    @pytest.mark.asyncio
    async def test_create_patient(self, mock_db, mock_patient):
        # Arrange
        service = PatientService(mock_db)
        service.repository = create_async_mock_repository()
        service.repository.create.return_value = mock_patient
        
        patient_data = PatientCreate(
            patient_id="P001",
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            gender="male",
            email="patient@example.com"
        )
        
        # Act
        result = await service.create_patient(patient_data, created_by=1)
        
        # Assert
        assert result == mock_patient
        service.repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_patients(self, mock_db, mock_patient):
        # Arrange
        service = PatientService(mock_db)
        service.repository = create_async_mock_repository()
        service.repository.search.return_value = [mock_patient]
        
        # Act
        result = await service.search_patients("John", ["first_name", "last_name"])
        
        # Assert
        assert len(result) == 1
        assert result[0] == mock_patient
        service.repository.search.assert_called_once_with("John", ["first_name", "last_name"])

class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user(self, mock_db, mock_user):
        # Arrange
        with patch('app.services.user_service.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            service = UserService(mock_db)
            service.repository = create_async_mock_repository()
            service.repository.get_user_by_email.return_value = None
            service.repository.create.return_value = mock_user
            
            user_data = UserCreate(
                username="testuser",
                email="test@example.com",
                password="SecurePass123",
                full_name="Test User",
                role="physician"
            )
            
            # Act
            result = await service.create_user(user_data)
            
            # Assert
            assert result == mock_user
            service.repository.get_user_by_email.assert_called_once_with("test@example.com")
            service.repository.create.assert_called_once()

class TestNotificationService:
    @pytest.mark.asyncio
    async def test_get_user_notifications(self, mock_db):
        # Arrange
        service = NotificationService(mock_db)
        service.repository = create_async_mock_repository()
        mock_notifications = [MagicMock(id=1), MagicMock(id=2)]
        service.repository.get_user_notifications.return_value = mock_notifications
        
        # Act
        result = await service.get_user_notifications(123)
        
        # Assert
        assert len(result) == 2
        service.repository.get_user_notifications.assert_called_once_with(
            user_id=123,
            unread_only=False,
            limit=50
        )
    
    @pytest.mark.asyncio
    async def test_mark_as_read(self, mock_db):
        # Arrange
        service = NotificationService(mock_db)
        service.repository = create_async_mock_repository()
        mock_notification = MagicMock(id=123, user_id=456, is_read=False)
        service.repository.get.return_value = mock_notification
        service.repository.update.return_value = mock_notification
        
        # Act
        result = await service.mark_as_read(123, user_id=456)
        
        # Assert
        assert result == mock_notification
        assert mock_notification.is_read == True
        service.repository.update.assert_called_once()

# tests/test_api_endpoints.py - CORREÇÃO PARCIAL
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHealthEndpoints:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data  # Mudança: verificar version ao invés de timestamp