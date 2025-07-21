#!/usr/bin/env python3
"""
SCRAPER MLB CON SELENIUM - ALTERNATIVA ROBUSTA
=============================================
Usa Selenium para cargar la página como un navegador real
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime
from typing import List, Dict, Optional

class MLBSeleniumScraper:
    """Scraper MLB usando Selenium para mayor robustez"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura el driver de Chrome con opciones optimizadas"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Para debugging, quitar --headless para ver el navegador
            # chrome_options.add_argument('--headless')
            
            # Instalar ChromeDriver automáticamente
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Driver de Chrome inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error al inicializar driver: {e}")
            raise
    
    def scrape_consensus(self, date: str = None) -> List[Dict]:
        """Scraping principal usando Selenium"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        url = f"https://contests.covers.com/consensus/topoverunderconsensus/all/expert/{date}"
        
        print(f"🌐 Cargando: {url}")
        
        try:
            # Cargar la página
            self.driver.get(url)
            
            # Esperar que la página se cargue completamente
            print("⏳ Esperando que la página se cargue...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Esperar un poco más para que se cargue el contenido dinámico
            time.sleep(5)
            
            print("✅ Página cargada")
            
            # Buscar tablas
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            print(f"📋 Tablas encontradas: {len(tables)}")
            
            if not tables:
                print("❌ No se encontraron tablas")
                return []
            
            consensos = []
            
            # Analizar cada tabla
            for i, table in enumerate(tables):
                print(f"\n🔍 Analizando tabla {i+1}")
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"   Filas encontradas: {len(rows)}")
                
                for j, row in enumerate(rows):
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 3:
                            row_text = row.text
                            print(f"   Fila {j}: {row_text[:100]}...")
                            
                            # Buscar patrones de consenso
                            if self._is_consensus_row(row_text):
                                consensus = self._extract_consensus(row_text, cells)
                                if consensus:
                                    consensos.append(consensus)
                                    print(f"   ✅ Consenso extraído: {consensus}")
                    
                    except Exception as e:
                        continue
            
            print(f"\n📊 Total consensos extraídos: {len(consensos)}")
            return consensos
            
        except Exception as e:
            print(f"❌ Error durante scraping: {e}")
            return []
    
    def _is_consensus_row(self, text: str) -> bool:
        """Verifica si una fila contiene datos de consenso"""
        text_lower = text.lower()
        
        # Buscar indicadores de consenso
        has_over_under = 'over' in text_lower or 'under' in text_lower
        has_percentage = '%' in text
        has_teams = bool(re.search(r'[A-Z]{2,4}', text))  # Códigos de equipos
        has_time = bool(re.search(r'\d{1,2}:\d{2}', text))  # Hora del juego
        
        return (has_over_under or has_percentage) and (has_teams or has_time)
    
    def _extract_consensus(self, row_text: str, cells) -> Optional[Dict]:
        """Extrae datos de consenso de una fila"""
        try:
            # Buscar porcentajes
            percentages = re.findall(r'(\d{1,3})%', row_text)
            
            # Buscar Over/Under
            direction = None
            if 'over' in row_text.lower():
                direction = 'Over'
            elif 'under' in row_text.lower():
                direction = 'Under'
            
            # Buscar equipos (códigos de 3 letras típicamente)
            teams = re.findall(r'\b[A-Z]{2,4}\b', row_text)
            
            # Buscar hora
            time_match = re.search(r'(\d{1,2}:\d{2})', row_text)
            game_time = time_match.group(1) if time_match else None
            
            if percentages and direction:
                return {
                    'equipo_visitante': teams[0] if len(teams) > 0 else 'N/A',
                    'equipo_local': teams[1] if len(teams) > 1 else 'N/A',
                    'direccion_consenso': direction,
                    'porcentaje_consenso': int(percentages[0]),
                    'num_experts': len(percentages),  # Aproximación
                    'hora_juego': game_time,
                    'fecha_juego': datetime.now().strftime('%Y-%m-%d'),
                    'raw_text': row_text[:100]  # Para debugging
                }
        
        except Exception as e:
            print(f"Error extrayendo consenso: {e}")
        
        return None
    
    def close(self):
        """Cierra el driver"""
        if self.driver:
            self.driver.quit()
            print("🔴 Driver cerrado")
    
    def __del__(self):
        """Destructor para cerrar driver automáticamente"""
        self.close()

def test_selenium_scraper():
    """Función de prueba del scraper Selenium"""
    print("🚀 PROBANDO SCRAPER SELENIUM")
    print("="*50)
    
    scraper = None
    
    try:
        scraper = MLBSeleniumScraper()
        consensos = scraper.scrape_consensus()
        
        if consensos:
            print(f"\n🎯 {len(consensos)} CONSENSOS ENCONTRADOS:")
            for i, consenso in enumerate(consensos):
                print(f"\n{i+1}. {consenso['equipo_visitante']} @ {consenso['equipo_local']}")
                print(f"   Consenso: {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
                print(f"   Hora: {consenso['hora_juego']}")
                print(f"   Raw: {consenso['raw_text']}")
        else:
            print("\n❌ No se encontraron consensos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    test_selenium_scraper()
    input("\n⏸️ Presiona Enter para continuar...")
