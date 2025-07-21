"""
PRUEBA RÁPIDA DEL SISTEMA SCRAPER ROBUSTO
========================================
Script para probar el sistema completo con filtros variables y reintentos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.scraper.sistema_scraper_robusto import ScraperRobusto, ConfiguracionFiltros
import json
from datetime import datetime

def main():
    print("🚀 PRUEBA RÁPIDA SISTEMA SCRAPER ROBUSTO")
    print("=" * 60)
    
    try:
        # 1. INICIALIZAR SISTEMA
        print("\n📋 1. INICIALIZANDO SISTEMA...")
        sistema = ScraperRobusto()
        
        # 2. MOSTRAR CONFIGURACIÓN ACTUAL
        print("\n📊 2. CONFIGURACIÓN ACTUAL:")
        config = sistema.obtener_resumen_configuracion()
        for seccion, datos in config.items():
            print(f"\n   🔧 {seccion.upper()}:")
            for key, value in datos.items():
                print(f"      • {key}: {value}")
        
        # 3. CONFIGURAR FILTROS DE PRUEBA (MÁS PERMISIVOS PARA TESTING)
        print("\n⚙️ 3. CONFIGURANDO FILTROS DE PRUEBA...")
        sistema.actualizar_configuracion(
            umbral_minimo=60,  # Más permisivo para testing
            expertos_minimos=10,
            picks_minimos=5,
            direccion_permitida=['OVER', 'UNDER']
        )
        
        # 4. EJECUTAR SCRAPING DE PRUEBA
        print("\n🔍 4. EJECUTANDO SCRAPING CON REINTENTOS...")
        print("   (Esto puede tomar varios minutos si hay reintentos)")
        
        resultado = sistema.ejecutar_ciclo_completo()
        
        # 5. MOSTRAR RESULTADOS
        print("\n📈 5. RESULTADOS FINALES:")
        print("   " + "="*50)
        
        if resultado['exito']:
            print(f"   ✅ ÉXITO")
            print(f"   📊 Consensos encontrados: {resultado['consensos_encontrados']}")
            print(f"   📢 Alertas enviadas: {resultado['alertas_enviadas']}")
            print(f"   ⏱️  Tiempo procesamiento: {resultado['tiempo_procesamiento']} seg")
            
            if resultado['alertas_enviadas'] > 0:
                print(f"\n   🎯 ¡SE ENVIARON {resultado['alertas_enviadas']} ALERTAS!")
            else:
                print(f"\n   ℹ️  No hay nuevas alertas (ya enviadas o no cumplen filtros)")
                
        else:
            print(f"   ❌ FALLO")
            if 'error' in resultado:
                print(f"   💥 Error: {resultado['error']}")
        
        print(f"   🕐 Timestamp: {resultado['timestamp']}")
        
        # 6. VERIFICAR ARCHIVOS GENERADOS
        print("\n📁 6. ARCHIVOS GENERADOS:")
        archivos_verificar = [
            "config/scraper_config.json",
            "data/historial_alertas.json"
        ]
        
        for archivo in archivos_verificar:
            if os.path.exists(archivo):
                size = os.path.getsize(archivo)
                print(f"   ✅ {archivo} ({size} bytes)")
            else:
                print(f"   ❌ {archivo} (no existe)")
        
        # 7. MOSTRAR CONTENIDO DEL HISTORIAL
        if os.path.exists("data/historial_alertas.json"):
            print("\n📋 7. HISTORIAL DE ALERTAS:")
            try:
                with open("data/historial_alertas.json", 'r', encoding='utf-8') as f:
                    historial = json.load(f)
                
                if historial:
                    for fecha, alertas in historial.items():
                        print(f"   📅 {fecha}: {len(alertas)} alertas")
                        for alert_id, datos in alertas.items():
                            partido = f"{datos.get('equipo_visitante', '?')} @ {datos.get('equipo_local', '?')}"
                            consenso = datos.get('consenso', '?')
                            print(f"      • {partido} - {consenso}")
                else:
                    print("   📝 Historial vacío")
            except Exception as e:
                print(f"   ❌ Error leyendo historial: {e}")
        
        print(f"\n🎉 PRUEBA COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n💥 ERROR EN LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
    
    return sistema if 'sistema' in locals() else None

if __name__ == "__main__":
    sistema = main()
    
    print(f"\n🤔 ¿QUIERES HACER UNA SEGUNDA PRUEBA?")
    print("   (Para probar que el historial evita duplicados)")
    
    respuesta = input("   Presiona 's' y Enter para segunda prueba, o solo Enter para salir: ")
    
    if respuesta.lower().strip() == 's' and sistema:
        print(f"\n🔄 EJECUTANDO SEGUNDA PRUEBA...")
        print("   (Esta debería mostrar 0 alertas nuevas)")
        resultado2 = sistema.ejecutar_ciclo_completo()
        
        print(f"\n📊 RESULTADO SEGUNDA PRUEBA:")
        print(f"   Alertas enviadas: {resultado2['alertas_enviadas']}")
        if resultado2['alertas_enviadas'] == 0:
            print(f"   ✅ ¡Perfecto! El historial funciona correctamente")
        else:
            print(f"   ⚠️  Enviadas alertas nuevas (puede haber cambios en la página)")
    
    input(f"\n⏸️ Presiona Enter para salir...")
