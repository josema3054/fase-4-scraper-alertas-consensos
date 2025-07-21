"""
TEST RÁPIDO - VERIFICAR SI HAY DATOS DISPONIBLES
==============================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timedelta

def test_fechas_disponibles():
    print("🔍 VERIFICANDO FECHAS CON DATOS DISPONIBLES")
    print("="*50)
    
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Probar varias fechas
    fechas_probar = [
        datetime.now().strftime('%Y-%m-%d'),                    # Hoy
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Ayer
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),  # Mañana
    ]
    
    try:
        for fecha in fechas_probar:
            print(f"\n📅 PROBANDO FECHA: {fecha}")
            
            url = f"https://contests.covers.com/consensus/topoverunderconsensus/all/expert/{fecha}"
            driver.get(url)
            time.sleep(5)
            
            print(f"   Título: {driver.title}")
            
            # Buscar cualquier elemento que contenga equipos MLB conocidos
            equipos_mlb = ['NYY', 'BOS', 'LAD', 'SF', 'HOU', 'ATL', 'STL', 'CHI']
            
            for equipo in equipos_mlb:
                elementos = driver.find_elements(By.XPATH, f"//*[contains(text(), '{equipo}')]")
                if elementos:
                    print(f"   ✅ Encontrado equipo {equipo}: {len(elementos)} elementos")
                    for elem in elementos[:2]:
                        texto = elem.text.strip()
                        if len(texto) > 0:
                            print(f"      '{texto}'")
                    break
            else:
                print(f"   ❌ No se encontraron equipos MLB")
            
            # Buscar porcentajes
            elementos_porcentaje = driver.find_elements(By.XPATH, "//*[contains(text(), '%')]")
            if elementos_porcentaje:
                print(f"   📊 Porcentajes encontrados: {len(elementos_porcentaje)}")
                for elem in elementos_porcentaje[:3]:
                    texto = elem.text.strip()
                    if '%' in texto and len(texto) < 30:
                        print(f"      '{texto}'")
            
            # Si encontramos datos, usar esta fecha
            if elementos_porcentaje:
                print(f"   🎯 FECHA CON DATOS: {fecha}")
                break
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        driver.quit()
        print("🔴 Navegador cerrado")

if __name__ == "__main__":
    test_fechas_disponibles()
    input("Presiona Enter para continuar...")
