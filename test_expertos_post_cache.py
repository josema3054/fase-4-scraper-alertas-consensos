"""
Script específico para probar la extracción de expertos después de limpiar cache
"""

import sys
import os
from datetime import datetime
import pytz

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_expert_extraction():
    """Prueba específica de extracción de número de expertos"""
    print("=" * 60)
    print("   PRUEBA DE EXTRACCIÓN DE EXPERTOS POST-CACHE")
    print("=" * 60)
    print()
    
    try:
        # Importar después de limpiar cache
        from src.scraper.mlb_scraper import MLBScraper
        from config.settings import Settings
        
        settings = Settings()
        print(f"⚙️  Configuración cargada:")
        print(f"   - Umbral: {settings.MLB_CONSENSUS_THRESHOLD}%")
        print(f"   - Expertos mínimos: {settings.MIN_EXPERTS_VOTING}")
        print()
        
        # Configurar fecha
        timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        current_time = datetime.now(timezone)
        current_date = current_time.strftime('%Y-%m-%d')
        
        print(f"📅 Fecha de prueba: {current_date}")
        print()
        
        with MLBScraper() as scraper:
            # URL específica
            url = f"{scraper.base_url}/{current_date}"
            print(f"🌐 URL: {url}")
            
            soup = scraper.get_page_content_sync(url)
            
            if soup:
                print("✅ Conexión exitosa")
                
                # Buscar filas de datos
                all_rows = soup.find_all('tr')
                game_rows = [row for row in all_rows if len(row.find_all('td')) >= 4]
                
                print(f"📊 Filas candidatas encontradas: {len(game_rows)}")
                print()
                
                found_expert_examples = 0
                
                for i, row in enumerate(game_rows[:15]):  # Revisar más filas
                    try:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 5:
                            # Verificar si parece una fila de datos MLB
                            team_cell = cells[0].get_text(strip=True)
                            experts_cell = cells[4]
                            
                            if 'MLB' in team_cell or any(team in team_cell.lower() for team in ['yankee', 'brave', 'pirate', 'sox']):
                                experts_text = experts_cell.get_text(strip=True)
                                
                                if experts_text and any(c.isdigit() for c in experts_text):
                                    found_expert_examples += 1
                                    print(f"🔍 Fila {i+1} - Análisis de expertos:")
                                    print(f"   Equipos: {team_cell}")
                                    print(f"   HTML expertos: {str(experts_cell)[:100]}...")
                                    print(f"   Texto expertos: '{experts_text}'")
                                    
                                    # Aplicar la lógica del scraper
                                    consensus_data = scraper._extract_consensus_from_row(row, current_date)
                                    if consensus_data:
                                        num_experts = consensus_data.get('num_experts', 0)
                                        print(f"   ✅ Expertos extraídos: {num_experts}")
                                        
                                        # Verificar si cumple el filtro
                                        porcentaje = consensus_data.get('porcentaje_consenso', 0)
                                        if porcentaje >= settings.MLB_CONSENSUS_THRESHOLD and num_experts >= settings.MIN_EXPERTS_VOTING:
                                            print(f"   🎯 CUMPLE FILTROS: {porcentaje}% con {num_experts} expertos")
                                        else:
                                            print(f"   ⚠️  No cumple filtros: {porcentaje}% con {num_experts} expertos")
                                    else:
                                        print(f"   ❌ No se pudo extraer datos de consenso")
                                    
                                    print()
                                    
                                    if found_expert_examples >= 3:
                                        break
                    
                    except Exception as e:
                        continue
                
                if found_expert_examples == 0:
                    print("⚠️  No se encontraron ejemplos claros de extracción de expertos")
                    print("   Esto puede indicar que:")
                    print("   1. No hay partidos programados para hoy")
                    print("   2. La estructura de la página ha cambiado")
                    print("   3. Es necesario revisar el HTML manualmente")
                else:
                    print(f"✅ Se analizaron {found_expert_examples} ejemplos de extracción de expertos")
                
            else:
                print("❌ No se pudo conectar con la página")
                
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_expert_extraction()
