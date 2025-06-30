import pytest
from app.health import HealthChecker, HealthStatus

def test_health_checker():
    checker = HealthChecker()
    result = checker.check_health()
    assert "status" in result
    assert result["status"] in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]

def test_health_components():
    from app.health import DatabaseHealthCheck
    checker = DatabaseHealthCheck()
    from unittest.mock import Mock
    result = checker.check(Mock())
    assert result.status in ["healthy", "unhealthy"]
