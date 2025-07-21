"""
TEST DIRECTO - NAVEGADOR VISIBLE FORZADO
========================================
Garantiza que el navegador Chrome se abra de forma visible
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

def test_navegador_forzado():
    """Test que garantiza navegador visible"""
    print("🚀 TEST NAVEGADOR VISIBLE FORZADO")
    print("=" * 50)
    
    driver = None
    
    try:
        print("🔧 Configurando Chrome COMPLETAMENTE VISIBLE...")
        
        chrome_options = Options()
        
        # CONFIGURACIONES PARA MÁXIMA VISIBILIDAD
        chrome_options.add_argument('--start-maximized')  # Ventana maximizada
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # User agent normal
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # IMPORTANTE: NO headless - debe ser visible
        # chrome_options.add_argument('--headless')  # NUNCA agregar esto
        
        print("📱 Configuración: VISIBLE, MAXIMIZADA, SIN HEADLESS")
        
        # Crear driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome creado - debería estar VISIBLE ahora")
        
        # Ir a covers.com
        url = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"
        print(f"🌐 Navegando a: {url}")
        
        driver.get(url)
        
        print("⏳ Esperando 10 segundos - INSPECCIONA EL NAVEGADOR CHROME")
        time.sleep(10)
        
        # Obtener información básica
        title = driver.title
        print(f"📄 Título: {title}")
        
        # Buscar tablas
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        if tables:
            first_table = tables[0]
            rows = first_table.find_elements(By.TAG_NAME, "tr")
            print(f"📋 Filas en primera tabla: {len(rows)}")
        
        print("⏳ Esperando 15 segundos más para inspección...")
        time.sleep(15)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if driver:
            print("🔚 Cerrando navegador...")
            driver.quit()

if __name__ == "__main__":
    success = test_navegador_forzado()
    
    if success:
        print("\n✅ Test completado - ¿Viste el navegador Chrome?")
    else:
        print("\n❌ Test falló")
    
    input("\nPresiona Enter para salir...")
