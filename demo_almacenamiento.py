"""
DEMOSTRACIÓN DE ALMACENAMIENTO DE DATOS
======================================
Script que muestra dónde y cómo se guardan los datos extraídos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
import pytz
from src.coordinador_scraping import CoordinadorScraping, HistorialAlertas

def demostrar_almacenamiento():
    """Demostrar dónde se guardan los datos"""
    
    print("🗄️ DEMOSTRACIÓN DE ALMACENAMIENTO DE DATOS")
    print("="*60)
    
    # 1. HISTORIAL LOCAL
    print("\\n📁 1. HISTORIAL LOCAL (JSON)")
    print("-" * 40)
    
    historial = HistorialAlertas()
    archivo_historial = historial.archivo
    print(f"📍 Ubicación: {os.path.abspath(archivo_historial)}")
    
    if os.path.exists(archivo_historial):
        with open(archivo_historial, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Archivo existe")
        print(f"📊 Fechas registradas: {len(data)}")
        
        for fecha, consensos in data.items():
            print(f"   {fecha}: {len(consensos)} consensos enviados")
            
    else:
        print("⚠️ Archivo no existe aún (se creará al enviar primera alerta)")
    
    # 2. CONFIGURACIÓN DE FILTROS
    print("\\n⚙️ 2. CONFIGURACIÓN DE FILTROS")
    print("-" * 40)
    
    config_filtros = "config/filtros_consenso.json"
    print(f"📍 Ubicación: {os.path.abspath(config_filtros)}")
    
    if os.path.exists(config_filtros):
        with open(config_filtros, 'r', encoding='utf-8') as f:
            filtros = json.load(f)
        
        print("✅ Configuración actual:")
        print(f"   • Umbral mínimo: {filtros.get('umbral_minimo', '?')}%")
        print(f"   • Expertos mínimos: {filtros.get('expertos_minimos', '?')}")
        print(f"   • Total line: {filtros.get('total_line_min', '?')} - {filtros.get('total_line_max', '?')}")
    
    # 3. LOGS
    print("\\n📋 3. LOGS DEL SISTEMA")
    print("-" * 40)
    
    logs_dir = "logs"
    print(f"📍 Ubicación: {os.path.abspath(logs_dir)}")
    
    if os.path.exists(logs_dir):
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        print(f"✅ Archivos de log: {len(log_files)}")
        
        for log_file in sorted(log_files)[-5:]:  # Últimos 5
            log_path = os.path.join(logs_dir, log_file)
            size = os.path.getsize(log_path)
            print(f"   📄 {log_file}: {size:,} bytes")
    else:
        print("⚠️ Directorio de logs no existe")
    
    # 4. DATOS TEMPORALES
    print("\\n💾 4. DATOS EXTRAÍDOS (TEMPORAL)")
    print("-" * 40)
    
    temp_dir = "temp"
    print(f"📍 Ubicación: {os.path.abspath(temp_dir)}")
    
    if os.path.exists(temp_dir):
        temp_files = os.listdir(temp_dir)
        print(f"✅ Archivos temporales: {len(temp_files)}")
        
        for temp_file in temp_files:
            if temp_file.endswith('.json'):
                temp_path = os.path.join(temp_dir, temp_file)
                size = os.path.getsize(temp_path)
                print(f"   📄 {temp_file}: {size:,} bytes")
    else:
        print("⚠️ Directorio temporal no existe")
    
    # 5. SUPABASE (si está configurado)
    print("\\n🗄️ 5. BASE DE DATOS SUPABASE")
    print("-" * 40)
    
    try:
        from config.settings import Settings
        settings = Settings()
        
        print("✅ Configuración Supabase encontrada:")
        print(f"   🌐 URL: {settings.SUPABASE_URL}")
        print(f"   🔑 Key: {'*' * 10}...{settings.SUPABASE_KEY[-4:]}")
        print("   📊 Tablas configuradas:")
        print("     • consensus_data (datos de consensos)")
        print("     • consensus_alerts (historial de alertas)")
        print("     • matches (partidos del día)")
        print("     • system_logs (logs del sistema)")
        
    except Exception as e:
        print(f"⚠️ Supabase no configurado: {e}")
    
    # 6. TELEGRAM (si está configurado)  
    print("\\n📱 6. NOTIFICACIONES TELEGRAM")
    print("-" * 40)
    
    try:
        from config.settings import Settings
        settings = Settings()
        
        print("✅ Configuración Telegram encontrada:")
        print(f"   🤖 Bot Token: {'*' * 10}...{settings.TELEGRAM_BOT_TOKEN[-4:]}")
        print(f"   💬 Chat ID: {settings.TELEGRAM_CHAT_ID}")
        print("   📤 Las alertas se envían automáticamente")
        
    except Exception as e:
        print(f"⚠️ Telegram no configurado: {e}")
    
    # 7. RESUMEN DEL FLUJO
    print("\\n🔄 7. FLUJO DE DATOS")
    print("-" * 40)
    print("1. 🕷️ SCRAPER extrae datos → Lista de consensos")
    print("2. 🔍 FILTROS aplican criterios → Consensos válidos")
    print("3. 📁 HISTORIAL verifica duplicados → Nuevos únicamente")
    print("4. 💾 GUARDA en múltiples lugares:")
    print("   ├── JSON local (historial_alertas.json)")
    print("   ├── Supabase (database cloud)")
    print("   └── Logs (archivos .log)")
    print("5. 📱 NOTIFICA vía Telegram → Usuario recibe alerta")
    print("6. ⏰ PROGRAMA próxima ejecución → Loop automático")
    
    print("\\n" + "="*60)
    print("✅ Demostración completada")

def crear_ejemplo_datos():
    """Crear ejemplo de cómo se ven los datos guardados"""
    
    print("\\n📄 EJEMPLO DE DATOS GUARDADOS")
    print("="*50)
    
    # Ejemplo de consenso extraído
    consenso_ejemplo = {
        "fecha_juego": "2025-07-20",
        "hora_juego": "1:35 pm ET", 
        "equipo_visitante": "NYY",
        "equipo_local": "ATL",
        "direccion_consenso": "UNDER",
        "porcentaje_consenso": 86,
        "porcentaje_over": 14,
        "porcentaje_under": 86,
        "total_line": 9.5,
        "num_experts": 7,
        "fecha_scraping": "2025-07-20T07:30:00-03:00",
        "deporte": "MLB",
        "tipo_consenso": "TOTAL"
    }
    
    print("🎯 CONSENSO EXTRAÍDO:")
    print(json.dumps(consenso_ejemplo, indent=2, ensure_ascii=False))
    
    # Ejemplo de historial
    historial_ejemplo = {
        "2025-07-20": {
            "abc123def456": {
                "partido": "NYY @ ATL",
                "consenso": "UNDER 86%",
                "expertos": 7,
                "timestamp": "2025-07-20T07:30:00-03:00"
            },
            "def456ghi789": {
                "partido": "SD @ WAS", 
                "consenso": "UNDER 86%",
                "expertos": 7,
                "timestamp": "2025-07-20T07:32:00-03:00"
            }
        }
    }
    
    print("\\n📋 HISTORIAL DE ALERTAS:")
    print(json.dumps(historial_ejemplo, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    demostrar_almacenamiento()
    crear_ejemplo_datos()
    input("\\n⏸️ Presiona Enter para continuar...")
