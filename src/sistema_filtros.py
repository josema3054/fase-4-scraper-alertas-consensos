"""
SISTEMA DE FILTROS VARIABLES Y SCHEDULER AUTOMÁTICO
==================================================
Este módulo maneja los filtros de consensos y programa los scrapings automáticos
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from dataclasses import dataclass
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FiltroConsensus:
    """Configuración de filtros para consensos"""
    umbral_minimo: int = 70  # % mínimo de consenso
    expertos_minimos: int = 15  # Cantidad mínima de expertos
    picks_minimos: int = 8  # Picks mínimos totales
    direccion_permitida: List[str] = None  # ['OVER', 'UNDER'] o None para ambas
    total_line_min: float = 6.0  # Total mínimo
    total_line_max: float = 15.0  # Total máximo
    
    def __post_init__(self):
        if self.direccion_permitida is None:
            self.direccion_permitida = ['OVER', 'UNDER']

class SistemaFiltros:
    """Sistema de filtros variables para consensos"""
    
    def __init__(self, config_path: str = "config/filtros_consensos.json"):
        self.config_path = config_path
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        self.filtros = self.cargar_filtros()
    
    def cargar_filtros(self) -> FiltroConsensus:
        """Cargar filtros desde archivo de configuración"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                return FiltroConsensus(
                    umbral_minimo=config.get('umbral_minimo', 70),
                    expertos_minimos=config.get('expertos_minimos', 15),
                    picks_minimos=config.get('picks_minimos', 8),
                    direccion_permitida=config.get('direccion_permitida', ['OVER', 'UNDER']),
                    total_line_min=config.get('total_line_min', 6.0),
                    total_line_max=config.get('total_line_max', 15.0)
                )
            else:
                # Crear archivo de configuración por defecto
                filtros_default = FiltroConsensus()
                self.guardar_filtros(filtros_default)
                return filtros_default
                
        except Exception as e:
            logger.error(f"Error cargando filtros: {e}")
            return FiltroConsensus()  # Usar valores por defecto
    
    def guardar_filtros(self, filtros: FiltroConsensus):
        """Guardar filtros en archivo de configuración"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'umbral_minimo': filtros.umbral_minimo,
                'expertos_minimos': filtros.expertos_minimos,
                'picks_minimos': filtros.picks_minimos,
                'direccion_permitida': filtros.direccion_permitida,
                'total_line_min': filtros.total_line_min,
                'total_line_max': filtros.total_line_max,
                'ultima_actualizacion': datetime.now(self.timezone).isoformat()
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.filtros = filtros
            logger.info(f"✅ Filtros guardados: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error guardando filtros: {e}")
    
    def aplicar_filtros(self, consensos: List[Dict]) -> List[Dict]:
        """Aplicar filtros a una lista de consensos"""
        consensos_validos = []
        
        for consenso in consensos:
            if self._consenso_cumple_filtros(consenso):
                consensos_validos.append(consenso)
        
        logger.info(f"🔍 Filtros aplicados: {len(consensos_validos)}/{len(consensos)} consensos válidos")
        return consensos_validos
    
    def _consenso_cumple_filtros(self, consenso: Dict) -> bool:
        """Verificar si un consenso cumple todos los filtros"""
        try:
            # Verificar umbral mínimo
            porcentaje = consenso.get('porcentaje_consenso', 0)
            if porcentaje < self.filtros.umbral_minimo:
                return False
            
            # Verificar expertos mínimos
            num_experts = consenso.get('num_experts', 0)
            total_picks = consenso.get('total_picks', 0)
            experts_a_verificar = max(num_experts, total_picks)
            
            if experts_a_verificar < self.filtros.expertos_minimos:
                return False
            
            # Verificar picks mínimos
            if total_picks < self.filtros.picks_minimos:
                return False
            
            # Verificar dirección permitida
            direccion = consenso.get('direccion_consenso', '').upper()
            if direccion not in self.filtros.direccion_permitida:
                return False
            
            # Verificar total line
            total_line = consenso.get('total_line', 0)
            if total_line and (total_line < self.filtros.total_line_min or total_line > self.filtros.total_line_max):
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Error verificando filtros para consenso: {e}")
            return False
    
    def actualizar_filtros(self, **kwargs):
        """Actualizar filtros dinámicamente"""
        filtros_actuales = self.filtros
        
        # Actualizar campos proporcionados
        for key, value in kwargs.items():
            if hasattr(filtros_actuales, key):
                setattr(filtros_actuales, key, value)
                logger.info(f"📝 Filtro actualizado: {key} = {value}")
        
        # Guardar cambios
        self.guardar_filtros(filtros_actuales)
    
    def obtener_resumen_filtros(self) -> Dict:
        """Obtener resumen de filtros actuales"""
        return {
            'umbral_minimo': f"{self.filtros.umbral_minimo}%",
            'expertos_minimos': self.filtros.expertos_minimos,
            'picks_minimos': self.filtros.picks_minimos,
            'direcciones_permitidas': self.filtros.direccion_permitida,
            'total_line_rango': f"{self.filtros.total_line_min} - {self.filtros.total_line_max}",
            'archivo_config': self.config_path
        }

class SistemaReintentos:
    """Sistema de reintentos para scraping con backoff exponencial"""
    
    def __init__(self, max_intentos: int = 3, delay_inicial: int = 120):  # 2 minutos
        self.max_intentos = max_intentos
        self.delay_inicial = delay_inicial
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
    
    def ejecutar_con_reintentos(self, func, *args, **kwargs):
        """Ejecutar función con sistema de reintentos"""
        ultimo_error = None
        
        for intento in range(1, self.max_intentos + 1):
            try:
                logger.info(f"🔄 Intento {intento}/{self.max_intentos}")
                resultado = func(*args, **kwargs)
                
                if resultado:  # Si hay resultado válido
                    logger.info(f"✅ Éxito en intento {intento}")
                    return resultado
                else:
                    logger.warning(f"⚠️ Intento {intento} sin resultados")
                    
            except Exception as e:
                ultimo_error = e
                logger.error(f"❌ Intento {intento} falló: {e}")
            
            # Si no es el último intento, esperar antes del siguiente
            if intento < self.max_intentos:
                delay = self.delay_inicial * intento  # Incrementar delay
                logger.info(f"⏳ Esperando {delay} segundos antes del siguiente intento...")
                time.sleep(delay)
        
        # Si llegamos aquí, todos los intentos fallaron
        logger.error(f"💥 Todos los intentos fallaron. Último error: {ultimo_error}")
        raise ultimo_error if ultimo_error else Exception("Todos los reintentos agotados")

def ejemplo_uso():
    """Ejemplo de uso del sistema de filtros"""
    print("🧪 PROBANDO SISTEMA DE FILTROS")
    print("="*50)
    
    # Inicializar sistema de filtros
    sistema_filtros = SistemaFiltros()
    
    # Mostrar filtros actuales
    print("📋 Filtros actuales:")
    resumen = sistema_filtros.obtener_resumen_filtros()
    for key, value in resumen.items():
        print(f"   {key}: {value}")
    
    # Ejemplo de consenso
    consenso_ejemplo = {
        'equipo_visitante': 'NYY',
        'equipo_local': 'BOS',
        'porcentaje_consenso': 85,
        'direccion_consenso': 'OVER',
        'num_experts': 25,
        'total_picks': 28,
        'total_line': 9.5
    }
    
    # Probar filtros
    print(f"\n🧪 Probando consenso ejemplo:")
    print(f"   {consenso_ejemplo['equipo_visitante']} @ {consenso_ejemplo['equipo_local']}")
    print(f"   {consenso_ejemplo['direccion_consenso']} {consenso_ejemplo['porcentaje_consenso']}%")
    print(f"   Expertos: {consenso_ejemplo['num_experts']}, Picks: {consenso_ejemplo['total_picks']}")
    
    resultado = sistema_filtros.aplicar_filtros([consenso_ejemplo])
    print(f"   Resultado: {'✅ CUMPLE' if resultado else '❌ NO CUMPLE'}")
    
    # Probar sistema de reintentos
    print(f"\n🔄 Probando sistema de reintentos...")
    sistema_reintentos = SistemaReintentos(max_intentos=2, delay_inicial=5)
    
    def funcion_que_falla():
        print("   Simulando función que falla...")
        raise Exception("Error simulado")
    
    try:
        sistema_reintentos.ejecutar_con_reintentos(funcion_que_falla)
    except Exception as e:
        print(f"   Final: {e}")

if __name__ == "__main__":
    ejemplo_uso()
