"""
Servicio de Background para Scrapers Automáticos
Ejecuta scrapers programados y envía alertas
"""

import asyncio
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from pathlib import Path

from src.database.data_manager import data_manager, ScraperProgramado
from src.scraper.mlb_selenium_scraper import MLBSeleniumScraper
from src.notifications.telegram_bot import TelegramNotifier
from src.utils.logger import setup_logger

class ScrapingBackgroundService:
    """Servicio que maneja la ejecución automática de scrapers"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.is_running = False
        self.scraper = MLBSeleniumScraper()
        self.telegram_bot = None  # Se inicializa si está configurado
        self.stats = {
            'scrapers_ejecutados_hoy': 0,
            'ultima_ejecucion': None,
            'errores_hoy': 0,
            'servicio_iniciado_en': datetime.now().isoformat()
        }
        
        # Configurar Telegram si está disponible
        self._init_telegram()
        
        self.logger.info("🚀 ScrapingBackgroundService inicializado")
    
    def _init_telegram(self):
        """Inicializa bot de Telegram si está configurado"""
        try:
            # Inicializar con configuración básica por ahora
            self.telegram_bot = TelegramNotifier(
                token="dummy_token",  # Reemplazar con token real
                chat_ids=[]  # Lista de chat IDs
            )
            self.logger.info("📱 Bot de Telegram inicializado (modo desarrollo)")
        except Exception as e:
            self.logger.error(f"❌ Error inicializando Telegram: {e}")
            self.telegram_bot = None
    
    def start_service(self):
        """Inicia el servicio en background"""
        if self.is_running:
            self.logger.warning("⚠️ El servicio ya está ejecutándose")
            return
        
        self.is_running = True
        self.logger.info("🟢 Iniciando servicio de scrapers automáticos...")
        
        # Programar verificaciones cada minuto
        schedule.every(1).minutes.do(self._verificar_scrapers_pendientes)
        
        # Programar limpieza diaria a las 2:00 AM
        schedule.every().day.at("02:00").do(self._limpieza_diaria)
        
        # Programar reporte diario a las 9:00 AM
        schedule.every().day.at("09:00").do(self._enviar_reporte_diario)
        
        # Ejecutar en thread separado para no bloquear
        service_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        service_thread.start()
        
        self.logger.info("✅ Servicio de background iniciado correctamente")
        
        # Enviar notificación de inicio
        self._enviar_notificacion("🚀 Sistema de Scrapers Automáticos iniciado", 
                                 "El servicio de background está activo y monitoreando scrapers programados.")
    
    def stop_service(self):
        """Detiene el servicio"""
        self.is_running = False
        schedule.clear()
        self.logger.info("🔴 Servicio de scrapers automáticos detenido")
        
        self._enviar_notificacion("🛑 Servicio Detenido", 
                                 "El servicio de scrapers automáticos ha sido detenido.")
    
    def _run_scheduler(self):
        """Ejecuta el scheduler en un loop continuo"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Verificar cada 30 segundos
            except Exception as e:
                self.logger.error(f"❌ Error en scheduler: {e}")
                time.sleep(60)  # Esperar más tiempo si hay error
    
    def _verificar_scrapers_pendientes(self):
        """Verifica si hay scrapers que deben ejecutarse"""
        try:
            scrapers_programados = data_manager.obtener_scrapers_programados(solo_activos=True)
            ahora = datetime.now()
            
            for scraper in scrapers_programados:
                if self._debe_ejecutar_scraper(scraper, ahora):
                    self.logger.info(f"🎯 Ejecutando scraper: {scraper.partido_id}")
                    self._ejecutar_scraper_automatico(scraper)
                    
        except Exception as e:
            self.logger.error(f"❌ Error verificando scrapers: {e}")
    
    def _debe_ejecutar_scraper(self, scraper: ScraperProgramado, ahora: datetime) -> bool:
        """Determina si un scraper debe ejecutarse ahora"""
        try:
            # Parsear fecha y hora del partido
            fecha_str = scraper.fecha_partido  # "2025-01-21"
            hora_str = scraper.hora_partido    # "7:10 pm ET"
            
            if not fecha_str or not hora_str:
                return False
            
            # Convertir hora del partido a datetime
            # Simplificado: asumir que es para hoy y convertir PM/AM
            from datetime import datetime
            import re
            
            hora_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)', hora_str, re.IGNORECASE)
            if not hora_match:
                return False
            
            hora = int(hora_match.group(1))
            minuto = int(hora_match.group(2))
            periodo = hora_match.group(3).lower()
            
            if periodo == 'pm' and hora != 12:
                hora += 12
            elif periodo == 'am' and hora == 12:
                hora = 0
            
            # Crear datetime del partido
            try:
                fecha_partido = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                datetime_partido = datetime.combine(fecha_partido, datetime.min.time().replace(hour=hora, minute=minuto))
            except:
                # Si no se puede parsear la fecha, usar hoy
                datetime_partido = datetime.now().replace(hour=hora, minute=minuto, second=0, microsecond=0)
            
            # Calcular cuándo ejecutar (15 minutos antes)
            momento_ejecucion = datetime_partido - timedelta(minutes=15)
            
            # Verificar si es el momento (con ventana de 2 minutos)
            diferencia = abs((ahora - momento_ejecucion).total_seconds())
            
            return diferencia <= 120  # Dentro de 2 minutos
            
        except Exception as e:
            self.logger.error(f"❌ Error evaluando tiempo de scraper {scraper.id}: {e}")
            return False
    
    def _ejecutar_scraper_automatico(self, scraper: ScraperProgramado):
        """Ejecuta un scraper automático específico"""
        try:
            self.logger.info(f"🤖 Ejecutando scraper automático: {scraper.visitante} @ {scraper.local}")
            
            # Marcar como en proceso
            data_manager.actualizar_estado_scraper(scraper.id, "ejecutando")
            
            # Ejecutar scraper
            inicio = time.time()
            resultados = self.scraper.scrape_mlb_consensus()
            duracion = time.time() - inicio
            
            if resultados:
                # Buscar el partido específico en los resultados
                partido_encontrado = None
                for resultado in resultados:
                    if (resultado.get('visitante', '').lower() == scraper.visitante.lower() and
                        resultado.get('local', '').lower() == scraper.local.lower()):
                        partido_encontrado = resultado
                        break
                
                if partido_encontrado:
                    # Verificar si hubo cambios significativos
                    cambios = self._detectar_cambios_consenso(scraper, partido_encontrado)
                    
                    # Guardar resultado
                    resultado_completo = {
                        'datos': partido_encontrado,
                        'duracion': duracion,
                        'timestamp': datetime.now().isoformat(),
                        'cambios_detectados': cambios
                    }
                    
                    data_manager.actualizar_estado_scraper(scraper.id, "ejecutado", resultado_completo)
                    
                    # Enviar alerta si hay cambios significativos
                    if cambios:
                        self._enviar_alerta_cambios(scraper, partido_encontrado, cambios)
                    
                    self.stats['scrapers_ejecutados_hoy'] += 1
                    self.stats['ultima_ejecucion'] = datetime.now().isoformat()
                    
                    self.logger.info(f"✅ Scraper ejecutado exitosamente: {scraper.partido_id}")
                else:
                    # No se encontró el partido específico
                    data_manager.actualizar_estado_scraper(scraper.id, "error", 
                                                         {"error": "Partido no encontrado en resultados"})
                    self.stats['errores_hoy'] += 1
                    self.logger.warning(f"⚠️ Partido no encontrado: {scraper.partido_id}")
            else:
                # Error en scraping
                data_manager.actualizar_estado_scraper(scraper.id, "error", 
                                                     {"error": "No se obtuvieron resultados"})
                self.stats['errores_hoy'] += 1
                self.logger.error(f"❌ Error en scraping para: {scraper.partido_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando scraper {scraper.id}: {e}")
            data_manager.actualizar_estado_scraper(scraper.id, "error", {"error": str(e)})
            self.stats['errores_hoy'] += 1
    
    def _detectar_cambios_consenso(self, scraper: ScraperProgramado, nuevos_datos: Dict) -> List[Dict]:
        """Detecta cambios significativos en el consenso"""
        cambios = []
        
        try:
            # Comparar porcentajes (extraer números de strings como "65%")
            consenso_anterior = scraper.consenso_actual
            over_actual = float(nuevos_datos.get('over_percentage', '0').replace('%', ''))
            under_actual = float(nuevos_datos.get('under_percentage', '0').replace('%', ''))
            
            # Determinar dirección actual
            direccion_actual = "OVER" if over_actual > under_actual else "UNDER"
            porcentaje_actual = max(over_actual, under_actual)
            
            # Extraer porcentaje anterior (simple)
            import re
            match = re.search(r'(\d+)%', consenso_anterior)
            porcentaje_anterior = float(match.group(1)) if match else 50
            
            # Detectar cambio significativo (>5%)
            diferencia = abs(porcentaje_actual - porcentaje_anterior)
            if diferencia >= 5:
                cambios.append({
                    'tipo': 'cambio_porcentaje',
                    'anterior': f"{porcentaje_anterior}%",
                    'actual': f"{porcentaje_actual}%",
                    'diferencia': f"+{diferencia}%" if porcentaje_actual > porcentaje_anterior else f"-{diferencia}%"
                })
            
            # Detectar cambio de dirección
            if "OVER" in consenso_anterior and direccion_actual == "UNDER":
                cambios.append({
                    'tipo': 'cambio_direccion',
                    'anterior': 'OVER',
                    'actual': 'UNDER'
                })
            elif "UNDER" in consenso_anterior and direccion_actual == "OVER":
                cambios.append({
                    'tipo': 'cambio_direccion', 
                    'anterior': 'UNDER',
                    'actual': 'OVER'
                })
            
        except Exception as e:
            self.logger.error(f"Error detectando cambios: {e}")
        
        return cambios
    
    def _enviar_alerta_cambios(self, scraper: ScraperProgramado, datos: Dict, cambios: List[Dict]):
        """Envía alerta por cambios significativos"""
        mensaje = f"🚨 **CAMBIO DETECTADO** 🚨\n\n"
        mensaje += f"🏟️ **Partido:** {scraper.visitante} @ {scraper.local}\n"
        mensaje += f"⏰ **Hora:** {scraper.hora_partido}\n\n"
        
        for cambio in cambios:
            if cambio['tipo'] == 'cambio_porcentaje':
                mensaje += f"📊 **Consenso:** {cambio['anterior']} → {cambio['actual']} ({cambio['diferencia']})\n"
            elif cambio['tipo'] == 'cambio_direccion':
                mensaje += f"🔄 **Dirección:** {cambio['anterior']} → {cambio['actual']}\n"
        
        mensaje += f"\n💡 **Estado Actual:**\n"
        mensaje += f"  OVER: {datos.get('over_percentage', 'N/A')}\n"
        mensaje += f"  UNDER: {datos.get('under_percentage', 'N/A')}\n"
        mensaje += f"  Expertos: {datos.get('num_experts', 'N/A')}\n"
        
        self._enviar_notificacion("🚨 Cambio de Consenso Detectado", mensaje)
    
    def _enviar_notificacion(self, titulo: str, mensaje: str):
        """Envía notificación por Telegram (si está configurado)"""
        if self.telegram_bot and self.telegram_bot.chat_ids:
            try:
                # Para el desarrollo, solo hacer log
                self.logger.info(f"📱 [TELEGRAM] {titulo}: {mensaje}")
                # Aquí iría: await self.telegram_bot.send_alert_message(f"{titulo}\n\n{mensaje}")
            except Exception as e:
                self.logger.error(f"❌ Error enviando notificación Telegram: {e}")
        else:
            self.logger.info(f"📱 [LOG] {titulo}: {mensaje}")
    
    def _limpieza_diaria(self):
        """Limpieza diaria de datos antiguos"""
        try:
            self.logger.info("🧹 Ejecutando limpieza diaria...")
            data_manager.limpiar_datos_antiguos(dias=7)
            
            # Resetear estadísticas del día
            self.stats['scrapers_ejecutados_hoy'] = 0
            self.stats['errores_hoy'] = 0
            
            self.logger.info("✅ Limpieza diaria completada")
            
        except Exception as e:
            self.logger.error(f"❌ Error en limpieza diaria: {e}")
    
    def _enviar_reporte_diario(self):
        """Envía reporte diario de actividad"""
        try:
            stats = data_manager.obtener_estadisticas_hoy()
            
            reporte = f"📊 **REPORTE DIARIO** - {stats['fecha']}\n\n"
            reporte += f"🤖 **Scrapers Automáticos:**\n"
            reporte += f"  • Programados: {stats['scrapers_automaticos']['total_programados']}\n"
            reporte += f"  • Ejecutados: {stats['scrapers_automaticos']['ejecutados']}\n" 
            reporte += f"  • Pendientes: {stats['scrapers_automaticos']['pendientes']}\n\n"
            
            reporte += f"📊 **Sesiones de Scraping:**\n"
            reporte += f"  • Total: {stats['sesiones_scraping']['total']}\n"
            reporte += f"  • Promedio partidos: {stats['sesiones_scraping']['promedio_partidos']}\n"
            reporte += f"  • Duración promedio: {stats['sesiones_scraping']['duracion_promedio']}s\n\n"
            
            reporte += f"📈 **Servicio:**\n"
            reporte += f"  • Ejecutados hoy: {self.stats['scrapers_ejecutados_hoy']}\n"
            reporte += f"  • Errores: {self.stats['errores_hoy']}\n"
            reporte += f"  • Última ejecución: {self.stats['ultima_ejecucion'] or 'Ninguna'}\n"
            
            self._enviar_notificacion("📊 Reporte Diario", reporte)
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte diario: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del servicio"""
        return {
            'servicio_activo': self.is_running,
            'telegram_configurado': self.telegram_bot is not None,
            'estadisticas': self.stats,
            'scrapers_pendientes': len(data_manager.obtener_scrapers_programados(solo_activos=True))
        }

# Instancia global del servicio
background_service = ScrapingBackgroundService()
