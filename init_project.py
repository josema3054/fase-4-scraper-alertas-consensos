#!/usr/bin/env python3
"""
Script de inicialización y validación del proyecto Fase 4
Ejecuta este script para verificar que todo esté configurado correctamente
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    """Imprime un encabezado decorativo"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime un mensaje de error"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprime un mensaje de advertencia"""
    print(f"⚠️  {message}")

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    print_header("Verificando versión de Python")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado - Compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} detectado - Se requiere Python 3.8+")
        return False

def check_required_files():
    """Verifica que todos los archivos requeridos estén presentes"""
    print_header("Verificando archivos del proyecto")
    
    required_files = [
        "requirements.txt",
        "main.py",
        "config/settings.py",
        "config/sports_config.json",
        "src/enhanced_consensus_system.py",
        "src/database/supabase_client.py",
        "src/notifications/telegram_bot.py",
        "src/scraper/mlb_scraper.py",
        "src/web/app.py",
        "docs/telegram_setup.md",
        "docs/github_setup.md",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Archivo encontrado: {file_path}")
        else:
            print_error(f"Archivo faltante: {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_env_configuration():
    """Verifica la configuración de variables de entorno"""
    print_header("Verificando configuración de entorno")
    
    env_example = Path("config/.env.example")
    env_file = Path("config/.env")
    
    if env_example.exists():
        print_success("Archivo .env.example encontrado")
    else:
        print_error("Archivo .env.example no encontrado")
    
    if env_file.exists():
        print_success("Archivo .env encontrado")
        print_warning("Recuerda verificar que todas las variables estén configuradas correctamente")
    else:
        print_warning("Archivo .env no encontrado")
        print("💡 Copia config/.env.example a config/.env y configura tus credenciales")

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print_header("Verificando dependencias de Python")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split("\n")
        
        missing_deps = []
        for req in requirements:
            if req and not req.startswith("#"):
                package = req.split("==")[0].split(">=")[0].split("<=")[0]
                try:
                    __import__(package.replace("-", "_"))
                    print_success(f"Dependencia instalada: {package}")
                except ImportError:
                    print_error(f"Dependencia faltante: {package}")
                    missing_deps.append(package)
        
        if missing_deps:
            print_warning("Instala las dependencias faltantes con: pip install -r requirements.txt")
            return False
        else:
            print_success("Todas las dependencias están instaladas")
            return True
            
    except FileNotFoundError:
        print_error("Archivo requirements.txt no encontrado")
        return False

def check_sports_config():
    """Verifica la configuración de deportes"""
    print_header("Verificando configuración de deportes")
    
    config_file = Path("config/sports_config.json")
    if not config_file.exists():
        print_error("Archivo config/sports_config.json no encontrado")
        return False
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        required_sports = ["mlb", "nba", "nfl", "nhl"]
        for sport in required_sports:
            if sport in config:
                print_success(f"Configuración de {sport.upper()} encontrada")
            else:
                print_error(f"Configuración de {sport.upper()} faltante")
        
        if "global_settings" in config:
            print_success("Configuración global encontrada")
        else:
            print_error("Configuración global faltante")
        
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"Error al leer config/sports_config.json: {e}")
        return False

def check_git_repository():
    """Verifica el estado del repositorio Git"""
    print_header("Verificando repositorio Git")
    
    git_dir = Path(".git")
    if not git_dir.exists():
        print_error("No se encontró repositorio Git inicializado")
        return False
    
    try:
        # Verificar estado del repositorio
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print_warning("Hay cambios sin commit en el repositorio")
        else:
            print_success("Repositorio Git está limpio")
        
        # Verificar si hay remote configurado
        result = subprocess.run(["git", "remote", "-v"], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print_success("Remote de Git configurado")
        else:
            print_warning("No hay remote configurado - consulta docs/github_setup.md")
        
        return True
        
    except subprocess.CalledProcessError:
        print_error("Error al verificar el estado de Git")
        return False

def create_initial_directories():
    """Crea directorios necesarios que podrían no existir"""
    print_header("Creando directorios necesarios")
    
    directories = [
        "logs",
        "backups",
        "data",
        "temp"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Directorio creado: {directory}")
        else:
            print_success(f"Directorio ya existe: {directory}")

def main():
    """Función principal del script de inicialización"""
    print_header("INICIALIZANDO PROYECTO FASE 4 - SCRAPER Y ALERTAS DEPORTIVAS")
    
    all_checks_passed = True
    
    # Ejecutar todas las verificaciones
    checks = [
        check_python_version,
        check_required_files,
        check_env_configuration,
        check_dependencies,
        check_sports_config,
        check_git_repository
    ]
    
    for check in checks:
        if not check():
            all_checks_passed = False
    
    # Crear directorios necesarios
    create_initial_directories()
    
    # Resultado final
    print_header("RESULTADO DE LA INICIALIZACIÓN")
    
    if all_checks_passed:
        print_success("¡Proyecto inicializado correctamente!")
        print("\n🚀 Próximos pasos:")
        print("1. Configura tus credenciales en config/.env")
        print("2. Ejecuta las pruebas con: python -m pytest tests/")
        print("3. Inicia la aplicación con: python main.py")
        print("4. Accede a la interfaz web en: http://localhost:8501")
        print("\n📚 Documentación disponible en:")
        print("- README.md - Información general")
        print("- CONFIGURACION_PROYECTO.md - Configuración detallada")
        print("- docs/telegram_setup.md - Configuración de Telegram")
        print("- docs/github_setup.md - Configuración de GitHub")
    else:
        print_error("Hay problemas que deben solucionarse antes de continuar")
        print("\n🔧 Revisa los errores anteriores y:")
        print("1. Instala las dependencias faltantes")
        print("2. Configura los archivos requeridos")
        print("3. Ejecuta este script nuevamente")
        sys.exit(1)

if __name__ == "__main__":
    main()
