"""
Scraper MLB híbrido: Requests + Selenium como fallback
=====================================================
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import List, Dict, Optional

# Selenium imports (solo si es necesario)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    import re
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)

class MLBHybridScraper:
    """Scraper híbrido: Requests primero, Selenium como fallback"""
    
    def __init__(self, base_url: str = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
    def scrape_mlb_consensus(self, date: Optional[str] = None) -> List[Dict]:
        """Método principal de scraping con fallback automático"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Iniciando scraping híbrido para fecha: {date}")
        
        # Intentar con requests primero
        try:
            logger.info("🔄 Intentando con requests/BeautifulSoup...")
            consensos = self._scrape_with_requests(date)
            if consensos:
                logger.info(f"✅ Requests exitoso: {len(consensos)} consensos")
                return consensos
            else:
                logger.warning("⚠️ Requests no obtuvo resultados, probando Selenium...")
        except Exception as e:
            logger.warning(f"❌ Requests falló: {e}, probando Selenium...")
        
        # Fallback a Selenium
        if SELENIUM_AVAILABLE:
            try:
                logger.info("🔄 Intentando con Selenium...")
                consensos = self._scrape_with_selenium(date)
                if consensos:
                    logger.info(f"✅ Selenium exitoso: {len(consensos)} consensos")
                    return consensos
                else:
                    logger.error("❌ Selenium tampoco obtuvo resultados")
            except Exception as e:
                logger.error(f"❌ Selenium falló: {e}")
            finally:
                if self.driver:
                    self.driver.quit()
                    self.driver = None
        else:
            logger.error("❌ Selenium no disponible, instala con: pip install selenium webdriver-manager")
        
        return []
    
    def _scrape_with_requests(self, date: str) -> List[Dict]:
        """Intento con requests/BeautifulSoup"""
        url = f"{self.base_url}/{date}"
        
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar tabla responsiva
        table = soup.find('table', class_='responsive')
        if not table:
            table = soup.find('table')
        
        if not table:
            return []
        
        consensos = []
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                row_text = row.get_text(strip=True)
                
                # Buscar indicadores de consenso
                if self._is_consensus_row(row_text):
                    consensus = self._extract_consensus_from_text(row_text, date)
                    if consensus:
                        consensos.append(consensus)
        
        return consensos
    
    def _scrape_with_selenium(self, date: str) -> List[Dict]:
        """Scraping con Selenium como fallback"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium no disponible")
        
        url = f"{self.base_url}/{date}"
        
        # Configurar Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Sin interfaz gráfica
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Cargar página
        self.driver.get(url)
        
        # Esperar que cargue
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)  # Esperar contenido dinámico
        
        # Buscar tablas
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        consensos = []
        
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        row_text = row.text
                        
                        if self._is_consensus_row(row_text):
                            consensus = self._extract_consensus_from_text(row_text, date)
                            if consensus:
                                consensos.append(consensus)
                
                except Exception:
                    continue
        
        return consensos
    
    def _is_consensus_row(self, text: str) -> bool:
        """Verifica si una fila contiene datos de consenso"""
        text_lower = text.lower()
        
        has_over_under = 'over' in text_lower or 'under' in text_lower
        has_percentage = '%' in text
        has_teams = bool(re.search(r'[A-Z]{2,4}', text))
        has_time = bool(re.search(r'\d{1,2}:\d{2}', text))
        
        return (has_over_under or has_percentage) and (has_teams or has_time)
    
    def _extract_consensus_from_text(self, text: str, date: str) -> Optional[Dict]:
        """Extrae datos de consenso del texto"""
        try:
            # Buscar porcentajes
            percentages = re.findall(r'(\d{1,3})%', text)
            if not percentages:
                return None
            
            # Buscar dirección
            direction = None
            if 'over' in text.lower():
                direction = 'Over'
            elif 'under' in text.lower():
                direction = 'Under'
            
            if not direction:
                return None
            
            # Buscar equipos
            teams = re.findall(r'\b[A-Z]{2,4}\b', text)
            
            # Buscar hora
            time_match = re.search(r'(\d{1,2}:\d{2})', text)
            game_time = time_match.group(1) if time_match else None
            
            return {
                'equipo_visitante': teams[0] if len(teams) > 0 else 'N/A',
                'equipo_local': teams[1] if len(teams) > 1 else 'N/A',
                'direccion_consenso': direction,
                'porcentaje_consenso': int(percentages[0]),
                'num_experts': int(percentages[1]) if len(percentages) > 1 else 20,  # Aproximación
                'hora_juego': game_time,
                'fecha_juego': date,
                'total_line': None,  # Se puede extraer si está disponible
                'spread_line': None
            }
        
        except Exception as e:
            logger.debug(f"Error extrayendo consenso: {e}")
            return None
    
    def __del__(self):
        """Cleanup"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
