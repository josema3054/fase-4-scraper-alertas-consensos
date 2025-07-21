"""
Script para probar el filtrado de consensos de totales con datos reales
"""

import sys
import os
import json
from datetime import datetime
import pytz

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scraper.mlb_scraper import MLBScraper
from config.settings import Settings

def filter_totals_consensus(consensus_data, threshold, min_experts):
    """Filtra consensos de totales según criterios configurados"""
    
    print(f"\n🎯 APLICANDO FILTROS:")
    print(f"   - Umbral mínimo: {threshold}%")
    print(f"   - Expertos mínimos: {min_experts}")
    
    filtered_data = []
    excluded_data = []
    
    for i, game in enumerate(consensus_data):
        print(f"\n📊 Analizando partido {i+1}:")
        print(f"   {game.get('equipo_visitante', 'N/A')} @ {game.get('equipo_local', 'N/A')}")
        
        # Obtener el porcentaje de consenso principal (el mayor)
        total_pct = game.get('porcentaje_total', 0)
        experts_count = game.get('num_experts', 0)
        
        print(f"   📈 Consenso Total: {total_pct}%")
        print(f"   👥 Expertos: {experts_count}")
        
        # Verificar criterios
        meets_threshold = total_pct >= threshold
        meets_experts = experts_count >= min_experts
        
        print(f"   ✅ Cumple umbral ({threshold}%): {'SÍ' if meets_threshold else 'NO'}")
        print(f"   ✅ Cumple expertos ({min_experts}): {'SÍ' if meets_experts else 'NO'}")
        
        if meets_threshold and meets_experts:
            print(f"   🎯 RESULTADO: ✅ CUMPLE CRITERIOS")
            game['meets_criteria'] = True
            game['threshold_used'] = threshold
            game['experts_required'] = min_experts
            filtered_data.append(game)
        else:
            print(f"   🎯 RESULTADO: ❌ NO CUMPLE")
            game['meets_criteria'] = False
            reasons = []
            if not meets_threshold:
                reasons.append(f"Consenso {total_pct}% < {threshold}%")
            if not meets_experts:
                reasons.append(f"Expertos {experts_count} < {min_experts}")
            game['exclusion_reasons'] = reasons
            excluded_data.append(game)
    
    return filtered_data, excluded_data

def main():
    print("=== PRUEBA DE FILTRADO DE CONSENSOS DE TOTALES ===")
    
    # Configurar timezone Argentina
    timezone = pytz.timezone('America/Argentina/Buenos_Aires')
    current_time = datetime.now(timezone)
    current_date = current_time.strftime('%Y-%m-%d')
    
    print(f"🕐 Fecha/Hora actual: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cargar configuración
    settings = Settings()
    threshold = settings.MLB_CONSENSUS_THRESHOLD
    min_experts = settings.MIN_EXPERTS_VOTING
    
    print(f"🎯 Configuración cargada:")
    print(f"   - Umbral: {threshold}%")
    print(f"   - Expertos mínimos: {min_experts}")
    
    try:
        # Obtener datos reales del scraper
        print(f"\n🕷️ Obteniendo datos de totales para {current_date}...")
        
        with MLBScraper() as scraper:
            # Usar método directo sin decorador async
            url = f"{scraper.base_url}/{current_date}"
            soup = scraper.get_page_content_sync(url)
            
            consensos = []
            if soup:
                # Buscar filas de partidos
                game_rows = soup.find_all('tr')
                # Filtrar filas que probablemente contengan datos de juegos
                game_rows = [row for row in game_rows if len(row.find_all('td')) >= 3]
                
                for row in game_rows:
                    try:
                        consensus_data = scraper._extract_consensus_from_row(row, current_date)
                        if consensus_data:
                            consensos.append(consensus_data)
                    except Exception as e:
                        continue
            
            print(f"📊 Total de partidos obtenidos: {len(consensos)}")
            
            if consensos:
                # Aplicar filtros
                filtered_data, excluded_data = filter_totals_consensus(consensos, threshold, min_experts)
                
                print(f"\n📈 RESUMEN DE RESULTADOS:")
                print(f"   🔍 Total analizados: {len(consensos)}")
                print(f"   ✅ Cumplen criterios: {len(filtered_data)}")
                print(f"   ❌ No cumplen: {len(excluded_data)}")
                
                if filtered_data:
                    print(f"\n🎯 PARTIDOS QUE CUMPLEN CRITERIOS:")
                    for i, game in enumerate(filtered_data):
                        print(f"   {i+1}. {game['equipo_visitante']} @ {game['equipo_local']}")
                        print(f"      📈 Consenso: {game['porcentaje_total']}%")
                        print(f"      👥 Expertos: {game['num_experts']}")
                        print(f"      🕐 Hora: {game.get('hora_partido', 'N/A')}")
                
                if excluded_data:
                    print(f"\n❌ PARTIDOS EXCLUIDOS:")
                    for i, game in enumerate(excluded_data):
                        print(f"   {i+1}. {game['equipo_visitante']} @ {game['equipo_local']}")
                        print(f"      📈 Consenso: {game['porcentaje_total']}%")
                        print(f"      👥 Expertos: {game['num_experts']}")
                        print(f"      ❌ Razones: {', '.join(game['exclusion_reasons'])}")
                
                # Guardar resultados
                results = {
                    'fecha_analisis': current_time.isoformat(),
                    'fecha_partidos': current_date,
                    'configuracion': {
                        'threshold': threshold,
                        'min_experts': min_experts
                    },
                    'estadisticas': {
                        'total_analizados': len(consensos),
                        'cumplen_criterios': len(filtered_data),
                        'no_cumplen': len(excluded_data),
                        'tasa_aprobacion': len(filtered_data) / len(consensos) * 100 if consensos else 0
                    },
                    'partidos_validos': filtered_data,
                    'partidos_excluidos': excluded_data,
                    'todos_los_partidos': consensos
                }
                
                with open('filter_results.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Resultados guardados en filter_results.json")
                
                # Estadísticas finales
                approval_rate = len(filtered_data) / len(consensos) * 100 if consensos else 0
                print(f"\n📊 ESTADÍSTICAS FINALES:")
                print(f"   📈 Tasa de aprobación: {approval_rate:.1f}%")
                print(f"   🎯 Partidos válidos para alertas: {len(filtered_data)}")
                
            else:
                print("❌ No se obtuvieron datos de consensos")
                
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
