#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO DEL SCRAPER MLB
====================================
Este script revela exactamente dónde está el problema del scraper
"""

import sys
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def print_separator(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    print_separator("🔍 DIAGNÓSTICO COMPLETO DEL SCRAPER MLB")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. VERIFICAR CONEXIÓN A COVERS.COM
    print_separator("1️⃣ VERIFICANDO CONEXIÓN A COVERS.COM")
    
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
        print(f"📄 Tamaño de respuesta: {len(response.text)} caracteres")
        
        if response.status_code != 200:
            print(f"❌ ERROR: Código de respuesta {response.status_code}")
            return
        
        # 2. ANALIZAR ESTRUCTURA HTML
        print_separator("2️⃣ ANALIZANDO ESTRUCTURA HTML")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar tablas
        tables = soup.find_all('table')
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        if not tables:
            print("❌ NO SE ENCONTRARON TABLAS")
            # Buscar divs que podrían contener datos
            divs_with_data = soup.find_all('div', class_=re.compile(r'match|game|consensus|betting', re.I))
            print(f"📦 Divs con posibles datos: {len(divs_with_data)}")
            
            if divs_with_data:
                print("🔍 Primeros 3 divs con datos:")
                for i, div in enumerate(divs_with_data[:3]):
                    print(f"   Div {i+1}: clase='{div.get('class')}', texto='{str(div)[:100]}...'")
            return
        
        # 3. ANALIZAR CADA TABLA
        print_separator("3️⃣ ANALIZANDO CONTENIDO DE TABLAS")
        
        for i, table in enumerate(tables):
            print(f"\n📋 TABLA {i+1}:")
            print(f"   Clases: {table.get('class')}")
            
            # Buscar filas
            rows = table.find_all('tr')
            print(f"   Filas encontradas: {len(rows)}")
            
            if rows:
                print(f"   📝 Primeras 3 filas:")
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    print(f"      Fila {j+1}: {len(cells)} celdas")
                    
                    # Mostrar contenido de las primeras celdas
                    for k, cell in enumerate(cells[:5]):
                        text = cell.get_text(strip=True)
                        if text:
                            print(f"         Celda {k+1}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # 4. BUSCAR PATRONES ESPECÍFICOS
        print_separator("4️⃣ BUSCANDO PATRONES DE DATOS MLB")
        
        # Buscar texto que contenga equipos de MLB
        mlb_teams = ['Yankees', 'Red Sox', 'Dodgers', 'Giants', 'Mets', 'Cubs', 'Cardinals', 'Braves']
        found_teams = []
        
        for team in mlb_teams:
            if team.lower() in response.text.lower():
                found_teams.append(team)
        
        print(f"🏟️ Equipos MLB encontrados: {found_teams}")
        
        # Buscar patrones de porcentajes
        percentage_pattern = r'\b\d{1,3}%\b'
        percentages = re.findall(percentage_pattern, response.text)
        print(f"📊 Porcentajes encontrados: {len(percentages)} (primeros 10: {percentages[:10]})")
        
        # Buscar patrones de números (posibles números de expertos)
        expert_pattern = r'\b(?:expert|voting|consensus).*?(\d+)\b'
        expert_matches = re.findall(expert_pattern, response.text, re.I)
        print(f"👥 Patrones de expertos: {expert_matches[:5]}")
        
        # 5. BUSCAR SELECTORES ESPECÍFICOS
        print_separator("5️⃣ PROBANDO SELECTORES ESPECÍFICOS")
        
        selectors_to_test = [
            'tr[data-game-id]',
            '.CoversMatchupsTable tr',
            '.MatchupTable tr',
            'tr:has(.consensus)',
            'tr:contains("Over")',
            'tr:contains("Under")',
            '.betting-data tr',
            '.consensus-data tr'
        ]
        
        for selector in selectors_to_test:
            try:
                elements = soup.select(selector)
                print(f"   Selector '{selector}': {len(elements)} elementos")
            except Exception as e:
                print(f"   Selector '{selector}': Error - {str(e)}")
        
        # 6. ANÁLISIS FINAL
        print_separator("6️⃣ RESUMEN Y RECOMENDACIONES")
        
        if found_teams:
            print("✅ La página contiene datos de MLB")
        else:
            print("❌ No se detectaron equipos de MLB en la página")
        
        if percentages:
            print("✅ Se encontraron porcentajes (posibles consensos)")
        else:
            print("❌ No se encontraron porcentajes")
        
        if tables:
            print("✅ Se encontraron tablas para analizar")
            print("\n💡 PRÓXIMOS PASOS:")
            print("   1. Revisar el selector de tabla principal")
            print("   2. Ajustar los selectores de filas y celdas")
            print("   3. Verificar los patrones de extracción de datos")
        else:
            print("❌ No se encontraron tablas")
            print("\n💡 PRÓXIMOS PASOS:")
            print("   1. La página podría usar JavaScript para cargar datos")
            print("   2. Considerar usar Selenium en lugar de requests")
            print("   3. Revisar si la URL es correcta")
        
        # 7. GUARDAR MUESTRA DEL HTML
        print_separator("7️⃣ GUARDANDO MUESTRA DE HTML")
        
        with open('sample_html.txt', 'w', encoding='utf-8') as f:
            f.write(response.text[:5000])  # Primeros 5000 caracteres
        
        print("💾 Muestra del HTML guardada en 'sample_html.txt'")
        print("   Puedes revisar este archivo para entender la estructura")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        print(f"🔧 Tipo de error: {type(e).__name__}")
        import traceback
        print("📋 Traceback completo:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print("\n" + "="*60)
    print("🎯 DIAGNÓSTICO COMPLETADO")
    print("="*60)
    input("\n⏸️ Presiona Enter para continuar...")
