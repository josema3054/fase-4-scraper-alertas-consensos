#!/usr/bin/env python3
"""
PRUEBA RÁPIDA CON LA URL CORRECTA DE CONSENSOS
============================================
"""

import requests
from bs4 import BeautifulSoup
import re

def test_consensus_url():
    print("🔍 PROBANDO URL DE CONSENSOS MLB")
    print("="*50)
    
    # URL con fecha actual
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://contests.covers.com/consensus/topoverunderconsensus/all/expert/{today}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🌐 Conectando a: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        print(f"✅ Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar porcentajes
            percentages = re.findall(r'\b\d{1,3}%\b', response.text)
            print(f"📊 Porcentajes encontrados: {len(percentages)}")
            if percentages:
                print(f"   Primeros 10: {percentages[:10]}")
            
            # Buscar palabras clave de consenso
            consensus_keywords = ['over', 'under', 'consensus', 'expert', 'voting']
            found_keywords = []
            for keyword in consensus_keywords:
                if keyword.lower() in response.text.lower():
                    found_keywords.append(keyword)
            
            print(f"🎯 Palabras clave encontradas: {found_keywords}")
            
            # Buscar tablas
            tables = soup.find_all('table')
            print(f"📋 Tablas encontradas: {len(tables)}")
            
            # Buscar elementos con clases relacionadas a consenso
            consensus_elements = soup.find_all(class_=re.compile(r'consensus|betting|odds|over|under', re.I))
            print(f"🔍 Elementos de consenso: {len(consensus_elements)}")
            
            # Guardar muestra del HTML
            with open('consensus_sample.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:10000])
            print("💾 Muestra guardada en 'consensus_sample.html'")
            
        else:
            print(f"❌ Error: Código {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_consensus_url()
    input("\n⏸️ Presiona Enter para continuar...")
