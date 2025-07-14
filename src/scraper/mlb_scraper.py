"""
Scraper especializado para obtener consensos de MLB desde covers.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional
import time
import logging
from src.utils.logger import get_logger
from src.utils.error_handler import handle_errors, retry_on_failure

logger = get_logger(__name__)

class MLBScraper:
    """Scraper para consensos de MLB desde covers.com"""
    
    def __init__(self, base_url: str = "https://www.covers.com/sports/mlb/consensus"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Configurar zona horaria de Argentina
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
    
    @retry_on_failure(max_attempts=3, delay=5)
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Obtiene el contenido HTML de una página"""
        try:
            logger.info(f"Obteniendo contenido de: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"Contenido obtenido exitosamente. Tamaño: {len(response.content)} bytes")
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener página {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al parsear página {url}: {e}")
            raise
    
    @handle_errors
    def scrape_mlb_consensus(self, date: Optional[str] = None) -> List[Dict]:
        """
        Scrape consensos de MLB para una fecha específica
        
        Args:
            date: Fecha en formato YYYY-MM-DD. Si es None, usa la fecha actual.
            
        Returns:
            Lista de diccionarios con datos de consenso
        """
        if date is None:
            date = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        logger.info(f"Iniciando scraping de consensos MLB para fecha: {date}")
        
        # URL para la fecha específica
        url = f"{self.base_url}?date={date}"
        soup = self.get_page_content(url)
        
        if not soup:
            logger.warning(f"No se pudo obtener contenido para fecha {date}")
            return []
        
        consensos = []
        
        try:
            # Buscar tabla de consensos (estructura típica de covers.com)
            consensus_tables = soup.find_all('table', class_=['consensus-table', 'table', 'data-table'])
            
            if not consensus_tables:
                # Intentar con selectores más específicos
                consensus_sections = soup.find_all('div', class_=['consensus', 'betting-consensus', 'picks-consensus'])
                logger.info(f"Encontradas {len(consensus_sections)} secciones de consenso")
            
            # Buscar filas de partidos
            game_rows = soup.find_all('tr', class_=['game-row', 'consensus-row', 'picks-row'])
            
            for row in game_rows:
                try:
                    consensus_data = self._extract_consensus_from_row(row, date)
                    if consensus_data:
                        consensos.append(consensus_data)
                except Exception as e:
                    logger.warning(f"Error al procesar fila de consenso: {e}")
                    continue
            
            logger.info(f"Scraped {len(consensos)} consensos para fecha {date}")
            
        except Exception as e:
            logger.error(f"Error durante scraping de consensos: {e}")
            raise
        
        return consensos
    
    def _extract_consensus_from_row(self, row, date: str) -> Optional[Dict]:
        """Extrae datos de consenso de una fila de la tabla"""
        try:
            # Estructura típica de datos que buscamos
            consensus_data = {
                'fecha': date,
                'fecha_scraping': datetime.now(self.timezone).isoformat(),
                'deporte': 'MLB',
                'equipo_local': '',
                'equipo_visitante': '',
                'consenso_spread': 0,
                'consenso_total': 0,
                'consenso_moneyline': 0,
                'porcentaje_spread': 0.0,
                'porcentaje_total': 0.0,
                'porcentaje_moneyline': 0.0,
                'hora_partido': '',
                'url_fuente': self.base_url
            }
            
            # Extraer nombres de equipos
            team_cells = row.find_all(['td', 'div'], class_=['team', 'teams', 'matchup'])
            if team_cells:
                team_text = team_cells[0].get_text(strip=True)
                if ' @ ' in team_text:
                    teams = team_text.split(' @ ')
                    consensus_data['equipo_visitante'] = teams[0].strip()
                    consensus_data['equipo_local'] = teams[1].strip()
                elif ' vs ' in team_text:
                    teams = team_text.split(' vs ')
                    consensus_data['equipo_visitante'] = teams[0].strip()
                    consensus_data['equipo_local'] = teams[1].strip()
            
            # Extraer porcentajes de consenso
            percentage_cells = row.find_all(['td', 'span'], class_=['percentage', 'consensus-pct', 'pct'])
            
            for i, cell in enumerate(percentage_cells[:3]):  # Máximo 3 porcentajes
                pct_text = cell.get_text(strip=True).replace('%', '')
                try:
                    percentage = float(pct_text)
                    if i == 0:
                        consensus_data['porcentaje_spread'] = percentage
                    elif i == 1:
                        consensus_data['porcentaje_total'] = percentage
                    elif i == 2:
                        consensus_data['porcentaje_moneyline'] = percentage
                except ValueError:
                    continue
            
            # Extraer hora del partido
            time_cells = row.find_all(['td', 'span'], class_=['time', 'game-time', 'start-time'])
            if time_cells:
                consensus_data['hora_partido'] = time_cells[0].get_text(strip=True)
            
            # Solo devolver si encontramos al menos los equipos
            if consensus_data['equipo_local'] and consensus_data['equipo_visitante']:
                return consensus_data
            
        except Exception as e:
            logger.warning(f"Error al extraer datos de fila: {e}")
        
        return None
    
    @handle_errors
    def scrape_multiple_dates(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Scrape consensos para múltiples fechas
        
        Args:
            start_date: Fecha inicial en formato YYYY-MM-DD
            end_date: Fecha final en formato YYYY-MM-DD
            
        Returns:
            Lista combinada de consensos de todas las fechas
        """
        logger.info(f"Scraping múltiples fechas: {start_date} hasta {end_date}")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_consensus = []
        current_date = start
        
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            try:
                daily_consensus = self.scrape_mlb_consensus(date_str)
                all_consensus.extend(daily_consensus)
                
                # Pausa entre requests para ser respetuosos
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error al obtener consensos para fecha {date_str}: {e}")
                continue
            
            current_date += timedelta(days=1)
        
        logger.info(f"Scraping completado. Total de consensos: {len(all_consensus)}")
        return all_consensus
    
    @handle_errors
    def get_live_consensus(self) -> List[Dict]:
        """Obtiene consensos para partidos en vivo o próximos"""
        logger.info("Obteniendo consensos en vivo")
        
        today = datetime.now(self.timezone).strftime('%Y-%m-%d')
        tomorrow = (datetime.now(self.timezone) + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Obtener consensos de hoy y mañana
        live_consensus = []
        live_consensus.extend(self.scrape_mlb_consensus(today))
        live_consensus.extend(self.scrape_mlb_consensus(tomorrow))
        
        return live_consensus
    
    def close(self):
        """Cierra la sesión del scraper"""
        if self.session:
            self.session.close()
            logger.info("Sesión del scraper cerrada")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Función principal para testing del scraper"""
    import json
    
    logger.info("=== PRUEBA DEL SCRAPER MLB ===")
    
    try:
        with MLBScraper() as scraper:
            # Probar scraping del día actual
            consensos = scraper.get_live_consensus()
            
            print(f"\n📊 Consensos obtenidos: {len(consensos)}")
            
            if consensos:
                print("\n🏈 Primeros 3 consensos:")
                for i, consenso in enumerate(consensos[:3]):
                    print(f"\n{i+1}. {consenso['equipo_visitante']} @ {consenso['equipo_local']}")
                    print(f"   Spread: {consenso['porcentaje_spread']}%")
                    print(f"   Total: {consenso['porcentaje_total']}%")
                    print(f"   ML: {consenso['porcentaje_moneyline']}%")
            
            # Guardar datos de prueba
            with open('test_consensos_mlb.json', 'w', encoding='utf-8') as f:
                json.dump(consensos, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Datos guardados en test_consensos_mlb.json")
            
    except Exception as e:
        logger.error(f"Error en prueba del scraper: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
