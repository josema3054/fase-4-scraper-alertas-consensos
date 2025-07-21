"""
Script de prueba para verificar que la opción de reiniciar cache funciona
"""

import os
import sys
from pathlib import Path

def verificar_cache_limpio():
    """Verifica si el cache está efectivamente limpio"""
    print("🧪 Verificando estado del cache...")
    
    base_dir = Path(".")
    
    # Contar archivos de cache
    pycache_dirs = list(base_dir.rglob("__pycache__"))
    pyc_files = list(base_dir.rglob("*.pyc"))
    
    print(f"📁 Directorios __pycache__ encontrados: {len(pycache_dirs)}")
    print(f"🐍 Archivos .pyc encontrados: {len(pyc_files)}")
    
    # Verificar módulos en memoria
    project_modules = [name for name in sys.modules.keys() 
                      if any(pattern in name for pattern in ['src.', 'config.'])]
    
    print(f"📦 Módulos del proyecto en memoria: {len(project_modules)}")
    
    if project_modules:
        print("   Módulos encontrados:")
        for module in project_modules[:5]:
            print(f"      • {module}")
        if len(project_modules) > 5:
            print(f"      ... y {len(project_modules) - 5} más")
    
    # Verificar si el cache está limpio
    cache_limpio = len(pycache_dirs) == 0 and len(pyc_files) == 0
    
    if cache_limpio:
        print("✅ Cache está limpio")
    else:
        print("⚠️  Cache contiene archivos")
    
    return cache_limpio

def generar_cache():
    """Genera algo de cache importando módulos"""
    print("🔄 Generando cache importando módulos...")
    
    try:
        # Importar módulos del proyecto para generar cache
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from config.settings import Settings
        print("   ✅ Importado: config.settings")
        
        from src.scraper.mlb_scraper import MLBScraper
        print("   ✅ Importado: src.scraper.mlb_scraper")
        
        from src.utils.logger import Logger
        print("   ✅ Importado: src.utils.logger")
        
        print("📦 Cache generado exitosamente")
        
    except ImportError as e:
        print(f"⚠️  Error al importar módulos: {e}")

def main():
    print("=" * 60)
    print("   PRUEBA DE FUNCIONALIDAD - REINICIAR CACHE")
    print("=" * 60)
    print()
    
    # Verificar estado inicial
    print("1️⃣ Estado inicial del cache:")
    cache_inicial_limpio = verificar_cache_limpio()
    print()
    
    # Generar cache si está limpio
    if cache_inicial_limpio:
        print("2️⃣ Generando cache para la prueba:")
        generar_cache()
        print()
        
        print("3️⃣ Estado después de generar cache:")
        verificar_cache_limpio()
        print()
    
    print("🎯 Instrucciones para continuar:")
    print("   1. Ejecuta: ejecutar_software.bat")
    print("   2. Selecciona opción 5 (Reiniciar cache)")
    print("   3. Vuelve a ejecutar este script para verificar")
    print()
    print("💡 O ejecuta directamente: python reiniciar_cache.py")
    print()

if __name__ == "__main__":
    main()
