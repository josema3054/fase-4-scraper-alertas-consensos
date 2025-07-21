@echo off
title DIAGNOSTICO DEL SCRAPER
color 0A
cls

echo.
echo ===============================================
echo     DIAGNOSTICO COMPLETO DEL SCRAPER MLB
echo ===============================================
echo.

cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"

echo Ejecutando diagnostico...
echo.

python diagnostico_completo.py

echo.
echo ===============================================
echo DIAGNOSTICO COMPLETADO
echo ===============================================
echo.
echo Revisa los resultados mostrados arriba
echo Se creo el archivo 'sample_html.txt' con una muestra del HTML
echo.
pause
