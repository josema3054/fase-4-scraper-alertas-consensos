"""
Script para probar el scraper MLB con datos reales del día actual
"""

import sys
import os
from datetime import datetime, timedelta
import pytz
import json

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scraper.mlb_scraper import MLBScraper
from config.settings import Settings

def main():
    print("=== PRUEBA DEL SCRAPER MLB - FECHA ACTUAL ===")
    
    # Configurar timezone Argentina
    timezone = pytz.timezone('America/Argentina/Buenos_Aires')
    current_time = datetime.now(timezone)
    current_date = current_time.strftime('%Y-%m-%d')
    
    print(f"🕐 Fecha/Hora actual (Argentina): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Fecha para scraping: {current_date}")
    
    # Cargar configuración
    settings = Settings()
    print(f"🎯 Umbral configurado: {settings.MLB_CONSENSUS_THRESHOLD}%")
    print(f"👥 Expertos mínimos: {settings.MIN_EXPERTS_VOTING}")
    
    try:
        with MLBScraper() as scraper:
            print(f"🌐 URL base: {scraper.base_url}")
            print(f"🔗 URL con fecha: {scraper.base_url}/{current_date}")
            
            # Probar conexión con la URL específica de totales
            print("\n🔗 Probando conexión...")
            soup = scraper.get_page_content_sync(f"{scraper.base_url}/{current_date}")
            
            if soup:
                print("✅ Conexión exitosa")
                
                # Verificar título de la página
                title = soup.find('title')
                if title:
                    print(f"📋 Título de página: {title.text.strip()}")
                
                # Buscar elementos relevantes
                tables = soup.find_all('table')
                print(f"📊 Tablas encontradas: {len(tables)}")
                
                consensus_elements = soup.find_all(class_=lambda x: x and 'consensus' in x.lower())
                print(f"🎯 Elementos con 'consensus': {len(consensus_elements)}")
                
                game_rows = soup.find_all('tr')
                print(f"📝 Filas de tabla encontradas: {len(game_rows)}")
                
                # Intentar scraping real de totales
                print(f"\n🕷️ Ejecutando scraping de TOTALES para {current_date}...")
                
                # Llamar directamente al método de scraping 
                consensos = []
                try:
                    # Usar el método de scraping con la fecha específica
                    url = f"{scraper.base_url}/{current_date}"
                    soup_date = scraper.get_page_content_sync(url)
                    
                    if soup_date:
                        # Buscar filas de partidos
                        game_rows = soup_date.find_all('tr', class_=['game-row', 'consensus-row', 'picks-row'])
                        print(f"🎯 Filas de juegos encontradas: {len(game_rows)}")
                        
                        # Si no encuentra con clases específicas, buscar todas las filas
                        if not game_rows:
                            all_rows = soup_date.find_all('tr')
                            # Filtrar filas que probablemente contengan datos de juegos
                            game_rows = [row for row in all_rows if len(row.find_all('td')) >= 3]
                            print(f"🔍 Filas candidatas encontradas: {len(game_rows)}")
                        
                        for i, row in enumerate(game_rows[:10]):  # Limitar a 10 para debugging
                            try:
                                # Extraer datos básicos de la fila
                                cells = row.find_all(['td', 'th'])
                                if len(cells) >= 3:
                                    row_text = ' | '.join([cell.get_text(strip=True) for cell in cells[:6]])
                                    print(f"  Fila {i+1}: {row_text}")
                                    
                                    # Intentar extraer datos de consenso
                                    consensus_data = scraper._extract_consensus_from_row(row, current_date)
                                    if consensus_data:
                                        consensos.append(consensus_data)
                                        print(f"    ✅ Datos extraídos: {consensus_data['equipo_visitante']} @ {consensus_data['equipo_local']}")
                            except Exception as e:
                                print(f"    ❌ Error en fila {i+1}: {e}")
                                continue
                    
                except Exception as e:
                    print(f"❌ Error en scraping manual: {e}")
                
                print(f"📊 Consensos obtenidos: {len(consensos)}")
                
                if consensos:
                    print("\n🏈 Datos encontrados:")
                    for i, consenso in enumerate(consensos):
                        print(f"\n{i+1}. {consenso.get('equipo_visitante', 'N/A')} @ {consenso.get('equipo_local', 'N/A')}")
                        print(f"   Hora: {consenso.get('hora_partido', 'N/A')}")
                        print(f"   Spread: {consenso.get('porcentaje_spread', 0)}%")
                        print(f"   Total: {consenso.get('porcentaje_total', 0)}%")
                        print(f"   ML: {consenso.get('porcentaje_moneyline', 0)}%")
                        print(f"   Fecha: {consenso.get('fecha', 'N/A')}")
                
                # Probar también fechas alternativas (comentado por ahora)
                yesterday = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
                tomorrow = (current_time + timedelta(days=1)).strftime('%Y-%m-%d')
                
                print(f"\n� Resumen de datos encontrados:")
                print(f"   - Fecha consultada: {current_date}")
                print(f"   - Consensos válidos: {len(consensos)}")
                
                consensos_yesterday = []
                consensos_tomorrow = []
                
                # Guardar datos para análisis
                all_data = {
                    'fecha_scraping': current_time.isoformat(),
                    'fecha_consultada': current_date,
                    'configuracion': {
                        'threshold': settings.MLB_CONSENSUS_THRESHOLD,
                        'min_experts': settings.MIN_EXPERTS_VOTING
                    },
                    'resultados': {
                        'hoy': consensos,
                        'ayer': consensos_yesterday,
                        'mañana': consensos_tomorrow
                    }
                }
                
                with open('scraper_real_test.json', 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Datos guardados en scraper_real_test.json")
                
            else:
                print("❌ No se pudo conectar con la página")
                
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
