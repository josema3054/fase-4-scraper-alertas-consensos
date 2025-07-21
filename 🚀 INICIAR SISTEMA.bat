@echo off
title SOFTWARE FASE 4 - CONSENSOS MLB
color 0A

:inicio
cls
echo.
echo    ██████╗ ██╗  ██╗ █████╗ ███████╗███████╗    ██╗  ██╗
echo    ██╔══██╗██║  ██║██╔══██╗██╔════╝██╔════╝    ██║  ██║
echo    ██████╔╝███████║███████║███████╗█████╗      ███████║
echo    ██╔═══╝ ██╔══██║██╔══██║╚════██║██╔══╝      ╚════██║
echo    ██║     ██║  ██║██║  ██║███████║███████╗         ██║
echo    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝         ╚═╝
echo.
echo    ═══════════════════════════════════════════════════════
echo              SISTEMA DE CONSENSOS MLB - TOTALES
echo    ═══════════════════════════════════════════════════════
echo.
echo    📊 Filtros actuales: 64%% umbral, 13 expertos mínimos
echo    🎯 Solo totales Over/Under de covers.com
echo.
echo    ═══════════════════════════════════════════════════════
echo.
echo    🌟 1. INICIAR INTERFAZ WEB (Recomendado)
echo    🧪 2. PROBAR SCRAPER CON DATOS REALES  
echo    ⚙️  3. CONFIGURACIÓN AVANZADA
echo    📋 4. VER ESTADO DEL SISTEMA
echo    🚪 5. SALIR
echo.
echo    ═══════════════════════════════════════════════════════

set /p opcion="    ➤ Selecciona una opción (1-5): "

if "%opcion%"=="1" goto web
if "%opcion%"=="2" goto test
if "%opcion%"=="3" goto config
if "%opcion%"=="4" goto estado  
if "%opcion%"=="5" goto salir

echo.
echo    ❌ Opción inválida. Presiona cualquier tecla e intenta de nuevo.
pause >nul
goto inicio

:web
cls
echo.
echo    🌐 INICIANDO INTERFAZ WEB...
echo    ═══════════════════════════════════════════════════════
echo.
echo    ➤ La aplicación se abrirá en tu navegador
echo    ➤ URL: http://localhost:8501
echo    ➤ Para cerrar: presiona Ctrl+C aquí
echo.
call INICIAR_WEB.bat
goto inicio

:test
cls
echo.
echo    🧪 PROBANDO SCRAPER...
echo    ═══════════════════════════════════════════════════════
call PROBAR_SCRAPER.bat
goto inicio

:config
cls
echo.
echo    ⚙️ CONFIGURACIÓN AVANZADA
echo    ═══════════════════════════════════════════════════════
call ejecutar_software.bat
goto inicio

:estado
cls
echo.
echo    📋 ESTADO DEL SISTEMA
echo    ═══════════════════════════════════════════════════════
echo.
cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"
call venv\Scripts\activate.bat
python -c "
from config.settings import Settings
import os
s = Settings()
print(f'    ✅ Directorio: {os.getcwd()}')
print(f'    ✅ Umbral configurado: {s.MLB_CONSENSUS_THRESHOLD}%%')
print(f'    ✅ Expertos mínimos: {s.MIN_EXPERTS_VOTING}')
print(f'    ✅ Entorno virtual activo')
try:
    import streamlit
    print('    ✅ Streamlit disponible')
except:
    print('    ❌ Streamlit no disponible')
try:
    from src.scraper.mlb_scraper import MLBScraper
    print('    ✅ Scraper MLB disponible')
except:
    print('    ❌ Scraper no disponible')
"
echo.
echo    ═══════════════════════════════════════════════════════
pause
goto inicio

:salir
cls
echo.
echo    ═══════════════════════════════════════════════════════
echo                        👋 ¡HASTA LUEGO!
echo    ═══════════════════════════════════════════════════════
echo.
timeout /t 2 /nobreak >nul
exit
