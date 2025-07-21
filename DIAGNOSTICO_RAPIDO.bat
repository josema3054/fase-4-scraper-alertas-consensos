@echo off
title DIAGNOSTICO RAPIDO - SCRAPER MLB
color 0A

cls
echo.
echo    DIAGNOSTICO RAPIDO DEL SCRAPER MLB
echo    =========================================
echo.
echo    Analizando covers.com...

cd /d "c:\Users\JVILLA\Desktop\fase-4-scraper-alertas-consensos"

python diagnostico_completo.py

echo.
echo    Diagnostico completado
echo    Revisa el archivo 'sample_html.txt' creado
echo.
pause
