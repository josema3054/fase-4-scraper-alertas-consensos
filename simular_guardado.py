"""
SIMULACIÓN DE GUARDADO DE DATOS
==============================
Muestra cómo se guardan los datos cuando el scraper encuentra consensos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
import pytz

def simular_guardado_consenso():
    """Simular el guardado de un consenso extraído"""
    
    print("💾 SIMULACIÓN DE GUARDADO DE DATOS")
    print("="*50)
    
    # Datos de ejemplo (como los que extrae el scraper real)
    consensos_extraidos = [
        {
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
            "fecha_scraping": datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).isoformat(),
            "deporte": "MLB",
            "tipo_consenso": "TOTAL"
        },
        {
            "fecha_juego": "2025-07-20",
            "hora_juego": "4:10 pm ET", 
            "equipo_visitante": "STL",
            "equipo_local": "AZ",
            "direccion_consenso": "OVER",
            "porcentaje_consenso": 78,
            "porcentaje_over": 78,
            "porcentaje_under": 22,
            "total_line": 9.0,
            "num_experts": 9,
            "fecha_scraping": datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).isoformat(),
            "deporte": "MLB", 
            "tipo_consenso": "TOTAL"
        }
    ]
    
    print(f"📊 Consensos extraídos: {len(consensos_extraidos)}")
    
    for i, consenso in enumerate(consensos_extraidos, 1):
        print(f"\\n{i}. {consenso['equipo_visitante']} @ {consenso['equipo_local']}")
        print(f"   Consenso: {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
        print(f"   Total: {consenso['total_line']} | Expertos: {consenso['num_experts']}")
    
    # PASO 1: Guardar en archivo temporal (para debugging)
    print("\\n📁 PASO 1: Guardando en archivo temporal...")
    
    os.makedirs("temp", exist_ok=True)
    temp_file = f"temp/consensos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(consensos_extraidos, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Guardado en: {temp_file}")
    
    # PASO 2: Simular filtrado
    print("\\n🔍 PASO 2: Aplicando filtros...")
    
    # Filtro: solo consensos >= 75%
    consensos_validos = [c for c in consensos_extraidos if c['porcentaje_consenso'] >= 75]
    
    print(f"✅ Consensos que pasan filtros: {len(consensos_validos)}")
    
    # PASO 3: Simular historial (evitar duplicados)
    print("\\n📋 PASO 3: Verificando historial...")
    
    os.makedirs("data", exist_ok=True)
    historial_file = "data/historial_alertas.json"
    
    # Cargar historial existente
    if os.path.exists(historial_file):
        with open(historial_file, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    else:
        historial = {}
    
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    if fecha_hoy not in historial:
        historial[fecha_hoy] = {}
    
    # Verificar duplicados y agregar nuevos
    consensos_nuevos = []
    
    for consenso in consensos_validos:
        # Generar ID único
        consenso_id = f"{consenso['equipo_visitante']}_{consenso['equipo_local']}_{consenso['direccion_consenso']}_{consenso['porcentaje_consenso']}"
        consenso_id = consenso_id.lower().replace(' ', '_')
        
        if consenso_id not in historial[fecha_hoy]:
            # Es nuevo, agregarlo
            consensos_nuevos.append(consenso)
            
            historial[fecha_hoy][consenso_id] = {
                "partido": f"{consenso['equipo_visitante']} @ {consenso['equipo_local']}",
                "consenso": f"{consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%",
                "expertos": consenso['num_experts'],
                "timestamp": consenso['fecha_scraping']
            }
            
            print(f"✅ Nuevo: {consenso['equipo_visitante']} @ {consenso['equipo_local']} - {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
        else:
            print(f"⏭️ Ya enviado: {consenso['equipo_visitante']} @ {consenso['equipo_local']}")
    
    # Guardar historial actualizado
    with open(historial_file, 'w', encoding='utf-8') as f:
        json.dump(historial, f, indent=2, ensure_ascii=False)
    
    print(f"\\n💾 Historial actualizado: {historial_file}")
    print(f"📊 Total consensos nuevos: {len(consensos_nuevos)}")
    
    # PASO 4: Simular alerta de Telegram
    print("\\n📱 PASO 4: Preparando alertas...")
    
    for consenso in consensos_nuevos:
        mensaje_alerta = f"""
🚨 **ALERTA MLB - CONSENSO ALTO**

🏈 **Partido:** {consenso['equipo_visitante']} @ {consenso['equipo_local']}
⏰ **Hora:** {consenso['hora_juego']}
📊 **Consenso:** {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%
📈 **Total:** {consenso['total_line']}
👥 **Expertos:** {consenso['num_experts']}

💡 **Significado:** {consenso['porcentaje_consenso']}% de expertos esperan que el total sea {consenso['direccion_consenso']} de {consenso['total_line']} runs.
        """.strip()
        
        print(f"\\n📤 Alerta preparada:")
        print("─" * 40)
        print(mensaje_alerta)
        print("─" * 40)
        
        # En el sistema real, aquí se enviaría por Telegram
        print(f"📱 (Se enviaría por Telegram al chat configurado)")
    
    # PASO 5: Mostrar resumen
    print("\\n📊 RESUMEN DE LA SESIÓN")
    print("="*40)
    print(f"• Consensos extraídos: {len(consensos_extraidos)}")
    print(f"• Consensos válidos (filtros): {len(consensos_validos)}")  
    print(f"• Consensos nuevos: {len(consensos_nuevos)}")
    print(f"• Alertas enviadas: {len(consensos_nuevos)}")
    
    print("\\n📁 Archivos creados/actualizados:")
    print(f"• {temp_file}")
    print(f"• {historial_file}")
    
    return consensos_nuevos

def mostrar_contenido_historial():
    """Mostrar el contenido actual del historial"""
    
    historial_file = "data/historial_alertas.json"
    
    if os.path.exists(historial_file):
        print("\\n📋 CONTENIDO DEL HISTORIAL")
        print("="*40)
        
        with open(historial_file, 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        for fecha, consensos in historial.items():
            print(f"\\n📅 {fecha}: {len(consensos)} alertas")
            
            for consenso_id, datos in consensos.items():
                print(f"  • {datos['partido']} - {datos['consenso']} ({datos['expertos']} expertos)")
    else:
        print("\\n⚠️ No hay historial aún")

if __name__ == "__main__":
    consensos_nuevos = simular_guardado_consenso()
    mostrar_contenido_historial()
    
    print("\\n✅ Simulación completada")
    print("\\n💡 En el sistema real:")
    print("• Los datos también se guardan en Supabase (cloud)")
    print("• Las alertas se envían automáticamente por Telegram")
    print("• El proceso se ejecuta cada X horas automáticamente")
    
    input("\\n⏸️ Presiona Enter para continuar...")
