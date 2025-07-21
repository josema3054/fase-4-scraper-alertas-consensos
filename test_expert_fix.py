"""
Test específico para la corrección del parsing de expertos
"""

import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scraper.mlb_scraper import MLBScraper

def test_expert_parsing_fix():
    print("=== TEST CORRECCIÓN PARSING DE EXPERTOS ===")
    
    try:
        with MLBScraper() as scraper:
            url = f"{scraper.base_url}/2025-07-18"
            soup = scraper.get_page_content_sync(url)
            
            if not soup:
                print("❌ No se pudo conectar")
                return
            
            all_rows = soup.find_all('tr')
            game_rows = [row for row in all_rows if len(row.find_all('td')) >= 5]
            
            print(f"🔍 Filas encontradas: {len(game_rows)}")
            
            # Casos esperados según tu imagen
            expected_cases = {
                'Yankees': 5,   # 4+1
                'Athletics': 17, # 13+4
                'White Sox': 17, # 13+4
            }
            
            for i, row in enumerate(game_rows[:6]):
                try:
                    consensus_data = scraper._extract_consensus_from_row(row, '2025-07-18')
                    
                    if consensus_data and consensus_data.get('equipo_visitante'):
                        visitante = consensus_data.get('equipo_visitante', '')
                        local = consensus_data.get('equipo_local', '')
                        experts = consensus_data.get('num_experts', 0)
                        porcentaje = consensus_data.get('porcentaje_consenso', 0)
                        
                        print(f"\n{i+1}. {visitante} @ {local}")
                        print(f"   📊 Consenso: {porcentaje}%")
                        print(f"   👥 Expertos: {experts}")
                        
                        # Verificar casos específicos
                        for team_name, expected_experts in expected_cases.items():
                            if team_name in visitante:
                                if experts == expected_experts:
                                    print(f"   ✅ CORRECTO: {team_name} tiene {experts} expertos (esperado: {expected_experts})")
                                else:
                                    print(f"   ❌ ERROR: {team_name} tiene {experts} expertos (esperado: {expected_experts})")
                                break
                        
                        # Verificar si cumple criterios (≥64% y ≥13 expertos)
                        cumple_porcentaje = porcentaje >= 64
                        cumple_expertos = experts >= 13
                        
                        if cumple_porcentaje and cumple_expertos:
                            print(f"   🎯 VÁLIDO para mostrar")
                        else:
                            reasons = []
                            if not cumple_porcentaje:
                                reasons.append(f"porcentaje {porcentaje}% < 64%")
                            if not cumple_expertos:
                                reasons.append(f"expertos {experts} < 13")
                            print(f"   ❌ NO VÁLIDO: {', '.join(reasons)}")
                
                except Exception as e:
                    print(f"   ❌ Error procesando fila {i+1}: {e}")
            
            print(f"\n🎯 CASOS ESPERADOS SEGÚN TU IMAGEN:")
            for team, expected in expected_cases.items():
                print(f"   • {team}: {expected} expertos")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_expert_parsing_fix()
