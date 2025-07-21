#!/usr/bin/env python3
"""
Script de prueba del scraper mejorado con logging a archivo.
"""

import sys
import os
from datetime import datetime

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_scraper_with_logging():
    """Prueba el scraper y guarda resultados en archivo"""
    
    # Crear archivo de resultados
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    result_file = f"test_results_{timestamp}.txt"
    
    def log_to_file(message):
        """Escribe mensaje tanto en consola como en archivo"""
        print(message)
        with open(result_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    
    try:
        log_to_file("=== PRUEBA DEL SCRAPER MEJORADO ===")
        log_to_file(f"Fecha y hora: {datetime.now()}")
        log_to_file("")
        
        # Importar módulos
        from scraper.mlb_scraper import MLBScraper
        log_to_file("✅ Módulos importados correctamente")
        
        # Crear scraper
        scraper = MLBScraper()
        log_to_file("✅ Scraper inicializado")
        
        # Fecha de prueba
        today = datetime.now().strftime('%Y-%m-%d')
        log_to_file(f"Fecha de prueba: {today}")
        log_to_file("")
        
        # Ejecutar scraping
        log_to_file("🔄 Iniciando scraping...")
        consensos = scraper.scrape_mlb_consensus(today)
        
        log_to_file("")
        log_to_file("=== RESULTADOS ===")
        log_to_file(f"Consensos extraídos: {len(consensos)}")
        log_to_file("")
        
        if consensos:
            log_to_file("✅ ¡ÉXITO! Consensos válidos encontrados:")
            log_to_file("")
            
            for i, c in enumerate(consensos, 1):
                log_to_file(f"{i}. {c['equipo_visitante']} @ {c['equipo_local']}")
                log_to_file(f"   Consenso: {c['direccion_consenso']} {c['porcentaje_consenso']}%")
                log_to_file(f"   Over/Under: {c['consenso_over']}% / {c['consenso_under']}%")
                log_to_file(f"   Total: {c['total_line']}")
                log_to_file(f"   Expertos: {c['num_experts']}")
                log_to_file(f"   Hora: {c['hora_partido']}")
                log_to_file("")
                
            log_to_file("🎯 CONCLUSIÓN: El scraper mejorado está funcionando correctamente!")
            return True
        else:
            log_to_file("⚠️ NO SE EXTRAJERON CONSENSOS VÁLIDOS")
            log_to_file("")
            log_to_file("Posibles causas:")
            log_to_file("1. No hay partidos programados para hoy")
            log_to_file("2. La estructura de la página cambió")
            log_to_file("3. Los filtros son demasiado restrictivos")
            log_to_file("")
            log_to_file("Revisa los logs detallados en la carpeta 'logs' para más información")
            return False
            
    except Exception as e:
        log_to_file(f"❌ ERROR DURANTE LA PRUEBA: {e}")
        import traceback
        log_to_file("")
        log_to_file("=== TRACEBACK COMPLETO ===")
        log_to_file(traceback.format_exc())
        return False
    
    finally:
        log_to_file("")
        log_to_file(f"=== Archivo de resultados guardado en: {result_file} ===")

if __name__ == "__main__":
    success = test_scraper_with_logging()
    
    if success:
        print("\n🎉 ¡La prueba fue exitosa!")
    else:
        print("\n🔧 La prueba necesita más ajustes")
        
    print("\n📄 Revisa el archivo de resultados generado para detalles completos")
