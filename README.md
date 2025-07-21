# 🚀 CÓMO USAR EL SISTEMA

## 📋 INICIO RÁPIDO

### **Hacer doble clic en: `INICIAR_SISTEMA.bat`**

### Opciones del menú:

1. **🚀 INICIAR SISTEMA** - Abre la interfaz web
2. **🧪 PROBAR SCRAPER** - Test rápido con datos reales  
3. **⚙️ CONFIGURACIÓN** - Ver/cambiar settings (64% umbral, 13 expertos)
4. **📊 ESTADO SISTEMA** - Verificar que todo funciona
5. **🔄 REINICIAR CACHE** - Usar después de cambios en código
6. **🚪 SALIR** - Cerrar

---

## 🎯 USO NORMAL

1. **Doble clic en `INICIAR_SISTEMA.bat`**
2. **Opción 1** → Se abre el navegador automáticamente
3. **Ir a "🕷️ Scraping Actual"**
4. **Clic en "🔄 Ejecutar Scraping Manual"**
5. **Ver partidos que cumplen: ≥64% consenso + ≥13 expertos**

---

## 🔧 SI HAY PROBLEMAS

### **Si la opción 1 no hace nada:**
1. Usa `INICIO_SIMPLE.bat` como alternativa
2. O ejecuta manualmente:
   ```
   streamlit run src/web/app.py --server.port 8501
   ```
3. Verifica estado con opción 4

### **Otros problemas:**
- **Cambios no se ven**: Opción 5 (Reiniciar cache) → Opción 1
- **Error general**: Opción 4 (Estado sistema) para diagnosticar
- **Interfaz no abre**: Ir manualmente a http://localhost:8501

---

## 📊 QUÉ VERÁS

El sistema muestra solo partidos MLB totales que cumplen:
- ✅ Consenso ≥ 64%
- ✅ ≥ 13 expertos votando

**Ejemplo:** Yankees @ Braves - 80% OVER, 41 expertos ✅
