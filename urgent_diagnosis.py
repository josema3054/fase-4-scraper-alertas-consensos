#!/usr/bin/env python3
"""
Script de diagnóstico urgente para identificar el problema específico.
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def urgent_diagnosis():
    """Diagnóstico urgente del problema de extracción"""
    
    print("=== DIAGNÓSTICO URGENTE DEL SCRAPER ===")
    print(f"Fecha: {datetime.now()}")
    
    # URL exacta que usa el scraper
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://contests.covers.com/consensus/topoverunderconsensus/mlb/expert/{today}"
    
    print(f"URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print("\n1. Descargando contenido...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"   ✅ Descarga exitosa: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("\n2. Buscando tablas...")
        tables = soup.find_all('table')
        print(f"   📊 Tablas encontradas: {len(tables)}")
        
        if not tables:
            print("   ❌ PROBLEMA: No hay tablas en la página")
            
            # Buscar divs que puedan contener datos
            print("\n   🔍 Buscando contenido alternativo...")
            
            # Buscar elementos con texto de equipos MLB
            team_elements = soup.find_all(text=re.compile(r'[A-Z]{3}.*@.*[A-Z]{3}'))
            print(f"   Elementos con equipos: {len(team_elements)}")
            
            if team_elements:
                print("   📋 Ejemplos de equipos encontrados:")
                for i, elem in enumerate(team_elements[:3]):
                    print(f"      {i+1}. '{elem.strip()}'")
            
            # Buscar porcentajes
            percentage_elements = soup.find_all(text=re.compile(r'\d+%'))
            print(f"   Elementos con porcentajes: {len(percentage_elements)}")
            
            if percentage_elements:
                print("   📋 Ejemplos de porcentajes:")
                for i, elem in enumerate(percentage_elements[:5]):
                    print(f"      {i+1}. '{elem.strip()}'")
            
            return False
        
        print("\n3. Analizando tabla principal...")
        table = tables[0]  # Primera tabla
        
        rows = table.find_all('tr')
        print(f"   📋 Filas en tabla: {len(rows)}")
        
        print("\n4. Analizando filas...")
        
        valid_data_rows = 0
        for i, row in enumerate(rows[:10]):  # Primeras 10 filas
            cells = row.find_all('td')
            
            if len(cells) >= 3:  # Criterio del scraper mejorado
                row_text = row.get_text(strip=True)
                
                # Criterios de filtrado del scraper
                has_teams = bool(re.search(r'[A-Z]{2,3}', row_text))
                has_percentage = '%' in row_text
                has_time = bool(re.search(r'\d{1,2}:\d{2}', row_text))
                
                print(f"\n   Fila {i}: {len(cells)} celdas")
                print(f"   Texto: '{row_text[:80]}...'")
                print(f"   Criterios: Equipos={has_teams}, %={has_percentage}, Hora={has_time}")
                
                if has_teams and (has_percentage or has_time):
                    valid_data_rows += 1
                    print(f"   ✅ VÁLIDA: Esta fila debería procesarse")
                    
                    # Mostrar contenido de celdas
                    for j, cell in enumerate(cells[:5]):
                        cell_text = cell.get_text(strip=True)
                        print(f"      Celda {j}: '{cell_text}'")
                else:
                    print(f"   ❌ NO VÁLIDA: No cumple criterios")
        
        print(f"\n📊 RESUMEN:")
        print(f"   Total filas: {len(rows)}")
        print(f"   Filas válidas identificadas: {valid_data_rows}")
        
        if valid_data_rows == 0:
            print("   ❌ PROBLEMA: No hay filas que cumplan los criterios")
            print("   🔧 SOLUCIÓN: Necesitamos relajar más los filtros")
        else:
            print("   ✅ HAY DATOS VÁLIDOS: El problema está en la extracción")
            print("   🔧 SOLUCIÓN: Necesitamos revisar la lógica de extracción")
        
        return valid_data_rows > 0
        
    except Exception as e:
        print(f"❌ Error durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = urgent_diagnosis()
    
    print(f"\n{'='*50}")
    if success:
        print("✅ DIAGNÓSTICO: Hay datos disponibles, problema en extracción")
    else:
        print("❌ DIAGNÓSTICO: No hay datos disponibles o estructura cambió")
    
    input("\nPresiona Enter para continuar...")
