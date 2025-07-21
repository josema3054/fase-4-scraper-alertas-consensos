"""
PRUEBA DIRECTA DEL SCRAPER SELENIUM - NAVEGADOR VISIBLE
=======================================================
Test directo para ver el navegador en acción y debug
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper.mlb_selenium_scraper import MLBSeleniumScraper
import time

def test_scraper_visible():
    """Test del scraper con navegador visible"""
    print("🚀 INICIANDO PRUEBA SCRAPER SELENIUM VISIBLE")
    print("=" * 60)
    
    scraper = MLBSeleniumScraper()
    
    try:
        print("📅 Scrapeando para fecha actual...")
        consensos = scraper.scrape_mlb_consensus()
        
        print(f"✅ Scraping completado: {len(consensos)} consensos encontrados")
        
        if consensos:
            print("\n📊 CONSENSOS ENCONTRADOS:")
            for i, consenso in enumerate(consensos):
                print(f"\n{i+1}. {consenso.get('equipo_visitante', 'N/A')} @ {consenso.get('equipo_local', 'N/A')}")
                print(f"   Consenso: {consenso.get('direccion_consenso', 'N/A')} {consenso.get('porcentaje_consenso', 0)}%")
                print(f"   Expertos: {consenso.get('num_experts', 0)}")
                print(f"   Hora: {consenso.get('hora_partido', 'N/A')}")
        else:
            print("\n⚠️ No se encontraron consensos")
            print("   Posibles causas:")
            print("   • No hay partidos MLB para hoy")
            print("   • Problemas con el scraping")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el scraper: {e}")
        return False
    
    finally:
        # El driver se cierra automáticamente
        print("🔚 Test finalizado")

if __name__ == "__main__":
    success = test_scraper_visible()
    
    if success:
        print("\n✅ Test completado")
    else:
        print("\n❌ Test falló")
    
    input("\nPresiona Enter para salir...")
