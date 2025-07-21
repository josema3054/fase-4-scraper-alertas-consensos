# Script para ejecutar la interfaz web de Streamlit
# Fase 4 - Scraper de Alertas y Consensos

Write-Host "========================================" -ForegroundColor Blue
Write-Host "       INICIANDO INTERFAZ WEB          " -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Cambiar al directorio del script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

Write-Host "📁 Directorio: $scriptPath" -ForegroundColor Green

# Verificar Python
Write-Host "🐍 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Write-Host "Por favor instale Python desde: https://python.org" -ForegroundColor Yellow
    Read-Host "Presione Enter para continuar"
    exit 1
}

# Verificar Streamlit
Write-Host "🌐 Verificando Streamlit..." -ForegroundColor Yellow
python -m streamlit --version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Streamlit no encontrado" -ForegroundColor Red
    Write-Host "📦 Instalando Streamlit..." -ForegroundColor Yellow
    python -m pip install streamlit
}

Write-Host ""
Write-Host "🚀 Iniciando interfaz web..." -ForegroundColor Green
Write-Host "🌐 Se abrirá automáticamente en: http://localhost:8502" -ForegroundColor Cyan
Write-Host "🛑 Para detener: Cierre esta ventana o presione Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Ejecutar la interfaz web
try {
    python ejecutar_interfaz_web.py
} catch {
    Write-Host "❌ Error al ejecutar la interfaz web" -ForegroundColor Red
    Write-Host "💡 Intente ejecutar manualmente:" -ForegroundColor Yellow
    Write-Host "   streamlit run src/web/app.py --server.port 8502" -ForegroundColor White
}

Write-Host ""
Write-Host "Interfaz web finalizada." -ForegroundColor Green
Read-Host "Presione Enter para continuar"
