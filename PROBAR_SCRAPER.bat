@echo off
echo ============================================
echo   🧪 PRUEBA DEL SCRAPER - FASE 4
echo   Datos reales de consensos de hoy
echo ============================================

cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"

echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

echo 🕷️ Ejecutando scraper con filtros...
echo.
python test_filter_totales.py

echo.
echo ✅ Prueba completada. Revisa los resultados arriba.
echo 📄 Datos guardados en: filter_results.json
echo.
pause
