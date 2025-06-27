# tests/conftest.py - CORREÇÃO COMPLETA
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.database import get_db

# Configuração do loop de eventos para testes
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Helper para criar AsyncMock que funciona corretamente
def create_async_mock():
    """Cria um mock que pode ser usado com await"""
    mock = AsyncMock()
    return mock

# Mock da sessão do banco de dados
@pytest.fixture
async def mock_db():
    """Mock database session"""
    session = MagicMock(spec=AsyncSession)
    
    # Configurar métodos síncronos
    session.add = MagicMock()
    session.flush = MagicMock()
    
    # Configurar métodos assíncronos
    session.commit = create_async_mock()
    session.refresh = create_async_mock()
    session.close = create_async_mock()
    session.rollback = create_async_mock()
    
    # Configurar execute para retornar um mock result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    session.execute = create_async_mock(return_value=mock_result)
    
    yield session

# Override do get_db para testes
@pytest.fixture
def override_get_db(mock_db):
    async def _get_db_override():
        yield mock_db
    
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

# Helper para criar mocks de repositórios assíncronos
def create_async_repository_mock():
    """Create a mock repository with async methods"""
    mock = MagicMock()
    
    # Converter todos os métodos importantes para AsyncMock
    async_methods = [
        'create', 'get', 'update', 'delete', 'list_all',
        'get_user_by_email', 'get_user_notifications',
        'mark_as_read', 'get_analysis_by_id', 'search',
        'get_by_patient_id', 'get_patient_analyses',
        'delete_analysis', 'update_patient', 'search_patients',
        'get_validation_by_id', 'get_pending_validations',
        'mark_all_as_read'
    ]
    
    for method in async_methods:
        setattr(mock, method, create_async_mock())
    
    return mock

# Fixtures para modelos
@pytest.fixture
def mock_user():
    """Mock user object"""
    from app.models.user import User
    from app.core.constants import UserRole
    return MagicMock(
        spec=User,
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        role=UserRole.PHYSICIAN,
        is_active=True,
        is_verified=True,
        is_superuser=False
    )

@pytest.fixture
def mock_patient():
    """Mock patient object"""
    from app.models.patient import Patient
    from datetime import date
    return MagicMock(
        spec=Patient,
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
    from app.models.ecg_analysis import ECGAnalysis
    from app.core.constants import AnalysisStatus
    from datetime import datetime
    return MagicMock(
        spec=ECGAnalysis,
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