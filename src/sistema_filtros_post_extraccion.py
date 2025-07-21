"""
SISTEMA DE FILTROS POST-EXTRACCIÓN
=================================
Este módulo toma los datos YA EXTRAÍDOS y les aplica filtros.
Trabaja con consensos completos, no durante el scraping.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pytz
from dataclasses import dataclass, asdict
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class FiltrosConsensus:
    """Configuración de filtros para aplicar a consensos ya extraídos"""
    
    # Filtros básicos de consenso
    umbral_minimo: int = 70
    umbral_maximo: int = 95
    expertos_minimos: int = 15
    picks_minimos: int = 8
    
    # Filtros de partido
    total_line_min: float = 6.0
    total_line_max: float = 15.0
    direcciones_permitidas: List[str] = None
    
    # Filtros de horario
    horas_permitidas: List[str] = None  # ["18:00", "19:00"] etc
    minutos_antes_inicio: int = 15  # Alertar X minutos antes
    
    # Filtros de completitud
    requerir_equipos: bool = True
    requerir_hora: bool = False
    requerir_total_line: bool = False
    completitud_minima: str = "2/3"  # Mínimo 2 de 3 campos principales
    
    def __post_init__(self):
        if self.direcciones_permitidas is None:
            self.direcciones_permitidas = ['OVER', 'UNDER']
        if self.horas_permitidas is None:
            self.horas_permitidas = []  # Vacío = todas las horas

class FiltroConsensus:
    """Sistema de filtrado post-extracción"""
    
    def __init__(self, archivo_config: str = "config/filtros_consenso.json"):
        self.archivo_config = archivo_config
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        self.filtros = self.cargar_filtros()
        
    def cargar_filtros(self) -> FiltrosConsensus:
        """Cargar configuración de filtros"""
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return FiltrosConsensus(**data)
            else:
                # Crear configuración por defecto
                filtros_default = FiltrosConsensus()
                self.guardar_filtros(filtros_default)
                return filtros_default
        except Exception as e:
            logger.error(f"Error cargando filtros: {e}")
            return FiltrosConsensus()
    
    def guardar_filtros(self, filtros: FiltrosConsensus):
        """Guardar configuración de filtros"""
        try:
            os.makedirs(os.path.dirname(self.archivo_config), exist_ok=True)
            data = asdict(filtros)
            data['ultima_actualizacion'] = datetime.now(self.timezone).isoformat()
            
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Filtros guardados: {self.archivo_config}")
            
        except Exception as e:
            logger.error(f"Error guardando filtros: {e}")
    
    def aplicar_filtros(self, consensos: List[Dict], tipo_filtro: str = "alerta") -> Tuple[List[Dict], Dict]:
        """
        Aplicar filtros a lista de consensos
        
        Args:
            consensos: Lista de consensos extraídos
            tipo_filtro: 'alerta', 'revision', 'todos'
            
        Returns:
            Tuple[consensos_filtrados, estadisticas]
        """
        logger.info(f"🔍 Aplicando filtros '{tipo_filtro}' a {len(consensos)} consensos")
        
        consensos_validos = []
        estadisticas = {
            'total_inicial': len(consensos),
            'filtrados': 0,
            'rechazados_por': {
                'umbral_consenso': 0,
                'pocos_expertos': 0,
                'datos_incompletos': 0,
                'fuera_de_horario': 0,
                'direccion_no_permitida': 0,
                'total_line_invalido': 0,
                'otros': 0
            }
        }
        
        for consenso in consensos:
            resultado_filtro = self._evaluar_consenso(consenso, tipo_filtro)
            
            if resultado_filtro['aprobado']:
                # Enriquecer consenso con info de filtro
                consenso_enriquecido = consenso.copy()
                consenso_enriquecido['filtro_aplicado'] = tipo_filtro
                consenso_enriquecido['timestamp_filtrado'] = datetime.now(self.timezone).isoformat()
                consenso_enriquecido['razon_aprobacion'] = resultado_filtro['razon']
                consensos_validos.append(consenso_enriquecido)
            else:
                # Contar razón de rechazo
                razon = resultado_filtro['razon_rechazo']
                if razon in estadisticas['rechazados_por']:
                    estadisticas['rechazados_por'][razon] += 1
                else:
                    estadisticas['rechazados_por']['otros'] += 1
        
        estadisticas['filtrados'] = len(consensos_validos)
        
        logger.info(f"✅ Filtros aplicados: {estadisticas['filtrados']}/{estadisticas['total_inicial']} aprobados")
        
        # Log de rechazos si hay
        rechazos = estadisticas['rechazados_por']
        rechazos_totales = sum(rechazos.values())
        if rechazos_totales > 0:
            logger.info("📋 Razones de rechazo:")
            for razon, cantidad in rechazos.items():
                if cantidad > 0:
                    logger.info(f"   • {razon}: {cantidad}")
        
        return consensos_validos, estadisticas
    
    def _evaluar_consenso(self, consenso: Dict, tipo_filtro: str) -> Dict:
        """Evaluar si un consenso cumple los filtros"""
        
        # FILTRO 1: COMPLETITUD DE DATOS
        if not self._tiene_datos_minimos(consenso):
            return {
                'aprobado': False,
                'razon_rechazo': 'datos_incompletos',
                'detalle': 'Faltan datos esenciales'
            }
        
        # FILTRO 2: UMBRAL DE CONSENSO
        porcentaje = consenso.get('porcentaje_consenso', 0)
        if porcentaje < self.filtros.umbral_minimo or porcentaje > self.filtros.umbral_maximo:
            return {
                'aprobado': False,
                'razon_rechazo': 'umbral_consenso',
                'detalle': f'Porcentaje {porcentaje}% fuera del rango {self.filtros.umbral_minimo}-{self.filtros.umbral_maximo}%'
            }
        
        # FILTRO 3: NÚMERO DE EXPERTOS
        num_experts = max(consenso.get('num_experts', 0), consenso.get('total_picks', 0))
        if num_experts < self.filtros.expertos_minimos:
            return {
                'aprobado': False,
                'razon_rechazo': 'pocos_expertos',
                'detalle': f'{num_experts} expertos < {self.filtros.expertos_minimos} mínimo'
            }
        
        # FILTRO 4: DIRECCIÓN DEL CONSENSO
        direccion = consenso.get('direccion_consenso', '').upper()
        if direccion and direccion not in self.filtros.direcciones_permitidas:
            return {
                'aprobado': False,
                'razon_rechazo': 'direccion_no_permitida',
                'detalle': f'Dirección {direccion} no permitida'
            }
        
        # FILTRO 5: TOTAL LINE
        total_line = consenso.get('total_line')
        if total_line and (total_line < self.filtros.total_line_min or total_line > self.filtros.total_line_max):
            return {
                'aprobado': False,
                'razon_rechazo': 'total_line_invalido',
                'detalle': f'Total line {total_line} fuera del rango {self.filtros.total_line_min}-{self.filtros.total_line_max}'
            }
        
        # FILTRO 6: HORARIO (si está especificado)
        if self.filtros.horas_permitidas and consenso.get('hora_juego'):
            if not self._hora_permitida(consenso['hora_juego']):
                return {
                    'aprobado': False,
                    'razon_rechazo': 'fuera_de_horario',
                    'detalle': f'Hora {consenso["hora_juego"]} no permitida'
                }
        
        # Si llega aquí, aprobado
        return {
            'aprobado': True,
            'razon': f'{tipo_filtro}_aprobado',
            'detalle': f'Cumple todos los criterios para {tipo_filtro}'
        }
    
    def _tiene_datos_minimos(self, consenso: Dict) -> bool:
        """Verificar si tiene los datos mínimos requeridos"""
        
        # Verificar equipos si es requerido
        if self.filtros.requerir_equipos:
            if not consenso.get('equipo_visitante') or not consenso.get('equipo_local'):
                return False
        
        # Verificar completitud mínima
        completitud_actual = consenso.get('completitud', '0/3')
        if not self._cumple_completitud_minima(completitud_actual):
            return False
        
        # Verificar campos específicos si son requeridos
        if self.filtros.requerir_hora and not consenso.get('hora_juego'):
            return False
        
        if self.filtros.requerir_total_line and not consenso.get('total_line'):
            return False
        
        return True
    
    def _cumple_completitud_minima(self, completitud_actual: str) -> bool:
        """Verificar si cumple la completitud mínima"""
        try:
            actual_num, actual_den = map(int, completitud_actual.split('/'))
            min_num, min_den = map(int, self.filtros.completitud_minima.split('/'))
            
            # Calcular porcentajes
            porcentaje_actual = actual_num / actual_den if actual_den > 0 else 0
            porcentaje_minimo = min_num / min_den if min_den > 0 else 0
            
            return porcentaje_actual >= porcentaje_minimo
        except:
            return False
    
    def _hora_permitida(self, hora_juego: str) -> bool:
        """Verificar si la hora está permitida"""
        if not self.filtros.horas_permitidas:
            return True  # Si no hay restricciones, todas las horas son válidas
        
        # Extraer solo la hora de la cadena (ej: "7:10 pm ET" -> "19:10")
        import re
        match = re.search(r'(\d{1,2}):(\d{2})\s*([ap])m', hora_juego.lower())
        if match:
            hora, minuto, periodo = match.groups()
            hora_24 = int(hora)
            if periodo == 'p' and hora_24 != 12:
                hora_24 += 12
            elif periodo == 'a' and hora_24 == 12:
                hora_24 = 0
            
            hora_formateada = f"{hora_24:02d}:{minuto}"
            return hora_formateada in self.filtros.horas_permitidas
        
        return True  # Si no puede parsear, aceptar
    
    def filtros_por_horario(self, consensos: List[Dict]) -> Dict[str, List[Dict]]:
        """Organizar consensos por horarios para scraping programado"""
        
        consensos_por_hora = {
            'matutino': [],      # 06:00 - 12:00
            'tarde': [],         # 12:00 - 18:00
            'noche': [],         # 18:00 - 24:00
            'urgente': [],       # Próximos a comenzar
            'sin_hora': []       # Sin información de hora
        }
        
        ahora = datetime.now(self.timezone)
        
        for consenso in consensos:
            hora_juego = consenso.get('hora_juego', '')
            
            if not hora_juego:
                consensos_por_hora['sin_hora'].append(consenso)
                continue
            
            # Determinar categoría por hora
            try:
                # Parsear hora
                import re
                match = re.search(r'(\d{1,2}):(\d{2})\s*([ap])m', hora_juego.lower())
                if match:
                    hora, minuto, periodo = match.groups()
                    hora_24 = int(hora)
                    if periodo == 'p' and hora_24 != 12:
                        hora_24 += 12
                    elif periodo == 'a' and hora_24 == 12:
                        hora_24 = 0
                    
                    # Clasificar por franja horaria
                    if 6 <= hora_24 < 12:
                        consensos_por_hora['matutino'].append(consenso)
                    elif 12 <= hora_24 < 18:
                        consensos_por_hora['tarde'].append(consenso)
                    else:
                        consensos_por_hora['noche'].append(consenso)
                    
                    # Verificar si es urgente (próximo a comenzar)
                    # TODO: Implementar lógica de tiempo real
                    
            except:
                consensos_por_hora['sin_hora'].append(consenso)
        
        return consensos_por_hora
    
    def actualizar_filtros(self, **kwargs):
        """Actualizar filtros dinámicamente"""
        for key, value in kwargs.items():
            if hasattr(self.filtros, key):
                setattr(self.filtros, key, value)
                logger.info(f"📝 Filtro actualizado: {key} = {value}")
        
        self.guardar_filtros(self.filtros)
    
    def obtener_resumen(self) -> Dict:
        """Obtener resumen de la configuración actual"""
        return {
            'filtros_consenso': {
                'umbral_minimo': f"{self.filtros.umbral_minimo}%",
                'umbral_maximo': f"{self.filtros.umbral_maximo}%",
                'expertos_minimos': self.filtros.expertos_minimos,
                'picks_minimos': self.filtros.picks_minimos
            },
            'filtros_partido': {
                'direcciones_permitidas': self.filtros.direcciones_permitidas,
                'total_line_rango': f"{self.filtros.total_line_min}-{self.filtros.total_line_max}",
                'completitud_minima': self.filtros.completitud_minima
            },
            'filtros_horario': {
                'horas_permitidas': self.filtros.horas_permitidas or "Todas",
                'minutos_antes_inicio': self.filtros.minutos_antes_inicio
            },
            'configuracion': {
                'archivo': self.archivo_config,
                'requerir_equipos': self.filtros.requerir_equipos,
                'requerir_hora': self.filtros.requerir_hora,
                'requerir_total_line': self.filtros.requerir_total_line
            }
        }

def test_filtros():
    """Probar el sistema de filtros"""
    print("🧪 PROBANDO SISTEMA DE FILTROS POST-EXTRACCIÓN")
    print("=" * 60)
    
    # Crear datos de prueba
    consensos_prueba = [
        {
            'id_unico': 'test001',
            'equipo_visitante': 'NYY',
            'equipo_local': 'BOS',
            'direccion_consenso': 'OVER',
            'porcentaje_consenso': 85,
            'num_experts': 25,
            'total_picks': 28,
            'total_line': 9.5,
            'hora_juego': '7:10 pm ET',
            'completitud': '3/3',
            'campos_extraidos': ['equipos', 'consenso', 'picks']
        },
        {
            'id_unico': 'test002',
            'equipo_visitante': 'STL',
            'equipo_local': 'AZ',
            'direccion_consenso': 'UNDER',
            'porcentaje_consenso': 65,  # Bajo umbral
            'num_experts': 12,  # Pocos expertos
            'total_line': 8.0,
            'completitud': '2/3'
        },
        {
            'id_unico': 'test003',
            'equipo_visitante': None,  # Datos incompletos
            'equipo_local': 'CHI',
            'direccion_consenso': 'OVER',
            'porcentaje_consenso': 88,
            'completitud': '1/3'
        }
    ]
    
    # Inicializar filtro
    filtro_sistema = FiltroConsensus()
    
    # Mostrar configuración
    print("📋 Configuración de filtros:")
    resumen = filtro_sistema.obtener_resumen()
    for seccion, datos in resumen.items():
        print(f"\n   {seccion}:")
        for key, value in datos.items():
            print(f"      • {key}: {value}")
    
    # Aplicar filtros
    print(f"\n🔍 Aplicando filtros a {len(consensos_prueba)} consensos de prueba...")
    
    consensos_filtrados, estadisticas = filtro_sistema.aplicar_filtros(consensos_prueba, "alerta")
    
    print(f"\n📊 RESULTADOS:")
    print(f"   Total inicial: {estadisticas['total_inicial']}")
    print(f"   Aprobados: {estadisticas['filtrados']}")
    print(f"   Rechazados: {estadisticas['total_inicial'] - estadisticas['filtrados']}")
    
    print(f"\n📋 Consensos aprobados:")
    for consenso in consensos_filtrados:
        partido = f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}"
        print(f"   • {partido} - {consenso['direccion_consenso']} {consenso['porcentaje_consenso']}%")
    
    print(f"\n❌ Razones de rechazo:")
    for razon, cantidad in estadisticas['rechazados_por'].items():
        if cantidad > 0:
            print(f"   • {razon}: {cantidad}")
    
    # Probar organización por horarios
    print(f"\n⏰ Organización por horarios:")
    por_horario = filtro_sistema.filtros_por_horario(consensos_prueba)
    for franja, consensos_franja in por_horario.items():
        if consensos_franja:
            print(f"   {franja}: {len(consensos_franja)} consensos")

if __name__ == "__main__":
    test_filtros()
    input("\n⏸️ Presiona Enter para continuar...")
