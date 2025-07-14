# 🤖 Configuración del Bot de Telegram - Fase 4

## 📋 Guía completa para crear y configurar el bot de Telegram

### 🚀 Paso 1: Crear el Bot en Telegram

1. **Abrir Telegram** y buscar `@BotFather`
2. **Iniciar conversación** con `/start`
3. **Crear nuevo bot** con `/newbot`
4. **Elegir nombre** para el bot (ej: "Consensos Deportivos Fase 4")
5. **Elegir username** (debe terminar en 'bot', ej: `consensos_fase4_bot`)
6. **Guardar el token** que te proporciona BotFather

### 🔑 Paso 2: Configurar Variables de Entorno

Agregar al archivo `.env`:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_IDS=chat_id_1,chat_id_2
```

### 👥 Paso 3: Obtener Chat IDs

#### Método 1: Usando el bot @userinfobot
1. Buscar `@userinfobot` en Telegram
2. Enviar `/start`
3. Copiar tu Chat ID

#### Método 2: Usando tu bot (Recomendado)
1. Agregar tu bot a un grupo o enviarle un mensaje privado
2. Visitar: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Buscar el campo `"chat":{"id":XXXXXX}`
4. Usar ese número como Chat ID

### ⚙️ Paso 4: Comandos del Bot

El bot responderá a estos comandos:

- `/start` - Mensaje de bienvenida
- `/status` - Estado actual del sistema
- `/help` - Información de ayuda

### 🚨 Tipos de Alertas que Enviará

1. **Alertas de Consenso Alto**
   - Se envían cuando un consenso supera el 75%
   - Incluye detalles del partido y porcentajes
   - Frecuencia: En tiempo real

2. **Reportes Diarios**
   - Resumen de actividad del día
   - Estadísticas de consensos procesados
   - Hora: 23:45 ART

3. **Alertas de Error**
   - Notificaciones cuando hay problemas en el sistema
   - Información para diagnóstico
   - Frecuencia: Según errores

### 📱 Configuración de Múltiples Chats

Puedes enviar alertas a múltiples chats:

```env
TELEGRAM_CHAT_IDS=123456789,987654321,-100123456789
```

**Tipos de Chat ID:**
- **Positivo**: Chat privado con usuario
- **Negativo**: Grupos y canales (empiezan con -)

### 🔧 Configuración Avanzada

#### Personalizar Umbrales de Alerta

En `config/settings.py`:

```python
TELEGRAM_CONFIG = {
    'consensus_threshold': 75,  # Porcentaje mínimo para alerta
    'max_alerts_per_hour': 10,  # Límite de alertas por hora
    'enable_daily_reports': True,
    'enable_error_alerts': True,
    'message_format': 'markdown'  # 'markdown' o 'html'
}
```

#### Horarios de Silencio

```python
QUIET_HOURS = {
    'enabled': True,
    'start_hour': 23,  # 23:00 ART
    'end_hour': 7,     # 07:00 ART
    'timezone': 'America/Argentina/Buenos_Aires'
}
```

### 🧪 Probar la Configuración

1. **Ejecutar test básico:**
   ```bash
   cd src/notifications
   python telegram_bot.py
   ```

2. **Desde la interfaz web:**
   - Ir a la pestaña "🤖 Telegram"
   - Usar "📡 Test de Conexión"
   - Usar "💬 Enviar Mensaje Test"

### 🔒 Seguridad

1. **Mantener el token secreto**
   - Nunca compartir el token en código público
   - Usar variables de entorno
   - Rotar el token si se compromete

2. **Verificar Chat IDs**
   - Solo enviar mensajes a chats autorizados
   - Verificar identidad de usuarios

3. **Limitar funcionalidades**
   - El bot solo envía mensajes
   - No procesa comandos administrativos críticos

### 🚨 Solución de Problemas

#### Error: "Chat not found"
- Verificar que el Chat ID sea correcto
- Asegurarse de que el bot esté agregado al grupo
- Verificar que el bot tenga permisos para enviar mensajes

#### Error: "Bot token is invalid"
- Verificar que el token esté completo
- Verificar que no haya espacios extra
- Contactar a BotFather si el bot fue eliminado

#### No llegan las alertas
- Verificar conexión a internet
- Revisar logs del sistema
- Probar con chat privado primero

### 📊 Monitoreo del Bot

El sistema registra:
- Mensajes enviados exitosamente
- Errores de envío
- Rate limiting de Telegram
- Estado de conexión

### 🔄 Mantenimiento

#### Rotación de Token
Si necesitas cambiar el token:
1. Contactar a BotFather: `/mybots`
2. Seleccionar tu bot
3. "API Token" → "Revoke current token"
4. Generar nuevo token
5. Actualizar variable de entorno
6. Reiniciar el sistema

#### Backup de Configuración
```bash
# Exportar configuración actual
python -c "from src.database.supabase_client import SupabaseClient; client = SupabaseClient(); client.backup_telegram_config()"
```

### 📈 Estadísticas y Métricas

El bot registra:
- Tiempo de respuesta de mensajes
- Tasa de entrega exitosa
- Número de chats activos
- Frecuencia de alertas por tipo

---

## 🎯 Ejemplo de Configuración Completa

### `.env` file:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_IDS=123456789,-100987654321
TELEGRAM_CONSENSUS_THRESHOLD=75
TELEGRAM_ENABLE_DAILY_REPORTS=true
TELEGRAM_ENABLE_ERROR_ALERTS=true
TELEGRAM_MAX_ALERTS_PER_HOUR=15
```

### Verificación final:
```python
# Ejecutar este script para verificar configuración
import os
from src.notifications.telegram_bot import TelegramNotifier

async def verify_setup():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_ids = os.getenv('TELEGRAM_CHAT_IDS').split(',')
    
    notifier = TelegramNotifier(token, chat_ids)
    success = await notifier.test_connection()
    
    if success:
        print("✅ Configuración de Telegram exitosa")
    else:
        print("❌ Error en configuración de Telegram")

# Ejecutar con: python -m asyncio verify_setup()
```

---

**📞 Soporte**: Si tienes problemas con la configuración, revisa los logs en `logs/scraper_YYYY-MM-DD.log`
