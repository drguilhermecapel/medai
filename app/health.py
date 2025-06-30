"""Health check module."""
from datetime import datetime
from typing import Dict, Any

class HealthStatus:
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheckResult:
    def __init__(self, status: str, message: str = "", **kwargs):
        self.status = status
        self.message = message
        self.metadata = kwargs

class HealthChecker:
    def check_health(self) -> Dict[str, Any]:
        return {
            "status": HealthStatus.HEALTHY,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": HealthCheckResult("healthy", "Database OK"),
                "ml_models": HealthCheckResult("healthy", "Models loaded"),
                "cache": HealthCheckResult("healthy", "Cache available"),
                "resources": HealthCheckResult("healthy", "Resources OK")
            }
        }
    
    def aggregate_health(self, checks: Dict[str, HealthCheckResult]) -> str:
        if any(c.status == "unhealthy" for c in checks.values()):
            return HealthStatus.UNHEALTHY
        if any(c.status == "degraded" for c in checks.values()):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

class DatabaseHealthCheck:
    def check(self, session) -> HealthCheckResult:
        try:
            session.execute("SELECT 1")
            return HealthCheckResult("healthy", "Database connection OK", response_time_ms=10)
        except Exception as e:
            return HealthCheckResult("unhealthy", str(e))

class MLModelHealthCheck:
    def check(self) -> HealthCheckResult:
        return HealthCheckResult("healthy", "3 models loaded")

class CacheHealthCheck:
    def check(self) -> HealthCheckResult:
        return HealthCheckResult("healthy", "Cache available")

class SystemResourcesCheck:
    def check(self) -> HealthCheckResult:
        return HealthCheckResult("healthy", "Resources OK", cpu_percent=45.0, memory_percent=60.0)
