"""
Módulo de utilidades para el sistema de scraping
"""

from .logger import get_logger
from .error_handler import handle_errors, retry_on_failure

__all__ = ['get_logger', 'handle_errors', 'retry_on_failure']
