"""
Test simple para verificar conectividad básica
"""

import requests
from bs4 import BeautifulSoup

def test_basic():
    print("🌐 Test de conectividad básica")
    
    try:
        url = "https://contests.covers.com/consensus/topoverunderconsensus/mlb/expert"
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Contar elementos clave
            print(f"Página cargada: {len(text)} caracteres")
            print(f"Menciones 'Over': {text.count('Over')}")
            print(f"Menciones 'Under': {text.count('Under')}")
            print(f"Menciones '%': {text.count('%')}")
            print(f"Menciones 'pm ET': {text.count('pm ET')}")
            
            # Si hay datos, el scraper debería funcionar
            if text.count('Over') > 0 and text.count('%') > 0:
                print("✅ Datos disponibles en la página")
            else:
                print("❌ No se detectan datos de consensos")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_basic()
