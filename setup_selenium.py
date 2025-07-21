#!/usr/bin/env python3
"""
INSTALADOR Y PROBADOR DE SELENIUM
=================================
"""

import subprocess
import sys

def install_selenium():
    """Instala Selenium y dependencias"""
    print("📦 Instalando Selenium y WebDriver Manager...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
        print("✅ Selenium instalado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error instalando Selenium: {e}")
        return False

def test_selenium():
    """Prueba básica de Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("🔧 Configurando Chrome driver...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("🌐 Probando navegación...")
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Selenium funcionando correctamente. Título: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Error probando Selenium: {e}")
        return False

def main():
    print("🚀 CONFIGURACIÓN DE SELENIUM PARA SCRAPING")
    print("="*50)
    
    # Instalar Selenium
    if not install_selenium():
        print("❌ No se pudo instalar Selenium")
        return
    
    # Probar Selenium
    if not test_selenium():
        print("❌ Selenium no funciona correctamente")
        print("💡 Posibles soluciones:")
        print("   1. Instalar Google Chrome")
        print("   2. Verificar conexión a internet")
        print("   3. Ejecutar como administrador")
        return
    
    print("\n🎉 ¡SELENIUM LISTO PARA USAR!")
    print("Ahora puedes usar el scraper híbrido que funciona con:")
    print("• Requests (rápido)")
    print("• Selenium (fallback robusto)")

if __name__ == "__main__":
    main()
    input("\n⏸️ Presiona Enter para continuar...")
