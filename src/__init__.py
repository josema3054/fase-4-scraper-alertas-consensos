"""
Paquete principal del sistema de scraping y alertas - Fase 4
"""

# Importaciones comentadas temporalmente para evitar errores circulares
# from .scraper import MLBScraper, ConsensusScheduler
# from .database import SupabaseClient, ConsensusModel, AlertModel, LogModel
# from .notifications import TelegramNotifier
# from .utils import get_logger, handle_errors, retry_on_failure

__version__ = "1.0.0"
__author__ = "Sistema Automatizado - Fase 4"

__all__ = [
    # 'MLBScraper',
    # 'ConsensusScheduler', 
    # 'SupabaseClient',
    # 'ConsensusModel',
    # 'AlertModel',
    # 'LogModel',
    # 'TelegramNotifier',
    'get_logger',
    'handle_errors',
    'retry_on_failure'
]
