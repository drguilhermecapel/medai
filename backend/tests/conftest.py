"""
Configuração global para testes pytest
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set environment variables for testing
os.environ["TESTING"] = "true"
os.environ["ENVIRONMENT"] = "testing"  # Fixed: should be "testing" not "test"
os.environ["DATABASE_URL"] = "sqlite:///test.db"  # Use SQLite for tests to avoid DB connection issues

import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_database_engine():
    """Mock database engine to avoid connection issues during testing"""
    from unittest.mock import patch
    
    with patch('app.core.database.create_database_engine') as mock_engine:
        mock_engine.return_value = MagicMock()
        yield mock_engine

@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings to use test configuration"""
    from unittest.mock import patch
    
    with patch('app.config.Settings') as mock_settings_class:
        mock_settings = MagicMock()
        mock_settings.DATABASE_URL = "sqlite:///test.db"
        mock_settings.TESTING = True
        mock_settings.is_testing = True
        mock_settings.is_development = False
        mock_settings.is_production = False
        mock_settings_class.return_value = mock_settings
        yield mock_settings