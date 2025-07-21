#!/usr/bin/env python3
"""
Script para reiniciar completamente el cache del sistema
Limpia cache de Python, Streamlit y fuerza la recarga de módulos
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def limpiar_cache_python():
    """Elimina archivos __pycache__ y .pyc"""
    print("🔄 Limpiando cache de Python...")
    
    # Obtener directorio base del proyecto
    base_dir = Path(__file__).parent
    
    # Contar archivos eliminados
    pycache_count = 0
    pyc_count = 0
    
    # Eliminar directorios __pycache__
    for pycache_dir in base_dir.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            pycache_count += 1
            print(f"   ✅ Eliminado: {pycache_dir}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando {pycache_dir}: {e}")
    
    # Eliminar archivos .pyc
    for pyc_file in base_dir.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            pyc_count += 1
            print(f"   ✅ Eliminado: {pyc_file}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando {pyc_file}: {e}")
    
    print(f"   📊 Total: {pycache_count} directorios __pycache__ y {pyc_count} archivos .pyc eliminados")

def limpiar_cache_streamlit():
    """Elimina cache de Streamlit"""
    print("🌐 Limpiando cache de Streamlit...")
    
    streamlit_cache_dirs = [
        Path.home() / ".streamlit" / "cache",
        Path.home() / ".streamlit" / "cache_resource_state",
        Path(".streamlit") / "cache"
    ]
    
    for cache_dir in streamlit_cache_dirs:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                print(f"   ✅ Eliminado: {cache_dir}")
            except Exception as e:
                print(f"   ⚠️  Error eliminando {cache_dir}: {e}")
        else:
            print(f"   ℹ️  No existe: {cache_dir}")

def limpiar_modulos_python():
    """Elimina módulos del proyecto del cache de Python"""
    print("📦 Limpiando módulos del proyecto...")
    
    modules_to_remove = []
    for module_name in list(sys.modules.keys()):
        if ('src.' in module_name or 
            module_name.startswith('config.') or 
            module_name.startswith('src') or
            module_name.startswith('config')):
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        if module_name in sys.modules:
            del sys.modules[module_name]
            print(f"   ✅ Módulo removido: {module_name}")
    
    print(f"   📊 Total: {len(modules_to_remove)} módulos removidos del cache")

def reinstalar_streamlit():
    """Reinstala Streamlit para asegurar cache limpio"""
    print("🔧 Reinstalando Streamlit...")
    
    try:
        # Desinstalar Streamlit
        result = subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "streamlit"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Streamlit desinstalado")
        else:
            print("   ⚠️  Advertencia al desinstalar Streamlit")
        
        # Reinstalar Streamlit
        result = subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Streamlit reinstalado")
        else:
            print(f"   ❌ Error reinstalando Streamlit: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Error en reinstalación: {e}")

def main():
    """Función principal"""
    print("=" * 50)
    print("   REINICIAR CACHE - CONSENSOS MLB")
    print("=" * 50)
    print()
    
    # Cambiar al directorio del proyecto
    os.chdir(Path(__file__).parent)
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    print()
    
    # Limpiar caches
    limpiar_cache_python()
    print()
    
    limpiar_cache_streamlit()
    print()
    
    limpiar_modulos_python()
    print()
    
    # Preguntar si reinstalar Streamlit
    respuesta = input("¿Reinstalar Streamlit para cache completamente limpio? (s/N): ").strip().lower()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        reinstalar_streamlit()
        print()
    
    print("✅ Cache reiniciado completamente")
    print()
    print("💡 Recomendaciones:")
    print("   • Cierra cualquier instancia de la interfaz web")
    print("   • Reinicia el terminal/comando")
    print("   • Ejecuta nuevamente la aplicación")
    print()

if __name__ == "__main__":
    main()
