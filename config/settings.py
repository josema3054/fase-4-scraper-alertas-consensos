"""
Configuración central del sistema
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    """Configuración del sistema usando Pydantic"""
    
    # === SUPABASE ===
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    
    # === TELEGRAM ===
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = Field(..., env="TELEGRAM_CHAT_ID")
    
    # === TIMEZONE ===
    TIMEZONE: str = Field(default="America/Argentina/Buenos_Aires", env="TIMEZONE")
    
    # === SCRAPING ===
    SCRAPING_DELAY: int = Field(default=2, env="SCRAPING_DELAY")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    RETRY_DELAY: int = Field(default=60, env="RETRY_DELAY")
    
    # === ALERT THRESHOLDS ===
    MLB_CONSENSUS_THRESHOLD: int = Field(default=80, env="MLB_CONSENSUS_THRESHOLD")
    MIN_EXPERTS_VOTING: int = Field(default=4, env="MIN_EXPERTS_VOTING")
    
    # === LOGGING ===
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_ROTATION_DAYS: int = Field(default=7, env="LOG_ROTATION_DAYS")
    
    # === DEVELOPMENT ===
    DEBUG: bool = Field(default=False, env="DEBUG")
    TEST_MODE: bool = Field(default=False, env="TEST_MODE")
    
    # === WEB INTERFACE ===
    STREAMLIT_PORT: int = Field(default=8501, env="STREAMLIT_PORT")
    STREAMLIT_HOST: str = Field(default="0.0.0.0", env="STREAMLIT_HOST")
    
    # === SCHEDULER ===
    MORNING_SCRAPING_TIME: str = Field(default="11:00", env="MORNING_SCRAPING_TIME")
    PRE_GAME_MINUTES: int = Field(default=15, env="PRE_GAME_MINUTES")
    DAILY_REPORT_TIME: str = Field(default="23:59", env="DAILY_REPORT_TIME")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# URLs base para scraping
COVERS_BASE_URL = "https://www.covers.com"
COVERS_MLB_URL = f"{COVERS_BASE_URL}/sports/mlb/picks"

# Headers para requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Configuración de deportes
SPORTS_CONFIG = {
    "mlb": {
        "enabled": True,
        "consensus_threshold": settings.MLB_CONSENSUS_THRESHOLD,
        "min_experts": settings.MIN_EXPERTS_VOTING,
        "scraping_url": COVERS_MLB_URL,
        "season_active": True,
        "timezone": "US/Eastern"
    },
    "nba": {
        "enabled": False,  # Para implementación futura
        "consensus_threshold": 75,
        "min_experts": 4,
        "scraping_url": f"{COVERS_BASE_URL}/sports/nba/picks",
        "season_active": False,
        "timezone": "US/Eastern"
    },
    "nfl": {
        "enabled": False,  # Para implementación futura
        "consensus_threshold": 70,
        "min_experts": 4,
        "scraping_url": f"{COVERS_BASE_URL}/sports/nfl/picks",
        "season_active": False,
        "timezone": "US/Eastern"
    },
    "nhl": {
        "enabled": False,  # Para implementación futura
        "consensus_threshold": 75,
        "min_experts": 4,
        "scraping_url": f"{COVERS_BASE_URL}/sports/nhl/picks",
        "season_active": False,
        "timezone": "US/Eastern"
    }
}

# Configuración de base de datos
DATABASE_TABLES = {
    "consensus_alerts": "fase4_consensus_alerts",
    "daily_monitoring": "fase4_daily_monitoring", 
    "system_logs": "fase4_system_logs",
    "matches": "fase4_matches",
    "consensus_data": "fase4_consensus_data"
}

def get_sport_config(sport: str) -> Optional[dict]:
    """Obtener configuración específica de un deporte"""
    return SPORTS_CONFIG.get(sport.lower())

def is_sport_enabled(sport: str) -> bool:
    """Verificar si un deporte está habilitado"""
    config = get_sport_config(sport)
    return config and config.get("enabled", False)

def get_consensus_threshold(sport: str) -> int:
    """Obtener umbral de consenso para un deporte"""
    config = get_sport_config(sport)
    return config.get("consensus_threshold", 80) if config else 80
