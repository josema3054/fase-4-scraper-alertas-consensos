"""
TEST CON FECHAS ESPECÍFICAS - NAVEGADOR VISIBLE
===============================================
Probar el scraper con fechas específicas que pueden tener datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper.mlb_selenium_scraper import MLBSeleniumScraper
from datetime import datetime, timedelta
import time

def test_fechas_especificas():
    """Test con fechas específicas"""
    print("🚀 TEST CON FECHAS ESPECÍFICAS - NAVEGADOR VISIBLE")
    print("=" * 60)
    
    # Fechas de prueba - períodos típicos de temporada MLB
    fechas_prueba = [
        "2024-07-15",  # Temporada regular MLB
        "2024-08-01",  # Temporada regular MLB
        "2024-06-15",  # Temporada regular MLB
        datetime.now().strftime('%Y-%m-%d'),  # Hoy
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Ayer
    ]
    
    scraper = MLBSeleniumScraper()
    
    for fecha in fechas_prueba:
        print(f"\n🗓️  PROBANDO FECHA: {fecha}")
        print("-" * 40)
        
        try:
            print(f"🚀 Iniciando scraping para {fecha}...")
            print("   ¡Observa el navegador Chrome que se abre!")
            
            consensos = scraper.scrape_mlb_consensus(fecha)
            
            print(f"✅ Scraping completado: {len(consensos)} consensos")
            
            if consensos:
                print(f"🎯 DATOS ENCONTRADOS para {fecha}:")
                for i, consenso in enumerate(consensos[:3]):  # Solo mostrar primeros 3
                    print(f"   {i+1}. {consenso.get('equipo_visitante', 'N/A')} @ {consenso.get('equipo_local', 'N/A')}")
                    print(f"      {consenso.get('direccion_consenso', 'N/A')} {consenso.get('porcentaje_consenso', 0)}%")
                
                print(f"\n🎉 ¡ÉXITO! Encontrados datos para {fecha}")
                break  # Si encontramos datos, parar aquí
            else:
                print(f"⚠️ No hay datos para {fecha}")
                
        except Exception as e:
            print(f"❌ Error con fecha {fecha}: {e}")
            
        # Pausa entre fechas
        print("⏳ Esperando 3 segundos antes de la siguiente fecha...")
        time.sleep(3)
    
    print("\n🔚 Test de fechas completado")

if __name__ == "__main__":
    test_fechas_especificas()
    input("\nPresiona Enter para salir...")
