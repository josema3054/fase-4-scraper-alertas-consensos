@echo off
title CONSENSOS MLB - MENU SIMPLE
cls
echo.
echo ========================================
echo    SISTEMA CONSENSOS MLB - TOTALES
echo ========================================
echo.
echo 1. Iniciar Interfaz Web
echo 2. Probar Scraper  
echo 3. Ver Estado
echo 4. Reiniciar Cache
echo 5. Salir
echo.
echo ========================================

:menu
set /p choice="Selecciona opción (1-5): "

if "%choice%"=="1" goto web
if "%choice%"=="2" goto test
if "%choice%"=="3" goto status
if "%choice%"=="4" goto cache
if "%choice%"=="5" goto exit

echo Opción inválida
goto menu

:web
cls
echo.
echo INICIANDO INTERFAZ WEB...
echo ========================
echo.
cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"

if exist "src\web\app.py" (
    echo ✅ Archivo encontrado
) else (
    echo ❌ ERROR: No se encuentra src\web\app.py
    pause
    goto menu
)

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Abriendo navegador en 3 segundos...
timeout /t 3 /nobreak >nul
start http://localhost:8501

echo.
echo EJECUTANDO STREAMLIT...
echo Presiona Ctrl+C para cerrar
echo.
streamlit run src/web/app.py --server.port 8501
goto menu

:test
cls
echo.
echo PROBANDO SCRAPER...
echo ===================
cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"
python test_scraper.py
echo.
pause
goto menu

:status
cls
echo.
echo ESTADO DEL SISTEMA...
echo ====================
cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"
python -c "import sys; print(f'Python: {sys.version}')"
python -c "try: import streamlit; print('Streamlit: OK'); except: print('Streamlit: ERROR')"
python -c "try: from src.scraper.mlb_scraper import MLBScraper; print('Scraper: OK'); except Exception as e: print(f'Scraper: ERROR - {e}')"
echo.
pause
goto menu

:cache
cls
echo.
echo REINICIANDO CACHE...
echo ===================
cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"
python reiniciar_cache.py
echo.
pause
goto menu

:exit
echo.
echo ¡Hasta luego!
timeout /t 2 /nobreak >nul
exit
