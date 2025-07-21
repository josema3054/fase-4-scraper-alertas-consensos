@echo off
echo ========================================
echo    ABRIENDO APLICACION WEB
echo ========================================
echo.

cd /d "%~dp0"

echo 🌐 Ejecutando aplicacion web Streamlit...
echo 📍 URL: http://localhost:8502
echo 🔄 Espera a que aparezca "You can now view your Streamlit app"
echo ⚡ Se abrira automaticamente en el navegador...
echo.

python -m streamlit run src\web\app.py --server.port 8502 --server.headless false

echo.
echo ❌ La aplicacion se ha cerrado.
pause
