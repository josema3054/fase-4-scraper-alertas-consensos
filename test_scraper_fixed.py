#!/usr/bin/env python3
"""
PRUEBA DIRECTA DEL SCRAPER MLB CON URL CORREGIDA
==============================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.mlb_scraper import MLBScraper
from datetime import datetime

def test_scraper():
    print("🚀 PROBANDO SCRAPER MLB CON URL CORREGIDA")
    print("="*50)
    
    # Fecha actual
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Fecha: {today}")
    
    try:
        # Crear instancia del scraper
        scraper = MLBScraper()
        print(f"🌐 URL base configurada: {scraper.base_url}")
        
        # Ejecutar scraping
        print("\n🔍 Ejecutando scraping...")
        consensos = scraper.scrape_mlb_consensus()
        
        print(f"\n📊 RESULTADOS:")
        print(f"   Total consensos encontrados: {len(consensos)}")
        
        if consensos:
            print("\n🎯 CONSENSOS EXTRAÍDOS:")
            for i, consenso in enumerate(consensos):
                print(f"\n   {i+1}. {consenso.get('equipo_visitante', 'N/A')} @ {consenso.get('equipo_local', 'N/A')}")
                print(f"      Consenso: {consenso.get('direccion_consenso', 'N/A')} {consenso.get('porcentaje_consenso', 'N/A')}%")
                print(f"      Expertos: {consenso.get('num_experts', 'N/A')}")
                print(f"      Hora: {consenso.get('hora_juego', 'N/A')}")
        else:
            print("\n❌ No se encontraron consensos")
            print("💡 Posibles causas:")
            print("   - No hay juegos para la fecha actual")
            print("   - La estructura de la página cambió")
            print("   - Problema de conectividad")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        print("\n📋 Detalles del error:")
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper()
    input("\n⏸️ Presiona Enter para continuar...")
