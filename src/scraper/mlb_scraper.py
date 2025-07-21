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
import re
from src.utils.logger import get_logger
from src.utils.error_handler import ErrorHandler, retry_on_failure, log_exception

logger = get_logger(__name__)

class MLBScraper:
    """Scraper para consensos de MLB desde covers.com"""
    
    def __init__(self, base_url: str = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"):
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
    
    def get_page_content_sync(self, url: str, timeout: int = 30) -> Optional[BeautifulSoup]:
        """Obtiene el contenido HTML de una página (versión síncrona)"""
        try:
            logger.info(f"Obteniendo contenido de: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"Contenido obtenido exitosamente. Tamaño: {len(response.content)} bytes")
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener página {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al procesar página {url}: {e}")
            raise

    def get_page_content(self, url: str, timeout: int = 30) -> Optional[BeautifulSoup]:
        """Alias para mantener compatibilidad con el código existente"""
        return self.get_page_content_sync(url, timeout)
    
    @log_exception
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
        
        logger.info(f"Iniciando scraping de consensos MLB TOTALES para fecha: {date}")
        
        # URL para la fecha específica (formato covers.com)
        url = f"{self.base_url}/{date}"
        soup = self.get_page_content(url)
        
        if not soup:
            logger.warning(f"No se pudo obtener contenido para fecha {date}")
            return []
        
        consensos = []
        
        try:
            # Buscar específicamente la tabla con clase "responsive"
            table = soup.find('table', class_='responsive')
            
            if not table:
                logger.warning("No se encontró tabla con clase 'responsive'")
                # Fallback: buscar cualquier tabla
                table = soup.find('table')
                if not table:
                    logger.warning("No se encontró ninguna tabla en la página")
                    return []
            
            # Buscar todas las filas de la tabla (excluir header)
            rows = table.find_all('tr')
            logger.info(f"Encontradas {len(rows)} filas en la tabla")
            
            # Filtrar filas de datos (que tengan suficientes celdas)
            game_rows = []
            for i, row in enumerate(rows):
                cells = row.find_all('td')
                row_text = row.get_text(strip=True)
                
                logger.debug(f"Fila {i}: {len(cells)} celdas - '{row_text[:100]}...'")
                
                # Criterios menos restrictivos para encontrar filas válidas
                if len(cells) >= 3:  # Reducido a 3 columnas mínimo
                    # Verificar que contenga indicadores de partido
                    has_teams = bool(re.search(r'[A-Z]{2,3}', row_text))
                    has_percentage = '%' in row_text
                    has_time = bool(re.search(r'\d{1,2}:\d{2}', row_text))
                    
                    # Si tiene equipos Y (porcentajes O hora), es candidata
                    if has_teams and (has_percentage or has_time):
                        game_rows.append(row)
                        logger.debug(f"Fila {i} añadida como válida: equipos={has_teams}, %={has_percentage}, hora={has_time}")
                    else:
                        logger.debug(f"Fila {i} descartada: equipos={has_teams}, %={has_percentage}, hora={has_time}")
                else:
                    logger.debug(f"Fila {i} descartada: solo {len(cells)} celdas")
            
            logger.info(f"Encontradas {len(game_rows)} filas con datos válidos de partidos")
            
            # Procesar cada fila válida
            for i, row in enumerate(game_rows):
                try:
                    consensus_data = self._extract_consensus_from_row(row, date)
                    if consensus_data:
                        consensos.append(consensus_data)
                        logger.info(f"Consenso {i+1} extraído: {consensus_data['equipo_visitante']} @ {consensus_data['equipo_local']} - "
                                  f"{consensus_data['direccion_consenso']}: {consensus_data['porcentaje_consenso']}% ({consensus_data['num_experts']} expertos)")
                except Exception as e:
                    logger.debug(f"Fila {i+1} no procesable: {str(e)[:100]}")
                    continue
            
            logger.info(f"Total consensos válidos extraídos: {len(consensos)}")
            
        except Exception as e:
            logger.error(f"Error durante scraping de consensos: {e}")
            raise
        
        return consensos
    
    def _extract_consensus_from_row(self, row, date: str) -> Optional[Dict]:
        """Extrae datos de consenso de totales (Over/Under) de una fila de la tabla"""
        try:
            # Obtener todas las celdas de la fila
            cells = row.find_all('td')
            if len(cells) < 3:  # Reducido a 3 celdas mínimo
                return None
            
            # Obtener texto de todas las celdas para análisis
            all_row_text = row.get_text(strip=True)
            logger.debug(f"Analizando fila con {len(cells)} celdas: {all_row_text[:200]}...")
            
            # Mostrar contenido de cada celda para depuración
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                logger.debug(f"  Celda {i}: '{cell_text[:50]}...'")
            
            # Inicializar datos del consenso
            consensus_data = {
                'fecha': date,
                'fecha_scraping': datetime.now(self.timezone).isoformat(),
                'deporte': 'MLB',
                'tipo_consenso': 'TOTAL',
                'equipo_local': 'Unknown',
                'equipo_visitante': 'Unknown',
                'total_line': 0.0,
                'consenso_over': 0,
                'consenso_under': 0,
                'porcentaje_consenso': 0.0,
                'direccion_consenso': '',
                'num_experts': 0,
                'hora_partido': '',
                'url_fuente': self.base_url
            }
            
            # Buscar equipos en cualquier celda
            team_found = False
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Patrones de equipos
                team_patterns = [
                    r'([A-Z]{2,3})\s+@\s+([A-Z]{2,3})',  # CHI @ HOU
                    r'([A-Z]{2,3})\s+([A-Z]{2,3})',      # CHI HOU
                    r'(\w+)\s+@\s+(\w+)'                  # Nombres completos
                ]
                
                for pattern in team_patterns:
                    team_match = re.search(pattern, cell_text)
                    if team_match:
                        consensus_data['equipo_visitante'] = team_match.group(1)
                        consensus_data['equipo_local'] = team_match.group(2)
                        team_found = True
                        logger.debug(f"Equipos encontrados en celda {i}: {consensus_data['equipo_visitante']} @ {consensus_data['equipo_local']}")
                        break
                
                if team_found:
                    break
            
            # Buscar hora del partido en cualquier celda
            time_found = False
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                time_match = re.search(r'(\d{1,2}:\d{2}\s*[ap]m\s*ET)', cell_text, re.IGNORECASE)
                if time_match:
                    consensus_data['hora_partido'] = time_match.group(1)
                    time_found = True
                    logger.debug(f"Hora encontrada en celda {i}: {consensus_data['hora_partido']}")
                    break
            
            # Buscar consenso Over/Under en cualquier celda
            consensus_found = False
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Buscar patrones como "80% Under" o "74% Over"
                over_match = re.search(r'(\d+)%\s*Over', cell_text, re.IGNORECASE)
                under_match = re.search(r'(\d+)%\s*Under', cell_text, re.IGNORECASE)
                
                if over_match:
                    consensus_data['consenso_over'] = int(over_match.group(1))
                    consensus_data['porcentaje_consenso'] = int(over_match.group(1))
                    consensus_data['direccion_consenso'] = 'OVER'
                    consensus_found = True
                    logger.debug(f"Consenso OVER encontrado en celda {i}: {consensus_data['porcentaje_consenso']}%")
                    break
                elif under_match:
                    consensus_data['consenso_under'] = int(under_match.group(1))
                    consensus_data['porcentaje_consenso'] = int(under_match.group(1))
                    consensus_data['direccion_consenso'] = 'UNDER'
                    consensus_found = True
                    logger.debug(f"Consenso UNDER encontrado en celda {i}: {consensus_data['porcentaje_consenso']}%")
                    break
            
            # Si el porcentaje Over/Under no se encuentra, calcular el complementario
            if consensus_data['consenso_over'] > 0 and consensus_data['consenso_under'] == 0:
                consensus_data['consenso_under'] = 100 - consensus_data['consenso_over']
            elif consensus_data['consenso_under'] > 0 and consensus_data['consenso_over'] == 0:
                consensus_data['consenso_over'] = 100 - consensus_data['consenso_under']
            
            # Mantener compatibilidad
            consensus_data['porcentaje_total'] = consensus_data['porcentaje_consenso']
            
            # Buscar línea del total en cualquier celda
            total_found = False
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                # Buscar números que puedan ser totales (entre 6.0 y 15.0)
                total_matches = re.findall(r'(\d+(?:\.\d+)?)', cell_text)
                for total_str in total_matches:
                    total_val = float(total_str)
                    if 6.0 <= total_val <= 15.0:  # Rango típico de totales MLB
                        consensus_data['total_line'] = total_val
                        total_found = True
                        logger.debug(f"Total encontrado en celda {i}: {total_val}")
                        break
                if total_found:
                    break
            
            # Buscar número de expertos en cualquier celda
            experts_found = False
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Buscar patrones de números de expertos
                pick_numbers = re.findall(r'\b(\d+)\b', cell_text)
                
                # Filtrar números que puedan ser expertos (típicamente entre 1 y 100)
                valid_numbers = [int(num) for num in pick_numbers if 1 <= int(num) <= 100]
                
                if len(valid_numbers) >= 2:
                    # Si hay dos números válidos, sumarlos (ej: "15 + 4" = 19)
                    consensus_data['num_experts'] = sum(valid_numbers[:2])
                    experts_found = True
                    logger.debug(f"Expertos (suma) encontrados en celda {i}: {valid_numbers[:2]} = {consensus_data['num_experts']}")
                    break
                elif len(valid_numbers) == 1:
                    # Si hay un solo número válido, usarlo directamente
                    consensus_data['num_experts'] = valid_numbers[0]
                    experts_found = True
                    logger.debug(f"Expertos encontrados en celda {i}: {consensus_data['num_experts']}")
                    break
            
            # Logging de depuración de toda la fila
            logger.debug(f"Fila procesada - Equipos: {team_found}, Hora: {time_found}, Consenso: {consensus_found}, Total: {total_found}, Expertos: {experts_found}")
            
            # Validar que tenemos datos mínimos válidos (criterios relajados)
            valid_team = (consensus_data['equipo_visitante'] != 'Unknown' and
                         consensus_data['equipo_local'] != 'Unknown')
            valid_consensus = (consensus_data['porcentaje_consenso'] > 0 and 
                             consensus_data['direccion_consenso'])
            valid_experts = consensus_data['num_experts'] > 0
            
            # Mostrar estado de validación
            logger.debug(f"Validación - Equipos: {valid_team}, Consenso: {valid_consensus}, Expertos: {valid_experts}")
            
            # Criterio mínimo: debe tener equipos Y (consenso O expertos)
            if valid_team and (valid_consensus or valid_experts):
                logger.info(f"Consenso válido extraído: {consensus_data['equipo_visitante']} @ {consensus_data['equipo_local']} - "
                           f"{consensus_data['direccion_consenso']}: {consensus_data['porcentaje_consenso']}% ({consensus_data['num_experts']} expertos)")
                return consensus_data
            else:
                logger.debug(f"Fila no válida - Equipos válidos: {valid_team}, "
                           f"Consenso válido: {valid_consensus}, Expertos válidos: {valid_experts}")
                logger.debug(f"  Equipos: {consensus_data['equipo_visitante']} @ {consensus_data['equipo_local']}")
                logger.debug(f"  Consenso: {consensus_data['direccion_consenso']} {consensus_data['porcentaje_consenso']}%")
                logger.debug(f"  Expertos: {consensus_data['num_experts']}")
            
            return None
            
        except Exception as e:
            logger.debug(f"Error al extraer consenso de fila: {e}")
            return None
    
    @log_exception
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
    
    @log_exception
    def get_live_consensus(self) -> List[Dict]:
        """Obtiene consensos para partidos en vivo o próximos (versión síncrona)"""
        logger.info("Obteniendo consensos en vivo")
        
        today = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        # Usar el método principal de scraping que ya está optimizado
        try:
            consensos = self.scrape_mlb_consensus(today)
            logger.info(f"Obtenidos {len(consensos)} consensos en vivo")
            return consensos
            
        except Exception as e:
            logger.error(f"Error obteniendo consensos en vivo: {e}")
            return []
    
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
    
    logger.info("=== PRUEBA DEL SCRAPER MLB TOTALES ===")
    
    try:
        with MLBScraper() as scraper:
            # Probar scraping del día actual
            consensos = scraper.get_live_consensus()
            
            print(f"\n📊 Consensos de totales obtenidos: {len(consensos)}")
            
            if consensos:
                print("\n🏈 Consensos encontrados:")
                for i, consenso in enumerate(consensos):
                    print(f"\n{i+1}. {consenso['equipo_visitante']} @ {consenso['equipo_local']}")
                    print(f"   Consenso: {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
                    print(f"   Over: {consenso['consenso_over']}% | Under: {consenso['consenso_under']}%")
                    print(f"   Total Line: {consenso['total_line']}")
                    print(f"   Expertos: {consenso['num_experts']}")
                    print(f"   Hora: {consenso['hora_partido']}")
            else:
                print("\n⚠️  No se encontraron consensos para hoy")
            
            # Guardar datos de prueba
            with open('test_consensos_mlb.json', 'w', encoding='utf-8') as f:
                json.dump(consensos, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Datos guardados en test_consensos_mlb.json")
            
    except Exception as e:
        logger.error(f"Error en prueba del scraper: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
