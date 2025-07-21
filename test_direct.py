"""
Test directo del scraper con logs detallados
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_direct():
    print("🔍 TEST DIRECTO DEL SCRAPER")
    print("=" * 50)
    
    try:
        from src.scraper.mlb_scraper import MLBScraper
        from datetime import datetime
        import pytz
        
        timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        current_date = datetime.now(timezone).strftime('%Y-%m-%d')
        
        print(f"📅 Fecha de scraping: {current_date}")
        print()
        
        scraper = MLBScraper()
        consensos = scraper.scrape_mlb_consensus(current_date)
        
        print(f"📊 Total de consensos encontrados: {len(consensos)}")
        print()
        
        if consensos:
            for i, consenso in enumerate(consensos, 1):
                print(f"🏈 PARTIDO {i}:")
                print(f"   Equipos: {consenso.get('equipo_visitante', 'N/A')} @ {consenso.get('equipo_local', 'N/A')}")
                print(f"   Over: {consenso.get('consenso_over', 0)}%")
                print(f"   Under: {consenso.get('consenso_under', 0)}%")
                print(f"   Consenso principal: {consenso.get('direccion_consenso', 'N/A')} {consenso.get('porcentaje_consenso', 0)}%")
                print(f"   Expertos: {consenso.get('num_experts', 0)}")
                print(f"   Hora: {consenso.get('hora_partido', 'N/A')}")
                print()
        else:
            print("❌ No se encontraron consensos")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()
