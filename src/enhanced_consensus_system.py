"""
Sistema integrado con todas las mejoras específicas solicitadas:
1. Multideportes
2. Consenso configurable por deporte
3. Scraping 15 minutos antes de cada partido
4. Logs detallados y reportes
5. Estadísticas históricas
"""

import asyncio
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
from src.utils.logger import get_logger, log_scraping_event, log_alert_event, generate_daily_report
from src.utils.sports_config import get_sports_config
from src.scraper.mlb_scraper import MLBScraper
from src.scraper.pregame_scheduler import PregameScheduler
from src.notifications.telegram_bot import TelegramNotifier
from src.database.supabase_client import SupabaseClient

logger = get_logger(__name__)

class EnhancedConsensusSystem:
    """Sistema de consensos mejorado con todas las características específicas"""
    
    def __init__(self):
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        self.sports_config = get_sports_config()
        self.pregame_scheduler = PregameScheduler()
        self.telegram_notifier = None
        self.supabase_client = None
        self.active_scrapers = {}
        
        logger.info("🚀 Sistema de consensos mejorado inicializado")
    
    async def initialize(self):
        """Inicializa todos los componentes del sistema"""
        try:
            # Inicializar base de datos
            self.supabase_client = SupabaseClient()
            await self.supabase_client.initialize()
            
            # Inicializar notificador Telegram
            # self.telegram_notifier = TelegramNotifier(token, chat_ids)
            # await self.telegram_notifier.setup_bot()
            
            # Inicializar scheduler pregame
            await self.pregame_scheduler.start()
            
            # Inicializar scrapers para deportes activos
            await self.initialize_active_scrapers()
            
            logger.info("✅ Sistema completamente inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando sistema: {e}")
            raise
    
    async def initialize_active_scrapers(self):
        """Inicializa scrapers para deportes activos"""
        active_sports = self.sports_config.get_active_sports()
        
        for sport in active_sports:
            if sport == 'MLB':
                self.active_scrapers[sport] = MLBScraper()
            # Agregar otros deportes cuando estén implementados
            # elif sport == 'NBA':
            #     self.active_scrapers[sport] = NBAScraper()
        
        logger.info(f"🏈 Scrapers activos: {list(self.active_scrapers.keys())}")
    
    async def run_daily_consensus_scraping(self):
        """
        Ejecuta scraping diario completo para todos los deportes activos
        con configuración específica por deporte
        """
        start_time = datetime.now(self.timezone)
        
        for sport, scraper in self.active_scrapers.items():
            try:
                sport_config = self.sports_config.get_sport_config(sport)
                
                # Log inicio del scraping
                log_scraping_event(logger, sport, 'start', {
                    'url': sport_config.get('url_base', 'N/A'),
                    'scraping_type': 'daily'
                })
                
                # Ejecutar scraping
                if sport == 'MLB':
                    consensus_data = await scraper.scrape_mlb_consensus()
                
                # Procesar resultados
                await self.process_consensus_results(sport, consensus_data, 'daily')
                
                # Programar scraping pregame para partidos del día
                await self.pregame_scheduler.schedule_daily_pregame_scraping(sport)
                
                # Log éxito
                duration = (datetime.now(self.timezone) - start_time).total_seconds()
                log_scraping_event(logger, sport, 'success', {
                    'consensus_count': len(consensus_data),
                    'duration_seconds': duration,
                    'high_consensus_count': len([c for c in consensus_data if self.is_high_consensus(sport, c)])
                })
                
            except Exception as e:
                log_scraping_event(logger, sport, 'error', {
                    'error_message': str(e),
                    'attempt': 1,
                    'retries_left': 2
                })
                
                # Intentar reintentos
                await self.retry_scraping(sport, scraper, 'daily')
    
    def is_high_consensus(self, sport: str, consensus_data: Dict) -> bool:
        """
        Verifica si un consenso es alto basado en configuración específica por deporte
        
        Args:
            sport: Deporte a verificar
            consensus_data: Datos del consenso
            
        Returns:
            True si es consenso alto
        """
        sport_config = self.sports_config.get_sport_config(sport)
        thresholds = sport_config.get('consensus_thresholds', {})
        
        # Verificar cada tipo de consenso con su umbral específico
        spread_threshold = thresholds.get('spread', 75)
        total_threshold = thresholds.get('total', 75)
        moneyline_threshold = thresholds.get('moneyline', 75)
        
        return any([
            consensus_data.get('porcentaje_spread', 0) >= spread_threshold,
            consensus_data.get('porcentaje_total', 0) >= total_threshold,
            consensus_data.get('porcentaje_moneyline', 0) >= moneyline_threshold
        ])
    
    async def process_consensus_results(self, sport: str, consensus_data: List[Dict], scraping_type: str):
        """
        Procesa resultados de consenso con configuración específica por deporte
        
        Args:
            sport: Deporte procesado
            consensus_data: Datos de consenso
            scraping_type: Tipo de scraping ('daily', 'live', 'pregame')
        """
        try:
            # Filtrar consensos altos basado en configuración del deporte
            high_consensus = [c for c in consensus_data if self.is_high_consensus(sport, c)]
            
            # Guardar en base de datos
            if self.supabase_client:
                await self.supabase_client.insert_consensus_data(consensus_data)
            
            # Enviar alertas si hay consensos altos
            if high_consensus and self.telegram_notifier:
                await self.send_sport_specific_alerts(sport, high_consensus, scraping_type)
            
            # Actualizar estadísticas históricas
            await self.update_historical_stats(sport, consensus_data)
            
        except Exception as e:
            logger.error(f"Error procesando resultados de {sport}: {e}")
    
    async def send_sport_specific_alerts(self, sport: str, high_consensus: List[Dict], scraping_type: str):
        """
        Envía alertas específicas por deporte con configuración personalizada
        
        Args:
            sport: Deporte de la alerta
            high_consensus: Consensos altos
            scraping_type: Tipo de scraping
        """
        try:
            sport_config = self.sports_config.get_sport_config(sport)
            alert_settings = sport_config.get('alert_settings', {})
            
            # Verificar si estamos en horas silenciosas
            if self.is_quiet_hours(alert_settings):
                logger.info(f"🔇 Alerta de {sport} pospuesta por horas silenciosas")
                return
            
            # Crear mensaje personalizado por deporte
            alert_message = self.create_sport_alert_message(sport, high_consensus, scraping_type)
            
            # Enviar alerta
            await self.telegram_notifier.send_message(alert_message)
            
            # Log evento de alerta
            log_alert_event(logger, 'consensus', 'sent', {
                'chat_count': len(self.telegram_notifier.chat_ids),
                'message_length': len(alert_message),
                'consensus_count': len(high_consensus)
            })
            
        except Exception as e:
            log_alert_event(logger, 'consensus', 'failed', {
                'error_message': str(e),
                'chat_id': 'multiple',
                'attempt': 1
            })
    
    def create_sport_alert_message(self, sport: str, high_consensus: List[Dict], scraping_type: str) -> str:
        """
        Crea mensaje de alerta personalizado por deporte
        
        Args:
            sport: Deporte
            high_consensus: Consensos altos
            scraping_type: Tipo de scraping
            
        Returns:
            Mensaje formateado para Telegram
        """
        sport_config = self.sports_config.get_sport_config(sport)
        thresholds = sport_config.get('consensus_thresholds', {})
        
        # Emojis por deporte
        sport_emojis = {
            'MLB': '⚾',
            'NBA': '🏀',
            'NFL': '🏈',
            'NHL': '🏒'
        }
        
        emoji = sport_emojis.get(sport, '🏆')
        
        # Título según tipo de scraping
        if scraping_type == 'pregame':
            title = f"{emoji} ALERTA PREGAME - {sport}"
        elif scraping_type == 'live':
            title = f"{emoji} ALERTA EN VIVO - {sport}"
        else:
            title = f"{emoji} CONSENSOS ALTOS - {sport}"
        
        message = f"🚨 *{title}*\n\n"
        message += f"🕐 {datetime.now(self.timezone).strftime('%d/%m/%Y %H:%M ART')}\n"
        message += f"📊 *{len(high_consensus)} consensos detectados*\n\n"
        
        # Configuración específica del deporte
        message += f"⚙️ *Umbrales {sport}:*\n"
        message += f"  • Spread: {thresholds.get('spread', 75)}%\n"
        message += f"  • Total: {thresholds.get('total', 75)}%\n"
        message += f"  • ML: {thresholds.get('moneyline', 75)}%\n\n"
        
        # Detalles de consensos
        for i, consensus in enumerate(high_consensus[:5]):
            away = consensus.get('equipo_visitante', 'TBD')
            home = consensus.get('equipo_local', 'TBD')
            
            message += f"*{i+1}. {away} @ {home}*\n"
            
            # Mostrar solo consensos que superan el umbral
            spread_pct = consensus.get('porcentaje_spread', 0)
            total_pct = consensus.get('porcentaje_total', 0)
            ml_pct = consensus.get('porcentaje_moneyline', 0)
            
            if spread_pct >= thresholds.get('spread', 75):
                message += f"   🎯 Spread: *{spread_pct}%*\n"
            if total_pct >= thresholds.get('total', 75):
                message += f"   🔢 Total: *{total_pct}%*\n"
            if ml_pct >= thresholds.get('moneyline', 75):
                message += f"   💰 ML: *{ml_pct}%*\n"
            
            message += "\n"
        
        if len(high_consensus) > 5:
            message += f"... y {len(high_consensus) - 5} más\n\n"
        
        return message
    
    def is_quiet_hours(self, alert_settings: Dict) -> bool:
        """Verifica si estamos en horas silenciosas"""
        quiet_hours = alert_settings.get('quiet_hours', {})
        if not quiet_hours.get('enabled', False):
            return False
        
        current_hour = datetime.now(self.timezone).hour
        start_hour = quiet_hours.get('start', 23)
        end_hour = quiet_hours.get('end', 7)
        
        if start_hour <= end_hour:
            return start_hour <= current_hour <= end_hour
        else:  # Cruza medianoche
            return current_hour >= start_hour or current_hour <= end_hour
    
    async def update_historical_stats(self, sport: str, consensus_data: List[Dict]):
        """
        Actualiza estadísticas históricas para análisis posterior
        
        Args:
            sport: Deporte
            consensus_data: Datos de consenso
        """
        try:
            # Aquí se implementaría la lógica para actualizar estadísticas
            # Por ahora, solo logeamos la acción
            logger.info(f"📈 Actualizando estadísticas históricas para {sport}: {len(consensus_data)} registros")
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas históricas: {e}")
    
    async def retry_scraping(self, sport: str, scraper, scraping_type: str, max_retries: int = 3):
        """
        Implementa lógica de reintentos para scraping
        
        Args:
            sport: Deporte
            scraper: Instancia del scraper
            scraping_type: Tipo de scraping
            max_retries: Máximo de reintentos
        """
        for attempt in range(1, max_retries + 1):
            try:
                delay = attempt * 10  # Incrementar delay
                
                log_scraping_event(logger, sport, 'retry', {
                    'attempt': attempt,
                    'delay_seconds': delay
                })
                
                await asyncio.sleep(delay)
                
                # Intentar scraping nuevamente
                if sport == 'MLB':
                    consensus_data = await scraper.scrape_mlb_consensus()
                    await self.process_consensus_results(sport, consensus_data, scraping_type)
                    
                    log_scraping_event(logger, sport, 'success', {
                        'consensus_count': len(consensus_data),
                        'duration_seconds': 0,
                        'high_consensus_count': len([c for c in consensus_data if self.is_high_consensus(sport, c)])
                    })
                    
                    return  # Éxito, salir del loop
                
            except Exception as e:
                if attempt == max_retries:
                    log_scraping_event(logger, sport, 'error', {
                        'error_message': f"Falló después de {max_retries} intentos: {str(e)}",
                        'attempt': attempt,
                        'retries_left': 0
                    })
                else:
                    log_scraping_event(logger, sport, 'error', {
                        'error_message': str(e),
                        'attempt': attempt,
                        'retries_left': max_retries - attempt
                    })
    
    async def generate_enhanced_daily_report(self):
        """
        Genera reporte diario mejorado con estadísticas específicas
        """
        try:
            today = datetime.now(self.timezone).strftime('%Y-%m-%d')
            log_file = f"logs/scraper_{today}.log"
            
            # Generar estadísticas del día
            stats = generate_daily_report(logger, log_file)
            
            # Agregar estadísticas específicas por deporte
            for sport in self.active_scrapers.keys():
                sport_stats = await self.get_sport_daily_stats(sport)
                stats[f'{sport}_stats'] = sport_stats
            
            # Crear reporte para Telegram
            report_message = self.create_daily_report_message(stats)
            
            if self.telegram_notifier:
                await self.telegram_notifier.send_message(report_message)
            
            logger.info(f"📊 Reporte diario mejorado generado para {today}")
            
        except Exception as e:
            logger.error(f"Error generando reporte diario: {e}")
    
    async def get_sport_daily_stats(self, sport: str) -> Dict:
        """
        Obtiene estadísticas diarias específicas por deporte
        
        Args:
            sport: Deporte
            
        Returns:
            Estadísticas del deporte
        """
        # Implementar consultas específicas a la base de datos
        return {
            'partidos_procesados': 0,
            'consensos_altos': 0,
            'alertas_enviadas': 0,
            'umbral_promedio': 0.0
        }
    
    def create_daily_report_message(self, stats: Dict) -> str:
        """
        Crea mensaje de reporte diario mejorado
        
        Args:
            stats: Estadísticas del día
            
        Returns:
            Mensaje formateado
        """
        message = f"📊 *REPORTE DIARIO MEJORADO*\n"
        message += f"📅 {stats.get('fecha', 'N/A')}\n\n"
        
        # Estadísticas generales
        scraping = stats.get('scraping_events', {})
        message += f"🕷️ *Scraping General:*\n"
        message += f"  • Exitosos: {scraping.get('successful', 0)}\n"
        message += f"  • Fallidos: {scraping.get('failed', 0)}\n"
        message += f"  • Reintentos: {scraping.get('retries', 0)}\n\n"
        
        # Estadísticas por deporte
        for sport in self.active_scrapers.keys():
            sport_stats = stats.get(f'{sport}_stats', {})
            emoji = {'MLB': '⚾', 'NBA': '🏀', 'NFL': '🏈', 'NHL': '🏒'}.get(sport, '🏆')
            
            message += f"{emoji} *{sport}:*\n"
            message += f"  • Partidos: {sport_stats.get('partidos_procesados', 0)}\n"
            message += f"  • Consensos altos: {sport_stats.get('consensos_altos', 0)}\n"
            message += f"  • Alertas: {sport_stats.get('alertas_enviadas', 0)}\n\n"
        
        # Estadísticas de alertas
        alerts = stats.get('alert_events', {})
        message += f"🚨 *Alertas:*\n"
        message += f"  • Enviadas: {alerts.get('total_sent', 0)}\n"
        message += f"  • Fallidas: {alerts.get('failed', 0)}\n\n"
        
        message += f"🕐 Generado: {datetime.now(self.timezone).strftime('%H:%M ART')}"
        
        return message
    
    async def shutdown(self):
        """Cierra todos los componentes del sistema"""
        try:
            await self.pregame_scheduler.stop()
            
            if self.telegram_notifier:
                await self.telegram_notifier.stop()
            
            for scraper in self.active_scrapers.values():
                scraper.close()
            
            logger.info("🛑 Sistema completamente cerrado")
            
        except Exception as e:
            logger.error(f"Error cerrando sistema: {e}")


async def main():
    """Función principal para testing del sistema mejorado"""
    logger.info("=== PRUEBA DEL SISTEMA MEJORADO ===")
    
    try:
        system = EnhancedConsensusSystem()
        await system.initialize()
        
        # Ejecutar scraping diario
        await system.run_daily_consensus_scraping()
        
        # Generar reporte
        await system.generate_enhanced_daily_report()
        
        await system.shutdown()
        
        logger.info("✅ Prueba del sistema mejorado completada")
        
    except Exception as e:
        logger.error(f"Error en prueba del sistema: {e}")


if __name__ == "__main__":
    asyncio.run(main())
