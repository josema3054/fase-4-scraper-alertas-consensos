#!/usr/bin/env python3
"""
Sistema Automatizado de Scraping y Alertas de Consensos Deportivos
Archivo principal - Fase 4

Este módulo coordina todo el sistema de scraping, alertas y monitoreo.
"""

import sys
import os
import argparse
import asyncio
from datetime import datetime

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logger
from utils.error_handler import ErrorHandler
from config.settings import Settings
from scraper.mlb_scraper import MLBScraper
from notifications.telegram_bot import TelegramBot
from database.supabase_client import SupabaseClient

# Configurar logger principal
logger = setup_logger('main')

class ConsensusAlertSystem:
    """Sistema principal de alertas de consenso deportivo"""
    
    def __init__(self):
        """Inicializar el sistema"""
        self.settings = Settings()
        self.db = SupabaseClient()
        self.telegram = TelegramBot()
        self.mlb_scraper = MLBScraper()
        self.error_handler = ErrorHandler()
        
    async def morning_scraping(self):
        """Scraping matutino para detectar partidos del día"""
        logger.info("🌅 Iniciando scraping matutino...")
        
        try:
            # Scraping de partidos MLB del día
            matches = await self.mlb_scraper.get_daily_matches()
            
            if matches:
                logger.info(f"📊 Encontrados {len(matches)} partidos MLB para hoy")
                
                # Guardar partidos en base de datos
                await self.db.save_daily_matches(matches)
                
                # Programar scrapings pre-partido
                await self.schedule_pre_game_scrapings(matches)
                
                # Enviar notificación de inicio
                message = f"🌅 Scraping matutino completado\\n📊 {len(matches)} partidos MLB detectados"
                await self.telegram.send_message(message)
                
            else:
                logger.warning("⚠️ No se encontraron partidos para hoy")
                await self.telegram.send_message("⚠️ No se encontraron partidos MLB para hoy")
                
        except Exception as e:
            error_msg = f"❌ Error en scraping matutino: {str(e)}"
            logger.error(error_msg)
            await self.error_handler.handle_error(e, "morning_scraping")
            await self.telegram.send_error_alert(error_msg)
    
    async def pre_game_scraping(self, match_info):
        """Scraping 15 minutos antes del partido"""
        logger.info(f"⚡ Scraping pre-partido: {match_info['teams']}")
        
        try:
            # Obtener consenso actualizado
            consensus_data = await self.mlb_scraper.get_match_consensus(match_info)
            
            if consensus_data:
                # Evaluar si enviar alerta
                should_alert = self.evaluate_alert_criteria(consensus_data)
                
                if should_alert:
                    await self.send_consensus_alert(consensus_data)
                
                # Guardar datos en base de datos
                await self.db.save_consensus_data(consensus_data)
                
            else:
                logger.warning(f"⚠️ No se pudo obtener consenso para {match_info['teams']}")
                
        except Exception as e:
            error_msg = f"❌ Error en scraping pre-partido {match_info['teams']}: {str(e)}"
            logger.error(error_msg)
            await self.error_handler.handle_error(e, "pre_game_scraping")
    
    def evaluate_alert_criteria(self, consensus_data):
        """Evaluar si el consenso cumple criterios para alerta"""
        consensus_percentage = consensus_data.get('consensus_percentage', 0)
        total_experts = consensus_data.get('total_experts', 0)
        
        # Verificar umbrales
        threshold = self.settings.MLB_CONSENSUS_THRESHOLD
        min_experts = self.settings.MIN_EXPERTS_VOTING
        
        meets_threshold = consensus_percentage >= threshold
        enough_experts = total_experts >= min_experts
        
        return meets_threshold and enough_experts
    
    async def send_consensus_alert(self, consensus_data):
        """Enviar alerta de consenso alto"""
        try:
            message = self.format_consensus_alert(consensus_data)
            await self.telegram.send_alert(message)
            
            # Registrar alerta enviada
            await self.db.log_alert_sent(consensus_data)
            
            logger.info(f"📱 Alerta enviada: {consensus_data['teams']}")
            
        except Exception as e:
            logger.error(f"❌ Error enviando alerta: {str(e)}")
    
    def format_consensus_alert(self, data):
        """Formatear mensaje de alerta de consenso"""
        return f"""🚨 Alerta Consenso Deportivo 🚨
Deporte: MLB
Evento: {data['teams']}
Consenso: {data['consensus_type']} ({data['consensus_percentage']}%)
Total Expertos: {data['total_experts']}
Hora del partido: {data['game_time']}
"""
    
    async def daily_report(self):
        """Generar y enviar reporte diario del sistema"""
        logger.info("🌙 Generando reporte diario...")
        
        try:
            stats = await self.db.get_daily_stats()
            
            message = f"""✅ Reporte diario Scraper Consensos ✅
Fecha: {datetime.now().strftime('%Y-%m-%d')}
Deportes monitoreados: MLB
Total Alertas enviadas: {stats['alerts_sent']}
Errores encontrados: {stats['errors_count']}
Estado: {'✅ Funcionando correctamente' if stats['errors_count'] == 0 else '⚠️ Revisar errores'}
"""
            
            await self.telegram.send_message(message)
            logger.info("📊 Reporte diario enviado")
            
        except Exception as e:
            error_msg = f"❌ Error generando reporte diario: {str(e)}"
            logger.error(error_msg)
            await self.telegram.send_error_alert(error_msg)
    
    async def schedule_pre_game_scrapings(self, matches):
        """Programar scrapings automáticos 15 min antes de cada partido"""
        # Esta función será implementada en scheduler.py
        logger.info(f"⏰ Programando {len(matches)} scrapings pre-partido")
        pass
    
    async def health_check(self):
        """Verificar salud del sistema"""
        try:
            # Verificar conexión a base de datos
            db_ok = await self.db.health_check()
            
            # Verificar bot de Telegram
            telegram_ok = await self.telegram.health_check()
            
            # Verificar scraper
            scraper_ok = await self.mlb_scraper.health_check()
            
            system_healthy = db_ok and telegram_ok and scraper_ok
            
            if not system_healthy:
                await self.telegram.send_error_alert("⚠️ Sistema no está completamente saludable")
            
            return system_healthy
            
        except Exception as e:
            logger.error(f"❌ Error en health check: {str(e)}")
            return False

async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Sistema de Alertas de Consenso Deportivo')
    parser.add_argument('--mode', choices=['morning', 'test', 'health'], 
                       default='morning', help='Modo de ejecución')
    parser.add_argument('--debug', action='store_true', help='Activar modo debug')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel('DEBUG')
        logger.debug("🔧 Modo debug activado")
    
    # Inicializar sistema
    system = ConsensusAlertSystem()
    
    try:
        if args.mode == 'morning':
            await system.morning_scraping()
        elif args.mode == 'test':
            logger.info("🧪 Ejecutando tests del sistema...")
            await system.health_check()
        elif args.mode == 'health':
            healthy = await system.health_check()
            print(f"Sistema saludable: {healthy}")
            
    except KeyboardInterrupt:
        logger.info("👋 Sistema detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
