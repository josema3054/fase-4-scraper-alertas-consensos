"""
Script para diagnosticar el problema de expertos en la interfaz web
"""

import sys
import os
from datetime import datetime
import pytz
import json

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_real_scraping():
    """Verificar el scraping en tiempo real"""
    print("🔍 DIAGNÓSTICO COMPLETO - PROBLEMA DE EXPERTOS")
    print("=" * 60)
    
    try:
        from src.scraper.mlb_scraper import MLBScraper
        from config.settings import Settings
        
        settings = Settings()
        timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        current_date = datetime.now(timezone).strftime('%Y-%m-%d')
        
        print(f"📅 Fecha actual: {current_date}")
        print(f"⚙️ Configuración - Umbral: {settings.MLB_CONSENSUS_THRESHOLD}%, Expertos: {settings.MIN_EXPERTS_VOTING}")
        print()
        
        # PASO 1: Verificar scraping directo
        print("🕷️ PASO 1: SCRAPING DIRECTO EN TIEMPO REAL")
        print("-" * 50)
        
        with MLBScraper() as scraper:
            url = f"{scraper.base_url}/{current_date}"
            print(f"🌐 URL: {url}")
            
            # Obtener página
            soup = scraper.get_page_content_sync(url)
            if not soup:
                print("❌ No se pudo obtener la página")
                return
            
            print("✅ Página obtenida exitosamente")
            
            # Buscar filas con datos
            all_rows = soup.find_all('tr')
            game_rows = [row for row in all_rows if len(row.find_all('td')) >= 5]
            
            print(f"📊 Filas encontradas: {len(game_rows)}")
            
            # Analizar los primeros 3 juegos
            print("\n📋 ANÁLISIS DETALLADO DE EXTRACCIÓN:")
            print("-" * 50)
            
            for i, row in enumerate(game_rows[:5]):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 5:
                    # Verificar si es una fila de MLB
                    team_cell = cells[0].get_text(strip=True)
                    if 'MLB' in team_cell:
                        experts_cell = cells[4]
                        experts_html = str(experts_cell)
                        experts_text = experts_cell.get_text(strip=True)
                        
                        print(f"\n🎯 JUEGO {i+1}:")
                        print(f"   Equipos: {team_cell}")
                        print(f"   HTML expertos: {experts_html[:200]}...")
                        print(f"   Texto expertos: '{experts_text}'")
                        
                        # Aplicar lógica del scraper
                        consensus_data = scraper._extract_consensus_from_row(row, current_date)
                        if consensus_data:
                            num_experts = consensus_data.get('num_experts', 0)
                            porcentaje = consensus_data.get('porcentaje_consenso', 0)
                            direccion = consensus_data.get('direccion_consenso', 'N/A')
                            
                            print(f"   ✅ RESULTADO: {num_experts} expertos")
                            print(f"   📊 Consenso: {direccion} {porcentaje}%")
                            
                            # Verificar si cumple filtros
                            if porcentaje >= settings.MLB_CONSENSUS_THRESHOLD and num_experts >= settings.MIN_EXPERTS_VOTING:
                                print(f"   🎯 CUMPLE FILTROS ✅")
                            else:
                                print(f"   ⚠️ NO cumple filtros")
                        else:
                            print(f"   ❌ No se pudo extraer datos")
        
        # PASO 2: Verificar método completo del scraper
        print(f"\n🔧 PASO 2: MÉTODO COMPLETO DEL SCRAPER")
        print("-" * 50)
        
        with MLBScraper() as scraper:
            consensos = scraper.scrape_mlb_consensus(current_date)
            
            print(f"📊 Consensos obtenidos: {len(consensos)}")
            
            if consensos:
                print("\n📋 RESULTADOS FINALES:")
                for i, consenso in enumerate(consensos, 1):
                    equipos = f"{consenso.get('equipo_visitante', 'N/A')} @ {consenso.get('equipo_local', 'N/A')}"
                    expertos = consenso.get('num_experts', 0)
                    porcentaje = consenso.get('porcentaje_consenso', 0)
                    direccion = consenso.get('direccion_consenso', 'N/A')
                    
                    print(f"   {i}. {equipos}")
                    print(f"      {direccion}: {porcentaje}% ({expertos} expertos)")
            else:
                print("❌ No se encontraron consensos que cumplan los filtros")
        
        # PASO 3: Buscar archivos de cache/datos
        print(f"\n💾 PASO 3: VERIFICAR ARCHIVOS DE DATOS")
        print("-" * 50)
        
        # Buscar archivos JSON con datos
        import glob
        json_files = glob.glob("*.json")
        if json_files:
            print("📄 Archivos JSON encontrados:")
            for file in json_files:
                print(f"   - {file}")
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'resultados' in data or 'consensos' in data:
                            print(f"     ⚠️ Contiene datos de consensos - podría ser cache")
                except:
                    pass
        else:
            print("✅ No se encontraron archivos JSON con posible cache")
        
        # PASO 4: Verificar caché de Streamlit
        print(f"\n🌐 PASO 4: VERIFICAR CACHE DE STREAMLIT")
        print("-" * 50)
        
        import streamlit as st
        print(f"📦 Versión de Streamlit: {st.__version__}")
        
        # Verificar directorios de cache
        from pathlib import Path
        streamlit_cache_dirs = [
            Path.home() / ".streamlit",
            Path(".streamlit"),
        ]
        
        cache_found = False
        for cache_dir in streamlit_cache_dirs:
            if cache_dir.exists():
                cache_files = list(cache_dir.rglob("*"))
                if cache_files:
                    print(f"   ⚠️ Cache encontrado en: {cache_dir}")
                    print(f"      Archivos: {len(cache_files)}")
                    cache_found = True
        
        if not cache_found:
            print("✅ No se encontró cache de Streamlit")
        
        print(f"\n🎯 RESUMEN:")
        print("=" * 60)
        print("Si los números siguen apareciendo mal en la interfaz web:")
        print("1. El scraper extrae correctamente (verificar arriba)")
        print("2. Pero la interfaz web usa datos antiguos")
        print("3. Posibles causas:")
        print("   - Cache del navegador")
        print("   - Cache de Streamlit no limpiado")
        print("   - La interfaz no ejecuta scraping nuevo")
        print("   - Usa datos de archivo JSON anterior")
        
    except Exception as e:
        print(f"❌ Error durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_real_scraping()
