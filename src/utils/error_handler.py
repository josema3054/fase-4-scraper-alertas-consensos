"""
Manejo de errores y reintentos del sistema
"""

import asyncio
import traceback
from datetime import datetime
from typing import Callable, Any, Optional
from functools import wraps

from ..utils.logger import get_logger

logger = get_logger('error_handler')

class ErrorHandler:
    """Manejador centralizado de errores"""
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 60):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.error_count = 0
        self.last_error_time = None
    
    async def handle_error(self, error: Exception, context: str, critical: bool = False):
        """
        Manejar error del sistema
        
        Args:
            error: Excepción ocurrida
            context: Contexto donde ocurrió el error
            critical: Si es un error crítico que requiere atención inmediata
        """
        self.error_count += 1
        self.last_error_time = datetime.now()
        
        error_msg = f"❌ Error en {context}: {str(error)}"
        
        if critical:
            logger.critical(error_msg, exc_info=True)
        else:
            logger.error(error_msg, exc_info=True)
        
        # Registrar en base de datos si es posible
        try:
            await self._log_error_to_db(error, context, critical)
        except Exception as db_error:
            logger.warning(f"⚠️ No se pudo registrar error en DB: {db_error}")
    
    async def _log_error_to_db(self, error: Exception, context: str, critical: bool):
        """Registrar error en base de datos"""
        # Implementación pendiente: conexión con base de datos
        pass
    
    def reset_error_count(self):
        """Resetear contador de errores"""
        self.error_count = 0
        logger.info("🔄 Contador de errores reseteado")

def retry_on_failure(max_retries: int = 3, delay: int = 60, exceptions: tuple = (Exception,)):
    """
    Decorador para reintentar funciones que fallan
    
    Args:
        max_retries: Número máximo de reintentos
        delay: Delay entre reintentos en segundos
        exceptions: Tupla de excepciones a capturar
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                        
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(f"⚠️ Intento {attempt + 1}/{max_retries + 1} falló: {str(e)}")
                        logger.info(f"⏳ Esperando {delay}s antes del siguiente intento...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"❌ Todos los intentos fallaron para {func.__name__}")
            
            # Si llegamos aquí, todos los intentos fallaron
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default_return=None, **kwargs) -> Any:
    """
    Ejecutar función de manera segura, retornando valor por defecto si falla
    
    Args:
        func: Función a ejecutar
        default_return: Valor a retornar si la función falla
        *args, **kwargs: Argumentos para la función
    
    Returns:
        Resultado de la función o default_return si falla
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"⚠️ Ejecución segura falló en {func.__name__}: {str(e)}")
        return default_return

class CircuitBreaker:
    """Implementación de Circuit Breaker para prevenir cascadas de errores"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecutar función a través del circuit breaker
        
        Args:
            func: Función a ejecutar
            *args, **kwargs: Argumentos para la función
        
        Returns:
            Resultado de la función
        
        Raises:
            Exception: Si el circuit breaker está abierto o la función falla
        """
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
                logger.info("🔄 Circuit breaker en estado HALF_OPEN")
            else:
                raise Exception("Circuit breaker está OPEN - función no ejecutada")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Éxito - resetear si estaba en HALF_OPEN
            if self.state == 'HALF_OPEN':
                self._reset()
            
            return result
            
        except Exception as e:
            self._record_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Verificar si es momento de intentar resetear el circuit breaker"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout
    
    def _record_failure(self):
        """Registrar un fallo"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"🔴 Circuit breaker ABIERTO - {self.failure_count} fallos consecutivos")
    
    def _reset(self):
        """Resetear el circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
        logger.info("✅ Circuit breaker reseteado - estado CLOSED")

# Instancia global del manejador de errores
error_handler = ErrorHandler()

def log_exception(func: Callable) -> Callable:
    """Decorador simple para loggear excepciones"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Excepción en {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper
