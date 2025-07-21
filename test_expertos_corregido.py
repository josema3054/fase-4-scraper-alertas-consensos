"""
Script para probar la corrección del conteo de expertos
"""

import sys
import os
import json

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scraper.mlb_scraper import MLBScraper
from config.settings import Settings

def main():
    print("=== PRUEBA CORRECCIÓN CONTEO DE EXPERTOS ===")
    
    settings = Settings()
    print(f"🎯 Umbral: {settings.MLB_CONSENSUS_THRESHOLD}%")
    print(f"👥 Expertos mínimos: {settings.MIN_EXPERTS_VOTING}")
    
    try:
        with MLBScraper() as scraper:
            # Usar el método interno que ya está probado
            url = f"{scraper.base_url}/2025-07-18"
            soup = scraper.get_page_content_sync(url)
            
            if not soup:
                print("❌ No se pudo conectar con la página")
                return
            
            consensos = []
            all_rows = soup.find_all('tr')
            game_rows = [row for row in all_rows if len(row.find_all('td')) >= 3]
            
            print(f"🔍 Filas candidatas encontradas: {len(game_rows)}")
            
            for row in game_rows:
                consensus_data = scraper._extract_consensus_from_row(row, '2025-07-18')
                if consensus_data and consensus_data.get('equipo_visitante') and consensus_data.get('equipo_local'):
                    consensos.append(consensus_data)
            
            print(f"\n📊 Total consensos extraídos: {len(consensos)}")
            
            # Mostrar todos los consensos con el conteo corregido
            for i, consenso in enumerate(consensos):
                equipo_visitante = consenso.get('equipo_visitante', 'N/A')
                equipo_local = consenso.get('equipo_local', 'N/A')
                porcentaje = consenso.get('porcentaje_consenso', 0)
                direccion = consenso.get('direccion_consenso', 'N/A')
                num_experts = consenso.get('num_experts', 0)
                
                # Verificar si cumple criterios
                cumple_porcentaje = porcentaje >= settings.MLB_CONSENSUS_THRESHOLD
                cumple_expertos = num_experts >= settings.MIN_EXPERTS_VOTING
                es_valido = cumple_porcentaje and cumple_expertos
                
                status = "✅ VÁLIDO" if es_valido else "❌ NO VÁLIDO"
                
                print(f"\n{i+1}. {equipo_visitante} @ {equipo_local}")
                print(f"   {porcentaje}% {direccion}, {num_experts} expertos")
                print(f"   {status}")
                
                if not cumple_porcentaje:
                    print(f"   🔴 Porcentaje {porcentaje}% < {settings.MLB_CONSENSUS_THRESHOLD}%")
                if not cumple_expertos:
                    print(f"   🔴 Expertos {num_experts} < {settings.MIN_EXPERTS_VOTING}")
            
            # Aplicar filtros
            consensos_validos = []
            for consenso in consensos:
                porcentaje = consenso.get('porcentaje_consenso', 0)
                num_experts = consenso.get('num_experts', 0)
                
                if porcentaje >= settings.MLB_CONSENSUS_THRESHOLD and num_experts >= settings.MIN_EXPERTS_VOTING:
                    consensos_validos.append(consenso)
            
            print(f"\n🏆 RESUMEN:")
            print(f"   Total extraídos: {len(consensos)}")
            print(f"   Válidos (≥{settings.MLB_CONSENSUS_THRESHOLD}% y ≥{settings.MIN_EXPERTS_VOTING} expertos): {len(consensos_validos)}")
            
            if consensos_validos:
                print(f"\n✅ PARTIDOS VÁLIDOS:")
                for consenso in consensos_validos:
                    equipo_visitante = consenso.get('equipo_visitante', 'N/A')
                    equipo_local = consenso.get('equipo_local', 'N/A')
                    porcentaje = consenso.get('porcentaje_consenso', 0)
                    direccion = consenso.get('direccion_consenso', 'N/A')
                    num_experts = consenso.get('num_experts', 0)
                    print(f"   • {equipo_visitante} @ {equipo_local} - {porcentaje}% {direccion}, {num_experts} expertos")
            
            # Guardar resultados
            resultado = {
                'total_extraidos': len(consensos),
                'total_validos': len(consensos_validos),
                'configuracion': {
                    'threshold': settings.MLB_CONSENSUS_THRESHOLD,
                    'min_experts': settings.MIN_EXPERTS_VOTING
                },
                'todos_los_consensos': consensos,
                'consensos_validos': consensos_validos
            }
            
            with open('test_expertos_corregido.json', 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Resultados guardados en test_expertos_corregido.json")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
