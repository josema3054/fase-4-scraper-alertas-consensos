"""
SCRAPER SUPER SIMPLE - MUESTRA TODO
==================================
Este scraper es extremadamente permisivo y muestra TODO lo que encuentra
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def scraper_super_simple():
    print("🔍 SCRAPER SUPER SIMPLE - MUESTRA TODO")
    print("="*50)
    print("   Este scraper te mostrará TODO lo que encuentra")
    print("="*50)
    
    # Configurar Chrome - SIN headless para ver
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # NO headless para ver el navegador
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://contests.covers.com/consensus/topoverunderconsensus/all/expert"
        print(f"🌐 Accediendo a: {url}")
        
        driver.get(url)
        print("⏳ Esperando carga...")
        time.sleep(8)
        
        print(f"📄 Título: {driver.title}")
        
        # Buscar TODAS las tablas
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📋 Tablas encontradas: {len(tables)}")
        
        datos_encontrados = []
        
        for i, table in enumerate(tables, 1):
            print(f"\n🔍 ANALIZANDO TABLA {i}:")
            
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"   Filas: {len(rows)}")
            
            for j, row in enumerate(rows):
                texto_fila = row.text.strip()
                
                if not texto_fila or len(texto_fila) < 5:
                    continue
                
                print(f"\n   Fila {j}: '{texto_fila}'")
                
                # Buscar patrones interesantes
                tiene_equipos = any(equipo in texto_fila.upper() for equipo in ['NYY', 'BOS', 'LAD', 'SF', 'HOU', 'ATL', 'STL', 'CHI', 'MLB'])
                tiene_porcentaje = '%' in texto_fila
                tiene_hora = ':' in texto_fila and ('pm' in texto_fila.lower() or 'am' in texto_fila.lower())
                tiene_numeros = any(char.isdigit() for char in texto_fila)
                
                indicadores = []
                if tiene_equipos: indicadores.append("EQUIPOS")
                if tiene_porcentaje: indicadores.append("%")
                if tiene_hora: indicadores.append("HORA")
                if tiene_numeros: indicadores.append("NUMS")
                
                if indicadores:
                    print(f"      → Indicadores: {', '.join(indicadores)}")
                    
                    # Si parece prometedor, guardar
                    if tiene_equipos or (tiene_porcentaje and tiene_numeros):
                        datos_encontrados.append({
                            'tabla': i,
                            'fila': j,
                            'texto': texto_fila,
                            'indicadores': indicadores
                        })
                        print(f"      ✅ GUARDADO como candidato")
        
        print(f"\n" + "="*50)
        print(f"📊 RESUMEN FINAL")
        print(f"="*50)
        print(f"   Candidatos encontrados: {len(datos_encontrados)}")
        
        if datos_encontrados:
            print(f"\n🎯 CANDIDATOS PROMETEDORES:")
            for i, dato in enumerate(datos_encontrados, 1):
                print(f"\n   {i}. Tabla {dato['tabla']}, Fila {dato['fila']}")
                print(f"      Indicadores: {', '.join(dato['indicadores'])}")
                print(f"      Texto: '{dato['texto']}'")
        else:
            print(f"\n❌ NO SE ENCONTRARON CANDIDATOS")
            print(f"   Posibles causas:")
            print(f"   • No hay partidos MLB programados")
            print(f"   • La página cambió su estructura")
            print(f"   • Los datos están en formato diferente")
        
        print(f"\n💡 El navegador quedará abierto 20 segundos para inspección manual...")
        time.sleep(20)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("🔴 Navegador cerrado")

if __name__ == "__main__":
    scraper_super_simple()
    input("Presiona Enter para continuar...")
