# tests/unit/test_health.py
"""
Testes para o módulo de health check e monitoramento.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.health import (
    HealthChecker,
    DatabaseHealthCheck,
    MLModelHealthCheck,
    CacheHealthCheck,
    SystemResourcesCheck,
    HealthStatus,
    HealthCheckResult
)


class TestHealthChecker:
    """Testes para o verificador de saúde principal."""
    
    @pytest.fixture
    def health_checker(self):
        return HealthChecker()
    
    def test_all_systems_healthy(self, health_checker):
        """Testa quando todos os sistemas estão saudáveis."""
        with patch.object(health_checker, 'checks') as mock_checks:
            mock_checks.return_value = {
                "database": HealthCheckResult(status="healthy", message="Database OK"),
                "ml_models": HealthCheckResult(status="healthy", message="Models loaded"),
                "cache": HealthCheckResult(status="healthy", message="Cache available"),
                "resources": HealthCheckResult(status="healthy", message="Resources OK")
            }
            
            result = health_checker.check_health()
            
            assert result.overall_status == HealthStatus.HEALTHY
            assert all(check.status == "healthy" for check in result.checks.values())
    
    def test_degraded_health(self, health_checker):
        """Testa status degradado quando um componente não crítico falha."""
        checks = {
            "database": HealthCheckResult(status="healthy"),
            "ml_models": HealthCheckResult(status="healthy"),
            "cache": HealthCheckResult(status="unhealthy", message="Cache unavailable"),
            "resources": HealthCheckResult(status="healthy")
        }
        
        result = health_checker.aggregate_health(checks)
        assert result == HealthStatus.DEGRADED
    
    def test_unhealthy_status(self, health_checker):
        """Testa status não saudável quando componente crítico falha."""
        checks = {
            "database": HealthCheckResult(status="unhealthy", message="Connection failed"),
            "ml_models": HealthCheckResult(status="healthy"),
            "cache": HealthCheckResult(status="healthy"),
            "resources": HealthCheckResult(status="healthy")
        }
        
        result = health_checker.aggregate_health(checks)
        assert result == HealthStatus.UNHEALTHY
    
    def test_health_check_timeout(self, health_checker):
        """Testa timeout em verificação de saúde."""
        with patch.object(health_checker, 'database_check') as mock_check:
            mock_check.side_effect = TimeoutError("Check timed out")
            
            result = health_checker.check_with_timeout(mock_check, timeout=1)
            
            assert result.status == "unhealthy"
            assert "timeout" in result.message.lower()


class TestDatabaseHealthCheck:
    """Testes para verificação de saúde do banco de dados."""
    
    @pytest.fixture
    def db_checker(self):
        return DatabaseHealthCheck()
    
    def test_database_connection_success(self, db_checker, db_session):
        """Testa conexão bem-sucedida com banco."""
        result = db_checker.check(db_session)
        
        assert result.status == "healthy"
        assert result.response_time_ms > 0
        assert result.response_time_ms < 100  # Deve ser rápido
    
    def test_database_connection_failure(self, db_checker):
        """Testa falha na conexão com banco."""
        mock_session = Mock()
        mock_session.execute.side_effect = Exception("Connection refused")
        
        result = db_checker.check(mock_session)
        
        assert result.status == "unhealthy"
        assert "connection refused" in result.message.lower()
    
    def test_database_slow_response(self, db_checker):
        """Testa resposta lenta do banco."""
        mock_session = Mock()
        
        def slow_execute(*args):
            import time
            time.sleep(0.2)  # 200ms
            return Mock()
        
        mock_session.execute = slow_execute
        
        result = db_checker.check(mock_session)
        
        assert result.status == "degraded"
        assert result.response_time_ms > 150
        assert "slow" in result.message.lower()
    
    def test_database_migration_check(self, db_checker, db_session):
        """Testa verificação de migrações pendentes."""
        with patch('app.health.check_pending_migrations') as mock_migrations:
            mock_migrations.return_value = True  # Tem migrações pendentes
            
            result = db_checker.check_migrations(db_session)
            
            assert result.status == "degraded"
            assert "pending migrations" in result.message.lower()


class TestMLModelHealthCheck:
    """Testes para verificação de saúde dos modelos ML."""
    
    @pytest.fixture
    def ml_checker(self):
        return MLModelHealthCheck()
    
    def test_all_models_loaded(self, ml_checker):
        """Testa quando todos os modelos estão carregados."""
        with patch('app.health.get_loaded_models') as mock_models:
            mock_models.return_value = {
                "diagnostic_model": {"loaded": True, "version": "v2.1.0"},
                "risk_model": {"loaded": True, "version": "v1.5.0"},
                "nlp_model": {"loaded": True, "version": "v3.0.0"}
            }
            
            result = ml_checker.check()
            
            assert result.status == "healthy"
            assert "3 models loaded" in result.message
    
    def test_model_loading_failure(self, ml_checker):
        """Testa falha no carregamento de modelo."""
        with patch('app.health.get_loaded_models') as mock_models:
            mock_models.return_value = {
                "diagnostic_model": {"loaded": False, "error": "File not found"},
                "risk_model": {"loaded": True, "version": "v1.5.0"}
            }
            
            result = ml_checker.check()
            
            assert result.status == "unhealthy"
            assert "diagnostic_model" in result.message
    
    def test_model_performance_check(self, ml_checker):
        """Testa verificação de performance dos modelos."""
        test_data = {"glucose": 126, "age": 55, "bmi": 28.5}
        
        with patch.object(ml_checker, 'model') as mock_model:
            mock_model.predict.return_value = {"risk": 0.75}
            
            result = ml_checker.check_model_performance("diagnostic_model", test_data)
            
            assert result.status == "healthy"
            assert result.metadata["inference_time_ms"] > 0
    
    def test_model_accuracy_degradation(self, ml_checker):
        """Testa detecção de degradação na acurácia."""
        with patch('app.health.get_model_metrics') as mock_metrics:
            mock_metrics.return_value = {
                "accuracy": 0.75,  # Abaixo do threshold
                "baseline_accuracy": 0.90,
                "predictions_count": 1000
            }
            
            result = ml_checker.check_model_accuracy("diagnostic_model")
            
            assert result.status == "degraded"
            assert "accuracy degradation" in result.message.lower()


class TestSystemResourcesCheck:
    """Testes para verificação de recursos do sistema."""
    
    @pytest.fixture
    def resources_checker(self):
        return SystemResourcesCheck()
    
    def test_resources_normal(self, resources_checker):
        """Testa recursos em níveis normais."""
        with patch('psutil.cpu_percent') as mock_cpu:
            with patch('psutil.virtual_memory') as mock_memory:
                with patch('psutil.disk_usage') as mock_disk:
                    mock_cpu.return_value = 45.0
                    mock_memory.return_value = Mock(percent=60.0)
                    mock_disk.return_value = Mock(percent=70.0)
                    
                    result = resources_checker.check()
                    
                    assert result.status == "healthy"
                    assert result.metadata["cpu_percent"] == 45.0
                    assert result.metadata["memory_percent"] == 60.0
    
    def test_high_cpu_usage(self, resources_checker):
        """Testa uso alto de CPU."""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 95.0
            
            result = resources_checker.check_cpu()
            
            assert result.status == "degraded"
            assert "high cpu usage" in result.message.lower()
    
    def test_low_memory(self, resources_checker):
        """Testa memória baixa."""
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value = Mock(
                percent=92.0,
                available=500 * 1024 * 1024  # 500MB
            )
            
            result = resources_checker.check_memory()
            
            assert result.status == "unhealthy"
            assert "low memory" in result.message.lower()
    
    def test_disk_space_warning(self, resources_checker):
        """Testa aviso de espaço em disco."""
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk.return_value = Mock(
                percent=88.0,
                free=2 * 1024 * 1024 * 1024  # 2GB
            )
            
            result = resources_checker.check_disk()
            
            assert result.status == "degraded"
            assert "disk space" in result.message.lower()


class TestHealthEndpoint:
    """Testes para o endpoint de health check."""
    
    def test_health_endpoint_response_format(self, client):
        """Testa formato da resposta do endpoint de saúde."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
        assert "version" in data
        assert "uptime_seconds" in data
    
    def test_detailed_health_check(self, client, auth_headers):
        """Testa health check detalhado (requer autenticação)."""
        response = client.get("/health/detailed", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "database" in data["checks"]
        assert "response_time_ms" in data["checks"]["database"]
        assert "ml_models" in data["checks"]
        assert "resources" in data["checks"]
    
    def test_readiness_probe(self, client):
        """Testa probe de prontidão para Kubernetes."""
        response = client.get("/ready")
        
        if response.status_code == 200:
            assert response.json()["ready"] is True
        else:
            assert response.status_code == 503
    
    def test_liveness_probe(self, client):
        """Testa probe de vivacidade para Kubernetes."""
        response = client.get("/alive")
        
        assert response.status_code == 200
        assert response.json()["alive"] is True


class TestHealthMetrics:
    """Testes para métricas de saúde."""
    
    def test_health_metrics_collection(self):
        """Testa coleta de métricas de saúde."""
        from app.health import HealthMetricsCollector
        
        collector = HealthMetricsCollector()
        
        # Registra algumas métricas
        collector.record_health_check("database", "healthy", 15.5)
        collector.record_health_check("ml_models", "healthy", 120.0)
        collector.record_health_check("cache", "degraded", 5.0)
        
        metrics = collector.get_metrics()
        
        assert metrics["total_checks"] == 3
        assert metrics["healthy_checks"] == 2
        assert metrics["degraded_checks"] == 1
        assert metrics["average_response_time_ms"] > 0
    
    def test_health_history(self):
        """Testa histórico de saúde."""
        from app.health import HealthHistory
        
        history = HealthHistory(max_entries=10)
        
        # Adiciona entradas ao histórico
        for i in range(15):
            history.add_entry({
                "timestamp": datetime.now() - timedelta(minutes=i),
                "status": "healthy" if i % 3 != 0 else "degraded",
                "checks": {}
            })
        
        # Verifica que mantém apenas as últimas 10
        assert len(history.entries) == 10
        
        # Verifica análise de tendência
        trend = history.analyze_trend()
        assert "degradation_rate" in trend
        assert trend["last_degraded_timestamp"] is not None