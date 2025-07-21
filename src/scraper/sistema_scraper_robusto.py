"""
SISTEMA SCRAPER ROBUSTO CON FILTROS VARIABLES Y REINTENTOS
=========================================================
Sistema completo que integra:
- Scraper Selenium robusto
- Filtros variables configurables
- Sistema de reintentos inteligente
- Historial de alertas para evitar duplicados
- Scheduler automático
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from dataclasses import dataclass, asdict
import hashlib
import logging

# Agregar rutas para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.mlb_selenium_scraper import MLBSeleniumScraper

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ConfiguracionFiltros:
    """Configuración completa de filtros para consensos"""
    # Filtros básicos
    umbral_minimo: int = 70
    expertos_minimos: int = 15
    picks_minimos: int = 8
    
    # Filtros avanzados
    direccion_permitida: Optional[List[str]] = None
    total_line_min: float = 6.0
    total_line_max: float = 15.0
    
    # Filtros dinámicos por hora
    filtros_por_hora: Optional[Dict[str, Dict]] = None  # Ej: {"09:00": {"umbral_minimo": 80}}
    
    # Configuración de scraping
    horas_scraping: Optional[List[str]] = None  # ["09:00", "15:00", "antes_partido"]
    minutos_antes_partido: int = 15
    
    def __post_init__(self):
        if self.direccion_permitida is None:
            self.direccion_permitida = ['OVER', 'UNDER']
        if self.horas_scraping is None:
            self.horas_scraping = ["09:00", "antes_partido"]
        if self.filtros_por_hora is None:
            self.filtros_por_hora = {}

class HistorialAlertas:
    """Manejo del historial de alertas para evitar duplicados"""
    
    def __init__(self, archivo_historial: str = "data/historial_alertas.json"):
        self.archivo_historial = archivo_historial
        self.historial = self.cargar_historial()
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
    
    def cargar_historial(self) -> Dict:
        """Cargar historial desde archivo"""
        try:
            if os.path.exists(self.archivo_historial):
                with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Error cargando historial: {e}")
            return {}
    
    def guardar_historial(self):
        """Guardar historial en archivo"""
        try:
            os.makedirs(os.path.dirname(self.archivo_historial), exist_ok=True)
            with open(self.archivo_historial, 'w', encoding='utf-8') as f:
                json.dump(self.historial, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando historial: {e}")
    
    def generar_id_consenso(self, consenso: Dict) -> str:
        """Generar ID único para un consenso"""
        # Crear ID basado en partido y porcentaje
        data = f"{consenso.get('equipo_visitante', '')}_{consenso.get('equipo_local', '')}_{consenso.get('direccion_consenso', '')}_{consenso.get('porcentaje_consenso', 0)}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def es_consenso_nuevo(self, consenso: Dict) -> bool:
        """Verificar si un consenso es nuevo (no enviado antes)"""
        consenso_id = self.generar_id_consenso(consenso)
        fecha_actual = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        # Verificar si ya fue enviado hoy
        if fecha_actual in self.historial:
            if consenso_id in self.historial[fecha_actual]:
                return False
        
        return True
    
    def marcar_consenso_enviado(self, consenso: Dict):
        """Marcar un consenso como enviado"""
        consenso_id = self.generar_id_consenso(consenso)
        fecha_actual = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        if fecha_actual not in self.historial:
            self.historial[fecha_actual] = {}
        
        self.historial[fecha_actual][consenso_id] = {
            'equipo_visitante': consenso.get('equipo_visitante'),
            'equipo_local': consenso.get('equipo_local'),
            'consenso': f"{consenso.get('direccion_consenso')} {consenso.get('porcentaje_consenso')}%",
            'timestamp': datetime.now(self.timezone).isoformat()
        }
        
        self.guardar_historial()
        logger.info(f"📝 Consenso marcado como enviado: {consenso_id}")
    
    def limpiar_historial_antiguo(self, dias_mantener: int = 7):
        """Limpiar historial de días anteriores"""
        fecha_limite = datetime.now(self.timezone) - timedelta(days=dias_mantener)
        fechas_a_eliminar = []
        
        for fecha_str in self.historial.keys():
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
                fecha = self.timezone.localize(fecha)
                if fecha < fecha_limite:
                    fechas_a_eliminar.append(fecha_str)
            except:
                continue
        
        for fecha in fechas_a_eliminar:
            del self.historial[fecha]
        
        if fechas_a_eliminar:
            self.guardar_historial()
            logger.info(f"🧹 Historial limpiado: {len(fechas_a_eliminar)} días antiguos eliminados")

class ScraperRobusto:
    """Sistema scraper robusto con filtros y reintentos"""
    
    def __init__(self, archivo_config: str = "config/scraper_config.json"):
        self.archivo_config = archivo_config
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        
        # Cargar configuración
        self.config = self.cargar_configuracion()
        
        # Inicializar componentes
        self.historial = HistorialAlertas()
        self.scraper = MLBSeleniumScraper()
        
        logger.info("🚀 Sistema scraper robusto inicializado")
    
    def cargar_configuracion(self) -> ConfiguracionFiltros:
        """Cargar configuración desde archivo"""
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Remover campos que no pertenecen a ConfiguracionFiltros
                    data.pop('ultima_actualizacion', None)
                    return ConfiguracionFiltros(**data)
            else:
                # Crear configuración por defecto
                config_default = ConfiguracionFiltros()
                self.guardar_configuracion(config_default)
                return config_default
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return ConfiguracionFiltros()
    
    def guardar_configuracion(self, config: ConfiguracionFiltros):
        """Guardar configuración en archivo"""
        try:
            os.makedirs(os.path.dirname(self.archivo_config), exist_ok=True)
            
            # Convertir a diccionario
            data = asdict(config)
            data['ultima_actualizacion'] = datetime.now(self.timezone).isoformat()
            
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Configuración guardada: {self.archivo_config}")
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def obtener_filtros_actuales(self) -> ConfiguracionFiltros:
        """Obtener filtros ajustados por hora si corresponde"""
        hora_actual = datetime.now(self.timezone).strftime('%H:%M')
        config_actual = self.config
        
        # Verificar si hay filtros específicos para esta hora
        if hora_actual in config_actual.filtros_por_hora:
            logger.info(f"🕐 Aplicando filtros específicos para las {hora_actual}")
            filtros_hora = config_actual.filtros_por_hora[hora_actual]
            
            # Crear nueva configuración con los ajustes
            config_ajustada = ConfiguracionFiltros(**asdict(config_actual))
            for key, value in filtros_hora.items():
                if hasattr(config_ajustada, key):
                    setattr(config_ajustada, key, value)
                    logger.info(f"   📝 {key}: {getattr(config_actual, key)} → {value}")
            
            return config_ajustada
        
        return config_actual
    
    def aplicar_filtros(self, consensos: List[Dict]) -> List[Dict]:
        """Aplicar filtros a consensos con configuración actual"""
        config = self.obtener_filtros_actuales()
        consensos_validos = []
        
        logger.info(f"🔍 Aplicando filtros (Umbral: {config.umbral_minimo}%, Expertos: {config.expertos_minimos})")
        
        for consenso in consensos:
            if self._consenso_cumple_filtros(consenso, config):
                # Verificar si es nuevo (no enviado antes)
                if self.historial.es_consenso_nuevo(consenso):
                    consensos_validos.append(consenso)
                else:
                    logger.debug(f"⏭️ Consenso ya enviado: {consenso.get('equipo_visitante')} @ {consenso.get('equipo_local')}")
        
        logger.info(f"✅ Filtros aplicados: {len(consensos_validos)}/{len(consensos)} consensos válidos y nuevos")
        return consensos_validos
    
    def _consenso_cumple_filtros(self, consenso: Dict, config: ConfiguracionFiltros) -> bool:
        """Verificar si consenso cumple filtros"""
        try:
            # Verificar umbral mínimo
            porcentaje = consenso.get('porcentaje_consenso', 0)
            if porcentaje < config.umbral_minimo:
                return False
            
            # Verificar expertos mínimos
            num_experts = consenso.get('num_experts', 0)
            total_picks = consenso.get('total_picks', 0)
            experts_a_verificar = max(num_experts, total_picks)
            
            if experts_a_verificar < config.expertos_minimos:
                return False
            
            # Verificar picks mínimos
            if total_picks < config.picks_minimos:
                return False
            
            # Verificar dirección permitida
            direccion = consenso.get('direccion_consenso', '').upper()
            if direccion not in config.direccion_permitida:
                return False
            
            # Verificar total line
            total_line = consenso.get('total_line', 0)
            if total_line and (total_line < config.total_line_min or total_line > config.total_line_max):
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Error verificando filtros: {e}")
            return False
    
    def scrape_con_reintentos(self, max_intentos: int = 3) -> List[Dict]:
        """Scraping con sistema de reintentos inteligente - EXTRAE TODOS LOS DATOS"""
        logger.info(f"🔄 Iniciando scraping con hasta {max_intentos} intentos")
        
        for intento in range(1, max_intentos + 1):
            try:
                logger.info(f"🚀 Intento {intento}/{max_intentos}")
                
                # Realizar scraping - EXTRAER TODO
                consensos = self.scraper.scrape_mlb_consensus()
                
                if consensos:
                    logger.info(f"✅ Éxito en intento {intento}: {len(consensos)} consensos encontrados")
                    
                    # NO aplicar filtros aquí - devolver TODOS los datos
                    logger.info("📊 Devolviendo TODOS los consensos extraídos (sin filtros)")
                    return consensos
                else:
                    logger.warning(f"⚠️ Intento {intento}: Sin resultados")
                    
            except Exception as e:
                logger.error(f"❌ Intento {intento} falló: {e}")
                
                # Si no es el último intento, esperar
                if intento < max_intentos:
                    delay = 120 * intento  # 2, 4, 6 minutos
                    logger.info(f"⏳ Esperando {delay//60} minutos antes del siguiente intento...")
                    time.sleep(delay)
        
        logger.error(f"💥 Todos los intentos fallaron")
        return []
    
    def aplicar_filtros_para_alertas(self, consensos: List[Dict]) -> List[Dict]:
        """Aplicar filtros SOLO para determinar qué consensos enviar como alertas"""
        if not consensos:
            return []
        
        logger.info(f"🔍 Aplicando filtros (Umbral: {self.config.umbral_minimo}%, Expertos: {self.config.expertos_minimos})")
        
        consensos_filtrados = []
        for consenso in consensos:
            if self._consenso_cumple_filtros(consenso, self.config):
                if not self.historial.consenso_ya_enviado(consenso):
                    consensos_filtrados.append(consenso)
        
        logger.info(f"✅ Filtros aplicados: {len(consensos_filtrados)}/{len(consensos)} consensos válidos y nuevos")
        return consensos_filtrados
    
    def procesar_alertas(self, consensos: List[Dict]) -> List[Dict]:
        """Procesar consensos y marcarlos como enviados"""
        alertas_procesadas = []
        
        for consenso in consensos:
            try:
                # Marcar como enviado
                self.historial.marcar_consenso_enviado(consenso)
                alertas_procesadas.append(consenso)
                
                logger.info(f"📢 Alerta procesada: {consenso['equipo_visitante']} @ {consenso['equipo_local']} "
                           f"- {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
                
            except Exception as e:
                logger.error(f"Error procesando alerta: {e}")
        
        return alertas_procesadas
    
    def ejecutar_ciclo_completo(self) -> Dict:
        """Ejecutar ciclo completo de scraping, filtrado y procesamiento"""
        inicio = time.time()
        
        logger.info("🎯 INICIANDO CICLO COMPLETO DE SCRAPING")
        logger.info("="*60)
        
        try:
            # Limpiar historial antiguo
            self.historial.limpiar_historial_antiguo()
            
            # Scraping con reintentos
            consensos_filtrados = self.scrape_con_reintentos()
            
            # Procesar alertas
            alertas_enviadas = self.procesar_alertas(consensos_filtrados)
            
            # Estadísticas
            tiempo_total = time.time() - inicio
            resultado = {
                'consensos_encontrados': len(consensos_filtrados),
                'alertas_enviadas': len(alertas_enviadas),
                'tiempo_procesamiento': round(tiempo_total, 2),
                'timestamp': datetime.now(self.timezone).isoformat(),
                'exito': len(alertas_enviadas) > 0
            }
            
            logger.info(f"📊 RESULTADO CICLO COMPLETO:")
            logger.info(f"   Consensos encontrados: {resultado['consensos_encontrados']}")
            logger.info(f"   Alertas enviadas: {resultado['alertas_enviadas']}")
            logger.info(f"   Tiempo total: {resultado['tiempo_procesamiento']} segundos")
            
            return resultado
            
        except Exception as e:
            logger.error(f"💥 Error en ciclo completo: {e}")
            return {
                'consensos_encontrados': 0,
                'alertas_enviadas': 0,
                'tiempo_procesamiento': time.time() - inicio,
                'error': str(e),
                'exito': False
            }
    
    def actualizar_configuracion(self, **kwargs):
        """Actualizar configuración dinámicamente"""
        logger.info("📝 Actualizando configuración...")
        
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                old_value = getattr(self.config, key)
                setattr(self.config, key, value)
                logger.info(f"   {key}: {old_value} → {value}")
        
        self.guardar_configuracion(self.config)
        logger.info("✅ Configuración actualizada")
    
    def obtener_resumen_configuracion(self) -> Dict:
        """Obtener resumen de la configuración actual"""
        config = self.obtener_filtros_actuales()
        return {
            'filtros_basicos': {
                'umbral_minimo': f"{config.umbral_minimo}%",
                'expertos_minimos': config.expertos_minimos,
                'picks_minimos': config.picks_minimos
            },
            'filtros_avanzados': {
                'direcciones_permitidas': config.direccion_permitida,
                'total_line_rango': f"{config.total_line_min} - {config.total_line_max}"
            },
            'configuracion_scraping': {
                'horas_scraping': config.horas_scraping,
                'minutos_antes_partido': config.minutos_antes_partido
            },
            'archivos': {
                'configuracion': self.archivo_config,
                'historial': self.historial.archivo_historial
            }
        }

def test_sistema_robusto():
    """Función de prueba del sistema completo"""
    print("🧪 PROBANDO SISTEMA SCRAPER ROBUSTO")
    print("="*60)
    
    try:
        # Inicializar sistema
        sistema = ScraperRobusto()
        
        # Mostrar configuración
        print("📋 Configuración actual:")
        resumen = sistema.obtener_resumen_configuracion()
        for seccion, datos in resumen.items():
            print(f"\n   {seccion}:")
            for key, value in datos.items():
                print(f"      {key}: {value}")
        
        # Ejecutar ciclo de prueba
        print(f"\n🚀 Ejecutando ciclo de prueba...")
        resultado = sistema.ejecutar_ciclo_completo()
        
        print(f"\n📊 Resultado:")
        for key, value in resultado.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sistema_robusto()
    input("\n⏸️ Presiona Enter para continuar...")
