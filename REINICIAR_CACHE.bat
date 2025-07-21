@echo off
echo ============================================
echo   🔄 REINICIAR CACHE - CONSENSOS MLB
echo ============================================

cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"

echo Activando entorno virtual...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✅ Entorno virtual activado
) else (
    echo ⚠️  Entorno virtual no encontrado, usando Python del sistema
)

echo.
echo � Ejecutando limpieza completa de cache...
python reiniciar_cache.py

echo.
echo ============================================
echo   ✅ PROCESO COMPLETADO
echo ============================================
echo.
echo 🎯 Próximos pasos recomendados:
echo    1. Cierra cualquier instancia de la aplicación web
echo    2. Reinicia el terminal si es necesario
echo    3. Usa ejecutar_software.bat opción 1 para la interfaz web
echo.

pause
