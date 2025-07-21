"""
PRUEBA COMPLETA DEL SISTEMA SEPARADO
===================================
Prueba el nuevo flujo: Scraper Puro → Filtros → Alertas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.coordinador_scraping import CoordinadorScraping
import json
from datetime import datetime

def main():
    print("🚀 PRUEBA COMPLETA DEL SISTEMA SEPARADO")
    print("=" * 70)
    print("   Flujo: SCRAPER PURO → DATOS → FILTROS → ALERTAS")
    print("=" * 70)
    
    try:
        # 1. INICIALIZAR COORDINADOR
        print("\n📋 1. INICIALIZANDO COORDINADOR...")
        coordinador = CoordinadorScraping()
        
        # 2. MOSTRAR CONFIGURACIÓN
        print("\n⚙️ 2. CONFIGURACIÓN DEL SISTEMA:")
        config = coordinador.obtener_resumen_configuracion()
        
        print(f"   🕷️ SCRAPER:")
        print(f"      • Tipo: {config['scraper']['tipo']}")
        print(f"      • Estrategia: Extrae TODO sin filtrar")
        
        print(f"\n   🔍 FILTROS:")
        filtros_consenso = config['filtros']['filtros_consenso']
        for key, value in filtros_consenso.items():
            print(f"      • {key}: {value}")
        
        print(f"\n   📁 HISTORIAL:")
        print(f"      • Archivo: {config['historial']['archivo']}")
        print(f"      • Alertas hoy: {config['historial']['alertas_hoy']}")
        
        # 3. CONFIGURAR FILTROS DE PRUEBA (MÁS PERMISIVOS)
        print("\n🔧 3. CONFIGURANDO FILTROS DE PRUEBA...")
        coordinador.configurar_filtros(
            umbral_minimo=60,  # Más permisivo
            umbral_maximo=95,
            expertos_minimos=8,  # Menos expertos requeridos
            picks_minimos=5,
            completitud_minima="1/3"  # Mínimo muy bajo
        )
        print("   ✅ Filtros configurados (permisivos para testing)")
        
        # 4. EJECUTAR SCRAPING COMPLETO
        print("\n🎯 4. EJECUTANDO SCRAPING COMPLETO...")
        print("   Esto puede tomar varios minutos...")
        
        resultado = coordinador.ejecutar_scraping_completo()
        
        # 5. MOSTRAR RESULTADOS DETALLADOS
        print("\n" + "="*70)
        print("📊 RESULTADOS DETALLADOS")
        print("="*70)
        
        if resultado['exito']:
            print(f"✅ ÉXITO - {resultado['fecha_procesada']}")
            print(f"🕐 {resultado['timestamp']}")
            
            print(f"\n📡 DATOS EXTRAÍDOS:")
            print(f"   • Total consensos: {resultado['datos_extraidos']}")
            print(f"   • Completos (3/3): {resultado['datos_completos']}")
            print(f"   • Parciales: {resultado['datos_parciales']}")
            
            if resultado['datos_extraidos'] > 0:
                porcentaje_completos = (resultado['datos_completos'] / resultado['datos_extraidos']) * 100
                print(f"   • Completitud: {porcentaje_completos:.1f}%")
            
            print(f"\n🔍 FILTROS APLICADOS:")
            print(f"   • Consensos filtrados: {resultado['consensos_filtrados']}")
            
            filtros_stats = resultado['filtros_aplicados']
            if filtros_stats['total_inicial'] > 0:
                porcentaje_aprobados = (filtros_stats['filtrados'] / filtros_stats['total_inicial']) * 100
                print(f"   • Tasa aprobación: {porcentaje_aprobados:.1f}%")
            
            # Mostrar rechazos
            rechazos = filtros_stats['rechazados_por']
            rechazos_totales = sum(rechazos.values())
            if rechazos_totales > 0:
                print(f"   • Total rechazados: {rechazos_totales}")
                print(f"   • Principales razones:")
                for razon, cantidad in rechazos.items():
                    if cantidad > 0:
                        print(f"     - {razon}: {cantidad}")
            
            print(f"\n📢 ALERTAS:")
            print(f"   • Alertas nuevas: {resultado['alertas_nuevas']}")
            print(f"   • Alertas enviadas: {resultado['alertas_enviadas']}")
            
            if resultado['alertas_nuevas'] > 0:
                print(f"   🎉 ¡SE GENERARON {resultado['alertas_nuevas']} ALERTAS NUEVAS!")
            else:
                print(f"   ℹ️  No hay alertas nuevas (ya enviadas o sin datos)")
            
            print(f"\n⏱️ PERFORMANCE:")
            print(f"   • Tiempo total: {resultado['tiempo_total']} segundos")
            print(f"   • Velocidad: {resultado['consensos_por_segundo']} consensos/seg")
            
        else:
            print(f"❌ ERROR: {resultado['error']}")
            
        # 6. ESTADÍSTICAS HISTÓRICAS
        print(f"\n📈 6. ESTADÍSTICAS HISTÓRICAS:")
        stats = coordinador.obtener_estadisticas_historicas(dias=3)
        print(f"   • Período: últimos {stats['periodo_dias']} días")
        print(f"   • Total alertas: {stats['total_alertas']}")
        print(f"   • Promedio diario: {stats['promedio_diario']}")
        print(f"   • Días con alertas: {stats['fechas_con_alertas']}")
        
        # 7. VERIFICAR ARCHIVOS GENERADOS
        print(f"\n📁 7. ARCHIVOS GENERADOS:")
        archivos_verificar = [
            "data/historial_alertas.json",
            "config/filtros_consenso.json",
            "datos_puros_scraper.json"
        ]
        
        for archivo in archivos_verificar:
            if os.path.exists(archivo):
                size = os.path.getsize(archivo)
                print(f"   ✅ {archivo} ({size} bytes)")
                
                # Mostrar muestra del contenido
                if archivo.endswith('.json'):
                    try:
                        with open(archivo, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if isinstance(data, list):
                            print(f"      📊 {len(data)} elementos")
                        elif isinstance(data, dict):
                            print(f"      📊 {len(data)} claves")
                    except:
                        pass
            else:
                print(f"   ❌ {archivo} (no existe)")
        
        # 8. GUARDAR RESULTADO COMPLETO
        with open('resultado_sistema_completo.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Resultado completo guardado: resultado_sistema_completo.json")
        
        # 9. RESUMEN FINAL
        print(f"\n" + "="*70)
        print("🎯 RESUMEN FINAL")
        print("="*70)
        
        if resultado['exito']:
            print(f"✅ Sistema funcionando correctamente")
            print(f"📡 Scraper: Extrajo {resultado['datos_extraidos']} consensos")
            print(f"🔍 Filtros: Aprobó {resultado['consensos_filtrados']} consensos")
            print(f"📢 Alertas: Generó {resultado['alertas_nuevas']} alertas nuevas")
            
            if resultado['alertas_nuevas'] > 0:
                print(f"\n🚨 SISTEMA LISTO PARA ENVIAR ALERTAS")
            else:
                print(f"\n🔄 Sistema operativo - esperando nuevos consensos")
                
        else:
            print(f"❌ Sistema requiere ajustes")
            print(f"💡 Revisar configuración y conectividad")
        
        print(f"\n📝 Próximos pasos:")
        print(f"   1. Revisar archivos JSON generados")
        print(f"   2. Ajustar filtros según necesidades")
        print(f"   3. Integrar con sistema de alertas")
        print(f"   4. Automatizar con scheduler")
        
        return resultado
        
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_con_reintentos():
    """Prueba con sistema de reintentos"""
    print("\n" + "="*50)
    print("🔄 PRUEBA CON REINTENTOS")
    print("="*50)
    
    coordinador = CoordinadorScraping()
    
    # Configurar filtros aún más permisivos
    coordinador.configurar_filtros(
        umbral_minimo=50,
        expertos_minimos=5,
        completitud_minima="1/3"
    )
    
    print("⚙️ Configurado para máxima permisividad")
    print("🔄 Ejecutando con hasta 2 reintentos...")
    
    resultado = coordinador.ejecutar_con_reintentos(max_intentos=2, delay_minutos=1)
    
    print(f"\n📊 RESULTADO CON REINTENTOS:")
    for key, value in resultado.items():
        print(f"   {key}: {value}")
    
    return resultado

if __name__ == "__main__":
    # Prueba principal
    resultado_principal = main()
    
    if resultado_principal and not resultado_principal.get('exito', False):
        print(f"\n🤔 ¿QUIERES PROBAR CON REINTENTOS?")
        print("   (Para casos donde el primer intento falla)")
        
        respuesta = input("   Presiona 'r' y Enter para reintentos, o solo Enter para salir: ")
        
        if respuesta.lower().strip() == 'r':
            test_con_reintentos()
    
    input(f"\n⏸️ Presiona Enter para salir...")
