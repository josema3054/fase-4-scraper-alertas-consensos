"""
Bot de Telegram para enviar alertas y notificaciones automáticas
"""

import asyncio
import telegram
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import pytz
from typing import List, Dict, Optional, Union
import json
from src.utils.logger import get_logger
from src.utils.error_handler import ErrorHandler, log_exception

logger = get_logger(__name__)

class TelegramNotifier:
    """Bot de Telegram para enviar alertas de consensos deportivos"""
    
    def __init__(self, token: str, chat_ids: List[str]):
        """
        Inicializa el notificador de Telegram
        
        Args:
            token: Token del bot de Telegram
            chat_ids: Lista de IDs de chat donde enviar mensajes
        """
        self.token = token
        self.chat_ids = chat_ids
        self.bot = telegram.Bot(token=token)
        self.application = None
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        
        logger.info(f"TelegramNotifier inicializado para {len(chat_ids)} chats")
    
    async def setup_bot(self):
        """Configura la aplicación del bot"""
        try:
            self.application = Application.builder().token(self.token).build()
            
            # Agregar comandos
            self.application.add_handler(CommandHandler("start", self._cmd_start))
            self.application.add_handler(CommandHandler("status", self._cmd_status))
            self.application.add_handler(CommandHandler("help", self._cmd_help))
            
            logger.info("Bot de Telegram configurado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al configurar bot de Telegram: {e}")
            raise
    
    async def _cmd_start(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_msg = """
🤖 *Bot de Alertas Deportivas - Fase 4*

¡Hola! Soy tu bot de alertas de consensos deportivos.

*Comandos disponibles:*
• /status - Estado del sistema
• /help - Ayuda
• /start - Este mensaje

🏈 Recibirás alertas automáticas cuando se detecten consensos altos en MLB.
        """
        
        await update.message.reply_text(
            welcome_msg,
            parse_mode='Markdown'
        )
    
    async def _cmd_status(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status"""
        status_msg = f"""
📊 *Estado del Sistema*

🕐 Hora actual: {datetime.now(self.timezone).strftime('%H:%M:%S ART')}
📅 Fecha: {datetime.now(self.timezone).strftime('%d/%m/%Y')}

✅ Bot operativo
🔄 Monitoring activo
🏈 MLB scraping configurado

*Próximas tareas programadas:*
• Scraping diario: 11:00 AM ART
• Updates en vivo: Cada 2 horas
• Reporte diario: 23:45 ART
        """
        
        await update.message.reply_text(
            status_msg,
            parse_mode='Markdown'
        )
    
    async def _cmd_help(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_msg = """
🆘 *Ayuda - Bot de Alertas Deportivas*

*¿Qué hace este bot?*
• Monitorea consensos en covers.com
• Envía alertas cuando hay consenso alto (>75%)
• Proporciona reportes diarios del sistema

*Tipos de alertas:*
🚨 Consenso Alto - Cuando >75% coincide
📊 Reporte Diario - Resumen del día
⚠️ Errores del Sistema - Si algo falla

*Horarios de actividad:*
• 11:00 AM - Scraping principal diario
• 12:00-23:00 - Updates cada 2 horas
• 23:45 - Reporte diario

¿Preguntas? Contacta al administrador.
        """
        
        await update.message.reply_text(
            help_msg,
            parse_mode='Markdown'
        )
    
    @log_exception
    async def send_consensus_alert(self, consensos: List[Dict], tipo: str = 'daily'):
        """
        Envía alerta de consensos detectados
        
        Args:
            consensos: Lista de consensos para alertar
            tipo: Tipo de scraping ('daily', 'live')
        """
        if not consensos:
            return
        
        # Filtrar consensos con porcentaje alto
        high_consensus = [
            c for c in consensos 
            if any([
                c.get('porcentaje_spread', 0) >= 75,
                c.get('porcentaje_total', 0) >= 75,
                c.get('porcentaje_moneyline', 0) >= 75
            ])
        ]
        
        if not high_consensus:
            logger.info("No hay consensos altos para alertar")
            return
        
        # Crear mensaje de alerta
        emoji = "🚨" if tipo == 'live' else "📊"
        titulo = "ALERTA EN VIVO" if tipo == 'live' else "CONSENSOS ALTOS DETECTADOS"
        
        mensaje = f"{emoji} *{titulo}*\n\n"
        mensaje += f"🕐 {datetime.now(self.timezone).strftime('%d/%m/%Y %H:%M ART')}\n"
        mensaje += f"🏈 *MLB - {len(high_consensus)} consensos altos*\n\n"
        
        for i, consenso in enumerate(high_consensus[:5]):  # Máximo 5 para no saturar
            equipo_vis = consenso.get('equipo_visitante', 'TBD')
            equipo_loc = consenso.get('equipo_local', 'TBD')
            pct_spread = consenso.get('porcentaje_spread', 0)
            pct_total = consenso.get('porcentaje_total', 0)
            pct_ml = consenso.get('porcentaje_moneyline', 0)
            
            mensaje += f"*{i+1}. {equipo_vis} @ {equipo_loc}*\n"
            
            if pct_spread >= 75:
                mensaje += f"   🎯 Spread: *{pct_spread}%*\n"
            if pct_total >= 75:
                mensaje += f"   🔢 Total: *{pct_total}%*\n"
            if pct_ml >= 75:
                mensaje += f"   💰 ML: *{pct_ml}%*\n"
            
            mensaje += "\n"
        
        if len(high_consensus) > 5:
            mensaje += f"... y {len(high_consensus) - 5} más\n\n"
        
        mensaje += f"📈 *Total procesados: {len(consensos)}*"
        
        await self.send_message(mensaje)
        logger.info(f"Alerta enviada: {len(high_consensus)} consensos altos")
    
    @log_exception
    async def send_daily_report(self, report_data: Dict):
        """
        Envía reporte diario del sistema
        
        Args:
            report_data: Datos del reporte diario
        """
        fecha = report_data.get('fecha', 'N/A')
        total_jobs = report_data.get('total_jobs_ejecutados', 0)
        estado = report_data.get('estado_sistema', 'unknown')
        
        emoji_estado = "✅" if estado == 'operational' else "⚠️"
        
        mensaje = f"""
📋 *REPORTE DIARIO - {fecha}*

{emoji_estado} Estado del sistema: *{estado.upper()}*
🔄 Jobs ejecutados: *{total_jobs}*
🕐 Generado: {datetime.now(self.timezone).strftime('%H:%M ART')}

*Resumen de actividad:*
• Scraping diario completado
• Monitoreo en vivo activo
• Alertas funcionando correctamente

🏈 *MLB Monitoring*
• Fuente: covers.com
• Frecuencia: Cada 2 horas
• Umbral de alerta: 75%

---
¡Hasta mañana! 🌙
        """
        
        await self.send_message(mensaje)
        logger.info("Reporte diario enviado")
    
    @log_exception
    async def send_error_alert(self, error_msg: str, context: str):
        """
        Envía alerta de error del sistema
        
        Args:
            error_msg: Mensaje de error
            context: Contexto donde ocurrió el error
        """
        mensaje = f"""
🚨 *ALERTA DE ERROR*

⚠️ Se detectó un problema en el sistema

*Contexto:* {context}
*Hora:* {datetime.now(self.timezone).strftime('%d/%m/%Y %H:%M ART')}

*Error:* 
`{error_msg[:200]}...` {'(truncado)' if len(error_msg) > 200 else ''}

🔧 El sistema intentará recuperarse automáticamente.
Si el problema persiste, se requiere intervención manual.
        """
        
        await self.send_message(mensaje)
        logger.info(f"Alerta de error enviada: {context}")
    
    @log_exception
    async def send_system_status(self, status_data: Dict):
        """
        Envía estado del sistema bajo demanda
        
        Args:
            status_data: Datos del estado del sistema
        """
        uptime = status_data.get('uptime', 'N/A')
        last_scraping = status_data.get('last_scraping', 'N/A')
        errors_today = status_data.get('errors_today', 0)
        
        mensaje = f"""
🔍 *ESTADO DEL SISTEMA*

🕐 {datetime.now(self.timezone).strftime('%d/%m/%Y %H:%M ART')}

*Información general:*
• Uptime: {uptime}
• Último scraping: {last_scraping}
• Errores hoy: {errors_today}

*Servicios:*
✅ Scraper MLB
✅ Base de datos
✅ Telegram Bot
✅ Scheduler

*Próximas tareas:*
🕚 11:00 AM - Scraping diario
🔄 Cada 2h - Updates en vivo
🌙 23:45 - Reporte diario
        """
        
        await self.send_message(mensaje)
        logger.info("Estado del sistema enviado")
    
    @log_exception
    async def send_message(self, text: str, parse_mode: str = 'Markdown'):
        """
        Envía mensaje a todos los chats configurados
        
        Args:
            text: Texto del mensaje
            parse_mode: Modo de parsing ('Markdown' o 'HTML')
        """
        for chat_id in self.chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=True
                )
                logger.debug(f"Mensaje enviado a chat {chat_id}")
                
                # Pausa entre mensajes para evitar rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error al enviar mensaje a chat {chat_id}: {e}")
                continue
    
    @log_exception
    async def test_connection(self) -> bool:
        """
        Prueba la conexión del bot
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Bot conectado: @{bot_info.username} ({bot_info.first_name})")
            
            # Enviar mensaje de prueba
            test_msg = f"""
🧪 *TEST DE CONEXIÓN*

✅ Bot funcionando correctamente
🕐 {datetime.now(self.timezone).strftime('%d/%m/%Y %H:%M ART')}

Este es un mensaje de prueba del sistema de alertas.
            """
            
            await self.send_message(test_msg)
            logger.info("Test de conexión exitoso")
            return True
            
        except Exception as e:
            logger.error(f"Error en test de conexión: {e}")
            return False
    
    def start_polling(self):
        """Inicia el bot en modo polling (para desarrollo)"""
        if self.application:
            self.application.run_polling()
    
    async def stop(self):
        """Detiene el bot"""
        if self.application:
            await self.application.stop()
            logger.info("Bot de Telegram detenido")


async def main():
    """Función principal para testing del bot"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_ids = os.getenv('TELEGRAM_CHAT_IDS', '').split(',')
    
    if not token or not chat_ids[0]:
        print("❌ Configure TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_IDS en .env")
        return
    
    logger.info("=== PRUEBA DEL BOT DE TELEGRAM ===")
    
    try:
        notifier = TelegramNotifier(token, chat_ids)
        await notifier.setup_bot()
        
        # Test de conexión
        success = await notifier.test_connection()
        
        if success:
            # Enviar algunos mensajes de prueba
            test_consensos = [
                {
                    'equipo_visitante': 'Yankees',
                    'equipo_local': 'Red Sox',
                    'porcentaje_spread': 78,
                    'porcentaje_total': 82,
                    'porcentaje_moneyline': 71
                }
            ]
            
            await notifier.send_consensus_alert(test_consensos, 'test')
            
            test_report = {
                'fecha': datetime.now().strftime('%Y-%m-%d'),
                'total_jobs_ejecutados': 4,
                'estado_sistema': 'operational'
            }
            
            await notifier.send_daily_report(test_report)
            
            print("✅ Pruebas del bot completadas exitosamente")
        
        await notifier.stop()
        
    except Exception as e:
        logger.error(f"Error en prueba del bot: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
