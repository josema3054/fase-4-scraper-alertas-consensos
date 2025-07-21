"""
Script para diagnosticar el comportamiento de la interfaz web
y verificar si está usando datos reales o simulados
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

try:
    from src.scraper.mlb_scraper import MLBScraper
    from config.settings import Settings
    print("✅ Dependencias importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    sys.exit(1)

def test_mlb_scraper_web_behavior():
    """Simula exactamente lo que hace la interfaz web"""
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO: Comportamiento de MLBScraper en interfaz web")
    print("="*60)
    
    try:
        # Configurar settings
        settings = Settings()
        print(f"⚙️ Umbral de consenso: {settings.MLB_CONSENSUS_THRESHOLD}%")
        print(f"👥 Expertos mínimos: {settings.MIN_EXPERTS_VOTING}")
        
        # Crear scraper (igual que en la interfaz web)
        mlb_scraper = MLBScraper()
        print(f"🌐 URL base: {mlb_scraper.base_url}")
        
        # Ejecutar get_live_consensus (igual que en run_live_scraping)
        print("\n🔄 Ejecutando get_live_consensus()...")
        consensus_data = mlb_scraper.get_live_consensus()
        
        if consensus_data:
            print(f"✅ Scraping exitoso: {len(consensus_data)} partidos obtenidos")
            print("\n📊 DATOS OBTENIDOS:")
            for i, game in enumerate(consensus_data, 1):
                print(f"\n{i}. {game.get('equipo_visitante', 'N/A')} vs {game.get('equipo_local', 'N/A')}")
                print(f"   Expertos: {game.get('num_experts', 'N/A')}")
                print(f"   Consenso: {game.get('porcentaje_consenso', 'N/A')}% {game.get('direccion_consenso', 'N/A')}")
                print(f"   Línea: {game.get('total_line', 'N/A')}")
                print(f"   Hora: {game.get('hora_partido', 'N/A')}")
            
            # Verificar si algún partido cumple los criterios
            print(f"\n🎯 FILTRADO CON CRITERIOS ACTUALES:")
            qualified_games = []
            for game in consensus_data:
                experts_count = game.get('num_experts', 0)
                consensus_pct = game.get('porcentaje_consenso', 0)
                
                meets_experts = experts_count >= settings.MIN_EXPERTS_VOTING
                meets_threshold = consensus_pct >= settings.MLB_CONSENSUS_THRESHOLD
                
                if meets_experts and meets_threshold:
                    qualified_games.append(game)
                    print(f"✅ {game.get('equipo_visitante')} vs {game.get('equipo_local')} - {experts_count} expertos, {consensus_pct}%")
                else:
                    reasons = []
                    if not meets_experts:
                        reasons.append(f"expertos {experts_count} < {settings.MIN_EXPERTS_VOTING}")
                    if not meets_threshold:
                        reasons.append(f"consenso {consensus_pct}% < {settings.MLB_CONSENSUS_THRESHOLD}%")
                    print(f"❌ {game.get('equipo_visitante')} vs {game.get('equipo_local')} - {', '.join(reasons)}")
            
            print(f"\n📈 RESUMEN:")
            print(f"Total partidos: {len(consensus_data)}")
            print(f"Partidos que cumplen criterios: {len(qualified_games)}")
            
            return True
            
        else:
            print("❌ No se obtuvieron datos del scraping")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_url_directly():
    """Prueba si podemos acceder directamente a la URL que usa la interfaz web"""
    print("\n" + "="*60)
    print("🌐 DIAGNÓSTICO: Acceso directo a covers.com")
    print("="*60)
    
    try:
        from src.scraper.mlb_scraper import MLBScraper
        import requests
        from datetime import datetime
        
        scraper = MLBScraper()
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"{scraper.base_url}/{today}"
        
        print(f"🔗 URL completa: {url}")
        print("🔄 Realizando petición HTTP...")
        
        response = requests.get(url, headers=scraper.headers, timeout=10)
        print(f"📡 Código de respuesta: {response.status_code}")
        print(f"📏 Tamaño de respuesta: {len(response.text)} caracteres")
        
        if response.status_code == 200:
            if "baseball" in response.text.lower() or "mlb" in response.text.lower():
                print("✅ La página contiene contenido de baseball")
                
                # Buscar indicadores de partidos
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar filas de datos
                rows = soup.find_all('tr')
                game_rows = [row for row in rows if len(row.find_all('td')) >= 5]
                print(f"📊 Filas de partidos encontradas: {len(game_rows)}")
                
                if len(game_rows) > 0:
                    print("✅ Se encontraron datos de partidos en la página")
                else:
                    print("❌ No se encontraron datos de partidos")
                    
            else:
                print("❌ La página no parece contener datos de baseball")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accediendo a la URL: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de interfaz web...")
    print(f"⏰ Fecha y hora: {datetime.now()}")
    
    # Test 1: Comportamiento del scraper
    scraper_works = test_mlb_scraper_web_behavior()
    
    # Test 2: Acceso directo a URL
    test_web_url_directly()
    
    print("\n" + "="*60)
    print("📋 CONCLUSIONES:")
    print("="*60)
    
    if scraper_works:
        print("✅ El scraper puede obtener datos reales")
        print("💡 Si la interfaz web muestra datos simulados, puede ser por:")
        print("   - Errores de conexión específicos en Streamlit")
        print("   - Problemas de timeout en el entorno web")
        print("   - Cache o estado de sesión en Streamlit")
    else:
        print("❌ El scraper no puede obtener datos reales")
        print("💡 La interfaz web está correctamente usando datos simulados como fallback")
    
    print("\n🔧 RECOMENDACIONES:")
    print("1. Ejecutar la interfaz web y verificar los mensajes de estado")
    print("2. Revisar si aparece 'Scraping real ejecutado' o 'datos simulados'")
    print("3. Si usa simulados, verificar conectividad y logs de error")
