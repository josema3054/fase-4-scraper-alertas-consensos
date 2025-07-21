"""
MENÚ PRINCIPAL DEL SISTEMA DE SCRAPING
=====================================
Administra todo el sistema de scraping con flujo separado
"""

import os
import sys
from datetime import datetime

def mostrar_menu():
    """Mostrar menú principal"""
    print("🚀 SISTEMA DE SCRAPING MLB - SOLO DATOS REALES")
    print("=" * 60)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    print("1. 📡 Scraping con datos reales de covers.com")
    print("2. ⚙️  Configurar filtros")
    print("3. 📊 Ver resultados anteriores")
    print("4. 🔍 Test scraper individual")
    print("5. 📋 Estado del sistema")
    print("6. 🚪 Salir")
    print()

def ejecutar_scraping_real():
    """Ejecutar scraping con datos reales - PRINCIPAL"""
    print("🚀 SCRAPING CON DATOS REALES DE COVERS.COM")
    print("============================================================")
    print("   Flujo: SCRAPER SELENIUM → DATOS REALES → FILTROS → ALERTAS")
    print("============================================================")
    print()
    print("📡 PASO 1: Extrayendo datos reales de covers.com...")
    print("   (Esto puede tomar varios minutos)")
    os.system('python test_datos_reales.py')

def configurar_filtros():
    """Configurar filtros del sistema"""
    print("⚙️ CONFIGURACIÓN DE FILTROS")
    print("=" * 40)
    
    print("Filtros actuales sugeridos:")
    print("• Umbral mínimo: 70%")
    print("• Expertos mínimos: 15")
    print("• Requerir equipos: Sí")
    print("• Direcciones permitidas: OVER, UNDER")
    
    print("\n¿Quieres usar la configuración de filtros avanzada?")
    respuesta = input("Presiona 'a' para avanzado, o Enter para continuar: ")
    
    if respuesta.lower() == 'a':
        os.system('python configurar_filtros.py')
    else:
        print("✅ Usando configuración estándar")

def ver_resultados():
    """Ver resultados de pruebas anteriores"""
    print("📊 RESULTADOS ANTERIORES")
    print("=" * 40)
    
    archivos_resultado = [
        'resultado_datos_reales.json',
        'test_simple_resultado.json',
        'datos_puros_scraper.json'
    ]
    
    for archivo in archivos_resultado:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print(f"✅ {archivo} ({size} bytes)")
            
            if archivo.endswith('.json'):
                try:
                    import json
                    with open(archivo, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        print(f"   📊 {len(data)} elementos")
                    elif isinstance(data, dict) and 'estadisticas' in data:
                        stats = data['estadisticas']
                        print(f"   📊 Extraídos: {stats.get('total_extraidos', 0)}")
                        print(f"   🔍 Filtrados: {stats.get('consensos_filtrados', 0)}")
                        print(f"   📢 Alertas: {stats.get('alertas_generadas', 0)}")
                except Exception as e:
                    print(f"   ❌ Error leyendo archivo: {e}")
        else:
            print(f"❌ {archivo} (no existe)")
    
    print("\n¿Abrir algún archivo?")
    archivo = input("Nombre del archivo (o Enter para continuar): ")
    if archivo and os.path.exists(archivo):
        os.system(f'notepad {archivo}')

def test_scraper_individual():
    """Test de scraper individual"""
    print("🔍 TEST SCRAPER INDIVIDUAL")
    print("=" * 40)
    print("1. Scraper Selenium (recomendado)")
    print("2. Scraper Puro (nuevo)")
    print("3. Scraper Legacy (requests)")
    
    opcion = input("Selecciona scraper (1-3): ").strip()
    
    if opcion == "1":
        print("🚀 Ejecutando Scraper Selenium...")
        os.system('python src\\scraper\\mlb_selenium_scraper.py')
    elif opcion == "2":
        print("🚀 Ejecutando Scraper Puro...")
        os.system('python src\\scraper\\mlb_scraper_puro.py')
    elif opcion == "3":
        print("🚀 Ejecutando Scraper Legacy...")
        os.system('python src\\scraper\\mlb_scraper.py')
    else:
        print("❌ Opción no válida")

def mostrar_estado_sistema():
    """Mostrar estado del sistema"""
    print("📋 ESTADO DEL SISTEMA")
    print("=" * 40)
    
    # Verificar archivos clave
    archivos_sistema = [
        ('src/scraper/mlb_selenium_scraper.py', 'Scraper Selenium'),
        ('src/scraper/mlb_scraper_puro.py', 'Scraper Puro'),
        ('src/sistema_filtros_post_extraccion.py', 'Sistema de Filtros'),
        ('src/coordinador_scraping.py', 'Coordinador'),
        ('test_datos_reales.py', 'Test Datos Reales')
    ]
    
    print("📁 ARCHIVOS DEL SISTEMA:")
    for archivo, descripcion in archivos_sistema:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print(f"   ✅ {descripcion}: {archivo} ({size} bytes)")
        else:
            print(f"   ❌ {descripcion}: {archivo} (FALTANTE)")
    
    # Verificar directorios
    print(f"\n📂 DIRECTORIOS:")
    directorios = ['src', 'src/scraper', 'config', 'data', 'logs']
    for directorio in directorios:
        if os.path.exists(directorio):
            print(f"   ✅ {directorio}/")
        else:
            print(f"   ❌ {directorio}/ (faltante)")
    
    # Estado de la configuración
    print(f"\n⚙️ CONFIGURACIÓN:")
    print(f"   • Flujo: Scraper Puro → Filtros → Alertas")
    print(f"   • Scraper principal: Selenium")
    print(f"   • Filtros: Post-extracción")
    print(f"   • Zona horaria: Argentina")
    print(f"   • Reintentos: Automáticos")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    print(f"   1. Ejecuta 'Scraping con datos reales' (Opción 1)")
    print(f"   2. Configura filtros según tus necesidades (Opción 2)")
    print(f"   3. Revisa resultados anteriores (Opción 3)")
    print(f"   4. Automatiza con scheduler cuando esté listo")

def main():
    """Función principal del menú"""
    while True:
        mostrar_menu()
        
        opcion = input("Selecciona una opción (1-6): ").strip()
        
        print()  # Línea en blanco
        
        if opcion == "1":
            ejecutar_scraping_real()
        elif opcion == "2":
            configurar_filtros()
        elif opcion == "3":
            ver_resultados()
        elif opcion == "4":
            test_scraper_individual()
        elif opcion == "5":
            mostrar_estado_sistema()
        elif opcion == "6":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")
        
        print()
        input("⏸️ Presiona Enter para continuar...")
        print("\n" * 2)  # Limpiar pantalla

if __name__ == "__main__":
    main()
