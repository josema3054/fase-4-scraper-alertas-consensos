#!/usr/bin/env python3
"""
Prueba directa del scraper mejorado para validar extracción de consensos.
"""

import sys
import os
from datetime import datetime

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scraper.mlb_scraper import MLBScraper
from utils.logger import logger

def test_improved_scraper():
    """Prueba el scraper mejorado con logging detallado"""
    
    print("=== PRUEBA DEL SCRAPER MEJORADO ===")
    
    try:
        # Inicializar scraper
        scraper = MLBScraper()
        
        # Usar fecha actual
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"Fecha de prueba: {today}")
        
        # Hacer scraping con logging detallado
        print("\n--- Iniciando scraping ---")
        consensos = scraper.scrape_mlb_consensus(today)
        
        print(f"\n--- Resultados ---")
        print(f"Consensos extraídos: {len(consensos)}")
        
        if consensos:
            print("\n--- Detalles de consensos válidos ---")
            for i, consenso in enumerate(consensos, 1):
                print(f"\nConsenso {i}:")
                print(f"  Equipos: {consenso['equipo_visitante']} @ {consenso['equipo_local']}")
                print(f"  Consenso: {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
                print(f"  Over/Under: {consenso['consenso_over']}% / {consenso['consenso_under']}%")
                print(f"  Total: {consenso['total_line']}")
                print(f"  Expertos: {consenso['num_experts']}")
                print(f"  Hora: {consenso['hora_partido']}")
        else:
            print("\n❌ No se extrajeron consensos válidos")
            
        return len(consensos) > 0
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_improved_scraper()
    
    if success:
        print("\n✅ Prueba exitosa: El scraper mejorado está funcionando")
    else:
        print("\n❌ Prueba fallida: Necesita más ajustes")
        
        # Mostrar logs recientes
        print("\n--- Logs recientes ---")
        log_file = "logs/scraper_" + datetime.now().strftime('%Y-%m-%d') + ".log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-20:]:  # Últimas 20 líneas
                    print(line.strip())
