# Guía de Setup de GitHub para el Proyecto Fase 4

## 📋 Resumen del Proyecto

**Nombre del Proyecto**: Sistema Automatizado de Scraping y Alertas Deportivas - Fase 4
**Descripción**: Sistema automatizado para scraping diario de consensos deportivos desde covers.com, con alertas automáticas por Telegram, almacenamiento en Supabase, interfaz web en Streamlit y soporte multideporte.

## 🔧 Configuración del Repositorio GitHub

### 1. Crear el Repositorio en GitHub

1. Ve a [GitHub](https://github.com) y haz login
2. Haz clic en "New repository" (repositorio nuevo)
3. Usa estos datos:
   - **Repository name**: `fase-4-scraper-alertas-consensos`
   - **Description**: `Sistema automatizado de scraping y alertas deportivas con soporte multideporte, notificaciones Telegram y interfaz web`
   - **Visibility**: Private (recomendado por contener configuraciones sensibles)
   - **NO** marques "Add a README file" (ya tenemos uno)
   - **NO** marques "Add .gitignore" (ya tenemos uno)
   - **License**: MIT (opcional)

### 2. Conectar el Repositorio Local con GitHub

Una vez creado el repositorio en GitHub, usa estos comandos:

```bash
# Añadir el repositorio remoto
git remote add origin https://github.com/TU_USUARIO/fase-4-scraper-alertas-consensos.git

# Cambiar a la rama main (GitHub usa main por defecto)
git branch -M main

# Subir los archivos al repositorio
git push -u origin main
```

### 3. Configurar GitHub Secrets (Importante)

Para proteger las credenciales sensibles, configura estos secrets en GitHub:

1. Ve a tu repositorio en GitHub
2. Haz clic en "Settings" → "Secrets and variables" → "Actions"
3. Añade estos secrets:

```
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase
TELEGRAM_BOT_TOKEN=tu_token_de_bot_telegram
TELEGRAM_CHAT_ID=tu_chat_id_telegram
```

## 📁 Estructura del Proyecto Subido

```
fase-4-scraper-alertas-consensos/
├── .gitignore                    # Archivos ignorados por Git
├── README.md                     # Documentación principal
├── CONFIGURACION_PROYECTO.md     # Configuración detallada
├── main.py                       # Punto de entrada principal
├── requirements.txt              # Dependencias Python
├── config/
│   ├── .env.example             # Ejemplo de variables de entorno
│   ├── settings.py              # Configuración principal
│   └── sports_config.json       # Configuración de deportes
├── docs/
│   ├── telegram_setup.md        # Guía de configuración Telegram
│   └── github_setup.md          # Esta guía
├── src/
│   ├── __init__.py
│   ├── enhanced_consensus_system.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── supabase_client.py
│   ├── notifications/
│   │   ├── __init__.py
│   │   └── telegram_bot.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── mlb_scraper.py
│   │   ├── scheduler.py
│   │   └── pregame_scheduler.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── error_handler.py
│   │   ├── logger.py
│   │   └── sports_config.py
│   └── web/
│       ├── __init__.py
│       └── app.py
└── tests/
    ├── __init__.py
    └── test_scraper.py
```

## 🚀 Próximos Pasos

1. **Crear el repositorio en GitHub** siguiendo las instrucciones anteriores
2. **Configurar los secrets** para proteger las credenciales
3. **Clonar el repositorio** en el entorno de producción
4. **Configurar las variables de entorno** copiando `.env.example` a `.env`
5. **Instalar dependencias** con `pip install -r requirements.txt`
6. **Ejecutar las pruebas** para validar el funcionamiento

## 📝 Comandos Útiles

```bash
# Ver el estado del repositorio
git status

# Ver los commits
git log --oneline

# Crear una nueva rama para desarrollo
git checkout -b desarrollo

# Actualizar el repositorio remoto
git push origin main

# Obtener cambios del repositorio remoto
git pull origin main
```

## 🔒 Consideraciones de Seguridad

- **NUNCA** subas archivos `.env` con credenciales reales
- Usa **GitHub Secrets** para variables sensibles
- Mantén el repositorio como **privado** si contiene lógica de negocio sensible
- Revisa regularmente los **permisos de acceso** al repositorio

## 📞 Soporte

Para cualquier problema con la configuración de GitHub, consulta:
- [Documentación oficial de GitHub](https://docs.github.com/)
- [Guía de Git](https://git-scm.com/doc)
- El archivo `CONFIGURACION_PROYECTO.md` para detalles específicos del proyecto
