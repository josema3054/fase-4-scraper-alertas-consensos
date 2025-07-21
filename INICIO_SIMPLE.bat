@echo off
echo 🚀 INICIANDO INTERFAZ WEB - SIMPLE
echo ================================

cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"

echo 📁 Directorio: %cd%

if exist "src\web\app.py" (
    echo ✅ Archivo encontrado: src\web\app.py
) else (
    echo ❌ ERROR: No se encuentra src\web\app.py
    pause
    exit
)

echo 🔧 Activando entorno virtual...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✅ Entorno activado
) else (
    echo ⚠️ Usando Python del sistema
)

echo 🧪 Probando Python...
python -c "print('✅ Python funcionando')"

echo 🧪 Probando Streamlit...
python -c "import streamlit; print('✅ Streamlit disponible')"

echo 🌐 Iniciando aplicación web...
echo ➡️ Se abrirá en: http://localhost:8501
echo ➡️ Para cerrar: Ctrl+C

timeout /t 2 /nobreak >nul
start http://localhost:8501

echo.
echo 🚀 Ejecutando streamlit...
streamlit run src/web/app.py --server.port 8501

echo.
echo 👋 Aplicación cerrada
pause
