"""
Modelos de datos para Supabase
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class ConsensusModel:
    """Modelo para datos de consenso"""
    fecha: str
    fecha_scraping: str
    deporte: str
    equipo_local: str
    equipo_visitante: str
    consenso_spread: int = 0
    consenso_total: int = 0
    consenso_moneyline: int = 0
    porcentaje_spread: float = 0.0
    porcentaje_total: float = 0.0
    porcentaje_moneyline: float = 0.0
    hora_partido: str = ""
    url_fuente: str = ""
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para Supabase"""
        data = asdict(self)
        if self.metadata:
            data['metadata'] = json.dumps(self.metadata)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsensusModel':
        """Crea el modelo desde un diccionario"""
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)
    
    def has_high_consensus(self, threshold: float = 75.0) -> bool:
        """Verifica si tiene consenso alto"""
        return any([
            self.porcentaje_spread >= threshold,
            self.porcentaje_total >= threshold,
            self.porcentaje_moneyline >= threshold
        ])
    
    def get_highest_consensus(self) -> tuple[str, float]:
        """Obtiene el consenso más alto y su tipo"""
        consensos = {
            'spread': self.porcentaje_spread,
            'total': self.porcentaje_total,
            'moneyline': self.porcentaje_moneyline
        }
        
        tipo_max = max(consensos, key=consensos.get)
        return tipo_max, consensos[tipo_max]

@dataclass
class AlertModel:
    """Modelo para alertas enviadas"""
    timestamp: str
    tipo_alerta: str
    deporte: str
    mensaje: str
    consensus_ids: List[int]
    telegram_chat_ids: List[str]
    enviado_exitosamente: bool = True
    error_mensaje: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para Supabase"""
        data = asdict(self)
        data['consensus_ids'] = json.dumps(self.consensus_ids)
        data['telegram_chat_ids'] = json.dumps(self.telegram_chat_ids)
        if self.metadata:
            data['metadata'] = json.dumps(self.metadata)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlertModel':
        """Crea el modelo desde un diccionario"""
        if 'consensus_ids' in data and isinstance(data['consensus_ids'], str):
            data['consensus_ids'] = json.loads(data['consensus_ids'])
        if 'telegram_chat_ids' in data and isinstance(data['telegram_chat_ids'], str):
            data['telegram_chat_ids'] = json.loads(data['telegram_chat_ids'])
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)

@dataclass
class LogModel:
    """Modelo para logs del sistema"""
    timestamp: str
    nivel: str
    modulo: str
    mensaje: str
    contexto: Optional[str] = None
    error_traceback: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para Supabase"""
        data = asdict(self)
        if self.metadata:
            data['metadata'] = json.dumps(self.metadata)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogModel':
        """Crea el modelo desde un diccionario"""
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)

@dataclass
class SystemStatusModel:
    """Modelo para estado del sistema"""
    timestamp: str
    servicio: str
    estado: str
    uptime_segundos: int
    cpu_uso: float
    memoria_uso: float
    requests_procesados: int
    errores_contados: int
    ultima_ejecucion: Optional[str] = None
    proxima_ejecucion: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para Supabase"""
        data = asdict(self)
        if self.metadata:
            data['metadata'] = json.dumps(self.metadata)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemStatusModel':
        """Crea el modelo desde un diccionario"""
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)

@dataclass
class ConfigurationModel:
    """Modelo para configuración del sistema"""
    clave: str
    valor: str
    tipo: str  # 'string', 'int', 'float', 'bool', 'json'
    descripcion: str
    categoria: str
    modificado_por: str
    timestamp: str
    es_sensible: bool = False  # Para passwords, tokens, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para Supabase"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigurationModel':
        """Crea el modelo desde un diccionario"""
        return cls(**data)
    
    def get_typed_value(self) -> Any:
        """Obtiene el valor con el tipo correcto"""
        if self.tipo == 'int':
            return int(self.valor)
        elif self.tipo == 'float':
            return float(self.valor)
        elif self.tipo == 'bool':
            return self.valor.lower() in ['true', '1', 'yes', 'on']
        elif self.tipo == 'json':
            return json.loads(self.valor)
        else:
            return self.valor

@dataclass
class BettingResultModel:
    """Modelo para resultados históricos de apuestas"""
    fecha_partido: str
    deporte: str
    equipo_local: str
    equipo_visitante: str
    consensus_id: int  # FK a consensus_data
    tipo_apuesta: str  # 'spread', 'total', 'moneyline'
    consenso_porcentaje: float
    linea_apuesta: str  # Línea específica de la apuesta
    resultado_partido: str  # JSON con scores finales
    resultado_apuesta: str  # 'win', 'loss', 'push'
    roi_calculado: float
    fecha_resultado: str
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para Supabase"""
        data = asdict(self)
        if self.metadata:
            data['metadata'] = json.dumps(self.metadata)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BettingResultModel':
        """Crea el modelo desde un diccionario"""
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)

@dataclass
class HistoricalStatsModel:
    """Modelo para estadísticas históricas agregadas"""
    fecha: str
    deporte: str
    tipo_apuesta: str
    rango_consenso: str  # '70-75', '75-80', '80-85', '85-90', '90+'
    total_apuestas: int
    apuestas_ganadoras: int
    apuestas_perdedoras: int
    apuestas_empate: int
    porcentaje_acierto: float
    roi_promedio: float
    mejor_racha: int
    peor_racha: int
    volumen_alertas: int
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para Supabase"""
        data = asdict(self)
        if self.metadata:
            data['metadata'] = json.dumps(self.metadata)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoricalStatsModel':
        """Crea el modelo desde un diccionario"""
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)

@dataclass
class TeamPerformanceModel:
    """Modelo para rendimiento histórico por equipo"""
    equipo: str
    deporte: str
    temporada: str
    total_partidos: int
    consenso_favor: int  # Partidos donde el consenso favoreció al equipo
    consenso_contra: int  # Partidos donde el consenso fue contra el equipo
    acierto_spread: float  # Porcentaje de acierto en spread
    acierto_total: float  # Porcentaje de acierto en total
    acierto_moneyline: float  # Porcentaje de acierto en moneyline
    roi_promedio: float
    mejor_mes: str
    peor_mes: str
    tendencia_consenso: str  # 'favorable', 'neutral', 'desfavorable'
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para Supabase"""
        data = asdict(self)
        if self.metadata:
            data['metadata'] = json.dumps(self.metadata)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamPerformanceModel':
        """Crea el modelo desde un diccionario"""
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)

# Esquemas de tablas para Supabase
TABLA_SCHEMAS = {
    'fase4_consensus_data': {
        'create_sql': '''
        CREATE TABLE IF NOT EXISTS fase4_consensus_data (
            id BIGSERIAL PRIMARY KEY,
            fecha DATE NOT NULL,
            fecha_scraping TIMESTAMPTZ NOT NULL,
            deporte VARCHAR(50) NOT NULL,
            equipo_local VARCHAR(100) NOT NULL,
            equipo_visitante VARCHAR(100) NOT NULL,
            consenso_spread INTEGER DEFAULT 0,
            consenso_total INTEGER DEFAULT 0,
            consenso_moneyline INTEGER DEFAULT 0,
            porcentaje_spread DECIMAL(5,2) DEFAULT 0.0,
            porcentaje_total DECIMAL(5,2) DEFAULT 0.0,
            porcentaje_moneyline DECIMAL(5,2) DEFAULT 0.0,
            hora_partido VARCHAR(20),
            url_fuente TEXT,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_consensus_fecha ON fase4_consensus_data(fecha);
        CREATE INDEX IF NOT EXISTS idx_consensus_deporte ON fase4_consensus_data(deporte);
        CREATE INDEX IF NOT EXISTS idx_consensus_equipos ON fase4_consensus_data(equipo_local, equipo_visitante);
        ''',
        'model': ConsensusModel
    },
    
    'fase4_alerts_sent': {
        'create_sql': '''
        CREATE TABLE IF NOT EXISTS fase4_alerts_sent (
            id BIGSERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            tipo_alerta VARCHAR(50) NOT NULL,
            deporte VARCHAR(50) NOT NULL,
            mensaje TEXT NOT NULL,
            consensus_ids JSONB,
            telegram_chat_ids JSONB,
            enviado_exitosamente BOOLEAN DEFAULT TRUE,
            error_mensaje TEXT,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON fase4_alerts_sent(timestamp);
        CREATE INDEX IF NOT EXISTS idx_alerts_tipo ON fase4_alerts_sent(tipo_alerta);
        ''',
        'model': AlertModel
    },
    
    'fase4_system_logs': {
        'create_sql': '''
        CREATE TABLE IF NOT EXISTS fase4_system_logs (
            id BIGSERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            nivel VARCHAR(20) NOT NULL,
            modulo VARCHAR(100) NOT NULL,
            mensaje TEXT NOT NULL,
            contexto VARCHAR(200),
            error_traceback TEXT,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON fase4_system_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_logs_nivel ON fase4_system_logs(nivel);
        CREATE INDEX IF NOT EXISTS idx_logs_modulo ON fase4_system_logs(modulo);
        ''',
        'model': LogModel
    },
    
    'fase4_system_status': {
        'create_sql': '''
        CREATE TABLE IF NOT EXISTS fase4_system_status (
            id BIGSERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            servicio VARCHAR(100) NOT NULL,
            estado VARCHAR(50) NOT NULL,
            uptime_segundos INTEGER DEFAULT 0,
            cpu_uso DECIMAL(5,2) DEFAULT 0.0,
            memoria_uso DECIMAL(10,2) DEFAULT 0.0,
            requests_procesados INTEGER DEFAULT 0,
            errores_contados INTEGER DEFAULT 0,
            ultima_ejecucion TIMESTAMPTZ,
            proxima_ejecucion TIMESTAMPTZ,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_status_timestamp ON fase4_system_status(timestamp);
        CREATE INDEX IF NOT EXISTS idx_status_servicio ON fase4_system_status(servicio);
        ''',
        'model': SystemStatusModel
    },
    
    'fase4_configuration': {
        'create_sql': '''
        CREATE TABLE IF NOT EXISTS fase4_configuration (
            id BIGSERIAL PRIMARY KEY,
            clave VARCHAR(100) UNIQUE NOT NULL,
            valor TEXT NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            descripcion TEXT,
            categoria VARCHAR(50),
            modificado_por VARCHAR(100),
            timestamp TIMESTAMPTZ NOT NULL,
            es_sensible BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_config_categoria ON fase4_configuration(categoria);
        CREATE INDEX IF NOT EXISTS idx_config_clave ON fase4_configuration(clave);
        ''',
        'model': ConfigurationModel
    },
    
    'fase4_betting_results': {
        'create_sql': '''
        CREATE TABLE IF NOT EXISTS fase4_betting_results (
            id BIGSERIAL PRIMARY KEY,
            fecha_partido DATE NOT NULL,
            deporte VARCHAR(50) NOT NULL,
            equipo_local VARCHAR(100) NOT NULL,
            equipo_visitante VARCHAR(100) NOT NULL,
            consensus_id BIGINT REFERENCES fase4_consensus_data(id),
            tipo_apuesta VARCHAR(20) NOT NULL,
            consenso_porcentaje DECIMAL(5,2) NOT NULL,
            linea_apuesta VARCHAR(50),
            resultado_partido JSONB,
            resultado_apuesta VARCHAR(10) NOT NULL,
            roi_calculado DECIMAL(8,4),
            fecha_resultado DATE,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_betting_results_fecha ON fase4_betting_results(fecha_partido);
        CREATE INDEX IF NOT EXISTS idx_betting_results_deporte ON fase4_betting_results(deporte);
        CREATE INDEX IF NOT EXISTS idx_betting_results_tipo ON fase4_betting_results(tipo_apuesta);
        CREATE INDEX IF NOT EXISTS idx_betting_results_consenso ON fase4_betting_results(consenso_porcentaje);
        CREATE INDEX IF NOT EXISTS idx_betting_results_resultado ON fase4_betting_results(resultado_apuesta);
        ''',
        'model': BettingResultModel
    },
    
    'fase4_historical_stats': {
        'create_sql': '''
        CREATE TABLE IF NOT EXISTS fase4_historical_stats (
            id BIGSERIAL PRIMARY KEY,
            fecha DATE NOT NULL,
            deporte VARCHAR(50) NOT NULL,
            tipo_apuesta VARCHAR(20) NOT NULL,
            rango_consenso VARCHAR(20) NOT NULL,
            total_apuestas INTEGER DEFAULT 0,
            apuestas_ganadoras INTEGER DEFAULT 0,
            apuestas_perdedoras INTEGER DEFAULT 0,
            apuestas_empate INTEGER DEFAULT 0,
            porcentaje_acierto DECIMAL(5,2) DEFAULT 0.0,
            roi_promedio DECIMAL(8,4) DEFAULT 0.0,
            mejor_racha INTEGER DEFAULT 0,
            peor_racha INTEGER DEFAULT 0,
            volumen_alertas INTEGER DEFAULT 0,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_historical_stats_fecha ON fase4_historical_stats(fecha);
        CREATE INDEX IF NOT EXISTS idx_historical_stats_deporte ON fase4_historical_stats(deporte);
        CREATE INDEX IF NOT EXISTS idx_historical_stats_tipo ON fase4_historical_stats(tipo_apuesta);
        CREATE INDEX IF NOT EXISTS idx_historical_stats_rango ON fase4_historical_stats(rango_consenso);
        CREATE INDEX IF NOT EXISTS idx_historical_stats_acierto ON fase4_historical_stats(porcentaje_acierto);
        ''',
        'model': HistoricalStatsModel
    },
    
    'fase4_team_performance': {
        'create_sql': '''
        CREATE TABLE IF NOT EXISTS fase4_team_performance (
            id BIGSERIAL PRIMARY KEY,
            equipo VARCHAR(100) NOT NULL,
            deporte VARCHAR(50) NOT NULL,
            temporada VARCHAR(20) NOT NULL,
            total_partidos INTEGER DEFAULT 0,
            consenso_favor INTEGER DEFAULT 0,
            consenso_contra INTEGER DEFAULT 0,
            acierto_spread DECIMAL(5,2) DEFAULT 0.0,
            acierto_total DECIMAL(5,2) DEFAULT 0.0,
            acierto_moneyline DECIMAL(5,2) DEFAULT 0.0,
            roi_promedio DECIMAL(8,4) DEFAULT 0.0,
            mejor_mes VARCHAR(20),
            peor_mes VARCHAR(20),
            tendencia_consenso VARCHAR(20),
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_team_performance_equipo ON fase4_team_performance(equipo);
        CREATE INDEX IF NOT EXISTS idx_team_performance_deporte ON fase4_team_performance(deporte);
        CREATE INDEX IF NOT EXISTS idx_team_performance_temporada ON fase4_team_performance(temporada);
        CREATE INDEX IF NOT EXISTS idx_team_performance_roi ON fase4_team_performance(roi_promedio);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_team_performance_unique ON fase4_team_performance(equipo, deporte, temporada);
        ''',
        'model': TeamPerformanceModel
    }
}

def get_table_schema(table_name: str) -> Dict:
    """Obtiene el schema de una tabla"""
    return TABLA_SCHEMAS.get(table_name, {})

def get_all_schemas() -> Dict:
    """Obtiene todos los schemas de tablas"""
    return TABLA_SCHEMAS
