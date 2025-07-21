#!/usr/bin/env python3
"""
Script simple para probar el scraper mejorado manualmente.
Ejecuta: python test_simple.py
"""

import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from scraper.mlb_scraper import MLBScraper
    from datetime import datetime
    
    print("=== PRUEBA SIMPLE DEL SCRAPER ===")
    
    # Crear scraper
    scraper = MLBScraper()
    
    # Fecha de hoy
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Probando fecha: {today}")
    
    # Hacer scraping
    print("Ejecutando scraping...")
    consensos = scraper.scrape_mlb_consensus(today)
    
    print(f"\nResultado: {len(consensos)} consensos extraídos")
    
    for i, c in enumerate(consensos):
        print(f"{i+1}. {c['equipo_visitante']} @ {c['equipo_local']} - {c['direccion_consenso']} {c['porcentaje_consenso']}%")
    
    if len(consensos) > 0:
        print("\n✅ ÉXITO: El scraper funciona!")
    else:
        print("\n⚠️ NO SE EXTRAJERON CONSENSOS")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
