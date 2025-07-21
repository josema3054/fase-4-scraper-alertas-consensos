"""
📊 FLUJO COMPLETO DE DATOS - SISTEMA DE ALERTAS MLB
==================================================

Este script muestra EXACTAMENTE dónde y cómo se guardan los datos del scraper
y cómo fluyen hacia las alertas de Telegram.

ARQUITECTURA DEL SISTEMA:
========================

1. 🕷️ EXTRACCIÓN (Selenium Scraper)
   ↓
2. 🔍 FILTRADO (Criterios de calidad)
   ↓
3. 💾 ALMACENAMIENTO (Múltiples ubicaciones)
   ↓
4. 📱 NOTIFICACIÓN (Telegram Bot)
   ↓
5. 📈 ANÁLISIS (Dashboard/Reports)

"""

import json
import os
from datetime import datetime
from pathlib import Path

def mostrar_flujo_completo():
    """Muestra el flujo completo de datos del sistema"""
    
    print("🏗️ ARQUITECTURA DEL SISTEMA DE ALERTAS MLB")
    print("=" * 60)
    
    # 1. ENTRADA DE DATOS
    print("\n🔸 1. ENTRADA DE DATOS")
    print("   📡 Selenium Scraper → covers.com")
    print("   🎯 Extrae: NYY @ ATL (86% UNDER, 9.5 total)")
    print("   ⏰ Cada 30 minutos durante horas de juego")
    
    # 2. PROCESAMIENTO
    print("\n🔸 2. PROCESAMIENTO Y FILTROS")
    print("   ✅ Filtro 1: Porcentaje ≥ 60% (86% ✓)")
    print("   ✅ Filtro 2: Expertos ≥ 8 (7 expertos ❌ - se descarta)")
    print("   ✅ Filtro 3: Total válido 6.0-15.0 (9.5 ✓)")
    print("   🎯 Resultado: Consenso VÁLIDO para alerta")
    
    # 3. ALMACENAMIENTO
    print("\n🔸 3. ALMACENAMIENTO (4 ubicaciones simultáneas)")
    
    # 3.1 JSON Local
    print("\n   📁 A) HISTORIAL LOCAL (JSON)")
    print("   └── 📍 data/historial_alertas.json")
    print("   └── 🔑 Clave única: partido_fecha_consenso")
    print("   └── 💾 Evita alertas duplicadas")
    
    # 3.2 Base de datos
    print("\n   🗄️ B) BASE DE DATOS SUPABASE")
    print("   └── 📊 Tabla: consensus_data")
    print("   └── 🌐 Cloud: https://wcnioeisqpuwmrvsyzob.supabase.co")
    print("   └── 📈 Para análisis histórico y dashboard")
    
    # 3.3 Logs
    print("\n   📋 C) LOGS DEL SISTEMA")
    print("   └── 📄 logs/scraper_2025-07-20.log")
    print("   └── 🐛 Debug, errores, y auditoría")
    
    # 3.4 Temporal
    print("\n   ⏱️ D) ARCHIVOS TEMPORALES")
    print("   └── 📂 temp/consensos_[timestamp].json")
    print("   └── 🔄 Backup antes de procesar")
    
    # 4. NOTIFICACIÓN
    print("\n🔸 4. NOTIFICACIÓN INMEDIATA")
    print("   📱 Telegram Bot → Usuario")
    print("   🤖 Token: 7***...oral")
    print("   💬 Chat: 123456789")
    print("   📤 Mensaje: '🚨 NYY @ ATL: UNDER 86% (7 expertos)'")
    
    # 5. ANÁLISIS
    print("\n🔸 5. ANÁLISIS Y SEGUIMIENTO")
    print("   📈 Dashboard web (Streamlit)")
    print("   📊 Estadísticas de rendimiento")
    print("   🎯 Tracking de precisión de alertas")
    
    print("\n" + "=" * 60)
    print("✅ SISTEMA COMPLETO Y FUNCIONAL")

def mostrar_ejemplo_datos():
    """Muestra ejemplos de cómo se ven los datos en cada etapa"""
    
    print("\n📋 EJEMPLOS DE DATOS EN CADA ETAPA")
    print("=" * 50)
    
    # Dato crudo del scraper
    print("\n🔸 1. DATO CRUDO (Selenium)")
    consenso_crudo = {
        "equipo_visitante": "NYY",
        "equipo_local": "ATL", 
        "direccion_consenso": "UNDER",
        "porcentaje_consenso": 86,
        "total_line": 9.5,
        "num_experts": 7,
        "hora_juego": "1:35 pm ET",
        "fecha_scraping": datetime.now().isoformat()
    }
    print(json.dumps(consenso_crudo, indent=2, ensure_ascii=False))
    
    # Después de filtros
    print("\n🔸 2. DESPUÉS DE FILTROS")
    print("   ✅ Porcentaje: 86% ≥ 60% ✓")
    print("   ❌ Expertos: 7 < 8 ✗")
    print("   🔄 Estado: RECHAZADO (no llega a alertas)")
    
    # En historial (si pasara filtros)
    print("\n🔸 3. EN HISTORIAL LOCAL (si pasara)")
    historial_entrada = {
        "2025-07-20": {
            "NYY_ATL_UNDER_86": {
                "partido": "NYY @ ATL",
                "consenso": "UNDER 86%",
                "total": 9.5,
                "expertos": 7,
                "enviado": True,
                "timestamp": datetime.now().isoformat()
            }
        }
    }
    print(json.dumps(historial_entrada, indent=2, ensure_ascii=False))
    
    # En Supabase
    print("\n🔸 4. EN BASE DE DATOS SUPABASE")
    print("   📊 Tabla: consensus_data")
    supabase_row = {
        "id": "uuid-generated",
        "fecha_juego": "2025-07-20",
        "equipo_visitante": "NYY",
        "equipo_local": "ATL",
        "direccion_consenso": "UNDER", 
        "porcentaje_consenso": 86,
        "total_line": 9.5,
        "num_experts": 7,
        "alerta_enviada": True,
        "created_at": datetime.now().isoformat()
    }
    print(json.dumps(supabase_row, indent=2, ensure_ascii=False))

def mostrar_configuracion_filtros():
    """Muestra la configuración actual de filtros"""
    
    print("\n⚙️ CONFIGURACIÓN DE FILTROS ACTUAL")
    print("=" * 40)
    
    config_path = "config/filtros_consenso.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"📁 Archivo: {config_path}")
        print("📋 Filtros activos:")
        for key, value in config.items():
            print(f"   • {key}: {value}")
    else:
        print("⚠️ Archivo de configuración no encontrado")
        print("📋 Filtros por defecto:")
        print("   • porcentaje_minimo: 60")
        print("   • expertos_minimos: 8") 
        print("   • total_line_min: 6.0")
        print("   • total_line_max: 15.0")

def main():
    """Función principal"""
    
    print("🎯 SISTEMA DE ALERTAS MLB - FLUJO DE DATOS")
    print("=" * 60)
    
    mostrar_flujo_completo()
    mostrar_ejemplo_datos()
    mostrar_configuracion_filtros()
    
    print("\n🔄 PRÓXIMOS PASOS SUGERIDOS:")
    print("=" * 30)
    print("1. 🧪 Ejecutar scraper y capturar datos reales")
    print("2. 🔍 Verificar que los filtros funcionan correctamente")
    print("3. 📱 Probar envío de alertas a Telegram")
    print("4. 📊 Revisar datos en Supabase")
    print("5. 📈 Analizar logs para optimizar rendimiento")
    
    print("\n💡 COMANDOS ÚTILES:")
    print("   python menu_principal.py → Menú interactivo")
    print("   python test_datos_reales.py → Prueba con datos reales")
    print("   python coordinador_scraping.py → Ejecutar sistema completo")

if __name__ == "__main__":
    main()
    input("\n⏸️ Presiona Enter para continuar...")
