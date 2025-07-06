"""
Configuração de logging para o sistema MedAI
Sistema estruturado de logs com diferentes níveis e formatos
"""
import logging
import logging.handlers
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import json
from pathlib import Path

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Formatter para logs em formato JSON estruturado"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata log record como JSON
        
        Args:
            record: Log record para formatar
            
        Returns:
            String JSON formatada
        """
        # Dados básicos do log
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adicionar informações de exceção se existir
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Adicionar dados extras se existirem
        if hasattr(record, 'extra') and record.extra:
            log_data["extra"] = record.extra
        
        # Adicionar informações específicas do MedAI
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, 'patient_id'):
            log_data["patient_id"] = record.patient_id
        
        if hasattr(record, 'action'):
            log_data["action"] = record.action
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para logs no console"""
    
    # Códigos de cor ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Ciano
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarelo
        'ERROR': '\033[31m',      # Vermelho
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata log record com cores
        
        Args:
            record: Log record para formatar
            
        Returns:
            String formatada com cores
        """
        # Aplicar cor baseada no nível
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formato base
        formatted = super().format(record)
        
        # Adicionar cores apenas se for terminal
        if sys.stderr.isatty():
            return f"{color}{formatted}{reset}"
        
        return formatted


class MedAILoggerAdapter(logging.LoggerAdapter):
    """Adapter para adicionar contexto médico aos logs"""
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any] = None):
        super().__init__(logger, extra or {})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Processa mensagem de log adicionando contexto
        
        Args:
            msg: Mensagem do log
            kwargs: Argumentos adicionais
            
        Returns:
            Tupla com mensagem processada e kwargs
        """
        # Adicionar dados extras do contexto
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        
        return msg, kwargs
    
    def log_medical_action(self, level: int, action: str, 
                          patient_id: str = None, exam_id: str = None,
                          diagnostic_id: str = None, **kwargs):
        """
        Log específico para ações médicas
        
        Args:
            level: Nível do log
            action: Ação realizada
            patient_id: ID do paciente (opcional)
            exam_id: ID do exame (opcional)
            diagnostic_id: ID do diagnóstico (opcional)
            **kwargs: Argumentos adicionais
        """
        extra = {
            'action': action,
            'category': 'medical_action'
        }
        
        if patient_id:
            extra['patient_id'] = patient_id
        if exam_id:
            extra['exam_id'] = exam_id
        if diagnostic_id:
            extra['diagnostic_id'] = diagnostic_id
        
        # Adicionar contexto extra
        extra.update(kwargs.get('extra', {}))
        kwargs['extra'] = extra
        
        self.log(level, f"Medical action: {action}", **kwargs)
    
    def log_ai_operation(self, level: int, operation: str, model_name: str,
                        confidence: float = None, processing_time: float = None,
                        **kwargs):
        """
        Log específico para operações de IA
        
        Args:
            level: Nível do log
            operation: Operação realizada
            model_name: Nome do modelo
            confidence: Confiança do resultado (opcional)
            processing_time: Tempo de processamento (opcional)
            **kwargs: Argumentos adicionais
        """
        extra = {
            'operation': operation,
            'model_name': model_name,
            'category': 'ai_operation'
        }
        
        if confidence is not None:
            extra['confidence'] = confidence
        if processing_time is not None:
            extra['processing_time'] = processing_time
        
        extra.update(kwargs.get('extra', {}))
        kwargs['extra'] = extra
        
        self.log(level, f"AI operation: {operation} with {model_name}", **kwargs)
    
    def log_security_event(self, level: int, event: str, user_id: str = None,
                          ip_address: str = None, **kwargs):
        """
        Log específico para eventos de segurança
        
        Args:
            level: Nível do log
            event: Evento de segurança
            user_id: ID do usuário (opcional)
            ip_address: Endereço IP (opcional)
            **kwargs: Argumentos adicionais
        """
        extra = {
            'event': event,
            'category': 'security'
        }
        
        if user_id:
            extra['user_id'] = user_id
        if ip_address:
            extra['ip_address'] = ip_address
        
        extra.update(kwargs.get('extra', {}))
        kwargs['extra'] = extra
        
        self.log(level, f"Security event: {event}", **kwargs)


class LoggerManager:
    """Gerenciador central de loggers do sistema"""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.configured = False
    
    def setup_logging(self) -> None:
        """Configura sistema de logging"""
        if self.configured:
            return
        
        # Configurar logger raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Remover handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Configurar handlers
        self._setup_console_handler(root_logger)
        self._setup_file_handler(root_logger)
        
        # Configurar loggers específicos
        self._setup_specific_loggers()
        
        # Configurar loggers de terceiros
        self._configure_third_party_loggers()
        
        self.configured = True
    
    def _setup_console_handler(self, logger: logging.Logger) -> None:
        """Configura handler para console"""
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Formato colorido para desenvolvimento
        if settings.is_development:
            formatter = ColoredFormatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # JSON para produção
            formatter = JSONFormatter()
        
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        logger.addHandler(console_handler)
    
    def _setup_file_handler(self, logger: logging.Logger) -> None:
        """Configura handler para arquivo"""
        if not settings.LOG_FILE:
            return
        
        # Criar diretório se não existir
        log_dir = Path(settings.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Handler com rotação
        file_handler = logging.handlers.RotatingFileHandler(
            filename=settings.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Sempre JSON para arquivos
        formatter = JSONFormatter()
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        logger.addHandler(file_handler)
    
    def _setup_specific_loggers(self) -> None:
        """Configura loggers específicos do sistema"""
        
        # Logger para ações médicas
        medical_logger = logging.getLogger('medai.medical')
        medical_logger.setLevel(logging.INFO)
        
        # Logger para operações de IA
        ai_logger = logging.getLogger('medai.ai')
        ai_logger.setLevel(logging.INFO)
        
        # Logger para segurança
        security_logger = logging.getLogger('medai.security')
        security_logger.setLevel(logging.WARNING)
        
        # Logger para performance
        performance_logger = logging.getLogger('medai.performance')
        performance_logger.setLevel(logging.INFO)
        
        # Logger para auditoria
        audit_logger = logging.getLogger('medai.audit')
        audit_logger.setLevel(logging.INFO)
        
        # Adicionar handler específico para auditoria
        if settings.is_production:
            audit_handler = logging.handlers.RotatingFileHandler(
                filename=str(Path(settings.LOG_FILE).parent / 'audit.log'),
                maxBytes=50 * 1024 * 1024,  # 50MB
                backupCount=10,
                encoding='utf-8'
            )
            audit_handler.setFormatter(JSONFormatter())
            audit_logger.addHandler(audit_handler)
    
    def _configure_third_party_loggers(self) -> None:
        """Configura loggers de bibliotecas terceiras"""
        
        # SQLAlchemy - reduzir verbosidade
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
        
        # Uvicorn
        logging.getLogger('uvicorn.access').setLevel(logging.INFO)
        logging.getLogger('uvicorn.error').setLevel(logging.INFO)
        
        # FastAPI
        logging.getLogger('fastapi').setLevel(logging.INFO)
        
        # Requests
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> MedAILoggerAdapter:
        """
        Obtém logger com adapter específico do MedAI
        
        Args:
            name: Nome do logger
            
        Returns:
            Logger adapter configurado
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return MedAILoggerAdapter(self.loggers[name])
    
    def get_medical_logger(self) -> MedAILoggerAdapter:
        """Obtém logger específico para ações médicas"""
        return self.get_logger('medai.medical')
    
    def get_ai_logger(self) -> MedAILoggerAdapter:
        """Obtém logger específico para IA"""
        return self.get_logger('medai.ai')
    
    def get_security_logger(self) -> MedAILoggerAdapter:
        """Obtém logger específico para segurança"""
        return self.get_logger('medai.security')
    
    def get_performance_logger(self) -> MedAILoggerAdapter:
        """Obtém logger específico para performance"""
        return self.get_logger('medai.performance')
    
    def get_audit_logger(self) -> MedAILoggerAdapter:
        """Obtém logger específico para auditoria"""
        return self.get_logger('medai.audit')


# Instância global do gerenciador
logger_manager = LoggerManager()


def setup_logging() -> None:
    """Função de conveniência para configurar logging"""
    logger_manager.setup_logging()


def get_logger(name: str) -> MedAILoggerAdapter:
    """
    Função de conveniência para obter logger
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger adapter configurado
    """
    return logger_manager.get_logger(name)


# Loggers específicos de conveniência
def get_medical_logger() -> MedAILoggerAdapter:
    """Logger para ações médicas"""
    return logger_manager.get_medical_logger()


def get_ai_logger() -> MedAILoggerAdapter:
    """Logger para operações de IA"""
    return logger_manager.get_ai_logger()


def get_security_logger() -> MedAILoggerAdapter:
    """Logger para eventos de segurança"""
    return logger_manager.get_security_logger()


def get_performance_logger() -> MedAILoggerAdapter:
    """Logger para métricas de performance"""
    return logger_manager.get_performance_logger()


def get_audit_logger() -> MedAILoggerAdapter:
    """Logger para auditoria"""
    return logger_manager.get_audit_logger()


# Decoradores para logging automático
def log_medical_action(action: str):
    """
    Decorator para logar ações médicas automaticamente
    
    Args:
        action: Descrição da ação
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_medical_logger()
            
            try:
                result = func(*args, **kwargs)
                logger.log_medical_action(
                    logging.INFO, 
                    action,
                    extra={'status': 'success', 'function': func.__name__}
                )
                return result
            except Exception as e:
                logger.log_medical_action(
                    logging.ERROR,
                    f"{action} - Error: {str(e)}",
                    extra={'status': 'error', 'function': func.__name__}
                )
                raise
        
        return wrapper
    return decorator


def log_ai_operation(operation: str, model_name: str):
    """
    Decorator para logar operações de IA
    
    Args:
        operation: Tipo de operação
        model_name: Nome do modelo
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_ai_logger()
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Extrair confiança se disponível no resultado
                confidence = None
                if isinstance(result, dict) and 'confidence' in result:
                    confidence = result['confidence']
                
                logger.log_ai_operation(
                    logging.INFO,
                    operation,
                    model_name,
                    confidence=confidence,
                    processing_time=processing_time,
                    extra={'status': 'success', 'function': func.__name__}
                )
                
                return result
                
            except Exception as e:
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.log_ai_operation(
                    logging.ERROR,
                    f"{operation} - Error: {str(e)}",
                    model_name,
                    processing_time=processing_time,
                    extra={'status': 'error', 'function': func.__name__}
                )
                raise
        
        return wrapper
    return decorator


def log_performance(operation: str):
    """
    Decorator para logar métricas de performance
    
    Args:
        operation: Nome da operação
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_performance_logger()
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(
                    f"Performance: {operation} completed in {duration:.3f}s",
                    extra={
                        'operation': operation,
                        'duration': duration,
                        'status': 'success',
                        'function': func.__name__
                    }
                )
                
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                logger.error(
                    f"Performance: {operation} failed after {duration:.3f}s - {str(e)}",
                    extra={
                        'operation': operation,
                        'duration': duration,
                        'status': 'error',
                        'function': func.__name__
                    }
                )
                raise
        
        return wrapper
    return decorator


# Função para criar logger contextual
def create_contextual_logger(name: str, **context) -> MedAILoggerAdapter:
    """
    Cria logger com contexto específico
    
    Args:
        name: Nome do logger
        **context: Contexto a ser adicionado a todos os logs
        
    Returns:
        Logger com contexto configurado
    """
    base_logger = logging.getLogger(name)
    return MedAILoggerAdapter(base_logger, context)


# Configurações específicas por ambiente
if settings.is_development:
    # Em desenvolvimento, logs mais verbosos
    logging.getLogger('medai').setLevel(logging.DEBUG)
elif settings.is_production:
    # Em produção, logs mais restritivos
    logging.getLogger('medai').setLevel(logging.INFO)
    
    # Desabilitar logs de debug de bibliotecas
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.ERROR)