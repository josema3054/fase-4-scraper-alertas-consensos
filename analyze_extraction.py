#!/usr/bin/env python3
"""
Script para analizar específicamente por qué no se extraen consensos.
"""

import sys
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def analyze_extraction_failure():
    """Analiza por qué falla la extracción de consensos"""
    
    print("=== ANÁLISIS DE FALLA EN EXTRACCIÓN ===")
    
    # URL para hoy
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://contests.covers.com/consensus/topoverunderconsensus/mlb/expert/{today}"
    
    print(f"Analizando URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Tamaño de respuesta: {len(response.content)} bytes")
        
        # Buscar tabla principal
        table = soup.find('table')
        if not table:
            print("❌ No se encontró tabla en la página")
            return
        
        print("✅ Tabla encontrada")
        
        # Obtener filas
        rows = table.find_all('tr')
        print(f"Total de filas: {len(rows)}")
        
        # Analizar primeras 5 filas con datos
        valid_rows = []
        for i, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 3:
                valid_rows.append((i, row))
        
        print(f"Filas con al menos 3 celdas: {len(valid_rows)}")
        
        # Mostrar contenido de las primeras filas válidas
        for j, (row_idx, row) in enumerate(valid_rows[:5]):
            print(f"\n--- FILA {row_idx} (válida #{j+1}) ---")
            
            cells = row.find_all('td')
            row_text = row.get_text(strip=True)
            
            print(f"Número de celdas: {len(cells)}")
            print(f"Texto completo: '{row_text}'")
            
            # Mostrar cada celda
            for k, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                print(f"  Celda {k}: '{cell_text}'")
            
            # Verificar criterios de filtrado
            has_teams = bool(re.search(r'[A-Z]{2,3}', row_text))
            has_percentage = '%' in row_text
            has_time = bool(re.search(r'\d{1,2}:\d{2}', row_text))
            
            print(f"Criterios - Equipos: {has_teams}, Porcentaje: {has_percentage}, Hora: {has_time}")
            
            if has_teams and (has_percentage or has_time):
                print("✅ Esta fila DEBERÍA ser procesada")
                
                # Intentar extraer datos
                print("\n  🔍 Análisis de extracción:")
                
                # Buscar equipos
                team_patterns = [
                    r'([A-Z]{2,3})\s+@\s+([A-Z]{2,3})',
                    r'([A-Z]{2,3})\s+([A-Z]{2,3})',
                    r'(\w+)\s+@\s+(\w+)'
                ]
                
                teams_found = False
                for pattern in team_patterns:
                    for cell in cells:
                        cell_text = cell.get_text(strip=True)
                        team_match = re.search(pattern, cell_text)
                        if team_match:
                            print(f"    Equipos encontrados: {team_match.group(1)} @ {team_match.group(2)}")
                            teams_found = True
                            break
                    if teams_found:
                        break
                
                # Buscar porcentajes
                percentages_found = False
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    over_match = re.search(r'(\d+)%\s*Over', cell_text, re.IGNORECASE)
                    under_match = re.search(r'(\d+)%\s*Under', cell_text, re.IGNORECASE)
                    
                    if over_match:
                        print(f"    Over encontrado: {over_match.group(1)}%")
                        percentages_found = True
                    elif under_match:
                        print(f"    Under encontrado: {under_match.group(1)}%")
                        percentages_found = True
                
                # Buscar expertos
                experts_found = False
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    pick_numbers = re.findall(r'\b(\d+)\b', cell_text)
                    valid_numbers = [int(num) for num in pick_numbers if 1 <= int(num) <= 100]
                    
                    if valid_numbers:
                        print(f"    Posibles expertos: {valid_numbers}")
                        experts_found = True
                        break
                
                print(f"    Resultado: Equipos={teams_found}, %={percentages_found}, Expertos={experts_found}")
                
                if not (teams_found and percentages_found and experts_found):
                    print("    ❌ FALLA: No se encontraron todos los datos necesarios")
                else:
                    print("    ✅ DEBERÍA FUNCIONAR: Todos los datos encontrados")
                    
            else:
                print("❌ Esta fila NO pasa el filtro inicial")
        
        if len(valid_rows) == 0:
            print("\n❌ PROBLEMA: No hay filas válidas para procesar")
        
        print(f"\n=== Análisis completado ===")
        
    except Exception as e:
        print(f"❌ Error durante análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_extraction_failure()
