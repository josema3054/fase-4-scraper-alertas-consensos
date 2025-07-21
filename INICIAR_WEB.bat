@echo off
echo ============================================
echo   🌐 INICIANDO INTERFAZ WEB - FASE 4
echo   Consensos de Totales MLB
echo ============================================

cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"

echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

echo 🚀 Iniciando aplicación web...
echo.
echo ➡️  La interfaz se abrirá en: http://localhost:8501
echo ➡️  Para cerrar, presiona Ctrl+C en esta ventana
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8501
streamlit run src/web/app.py --server.port 8501

pause
