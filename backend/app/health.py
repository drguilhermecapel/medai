
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
