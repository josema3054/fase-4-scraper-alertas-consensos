"""
PRUEBA CON FECHA ESPECÍFICA QUE TENGA DATOS
==========================================
Usar una fecha que sabemos que tiene partidos MLB
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def test_fecha_con_datos():
    print("🏈 PROBANDO CON FECHA QUE TIENE DATOS MLB")
    print("="*50)
    
    from src.scraper.mlb_selenium_scraper import MLBSeleniumScraper
    
    # Usar fecha de temporada MLB (julio típicamente tiene muchos juegos)
    # O usar fecha sin especificar para que use "hoy" por defecto
    fechas_probar = [
        "2024-07-15",  # Fecha de temporada pasada
        "2024-08-01",  # Otro día con muchos juegos
        None           # Fecha actual (covers.com decide)
    ]
    
    scraper = MLBSeleniumScraper()
    
    for fecha in fechas_probar:
        print(f"\n📅 PROBANDO FECHA: {fecha or 'ACTUAL'}")
        
        try:
            consensos = scraper.scrape_mlb_consensus(fecha)
            
            print(f"✅ Resultado: {len(consensos)} consensos encontrados")
            
            if consensos:
                print("🎯 ¡DATOS ENCONTRADOS!")
                for i, consenso in enumerate(consensos[:3], 1):
                    partido = f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}"
                    direccion = consenso.get('direccion_consenso', '?')
                    porcentaje = consenso.get('porcentaje_consenso', 0)
                    
                    print(f"   {i}. {partido} - {direccion} {porcentaje}%")
                
                # Si encontramos datos, ya no probamos más fechas
                break
            else:
                print("⚠️ Sin datos en esta fecha")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    else:
        print(f"\n💡 SUGERENCIAS:")
        print(f"   1. Revisar si es temporada MLB activa")
        print(f"   2. Verificar manualmente covers.com en el navegador")
        print(f"   3. Ajustar los filtros de extracción")

if __name__ == "__main__":
    test_fecha_con_datos()
    input("Presiona Enter...")
