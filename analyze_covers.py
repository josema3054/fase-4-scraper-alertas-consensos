"""
Script para analizar la estructura de covers.com y obtener información precisa
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import re

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def analyze_covers_structure():
    """Analiza la estructura HTML de covers.com para entender cómo extraer datos"""
    
    print("🔍 ANALIZANDO ESTRUCTURA DE COVERS.COM")
    print("=" * 60)
    
    url = "https://contests.covers.com/consensus/topoverunderconsensus/mlb/expert"
    
    try:
        # Configurar headers como un navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        print(f"🌐 Conectando a: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Respuesta exitosa: {response.status_code}")
        print(f"📏 Tamaño de la página: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("\n" + "="*60)
        print("ANÁLISIS DE ESTRUCTURA HTML")
        print("="*60)
        
        # 1. Buscar todas las tablas
        tables = soup.find_all('table')
        print(f"\n🏗️  TABLAS ENCONTRADAS: {len(tables)}")
        for i, table in enumerate(tables):
            table_classes = table.get('class', [])
            table_id = table.get('id', 'sin-id')
            print(f"   Tabla {i+1}: id='{table_id}', class={table_classes}")
            
            # Contar filas en cada tabla
            rows = table.find_all('tr')
            print(f"              Filas: {len(rows)}")
            
            # Mostrar las primeras 3 filas de la tabla más grande
            if len(rows) > 5:  # La tabla principal probablemente tiene más de 5 filas
                print(f"              📋 MUESTRA DE FILAS (Tabla {i+1}):")
                for j, row in enumerate(rows[:3]):
                    row_text = row.get_text(separator=' | ', strip=True)
                    print(f"                 Fila {j+1}: {row_text[:100]}...")
        
        # 2. Buscar elementos que contengan códigos de equipos
        print(f"\n🏈 BUSCANDO CÓDIGOS DE EQUIPOS MLB...")
        team_patterns = [
            r'\b(ATH|CLE|NYY|ATL|SD|WAS|CHW|PIT|SF|TOR|BAL|TB)\b',
            r'\b(MLB[A-Z]{3}[A-Z]{3})\b',
            r'\b([A-Z]{2,3})\s+([A-Z]{2,3})\b'
        ]
        
        for pattern in team_patterns:
            matches = re.findall(pattern, str(soup))
            if matches:
                print(f"   Patrón '{pattern}': {len(matches)} coincidencias")
                print(f"   Ejemplos: {matches[:5]}")
        
        # 3. Buscar elementos que contengan porcentajes
        print(f"\n📊 BUSCANDO PORCENTAJES...")
        percentage_patterns = [
            r'(\d+)\s*%\s*(Over|Under)',
            r'(\d+)%',
            r'(\d+)\s*%'
        ]
        
        for pattern in percentage_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches:
                print(f"   Patrón '{pattern}': {len(matches)} coincidencias")
                print(f"   Ejemplos: {matches[:5]}")
        
        # 4. Buscar elementos que contengan horas
        print(f"\n⏰ BUSCANDO HORAS DE PARTIDOS...")
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*[ap]m\s*ET)',
            r'(\d{1,2}:\d{2})',
            r'(pm\s*ET|am\s*ET)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches:
                print(f"   Patrón '{pattern}': {len(matches)} coincidencias")
                print(f"   Ejemplos: {matches[:5]}")
        
        # 5. Buscar divs o secciones específicas
        print(f"\n📦 BUSCANDO CONTENEDORES ESPECÍFICOS...")
        containers = soup.find_all(['div', 'section'], class_=re.compile(r'(consensus|picks|betting|game|match)'))
        print(f"   Contenedores relacionados: {len(containers)}")
        
        for container in containers[:3]:
            classes = container.get('class', [])
            container_id = container.get('id', 'sin-id')
            print(f"   Contenedor: id='{container_id}', class={classes}")
        
        # 6. Guardar una muestra del HTML para análisis manual
        print(f"\n💾 GUARDANDO MUESTRA DEL HTML...")
        with open('covers_sample.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify())[:10000])  # Primeros 10KB
        print("   ✅ Guardado en 'covers_sample.html'")
        
        # 7. Buscar específicamente texto que contenga "Under" y "Over"
        print(f"\n🎯 BUSCANDO TEXTO CON 'OVER' Y 'UNDER'...")
        all_text = soup.get_text()
        over_count = all_text.lower().count('over')
        under_count = all_text.lower().count('under')
        print(f"   'Over' aparece: {over_count} veces")
        print(f"   'Under' aparece: {under_count} veces")
        
        # Buscar líneas específicas que contengan Over/Under
        lines_with_consensus = []
        for line in all_text.split('\n'):
            line = line.strip()
            if 'over' in line.lower() and 'under' in line.lower() and any(char.isdigit() for char in line):
                lines_with_consensus.append(line)
        
        print(f"\n📋 LÍNEAS CON CONSENSO OVER/UNDER:")
        for i, line in enumerate(lines_with_consensus[:5]):
            print(f"   {i+1}. {line}")
        
        print(f"\n" + "="*60)
        print("✅ ANÁLISIS COMPLETADO")
        print("🔍 Revisa 'covers_sample.html' para más detalles")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_covers_structure()
