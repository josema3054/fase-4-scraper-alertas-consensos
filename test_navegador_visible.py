"""
TEST NAVEGADOR VISIBLE - Verificar que Selenium funciona y se ve el navegador
============================================================================
Script simple para comprobar que el navegador Chrome se abre y es visible
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

def test_navegador_visible():
    """Test básico del navegador visible"""
    driver = None
    
    try:
        print("🔧 Configurando Chrome driver VISIBLE...")
        
        chrome_options = Options()
        
        # Configuraciones básicas
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # IMPORTANTE: NO agregar --headless para que sea visible
        print("📱 Modo VISIBLE activado (no headless)")
        
        # Crear driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configuraciones
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(60)
        
        print("✅ Chrome driver creado correctamente")
        print("🌐 Navegador debería ser VISIBLE ahora")
        
        # Ir a la página de covers.com
        url = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"
        print(f"🚀 Navegando a: {url}")
        
        driver.get(url)
        
        print("⏳ Esperando 5 segundos para que cargue la página...")
        time.sleep(5)
        
        # Obtener título de la página
        title = driver.title
        print(f"📄 Título de la página: {title}")
        
        # Buscar tablas
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        if tables:
            # Ver la primera tabla
            first_table = tables[0]
            rows = first_table.find_elements(By.TAG_NAME, "tr")
            print(f"📋 Filas en la primera tabla: {len(rows)}")
            
            # Mostrar las primeras 3 filas
            for i, row in enumerate(rows[:3]):
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    cell_texts = [cell.text.strip() for cell in cells]
                    print(f"   Fila {i+1}: {cell_texts}")
        
        print("⏳ Esperando 10 segundos más para inspección manual...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if driver:
            print("🔚 Cerrando navegador...")
            driver.quit()

if __name__ == "__main__":
    print("🧪 INICIANDO TEST DE NAVEGADOR VISIBLE")
    print("=" * 50)
    
    success = test_navegador_visible()
    
    if success:
        print("\n✅ Test completado correctamente")
    else:
        print("\n❌ Test falló")
    
    input("\nPresiona Enter para salir...")
