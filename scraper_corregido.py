"""
SCRAPER MLB SELENIUM - VERSIÓN CORREGIDA DEFINITIVA
=================================================
Basado en el análisis exacto de la estructura de covers.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLBSeleniumScraperFixed:
    """Scraper MLB Selenium - Versión Corregida"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"
        
    def _setup_driver(self):
        """Configurar Chrome driver - MODO VISIBLE"""
        try:
            print("🔧 Configurando Chrome driver...")
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # NO headless - queremos ver el navegador
            # chrome_options.add_argument('--headless')  # DESACTIVADO
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            print("✅ Chrome configurado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando driver: {e}")
            return False
    
    def scrape_mlb_consensus(self, date: Optional[str] = None) -> List[Dict]:
        """Scraper principal - Versión corregida"""
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"🚀 Iniciando scraping para {date}")
        
        if not self._setup_driver():
            return []
        
        try:
            # Navegar a la página
            url = f"{self.base_url}/{date}"
            print(f"🌐 Navegando a: {url}")
            self.driver.get(url)
            
            print("⏳ Esperando 10 segundos para carga completa...")
            time.sleep(10)
            
            print(f"📄 Título: {self.driver.title}")
            
            # Buscar la tabla con clase "responsive"
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table.responsive")
            
            if not tables:
                print("❌ No se encontró tabla con clase 'responsive'")
                return []
            
            print(f"📊 Tablas encontradas: {len(tables)}")
            
            consensos = []
            
            # Procesar la primera tabla (que contiene los consensos)
            table = tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            print(f"📋 Filas en tabla: {len(rows)}")
            
            # Procesar cada fila (saltar la primera que es header)
            for i, row in enumerate(rows[1:], 1):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) < 6:
                        continue
                    
                    # Extraer datos de las celdas según la estructura conocida
                    consenso = self._extraer_consenso_de_celdas(cells, date, i)
                    
                    if consenso:
                        consensos.append(consenso)
                        print(f"✅ Consenso {i}: {consenso['equipo_visitante']} @ {consenso['equipo_local']} - "
                              f"{consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
                
                except Exception as e:
                    print(f"⚠️ Error procesando fila {i}: {e}")
                    continue
            
            print(f"🎯 TOTAL CONSENSOS EXTRAÍDOS: {len(consensos)}")
            return consensos
            
        except Exception as e:
            print(f"❌ Error durante scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if self.driver:
                print("🔴 Cerrando navegador...")
                self.driver.quit()
    
    def _extraer_consenso_de_celdas(self, cells, date: str, row_num: int) -> Optional[Dict]:
        """Extraer consenso directamente de las celdas de la tabla"""
        try:
            # Según el debug anterior, la estructura es:
            # Celda 0: "MLB\\nTEAM1\\nTEAM2"
            # Celda 1: "Date\\nTime ET"  
            # Celda 2: "XX % Under\\nYY % Over" (o viceversa)
            # Celda 3: "Total"
            # Celda 4: "Picks"
            # Celda 5: "Details"
            
            if len(cells) < 6:
                return None
            
            # CELDA 0: Equipos
            teams_text = cells[0].text.strip()
            print(f"   Debug fila {row_num} - Equipos: '{teams_text}'")
            
            # Extraer equipos (formato: "MLB\\nNYY\\nATL")
            lines = teams_text.split('\\n')
            if len(lines) < 3:
                # Intentar con salto de línea real
                lines = teams_text.split('\n')
            
            if len(lines) >= 3 and lines[0] == 'MLB':
                equipo_visitante = lines[1].strip()
                equipo_local = lines[2].strip()
            else:
                return None
            
            # CELDA 1: Fecha y hora
            datetime_text = cells[1].text.strip()
            print(f"   Debug fila {row_num} - Fecha/Hora: '{datetime_text}'")
            
            # Extraer hora (formato: "Sun. Jul. 20\\n1:35 pm ET")
            hora_match = re.search(r'(\\d{1,2}:\\d{2}\\s+[ap]m\\s+ET)', datetime_text, re.IGNORECASE)
            if not hora_match:
                hora_match = re.search(r'(\\d{1,2}:\\d{2}\\s+[ap]m\\s+ET)', datetime_text.replace('\n', '\\n'), re.IGNORECASE)
            
            hora_juego = hora_match.group(1) if hora_match else "N/A"
            
            # CELDA 2: Consenso (formato: "86 % Under\\n14 % Over")
            consensus_text = cells[2].text.strip()
            print(f"   Debug fila {row_num} - Consenso: '{consensus_text}'")
            
            # Buscar porcentajes
            over_match = re.search(r'(\\d{1,3})\\s*%\\s*Over', consensus_text, re.IGNORECASE)
            under_match = re.search(r'(\\d{1,3})\\s*%\\s*Under', consensus_text, re.IGNORECASE)
            
            if over_match:
                porcentaje_over = int(over_match.group(1))
                porcentaje_under = 100 - porcentaje_over
                direccion_consenso = 'OVER'
                porcentaje_consenso = porcentaje_over
            elif under_match:
                porcentaje_under = int(under_match.group(1))
                porcentaje_over = 100 - porcentaje_under
                direccion_consenso = 'UNDER'
                porcentaje_consenso = porcentaje_under
            else:
                return None
            
            # CELDA 3: Total
            total_text = cells[3].text.strip()
            print(f"   Debug fila {row_num} - Total: '{total_text}'")
            
            try:
                total_line = float(total_text)
            except:
                total_line = 0.0
            
            # CELDA 4: Picks
            picks_text = cells[4].text.strip()
            print(f"   Debug fila {row_num} - Picks: '{picks_text}'")
            
            # Extraer números de picks
            pick_numbers = re.findall(r'\\b(\\d+)\\b', picks_text)
            
            if len(pick_numbers) >= 2:
                picks_1 = int(pick_numbers[0])
                picks_2 = int(pick_numbers[1])
                total_picks = picks_1 + picks_2
            else:
                picks_1 = picks_2 = 0
                total_picks = int(pick_numbers[0]) if pick_numbers else 0
            
            # Construir objeto de consenso
            consenso = {
                'fecha_juego': date,
                'hora_juego': hora_juego,
                'equipo_visitante': equipo_visitante,
                'equipo_local': equipo_local,
                'direccion_consenso': direccion_consenso,
                'porcentaje_consenso': porcentaje_consenso,
                'porcentaje_over': porcentaje_over,
                'porcentaje_under': porcentaje_under,
                'total_line': total_line,
                'picks_over': picks_1 if direccion_consenso == 'OVER' else picks_2,
                'picks_under': picks_2 if direccion_consenso == 'OVER' else picks_1,
                'total_picks': total_picks,
                'num_experts': total_picks,
                'fecha_scraping': datetime.now().isoformat(),
                'deporte': 'MLB',
                'tipo_consenso': 'TOTAL',
                'consenso_over': porcentaje_over,
                'consenso_under': porcentaje_under,
                'url_fuente': self.base_url
            }
            
            return consenso
            
        except Exception as e:
            print(f"❌ Error extrayendo consenso de fila {row_num}: {e}")
            return None

    def get_live_consensus(self) -> List[Dict]:
        """Compatible con la interfaz web"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.scrape_mlb_consensus(today)

def test_scraper_corregido():
    """Test del scraper corregido"""
    print("🧪 PROBANDO SCRAPER SELENIUM CORREGIDO")
    print("="*60)
    
    scraper = MLBSeleniumScraperFixed()
    
    try:
        consensos = scraper.scrape_mlb_consensus()
        
        print(f"\\n📊 RESULTADO FINAL:")
        print(f"   Consensos encontrados: {len(consensos)}")
        
        if consensos:
            print(f"\\n🎯 CONSENSOS VÁLIDOS:")
            for i, consenso in enumerate(consensos):
                print(f"\\n   {i+1}. {consenso['equipo_visitante']} @ {consenso['equipo_local']}")
                print(f"      Consenso: {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
                print(f"      Over: {consenso['porcentaje_over']}% | Under: {consenso['porcentaje_under']}%")
                print(f"      Total: {consenso['total_line']}")
                print(f"      Picks: {consenso['total_picks']} expertos")
                print(f"      Hora: {consenso['hora_juego']}")
        else:
            print(f"\\n❌ No se encontraron consensos válidos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper_corregido()
    input("\\n⏸️ Presiona Enter para continuar...")
