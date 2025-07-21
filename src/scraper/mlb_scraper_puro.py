"""
SCRAPER PURO - SOLO EXTRAE DATOS
===============================
El scraper solo se encarga de extraer TODOS los consensos disponibles.
Los filtros se aplican por separado cuando se necesiten.
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
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLBScraperPuro:
    """Scraper MLB - SOLO extrae datos, NO filtra"""
    
    def __init__(self):
        self.driver = None
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        self.base_url = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"
        
    def _setup_driver(self):
        """Configurar Chrome driver"""
        try:
            logger.info("🔧 Configurando Chrome driver...")
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Desactivar imágenes para velocidad
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Comentar para ver navegador
            chrome_options.add_argument('--headless')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ Chrome driver configurado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando driver: {e}")
            return False
    
    def extraer_todos_los_consensos(self, fecha: Optional[str] = None) -> List[Dict]:
        """
        EXTRAE TODOS LOS CONSENSOS SIN FILTRAR
        - Solo se encarga de obtener datos de covers.com
        - No aplica ningún filtro
        - Devuelve TODO lo que encuentra
        """
        
        if fecha is None:
            fecha = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        logger.info(f"🚀 EXTRAYENDO TODOS LOS CONSENSOS para {fecha}")
        logger.info("   (SIN filtros - datos puros)")
        
        if not self._setup_driver():
            return []
        
        try:
            url = f"{self.base_url}/{fecha}"
            logger.info(f"🌐 Accediendo a: {url}")
            
            self.driver.get(url)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(8)  # Esperar contenido dinámico
            logger.info("✅ Página cargada")
            
            # Buscar todas las tablas
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"📋 Tablas encontradas: {len(tables)}")
            
            if not tables:
                logger.warning("❌ No se encontraron tablas")
                return []
            
            todos_los_consensos = []
            
            # Procesar TODAS las tablas
            for table_idx, table in enumerate(tables):
                logger.info(f"🔍 Procesando tabla {table_idx + 1}")
                
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    logger.info(f"   Filas en tabla: {len(rows)}")
                    
                    for row_idx, row in enumerate(rows):
                        try:
                            row_text = row.text.strip()
                            
                            if not row_text or len(row_text) < 20:
                                continue
                            
                            # Solo verificar si parece ser una fila de datos
                            if self._parece_fila_de_consenso(row_text):
                                consenso = self._extraer_datos_completos(row_text, fecha)
                                if consenso:
                                    todos_los_consensos.append(consenso)
                                    logger.info(f"✅ Consenso extraído: {consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')} - {consenso.get('porcentaje_consenso', 0)}%")
                        
                        except Exception as e:
                            logger.debug(f"Error procesando fila {row_idx}: {e}")
                            continue
                
                except Exception as e:
                    logger.warning(f"Error procesando tabla {table_idx}: {e}")
                    continue
            
            logger.info(f"🎯 TOTAL EXTRAÍDO: {len(todos_los_consensos)} consensos")
            return todos_los_consensos
            
        except Exception as e:
            logger.error(f"❌ Error durante extracción: {e}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("🔴 Driver cerrado")
    
    def _parece_fila_de_consenso(self, texto: str) -> bool:
        """Verificar si parece una fila de consenso (criterios MUY amplios)"""
        
        texto_lower = texto.lower()
        
        # Criterios básicos - MUY permisivos
        tiene_equipos = bool(re.search(r'[A-Z]{2,4}', texto))  # Cualquier sigla
        tiene_porcentaje = '%' in texto
        tiene_numeros = bool(re.search(r'\d', texto))
        
        # Excluir solo headers obvios
        es_header_obvio = any(word in texto_lower for word in ['matchup', 'consensus', 'total', 'picks', 'header'])
        
        # Si tiene equipos O porcentajes O números, y no es header obvio
        parece_valido = (tiene_equipos or tiene_porcentaje or tiene_numeros) and not es_header_obvio
        
        if parece_valido:
            logger.debug(f"✅ Fila candidata: {texto[:60]}...")
        
        return parece_valido
    
    def _extraer_datos_completos(self, texto: str, fecha: str) -> Optional[Dict]:
        """
        EXTRAE TODOS LOS DATOS POSIBLES SIN FILTROS
        - Intenta extraer todo lo que puede
        - No valida si cumple criterios mínimos
        - Devuelve el consenso aunque esté incompleto
        """
        try:
            logger.debug(f"🔍 Extrayendo de: {texto}")
            
            # Estructura base del consenso
            consenso = {
                # Identificación
                'id_unico': self._generar_id_unico(texto),
                'fecha_juego': fecha,
                'fecha_extraccion': datetime.now(self.timezone).isoformat(),
                'texto_original': texto[:300],  # Para debugging
                
                # Equipos
                'equipo_visitante': None,
                'equipo_local': None,
                'partido_completo': None,
                
                # Horario
                'hora_juego': None,
                'fecha_partido_formateada': None,
                
                # Consenso
                'direccion_consenso': None,  # OVER/UNDER
                'porcentaje_consenso': 0,
                'porcentaje_over': 0,
                'porcentaje_under': 0,
                
                # Total line
                'total_line': None,
                
                # Expertos/Picks
                'picks_over': 0,
                'picks_under': 0,
                'total_picks': 0,
                'num_experts': 0,
                
                # Metadata
                'deporte': 'MLB',
                'fuente': 'covers.com',
                'estado_extraccion': 'sin_filtrar',
                'campos_extraidos': []
            }
            
            # EXTRACCIÓN 1: EQUIPOS
            equipos_extraidos = self._extraer_equipos(texto)
            if equipos_extraidos:
                consenso['equipo_visitante'] = equipos_extraidos['visitante']
                consenso['equipo_local'] = equipos_extraidos['local']
                consenso['partido_completo'] = f"{equipos_extraidos['visitante']} @ {equipos_extraidos['local']}"
                consenso['campos_extraidos'].append('equipos')
            
            # EXTRACCIÓN 2: FECHA Y HORA
            fecha_hora = self._extraer_fecha_hora(texto)
            if fecha_hora:
                consenso['fecha_partido_formateada'] = fecha_hora.get('fecha')
                consenso['hora_juego'] = fecha_hora.get('hora')
                consenso['campos_extraidos'].append('fecha_hora')
            
            # EXTRACCIÓN 3: CONSENSO OVER/UNDER
            consenso_data = self._extraer_consenso_over_under(texto)
            if consenso_data:
                consenso.update(consenso_data)
                consenso['campos_extraidos'].append('consenso')
            
            # EXTRACCIÓN 4: TOTAL LINE
            total_line = self._extraer_total_line(texto)
            if total_line:
                consenso['total_line'] = total_line
                consenso['campos_extraidos'].append('total_line')
            
            # EXTRACCIÓN 5: PICKS Y EXPERTOS
            picks_data = self._extraer_picks_expertos(texto)
            if picks_data:
                consenso.update(picks_data)
                consenso['campos_extraidos'].append('picks')
            
            # Determinar completitud
            campos_importantes = ['equipos', 'consenso', 'picks']
            campos_completos = [campo for campo in campos_importantes if campo in consenso['campos_extraidos']]
            consenso['completitud'] = f"{len(campos_completos)}/{len(campos_importantes)}"
            
            # SIEMPRE devolver el consenso, aunque esté incompleto
            if len(consenso['campos_extraidos']) > 0:
                logger.info(f"📊 Consenso extraído ({consenso['completitud']}): {consenso.get('partido_completo', 'Equipos N/A')} - {consenso.get('direccion_consenso', '?')} {consenso.get('porcentaje_consenso', 0)}%")
                return consenso
            else:
                logger.debug(f"❌ No se extrajo ningún campo válido")
                return None
                
        except Exception as e:
            logger.debug(f"❌ Error extrayendo datos: {e}")
            return None
    
    def _generar_id_unico(self, texto: str) -> str:
        """Generar ID único basado en el texto"""
        import hashlib
        return hashlib.md5(texto[:100].encode()).hexdigest()[:12]
    
    def _extraer_equipos(self, texto: str) -> Optional[Dict]:
        """Extraer equipos del texto"""
        patrones_equipos = [
            r'([A-Z]{2,3})\s+([A-Z]{2,3})',  # STL AZ
            r'MLB\s+([A-Z]{2,3})\s+([A-Z]{2,3})',  # MLB STL AZ
            r'([A-Z]{2,4})\s*@\s*([A-Z]{2,4})',  # STL @ AZ
        ]
        
        for patron in patrones_equipos:
            match = re.search(patron, texto)
            if match:
                return {
                    'visitante': match.group(1),
                    'local': match.group(2)
                }
        return None
    
    def _extraer_fecha_hora(self, texto: str) -> Optional[Dict]:
        """Extraer fecha y hora del partido"""
        resultado = {}
        
        # Patrones de fecha
        patrones_fecha = [
            r'((?:Sun|Mon|Tue|Wed|Thu|Fri|Sat)\.\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.\s+\d{1,2})',
            r'(\w{3}\.\s+\w{3}\.\s+\d{1,2})',
        ]
        
        for patron in patrones_fecha:
            match = re.search(patron, texto)
            if match:
                resultado['fecha'] = match.group(1)
                break
        
        # Patrones de hora
        patrones_hora = [
            r'(\d{1,2}:\d{2}\s+[ap]m\s+ET)',
            r'(\d{1,2}:\d{2}\s*[ap]m)',
        ]
        
        for patron in patrones_hora:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                resultado['hora'] = match.group(1)
                break
        
        return resultado if resultado else None
    
    def _extraer_consenso_over_under(self, texto: str) -> Optional[Dict]:
        """Extraer datos de consenso Over/Under"""
        patrones_consenso = [
            r'(\d{1,3})\s*%\s*(Over)',
            r'(\d{1,3})\s*%\s*(Under)',
        ]
        
        for patron in patrones_consenso:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                porcentaje = int(match.group(1))
                direccion = match.group(2).upper()
                
                resultado = {
                    'porcentaje_consenso': porcentaje,
                    'direccion_consenso': direccion
                }
                
                if direccion == 'OVER':
                    resultado['porcentaje_over'] = porcentaje
                    resultado['porcentaje_under'] = 100 - porcentaje
                else:
                    resultado['porcentaje_under'] = porcentaje
                    resultado['porcentaje_over'] = 100 - porcentaje
                
                return resultado
        
        return None
    
    def _extraer_total_line(self, texto: str) -> Optional[float]:
        """Extraer la línea del total"""
        # Buscar números que puedan ser totales MLB (6-15)
        numeros = re.findall(r'\b(\d{1,2}(?:\.\d)?)\b', texto)
        for num_str in numeros:
            try:
                num_val = float(num_str)
                if 6.0 <= num_val <= 15.0:
                    return num_val
            except ValueError:
                continue
        return None
    
    def _extraer_picks_expertos(self, texto: str) -> Optional[Dict]:
        """Extraer datos de picks y expertos"""
        # Buscar números pequeños que puedan ser picks
        numeros = re.findall(r'\b(\d{1,2})\b', texto)
        numeros_validos = [int(num) for num in numeros if 1 <= int(num) <= 50]
        
        if len(numeros_validos) >= 2:
            return {
                'picks_over': numeros_validos[0],
                'picks_under': numeros_validos[1],
                'total_picks': numeros_validos[0] + numeros_validos[1],
                'num_experts': numeros_validos[0] + numeros_validos[1]
            }
        elif len(numeros_validos) == 1:
            return {
                'picks_over': 0,
                'picks_under': 0,
                'total_picks': numeros_validos[0],
                'num_experts': numeros_validos[0]
            }
        
        return None
    
    def obtener_consensos_del_dia(self, fecha: Optional[str] = None) -> List[Dict]:
        """Método principal - obtiene TODOS los consensos del día"""
        return self.extraer_todos_los_consensos(fecha)
    
    def close(self):
        """Cerrar driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def test_scraper_puro():
    """Probar el scraper puro"""
    print("🧪 PROBANDO SCRAPER PURO (SIN FILTROS)")
    print("=" * 60)
    
    scraper = MLBScraperPuro()
    
    try:
        # Extraer todos los consensos
        todos_consensos = scraper.obtener_consensos_del_dia()
        
        print(f"\n📊 RESULTADO:")
        print(f"   Total consensos extraídos: {len(todos_consensos)}")
        
        if todos_consensos:
            print(f"\n📋 CONSENSOS ENCONTRADOS (SIN FILTRAR):")
            
            for i, consenso in enumerate(todos_consensos, 1):
                completitud = consenso.get('completitud', '?/?')
                partido = consenso.get('partido_completo', 'Equipos N/A')
                direccion = consenso.get('direccion_consenso', '?')
                porcentaje = consenso.get('porcentaje_consenso', 0)
                picks = consenso.get('total_picks', 0)
                hora = consenso.get('hora_juego', 'N/A')
                
                print(f"\n   {i}. [{completitud}] {partido}")
                print(f"      Consenso: {direccion} {porcentaje}%")
                print(f"      Picks: {picks} | Hora: {hora}")
                
                # Mostrar campos extraídos
                campos = ', '.join(consenso.get('campos_extraidos', []))
                print(f"      Campos: {campos}")
            
            # Guardar todos los datos
            with open('datos_puros_scraper.json', 'w', encoding='utf-8') as f:
                json.dump(todos_consensos, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Datos guardados en: datos_puros_scraper.json")
            
            # Estadísticas
            total_completos = sum(1 for c in todos_consensos if c.get('completitud') == '3/3')
            total_parciales = len(todos_consensos) - total_completos
            
            print(f"\n📈 ESTADÍSTICAS:")
            print(f"   Consensos completos (3/3): {total_completos}")
            print(f"   Consensos parciales: {total_parciales}")
            print(f"   Total extraído: {len(todos_consensos)}")
        else:
            print(f"\n❌ No se encontraron consensos")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper_puro()
    input("\n⏸️ Presiona Enter para continuar...")
