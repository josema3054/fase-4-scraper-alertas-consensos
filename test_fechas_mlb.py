"""
TEST CON FECHAS CONOCIDAS QUE TIENEN DATOS MLB
=============================================
Probar con fechas específicas de la temporada MLB 2024/2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_fechas_con_datos():
    """Probar con fechas conocidas que tienen datos"""
    driver = None
    
    # Fechas a probar (formato YYYY-MM-DD)
    fechas_test = [
        "2024-07-15",  # Temporada MLB 2024
        "2024-08-01",  # Plena temporada
        "2024-09-15",  # Final de temporada regular
        "2024-06-20",  # Temporada alta
        "2025-07-19",  # Ayer
    ]
    
    try:
        print("🔧 Configurando Chrome VISIBLE...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome configurado correctamente")
        
        for fecha in fechas_test:
            print(f"\\n🗓️  PROBANDO FECHA: {fecha}")
            print("-" * 40)
            
            url = f"https://contests.covers.com/consensus/topoverunderconsensus/all/expert/{fecha}"
            print(f"🚀 URL: {url}")
            
            try:
                driver.get(url)
                
                # Esperar que cargue
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(5)
                
                title = driver.title
                print(f"📄 Título: {title}")
                
                # Buscar tablas
                tables = driver.find_elements(By.TAG_NAME, "table")
                print(f"📊 Tablas encontradas: {len(tables)}")
                
                # Analizar contenido
                body_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Contar indicadores de datos
                over_count = body_text.upper().count('OVER')
                under_count = body_text.upper().count('UNDER')
                percent_count = body_text.count('%')
                mlb_count = body_text.upper().count('MLB')
                
                print(f"   'Over': {over_count} ocurrencias")
                print(f"   'Under': {under_count} ocurrencias")
                print(f"   '%': {percent_count} ocurrencias")
                print(f"   'MLB': {mlb_count} ocurrencias")
                
                # Buscar líneas con consensos
                lines_with_consensus = []
                for line in body_text.split('\\n'):
                    line = line.strip()
                    if (('%' in line and ('over' in line.lower() or 'under' in line.lower())) or
                        (len(line) > 20 and any(word in line.upper() for word in ['STL', 'NYY', 'LAD', 'BOS', 'CHI']))):
                        lines_with_consensus.append(line)
                
                print(f"   Líneas con consensos: {len(lines_with_consensus)}")
                
                if lines_with_consensus:
                    print("   Ejemplos:")
                    for line in lines_with_consensus[:3]:
                        print(f"      {line[:80]}...")
                    
                    # ¡Esta fecha tiene datos!
                    print(f"\\n🎯 FECHA {fecha} TIENE DATOS - USAR PARA PRUEBAS")
                    break
                else:
                    print(f"   ❌ Sin datos útiles para {fecha}")
                    
            except Exception as e:
                print(f"   ❌ Error con fecha {fecha}: {e}")
                continue
                
            # Pausa entre fechas
            time.sleep(2)
        
        print("\\n📋 RESUMEN:")
        print("Si encontramos una fecha con datos, úsala en el scraper principal.")
        print("Si no hay datos, puede ser que:")
        print("1. La temporada MLB no esté activa")
        print("2. covers.com cambió su estructura")
        print("3. Necesitamos autenticación o cookies")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
        
    finally:
        if driver:
            print("\\n⏸️  Manteniendo navegador abierto para inspección...")
            input("Presiona Enter para cerrar el navegador...")
            driver.quit()

if __name__ == "__main__":
    print("📅 INICIANDO TEST DE FECHAS CON DATOS MLB")
    print("=" * 50)
    
    success = test_fechas_con_datos()
    
    if success:
        print("\\n✅ Test completado")
    else:
        print("\\n❌ Test falló")
