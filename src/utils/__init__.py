"""
Módulo de utilidades para el sistema de scraping
"""

from .logger import get_logger
from .error_handler import ErrorHandler, retry_on_failure, log_exception

__all__ = ['get_logger', 'ErrorHandler', 'retry_on_failure', 'log_exception']
