"""
Sistema de logging avanzado para el proyecto
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

def setup_logger(name: str, level: str = "DEBUG") -> logging.Logger:
    """
    Configurar logger con rotación de archivos y formato personalizado
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato de mensajes
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo con rotación diaria
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"scraper_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=7,  # Mantener 7 días de logs
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def cleanup_old_logs(days: int = 7):
    """
    Limpiar logs antiguos
    
    Args:
        days: Días de logs a mantener
    """
    log_dir = Path("logs")
    if not log_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for log_file in log_dir.glob("*.log"):
        try:
            file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_date < cutoff_date:
                log_file.unlink()
                print(f"🗑️ Log eliminado: {log_file}")
        except Exception as e:
            print(f"❌ Error eliminando log {log_file}: {e}")

def log_system_info(logger: logging.Logger):
    """Registrar información del sistema al inicio"""
    import platform
    import psutil
    
    logger.info("🚀 Sistema iniciado")
    logger.info(f"🐍 Python: {platform.python_version()}")
    logger.info(f"💻 OS: {platform.system()} {platform.release()}")
    logger.info(f"🧠 RAM: {psutil.virtual_memory().total // (1024**3)} GB")
    logger.info(f"📁 Directorio: {os.getcwd()}")
    logger.info(f"⏰ Timezone: {datetime.now().astimezone().tzinfo}")

def log_scraping_event(logger: logging.Logger, sport: str, event_type: str, details: dict):
    """
    Registra eventos de scraping de forma estructurada
    
    Args:
        logger: Logger a usar
        sport: Deporte scrapeado
        event_type: Tipo de evento (start, success, error, retry)
        details: Detalles del evento
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    event_msg = f"🕷️ SCRAPING_{event_type.upper()}"
    event_msg += f" | {sport}"
    event_msg += f" | {timestamp}"
    
    if event_type == 'start':
        event_msg += f" | URL: {details.get('url', 'N/A')}"
        event_msg += f" | Tipo: {details.get('scraping_type', 'regular')}"
    
    elif event_type == 'success':
        event_msg += f" | Consensos: {details.get('consensus_count', 0)}"
        event_msg += f" | Tiempo: {details.get('duration_seconds', 0):.2f}s"
        event_msg += f" | Alto_consenso: {details.get('high_consensus_count', 0)}"
    
    elif event_type == 'error':
        event_msg += f" | Error: {details.get('error_message', 'Unknown')}"
        event_msg += f" | Intento: {details.get('attempt', 1)}"
        event_msg += f" | Reintentos_restantes: {details.get('retries_left', 0)}"
    
    elif event_type == 'retry':
        event_msg += f" | Intento: {details.get('attempt', 1)}"
        event_msg += f" | Espera: {details.get('delay_seconds', 0)}s"
    
    logger.info(event_msg)

def log_alert_event(logger: logging.Logger, alert_type: str, event_type: str, details: dict):
    """
    Registra eventos de alertas de forma estructurada
    
    Args:
        logger: Logger a usar
        alert_type: Tipo de alerta (consensus, error, daily_report)
        event_type: Tipo de evento (sent, failed, retry)
        details: Detalles del evento
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    event_msg = f"🚨 ALERT_{event_type.upper()}"
    event_msg += f" | {alert_type}"
    event_msg += f" | {timestamp}"
    
    if event_type == 'sent':
        event_msg += f" | Chats: {details.get('chat_count', 0)}"
        event_msg += f" | Mensaje_length: {details.get('message_length', 0)}"
        event_msg += f" | Consensos: {details.get('consensus_count', 0)}"
    
    elif event_type == 'failed':
        event_msg += f" | Error: {details.get('error_message', 'Unknown')}"
        event_msg += f" | Chat_ID: {details.get('chat_id', 'N/A')}"
        event_msg += f" | Intento: {details.get('attempt', 1)}"
    
    elif event_type == 'retry':
        event_msg += f" | Intento: {details.get('attempt', 1)}"
        event_msg += f" | Espera: {details.get('delay_seconds', 0)}s"
    
    logger.info(event_msg)

def generate_daily_report(logger: logging.Logger, log_file_path: str) -> dict:
    """
    Genera reporte diario basado en logs
    
    Args:
        logger: Logger a usar
        log_file_path: Ruta al archivo de log del día
        
    Returns:
        Diccionario con estadísticas del día
    """
    try:
        if not os.path.exists(log_file_path):
            logger.warning(f"Archivo de log no encontrado: {log_file_path}")
            return {}
        
        stats = {
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'scraping_events': {
                'total_attempts': 0,
                'successful': 0,
                'failed': 0,
                'retries': 0,
                'total_consensus': 0,
                'high_consensus': 0
            },
            'alert_events': {
                'total_sent': 0,
                'failed': 0,
                'consensus_alerts': 0,
                'error_alerts': 0,
                'daily_reports': 0
            },
            'error_summary': {
                'total_errors': 0,
                'critical_errors': 0,
                'network_errors': 0,
                'telegram_errors': 0
            },
            'system_info': {
                'uptime_hours': 0,
                'log_file_size': 0,
                'total_log_lines': 0
            }
        }
        
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            stats['system_info']['total_log_lines'] = len(lines)
            
            for line in lines:
                # Analizar eventos de scraping
                if 'SCRAPING_START' in line:
                    stats['scraping_events']['total_attempts'] += 1
                elif 'SCRAPING_SUCCESS' in line:
                    stats['scraping_events']['successful'] += 1
                    # Extraer número de consensos
                    if 'Consensos:' in line:
                        try:
                            consensus_count = int(line.split('Consensos:')[1].split('|')[0].strip())
                            stats['scraping_events']['total_consensus'] += consensus_count
                        except:
                            pass
                    # Extraer consensos altos
                    if 'Alto_consenso:' in line:
                        try:
                            high_count = int(line.split('Alto_consenso:')[1].split('|')[0].strip())
                            stats['scraping_events']['high_consensus'] += high_count
                        except:
                            pass
                elif 'SCRAPING_ERROR' in line:
                    stats['scraping_events']['failed'] += 1
                elif 'SCRAPING_RETRY' in line:
                    stats['scraping_events']['retries'] += 1
                
                # Analizar eventos de alertas
                if 'ALERT_SENT' in line:
                    stats['alert_events']['total_sent'] += 1
                    if 'consensus' in line.lower():
                        stats['alert_events']['consensus_alerts'] += 1
                    elif 'error' in line.lower():
                        stats['alert_events']['error_alerts'] += 1
                    elif 'daily' in line.lower():
                        stats['alert_events']['daily_reports'] += 1
                elif 'ALERT_FAILED' in line:
                    stats['alert_events']['failed'] += 1
                
                # Analizar errores
                if '[ERROR]' in line:
                    stats['error_summary']['total_errors'] += 1
                    if 'network' in line.lower() or 'connection' in line.lower():
                        stats['error_summary']['network_errors'] += 1
                    elif 'telegram' in line.lower():
                        stats['error_summary']['telegram_errors'] += 1
                elif '[CRITICAL]' in line:
                    stats['error_summary']['critical_errors'] += 1
        
        # Calcular tamaño del archivo
        stats['system_info']['log_file_size'] = os.path.getsize(log_file_path)
        
        logger.info(f"📊 Reporte diario generado: {stats['scraping_events']['successful']} scraping exitosos")
        return stats
        
    except Exception as e:
        logger.error(f"Error generando reporte diario: {e}")
        return {}

def log_daily_summary(logger: logging.Logger, stats: dict):
    """
    Registra resumen diario en formato estructurado
    
    Args:
        logger: Logger a usar
        stats: Estadísticas del día
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    logger.info("=" * 80)
    logger.info(f"📊 RESUMEN DIARIO - {stats.get('fecha', 'N/A')} - {timestamp}")
    logger.info("=" * 80)
    
    # Scraping stats
    scraping = stats.get('scraping_events', {})
    logger.info(f"🕷️ SCRAPING | Intentos: {scraping.get('total_attempts', 0)} | Exitosos: {scraping.get('successful', 0)} | Fallos: {scraping.get('failed', 0)}")
    logger.info(f"🕷️ SCRAPING | Consensos totales: {scraping.get('total_consensus', 0)} | Alto consenso: {scraping.get('high_consensus', 0)}")
    logger.info(f"🕷️ SCRAPING | Reintentos: {scraping.get('retries', 0)}")
    
    # Alert stats
    alerts = stats.get('alert_events', {})
    logger.info(f"🚨 ALERTAS | Enviadas: {alerts.get('total_sent', 0)} | Fallidas: {alerts.get('failed', 0)}")
    logger.info(f"🚨 ALERTAS | Consenso: {alerts.get('consensus_alerts', 0)} | Error: {alerts.get('error_alerts', 0)} | Reportes: {alerts.get('daily_reports', 0)}")
    
    # Error stats
    errors = stats.get('error_summary', {})
    logger.info(f"❌ ERRORES | Total: {errors.get('total_errors', 0)} | Críticos: {errors.get('critical_errors', 0)}")
    logger.info(f"❌ ERRORES | Red: {errors.get('network_errors', 0)} | Telegram: {errors.get('telegram_errors', 0)}")
    
    # System stats
    system = stats.get('system_info', {})
    logger.info(f"🔧 SISTEMA | Líneas de log: {system.get('total_log_lines', 0)} | Tamaño: {system.get('log_file_size', 0)} bytes")
    
    logger.info("=" * 80)

class LoggerMixin:
    """Mixin para agregar logging a cualquier clase"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = setup_logger(self.__class__.__name__)
    
    def log_info(self, message: str):
        """Log información"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log advertencia"""
        self.logger.warning(message)
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log error"""
        self.logger.error(message, exc_info=exc_info)
    
    def log_debug(self, message: str):
        """Log debug"""
        self.logger.debug(message)

# Logger principal del sistema
main_logger = setup_logger('consensus_alerts')

def get_logger(name: str) -> logging.Logger:
    """Obtener logger configurado por nombre"""
    return setup_logger(name)
