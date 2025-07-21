"""
🔗 CONEXIÓN ENTRE MÓDULOS DEL SISTEMA
=====================================

Este script muestra cómo se conectan todos los módulos:
Scraper → Coordinador → Filtros → Base de Datos → Telegram

"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def mostrar_conexiones():
    """Muestra las conexiones entre módulos"""
    
    print("🔗 DIAGRAMA DE CONEXIONES DEL SISTEMA")
    print("=" * 50)
    
    print("""
    ┌─────────────────┐    
    │   🌐 COVERS.COM │    
    └─────────┬───────┘    
              │            
              ▼            
    ┌─────────────────┐    
    │  🕷️ MLB SCRAPER │    ← src/scraper/mlb_selenium_scraper.py
    │   (Selenium)    │    
    └─────────┬───────┘    
              │            
              ▼            
    ┌─────────────────┐    
    │ 🎯 COORDINADOR  │    ← coordinador_scraping.py
    │   (Orquestador) │    
    └─────────┬───────┘    
              │            
              ├─────────────────┐
              ▼                 ▼
    ┌─────────────────┐    ┌─────────────────┐
    │ 🔍 FILTROS      │    │ 📁 HISTORIAL    │
    │ (Validación)    │    │ (Anti-duplicado)│
    └─────────┬───────┘    └─────────┬───────┘
              │                      │
              └──────────┬───────────┘
                         ▼
               ┌─────────────────┐
               │ ✅ CONSENSO     │
               │   VÁLIDO        │
               └─────────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌─────────┐  ┌─────────────┐  ┌─────────────┐
    │📁 JSON  │  │🗄️ SUPABASE │  │📱 TELEGRAM │
    │ Local   │  │ Database    │  │   Bot       │
    └─────────┘  └─────────────┘  └─────────────┘
    """)

def mostrar_archivos_clave():
    """Muestra los archivos clave y su función"""
    
    print("\n📂 ARCHIVOS CLAVE DEL SISTEMA")
    print("=" * 35)
    
    archivos = {
        "🕷️ SCRAPING": {
            "src/scraper/mlb_selenium_scraper.py": "Extrae datos de covers.com",
            "src/scraper/mlb_scraper.py": "Scraper legacy (requests/bs4)",
        },
        "🎯 COORDINACIÓN": {
            "coordinador_scraping.py": "Orquestador principal del sistema",
            "sistema_filtros_post_extraccion.py": "Filtros de calidad",
        },
        "💾 DATOS": {
            "src/database/supabase_client.py": "Cliente de base de datos",
            "src/database/models.py": "Modelos de datos",
            "data/historial_alertas.json": "Historial local",
        },
        "📱 NOTIFICACIONES": {
            "src/notifications/telegram_bot.py": "Bot de Telegram",
        },
        "⚙️ CONFIGURACIÓN": {
            "config/filtros_consenso.json": "Criterios de filtrado",
            "config/settings.py": "Configuración general",
        },
        "🖥️ INTERFAZ": {
            "menu_principal.py": "Menú interactivo",
            "interfaz_completa.py": "Dashboard Streamlit",
            "test_datos_reales.py": "Pruebas en vivo",
        }
    }
    
    for categoria, files in archivos.items():
        print(f"\n{categoria}")
        print("-" * 25)
        for file, desc in files.items():
            print(f"  📄 {file}")
            print(f"     └─ {desc}")

def mostrar_flujo_ejecucion():
    """Muestra el flujo de ejecución paso a paso"""
    
    print("\n⚡ FLUJO DE EJECUCIÓN")
    print("=" * 25)
    
    pasos = [
        ("🚀", "INICIO", "Usuario ejecuta: python menu_principal.py"),
        ("🔧", "SETUP", "Configurar Chrome driver (modo visible)"),
        ("🌐", "NAVEGACIÓN", "Ir a covers.com/consensus/..."),
        ("⏳", "ESPERA", "Esperar 10 seg para carga completa"),
        ("🔍", "EXTRACCIÓN", "Buscar tabla.responsive y extraer filas"),
        ("✅", "VALIDACIÓN", "Aplicar filtros de calidad"),
        ("🔄", "HISTORIAL", "Verificar duplicados"),
        ("💾", "GUARDADO", "Guardar en JSON + Supabase + Logs"),
        ("📱", "ALERTA", "Enviar notificación Telegram"),
        ("📊", "DASHBOARD", "Actualizar interfaz web"),
        ("⏰", "PROGRAMA", "Programar próxima ejecución"),
    ]
    
    for i, (icono, fase, descripcion) in enumerate(pasos, 1):
        print(f"{i:2d}. {icono} {fase:<12} │ {descripcion}")

def verificar_archivos():
    """Verifica que existan los archivos principales"""
    
    print("\n🔍 VERIFICACIÓN DE ARCHIVOS")
    print("=" * 30)
    
    archivos_principales = [
        "src/scraper/mlb_selenium_scraper.py",
        "coordinador_scraping.py", 
        "sistema_filtros_post_extraccion.py",
        "src/notifications/telegram_bot.py",
        "menu_principal.py",
        "config/settings.py"
    ]
    
    for archivo in archivos_principales:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")

def main():
    """Función principal"""
    
    print("🔗 ARQUITECTURA Y CONEXIONES DEL SISTEMA MLB")
    print("=" * 50)
    
    mostrar_conexiones()
    mostrar_archivos_clave()
    mostrar_flujo_ejecucion()
    verificar_archivos()
    
    print("\n" + "=" * 50)
    print("💡 RESUMEN:")
    print("   1. 🕷️ Scraper extrae → Lista de consensos")
    print("   2. 🎯 Coordinador filtra → Consensos válidos") 
    print("   3. 📁 Sistema guarda → Múltiples ubicaciones")
    print("   4. 📱 Telegram notifica → Usuario recibe alerta")
    print("   5. 🔄 Loop continúa → Automatización completa")

if __name__ == "__main__":
    main()
    input("\n⏸️ Presiona Enter para continuar...")
