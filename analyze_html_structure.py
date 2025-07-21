#!/usr/bin/env python3
"""
Script para analizar la estructura HTML real de covers.com
y determinar cómo extraer los datos de consensos correctamente.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sys
import os

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def analyze_covers_structure():
    """Analiza la estructura HTML de covers.com para MLB"""
    
    # URL actual para hoy
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://www.covers.com/sports/mlb/matchups?selectedDate={today}"
    
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
        
        print(f"Estado de respuesta: {response.status_code}")
        print(f"Tamaño de contenido: {len(response.content)} bytes")
        
        # Buscar todas las tablas posibles
        print("\n=== BUSCANDO TABLAS ===")
        tables = soup.find_all('table')
        print(f"Tablas encontradas: {len(tables)}")
        
        for i, table in enumerate(tables):
            print(f"\nTabla {i+1}:")
            print(f"  Classes: {table.get('class', [])}")
            print(f"  ID: {table.get('id', 'Sin ID')}")
            rows = table.find_all('tr')
            print(f"  Filas: {len(rows)}")
            
            # Analizar primera fila como ejemplo
            if rows:
                first_row = rows[0]
                cells = first_row.find_all(['td', 'th'])
                print(f"  Celdas en primera fila: {len(cells)}")
                
                for j, cell in enumerate(cells[:5]):  # Solo primeras 5 celdas
                    text = cell.get_text(strip=True)[:50]  # Primeros 50 caracteres
                    print(f"    Celda {j+1}: '{text}...'")
        
        # Buscar divs con clases relacionadas a matchups o consensus
        print("\n=== BUSCANDO DIVS RELEVANTES ===")
        
        # Palabras clave para buscar
        keywords = ['matchup', 'consensus', 'game', 'betting', 'pick', 'total', 'over', 'under']
        
        for keyword in keywords:
            elements = soup.find_all(['div', 'section'], class_=re.compile(keyword, re.I))
            if elements:
                print(f"\nElementos con '{keyword}' en class: {len(elements)}")
                for i, elem in enumerate(elements[:3]):  # Solo primeros 3
                    classes = elem.get('class', [])
                    text = elem.get_text(strip=True)[:100]
                    print(f"  {i+1}. Classes: {classes}")
                    print(f"     Texto: '{text}...'")
        
        # Buscar texto que contenga patrones de equipos MLB
        print("\n=== BUSCANDO PATRONES DE EQUIPOS ===")
        
        # Patrones comunes de equipos MLB
        team_patterns = [
            r'[A-Z]{2,3}\s+@\s+[A-Z]{2,3}',  # CHI @ HOU
            r'[A-Z]{2,3}\s+[A-Z]{2,3}',      # CHI HOU
            r'\d+%\s+(Over|Under)',           # 74% Over
            r'(\d+)\s*\+\s*(\d+)',           # 15 + 4 (expertos)
        ]
        
        all_text = soup.get_text()
        
        for pattern in team_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            if matches:
                print(f"\nPatrón '{pattern}' encontrado {len(matches)} veces:")
                for match in matches[:5]:  # Primeros 5 matches
                    print(f"  - {match}")
        
        # Buscar elementos específicos por contenido
        print("\n=== ELEMENTOS CON PORCENTAJES ===")
        
        percentage_elements = soup.find_all(text=re.compile(r'\d+%'))
        print(f"Elementos con porcentajes: {len(percentage_elements)}")
        
        for i, elem in enumerate(percentage_elements[:10]):  # Primeros 10
            parent = elem.parent
            if parent:
                print(f"  {i+1}. Texto: '{elem.strip()}'")
                print(f"     Padre: {parent.name}, classes: {parent.get('class', [])}")
        
        # Guardar HTML para análisis offline
        with open('covers_html_sample.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\nHTML guardado en: covers_html_sample.html")
        
        return True
        
    except Exception as e:
        print(f"Error al analizar estructura: {e}")
        return False

if __name__ == "__main__":
    print("=== ANALIZADOR DE ESTRUCTURA HTML DE COVERS.COM ===")
    analyze_covers_structure()
