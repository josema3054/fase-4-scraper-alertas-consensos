#!/usr/bin/env python3
"""
Script para probar la funcionalidad de reinicio de cache
"""

import os
import sys
import shutil
from pathlib import Path

def find_pycache_dirs():
    """Encuentra todos los directorios __pycache__"""
    current_dir = Path.cwd()
    pycache_dirs = list(current_dir.rglob('__pycache__'))
    return pycache_dirs

def find_pyc_files():
    """Encuentra todos los archivos .pyc"""
    current_dir = Path.cwd()
    pyc_files = list(current_dir.rglob('*.pyc'))
    return pyc_files

def remove_cache():
    """Elimina cache de Python"""
    print("🔍 Buscando archivos de cache...")
    
    # Buscar directorios __pycache__
    pycache_dirs = find_pycache_dirs()
    print(f"📁 Encontrados {len(pycache_dirs)} directorios __pycache__:")
    for dir_path in pycache_dirs:
        print(f"   {dir_path}")
    
    # Buscar archivos .pyc
    pyc_files = find_pyc_files()
    print(f"📄 Encontrados {len(pyc_files)} archivos .pyc:")
    for file_path in pyc_files:
        print(f"   {file_path}")
    
    print("\n🗑️  Eliminando cache...")
    
    # Eliminar directorios __pycache__
    removed_dirs = 0
    for dir_path in pycache_dirs:
        try:
            shutil.rmtree(dir_path)
            removed_dirs += 1
            print(f"   ✅ Eliminado: {dir_path}")
        except Exception as e:
            print(f"   ❌ Error eliminando {dir_path}: {e}")
    
    # Eliminar archivos .pyc
    removed_files = 0
    for file_path in pyc_files:
        try:
            file_path.unlink()
            removed_files += 1
            print(f"   ✅ Eliminado: {file_path}")
        except Exception as e:
            print(f"   ❌ Error eliminando {file_path}: {e}")
    
    print(f"\n✅ Resumen:")
    print(f"   📁 Directorios eliminados: {removed_dirs}/{len(pycache_dirs)}")
    print(f"   📄 Archivos eliminados: {removed_files}/{len(pyc_files)}")

def clear_module_cache():
    """Limpia el cache de módulos de Python"""
    print("\n🔃 Limpiando cache de módulos...")
    
    modules_to_remove = []
    for module_name in list(sys.modules.keys()):
        if 'src.' in module_name or module_name.startswith('config.'):
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        if module_name in sys.modules:
            del sys.modules[module_name]
    
    print(f"✅ {len(modules_to_remove)} módulos removidos del cache")
    if modules_to_remove:
        print("   Módulos removidos:")
        for module in modules_to_remove:
            print(f"   - {module}")

def main():
    print("🔄 PRUEBA DE REINICIO DE CACHE")
    print("=" * 50)
    
    print(f"📍 Directorio actual: {os.getcwd()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Verificar estado inicial
    print("\n📊 ESTADO INICIAL:")
    pycache_dirs = find_pycache_dirs()
    pyc_files = find_pyc_files()
    print(f"   📁 Directorios __pycache__: {len(pycache_dirs)}")
    print(f"   📄 Archivos .pyc: {len(pyc_files)}")
    
    # Limpiar cache
    remove_cache()
    clear_module_cache()
    
    # Verificar estado final
    print("\n📊 ESTADO FINAL:")
    pycache_dirs_after = find_pycache_dirs()
    pyc_files_after = find_pyc_files()
    print(f"   📁 Directorios __pycache__: {len(pycache_dirs_after)}")
    print(f"   📄 Archivos .pyc: {len(pyc_files_after)}")
    
    print("\n✅ Reinicio de cache completado!")

if __name__ == "__main__":
    main()
