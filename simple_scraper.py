#!/usr/bin/env python3
"""
SCRAPER SIMPLE Y DIRECTO PARA COVERS.COM
========================================
Sin dependencias complejas, solo requests
"""

import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_covers_simple():
    """Scraper simplificado para covers.com"""
    
    print("🚀 SCRAPER SIMPLE DE COVERS.COM")
    print("="*50)
    
    # URL con fecha actual
    date = datetime.now().strftime('%Y-%m-%d')
    url = f"https://contests.covers.com/consensus/topoverunderconsensus/all/expert/{date}"
    
    print(f"📅 Fecha: {date}")
    print(f"🌐 URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        print("⏳ Conectando...")
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        
        print(f"📊 Código de respuesta: {response.status_code}")
        print(f"📄 Tamaño: {len(response.text)} caracteres")
        
        if response.status_code != 200:
            print(f"❌ Error HTTP: {response.status_code}")
            return []
        
        # Analizar contenido básico
        content = response.text
        
        print("\n🔍 ANÁLISIS BÁSICO:")
        
        # Contar palabras clave
        keywords = {
            'over': content.lower().count('over'),
            'under': content.lower().count('under'),
            'consensus': content.lower().count('consensus'),
            '%': content.count('%'),
            'mlb': content.lower().count('mlb'),
            'total': content.lower().count('total')
        }
        
        for word, count in keywords.items():
            print(f"   '{word}': {count} veces")
        
        # Buscar patrones de porcentaje
        percentages = re.findall(r'\b(\d{1,3})%\b', content)
        print(f"   Porcentajes encontrados: {len(percentages)}")
        if percentages:
            print(f"   Primeros 10: {percentages[:10]}")
        
        # Buscar patrones de equipos (códigos de 3 letras)
        teams = re.findall(r'\b[A-Z]{3}\b', content)
        unique_teams = list(set(teams))
        print(f"   Códigos de equipos únicos: {len(unique_teams)}")
        if unique_teams:
            print(f"   Primeros 10: {unique_teams[:10]}")
        
        # Buscar patrones de hora
        times = re.findall(r'\b\d{1,2}:\d{2}\b', content)
        print(f"   Horas encontradas: {len(times)}")
        if times:
            print(f"   Primeras 5: {times[:5]}")
        
        # Análisis HTML con BeautifulSoup
        print("\n🔍 ANÁLISIS HTML:")
        soup = BeautifulSoup(content, 'html.parser')
        
        tables = soup.find_all('table')
        print(f"   Tablas encontradas: {len(tables)}")
        
        if tables:
            for i, table in enumerate(tables[:3]):  # Solo las primeras 3
                rows = table.find_all('tr')
                print(f"   Tabla {i+1}: {len(rows)} filas")
                
                if rows:
                    # Analizar primera fila con datos
                    for row in rows[:5]:  # Primeras 5 filas
                        cells = row.find_all(['td', 'th'])
                        if cells and len(cells) >= 3:
                            row_text = row.get_text(strip=True)
                            if row_text:
                                print(f"      Fila ejemplo: '{row_text[:80]}...'")
                            break
        
        # Buscar divs con clases relevantes
        relevant_divs = soup.find_all('div', class_=re.compile(r'consensus|betting|odds|game|match', re.I))
        print(f"   Divs relevantes: {len(relevant_divs)}")
        
        # Guardar muestra del HTML
        with open('covers_sample.html', 'w', encoding='utf-8') as f:
            f.write(content[:20000])  # Primeros 20KB
        print("   💾 Muestra guardada en 'covers_sample.html'")
        
        # Intentar extraer consensos básicos
        print("\n🎯 EXTRACCIÓN DE CONSENSOS:")
        consensos = extract_basic_consensus(content)
        print(f"   Consensos extraídos: {len(consensos)}")
        
        for i, consenso in enumerate(consensos[:5]):  # Primeros 5
            print(f"   {i+1}. {consenso}")
        
        return consensos
        
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_basic_consensus(content):
    """Extracción básica de consensos desde el HTML"""
    consensos = []
    
    try:
        # Buscar patrones que contengan porcentajes y Over/Under
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Si la línea contiene porcentaje y Over/Under
            if '%' in line and ('over' in line.lower() or 'under' in line.lower()):
                # Buscar porcentajes
                percentages = re.findall(r'(\d{1,3})%', line)
                
                # Buscar dirección
                direction = 'Over' if 'over' in line.lower() else 'Under'
                
                # Buscar códigos de equipos
                teams = re.findall(r'\b[A-Z]{2,4}\b', line)
                
                if percentages:
                    consenso = {
                        'texto': line[:100],
                        'porcentaje': percentages[0],
                        'direccion': direction,
                        'equipos': teams[:2] if len(teams) >= 2 else teams
                    }
                    consensos.append(consenso)
    
    except Exception as e:
        print(f"Error en extracción: {e}")
    
    return consensos

if __name__ == "__main__":
    consensos = scrape_covers_simple()
    
    if consensos:
        print(f"\n✅ Se encontraron {len(consensos)} posibles consensos")
    else:
        print("\n❌ No se encontraron consensos")
        print("💡 Esto puede indicar:")
        print("   - No hay juegos para hoy")
        print("   - La página cambió su estructura")
        print("   - Se necesita Selenium para contenido dinámico")
    
    input("\n⏸️ Presiona Enter para continuar...")
