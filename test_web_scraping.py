import sys
sys.path.append('src')
from src.scraper.mlb_scraper import MLBScraper

with MLBScraper() as scraper:
    data = scraper.get_live_consensus()
    print(f'Total consensos: {len(data)}')
    
    for i, d in enumerate(data[:5]):
        visitante = d.get('equipo_visitante', 'N/A')
        local = d.get('equipo_local', 'N/A') 
        porcentaje = d.get('porcentaje_consenso', 0)
        expertos = d.get('num_experts', 0)
        print(f'{i+1}. {visitante} @ {local} - {porcentaje}%, {expertos} expertos')
