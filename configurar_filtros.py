"""
CONFIGURADOR DE FILTROS DINÁMICOS
================================
Script para configurar filtros variables por hora del día
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.scraper.sistema_scraper_robusto import ScraperRobusto, ConfiguracionFiltros
import json

def configurar_filtros_dinamicos():
    """Configurar filtros que varían según la hora del día"""
    
    print("⚙️ CONFIGURADOR DE FILTROS DINÁMICOS")
    print("=" * 50)
    
    # Inicializar sistema
    sistema = ScraperRobusto()
    
    print("\n📋 Configuración actual:")
    config_actual = sistema.obtener_resumen_configuracion()
    for key, value in config_actual['filtros_basicos'].items():
        print(f"   {key}: {value}")
    
    print("\n🕐 CONFIGURANDO FILTROS POR HORA...")
    print("   Estrategia recomendada:")
    print("   • Mañana (09:00): Filtros más estrictos para consensos matutinos")
    print("   • Antes de partidos: Filtros más permisivos para alertas urgentes")
    
    # Configuración sugerida de filtros por hora
    configuracion_propuesta = {
        # Filtros base (por defecto)
        "umbral_minimo": 70,
        "expertos_minimos": 15,
        "picks_minimos": 8,
        "direccion_permitida": ["OVER", "UNDER"],
        "total_line_min": 6.0,
        "total_line_max": 15.0,
        
        # Horarios de scraping
        "horas_scraping": ["09:00", "antes_partido"],
        "minutos_antes_partido": 15,
        
        # Filtros específicos por hora
        "filtros_por_hora": {
            "09:00": {  # Scraping matutino - MÁS ESTRICTO
                "umbral_minimo": 75,
                "expertos_minimos": 20,
                "picks_minimos": 12
            },
            "12:00": {  # Mediodía - INTERMEDIO
                "umbral_minimo": 72,
                "expertos_minimos": 18,
                "picks_minimos": 10
            },
            "15:00": {  # Tarde - ESTÁNDAR
                "umbral_minimo": 70,
                "expertos_minimos": 15,
                "picks_minimos": 8
            },
            "18:00": {  # Noche - MÁS PERMISIVO (antes de partidos)
                "umbral_minimo": 65,
                "expertos_minimos": 12,
                "picks_minimos": 6
            }
        }
    }
    
    print("\n📊 CONFIGURACIÓN PROPUESTA:")
    print("   🌅 09:00 (Matutino)  - MÁS ESTRICTO:  Umbral 75%, 20+ expertos")
    print("   ☀️  12:00 (Mediodía) - INTERMEDIO:    Umbral 72%, 18+ expertos")
    print("   🌇 15:00 (Tarde)    - ESTÁNDAR:      Umbral 70%, 15+ expertos")
    print("   🌃 18:00 (Noche)    - MÁS PERMISIVO: Umbral 65%, 12+ expertos")
    
    respuesta = input("\n¿Aplicar esta configuración? (s/n): ").strip().lower()
    
    if respuesta == 's':
        try:
            # Aplicar configuración
            sistema.actualizar_configuracion(**configuracion_propuesta)
            
            print("\n✅ CONFIGURACIÓN APLICADA EXITOSAMENTE")
            
            # Verificar que se guardó correctamente
            sistema_verificacion = ScraperRobusto()
            config_nueva = sistema_verificacion.obtener_resumen_configuracion()
            
            print("\n📋 Configuración guardada:")
            for seccion, datos in config_nueva.items():
                if seccion != 'archivos':
                    print(f"   {seccion}:")
                    for key, value in datos.items():
                        print(f"      • {key}: {value}")
            
            # Verificar archivo de configuración
            if os.path.exists("config/scraper_config.json"):
                with open("config/scraper_config.json", 'r', encoding='utf-8') as f:
                    config_archivo = json.load(f)
                
                print(f"\n📁 Archivo de configuración creado:")
                print(f"   📍 config/scraper_config.json")
                print(f"   📊 Filtros por hora: {len(config_archivo.get('filtros_por_hora', {}))}")
                print(f"   🕐 Última actualización: {config_archivo.get('ultima_actualizacion', 'N/A')}")
            
            print(f"\n🎯 PRÓXIMOS PASOS:")
            print(f"   1. Ejecutar: python test_sistema_robusto.py")
            print(f"   2. Verificar que los filtros se aplican correctamente")
            print(f"   3. Automatizar con el scheduler")
            
        except Exception as e:
            print(f"\n❌ Error aplicando configuración: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n⏸️ Configuración no aplicada")
    
    return sistema

def mostrar_configuracion_actual():
    """Mostrar la configuración actual en detalle"""
    print("\n🔍 CONFIGURACIÓN ACTUAL DETALLADA:")
    print("=" * 50)
    
    try:
        if os.path.exists("config/scraper_config.json"):
            with open("config/scraper_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("📊 Filtros base:")
            filtros_base = ['umbral_minimo', 'expertos_minimos', 'picks_minimos']
            for filtro in filtros_base:
                print(f"   • {filtro}: {config.get(filtro, 'N/A')}")
            
            print(f"\n🕐 Filtros por hora:")
            filtros_hora = config.get('filtros_por_hora', {})
            if filtros_hora:
                for hora, filtros in filtros_hora.items():
                    print(f"   📅 {hora}:")
                    for key, value in filtros.items():
                        print(f"      • {key}: {value}")
            else:
                print("   📝 No hay filtros por hora configurados")
            
            print(f"\n⏰ Configuración de scraping:")
            print(f"   • Horas: {config.get('horas_scraping', [])}")
            print(f"   • Minutos antes partido: {config.get('minutos_antes_partido', 15)}")
            
        else:
            print("❌ No existe archivo de configuración")
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")

def menu_principal():
    """Menú principal del configurador"""
    while True:
        print("\n" + "="*50)
        print("🎛️  CONFIGURADOR DE FILTROS DINÁMICOS")
        print("="*50)
        print("1. 📊 Mostrar configuración actual")
        print("2. ⚙️  Aplicar configuración sugerida")
        print("3. 🧪 Probar sistema robusto")
        print("4. 🚪 Salir")
        
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
        if opcion == '1':
            mostrar_configuracion_actual()
        elif opcion == '2':
            configurar_filtros_dinamicos()
        elif opcion == '3':
            print("\n🚀 Iniciando prueba del sistema...")
            os.system('python test_sistema_robusto.py')
        elif opcion == '4':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción no válida")

if __name__ == "__main__":
    menu_principal()
