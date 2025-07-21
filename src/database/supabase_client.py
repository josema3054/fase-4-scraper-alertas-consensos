"""
Cliente de Supabase para el sistema de alertas
"""

import asyncio
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

from src.utils.logger import get_logger
from src.utils.error_handler import retry_on_failure, log_exception
from config.settings import Settings

logger = get_logger('supabase_client')

# Definir nombres de tablas
DATABASE_TABLES = {
    "consensus_data": "consensus_data",
    "consensus_alerts": "consensus_alerts", 
    "matches": "matches",
    "system_logs": "system_logs"
}

class SupabaseClient:
    """Cliente para interactuar con Supabase"""
    
    def __init__(self):
        self.settings = Settings()
        self.supabase: Client = create_client(
            self.settings.SUPABASE_URL,
            self.settings.SUPABASE_KEY
        )
        logger.info("✅ Cliente Supabase inicializado")
    
    @retry_on_failure(max_retries=3)
    async def health_check(self) -> bool:
        """Verificar conexión con Supabase"""
        try:
            # Hacer una consulta simple para verificar conexión
            response = self.supabase.table(DATABASE_TABLES["system_logs"]).select("*").limit(1).execute()
            logger.debug("✅ Health check Supabase exitoso")
            return True
        except Exception as e:
            logger.error(f"❌ Health check Supabase falló: {str(e)}")
            return False
    
    @log_exception
    async def save_daily_matches(self, matches: List[Dict[str, Any]]) -> bool:
        """
        Guardar partidos del día en la base de datos
        
        Args:
            matches: Lista de partidos con información completa
        
        Returns:
            True si se guardaron exitosamente
        """
        try:
            for match in matches:
                match_data = {
                    'date': match.get('date', date.today().isoformat()),
                    'sport': 'mlb',
                    'team_1': match.get('team_1'),
                    'team_2': match.get('team_2'),
                    'game_time': match.get('game_time'),
                    'initial_consensus': match.get('initial_consensus'),
                    'created_at': datetime.now().isoformat(),
                    'status': 'scheduled'
                }
                
                response = self.supabase.table(DATABASE_TABLES["matches"]).insert(match_data).execute()
                
            logger.info(f"💾 Guardados {len(matches)} partidos en base de datos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando partidos: {str(e)}")
            return False
    
    @log_exception
    async def save_consensus_data(self, consensus_data: Dict[str, Any]) -> bool:
        """
        Guardar datos de consenso en la base de datos
        
        Args:
            consensus_data: Datos del consenso obtenido
        
        Returns:
            True si se guardó exitosamente
        """
        try:
            data = {
                'date': consensus_data.get('date', date.today().isoformat()),
                'sport': 'mlb',
                'teams': consensus_data.get('teams'),
                'consensus_type': consensus_data.get('consensus_type'),
                'consensus_percentage': consensus_data.get('consensus_percentage'),
                'total_experts': consensus_data.get('total_experts'),
                'game_time': consensus_data.get('game_time'),
                'alert_sent': consensus_data.get('alert_sent', False),
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table(DATABASE_TABLES["consensus_data"]).insert(data).execute()
            
            logger.info(f"💾 Guardado consenso: {consensus_data.get('teams')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando consenso: {str(e)}")
            return False
    
    @log_exception
    async def log_alert_sent(self, consensus_data: Dict[str, Any]) -> bool:
        """
        Registrar que se envió una alerta
        
        Args:
            consensus_data: Datos del consenso que generó la alerta
        
        Returns:
            True si se registró exitosamente
        """
        try:
            alert_data = {
                'date': date.today().isoformat(),
                'sport': 'mlb',
                'teams': consensus_data.get('teams'),
                'consensus_type': consensus_data.get('consensus_type'),
                'consensus_percentage': consensus_data.get('consensus_percentage'),
                'total_experts': consensus_data.get('total_experts'),
                'alert_time': datetime.now().isoformat(),
                'alert_type': 'consensus_high'
            }
            
            response = self.supabase.table(DATABASE_TABLES["consensus_alerts"]).insert(alert_data).execute()
            
            logger.info(f"📱 Registrada alerta: {consensus_data.get('teams')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registrando alerta: {str(e)}")
            return False
    
    @log_exception
    async def get_daily_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del día actual
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            today = date.today().isoformat()
            
            # Contar alertas enviadas hoy
            alerts_response = self.supabase.table(DATABASE_TABLES["consensus_alerts"]).select("*").eq('date', today).execute()
            alerts_count = len(alerts_response.data)
            
            # Contar errores del sistema hoy
            errors_response = self.supabase.table(DATABASE_TABLES["system_logs"]).select("*").eq('date', today).eq('level', 'ERROR').execute()
            errors_count = len(errors_response.data)
            
            # Contar partidos monitoreados hoy
            matches_response = self.supabase.table(DATABASE_TABLES["matches"]).select("*").eq('date', today).execute()
            matches_count = len(matches_response.data)
            
            stats = {
                'date': today,
                'alerts_sent': alerts_count,
                'errors_count': errors_count,
                'matches_monitored': matches_count,
                'system_healthy': errors_count == 0
            }
            
            logger.debug(f"📊 Estadísticas diarias: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
            return {
                'date': date.today().isoformat(),
                'alerts_sent': 0,
                'errors_count': 1,  # Este mismo error
                'matches_monitored': 0,
                'system_healthy': False
            }
    
    @log_exception
    async def log_system_event(self, level: str, message: str, context: Optional[str] = None) -> bool:
        """
        Registrar evento del sistema en logs
        
        Args:
            level: Nivel del log (INFO, WARNING, ERROR, CRITICAL)
            message: Mensaje del evento
            context: Contexto adicional
        
        Returns:
            True si se registró exitosamente
        """
        try:
            log_data = {
                'date': date.today().isoformat(),
                'timestamp': datetime.now().isoformat(),
                'level': level.upper(),
                'message': message,
                'context': context,
                'system': 'consensus_alerts'
            }
            
            response = self.supabase.table(DATABASE_TABLES["system_logs"]).insert(log_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registrando evento del sistema: {str(e)}")
            return False
    
    @log_exception
    async def get_alerts_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Obtener historial de alertas de los últimos días
        
        Args:
            days: Número de días hacia atrás
        
        Returns:
            Lista de alertas
        """
        try:
            from datetime import timedelta
            start_date = (date.today() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table(DATABASE_TABLES["consensus_alerts"]).select("*").gte('date', start_date).order('alert_time', desc=True).execute()
            
            logger.debug(f"📋 Obtenidas {len(response.data)} alertas de los últimos {days} días")
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial de alertas: {str(e)}")
            return []
    
    @log_exception
    async def get_system_health_status(self) -> Dict[str, Any]:
        """
        Obtener estado de salud del sistema
        
        Returns:
            Diccionario con estado de salud
        """
        try:
            today = date.today().isoformat()
            
            # Verificar si hubo scraping matutino hoy
            morning_scraping = self.supabase.table(DATABASE_TABLES["system_logs"]).select("*").eq('date', today).eq('message', 'Morning scraping completed').execute()
            
            # Contar errores críticos hoy
            critical_errors = self.supabase.table(DATABASE_TABLES["system_logs"]).select("*").eq('date', today).eq('level', 'CRITICAL').execute()
            
            # Última actividad del sistema
            last_activity = self.supabase.table(DATABASE_TABLES["system_logs"]).select("*").order('timestamp', desc=True).limit(1).execute()
            
            health_status = {
                'date': today,
                'morning_scraping_done': len(morning_scraping.data) > 0,
                'critical_errors_today': len(critical_errors.data),
                'last_activity': last_activity.data[0]['timestamp'] if last_activity.data else None,
                'system_operational': len(critical_errors.data) == 0 and len(morning_scraping.data) > 0
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de salud: {str(e)}")
            return {
                'date': today,
                'morning_scraping_done': False,
                'critical_errors_today': 1,
                'last_activity': None,
                'system_operational': False
            }
