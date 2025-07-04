print('🔧 ADICIONANDO CLASSES FALTANTES...')

# Adicionar HealthChecker ao health.py
health_additions = '''

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
'''

# Adicionar ao health.py
with open('backend/app/health.py', 'r', encoding='utf-8') as f:
    health_content = f.read()

if 'class HealthChecker' not in health_content:
    health_content += health_additions
    with open('backend/app/health.py', 'w', encoding='utf-8') as f:
        f.write(health_content)
    print('✅ HealthChecker adicionado!')

# Adicionar ao config.py
with open('backend/app/config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()

if 'class DatabaseConfig' not in config_content:
    config_content += '\n' + '''

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
'''
    
    with open('backend/app/config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    print('✅ DatabaseConfig adicionado!')

# Adicionar ValidationResult ao validation_service
validation_additions = '''

class ValidationResult:
    """Validation result class"""
    
    def __init__(self, is_valid: bool, message: str = None, code: str = None, data: dict = None):
        self.is_valid = is_valid
        self.message = message or ("Validation passed" if is_valid else "Validation failed")
        self.code = code
        self.data = data or {}
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: str, field: str = None):
        """Add validation error"""
        self.errors.append({"message": error, "field": field})
        self.is_valid = False
    
    def add_warning(self, warning: str, field: str = None):
        """Add validation warning"""
        self.warnings.append({"message": warning, "field": field})
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "message": self.message,
            "code": self.code,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings
        }
'''

# Verificar se existe o arquivo validation_service
import os
validation_file = 'backend/app/services/validation_service.py'
if os.path.exists(validation_file):
    with open(validation_file, 'r', encoding='utf-8') as f:
        validation_content = f.read()

    if 'class ValidationResult' not in validation_content:
        validation_content += validation_additions
        with open(validation_file, 'w', encoding='utf-8') as f:
            f.write(validation_content)
        print('✅ ValidationResult adicionado!')
else:
    # Criar arquivo se não existir
    with open(validation_file, 'w', encoding='utf-8') as f:
        f.write(f'''"""
Validation service module
"""
{validation_additions}
''')
    print('✅ ValidationResult criado em novo arquivo!')

print('✅ Todas as classes faltantes foram adicionadas!')

