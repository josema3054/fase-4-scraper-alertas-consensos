# Script de inicialización para Windows PowerShell
# Ejecuta este script para configurar el proyecto Fase 4

Write-Host "============================================" -ForegroundColor Green
Write-Host "  INICIALIZANDO PROYECTO FASE 4" -ForegroundColor Green
Write-Host "  Scraper y Alertas Deportivas" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Función para mostrar mensajes con colores
function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Write-Info($message) {
    Write-Host "💡 $message" -ForegroundColor Cyan
}

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "main.py")) {
    Write-Error "Este script debe ejecutarse desde el directorio raíz del proyecto"
    exit 1
}

Write-Success "Directorio del proyecto verificado"

# Verificar Python
Write-Host "`n--- Verificando Python ---" -ForegroundColor Blue
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python encontrado: $pythonVersion"
} catch {
    Write-Error "Python no encontrado. Instala Python 3.8+ desde https://python.org"
    exit 1
}

# Verificar Git
Write-Host "`n--- Verificando Git ---" -ForegroundColor Blue
try {
    $gitVersion = git --version 2>&1
    Write-Success "Git encontrado: $gitVersion"
} catch {
    Write-Error "Git no encontrado. Instala Git desde https://git-scm.com"
    exit 1
}

# Crear entorno virtual si no existe
Write-Host "`n--- Configurando entorno virtual ---" -ForegroundColor Blue
if (-not (Test-Path "venv")) {
    Write-Info "Creando entorno virtual..."
    python -m venv venv
    Write-Success "Entorno virtual creado"
} else {
    Write-Success "Entorno virtual ya existe"
}

# Activar entorno virtual
Write-Info "Activando entorno virtual..."
& "venv\Scripts\Activate.ps1"

# Instalar dependencias
Write-Host "`n--- Instalando dependencias ---" -ForegroundColor Blue
if (Test-Path "requirements.txt") {
    Write-Info "Instalando dependencias de Python..."
    pip install -r requirements.txt
    Write-Success "Dependencias instaladas"
} else {
    Write-Error "Archivo requirements.txt no encontrado"
}

# Crear archivo .env si no existe
Write-Host "`n--- Configurando variables de entorno ---" -ForegroundColor Blue
if (-not (Test-Path "config\.env")) {
    if (Test-Path "config\.env.example") {
        Copy-Item "config\.env.example" "config\.env"
        Write-Success "Archivo .env creado desde .env.example"
        Write-Warning "¡IMPORTANTE! Edita config\.env con tus credenciales reales"
    } else {
        Write-Error "Archivo config\.env.example no encontrado"
    }
} else {
    Write-Success "Archivo .env ya existe"
}

# Crear directorios necesarios
Write-Host "`n--- Creando directorios ---" -ForegroundColor Blue
$directories = @("logs", "backups", "data", "temp")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Success "Directorio creado: $dir"
    } else {
        Write-Success "Directorio ya existe: $dir"
    }
}

# Verificar estructura del proyecto
Write-Host "`n--- Verificando estructura del proyecto ---" -ForegroundColor Blue
$requiredFiles = @(
    "main.py",
    "requirements.txt",
    "config\settings.py",
    "config\sports_config.json",
    "src\enhanced_consensus_system.py",
    "src\database\supabase_client.py",
    "src\notifications\telegram_bot.py",
    "src\scraper\mlb_scraper.py",
    "src\web\app.py",
    "README.md"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Success "Archivo encontrado: $file"
    } else {
        Write-Error "Archivo faltante: $file"
        $missingFiles += $file
    }
}

# Ejecutar script de inicialización Python
Write-Host "`n--- Ejecutando validación completa ---" -ForegroundColor Blue
if (Test-Path "init_project.py") {
    python init_project.py
} else {
    Write-Warning "Script de inicialización Python no encontrado"
}

# Mostrar información final
Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  CONFIGURACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

if ($missingFiles.Count -eq 0) {
    Write-Success "¡Proyecto configurado exitosamente!"
    Write-Host "`n🚀 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "1. Edita config\.env con tus credenciales reales"
    Write-Host "2. Ejecuta las pruebas: python -m pytest tests/"
    Write-Host "3. Inicia la aplicación: python main.py"
    Write-Host "4. Accede a la web: http://localhost:8501"
    
    Write-Host "`n📚 Documentación disponible:" -ForegroundColor Cyan
    Write-Host "- README.md"
    Write-Host "- CONFIGURACION_PROYECTO.md"
    Write-Host "- docs\telegram_setup.md"
    Write-Host "- docs\github_setup.md"
} else {
    Write-Error "Faltan archivos importantes. Revisa la instalación."
    Write-Host "Archivos faltantes:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
}

Write-Host "`n💡 Para activar el entorno virtual en futuras sesiones:" -ForegroundColor Cyan
Write-Host "   venv\Scripts\Activate.ps1"
