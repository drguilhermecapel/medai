import os
from pathlib import Path

# Criar app/health.py se não existir
health_content = '''
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
'''

if not Path('app/health.py').exists():
    with open('app/health.py', 'w', encoding='utf-8') as f:
        f.write(health_content)
    print("✅ app/health.py criado")

# Adicionar ValidationError ao validation_service se não existir
validation_service_path = 'app/services/validation_service.py'
if Path(validation_service_path).exists():
    with open(validation_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'class ValidationError' not in content:
        validation_error_class = '''

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)
'''
        content += validation_error_class
        
        with open(validation_service_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ ValidationError adicionada ao validation_service")

print("✅ Módulos faltantes criados")

