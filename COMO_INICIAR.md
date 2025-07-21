# 🚀 CÓMO INICIAR EL SISTEMA

## 📋 ARCHIVO PRINCIPAL PARA EJECUTAR EL SOFTWARE

### 🌟 **ARCHIVO ÚNICO - INICIO DEL SISTEMA**
```
📁 Hacer doble clic en: INICIAR_SISTEMA.bat
```
- ✅ **MENÚ COMPLETO** con todas las opciones
- ✅ **Interfaz visual mejorada** con arte ASCII
- ✅ **Opciones numeradas** fáciles de usar
- ✅ **Verificación automática** de entorno y dependencias

### 🎯 **OPCIONES DISPONIBLES EN EL MENÚ:**

1. **� INICIAR SISTEMA (Interfaz Web)**
   - Abre la interfaz web completa
   - Se abre automáticamente en el navegador
   - Acceso a scraping, configuración y visualización

2. **🧪 PROBAR SCRAPER CON DATOS REALES**
   - Ejecuta prueba con datos en vivo
   - Verifica extracción de expertos
   - Muestra partidos que cumplen criterios

3. **⚙️ CONFIGURACIÓN DEL SISTEMA**
   - Muestra configuración actual
   - Instrucciones para cambiar valores
   - Umbral y número mínimo de expertos

4. **📊 VER ESTADO DEL SISTEMA**
   - Estado de Python y dependencias
   - Verificación de módulos
   - Información del entorno virtual

5. **🔄 REINICIAR CACHE DE LA APLICACIÓN**
   - Limpia cache de Python y Streamlit
   - Recarga módulos del código
   - **Usar después de hacer cambios en el código**

6. **🚪 SALIR**
   - Cierra el sistema de forma segura

## 🎯 PASOS RÁPIDOS PARA EMPEZAR

1. **Hacer doble clic en `INICIAR_SISTEMA.bat`**
2. **Seleccionar opción 1: INICIAR SISTEMA**
3. **Esperar a que se abra el navegador**
4. **Ir a la pestaña "🕷️ Scraping Actual"**
5. **Hacer clic en "🔄 Ejecutar Scraping Manual"**
6. **Ver los partidos que cumplen los criterios**

---

## 📊 QUÉ VAS A VER

El sistema te mostrará solo los partidos de totales MLB que:
- ✅ Tengan consenso >= 64%
- ✅ Tengan >= 13 expertos votando

### Ejemplo de resultado de hoy (18 julio 2025):
- **Yankees @ Braves** - 80% OVER, 41 expertos ✅
- **Athletics @ Guardians** - 76% UNDER, 134 expertos ✅
- **White Sox @ Pirates** - 76% UNDER, 134 expertos ✅

---

## 🔧 CONFIGURACIÓN

Para cambiar los valores de umbral (64%) o expertos mínimos (13):
1. Abre la interfaz web (`INICIAR_WEB.bat`)
2. Ve a la pestaña "⚙️ Configuración"
3. Modifica los valores
4. Haz clic en "Guardar Configuración"

---

## ❓ PROBLEMAS COMUNES

### Si no funciona:
1. Verifica que tengas Python instalado
2. Ejecuta `setup_windows.ps1` primero
3. O usa `ejecutar_software.bat` que instala dependencias automáticamente

### Si el navegador no se abre:
- Ve manualmente a: http://localhost:8501

### Si los cambios en el código no se ven:
1. **USA LA OPCIÓN DE REINICIAR CACHE:**
   - Ejecuta `INICIAR_SISTEMA.bat` 
   - Selecciona opción 5: "Reiniciar cache"
2. Luego selecciona opción 1 para iniciar la interfaz web
3. **Alternativa rápida:** Ejecuta `REINICIAR_CACHE.bat` directamente

### Si la aplicación se comporta de manera extraña:
1. Ejecuta `INICIAR_SISTEMA.bat`
2. Selecciona opción 5 (Reiniciar cache)
3. Cierra todas las instancias de la aplicación
4. Reinicia el terminal/consola
5. Vuelve a ejecutar opción 1

---

## 📞 SOPORTE

- 📄 Logs del sistema en: `logs/`
- 📊 Resultados de pruebas en: archivos `.json`
- 🔧 Configuración en: `config/.env`
