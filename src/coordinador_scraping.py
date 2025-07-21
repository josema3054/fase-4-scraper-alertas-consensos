"""
COORDINADOR DEL SISTEMA DE SCRAPING
==================================
Este módulo coordina:
1. Scraper puro (extrae TODOS los datos)
2. Sistema de filtros (aplica criterios después)
3. Reintentos automáticos
4. Historial de alertas
5. Programación automática

Flujo: SCRAPER → DATOS → FILTROS → ALERTAS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.mlb_scraper_puro import MLBScraperPuro
from src.sistema_filtros_post_extraccion import FiltroConsensus
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pytz
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistorialAlertas:
    """Manejo del historial para evitar duplicados"""
    
    def __init__(self, archivo: str = "data/historial_alertas.json"):
        self.archivo = archivo
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        self.historial = self.cargar_historial()
    
    def cargar_historial(self) -> Dict:
        """Cargar historial desde archivo"""
        try:
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Error cargando historial: {e}")
            return {}
    
    def guardar_historial(self):
        """Guardar historial"""
        try:
            os.makedirs(os.path.dirname(self.archivo), exist_ok=True)
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.historial, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando historial: {e}")
    
    def generar_id_consenso(self, consenso: Dict) -> str:
        """Generar ID único para un consenso"""
        # Basado en partido + dirección + porcentaje
        data = f"{consenso.get('equipo_visitante', '')}_{consenso.get('equipo_local', '')}_{consenso.get('direccion_consenso', '')}_{consenso.get('porcentaje_consenso', 0)}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def es_consenso_nuevo(self, consenso: Dict) -> bool:
        """Verificar si es nuevo (no enviado antes)"""
        consenso_id = self.generar_id_consenso(consenso)
        fecha_hoy = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        return not (fecha_hoy in self.historial and consenso_id in self.historial[fecha_hoy])
    
    def marcar_consenso_enviado(self, consenso: Dict):
        """Marcar consenso como enviado"""
        consenso_id = self.generar_id_consenso(consenso)
        fecha_hoy = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        if fecha_hoy not in self.historial:
            self.historial[fecha_hoy] = {}
        
        self.historial[fecha_hoy][consenso_id] = {
            'partido': f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}",
            'consenso': f"{consenso.get('direccion_consenso', '?')} {consenso.get('porcentaje_consenso', 0)}%",
            'expertos': consenso.get('num_experts', 0),
            'timestamp': datetime.now(self.timezone).isoformat()
        }
        
        self.guardar_historial()
    
    def limpiar_historial_antiguo(self, dias: int = 7):
        """Limpiar historial de más de X días"""
        fecha_limite = datetime.now(self.timezone) - timedelta(days=dias)
        fechas_eliminar = []
        
        for fecha_str in self.historial.keys():
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
                if self.timezone.localize(fecha) < fecha_limite:
                    fechas_eliminar.append(fecha_str)
            except:
                continue
        
        for fecha in fechas_eliminar:
            del self.historial[fecha]
        
        if fechas_eliminar:
            self.guardar_historial()
            logger.info(f"🧹 Historial limpiado: {len(fechas_eliminar)} días eliminados")

class CoordinadorScraping:
    """Coordinador principal del sistema"""
    
    def __init__(self):
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        
        # Inicializar componentes
        self.scraper = MLBScraperPuro()
        self.filtro = FiltroConsensus()
        self.historial = HistorialAlertas()
        
        logger.info("🚀 Coordinador de scraping inicializado")
    
    def ejecutar_scraping_completo(self, fecha: Optional[str] = None) -> Dict:
        """
        FLUJO COMPLETO: Scraper → Filtros → Alertas
        
        Returns:
            Dict con resultados y estadísticas
        """
        inicio = time.time()
        
        if fecha is None:
            fecha = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        logger.info("🎯 INICIANDO SCRAPING COMPLETO")
        logger.info(f"   Fecha: {fecha}")
        logger.info("=" * 60)
        
        try:
            # PASO 1: SCRAPING PURO (sin filtros)
            logger.info("📡 PASO 1: Extrayendo TODOS los datos...")
            datos_puros = self.scraper.obtener_consensos_del_dia(fecha)
            
            if not datos_puros:
                return {
                    'exito': False,
                    'error': 'No se obtuvieron datos del scraper',
                    'datos_extraidos': 0,
                    'alertas_nuevas': 0,
                    'tiempo_total': time.time() - inicio
                }
            
            logger.info(f"✅ Datos extraídos: {len(datos_puros)} consensos totales")
            
            # PASO 2: APLICAR FILTROS
            logger.info("🔍 PASO 2: Aplicando filtros...")
            consensos_filtrados, stats_filtros = self.filtro.aplicar_filtros(datos_puros, "alerta")
            
            logger.info(f"✅ Filtros aplicados: {len(consensos_filtrados)} consensos válidos")
            
            # PASO 3: VERIFICAR DUPLICADOS
            logger.info("🔄 PASO 3: Verificando duplicados...")
            consensos_nuevos = []
            
            for consenso in consensos_filtrados:
                if self.historial.es_consenso_nuevo(consenso):
                    consensos_nuevos.append(consenso)
                else:
                    logger.debug(f"⏭️ Ya enviado: {consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}")
            
            logger.info(f"✅ Consensos nuevos: {len(consensos_nuevos)}")
            
            # PASO 4: PROCESAR ALERTAS
            logger.info("📢 PASO 4: Procesando alertas...")
            alertas_enviadas = self.procesar_alertas(consensos_nuevos)
            
            # PASO 5: ESTADÍSTICAS
            tiempo_total = time.time() - inicio
            
            resultado = {
                'exito': True,
                'fecha_procesada': fecha,
                'timestamp': datetime.now(self.timezone).isoformat(),
                
                # Datos del scraper
                'datos_extraidos': len(datos_puros),
                'datos_completos': len([d for d in datos_puros if d.get('completitud') == '3/3']),
                'datos_parciales': len([d for d in datos_puros if d.get('completitud') != '3/3']),
                
                # Datos de filtros
                'consensos_filtrados': len(consensos_filtrados),
                'filtros_aplicados': stats_filtros,
                
                # Alertas
                'alertas_nuevas': len(consensos_nuevos),
                'alertas_enviadas': len(alertas_enviadas),
                
                # Performance
                'tiempo_total': round(tiempo_total, 2),
                'consensos_por_segundo': round(len(datos_puros) / tiempo_total, 2) if tiempo_total > 0 else 0
            }
            
            logger.info("📊 RESULTADO COMPLETO:")
            logger.info(f"   📡 Datos extraídos: {resultado['datos_extraidos']} (Completos: {resultado['datos_completos']}, Parciales: {resultado['datos_parciales']})")
            logger.info(f"   🔍 Consensos filtrados: {resultado['consensos_filtrados']}")
            logger.info(f"   📢 Alertas nuevas: {resultado['alertas_nuevas']}")
            logger.info(f"   ⏱️  Tiempo total: {resultado['tiempo_total']} segundos")
            
            return resultado
            
        except Exception as e:
            logger.error(f"💥 Error en scraping completo: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'exito': False,
                'error': str(e),
                'datos_extraidos': 0,
                'alertas_nuevas': 0,
                'tiempo_total': time.time() - inicio
            }
    
    def ejecutar_con_reintentos(self, max_intentos: int = 3, delay_minutos: int = 2) -> Dict:
        """Ejecutar con sistema de reintentos"""
        
        logger.info(f"🔄 SCRAPING CON REINTENTOS (máx {max_intentos})")
        
        for intento in range(1, max_intentos + 1):
            try:
                logger.info(f"🚀 Intento {intento}/{max_intentos}")
                
                resultado = self.ejecutar_scraping_completo()
                
                if resultado['exito'] and resultado['datos_extraidos'] > 0:
                    logger.info(f"✅ Éxito en intento {intento}")
                    return resultado
                else:
                    logger.warning(f"⚠️ Intento {intento} sin resultados válidos")
                
            except Exception as e:
                logger.error(f"❌ Intento {intento} falló: {e}")
            
            # Esperar antes del siguiente intento
            if intento < max_intentos:
                delay_segundos = delay_minutos * 60 * intento  # Delay incremental
                logger.info(f"⏳ Esperando {delay_segundos//60} minutos antes del siguiente intento...")
                time.sleep(delay_segundos)
        
        # Si llega aquí, todos fallaron
        logger.error("💥 Todos los intentos fallaron")
        return {
            'exito': False,
            'error': 'Todos los reintentos agotados',
            'intentos_realizados': max_intentos,
            'datos_extraidos': 0,
            'alertas_nuevas': 0
        }
    
    def procesar_alertas(self, consensos: List[Dict]) -> List[Dict]:
        """Procesar consensos como alertas"""
        alertas_procesadas = []
        
        for consenso in consensos:
            try:
                # Marcar como enviado
                self.historial.marcar_consenso_enviado(consenso)
                
                # Enriquecer con datos de alerta
                alerta = consenso.copy()
                alerta['tipo'] = 'nueva_alerta'
                alerta['timestamp_alerta'] = datetime.now(self.timezone).isoformat()
                alerta['urgencia'] = self._calcular_urgencia(consenso)
                
                alertas_procesadas.append(alerta)
                
                # Log de alerta
                partido = f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}"
                consenso_info = f"{consenso.get('direccion_consenso', '?')} {consenso.get('porcentaje_consenso', 0)}%"
                expertos = consenso.get('num_experts', 0)
                
                logger.info(f"📢 ALERTA: {partido} - {consenso_info} ({expertos} expertos)")
                
            except Exception as e:
                logger.error(f"Error procesando alerta: {e}")
        
        return alertas_procesadas
    
    def _calcular_urgencia(self, consenso: Dict) -> str:
        """Calcular urgencia de la alerta"""
        porcentaje = consenso.get('porcentaje_consenso', 0)
        expertos = consenso.get('num_experts', 0)
        
        if porcentaje >= 85 and expertos >= 25:
            return 'ALTA'
        elif porcentaje >= 75 and expertos >= 15:
            return 'MEDIA'
        else:
            return 'BAJA'
    
    def obtener_estadisticas_historicas(self, dias: int = 7) -> Dict:
        """Obtener estadísticas de los últimos días"""
        historial = self.historial.historial
        
        fecha_limite = datetime.now(self.timezone) - timedelta(days=dias)
        alertas_periodo = {}
        
        for fecha_str, alertas in historial.items():
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
                if self.timezone.localize(fecha) >= fecha_limite:
                    alertas_periodo[fecha_str] = alertas
            except:
                continue
        
        total_alertas = sum(len(alertas) for alertas in alertas_periodo.values())
        
        return {
            'periodo_dias': dias,
            'fechas_con_alertas': len(alertas_periodo),
            'total_alertas': total_alertas,
            'promedio_diario': round(total_alertas / max(dias, 1), 2),
            'detalle_por_fecha': alertas_periodo
        }
    
    def limpiar_sistema(self):
        """Limpiar datos antiguos"""
        self.historial.limpiar_historial_antiguo()
    
    def configurar_filtros(self, **kwargs):
        """Configurar filtros dinámicamente"""
        self.filtro.actualizar_filtros(**kwargs)
    
    def obtener_resumen_configuracion(self) -> Dict:
        """Resumen de toda la configuración"""
        return {
            'scraper': {
                'tipo': 'MLBScraperPuro',
                'extrae_datos_sin_filtrar': True
            },
            'filtros': self.filtro.obtener_resumen(),
            'historial': {
                'archivo': self.historial.archivo,
                'alertas_hoy': len(self.historial.historial.get(datetime.now(self.timezone).strftime('%Y-%m-%d'), {}))
            }
        }

def test_coordinador():
    """Test del coordinador completo"""
    print("🧪 PROBANDO COORDINADOR COMPLETO")
    print("=" * 60)
    
    try:
        # Inicializar coordinador
        coordinador = CoordinadorScraping()
        
        # Mostrar configuración
        print("📋 Configuración del sistema:")
        config = coordinador.obtener_resumen_configuracion()
        for seccion, datos in config.items():
            print(f"\n   {seccion}:")
            if isinstance(datos, dict):
                for key, value in datos.items():
                    if isinstance(value, dict):
                        print(f"      {key}:")
                        for subkey, subvalue in value.items():
                            print(f"         • {subkey}: {subvalue}")
                    else:
                        print(f"      • {key}: {value}")
            else:
                print(f"      {datos}")
        
        # Ejecutar scraping completo
        print(f"\n🚀 Ejecutando scraping completo...")
        resultado = coordinador.ejecutar_scraping_completo()
        
        print(f"\n📊 RESULTADO FINAL:")
        if resultado['exito']:
            print(f"   ✅ ÉXITO")
            print(f"   📡 Datos extraídos: {resultado['datos_extraidos']}")
            print(f"      • Completos: {resultado['datos_completos']}")
            print(f"      • Parciales: {resultado['datos_parciales']}")
            print(f"   🔍 Consensos filtrados: {resultado['consensos_filtrados']}")
            print(f"   📢 Alertas nuevas: {resultado['alertas_nuevas']}")
            print(f"   ⏱️  Tiempo total: {resultado['tiempo_total']} segundos")
            print(f"   📈 Performance: {resultado['consensos_por_segundo']} consensos/segundo")
        else:
            print(f"   ❌ ERROR: {resultado['error']}")
        
        # Mostrar estadísticas históricas
        print(f"\n📈 Estadísticas históricas:")
        stats = coordinador.obtener_estadisticas_historicas()
        print(f"   • Últimos {stats['periodo_dias']} días")
        print(f"   • Total alertas: {stats['total_alertas']}")
        print(f"   • Promedio diario: {stats['promedio_diario']}")
        
        # Guardar resultado para análisis
        with open('resultado_coordinador.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultado guardado: resultado_coordinador.json")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

def test_con_reintentos():
    """Test del coordinador con reintentos"""
    print("🔄 PROBANDO COORDINADOR CON REINTENTOS")
    print("=" * 60)
    
    coordinador = CoordinadorScraping()
    
    # Configurar filtros más permisivos para testing
    coordinador.configurar_filtros(
        umbral_minimo=60,
        expertos_minimos=10,
        completitud_minima="1/3"
    )
    
    print("⚙️ Filtros configurados para testing (más permisivos)")
    
    # Ejecutar con reintentos
    resultado = coordinador.ejecutar_con_reintentos(max_intentos=2, delay_minutos=1)
    
    print(f"\n📊 RESULTADO CON REINTENTOS:")
    for key, value in resultado.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    print("¿Qué test quieres ejecutar?")
    print("1. Test coordinador básico")
    print("2. Test con reintentos")
    
    opcion = input("Opción (1-2): ").strip()
    
    if opcion == "2":
        test_con_reintentos()
    else:
        test_coordinador()
    
    input("\n⏸️ Presiona Enter para continuar...")
