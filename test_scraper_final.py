"""
TEST RÁPIDO DEL SCRAPER SELENIUM OPTIMIZADO
=========================================
"""

import sys
import os
sys.path.append('.')

from src.scraper.mlb_selenium_scraper import MLBSeleniumScraper
from datetime import datetime
import json

def test_scraper_optimizado():
    """Test rápido del scraper optimizado"""
    print("🚀 PROBANDO SCRAPER SELENIUM OPTIMIZADO")
    print("="*60)
    
    scraper = MLBSeleniumScraper()
    
    try:
        # Usar fecha actual
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 Scrapeando fecha: {today}")
        
        # Ejecutar scraping
        consensos = scraper.scrape_mlb_consensus(today)
        
        print(f"\n📊 RESULTADOS:")
        print(f"   Consensos encontrados: {len(consensos)}")
        
        if consensos:
            print(f"\n🎯 DATOS EXTRAÍDOS:")
            for i, consenso in enumerate(consensos[:3], 1):  # Solo los primeros 3
                print(f"\n   {i}. PARTIDO:")
                print(f"      Equipos: {consenso.get('equipo_visitante', 'N/A')} @ {consenso.get('equipo_local', 'N/A')}")
                print(f"      Fecha: {consenso.get('fecha_juego', 'N/A')}")
                print(f"      Hora: {consenso.get('hora_juego', 'N/A')}")
                print(f"      Consenso: {consenso.get('direccion_consenso', 'N/A')} {consenso.get('porcentaje_consenso', 0)}%")
                print(f"      Total Line: {consenso.get('total_line', 'N/A')}")
                print(f"      Picks Over: {consenso.get('picks_over', 'N/A')}")
                print(f"      Picks Under: {consenso.get('picks_under', 'N/A')}")
                print(f"      Total Picks: {consenso.get('total_picks', 'N/A')}")
                print(f"      Raw Text: {consenso.get('raw_text', '')[:100]}...")
            
            # Guardar datos completos para análisis
            with open('test_scraper_optimizado.json', 'w', encoding='utf-8') as f:
                json.dump(consensos, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Datos guardados en: test_scraper_optimizado.json")
            
            # Mostrar estadísticas
            datos_con_fecha = sum(1 for c in consensos if c.get('fecha_juego'))
            datos_con_hora = sum(1 for c in consensos if c.get('hora_juego'))
            datos_con_equipos = sum(1 for c in consensos if c.get('equipo_visitante') and c.get('equipo_local'))
            datos_con_consenso = sum(1 for c in consensos if c.get('porcentaje_consenso', 0) > 0)
            datos_con_picks = sum(1 for c in consensos if c.get('total_picks', 0) > 0)
            
            print(f"\n📈 ESTADÍSTICAS DE EXTRACCIÓN:")
            print(f"   Con fecha: {datos_con_fecha}/{len(consensos)} ({datos_con_fecha/len(consensos)*100:.1f}%)")
            print(f"   Con hora: {datos_con_hora}/{len(consensos)} ({datos_con_hora/len(consensos)*100:.1f}%)")
            print(f"   Con equipos: {datos_con_equipos}/{len(consensos)} ({datos_con_equipos/len(consensos)*100:.1f}%)")
            print(f"   Con consenso: {datos_con_consenso}/{len(consensos)} ({datos_con_consenso/len(consensos)*100:.1f}%)")
            print(f"   Con picks: {datos_con_picks}/{len(consensos)} ({datos_con_picks/len(consensos)*100:.1f}%)")
        else:
            print(f"\n❌ No se encontraron consensos")
            print(f"💡 Posibles causas:")
            print(f"   - No hay juegos MLB para hoy")
            print(f"   - Los criterios de filtrado son muy estrictos")
            print(f"   - La página cambió su estructura")
        
        print(f"\n" + "="*60)
        return consensos
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"🔍 Detalles:")
        traceback.print_exc()
        return []

if __name__ == "__main__":
    consensos = test_scraper_optimizado()
    input(f"\n⏸️ Presiona Enter para salir...")
