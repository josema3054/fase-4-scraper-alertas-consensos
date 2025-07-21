#!/usr/bin/env python3
"""
Script que fuerza la ejecución del scraper con logging DEBUG.
"""

import sys
import os
from datetime import datetime

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Limpiar cualquier caché de Python
sys.dont_write_bytecode = True

# Limpiar caché de módulos
modules_to_remove = [k for k in sys.modules.keys() if k.startswith('scraper') or k.startswith('utils')]
for module in modules_to_remove:
    del sys.modules[module]

try:
    # Importar después de limpiar caché
    from scraper.mlb_scraper import MLBScraper
    
    print("=== FORZANDO EJECUCIÓN DEL SCRAPER ===")
    print(f"Fecha y hora: {datetime.now()}")
    
    # Crear scraper
    scraper = MLBScraper()
    
    # Fecha de hoy
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Fecha de prueba: {today}")
    
    # Forzar scraping
    print("\n🔄 Ejecutando scraping...")
    consensos = scraper.scrape_mlb_consensus(today)
    
    print(f"\n📊 RESULTADO: {len(consensos)} consensos extraídos")
    
    if consensos:
        print("\n✅ ¡CONSENSOS ENCONTRADOS!")
        for i, c in enumerate(consensos, 1):
            print(f"\n{i}. {c['equipo_visitante']} @ {c['equipo_local']}")
            print(f"   Consenso: {c['direccion_consenso']} {c['porcentaje_consenso']}%")
            print(f"   Over/Under: {c['consenso_over']}% / {c['consenso_under']}%")
            print(f"   Total: {c['total_line']}")
            print(f"   Expertos: {c['num_experts']}")
            print(f"   Hora: {c['hora_partido']}")
    else:
        print("\n⚠️ NO SE EXTRAJERON CONSENSOS")
        print("📋 Revisa el log más reciente para detalles:")
        
        # Mostrar último log
        log_file = f"logs/scraper_{today}.log"
        if os.path.exists(log_file):
            print(f"   Archivo: {log_file}")
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print("\n📄 Últimas 10 líneas del log:")
                for line in lines[-10:]:
                    print(f"   {line.strip()}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print(f"\n⏰ Prueba completada: {datetime.now()}")
