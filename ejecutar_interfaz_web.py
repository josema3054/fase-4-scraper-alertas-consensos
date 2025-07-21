#!/usr/bin/env python3
"""
Script para ejecutar la interfaz web de Streamlit
"""

import os
import sys
import subprocess
import webbrowser
import time
import socket
from pathlib import Path

def is_port_in_use(port):
    """Verifica si un puerto está en uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def wait_for_server(url, timeout=30):
    """Espera a que el servidor esté disponible"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    """Función principal"""
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent.absolute()
    os.chdir(project_dir)
    
    # Configurar variables de entorno
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_dir)
    
    # Puerto para Streamlit
    port = 8502
    url = f"http://localhost:{port}"
    
    print("🚀 Iniciando interfaz web...")
    print(f"📁 Directorio del proyecto: {project_dir}")
    print(f"🌐 URL: {url}")
    
    # Verificar si el puerto ya está en uso
    if is_port_in_use(port):
        print(f"⚠️  El puerto {port} ya está en uso")
        response = input("¿Desea intentar abrir la URL existente? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            webbrowser.open(url)
            return
        else:
            port = 8503  # Usar puerto alternativo
            url = f"http://localhost:{port}"
    
    try:
        # Usar el Python del entorno virtual si existe
        venv_python = project_dir / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            python_exe = str(venv_python)
        else:
            python_exe = sys.executable
        
        # Comando para ejecutar Streamlit
        cmd = [
            python_exe, 
            '-m', 'streamlit', 
            'run', 
            'src/web/app.py',
            '--server.port', str(port),
            '--server.address', 'localhost',
            '--server.headless', 'false',
            '--browser.gatherUsageStats', 'false'
        ]
        
        print(f"🔧 Ejecutando: {' '.join(cmd)}")
        
        # Ejecutar Streamlit en background
        process = subprocess.Popen(
            cmd, 
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # Esperar a que el servidor esté listo
        print("⏳ Esperando a que el servidor esté listo...")
        if wait_for_server(url):
            print("✅ Servidor iniciado correctamente")
            print(f"🌐 Abriendo navegador en: {url}")
            webbrowser.open(url)
        else:
            print("⚠️  El servidor tardó mucho en iniciar")
            print(f"🌐 Intente abrir manualmente: {url}")
        
        print("\n" + "="*50)
        print("📊 INTERFAZ WEB ACTIVA")
        print("="*50)
        print(f"🌐 URL: {url}")
        print("🛑 Para detener: Ctrl+C en la consola de Streamlit")
        print("="*50)
        
        # Mantener el script activo
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servidor...")
            process.terminate()
            
    except FileNotFoundError:
        print("❌ Error: Streamlit no está instalado")
        print("💡 Instale con: pip install streamlit")
        
    except Exception as e:
        print(f"❌ Error al iniciar la interfaz: {e}")
        print("💡 Intente ejecutar manualmente:")
        print(f"   streamlit run src/web/app.py --server.port {port}")

if __name__ == "__main__":
    main()
