"""
SCRAPER MLB SELENIUM - VERSIÓN CORREGIDA SIMPLE
===============================================
Extrae exactamente los datos que vemos en el debug anterior
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime
from typing import List, Dict, Optional

class MLBScraperSimple:
    """Scraper simplificado para extraer datos exactos de covers.com"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"
    
    def _setup_driver(self):
        """Configurar Chrome - MODO VISIBLE"""
        try:
            print("🔧 Configurando Chrome...")
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # SIN headless - queremos ver el navegador
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(60)
            
            print("✅ Chrome configurado")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando driver: {e}")
            return False
    
    def scrape_mlb_consensus(self, date: Optional[str] = None) -> List[Dict]:
        """Scraper principal"""
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"🚀 Iniciando scraping para {date}")
        
        if not self._setup_driver():
            return []
        
        consensos = []
        
        try:
            # Ir a la página
            url = f"{self.base_url}/{date}"
            print(f"🌐 Navegando a: {url}")
            self.driver.get(url)
            
            # Esperar carga
            print("⏳ Esperando 10 segundos...")
            time.sleep(10)
            
            print(f"📄 Título: {self.driver.title}")
            
            # Buscar tabla responsive
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table.responsive")
            
            if not tables:
                print("❌ No se encontró tabla responsive")
                return []
            
            print(f"📊 Tablas encontradas: {len(tables)}")
            
            # Procesar primera tabla
            table = tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            print(f"📋 Filas totales: {len(rows)}")
            
            # Procesar cada fila (saltar header)
            for i, row in enumerate(rows[1:], 1):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) < 6:
                        continue
                    
                    print(f"\\n🔍 Procesando fila {i}:")
                    
                    # Celda 0: Equipos (MLB\\nTEAM1\\nTEAM2)
                    teams_cell = cells[0].text.strip()
                    print(f"   Equipos: '{teams_cell}'")
                    
                    # Dividir por saltos de línea
                    team_lines = teams_cell.split('\\n')
                    if len(team_lines) < 3 or team_lines[0] != 'MLB':
                        continue
                    
                    equipo_visitante = team_lines[1].strip()
                    equipo_local = team_lines[2].strip()
                    
                    # Celda 1: Fecha y hora
                    datetime_cell = cells[1].text.strip()
                    print(f"   Fecha/Hora: '{datetime_cell}'")
                    
                    # Extraer hora
                    hora_match = re.search(r'(\\d{1,2}:\\d{2}\\s+[ap]m\\s+ET)', datetime_cell, re.IGNORECASE)
                    hora_juego = hora_match.group(1) if hora_match else "N/A"
                    
                    # Celda 2: Consenso (XX % Under\\nYY % Over)
                    consensus_cell = cells[2].text.strip()
                    print(f"   Consenso: '{consensus_cell}'")
                    
                    # Extraer porcentajes
                    over_match = re.search(r'(\\d{1,3})\\s*%\\s*Over', consensus_cell, re.IGNORECASE)
                    under_match = re.search(r'(\\d{1,3})\\s*%\\s*Under', consensus_cell, re.IGNORECASE)
                    
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
                        continue
                    
                    # Celda 3: Total
                    total_cell = cells[3].text.strip()
                    print(f"   Total: '{total_cell}'")
                    
                    try:
                        total_line = float(total_cell)
                    except:
                        total_line = 0.0
                    
                    # Celda 4: Picks
                    picks_cell = cells[4].text.strip()
                    print(f"   Picks: '{picks_cell}'")
                    
                    # Extraer números de picks
                    pick_numbers = re.findall(r'\\b(\\d+)\\b', picks_cell)
                    total_picks = sum(int(n) for n in pick_numbers) if pick_numbers else 0
                    
                    # Crear consenso
                    consenso = {
                        'fecha_juego': date,
                        'hora_juego': hora_juego,
                        'equipo_visitante': equipo_visitante,
                        'equipo_local': equipo_local,
                        'direccion_consenso': direccion_consenso,
                        'porcentaje_consenso': porcentaje_consenso,
                        'porcentaje_over': porcentaje_over,
                        'porcentaje_under': porcentaje_under,
                        'consenso_over': porcentaje_over,  # Compatibilidad
                        'consenso_under': porcentaje_under,  # Compatibilidad
                        'total_line': total_line,
                        'num_experts': total_picks,
                        'total_picks': total_picks,
                        'fecha_scraping': datetime.now().isoformat(),
                        'deporte': 'MLB',
                        'tipo_consenso': 'TOTAL',
                        'url_fuente': self.base_url
                    }
                    
                    consensos.append(consenso)
                    
                    print(f"✅ Consenso {i}: {equipo_visitante} @ {equipo_local} - "
                          f"{direccion_consenso} {porcentaje_consenso}% (Total: {total_line})")
                    
                except Exception as e:
                    print(f"⚠️ Error en fila {i}: {e}")
                    continue
            
            print(f"\\n🎯 TOTAL CONSENSOS: {len(consensos)}")
            
        except Exception as e:
            print(f"❌ Error general: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            if self.driver:
                print("🔴 Cerrando navegador...")
                self.driver.quit()
        
        return consensos
    
    def get_live_consensus(self) -> List[Dict]:
        """Para compatibilidad con la interfaz"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.scrape_mlb_consensus(today)

def test_simple():
    """Test del scraper simple"""
    print("🧪 PROBANDO SCRAPER SIMPLE")
    print("="*50)
    
    scraper = MLBScraperSimple()
    
    try:
        consensos = scraper.scrape_mlb_consensus()
        
        print(f"\\n📊 RESULTADO: {len(consensos)} consensos")
        
        for i, c in enumerate(consensos):
            print(f"\\n{i+1}. {c['equipo_visitante']} @ {c['equipo_local']}")
            print(f"   {c['direccion_consenso']} {c['porcentaje_consenso']}%")
            print(f"   Total: {c['total_line']} | Expertos: {c['num_experts']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple()
    input("\\nPresiona Enter...")
