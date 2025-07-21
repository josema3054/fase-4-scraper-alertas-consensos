"""
ANÁLISIS DE CONTENIDO HTML DE COVERS.COM
=======================================
Script para ver exactamente qué estructura tiene la página
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

def analizar_pagina():
    print("🔍 ANÁLISIS DE ESTRUCTURA HTML DE COVERS.COM")
    print("="*60)
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # SIN headless para ver qué pasa
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert/2025-07-20"
        print(f"🌐 Accediendo a: {url}")
        
        driver.get(url)
        time.sleep(10)  # Esperar más tiempo para asegurar carga completa
        
        print(f"📄 Título: {driver.title}")
        
        # Buscar todas las tablas
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📋 Tablas encontradas: {len(tables)}")
        
        for i, table in enumerate(tables, 1):
            print(f"\n🔍 TABLA {i}:")
            
            # Obtener todas las filas
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"   Filas: {len(rows)}")
            
            # Mostrar las primeras 5 filas con contenido
            for j, row in enumerate(rows[:8]):
                row_text = row.text.strip()
                if row_text:
                    print(f"   Fila {j}: '{row_text}'")
                    
                    # Si parece una fila con datos, mostrar las celdas
                    if j > 0 and len(row_text) > 20:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        print(f"      Celdas: {len(cells)}")
                        for k, cell in enumerate(cells):
                            cell_text = cell.text.strip()
                            if cell_text:
                                print(f"         Celda {k}: '{cell_text}'")
        
        # También buscar por clases específicas
        print(f"\n🔍 BÚSQUEDA POR CLASES:")
        
        # Buscar elementos con texto que contenga equipos
        elementos_equipos = driver.find_elements(By.XPATH, "//*[contains(text(), 'MLB') or contains(text(), 'NYY') or contains(text(), 'BOS') or contains(text(), 'LAD')]")
        print(f"   Elementos con equipos MLB: {len(elementos_equipos)}")
        
        for elem in elementos_equipos[:5]:
            print(f"      '{elem.text.strip()}'")
        
        # Buscar elementos con porcentajes
        elementos_porcentaje = driver.find_elements(By.XPATH, "//*[contains(text(), '%')]")
        print(f"   Elementos con %: {len(elementos_porcentaje)}")
        
        for elem in elementos_porcentaje[:5]:
            texto = elem.text.strip()
            if len(texto) < 50:  # Solo mostrar textos cortos
                print(f"      '{texto}'")
        
        print(f"\n💾 Para más análisis, la página quedará abierta por 30 segundos...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("🔴 Navegador cerrado")

if __name__ == "__main__":
    analizar_pagina()
