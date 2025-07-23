"""
Sistema de Gestión de Datos - Persistencia Local y Base de Datos
Maneja el almacenamiento y recuperación de datos de scraping
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3
from dataclasses import dataclass, asdict

@dataclass
class ScrapingSession:
    """Representa una sesión de scraping"""
    id: str
    fecha: str  # YYYY-MM-DD
    hora_ejecucion: str  # HH:MM:SS
    total_partidos: int
    datos_raw: List[Dict[str, Any]]
    filtros_aplicados: Dict[str, Any]
    estado: str  # "completado", "error", "en_proceso"
    duracion_segundos: float
    errores: List[str]

@dataclass  
class ScraperProgramado:
    """Representa un scraper programado"""
    id: str
    partido_id: str
    visitante: str
    local: str
    fecha_partido: str
    hora_partido: str
    hora_scraping: str
    consenso_actual: str
    estado: str  # "programado", "ejecutado", "error", "cancelado"
    creado_en: str
    ejecutado_en: Optional[str] = None
    resultado: Optional[Dict[str, Any]] = None

class DataManager:
    """Gestor principal de datos del sistema"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.db_path = self.data_dir / "scraping_data.db"
        
        # Crear directorio si no existe
        self.data_dir.mkdir(exist_ok=True)
        
        # Inicializar base de datos
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos SQLite local"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scraping_sessions (
                    id TEXT PRIMARY KEY,
                    fecha TEXT NOT NULL,
                    hora_ejecucion TEXT NOT NULL,
                    total_partidos INTEGER,
                    datos_raw TEXT,
                    filtros_aplicados TEXT,
                    estado TEXT,
                    duracion_segundos REAL,
                    errores TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scrapers_programados (
                    id TEXT PRIMARY KEY,
                    partido_id TEXT NOT NULL,
                    visitante TEXT,
                    local TEXT,
                    fecha_partido TEXT,
                    hora_partido TEXT,
                    hora_scraping TEXT,
                    consenso_actual TEXT,
                    estado TEXT,
                    creado_en TEXT,
                    ejecutado_en TEXT,
                    resultado TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alertas_enviadas (
                    id TEXT PRIMARY KEY,
                    partido_id TEXT,
                    tipo_alerta TEXT,
                    mensaje TEXT,
                    canal TEXT,
                    enviado_en TEXT,
                    exitoso INTEGER
                )
            ''')
            
            conn.commit()
    
    # === GESTIÓN DE SESIONES DE SCRAPING ===
    
    def guardar_sesion_scraping(self, datos: List[Dict], filtros: Dict = None, 
                               duracion: float = 0, errores: List[str] = None) -> str:
        """Guarda una sesión de scraping completa"""
        now = datetime.now()
        session_id = f"scraping_{now.strftime('%Y%m%d_%H%M%S')}"
        
        sesion = ScrapingSession(
            id=session_id,
            fecha=now.strftime('%Y-%m-%d'),
            hora_ejecucion=now.strftime('%H:%M:%S'),
            total_partidos=len(datos),
            datos_raw=datos,
            filtros_aplicados=filtros or {},
            estado="completado" if not errores else "error",
            duracion_segundos=duracion,
            errores=errores or []
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO scraping_sessions 
                (id, fecha, hora_ejecucion, total_partidos, datos_raw, 
                 filtros_aplicados, estado, duracion_segundos, errores)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sesion.id, sesion.fecha, sesion.hora_ejecucion, sesion.total_partidos,
                json.dumps(sesion.datos_raw), json.dumps(sesion.filtros_aplicados),
                sesion.estado, sesion.duracion_segundos, json.dumps(sesion.errores)
            ))
            conn.commit()
        
        return session_id
    
    def obtener_sesion_del_dia(self, fecha: str = None) -> Optional[ScrapingSession]:
        """Obtiene la sesión de scraping más reciente del día especificado"""
        if not fecha:
            fecha = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM scraping_sessions 
                WHERE fecha = ? AND estado = 'completado'
                ORDER BY hora_ejecucion DESC 
                LIMIT 1
            ''', (fecha,))
            
            row = cursor.fetchone()
            
            if row:
                return ScrapingSession(
                    id=row[0], fecha=row[1], hora_ejecucion=row[2],
                    total_partidos=row[3], datos_raw=json.loads(row[4]),
                    filtros_aplicados=json.loads(row[5]), estado=row[6],
                    duracion_segundos=row[7], errores=json.loads(row[8])
                )
            
            return None
    
    def obtener_todas_las_sesiones(self, limite: int = 10) -> List[ScrapingSession]:
        """Obtiene las últimas sesiones de scraping"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM scraping_sessions 
                ORDER BY fecha DESC, hora_ejecucion DESC 
                LIMIT ?
            ''', (limite,))
            
            sesiones = []
            for row in cursor.fetchall():
                sesiones.append(ScrapingSession(
                    id=row[0], fecha=row[1], hora_ejecucion=row[2],
                    total_partidos=row[3], datos_raw=json.loads(row[4]),
                    filtros_aplicados=json.loads(row[5]), estado=row[6],
                    duracion_segundos=row[7], errores=json.loads(row[8])
                ))
            
            return sesiones
    
    # === GESTIÓN DE SCRAPERS PROGRAMADOS ===
    
    def programar_scraper(self, partido_data: Dict) -> str:
        """Programa un nuevo scraper automático"""
        now = datetime.now()
        scraper_id = f"scraper_{partido_data.get('visitante', 'unk')}_{partido_data.get('local', 'unk')}_{now.strftime('%Y%m%d')}"
        
        scraper = ScraperProgramado(
            id=scraper_id,
            partido_id=f"{partido_data.get('visitante')}@{partido_data.get('local')}",
            visitante=partido_data.get('visitante', ''),
            local=partido_data.get('local', ''),
            fecha_partido=partido_data.get('fecha', ''),
            hora_partido=partido_data.get('hora', ''),
            hora_scraping=f"15 min antes de {partido_data.get('hora', '')}",
            consenso_actual=f"{partido_data.get('over_percentage', '0')}% OVER",
            estado="programado",
            creado_en=now.isoformat()
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO scrapers_programados 
                (id, partido_id, visitante, local, fecha_partido, hora_partido,
                 hora_scraping, consenso_actual, estado, creado_en)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scraper.id, scraper.partido_id, scraper.visitante, scraper.local,
                scraper.fecha_partido, scraper.hora_partido, scraper.hora_scraping,
                scraper.consenso_actual, scraper.estado, scraper.creado_en
            ))
            conn.commit()
        
        return scraper_id
    
    def obtener_scrapers_programados(self, solo_activos: bool = True) -> List[ScraperProgramado]:
        """Obtiene todos los scrapers programados"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM scrapers_programados
            '''
            params = ()
            
            if solo_activos:
                query += " WHERE estado = 'programado'"
            
            query += " ORDER BY fecha_partido, hora_partido"
            
            cursor = conn.execute(query, params)
            scrapers = []
            
            for row in cursor.fetchall():
                scrapers.append(ScraperProgramado(
                    id=row[0], partido_id=row[1], visitante=row[2], local=row[3],
                    fecha_partido=row[4], hora_partido=row[5], hora_scraping=row[6],
                    consenso_actual=row[7], estado=row[8], creado_en=row[9],
                    ejecutado_en=row[10], resultado=json.loads(row[11]) if row[11] else None
                ))
            
            return scrapers
    
    def actualizar_estado_scraper(self, scraper_id: str, estado: str, 
                                 resultado: Dict = None):
        """Actualiza el estado de un scraper programado"""
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE scrapers_programados 
                SET estado = ?, ejecutado_en = ?, resultado = ?
                WHERE id = ?
            ''', (
                estado, 
                now.isoformat() if estado == "ejecutado" else None,
                json.dumps(resultado) if resultado else None,
                scraper_id
            ))
            conn.commit()
    
    # === ESTADÍSTICAS Y REPORTES ===
    
    def obtener_estadisticas_hoy(self) -> Dict[str, Any]:
        """Obtiene estadísticas del día actual"""
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            # Sesiones del día
            cursor = conn.execute('''
                SELECT COUNT(*), AVG(total_partidos), AVG(duracion_segundos)
                FROM scraping_sessions 
                WHERE fecha = ? AND estado = 'completado'
            ''', (hoy,))
            
            stats_sesiones = cursor.fetchone()
            
            # Scrapers programados
            cursor = conn.execute('''
                SELECT COUNT(*), 
                       SUM(CASE WHEN estado = 'programado' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN estado = 'ejecutado' THEN 1 ELSE 0 END)
                FROM scrapers_programados 
                WHERE fecha_partido = ?
            ''', (hoy,))
            
            stats_scrapers = cursor.fetchone()
            
            return {
                'fecha': hoy,
                'sesiones_scraping': {
                    'total': stats_sesiones[0] or 0,
                    'promedio_partidos': round(stats_sesiones[1] or 0, 1),
                    'duracion_promedio': round(stats_sesiones[2] or 0, 1)
                },
                'scrapers_automaticos': {
                    'total_programados': stats_scrapers[0] or 0,
                    'pendientes': stats_scrapers[1] or 0,
                    'ejecutados': stats_scrapers[2] or 0
                }
            }
    
    def limpiar_datos_antiguos(self, dias: int = 7):
        """Limpia datos antiguos para mantener la base de datos eficiente"""
        fecha_limite = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                DELETE FROM scraping_sessions 
                WHERE fecha < date(?, '-{} days')
            '''.format(dias), (fecha_limite,))
            
            conn.execute('''
                DELETE FROM scrapers_programados 
                WHERE fecha_partido < date(?, '-{} days')
            '''.format(dias), (fecha_limite,))
            
            conn.commit()

# Instancia global del gestor de datos
data_manager = DataManager()
