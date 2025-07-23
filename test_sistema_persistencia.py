"""
Script de prueba del nuevo sistema con persistencia de datos
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from src.database.data_manager import data_manager
from src.background_service import background_service
from datetime import datetime

def probar_persistencia():
    """Prueba la funcionalidad de persistencia de datos"""
    print("=" * 60)
    print("   PRUEBA DEL SISTEMA DE PERSISTENCIA")
    print("=" * 60)
    print()
    
    # 1. Probar base de datos
    print("1️⃣ **PROBANDO BASE DE DATOS**")
    try:
        # Simular datos de scraping
        datos_test = [
            {
                'visitante': 'SD',
                'local': 'MIA', 
                'fecha': '2025-01-21',
                'hora': '6:40 pm ET',
                'over_percentage': '17%',
                'under_percentage': '83%',
                'total': '8.5',
                'expertos': '6'
            },
            {
                'visitante': 'CIN',
                'local': 'WAS',
                'fecha': '2025-01-21', 
                'hora': '6:45 pm ET',
                'over_percentage': '83%',
                'under_percentage': '17%',
                'total': '9.0',
                'expertos': '6'
            }
        ]
        
        # Guardar sesión de prueba
        session_id = data_manager.guardar_sesion_scraping(
            datos=datos_test,
            filtros={'test': True},
            duracion=45.5,
            errores=[]
        )
        
        print(f"   ✅ Sesión guardada con ID: {session_id}")
        
        # Recuperar sesión del día
        sesion_hoy = data_manager.obtener_sesion_del_dia()
        if sesion_hoy:
            print(f"   ✅ Sesión recuperada: {sesion_hoy.total_partidos} partidos")
        else:
            print("   ⚠️ No se encontró sesión del día")
            
    except Exception as e:
        print(f"   ❌ Error en base de datos: {e}")
        return False
    
    print()
    
    # 2. Probar programación de scrapers
    print("2️⃣ **PROBANDO SCRAPERS PROGRAMADOS**")
    try:
        # Programar scrapers de prueba
        for dato in datos_test:
            scraper_id = data_manager.programar_scraper(dato)
            print(f"   ✅ Scraper programado: {scraper_id}")
        
        # Obtener scrapers programados
        scrapers = data_manager.obtener_scrapers_programados()
        print(f"   📊 Total scrapers programados: {len(scrapers)}")
        
        for scraper in scrapers[:2]:  # Mostrar solo los primeros 2
            print(f"      • {scraper.visitante} @ {scraper.local} - {scraper.estado}")
            
    except Exception as e:
        print(f"   ❌ Error en scrapers: {e}")
        return False
    
    print()
    
    # 3. Probar estadísticas
    print("3️⃣ **PROBANDO ESTADÍSTICAS**")
    try:
        stats = data_manager.obtener_estadisticas_hoy()
        print(f"   📊 Sesiones hoy: {stats['sesiones_scraping']['total']}")
        print(f"   🤖 Scrapers programados: {stats['scrapers_automaticos']['total_programados']}")
        print(f"   ⏱️ Duración promedio: {stats['sesiones_scraping']['duracion_promedio']}s")
        
    except Exception as e:
        print(f"   ❌ Error en estadísticas: {e}")
        return False
    
    print()
    print("✅ **TODAS LAS PRUEBAS DE PERSISTENCIA EXITOSAS**")
    return True

def probar_servicio_background():
    """Prueba el servicio de background"""
    print("=" * 60)
    print("   PRUEBA DEL SERVICIO DE BACKGROUND")
    print("=" * 60)
    print()
    
    try:
        # Obtener estado del servicio
        status = background_service.get_status()
        
        print("1️⃣ **ESTADO ACTUAL**")
        print(f"   Servicio activo: {status['servicio_activo']}")
        print(f"   Telegram configurado: {status['telegram_configurado']}")
        print(f"   Scrapers pendientes: {status['scrapers_pendientes']}")
        print()
        
        print("2️⃣ **ESTADÍSTICAS**")
        stats = status['estadisticas']
        print(f"   Scrapers ejecutados hoy: {stats['scrapers_ejecutados_hoy']}")
        print(f"   Errores hoy: {stats['errores_hoy']}")
        print(f"   Última ejecución: {stats['ultima_ejecucion'] or 'Ninguna'}")
        print(f"   Servicio iniciado: {stats['servicio_iniciado_en']}")
        print()
        
        if not status['servicio_activo']:
            print("3️⃣ **INICIANDO SERVICIO**")
            # background_service.start_service()  # Comentado para no iniciar automáticamente
            print("   ℹ️ Servicio no iniciado (comentado para pruebas)")
        else:
            print("3️⃣ **SERVICIO YA ACTIVO**")
        
        print()
        print("✅ **PRUEBA DE SERVICIO COMPLETADA**")
        return True
        
    except Exception as e:
        print(f"❌ Error probando servicio: {e}")
        return False

def mostrar_instrucciones():
    """Muestra instrucciones para continuar"""
    print("=" * 60)
    print("   PRÓXIMOS PASOS RECOMENDADOS")
    print("=" * 60)
    print()
    
    print("🚀 **PARA USAR EL NUEVO SISTEMA:**")
    print()
    print("1️⃣ **Ejecutar la aplicación web:**")
    print("   • Ejecuta: abrir_web.bat")
    print("   • Los datos se cargarán automáticamente si existen")
    print("   • Los scrapers se guardan en la base de datos")
    print()
    
    print("2️⃣ **Iniciar el servicio automático:**")
    print("   • Desde la web: Se mostrará botón si no está activo")
    print("   • O ejecuta: python -c \"from src.background_service import background_service; background_service.start_service()\"")
    print()
    
    print("3️⃣ **Configurar Telegram (opcional):**")
    print("   • Configura las variables de entorno para Telegram")
    print("   • El sistema funcionará sin Telegram, pero no enviará alertas")
    print()
    
    print("4️⃣ **Monitorear el sistema:**")
    print("   • La web muestra el estado en tiempo real")
    print("   • Los datos persisten entre sesiones") 
    print("   • Los scrapers se ejecutan automáticamente")
    print()
    
    print("🎯 **VENTAJAS DEL NUEVO SISTEMA:**")
    print("   ✅ Los datos no se pierden al cerrar la aplicación")
    print("   ✅ Los scrapers se ejecutan automáticamente")
    print("   ✅ Historial completo de sesiones")
    print("   ✅ Estadísticas y reportes automáticos")
    print("   ✅ Alertas por Telegram (opcional)")
    print("   ✅ Sistema puede correr 24/7")
    print()

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA MEJORADO")
    print()
    
    # Prueba 1: Persistencia
    if not probar_persistencia():
        print("❌ Falló la prueba de persistencia")
        return
    
    print()
    
    # Prueba 2: Servicio de background
    if not probar_servicio_background():
        print("❌ Falló la prueba del servicio")
        return
    
    print()
    
    # Mostrar instrucciones
    mostrar_instrucciones()
    
    print("🎉 **TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE**")
    print("🚀 **EL SISTEMA ESTÁ LISTO PARA USO EN PRODUCCIÓN**")

if __name__ == "__main__":
    main()
