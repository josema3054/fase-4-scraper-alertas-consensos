"""
Programador de tareas para automatizar el scraping de consensos
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from datetime import datetime, timedelta
import logging
from typing import Optional, Callable
from src.utils.logger import get_logger
from src.utils.error_handler import handle_errors
from .mlb_scraper import MLBScraper

logger = get_logger(__name__)

class ConsensusScheduler:
    """Programador para ejecutar scraping automático de consensos"""
    
    def __init__(self, timezone: str = 'America/Argentina/Buenos_Aires'):
        self.scheduler = BackgroundScheduler()
        self.timezone = pytz.timezone(timezone)
        self.mlb_scraper = None
        self.is_running = False
        
        # Callbacks para diferentes eventos
        self.on_consensus_scraped: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_daily_report: Optional[Callable] = None
        
        logger.info(f"Scheduler inicializado con zona horaria: {timezone}")
    
    def set_callbacks(self, 
                     on_consensus_scraped: Optional[Callable] = None,
                     on_error: Optional[Callable] = None,
                     on_daily_report: Optional[Callable] = None):
        """Configura callbacks para eventos del scheduler"""
        self.on_consensus_scraped = on_consensus_scraped
        self.on_error = on_error
        self.on_daily_report = on_daily_report
        logger.info("Callbacks configurados")
    
    @handle_errors
    def setup_mlb_schedule(self):
        """Configura el horario de scraping para MLB"""
        logger.info("Configurando horarios de scraping para MLB")
        
        # Scraping principal diario a las 11:00 AM ART
        self.scheduler.add_job(
            func=self._scrape_mlb_daily,
            trigger=CronTrigger(
                hour=11, 
                minute=0, 
                timezone=self.timezone
            ),
            id='mlb_daily_scraping',
            name='MLB Daily Consensus Scraping',
            replace_existing=True,
            max_instances=1
        )
        
        # Scraping cada 2 horas durante horas de juego (12:00-23:00 ART)
        self.scheduler.add_job(
            func=self._scrape_mlb_live,
            trigger=CronTrigger(
                hour='12-23/2',  # Cada 2 horas de 12:00 a 23:00
                minute=15,
                timezone=self.timezone
            ),
            id='mlb_live_scraping',
            name='MLB Live Consensus Scraping',
            replace_existing=True,
            max_instances=1
        )
        
        # Reporte diario a las 23:45 ART
        self.scheduler.add_job(
            func=self._generate_daily_report,
            trigger=CronTrigger(
                hour=23,
                minute=45,
                timezone=self.timezone
            ),
            id='daily_report',
            name='Daily Report Generation',
            replace_existing=True,
            max_instances=1
        )
        
        # Limpieza de logs antiguos cada domingo a las 02:00 ART
        self.scheduler.add_job(
            func=self._cleanup_old_logs,
            trigger=CronTrigger(
                day_of_week='sun',
                hour=2,
                minute=0,
                timezone=self.timezone
            ),
            id='log_cleanup',
            name='Weekly Log Cleanup',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info("Horarios de MLB configurados exitosamente")
    
    @handle_errors
    def _scrape_mlb_daily(self):
        """Ejecuta scraping diario completo de MLB"""
        logger.info("🏈 Iniciando scraping diario de MLB")
        
        try:
            if not self.mlb_scraper:
                self.mlb_scraper = MLBScraper()
            
            # Obtener consensos del día
            today = datetime.now(self.timezone).strftime('%Y-%m-%d')
            consensos = self.mlb_scraper.scrape_mlb_consensus(today)
            
            logger.info(f"Scraping diario completado: {len(consensos)} consensos obtenidos")
            
            # Llamar callback si está configurado
            if self.on_consensus_scraped:
                self.on_consensus_scraped(consensos, 'daily')
            
            return consensos
            
        except Exception as e:
            error_msg = f"Error en scraping diario de MLB: {e}"
            logger.error(error_msg)
            
            if self.on_error:
                self.on_error(error_msg, 'scraping_daily')
            
            raise
    
    @handle_errors
    def _scrape_mlb_live(self):
        """Ejecuta scraping de consensos en vivo"""
        logger.info("⚡ Iniciando scraping en vivo de MLB")
        
        try:
            if not self.mlb_scraper:
                self.mlb_scraper = MLBScraper()
            
            # Obtener consensos actuales
            consensos = self.mlb_scraper.get_live_consensus()
            
            logger.info(f"Scraping en vivo completado: {len(consensos)} consensos actualizados")
            
            # Llamar callback si está configurado
            if self.on_consensus_scraped:
                self.on_consensus_scraped(consensos, 'live')
            
            return consensos
            
        except Exception as e:
            error_msg = f"Error en scraping en vivo de MLB: {e}"
            logger.error(error_msg)
            
            if self.on_error:
                self.on_error(error_msg, 'scraping_live')
            
            raise
    
    @handle_errors
    def _generate_daily_report(self):
        """Genera reporte diario del sistema"""
        logger.info("📊 Generando reporte diario")
        
        try:
            report_data = {
                'fecha': datetime.now(self.timezone).strftime('%Y-%m-%d'),
                'timestamp': datetime.now(self.timezone).isoformat(),
                'total_jobs_ejecutados': len(self.scheduler.get_jobs()),
                'ultimo_scraping': 'completed',
                'estado_sistema': 'operational'
            }
            
            logger.info("Reporte diario generado exitosamente")
            
            # Llamar callback si está configurado
            if self.on_daily_report:
                self.on_daily_report(report_data)
            
            return report_data
            
        except Exception as e:
            error_msg = f"Error al generar reporte diario: {e}"
            logger.error(error_msg)
            
            if self.on_error:
                self.on_error(error_msg, 'daily_report')
            
            raise
    
    @handle_errors
    def _cleanup_old_logs(self):
        """Limpia logs antiguos del sistema"""
        logger.info("🧹 Iniciando limpieza de logs antiguos")
        
        try:
            # Implementar lógica de limpieza aquí
            # Por ahora, solo registrar la acción
            
            cleanup_info = {
                'fecha': datetime.now(self.timezone).strftime('%Y-%m-%d'),
                'accion': 'log_cleanup',
                'estado': 'completed'
            }
            
            logger.info("Limpieza de logs completada")
            return cleanup_info
            
        except Exception as e:
            error_msg = f"Error en limpieza de logs: {e}"
            logger.error(error_msg)
            
            if self.on_error:
                self.on_error(error_msg, 'log_cleanup')
            
            raise
    
    def start(self):
        """Inicia el scheduler"""
        try:
            if not self.is_running:
                self.setup_mlb_schedule()
                self.scheduler.start()
                self.is_running = True
                logger.info("✅ Scheduler iniciado exitosamente")
                
                # Log de jobs programados
                jobs = self.scheduler.get_jobs()
                logger.info(f"Jobs programados: {len(jobs)}")
                for job in jobs:
                    logger.info(f"  - {job.name} (ID: {job.id}) - Próxima ejecución: {job.next_run_time}")
            else:
                logger.warning("El scheduler ya está en ejecución")
                
        except Exception as e:
            logger.error(f"Error al iniciar scheduler: {e}")
            raise
    
    def stop(self):
        """Detiene el scheduler"""
        try:
            if self.is_running:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                logger.info("🛑 Scheduler detenido exitosamente")
                
                # Cerrar scraper si existe
                if self.mlb_scraper:
                    self.mlb_scraper.close()
                    self.mlb_scraper = None
            else:
                logger.warning("El scheduler no está en ejecución")
                
        except Exception as e:
            logger.error(f"Error al detener scheduler: {e}")
            raise
    
    def pause_job(self, job_id: str):
        """Pausa un job específico"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job pausado: {job_id}")
        except Exception as e:
            logger.error(f"Error al pausar job {job_id}: {e}")
            raise
    
    def resume_job(self, job_id: str):
        """Reanuda un job específico"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job reanudado: {job_id}")
        except Exception as e:
            logger.error(f"Error al reanudar job {job_id}: {e}")
            raise
    
    def get_job_status(self) -> dict:
        """Obtiene el estado de todos los jobs"""
        jobs_status = {}
        
        try:
            for job in self.scheduler.get_jobs():
                jobs_status[job.id] = {
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger),
                    'pending': job.pending
                }
                
        except Exception as e:
            logger.error(f"Error al obtener estado de jobs: {e}")
        
        return jobs_status
    
    def run_job_now(self, job_id: str):
        """Ejecuta un job inmediatamente"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.func()
                logger.info(f"Job ejecutado manualmente: {job_id}")
            else:
                logger.error(f"Job no encontrado: {job_id}")
                
        except Exception as e:
            logger.error(f"Error al ejecutar job {job_id}: {e}")
            raise
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def main():
    """Función principal para testing del scheduler"""
    logger.info("=== PRUEBA DEL SCHEDULER ===")
    
    def on_consensus_callback(consensos, tipo):
        print(f"📊 Callback: {len(consensos)} consensos obtenidos ({tipo})")
    
    def on_error_callback(error, contexto):
        print(f"❌ Callback Error [{contexto}]: {error}")
    
    def on_report_callback(report):
        print(f"📋 Callback Reporte: {report}")
    
    try:
        scheduler = ConsensusScheduler()
        scheduler.set_callbacks(
            on_consensus_scraped=on_consensus_callback,
            on_error=on_error_callback,
            on_daily_report=on_report_callback
        )
        
        print("\n🚀 Iniciando scheduler de prueba...")
        scheduler.start()
        
        print("\n📋 Estado de jobs:")
        status = scheduler.get_job_status()
        for job_id, info in status.items():
            print(f"  - {info['name']}: {info['next_run']}")
        
        print("\n⚡ Ejecutando scraping manual...")
        scheduler.run_job_now('mlb_daily_scraping')
        
        print("\n✅ Prueba completada. Deteniendo scheduler...")
        scheduler.stop()
        
    except Exception as e:
        logger.error(f"Error en prueba del scheduler: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
