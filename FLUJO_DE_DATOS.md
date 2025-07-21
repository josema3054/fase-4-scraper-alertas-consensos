"""
FLUJO COMPLETO DE DATOS - SISTEMA DE ALERTAS MLB
==============================================

Este documento explica dónde se guardan los datos y cómo fluyen por el sistema.

📊 FLUJO DE DATOS:
==================

1. SCRAPING (mlb_selenium_scraper.py)
   ↓
   📝 Datos extraídos en formato JSON
   
2. FILTROS (sistema_filtros_post_extraccion.py)
   ↓
   ✅ Consensos que cumplen criterios
   
3. ALMACENAMIENTO (múltiples lugares)
   ├── 📁 ARCHIVO LOCAL (historial_alertas.json)
   ├── 🗄️ SUPABASE DATABASE
   └── 📱 TELEGRAM (alertas)

🗄️ LUGARES DONDE SE GUARDAN LOS DATOS:
======================================

A) ARCHIVOS LOCALES:
-------------------
📁 data/historial_alertas.json
   - Consensos ya enviados (evita duplicados)
   - Estructura por fecha
   - Se limpia automáticamente cada 7 días

📁 logs/scraper_YYYY-MM-DD.log
   - Logs detallados de cada ejecución
   - Errores y estadísticas
   - Rotación diaria

B) BASE DE DATOS SUPABASE:
-------------------------
🗃️ TABLA: consensus_data
   - Todos los consensos extraídos
   - Datos históricos
   - Usado para análisis

🗃️ TABLA: consensus_alerts
   - Registro de alertas enviadas
   - Timestamp y destinatarios
   - Estadísticas de envío

🗃️ TABLA: matches
   - Partidos del día
   - Horarios y equipos
   - Estado del partido

🗃️ TABLA: system_logs
   - Logs del sistema
   - Health checks
   - Monitoreo

C) NOTIFICACIONES:
-----------------
📱 TELEGRAM
   - Alertas en tiempo real
   - Bot interactivo
   - Comandos de estado

📊 ESTRUCTURA DE DATOS GUARDADOS:
=================================

CONSENSO EXTRAÍDO (formato completo):
{
    "fecha_juego": "2025-07-20",
    "hora_juego": "1:35 pm ET",
    "equipo_visitante": "NYY",
    "equipo_local": "ATL", 
    "direccion_consenso": "UNDER",
    "porcentaje_consenso": 86,
    "porcentaje_over": 14,
    "porcentaje_under": 86,
    "consenso_over": 14,
    "consenso_under": 86,
    "total_line": 9.5,
    "num_experts": 7,
    "total_picks": 7,
    "fecha_scraping": "2025-07-20T07:30:00-03:00",
    "deporte": "MLB",
    "tipo_consenso": "TOTAL",
    "url_fuente": "https://contests.covers.com/consensus/...",
    "raw_text": "MLB NYY ATL Sun. Jul. 20 1:35 pm ET 86 % Under..."
}

HISTORIAL DE ALERTAS (data/historial_alertas.json):
{
    "2025-07-20": {
        "abc123def456": {
            "partido": "NYY @ ATL",
            "consenso": "UNDER 86%",
            "expertos": 7,
            "timestamp": "2025-07-20T07:30:00-03:00"
        }
    }
}

⚙️ CONFIGURACIÓN:
================

FILTROS (config/filtros_consenso.json):
- Umbral de porcentaje mínimo
- Número mínimo de expertos
- Deportes a procesar

SETTINGS (config/settings.py):
- Credenciales de Supabase
- Token de Telegram
- Configuración de scraping

🔄 PROCESO AUTOMÁTICO:
====================

1. SCRAPER ejecuta cada X horas
2. Extrae TODOS los consensos disponibles
3. Aplica FILTROS para encontrar los mejores
4. Verifica HISTORIAL (evita duplicados)
5. Guarda en SUPABASE (persistencia)
6. Envía ALERTAS por Telegram
7. Actualiza HISTORIAL local

📈 ANÁLISIS POSTERIOR:
=====================

Los datos se pueden analizar desde:

A) SUPABASE Dashboard:
   - Consultas SQL directas
   - Estadísticas por fecha
   - Análisis de rendimiento

B) Scripts de análisis:
   - Leer de data/historial_alertas.json
   - Conectar a Supabase
   - Generar reportes

C) Interfaz web (Streamlit):
   - Visualización en tiempo real
   - Gráficos y estadísticas
   - Control del sistema

🎯 EJEMPLO DE USO:
=================

Para revisar todos los consensos de hoy:
```python
from src.database.supabase_client import SupabaseClient

client = SupabaseClient()
consensos_hoy = client.supabase.table("consensus_data").select("*").eq("date", "2025-07-20").execute()

print(f"Consensos encontrados: {len(consensos_hoy.data)}")
for consenso in consensos_hoy.data:
    print(f"- {consenso['teams']}: {consenso['consensus_percentage']}%")
```

Para ver historial local:
```python
import json
with open('data/historial_alertas.json', 'r') as f:
    historial = json.load(f)
    
print(f"Alertas enviadas hoy: {len(historial.get('2025-07-20', {}))}")
```

🛠️ MANTENIMIENTO:
=================

- Limpieza automática del historial cada 7 días
- Rotación de logs diaria  
- Health checks de Supabase
- Monitoreo de Telegram
- Backup automático (si configurado)

"""

print("📋 DOCUMENTO DE FLUJO DE DATOS CREADO")
print("="*60)
print("Los datos se guardan en:")
print("✅ data/historial_alertas.json (local)")  
print("✅ Base de datos Supabase (cloud)")
print("✅ Logs en logs/ (local)")
print("✅ Alertas por Telegram (tiempo real)")
print("="*60)
