"""
Sistema de scraping inteligente que programa automáticamente 
extracciones 15 minutos antes de cada partido
"""

import asyncio
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from src.utils.logger import get_logger
from src.utils.sports_config import get_sports_config
from src.scraper.mlb_scraper import MLBScraper

logger = get_logger(__name__)

class PregameScheduler:
    """Programador inteligente para scraping pre-partido"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        self.sports_config = get_sports_config()
        self.scheduled_jobs = {}
        self.game_schedules = {}
        
        logger.info("PregameScheduler inicializado")
    
    async def start(self):
        """Inicia el scheduler"""
        self.scheduler.start()
        logger.info("✅ PregameScheduler iniciado")
    
    async def stop(self):
        """Detiene el scheduler"""
        self.scheduler.shutdown()
        logger.info("🛑 PregameScheduler detenido")
    
    async def schedule_daily_pregame_scraping(self, sport: str = 'MLB'):
        """
        Programa scraping pregame para todos los partidos del día
        
        Args:
            sport: Deporte para programar
        """
        try:
            logger.info(f"📅 Programando scraping pregame para {sport}")
            
            # Obtener horarios de partidos del día
            games_today = await self.get_games_schedule(sport)
            
            if not games_today:
                logger.info(f"📅 No hay partidos programados para {sport} hoy")
                return
            
            # Programar scraping 15 minutos antes de cada partido
            scheduled_count = 0
            
            for game in games_today:
                success = await self.schedule_pregame_scraping(sport, game)
                if success:
                    scheduled_count += 1
            
            logger.info(f"✅ {scheduled_count} scrapings pregame programados para {sport}")
            
        except Exception as e:
            logger.error(f"Error programando scraping pregame: {e}")
    
    async def get_games_schedule(self, sport: str) -> List[Dict]:
        """
        Obtiene horarios de partidos desde covers.com
        
        Args:
            sport: Deporte a consultar
            
        Returns:
            Lista de partidos con horarios
        """
        try:
            if sport == 'MLB':
                scraper = MLBScraper()
                
                # Obtener página de horarios
                schedule_url = f"https://www.covers.com/sports/mlb/schedule"
                soup = await scraper.get_page_content(schedule_url)
                
                if not soup:
                    return []
                
                games = []
                
                # Buscar elementos de partidos con horarios
                game_elements = soup.find_all(['div', 'tr'], class_=['game', 'game-row', 'schedule-game'])
                
                for element in game_elements:
                    game_info = self.extract_game_time(element, sport)
                    if game_info:
                        games.append(game_info)
                
                scraper.close()
                return games
                
        except Exception as e:
            logger.error(f"Error obteniendo horarios de {sport}: {e}")
            return []
    
    def extract_game_time(self, element, sport: str) -> Optional[Dict]:
        """
        Extrae información de horario de un elemento HTML
        
        Args:
            element: Elemento HTML del partido
            sport: Deporte
            
        Returns:
            Información del partido o None
        """
        try:
            # Buscar equipos
            team_elements = element.find_all(['span', 'div'], class_=['team', 'teams', 'matchup'])
            if not team_elements:
                return None
            
            teams_text = team_elements[0].get_text(strip=True)
            
            # Buscar hora del partido
            time_elements = element.find_all(['span', 'div'], class_=['time', 'game-time', 'start-time'])
            if not time_elements:
                return None
            
            time_text = time_elements[0].get_text(strip=True)
            
            # Parsear hora (formato típico: "2:10 PM", "14:30", etc.)
            game_time = self.parse_game_time(time_text)
            
            if not game_time:
                return None
            
            # Separar equipos
            if ' @ ' in teams_text:
                away_team, home_team = teams_text.split(' @ ')
            elif ' vs ' in teams_text:
                away_team, home_team = teams_text.split(' vs ')
            else:
                return None
            
            return {
                'sport': sport,
                'away_team': away_team.strip(),
                'home_team': home_team.strip(),
                'game_time': game_time,
                'game_time_str': time_text
            }
            
        except Exception as e:
            logger.warning(f"Error extrayendo horario de partido: {e}")
            return None
    
    def parse_game_time(self, time_str: str) -> Optional[datetime]:
        """
        Parsea string de hora a datetime
        
        Args:
            time_str: String con hora (ej: "2:10 PM", "14:30")
            
        Returns:
            datetime object o None
        """
        try:
            today = datetime.now(self.timezone).date()
            
            # Formato 12 horas (2:10 PM)
            if 'PM' in time_str or 'AM' in time_str:
                time_clean = time_str.replace('PM', '').replace('AM', '').strip()
                time_parts = time_clean.split(':')
                
                if len(time_parts) == 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    
                    # Ajustar para formato 24 horas
                    if 'PM' in time_str and hour != 12:
                        hour += 12
                    elif 'AM' in time_str and hour == 12:
                        hour = 0
                    
                    return datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            
            # Formato 24 horas (14:30)
            elif ':' in time_str:
                time_parts = time_str.split(':')
                if len(time_parts) == 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    
                    return datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            
            return None
            
        except Exception as e:
            logger.warning(f"Error parseando hora '{time_str}': {e}")
            return None
    
    async def schedule_pregame_scraping(self, sport: str, game: Dict) -> bool:
        """
        Programa scraping específico para un partido
        
        Args:
            sport: Deporte
            game: Información del partido
            
        Returns:
            True si se programó exitosamente
        """
        try:
            game_time = game['game_time']
            pregame_minutes = self.sports_config.get_pregame_scraping_minutes(sport)
            
            # Calcular tiempo de scraping (15 minutos antes)
            scraping_time = game_time - timedelta(minutes=pregame_minutes)
            
            # Asegurar que el scraping sea en el futuro
            now = datetime.now(self.timezone)
            if scraping_time <= now:
                logger.warning(f"⚠️ Partido muy pronto para programar scraping: {game['away_team']} @ {game['home_team']}")
                return False
            
            # Crear job ID único
            job_id = f"pregame_{sport}_{game['away_team']}_{game['home_team']}_{game_time.strftime('%H%M')}"
            
            # Programar el job
            self.scheduler.add_job(
                func=self.execute_pregame_scraping,
                trigger=DateTrigger(run_date=scraping_time),
                args=[sport, game],
                id=job_id,
                name=f"Pregame {sport}: {game['away_team']} @ {game['home_team']}",
                replace_existing=True
            )
            
            # Guardar referencia
            self.scheduled_jobs[job_id] = {
                'sport': sport,
                'game': game,
                'scraping_time': scraping_time,
                'scheduled_at': now
            }
            
            logger.info(f"📅 Programado scraping para {scraping_time.strftime('%H:%M')}: {game['away_team']} @ {game['home_team']}")
            return True
            
        except Exception as e:
            logger.error(f"Error programando scraping pregame: {e}")
            return False
    
    async def execute_pregame_scraping(self, sport: str, game: Dict):
        """
        Ejecuta scraping pregame para un partido específico
        
        Args:
            sport: Deporte
            game: Información del partido
        """
        try:
            logger.info(f"🕷️ Ejecutando scraping pregame: {game['away_team']} @ {game['home_team']}")
            
            if sport == 'MLB':
                scraper = MLBScraper()
                
                # Scraping específico del partido
                consensus_data = await scraper.scrape_mlb_consensus()
                
                # Filtrar solo el partido específico
                game_consensus = [
                    c for c in consensus_data 
                    if (c.get('equipo_visitante') == game['away_team'] and 
                        c.get('equipo_local') == game['home_team'])
                ]
                
                if game_consensus:
                    logger.info(f"✅ Consenso pregame obtenido: {len(game_consensus)} registros")
                    
                    # Enviar a procesamiento (callback o base de datos)
                    await self.process_pregame_consensus(sport, game, game_consensus)
                else:
                    logger.warning(f"⚠️ No se encontró consenso para: {game['away_team']} @ {game['home_team']}")
                
                scraper.close()
                
        except Exception as e:
            logger.error(f"Error en scraping pregame: {e}")
    
    async def process_pregame_consensus(self, sport: str, game: Dict, consensus_data: List[Dict]):
        """
        Procesa los datos de consenso pregame
        
        Args:
            sport: Deporte
            game: Información del partido
            consensus_data: Datos de consenso
        """
        try:
            # Marcar como datos pregame
            for consensus in consensus_data:
                consensus['tipo_scraping'] = 'pregame'
                consensus['minutos_antes_partido'] = self.sports_config.get_pregame_scraping_minutes(sport)
                consensus['partido_programado'] = game['game_time'].isoformat()
            
            # Aquí se conectaría con el sistema de alertas y base de datos
            logger.info(f"📊 Procesando {len(consensus_data)} consensos pregame")
            
            # TODO: Integrar con TelegramNotifier para alertas específicas
            # TODO: Guardar en base de datos con flag de pregame
            
        except Exception as e:
            logger.error(f"Error procesando consenso pregame: {e}")
    
    def get_scheduled_jobs_info(self) -> Dict:
        """Obtiene información de jobs programados"""
        return {
            'total_jobs': len(self.scheduled_jobs),
            'active_jobs': len(self.scheduler.get_jobs()),
            'scheduled_jobs': self.scheduled_jobs
        }


# Instancia global
pregame_scheduler = PregameScheduler()


async def main():
    """Función de prueba"""
    logger.info("=== PRUEBA DEL PREGAME SCHEDULER ===")
    
    try:
        scheduler = PregameScheduler()
        await scheduler.start()
        
        # Programar scraping pregame para MLB
        await scheduler.schedule_daily_pregame_scraping('MLB')
        
        # Mostrar información
        info = scheduler.get_scheduled_jobs_info()
        logger.info(f"📊 Jobs programados: {info['total_jobs']}")
        
        # Mantener activo por un tiempo para pruebas
        await asyncio.sleep(10)
        
        await scheduler.stop()
        logger.info("✅ Prueba completada")
        
    except Exception as e:
        logger.error(f"Error en prueba: {e}")


if __name__ == "__main__":
    asyncio.run(main())
