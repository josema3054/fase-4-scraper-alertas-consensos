#!/usr/bin/env python3
"""
BUSCAR LA URL CORRECTA DE CONSENSOS MLB EN COVERS.COM
===================================================
"""

import requests
from bs4 import BeautifulSoup
import re
import time

def test_multiple_urls():
    print("🔍 BUSCANDO LA URL CORRECTA DE CONSENSOS MLB")
    print("="*60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # URLs candidatas para probar
    urls_to_test = [
        "https://www.covers.com/sports/mlb/consensus",
        "https://www.covers.com/sports/mlb/matchups",
        "https://www.covers.com/sport/baseball/mlb/consensus",
        "https://www.covers.com/sport/baseball/mlb/matchups",
        "https://contests.covers.com/consensus/topoverunderconsensus/mlb/expert",
        "https://www.covers.com/sports/mlb",
        "https://www.covers.com/sports/mlb/odds",
        "https://www.covers.com/sports/mlb/betting-odds",
        "https://www.covers.com/consensus/mlb",
        "https://www.covers.com/mlb/consensus"
    ]
    
    working_urls = []
    
    for url in urls_to_test:
        try:
            print(f"\n🌐 Probando: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                # Buscar indicadores de consenso
                content = response.text.lower()
                indicators = {
                    'consensus': content.count('consensus'),
                    'over': content.count('over'),
                    'under': content.count('under'),
                    'percentage': len(re.findall(r'\d+%', content)),
                    'expert': content.count('expert'),
                    'betting': content.count('betting')
                }
                
                score = sum(indicators.values())
                print(f"   ✅ FUNCIONA - Score de consenso: {score}")
                print(f"   📊 Indicadores: {indicators}")
                
                working_urls.append((url, score, indicators))
                
                # Guardar muestra si tiene buen score
                if score > 10:
                    filename = f"sample_{len(working_urls)}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text[:20000])
                    print(f"   💾 Muestra guardada: {filename}")
            
            elif response.status_code == 404:
                print(f"   ❌ No existe (404)")
            elif response.status_code == 403:
                print(f"   🚫 Acceso denegado (403)")
            else:
                print(f"   ⚠️ Error {response.status_code}")
                
            time.sleep(1)  # Pausa entre requests
            
        except requests.RequestException as e:
            print(f"   ❌ Error de conexión: {str(e)[:100]}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*60)
    print("🎯 RESULTADOS FINALES")
    print("="*60)
    
    if working_urls:
        # Ordenar por score
        working_urls.sort(key=lambda x: x[1], reverse=True)
        
        print(f"✅ URLs que funcionan: {len(working_urls)}")
        
        for i, (url, score, indicators) in enumerate(working_urls, 1):
            print(f"\n{i}. {url}")
            print(f"   Score: {score}")
            print(f"   Mejor para: ", end="")
            best_indicators = sorted(indicators.items(), key=lambda x: x[1], reverse=True)[:3]
            print(", ".join([f"{k}({v})" for k, v in best_indicators]))
        
        best_url = working_urls[0][0]
        print(f"\n🏆 MEJOR URL ENCONTRADA:")
        print(f"   {best_url}")
        print(f"   Score: {working_urls[0][1]}")
        
        return best_url
    else:
        print("❌ No se encontraron URLs funcionando")
        print("💡 Posibles soluciones:")
        print("   1. Verificar si covers.com cambió su estructura")
        print("   2. Probar con diferentes user agents")
        print("   3. Revisar si necesita JavaScript (usar Selenium)")
        
        return None

if __name__ == "__main__":
    best_url = test_multiple_urls()
    
    if best_url:
        print(f"\n🔧 Para actualizar el scraper, usa esta URL:")
        print(f"   {best_url}")
    
    input("\n⏸️ Presiona Enter para continuar...")
