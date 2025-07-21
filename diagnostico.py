"""
Script de diagnóstico para verificar por qué no inicia Streamlit
"""

import sys
import os
from pathlib import Path

def test_basic():
    """Pruebas básicas del sistema"""
    print("🔍 DIAGNÓSTICO DEL SISTEMA")
    print("=" * 40)
    
    # 1. Verificar directorio
    current_dir = Path.cwd()
    print(f"📁 Directorio actual: {current_dir}")
    
    # 2. Verificar archivo de app
    app_file = Path("src/web/app.py")
    if app_file.exists():
        print(f"✅ Archivo encontrado: {app_file}")
        print(f"   Tamaño: {app_file.stat().st_size} bytes")
    else:
        print(f"❌ Archivo NO encontrado: {app_file}")
        return False
    
    # 3. Verificar imports básicos
    try:
        import streamlit
        print(f"✅ Streamlit disponible: {streamlit.__version__}")
    except ImportError as e:
        print(f"❌ Error importando Streamlit: {e}")
        return False
    
    # 4. Verificar si se puede cargar la app
    try:
        sys.path.append(str(Path("src").absolute()))
        
        # Intentar imports de la app sin ejecutar
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", app_file)
        if spec and spec.loader:
            print("✅ El archivo de la app se puede cargar")
        else:
            print("❌ No se puede cargar el archivo de la app")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando la app: {e}")
        return False
    
    # 5. Verificar puerto
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8501))
    sock.close()
    
    if result == 0:
        print("⚠️ Puerto 8501 ya está en uso")
    else:
        print("✅ Puerto 8501 disponible")
    
    print("\n🎯 COMANDO SUGERIDO:")
    print("streamlit run src/web/app.py --server.port 8501")
    
    return True

if __name__ == "__main__":
    test_basic()
