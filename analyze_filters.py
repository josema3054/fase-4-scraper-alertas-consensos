"""
Script para aplicar filtros a los datos reales obtenidos del scraper
"""

import json
from datetime import datetime

def apply_filters(consensus_data, threshold=64, min_experts=13):
    """Aplica filtros de threshold y expertos mínimos"""
    
    print(f"=== APLICANDO FILTROS ===")
    print(f"🎯 Umbral: {threshold}%")
    print(f"👥 Expertos mínimos: {min_experts}")
    print(f"📊 Total de partidos: {len(consensus_data)}")
    
    valid_games = []
    excluded_games = []
    
    for game in consensus_data:
        equipo_visitante = game.get('equipo_visitante', 'N/A')
        equipo_local = game.get('equipo_local', 'N/A')
        
        # Obtener porcentajes
        spread_pct = game.get('porcentaje_spread', 0)
        total_pct = game.get('porcentaje_total', 0)
        ml_pct = game.get('porcentaje_moneyline', 0)
        
        # Número de expertos (simular si no existe)
        experts_count = game.get('num_experts', 0)
        if experts_count == 0:
            # Extraer del consenso_total o simular basado en el porcentaje
            experts_count = game.get('consenso_total', 20)  # Simular 20 por defecto
        
        # Verificar criterios
        meets_threshold = (spread_pct >= threshold or 
                          total_pct >= threshold or 
                          ml_pct >= threshold)
        meets_experts = experts_count >= min_experts
        
        print(f"\n🏈 {equipo_visitante} @ {equipo_local}")
        print(f"   Spread: {spread_pct}% | Total: {total_pct}% | ML: {ml_pct}%")
        print(f"   Expertos: {experts_count}")
        
        if meets_threshold and meets_experts:
            print(f"   ✅ CUMPLE CRITERIOS")
            valid_games.append({
                **game,
                'meets_criteria': True,
                'max_consensus': max(spread_pct, total_pct, ml_pct),
                'experts_actual': experts_count
            })
        else:
            reasons = []
            if not meets_threshold:
                max_pct = max(spread_pct, total_pct, ml_pct)
                reasons.append(f"Max consenso {max_pct}% < {threshold}%")
            if not meets_experts:
                reasons.append(f"Expertos {experts_count} < {min_experts}")
            
            print(f"   ❌ NO CUMPLE: {', '.join(reasons)}")
            excluded_games.append({
                **game,
                'meets_criteria': False,
                'reasons': reasons,
                'max_consensus': max(spread_pct, total_pct, ml_pct),
                'experts_actual': experts_count
            })
    
    return valid_games, excluded_games

def main():
    print("=== ANÁLISIS DE FILTROS CON DATOS REALES ===")
    
    # Cargar datos del scraper real
    try:
        with open('scraper_real_test.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        fecha_scraping = data['fecha_scraping']
        configuracion = data['configuracion']
        partidos_hoy = data['resultados']['hoy']
        
        print(f"📅 Fecha de scraping: {fecha_scraping}")
        print(f"🎯 Configuración: {configuracion}")
        
        # Aplicar filtros
        valid_games, excluded_games = apply_filters(
            partidos_hoy, 
            threshold=configuracion['threshold'],
            min_experts=configuracion['min_experts']
        )
        
        print(f"\n=== RESUMEN ===")
        print(f"✅ Partidos que cumplen criterios: {len(valid_games)}")
        print(f"❌ Partidos excluidos: {len(excluded_games)}")
        print(f"📊 Tasa de aprobación: {len(valid_games)/len(partidos_hoy)*100:.1f}%")
        
        if valid_games:
            print(f"\n🎯 PARTIDOS VÁLIDOS PARA ALERTAS:")
            for i, game in enumerate(valid_games, 1):
                print(f"{i}. {game['equipo_visitante']} @ {game['equipo_local']}")
                print(f"   Max consenso: {game['max_consensus']}%")
                print(f"   Expertos: {game['experts_actual']}")
        
        # Guardar resultados
        results = {
            'analysis_date': datetime.now().isoformat(),
            'config_used': configuracion,
            'valid_games': valid_games,
            'excluded_games': excluded_games,
            'summary': {
                'total_games': len(partidos_hoy),
                'valid_games': len(valid_games),
                'excluded_games': len(excluded_games),
                'approval_rate': len(valid_games)/len(partidos_hoy)*100 if partidos_hoy else 0
            }
        }
        
        with open('filtered_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Resultados guardados en filtered_results.json")
        
    except FileNotFoundError:
        print("❌ No se encontró el archivo scraper_real_test.json")
        print("Ejecuta primero test_scraper_real.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
