# 🚨 Sistema Automatizado de Scraping y Alertas de Consensos Deportivos

Sistema inteligente que monitorea consensos deportivos en tiempo real y envía alertas automáticas vía Telegram cuando se detectan oportunidades de apuesta con alto consenso de expertos.

## 🎯 Características Principales

- **🔄 Scraping Automatizado**: Monitoreo diario desde covers.com sin navegador
- **📱 Alertas Telegram**: Notificaciones instantáneas cuando se alcanzan umbrales
- **🎮 Interfaz Web**: Dashboard Streamlit para configuración y monitoreo
- **📊 Analytics**: Estadísticas de efectividad y historial completo
- **🛡️ Tolerancia a Errores**: Sistema robusto con reintentos automáticos
- **📝 Logs Detallados**: Monitoreo completo del sistema

## ⚡ Inicio Rápido

### 1. Clona el Repositorio
```bash
git clone https://github.com/josema3054/fase-4-scraper-alertas-consensos.git
cd fase-4-scraper-alertas-consensos
```

### 2. Instala Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configura Variables de Entorno
```bash
cp config/.env.example .env
# Edita .env con tus credenciales
```

### 4. Configura la Base de Datos
```bash
python src/database/setup_tables.py
```

### 5. Ejecuta el Sistema
```bash
# Modo desarrollo (manual)
python main.py

# Interfaz web de configuración
streamlit run src/web/app.py

# Modo producción (automatizado)
python scheduler.py
```

## 📅 Flujo Automatizado

### 🌅 11:00 AM ART - Scraping Inicial
- Detecta todos los partidos MLB del día
- Obtiene consensos iniciales de expertos
- Programa scrapings automáticos pre-partido

### ⚡ 15 min antes de cada partido
- Scraping final de consenso actualizado
- Evaluación de umbrales (default: ≥80% MLB)
- Envío automático de alertas si se cumple criterio

### 🌙 Final del día
- Reporte automático de actividad diaria
- Estadísticas de alertas enviadas
- Verificación de salud del sistema

## 🚨 Tipos de Alertas

### 📱 Alerta de Consenso Alto
```
🚨 Alerta Consenso Deportivo 🚨
Deporte: MLB
Evento: NY Yankees vs Boston Red Sox
Consenso: Over (85%)
Total Expertos: 24
Hora del partido: 20:00 ET
```

### 📊 Reporte Diario del Sistema
```
✅ Reporte diario Scraper Consensos ✅
Fecha: 2025-07-13
Deportes monitoreados: MLB
Total Alertas enviadas: 6
Errores encontrados: 0
Estado: ✅ Funcionando correctamente
```

## 🛠️ Configuración

### Variables de Entorno Requeridas
```env
SUPABASE_URL=tu_url_supabase
SUPABASE_KEY=tu_key_supabase
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id
TIMEZONE=America/Argentina/Buenos_Aires
```

### Umbrales por Deporte
```json
{
  "mlb": {
    "consensus_threshold": 80,
    "min_experts": 4,
    "enabled": true
  }
}
```

## 📊 Interfaz Web - Dashboard

Accede a `http://localhost:8501` para:

- **⚙️ Configurar umbrales** por deporte
- **📈 Ver estadísticas** de efectividad
- **📱 Historial de alertas** enviadas
- **🔧 Monitorear estado** del sistema
- **📊 Analytics** de consensos

## 🏗️ Arquitectura del Proyecto

```
fase-4-scraper-alertas-consensos/
├── src/
│   ├── scraper/           # Módulos de scraping
│   │   ├── __init__.py
│   │   ├── covers_scraper.py
│   │   ├── mlb_scraper.py
│   │   └── base_scraper.py
│   ├── database/          # Gestión de base de datos
│   │   ├── __init__.py
│   │   ├── supabase_client.py
│   │   ├── models.py
│   │   └── setup_tables.py
│   ├── notifications/     # Sistema de alertas
│   │   ├── __init__.py
│   │   ├── telegram_bot.py
│   │   └── alert_manager.py
│   ├── web/              # Interfaz Streamlit
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── pages/
│   │   └── components/
│   └── utils/            # Utilidades generales
│       ├── __init__.py
│       ├── logger.py
│       ├── error_handler.py
│       └── timezone_utils.py
├── config/               # Configuraciones
│   ├── settings.py
│   ├── sports_config.json
│   └── .env.example
├── logs/                # Logs automáticos
├── tests/               # Tests unitarios
├── docs/                # Documentación
├── main.py              # Entrada principal
├── scheduler.py         # Automatización
└── requirements.txt     # Dependencias
```

## 🤖 Configuración del Bot de Telegram

### 1. Crear Bot con BotFather
1. Habla con [@BotFather](https://t.me/botfather)
2. Ejecuta `/newbot`
3. Asigna nombre y username al bot
4. Copia el token proporcionado

### 2. Obtener Chat ID
```bash
# Envía un mensaje a tu bot y ejecuta:
python src/notifications/get_chat_id.py
```

### 3. Configurar Variables
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTuVwXYz
TELEGRAM_CHAT_ID=123456789
```

## 🚀 Despliegue en Render

### 1. Conecta con GitHub
- Conecta tu cuenta de Render con GitHub
- Selecciona el repositorio `fase-4-scraper-alertas-consensos`

### 2. Configura el Servicio
```yaml
# render.yaml
services:
  - type: web
    name: consensus-alerts
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run src/web/app.py --server.port $PORT --server.address 0.0.0.0
```

### 3. Configura Variables de Entorno
- Agrega todas las variables de `.env` en el dashboard de Render

## 📈 Monitoreo y Logs

### Logs Automáticos
- **Ubicación**: `logs/scraper_YYYY-MM-DD.log`
- **Rotación**: Diaria automática
- **Niveles**: INFO, WARNING, ERROR, CRITICAL

### Métricas del Sistema
- Alertas enviadas por día
- Errores de scraping
- Tiempo de respuesta promedio
- Consensos detectados vs alertas enviadas

## 🔧 Desarrollo y Testing

### Ejecutar Tests
```bash
python -m pytest tests/ -v
```

### Modo Debug
```bash
export DEBUG=true
python main.py --debug
```

### Testing Manual
```bash
# Test scraper específico
python src/scraper/mlb_scraper.py --test

# Test alertas Telegram
python src/notifications/telegram_bot.py --test
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Deportes Soportados

### ✅ Implementados
- **MLB** (Béisbol): Completamente funcional

### 🔄 En Desarrollo
- **NBA** (Básquet): Próxima implementación
- **NFL** (Fútbol Americano): Planificado
- **NHL** (Hockey): Planificado

## 📞 Soporte

- **📂 Issues**: [GitHub Issues](https://github.com/josema3054/fase-4-scraper-alertas-consensos/issues)
- **📖 Documentación**: Ver carpeta `docs/`
- **🔧 Configuración**: Consultar `CONFIGURACION_PROYECTO.md`

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

---

⚠️ **Disclaimer**: Este software es para propósitos educativos y de investigación. Las apuestas deportivas involucran riesgo financiero. Usa responsablemente.
