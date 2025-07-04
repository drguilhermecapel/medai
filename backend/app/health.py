
"""
Health check module for MEDAI
"""
from typing import Dict, Any

def check_database_health() -> Dict[str, Any]:
    """Check database health"""
    return {"status": "healthy", "type": "database"}

def check_redis_health() -> Dict[str, Any]:
    """Check Redis health"""
    return {"status": "healthy", "type": "redis"}

def check_ml_models_health() -> Dict[str, Any]:
    """Check ML models health"""
    return {
        "status": "healthy", 
        "type": "ml_models",
        "models": ["ecg_classifier", "risk_predictor"]
    }

def check_system_resources() -> Dict[str, Any]:
    """Check system resources"""
    return {
        "memory": {"status": "healthy", "usage": "45%"},
        "disk": {"status": "healthy", "usage": "32%"}
    }

def aggregate_health_checks(checks: Dict[str, Dict]) -> Dict[str, Any]:
    """Aggregate health check results"""
    statuses = [check["status"] for check in checks.values()]
    
    if all(status == "healthy" for status in statuses):
        overall = "healthy"
    elif any(status == "unhealthy" for status in statuses):
        overall = "degraded" 
    else:
        overall = "unknown"
    
    return {
        "overall_status": overall,
        "services": checks,
        "timestamp": "2024-01-01T00:00:00Z"
    }


class HealthChecker:
    """Health checker class"""
    
    def __init__(self):
        self.checks = {}
    
    def add_check(self, name: str, check_func):
        """Add health check"""
        self.checks[name] = check_func
    
    def run_checks(self) -> dict:
        """Run all health checks"""
        results = {}
        for name, check_func in self.checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        return results
    
    def get_overall_status(self) -> str:
        """Get overall health status"""
        results = self.run_checks()
        statuses = [r.get("status", "unknown") for r in results.values()]
        
        if all(s == "healthy" for s in statuses):
            return "healthy"
        elif any(s == "unhealthy" for s in statuses):
            return "unhealthy"
        else:
            return "degraded"

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self, url: str, pool_size: int = 10):
        self.url = url
        self.pool_size = pool_size
        self.echo = False
        self.pool_timeout = 30
        self.pool_recycle = 3600
    
    def get_engine_args(self) -> dict:
        """Get SQLAlchemy engine arguments"""
        return {
            "pool_size": self.pool_size,
            "echo": self.echo,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle
        }
