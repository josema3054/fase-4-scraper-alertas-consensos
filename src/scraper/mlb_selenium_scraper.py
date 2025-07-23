"""
SCRAPER MLB 100% SELENIUM - VERSIÓN DEFINITIVA
=============================================
Este scraper usa solo Selenium y DEBE funcionar
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
import pytz
from typing import List, Dict, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLBSeleniumScraper:
    """Scraper MLB 100% Selenium - Sin requests, sin complicaciones"""
    
    def __init__(self):
        self.driver = None
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        # Para compatibilidad con la interfaz web
        self.base_url = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"
        
    def _setup_driver(self):
        """Configurar Chrome driver FORZADAMENTE VISIBLE"""
        try:
            logger.info("🔧 Configurando Chrome driver en modo HEADLESS...")
            chrome_options = Options()
            # Configuraciones generales
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            # User agent realista
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            # Modo headless recomendado para servidores
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            logger.info("🤖 Modo HEADLESS habilitado - navegador NO será visible")
            
            # Desactivar imágenes para velocidad pero mantener visibilidad
            prefs = {
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Configuraciones adicionales para modo visible
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Instalar driver automáticamente
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configuraciones adicionales
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ Chrome driver configurado - NAVEGADOR DEBE SER VISIBLE")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando driver: {e}")
            return False
    
    def scrape_mlb_consensus(self, date: Optional[str] = None) -> List[Dict]:
        """Scraping principal - Solo Selenium"""
        
        if date is None:
            date = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        logger.info(f"🚀 INICIANDO SCRAPING SELENIUM para {date}")
        
        if not self._setup_driver():
            return []
        
        try:
            # URL de covers.com
            url = f"https://contests.covers.com/consensus/topoverunderconsensus/all/expert/{date}"
            logger.info(f"🌐 Navegando a: {url}")
            
            # Cargar página
            self.driver.get(url)
            logger.info("⏳ Esperando que la página se cargue...")
            
            # Esperar que el body se cargue
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Esperar contenido dinámico - MÁS TIEMPO para debugging
            time.sleep(15)  # Aumentado para dar tiempo a inspeccionar
            logger.info("✅ Página cargada completamente")
            
            # PAUSA PARA INSPECCIÓN MANUAL
            logger.info("🔍 PAUSA DE 10 SEGUNDOS PARA INSPECCIÓN VISUAL")
            logger.info("   Puedes ver la página ahora en el navegador abierto")
            time.sleep(10)
            
            # Verificar título de la página
            title = self.driver.title
            logger.info(f"📄 Título de página: {title}")
            
            # Buscar todas las tablas
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"📋 Tablas encontradas: {len(tables)}")
            
            if not tables:
                logger.warning("❌ No se encontraron tablas")
                return []
            
            consensos_encontrados = []
            
            # Procesar cada tabla
            for table_idx, table in enumerate(tables):
                logger.info(f"🔍 Procesando tabla {table_idx + 1}")
                
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    logger.info(f"   Filas en tabla {table_idx + 1}: {len(rows)}")
                    
                    # Procesar cada fila (saltar la primera que es header)
                    for row_idx, row in enumerate(rows[1:], 1):
                        try:
                            # Obtener celdas de la fila
                            cells = row.find_elements(By.TAG_NAME, "td")
                            
                            if len(cells) < 6:  # Debe tener al menos 6 celdas
                                continue
                            
                            logger.info(f"   🔍 Procesando fila {row_idx} con {len(cells)} celdas")
                            
                            # Extraer datos directamente de las celdas
                            consenso = self._extraer_consenso_de_celdas(cells, date, row_idx)
                            if consenso:
                                consensos_encontrados.append(consenso)
                                logger.info(f"✅ Consenso {row_idx}: {consenso['equipo_visitante']} @ {consenso['equipo_local']} - {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
                        
                        except Exception as e:
                            logger.warning(f"Error procesando fila {row_idx}: {e}")
                            continue
                
                except Exception as e:
                    logger.warning(f"Error procesando tabla {table_idx}: {e}")
                    continue
            
            logger.info(f"🎯 TOTAL CONSENSOS EXTRAÍDOS: {len(consensos_encontrados)}")
            return consensos_encontrados
            
        except Exception as e:
            logger.error(f"❌ Error durante scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("🔴 Driver cerrado")
    
    def _extraer_consenso_de_celdas(self, cells, date: str, row_num: int) -> Optional[Dict]:
        """Extraer consenso directamente de las celdas de la tabla de Selenium"""
        try:
            # Según el debug anterior, la estructura es:
            # Celda 0: "MLB\nTEAM1\nTEAM2"
            # Celda 1: "Date\nTime ET"  
            # Celda 2: "XX % Under\nYY % Over" (o viceversa)
            # Celda 3: "Total"
            # Celda 4: "Picks"
            # Celda 5: "Details"
            
            if len(cells) < 6:
                return None
            
            # CELDA 0: Equipos
            teams_text = cells[0].text.strip()
            logger.debug(f"   Debug fila {row_num} - Equipos: '{teams_text}'")
            
            # Extraer equipos (formato: "MLB\nNYY\nATL")
            lines = teams_text.split('\n')
            
            if len(lines) >= 3 and lines[0] == 'MLB':
                equipo_visitante = lines[1].strip()
                equipo_local = lines[2].strip()
            else:
                return None
            
            # CELDA 1: Fecha y hora
            datetime_text = cells[1].text.strip()
            logger.debug(f"   Debug fila {row_num} - Fecha/Hora: '{datetime_text}'")
            
            # Extraer hora (formato: "Sun. Jul. 20\n1:35 pm ET")
            hora_match = re.search(r'(\d{1,2}:\d{2}\s+[ap]m\s+ET)', datetime_text, re.IGNORECASE)
            hora_juego = hora_match.group(1) if hora_match else "N/A"
            
            # CELDA 2: Consenso (formato: "86 % Under\n14 % Over")
            consensus_text = cells[2].text.strip()
            logger.debug(f"   Debug fila {row_num} - Consenso: '{consensus_text}'")
            
            # Buscar porcentajes
            over_match = re.search(r'(\d{1,3})\s*%\s*Over', consensus_text, re.IGNORECASE)
            under_match = re.search(r'(\d{1,3})\s*%\s*Under', consensus_text, re.IGNORECASE)
            
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
            logger.debug(f"   Debug fila {row_num} - Total: '{total_text}'")
            
            try:
                total_line = float(total_text)
            except:
                total_line = 0.0
            
            # CELDA 4: Picks
            picks_text = cells[4].text.strip()
            logger.debug(f"   Debug fila {row_num} - Picks: '{picks_text}'")
            
            # Extraer números de picks - Formato esperado: "5\n1" (5 picks over, 1 pick under)
            pick_lines = picks_text.split('\n')
            pick_numbers = []
            
            # Extraer todos los números de las líneas
            for line in pick_lines:
                numbers = re.findall(r'\b(\d+)\b', line.strip())
                pick_numbers.extend([int(n) for n in numbers])
            
            logger.debug(f"   Debug fila {row_num} - Números extraídos de picks: {pick_numbers}")
            
            if len(pick_numbers) >= 2:
                picks_1 = pick_numbers[0]  # Primer número (generalmente el del consenso)
                picks_2 = pick_numbers[1]  # Segundo número (generalmente el contrario)
                total_picks = picks_1 + picks_2
            elif len(pick_numbers) == 1:
                # Si solo hay un número, es el total
                total_picks = pick_numbers[0]
                picks_1 = int(total_picks * (porcentaje_over / 100)) if porcentaje_over > 0 else 0
                picks_2 = total_picks - picks_1
            else:
                # Si no se pueden extraer números, estimar basado en porcentajes
                total_picks = 10  # Default conservador
                picks_1 = int(total_picks * (porcentaje_over / 100))
                picks_2 = total_picks - picks_1
            
            logger.debug(f"   Debug fila {row_num} - Picks calculados: {picks_1} over, {picks_2} under, {total_picks} total")
            
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
                'fecha_scraping': datetime.now(self.timezone).isoformat(),
                'deporte': 'MLB',
                'tipo_consenso': 'TOTAL',
                'consenso_over': porcentaje_over,
                'consenso_under': porcentaje_under,
                'url_fuente': self.base_url
            }
            
            return consenso
            
        except Exception as e:
            logger.warning(f"❌ Error extrayendo consenso de fila {row_num}: {e}")
            return None

    def _es_fila_consenso(self, texto: str) -> bool:
        """Determinar si una fila contiene datos de consenso - VERSIÓN CORREGIDA"""
        
        # Solo rechazar filas muy obvias que no sirven
        if len(texto.strip()) < 10:
            return False
        
        # Rechazar headers obvios
        if any(palabra in texto.lower() for palabra in ['javascript', 'function', 'window', 'document', 'script', 'style', 'matchup', 'date', 'consensus']):
            return False
        
        # Si contiene equipos MLB y porcentajes, probablemente es válida
        tiene_equipos = bool(re.search(r'MLB.*[A-Z]{2,3}.*[A-Z]{2,3}', texto))
        tiene_porcentaje = '%' in texto
        
        return tiene_equipos and tiene_porcentaje
    
    def _extraer_consenso(self, texto: str, fecha: str) -> Optional[Dict]:
        """Extraer datos de consenso - VERSIÓN CORREGIDA PARA COVERS.COM"""
        try:
            logger.debug(f"🔍 Analizando: {texto[:100]}...")
            
            # Separar las partes del texto (el texto viene todo junto de las celdas)
            # Formato típico: "MLB NYY ATL Sun. Jul. 20 1:35 pm ET 86 % Under 14 % Over 9.5 6 1 Details"
            
            # 1. EXTRAER EQUIPOS
            # Buscar patrón "MLB TEAM1 TEAM2"
            team_match = re.search(r'MLB\s+([A-Z]{2,3})\s+([A-Z]{2,3})', texto)
            if not team_match:
                return None
            
            equipo_visitante = team_match.group(1)
            equipo_local = team_match.group(2)
            
            # 2. EXTRAER HORA
            time_match = re.search(r'(\d{1,2}:\d{2}\s+[ap]m\s+ET)', texto, re.IGNORECASE)
            hora_juego = time_match.group(1) if time_match else "N/A"
            
            # 3. EXTRAER CONSENSO
            # Buscar patrones como "86 % Under" o "78 % Over"
            over_match = re.search(r'(\d{1,3})\s*%\s*Over', texto, re.IGNORECASE)
            under_match = re.search(r'(\d{1,3})\s*%\s*Under', texto, re.IGNORECASE)
            
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
            
            # 4. EXTRAER TOTAL LINE
            # Buscar números que puedan ser totales (entre 6.0 y 15.0)
            total_numbers = re.findall(r'\b(\d{1,2}(?:\.\d)?)\b', texto)
            total_line = 0.0
            
            for num_str in total_numbers:
                try:
                    num_val = float(num_str)
                    if 6.0 <= num_val <= 15.0:
                        total_line = num_val
                        break
                except ValueError:
                    continue
            
            # 5. EXTRAER PICKS
            # Los números pequeños al final probablemente son picks
            small_numbers = re.findall(r'\b(\d{1,2})\b', texto)
            pick_numbers = [int(n) for n in small_numbers if 1 <= int(n) <= 50 and int(n) != porcentaje_consenso]
            
            total_picks = sum(pick_numbers) if pick_numbers else 1
            
            # Construir objeto de consenso
            consenso = {
                'fecha_juego': fecha,
                'hora_juego': hora_juego,
                'equipo_visitante': equipo_visitante,
                'equipo_local': equipo_local,
                'direccion_consenso': direccion_consenso,
                'porcentaje_consenso': porcentaje_consenso,
                'porcentaje_over': porcentaje_over,
                'porcentaje_under': porcentaje_under,
                'consenso_over': porcentaje_over,  # Para compatibilidad
                'consenso_under': porcentaje_under,  # Para compatibilidad
                'total_line': total_line,
                'picks_over': pick_numbers[0] if pick_numbers and direccion_consenso == 'OVER' else 0,
                'picks_under': pick_numbers[1] if len(pick_numbers) > 1 and direccion_consenso == 'UNDER' else 0,
                'total_picks': total_picks,
                'num_experts': total_picks,
                'fecha_scraping': datetime.now(self.timezone).isoformat(),
                'deporte': 'MLB',
                'tipo_consenso': 'TOTAL',
                'raw_text': texto[:200]
            }
            
            logger.info(f"🎯 CONSENSO EXTRAÍDO: {equipo_visitante} @ {equipo_local} | "
                       f"{direccion_consenso} {porcentaje_consenso}% | Total: {total_line}")
            
            return consenso
            
        except Exception as e:
            logger.debug(f"❌ Error extrayendo consenso: {e}")
            return None

    def get_live_consensus(self) -> List[Dict]:
        """Obtiene consensos para partidos en vivo o próximos - Compatible con interfaz web"""
        try:
            logger.info("🔴 Obteniendo consensos en vivo con Selenium...")
            
            # Usar fecha actual
            today = datetime.now(self.timezone).strftime('%Y-%m-%d')
            consensos = self.scrape_mlb_consensus(today)
            
            logger.info(f"✅ Obtenidos {len(consensos)} consensos en vivo")
            return consensos
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo consensos en vivo: {e}")
            return []

    def close(self):
        """Cierra el driver si está activo"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔴 Driver Selenium cerrado")
            except:
                pass
            finally:
                self.driver = None

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def test_scraper():
    """Función de prueba"""
    print("🚀 PROBANDO SCRAPER SELENIUM MLB")
    print("="*60)
    
    scraper = MLBSeleniumScraper()
    
    try:
        consensos = scraper.scrape_mlb_consensus()
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   Consensos encontrados: {len(consensos)}")
        
        if consensos:
            print(f"\n🎯 CONSENSOS VÁLIDOS:")
            for i, consenso in enumerate(consensos):
                print(f"\n   {i+1}. {consenso['equipo_visitante']} @ {consenso['equipo_local']}")
                print(f"      Consenso: {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
                print(f"      Expertos: {consenso['num_experts']}")
                print(f"      Hora: {consenso.get('hora_juego', 'N/A')}")
                print(f"      Texto original: {consenso['raw_text']}")
        else:
            print(f"\n❌ No se encontraron consensos válidos")
            print(f"💡 Posibles causas:")
            print(f"   - No hay juegos MLB para hoy")
            print(f"   - La página cambió su estructura")
            print(f"   - Problema de conectividad")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper()
    input("\n⏸️ Presiona Enter para continuar...")
