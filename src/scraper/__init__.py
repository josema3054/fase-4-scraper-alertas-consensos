"""
Módulo de scraping para obtener consensos deportivos desde covers.com
Soporte para múltiples deportes: MLB, NBA, NFL, NHL
"""

from .mlb_scraper import MLBScraper
from .scheduler import ConsensusScheduler

# Importaciones futuras (cuando estén implementadas)
# from .nba_scraper import NBAScraper
# from .nfl_scraper import NFLScraper
# from .nhl_scraper import NHLScraper

__all__ = ['MLBScraper', 'ConsensusScheduler']

# Configuración de deportes disponibles
SPORTS_CONFIG = {
    'MLB': {
        'scraper_class': MLBScraper,
        'enabled': True,
        'season_months': [3, 4, 5, 6, 7, 8, 9, 10],
        'consensus_threshold': 75,
        'url_base': 'https://www.covers.com/sports/mlb/consensus',
        'schedule_url': 'https://www.covers.com/sports/mlb/schedule'
    },
    'NBA': {
        'scraper_class': None,  # NBAScraper cuando esté implementado
        'enabled': False,
        'season_months': [10, 11, 12, 1, 2, 3, 4, 5, 6],
        'consensus_threshold': 70,
        'url_base': 'https://www.covers.com/sports/nba/consensus',
        'schedule_url': 'https://www.covers.com/sports/nba/schedule'
    },
    'NFL': {
        'scraper_class': None,  # NFLScraper cuando esté implementado
        'enabled': False,
        'season_months': [9, 10, 11, 12, 1, 2],
        'consensus_threshold': 75,
        'url_base': 'https://www.covers.com/sports/nfl/consensus',
        'schedule_url': 'https://www.covers.com/sports/nfl/schedule'
    },
    'NHL': {
        'scraper_class': None,  # NHLScraper cuando esté implementado
        'enabled': False,
        'season_months': [10, 11, 12, 1, 2, 3, 4, 5, 6],
        'consensus_threshold': 75,
        'url_base': 'https://www.covers.com/sports/nhl/consensus',
        'schedule_url': 'https://www.covers.com/sports/nhl/schedule'
    }
}

def get_active_sports():
    """Obtiene los deportes activos basados en la temporada"""
    from datetime import datetime
    current_month = datetime.now().month
    
    active_sports = []
    for sport, config in SPORTS_CONFIG.items():
        if config['enabled'] and current_month in config['season_months']:
            active_sports.append(sport)
    
    return active_sports
