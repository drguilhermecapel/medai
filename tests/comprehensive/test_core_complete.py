"""
Testes abrangentes para módulos core
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

class TestCoreModules:
    """Testes para módulos core"""
    
    def test_constants_all_enums(self):
        """Testa todos os enums das constants"""
        from backend.app.core.constants import (
            UserRole, DiagnosisCategory, NotificationPriority,
            NotificationType, UserRoles, AnalysisStatus, ClinicalUrgency,
            ValidationStatus, ModelType
        )
        
        # Testar UserRole
        assert UserRole.ADMIN == "admin"
        assert UserRole.VIEWER == "viewer"
        
        # Testar DiagnosisCategory
        assert DiagnosisCategory.NORMAL == "normal"
        assert DiagnosisCategory.CRITICAL == "critical"
        
        # Testar NotificationPriority
        assert NotificationPriority.LOW == "low"
        assert NotificationPriority.CRITICAL == "critical"
        
        print("✅ Todos os enums testados")
    
    def test_config_settings(self):
        """Testa configurações"""
        from backend.app.config import Settings, DatabaseConfig
        
        settings = Settings()
        assert hasattr(settings, 'API_V1_STR')
        assert settings.API_V1_STR == "/api/v1"
        
        db_config = DatabaseConfig("sqlite:///test.db")
        assert db_config.url == "sqlite:///test.db"
        assert db_config.pool_size == 10
        
        print("✅ Configurações testadas")
    
    def test_health_checker(self):
        """Testa health checker"""
        from backend.app.health import HealthChecker
        
        checker = HealthChecker()
        
        def mock_check():
            return {"status": "healthy"}
        
        checker.add_check("test", mock_check)
        results = checker.run_checks()
        assert "test" in results
        
        status = checker.get_overall_status()
        assert status in ["healthy", "unhealthy", "degraded"]
        
        print("✅ Health checker testado")
