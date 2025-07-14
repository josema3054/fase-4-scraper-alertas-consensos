"""
Configuración específica por deporte para consensos y alertas
"""

from typing import Dict, Any
from datetime import datetime
import json
from pathlib import Path

class SportsConfiguration:
    """Configuración específica por deporte"""
    
    def __init__(self, config_file: str = "config/sports_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Carga configuración desde archivo"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto para todos los deportes"""
        return {
            'MLB': {
                'enabled': True,
                'consensus_thresholds': {
                    'spread': 80,
                    'total': 75,
                    'moneyline': 70
                },
                'alert_settings': {
                    'min_consensus_for_alert': 80,
                    'max_alerts_per_day': 20,
                    'quiet_hours': {
                        'start': 23,
                        'end': 7
                    }
                },
                'scraping_settings': {
                    'main_scraping_hour': 11,
                    'live_update_interval': 120,  # minutos
                    'pregame_scraping_minutes': 15
                },
                'season_info': {
                    'active_months': [3, 4, 5, 6, 7, 8, 9, 10],
                    'typical_game_hours': [13, 14, 15, 16, 17, 18, 19, 20, 21]
                }
            },
            'NBA': {
                'enabled': False,
                'consensus_thresholds': {
                    'spread': 70,
                    'total': 75,
                    'moneyline': 65
                },
                'alert_settings': {
                    'min_consensus_for_alert': 70,
                    'max_alerts_per_day': 25,
                    'quiet_hours': {
                        'start': 23,
                        'end': 7
                    }
                },
                'scraping_settings': {
                    'main_scraping_hour': 11,
                    'live_update_interval': 120,
                    'pregame_scraping_minutes': 15
                },
                'season_info': {
                    'active_months': [10, 11, 12, 1, 2, 3, 4, 5, 6],
                    'typical_game_hours': [19, 20, 21, 22]
                }
            },
            'NFL': {
                'enabled': False,
                'consensus_thresholds': {
                    'spread': 75,
                    'total': 80,
                    'moneyline': 70
                },
                'alert_settings': {
                    'min_consensus_for_alert': 75,
                    'max_alerts_per_day': 15,
                    'quiet_hours': {
                        'start': 23,
                        'end': 7
                    }
                },
                'scraping_settings': {
                    'main_scraping_hour': 11,
                    'live_update_interval': 180,
                    'pregame_scraping_minutes': 15
                },
                'season_info': {
                    'active_months': [9, 10, 11, 12, 1, 2],
                    'typical_game_hours': [13, 16, 17, 20, 21]
                }
            },
            'NHL': {
                'enabled': False,
                'consensus_thresholds': {
                    'spread': 75,
                    'total': 70,
                    'moneyline': 75
                },
                'alert_settings': {
                    'min_consensus_for_alert': 75,
                    'max_alerts_per_day': 18,
                    'quiet_hours': {
                        'start': 23,
                        'end': 7
                    }
                },
                'scraping_settings': {
                    'main_scraping_hour': 11,
                    'live_update_interval': 120,
                    'pregame_scraping_minutes': 15
                },
                'season_info': {
                    'active_months': [10, 11, 12, 1, 2, 3, 4, 5, 6],
                    'typical_game_hours': [17, 18, 19, 20, 21]
                }
            }
        }
    
    def save_config(self):
        """Guarda configuración actual"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_sport_config(self, sport: str) -> Dict[str, Any]:
        """Obtiene configuración de un deporte específico"""
        return self.config.get(sport, {})
    
    def update_sport_config(self, sport: str, config: Dict[str, Any]):
        """Actualiza configuración de un deporte"""
        if sport not in self.config:
            self.config[sport] = {}
        
        self.config[sport].update(config)
        self.save_config()
    
    def get_consensus_threshold(self, sport: str, consensus_type: str) -> int:
        """Obtiene umbral de consenso para un deporte y tipo específico"""
        sport_config = self.get_sport_config(sport)
        return sport_config.get('consensus_thresholds', {}).get(consensus_type, 75)
    
    def set_consensus_threshold(self, sport: str, consensus_type: str, threshold: int):
        """Establece umbral de consenso"""
        if sport not in self.config:
            self.config[sport] = {'consensus_thresholds': {}}
        elif 'consensus_thresholds' not in self.config[sport]:
            self.config[sport]['consensus_thresholds'] = {}
        
        self.config[sport]['consensus_thresholds'][consensus_type] = threshold
        self.save_config()
    
    def is_sport_enabled(self, sport: str) -> bool:
        """Verifica si un deporte está habilitado"""
        return self.get_sport_config(sport).get('enabled', False)
    
    def get_active_sports(self) -> list:
        """Obtiene deportes activos según temporada"""
        current_month = datetime.now().month
        active_sports = []
        
        for sport, config in self.config.items():
            if (config.get('enabled', False) and 
                current_month in config.get('season_info', {}).get('active_months', [])):
                active_sports.append(sport)
        
        return active_sports
    
    def get_pregame_scraping_minutes(self, sport: str) -> int:
        """Obtiene minutos antes del partido para scraping"""
        sport_config = self.get_sport_config(sport)
        return sport_config.get('scraping_settings', {}).get('pregame_scraping_minutes', 15)


# Instancia global de configuración
sports_config = SportsConfiguration()


def get_sports_config() -> SportsConfiguration:
    """Obtiene la instancia de configuración de deportes"""
    return sports_config
