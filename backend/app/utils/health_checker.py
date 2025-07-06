"""
Sistema de verificação de saúde do MedAI
Monitora estado de todos os componentes críticos do sistema
"""
import asyncio
import time
import psutil
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import engine, db_manager
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class HealthStatus(str, Enum):
    """Status de saúde dos componentes"""
    HEALTHY = "healthy"
    WARNING = "warning" 
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Status de saúde de um componente"""
    name: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    details: Dict[str, Any]
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['last_check'] = self.last_check.isoformat()
        data['status'] = self.status.value
        return data


class BaseHealthCheck:
    """Classe base para verificações de saúde"""
    
    def __init__(self, name: str, timeout: int = 5):
        self.name = name
        self.timeout = timeout
    
    async def check(self) -> ComponentHealth:
        """
        Executa verificação de saúde
        
        Returns:
            Status de saúde do componente
        """
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # Execução da verificação com timeout
            check_result = await asyncio.wait_for(
                self._perform_check(),
                timeout=self.timeout
            )
            
            if isinstance(check_result, dict):
                details.update(check_result)
            
            status = self._determine_status(details, errors)
            
        except asyncio.TimeoutError:
            status = HealthStatus.UNHEALTHY
            errors.append(f"Health check timeout after {self.timeout}s")
            
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            errors.append(f"Health check failed: {str(e)}")
            logger.error(f"Health check failed for {self.name}: {e}")
        
        response_time = (time.time() - start_time) * 1000
        
        return ComponentHealth(
            name=self.name,
            status=status,
            response_time_ms=round(response_time, 2),
            last_check=datetime.utcnow(),
            details=details,
            errors=errors
        )
    
    async def _perform_check(self) -> Dict[str, Any]:
        """
        Implementação específica da verificação
        Deve ser sobrescrita pelas subclasses
        """
        raise NotImplementedError
    
    def _determine_status(self, details: Dict[str, Any], errors: List[str]) -> HealthStatus:
        """
        Determina status baseado nos detalhes e erros
        
        Args:
            details: Detalhes da verificação
            errors: Lista de erros
            
        Returns:
            Status de saúde
        """
        if errors:
            return HealthStatus.UNHEALTHY
        
        # Verificar response time
        response_time = details.get('response_time_ms', 0)
        if response_time > 5000:  # > 5 segundos
            return HealthStatus.UNHEALTHY
        elif response_time > 1000:  # > 1 segundo
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY


class DatabaseHealthCheck(BaseHealthCheck):
    """Verificação de saúde do banco de dados"""
    
    def __init__(self):
        super().__init__("database", timeout=10)
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Verifica saúde do banco de dados"""
        details = {}
        
        try:
            # Teste de conexão básica
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as health_check"))
                health_value = result.scalar()
                
                if health_value != 1:
                    raise Exception("Database query returned unexpected result")
            
            # Informações do pool de conexões
            pool = engine.pool
            details.update({
                "connection_test": "passed",
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid()
            })
            
            # Informações da versão do banco
            try:
                db_info = db_manager.get_database_info()
                details.update({
                    "version": db_info.get("version", "unknown"),
                    "table_count": db_info.get("table_count", 0)
                })
            except Exception as e:
                logger.warning(f"Could not get database info: {e}")
            
        except SQLAlchemyError as e:
            raise Exception(f"Database connection failed: {str(e)}")
        
        return details


class RedisHealthCheck(BaseHealthCheck):
    """Verificação de saúde do Redis"""
    
    def __init__(self):
        super().__init__("redis", timeout=5)
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Verifica saúde do Redis"""
        details = {}
        
        try:
            # Criar conexão Redis
            redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=self.timeout
            )
            
            # Teste básico de ping
            if not redis_client.ping():
                raise Exception("Redis ping failed")
            
            # Informações do servidor
            info = redis_client.info()
            details.update({
                "ping_test": "passed",
                "version": info.get("redis_version"),
                "memory_used": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "uptime_seconds": info.get("uptime_in_seconds"),
                "keyspace": len(redis_client.keys("*"))
            })
            
            # Teste de escrita/leitura
            test_key = f"health_check_{int(time.time())}"
            test_value = "medai_health_test"
            
            redis_client.setex(test_key, 60, test_value)
            retrieved_value = redis_client.get(test_key)
            redis_client.delete(test_key)
            
            if retrieved_value != test_value:
                raise Exception("Redis read/write test failed")
            
            details["read_write_test"] = "passed"
            
        except redis.RedisError as e:
            raise Exception(f"Redis connection failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Redis health check failed: {str(e)}")
        
        return details


class SystemResourcesHealthCheck(BaseHealthCheck):
    """Verificação de recursos do sistema"""
    
    def __init__(self):
        super().__init__("system_resources", timeout=3)
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Verifica recursos do sistema"""
        details = {}
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            details["cpu_percent"] = cpu_percent
            
            # Memória
            memory = psutil.virtual_memory()
            details.update({
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2)
            })
            
            # Disco
            disk = psutil.disk_usage('/')
            details.update({
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            })
            
            # Load average (apenas Linux/Mac)
            try:
                load_avg = psutil.getloadavg()
                details["load_average"] = {
                    "1min": load_avg[0],
                    "5min": load_avg[1],
                    "15min": load_avg[2]
                }
            except AttributeError:
                # Windows não suporta getloadavg
                pass
            
        except Exception as e:
            raise Exception(f"System resources check failed: {str(e)}")
        
        return details
    
    def _determine_status(self, details: Dict[str, Any], errors: List[str]) -> HealthStatus:
        """Determina status baseado nos recursos do sistema"""
        if errors:
            return HealthStatus.UNHEALTHY
        
        # Verificar CPU
        if details.get("cpu_percent", 0) > 90:
            return HealthStatus.UNHEALTHY
        elif details.get("cpu_percent", 0) > 70:
            return HealthStatus.WARNING
        
        # Verificar memória
        if details.get("memory_percent", 0) > 90:
            return HealthStatus.UNHEALTHY
        elif details.get("memory_percent", 0) > 80:
            return HealthStatus.WARNING
        
        # Verificar disco
        if details.get("disk_percent", 0) > 95:
            return HealthStatus.UNHEALTHY
        elif details.get("disk_percent", 0) > 85:
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY


class AIModelsHealthCheck(BaseHealthCheck):
    """Verificação de saúde dos modelos de IA"""
    
    def __init__(self):
        super().__init__("ai_models", timeout=10)
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Verifica saúde dos modelos de IA"""
        details = {}
        
        try:
            from app.core.config import ML_CONFIG
            
            models_status = {}
            
            for model_name, config in ML_CONFIG.items():
                model_path = config.get("path")
                if model_path:
                    import os
                    if os.path.exists(model_path):
                        # Verificar se o modelo pode ser carregado
                        try:
                            # Aqui seria feita a verificação real do modelo
                            # Por enquanto, apenas verificar se o arquivo existe
                            file_size = os.path.getsize(model_path)
                            models_status[model_name] = {
                                "status": "available",
                                "path": model_path,
                                "size_mb": round(file_size / (1024*1024), 2),
                                "version": config.get("version", "unknown")
                            }
                        except Exception as e:
                            models_status[model_name] = {
                                "status": "error",
                                "error": str(e)
                            }
                    else:
                        models_status[model_name] = {
                            "status": "not_found",
                            "path": model_path
                        }
            
            details["models"] = models_status
            details["total_models"] = len(ML_CONFIG)
            details["available_models"] = len([
                m for m in models_status.values() 
                if m.get("status") == "available"
            ])
            
        except Exception as e:
            raise Exception(f"AI models check failed: {str(e)}")
        
        return details
    
    def _determine_status(self, details: Dict[str, Any], errors: List[str]) -> HealthStatus:
        """Determina status baseado na disponibilidade dos modelos"""
        if errors:
            return HealthStatus.UNHEALTHY
        
        total_models = details.get("total_models", 0)
        available_models = details.get("available_models", 0)
        
        if total_models == 0:
            return HealthStatus.WARNING
        
        availability_ratio = available_models / total_models
        
        if availability_ratio < 0.5:
            return HealthStatus.UNHEALTHY
        elif availability_ratio < 1.0:
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY


class HealthChecker:
    """Gerenciador principal de verificações de saúde"""
    
    def __init__(self):
        self.checks = [
            DatabaseHealthCheck(),
            RedisHealthCheck(),
            SystemResourcesHealthCheck(),
            AIModelsHealthCheck()
        ]
        self._cache = {}
        self._cache_ttl = 30  # 30 segundos
    
    async def check_all(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Executa todas as verificações de saúde
        
        Args:
            use_cache: Se deve usar cache para resultados recentes
            
        Returns:
            Resultado consolidado de todas as verificações
        """
        cache_key = "all_health_checks"
        
        # Verificar cache
        if use_cache and cache_key in self._cache:
            cached_result, cache_time = self._cache[cache_key]
            if (datetime.utcnow() - cache_time).total_seconds() < self._cache_ttl:
                return cached_result
        
        # Executar verificações em paralelo
        tasks = [check.check() for check in self.checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        component_results = {}
        overall_status = HealthStatus.HEALTHY
        total_response_time = 0
        error_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Erro na verificação
                component_name = self.checks[i].name
                component_results[component_name] = ComponentHealth(
                    name=component_name,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=0,
                    last_check=datetime.utcnow(),
                    details={},
                    errors=[f"Health check exception: {str(result)}"]
                ).to_dict()
                overall_status = HealthStatus.UNHEALTHY
                error_count += 1
            else:
                component_results[result.name] = result.to_dict()
                total_response_time += result.response_time_ms
                
                # Determinar status geral
                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.WARNING and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.WARNING
                
                if result.errors:
                    error_count += len(result.errors)
        
        # Compilar resultado final
        health_result = {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "summary": {
                "total_checks": len(self.checks),
                "healthy_checks": len([
                    r for r in component_results.values() 
                    if r["status"] == HealthStatus.HEALTHY.value
                ]),
                "warning_checks": len([
                    r for r in component_results.values() 
                    if r["status"] == HealthStatus.WARNING.value
                ]),
                "unhealthy_checks": len([
                    r for r in component_results.values() 
                    if r["status"] == HealthStatus.UNHEALTHY.value
                ]),
                "total_errors": error_count,
                "average_response_time_ms": round(
                    total_response_time / len(self.checks), 2
                ) if self.checks else 0
            },
            "components": component_results
        }
        
        # Atualizar cache
        self._cache[cache_key] = (health_result, datetime.utcnow())
        
        return health_result
    
    async def check_component(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Executa verificação de um componente específico
        
        Args:
            component_name: Nome do componente
            
        Returns:
            Resultado da verificação ou None se não encontrado
        """
        check = next((c for c in self.checks if c.name == component_name), None)
        if not check:
            return None
        
        result = await check.check()
        return result.to_dict()
    
    async def get_detailed_health(self) -> Dict[str, Any]:
        """
        Obtém verificação detalhada de saúde
        
        Returns:
            Resultado detalhado com informações adicionais
        """
        basic_health = await self.check_all()
        
        # Adicionar informações extras
        basic_health["detailed"] = True
        basic_health["uptime"] = self._get_uptime()
        basic_health["configuration"] = {
            "debug": settings.DEBUG,
            "workers": settings.WORKERS,
            "environment": settings.ENVIRONMENT
        }
        
        return basic_health
    
    def _get_uptime(self) -> Dict[str, Any]:
        """Calcula uptime do sistema"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            return {
                "uptime_seconds": int(uptime_seconds),
                "uptime_human": str(timedelta(seconds=int(uptime_seconds))),
                "boot_time": datetime.fromtimestamp(boot_time).isoformat()
            }
        except Exception:
            return {
                "uptime_seconds": 0,
                "uptime_human": "unknown",
                "boot_time": "unknown"
            }
    
    def clear_cache(self) -> None:
        """Limpa cache de verificações"""
        self._cache.clear()
    
    def add_custom_check(self, health_check: BaseHealthCheck) -> None:
        """
        Adiciona verificação customizada
        
        Args:
            health_check: Instância de verificação de saúde
        """
        self.checks.append(health_check)


# Instância global do health checker
health_checker = HealthChecker()


# Funções de conveniência
async def get_health_status() -> Dict[str, Any]:
    """Função de conveniência para obter status de saúde"""
    return await health_checker.check_all()


async def get_detailed_health_status() -> Dict[str, Any]:
    """Função de conveniência para obter status detalhado"""
    return await health_checker.get_detailed_health()


async def check_system_health() -> bool:
    """
    Verifica se o sistema está saudável
    
    Returns:
        True se todos os componentes estão saudáveis
    """
    health = await health_checker.check_all()
    return health["status"] == HealthStatus.HEALTHY.value