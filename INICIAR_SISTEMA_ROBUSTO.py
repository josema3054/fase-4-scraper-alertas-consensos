"""
MENÚ PRINCIPAL DEL SISTEMA SCRAPER ROBUSTO
==========================================
Script principal que integra todas las funcionalidades del sistema
"""

import os
import sys

def mostrar_menu():
    print("🎯 SISTEMA SCRAPER ROBUSTO - MENÚ PRINCIPAL")
    print("=" * 60)
    print("1. 🧪 Probar sistema completo")
    print("2. ⚙️  Configurar filtros dinámicos")
    print("3. 🌐 Iniciar interfaz web")
    print("4. 🔄 Ejecutar scraping único")
    print("5. 📊 Ver configuración actual")
    print("6. 📁 Ver historial de alertas")
    print("7. 🧹 Limpiar historial")
    print("8. 🚪 Salir")
    print("=" * 60)

def probar_sistema_completo():
    """Opción 1: Probar sistema completo"""
    print("\n🚀 Ejecutando prueba completa del sistema...")
    os.system('python test_sistema_robusto.py')

def configurar_filtros():
    """Opción 2: Configurar filtros dinámicos"""
    print("\n⚙️ Abriendo configurador de filtros...")
    os.system('python configurar_filtros.py')

def iniciar_interfaz_web():
    """Opción 3: Iniciar interfaz web"""
    print("\n🌐 Iniciando interfaz web...")
    print("   📍 URL: http://localhost:8501")
    print("   💡 Presiona Ctrl+C para detener")
    os.system('cd src\\web && streamlit run app.py')

def ejecutar_scraping_unico():
    """Opción 4: Ejecutar scraping único"""
    print("\n🔄 EJECUTANDO SCRAPING ÚNICO CON SISTEMA ROBUSTO")
    print("-" * 50)
    
    try:
        # Import dinámico
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from scraper.sistema_scraper_robusto import ScraperRobusto
        
        # Inicializar y ejecutar
        sistema = ScraperRobusto()
        resultado = sistema.ejecutar_ciclo_completo()
        
        # Mostrar resultados
        print(f"\n📊 RESULTADO:")
        print(f"   ✅ Éxito: {'Sí' if resultado['exito'] else 'No'}")
        print(f"   🎯 Consensos encontrados: {resultado['consensos_encontrados']}")
        print(f"   📢 Alertas nuevas: {resultado['alertas_enviadas']}")
        print(f"   ⏱️  Tiempo: {resultado['tiempo_procesamiento']} seg")
        
        if not resultado['exito'] and 'error' in resultado:
            print(f"   💥 Error: {resultado['error']}")
            
        print(f"   🕐 Timestamp: {resultado['timestamp']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def ver_configuracion_actual():
    """Opción 5: Ver configuración actual"""
    print("\n📋 CONFIGURACIÓN ACTUAL")
    print("-" * 40)
    
    try:
        import json
        
        # Leer configuración del scraper
        if os.path.exists("config/scraper_config.json"):
            with open("config/scraper_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("⚙️ FILTROS BASE:")
            print(f"   • Umbral mínimo: {config.get('umbral_minimo', 'N/A')}%")
            print(f"   • Expertos mínimos: {config.get('expertos_minimos', 'N/A')}")
            print(f"   • Picks mínimos: {config.get('picks_minimos', 'N/A')}")
            print(f"   • Direcciones: {config.get('direccion_permitida', 'N/A')}")
            
            filtros_hora = config.get('filtros_por_hora', {})
            if filtros_hora:
                print(f"\n🕐 FILTROS POR HORA ({len(filtros_hora)} configurados):")
                for hora, filtros in filtros_hora.items():
                    print(f"   📅 {hora}:")
                    for key, value in filtros.items():
                        print(f"      • {key}: {value}")
            else:
                print(f"\n🕐 FILTROS POR HORA: No configurados")
            
            print(f"\n📊 CONFIGURACIÓN SCRAPING:")
            print(f"   • Horas: {config.get('horas_scraping', 'N/A')}")
            print(f"   • Minutos antes partido: {config.get('minutos_antes_partido', 'N/A')}")
            
            print(f"\n📁 ARCHIVOS:")
            print(f"   • Configuración: config/scraper_config.json")
            print(f"   • Última actualización: {config.get('ultima_actualizacion', 'N/A')}")
            
        else:
            print("❌ No existe archivo de configuración")
            print("💡 Ejecuta la opción 2 para crear la configuración")
            
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")

def ver_historial_alertas():
    """Opción 6: Ver historial de alertas"""
    print("\n📋 HISTORIAL DE ALERTAS")
    print("-" * 30)
    
    try:
        import json
        
        if os.path.exists("data/historial_alertas.json"):
            with open("data/historial_alertas.json", 'r', encoding='utf-8') as f:
                historial = json.load(f)
            
            if historial:
                total_alertas = 0
                for fecha, alertas in historial.items():
                    print(f"\n📅 {fecha}: {len(alertas)} alertas")
                    total_alertas += len(alertas)
                    
                    for alert_id, datos in alertas.items():
                        partido = f"{datos.get('equipo_visitante', '?')} @ {datos.get('equipo_local', '?')}"
                        consenso = datos.get('consenso', '?')
                        timestamp = datos.get('timestamp', '?')
                        print(f"   • {partido} - {consenso} ({timestamp})")
                
                print(f"\n📊 RESUMEN:")
                print(f"   • Total días con alertas: {len(historial)}")
                print(f"   • Total alertas enviadas: {total_alertas}")
            else:
                print("📝 Historial vacío")
        else:
            print("❌ No existe historial de alertas")
            print("💡 Ejecuta un scraping para crear el historial")
            
    except Exception as e:
        print(f"❌ Error leyendo historial: {e}")

def limpiar_historial():
    """Opción 7: Limpiar historial"""
    print("\n🧹 LIMPIAR HISTORIAL DE ALERTAS")
    print("-" * 35)
    
    try:
        if os.path.exists("data/historial_alertas.json"):
            respuesta = input("¿Estás seguro de que quieres limpiar el historial? (s/N): ").strip().lower()
            
            if respuesta == 's':
                # Respaldar antes de limpiar
                import json
                import shutil
                from datetime import datetime
                
                # Crear respaldo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f"backups/historial_backup_{timestamp}.json"
                os.makedirs("backups", exist_ok=True)
                shutil.copy("data/historial_alertas.json", backup_file)
                
                # Limpiar historial
                with open("data/historial_alertas.json", 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)
                
                print(f"✅ Historial limpiado exitosamente")
                print(f"💾 Respaldo guardado en: {backup_file}")
            else:
                print("⏸️ Operación cancelada")
        else:
            print("📝 No hay historial que limpiar")
            
    except Exception as e:
        print(f"❌ Error limpiando historial: {e}")

def main():
    """Función principal del menú"""
    while True:
        try:
            mostrar_menu()
            
            opcion = input("\nSelecciona una opción (1-8): ").strip()
            
            if opcion == '1':
                probar_sistema_completo()
            elif opcion == '2':
                configurar_filtros()
            elif opcion == '3':
                iniciar_interfaz_web()
            elif opcion == '4':
                ejecutar_scraping_unico()
            elif opcion == '5':
                ver_configuracion_actual()
            elif opcion == '6':
                ver_historial_alertas()
            elif opcion == '7':
                limpiar_historial()
            elif opcion == '8':
                print("\n👋 ¡Hasta luego!")
                print("🎯 Sistema scraper robusto finalizado")
                break
            else:
                print("\n❌ Opción no válida. Selecciona 1-8.")
            
            # Pausa antes del siguiente menú
            if opcion != '8':
                input("\n⏸️ Presiona Enter para continuar...")
                print("\n" + "="*60 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            print("🎯 Sistema scraper robusto finalizado")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("⏸️ Presiona Enter para continuar...")

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("src"):
        print("❌ Error: Este script debe ejecutarse desde el directorio raíz del proyecto")
        print("💡 Asegúrate de estar en: fase-4-scraper-alertas-consensos")
        input("⏸️ Presiona Enter para salir...")
        sys.exit(1)
    
    main()
