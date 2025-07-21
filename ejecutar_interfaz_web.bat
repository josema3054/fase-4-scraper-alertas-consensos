@echo off
echo ========================================
echo       INICIANDO INTERFAZ WEB
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Python no encontrado
    echo Por favor instale Python desde: https://python.org
    pause
    exit /b 1
)

echo.
echo Verificando Streamlit...
python -m streamlit --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Streamlit no encontrado
    echo Instalando Streamlit...
    python -m pip install streamlit
)

echo.
echo 🚀 Iniciando interfaz web...
echo 🌐 Se abrirá automáticamente en: http://localhost:8503
echo 🛑 Para detener: Cierre esta ventana o presione Ctrl+C
echo.

REM Usar el Python del entorno virtual si existe
if exist "venv\Scripts\python.exe" (
    echo Usando entorno virtual...
    "venv\Scripts\python.exe" -m streamlit run src\web\app.py --server.port 8503
) else (
    echo Usando Python del sistema...
    python -m streamlit run src\web\app.py --server.port 8503
)

echo.
echo Interfaz web finalizada.
pause
