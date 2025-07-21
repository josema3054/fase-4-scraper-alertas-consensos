@echo off
chcp 65001 >nul
title SOFTWARE FASE 4 - CONSENSOS MLB
color 0A

:inicio
cls
echo.
echo ========================================================
echo         SISTEMA DE CONSENSOS MLB - TOTALES
echo ========================================================
echo.
echo Filtros actuales: 66%% umbral, 16 expertos minimos
echo Solo totales Over/Under de covers.com
echo.

cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"

echo Activando entorno virtual...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo    Entorno virtual activado
) else (
    echo    Entorno virtual no encontrado
    echo    Usando Python del sistema
)

echo Verificando dependencias...
pip install -q -r requirements.txt >nul 2>&1
echo    Dependencias verificadas

echo.
echo ========================================================
echo                OPCIONES DISPONIBLES
echo ========================================================
echo.
echo 1. INICIAR SISTEMA (Interfaz Web)
echo 2. PROBAR SCRAPER CON DATOS REALES
echo 3. DIAGNOSTICO COMPLETO DEL PROBLEMA
echo 4. CONFIGURACION DEL SISTEMA
echo 5. VER ESTADO DEL SISTEMA
echo 6. REINICIAR CACHE DE LA APLICACION
echo 7. SALIR
echo.
echo ========================================================

:menu
echo.
set /p choice="Selecciona una opcion (1-7): "

if "%choice%"=="1" goto iniciar_sistema
if "%choice%"=="2" goto test_scraper
if "%choice%"=="3" goto diagnostico_completo
if "%choice%"=="4" goto configurar
if "%choice%"=="5" goto estado
if "%choice%"=="6" goto reiniciar_cache
if "%choice%"=="7" goto salir

echo Opcion invalida, intenta de nuevo.
goto menu

:iniciar_sistema
cls
echo.
echo INICIANDO SISTEMA - INTERFAZ WEB
echo ========================================================
echo.
echo Verificando que el archivo de la aplicacion existe...
if exist "src\web\app.py" (
    echo    Archivo de aplicacion encontrado
) else (
    echo    ERROR: No se encuentra src\web\app.py
    echo    Verifica que estes en el directorio correcto
    pause
    goto inicio
)

echo La interfaz se abrira automaticamente en: http://localhost:8501
echo Para cerrar la aplicacion, presiona Ctrl+C
echo Si hiciste cambios en el codigo, usa opcion 6 primero
echo.
echo ========================================================
echo Iniciando Streamlit...
timeout /t 3 /nobreak >nul
start http://localhost:8501
echo Ejecutando: streamlit run src/web/app.py --server.port 8501
streamlit run src/web/app.py --server.port 8501
if errorlevel 1 (
    echo.
    echo ERROR: Fallo al iniciar Streamlit
    echo Sugerencias:
    echo    1. Verifica que Python este funcionando
    echo    2. Ejecuta la opcion 5 para ver estado del sistema
    echo    3. Prueba la opcion 6 para reiniciar cache
    echo.
    pause
)
goto menu

:test_scraper
cls
echo.
echo DIAGNOSTICO URGENTE DEL SCRAPER
echo ========================================================
echo.
echo Ejecutando diagnostico detallado...
python urgent_diagnosis.py
echo.
echo ========================================================
echo El diagnostico mostrara exactamente donde esta el problema
echo.
pause
goto inicio

:diagnostico_completo
cls
echo.
echo DIAGNOSTICO COMPLETO DEL PROBLEMA
echo ========================================================
echo.
echo Este diagnostico mostrara EXACTAMENTE donde esta el problema
echo Analizara la estructura real de covers.com
echo Identificara que selectores necesitamos usar
echo.
echo Ejecutando diagnostico completo (puede tardar 30-60 segundos)...
python diagnostico_completo.py
echo.
echo ========================================================
echo Revisa la salida anterior para entender el problema
echo Se creo 'sample_html.txt' con una muestra del HTML
echo.
pause
goto inicio

:configurar
cls
echo.
echo CONFIGURACION DEL SISTEMA
echo ========================================================
echo.
python -c "from config.settings import Settings; s = Settings(); print(f'    Umbral actual: {s.MLB_CONSENSUS_THRESHOLD}%%'); print(f'    Expertos minimos: {s.MIN_EXPERTS_VOTING}')"
echo.
echo Para cambiar la configuracion:
echo    1. Usa la interfaz web (opcion 1)
echo    2. Ve a la pestana "Configuracion"
echo    3. Modifica los valores y guarda
echo.
echo ========================================================
pause
goto inicio

:estado
cls
echo.
echo ESTADO DEL SISTEMA
echo ========================================================
echo.
echo Directorio: %cd%
if defined VIRTUAL_ENV (
    echo    Entorno virtual: %VIRTUAL_ENV%
) else (
    echo    Entorno virtual: No activado
)
python -c "import sys; print(f'    Python: {sys.version.split()[0]}')"
python -c "try: import streamlit; print('    Streamlit: Disponible'); except: print('    Streamlit: No disponible')"
python -c "try: from src.scraper.mlb_scraper import MLBScraper; print('    Scraper: Disponible'); except Exception as e: print(f'    Scraper: Error - {e}')"
echo.
echo ========================================================
pause
goto inicio

:reiniciar_cache
cls
echo.
echo REINICIANDO CACHE DE LA APLICACION
echo ========================================================
echo.
echo Ejecutando script de limpieza completa...
python reiniciar_cache.py
echo.
echo Cache reiniciado correctamente
echo Los cambios en el codigo se aplicaran en la proxima ejecucion
echo.
echo Sugerencia: Usa opcion 1 para iniciar con cache limpio
echo.
echo ========================================================
pause
goto inicio

:salir
cls
echo.
echo HASTA LUEGO!
echo ========================================================
echo.
echo Recuerda:
echo    - Los datos se guardan automaticamente
echo    - Puedes volver a ejecutar cuando quieras
echo    - Si hay problemas, usa la opcion 6 (Reiniciar cache)
echo.
timeout /t 3 /nobreak >nul
exit
