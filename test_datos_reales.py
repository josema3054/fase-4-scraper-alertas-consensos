"""
PRUEBA CON DATOS REALES DE COVERS.COM
====================================
Usando el scraper Selenium que ya funciona + nuevo sistema de filtros
"""

import sys
import os
import json
from datetime import datetime

# Agregar rutas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 PRUEBA CON DATOS REALES DE COVERS.COM")
    print("=" * 60)
    print("   Flujo: SCRAPER REAL → DATOS REALES → FILTROS → ALERTAS")
    print("=" * 60)
    
    try:
        # PASO 1: EXTRACCIÓN CON SCRAPER REAL
        print("\n📡 PASO 1: Extrayendo datos reales de covers.com...")
        print("   (Esto puede tomar varios minutos)")
        
        from src.scraper.mlb_selenium_scraper import MLBSeleniumScraper
        
        scraper = MLBSeleniumScraper()
        
        # Ejecutar scraping real
        datos_reales = scraper.scrape_mlb_consensus()
        
        print(f"✅ Datos extraídos de covers.com: {len(datos_reales)} consensos")
        
        if not datos_reales:
            print("❌ No se obtuvieron datos de covers.com")
            print("💡 Posibles causas:")
            print("   • No hay partidos MLB para hoy")
            print("   • Problema de conectividad")
            return None
        
        # PASO 2: ANÁLISIS DE DATOS EXTRAÍDOS
        print(f"\n📋 PASO 2: Análisis de datos extraídos...")
        
        # Analizar completitud
        datos_completos = []
        datos_parciales = []
        
        for consenso in datos_reales:
            equipo_visitante = consenso.get('equipo_visitante')
            equipo_local = consenso.get('equipo_local')
            porcentaje = consenso.get('porcentaje_consenso', 0)
            expertos = consenso.get('num_experts', 0)
            
            # Considerar completo si tiene equipos, porcentaje y expertos
            if (equipo_visitante and equipo_local and 
                porcentaje > 0 and expertos > 0):
                datos_completos.append(consenso)
            else:
                datos_parciales.append(consenso)
        
        print(f"   • Datos completos: {len(datos_completos)}")
        print(f"   • Datos parciales: {len(datos_parciales)}")
        
        # Mostrar muestra de datos
        print(f"\n📊 MUESTRA DE DATOS EXTRAÍDOS:")
        for i, consenso in enumerate(datos_reales[:5]):
            partido = f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}"
            direccion = consenso.get('direccion_consenso', '?')
            porcentaje = consenso.get('porcentaje_consenso', 0)
            expertos = consenso.get('num_experts', 0)
            
            print(f"   {i+1}. {partido} - {direccion} {porcentaje}% ({expertos} exp)")
        
        # PASO 3: APLICAR FILTROS
        print(f"\n🔍 PASO 3: Aplicando filtros a datos reales...")
        
        # Configurar filtros
        filtros = {
            'umbral_minimo': 70,
            'expertos_minimos': 15,
            'requerir_equipos': True,
            'requerir_porcentaje': True
        }
        
        print(f"   Filtros configurados:")
        for key, value in filtros.items():
            print(f"      • {key}: {value}")
        
        # Aplicar filtros
        consensos_filtrados = []
        rechazados = []
        
        for consenso in datos_reales:
            # Extraer datos
            equipo_visitante = consenso.get('equipo_visitante')
            equipo_local = consenso.get('equipo_local')
            porcentaje = consenso.get('porcentaje_consenso', 0)
            expertos = consenso.get('num_experts', 0)
            
            # Aplicar filtros
            razones_rechazo = []
            
            if filtros['requerir_equipos'] and (not equipo_visitante or not equipo_local):
                razones_rechazo.append("equipos faltantes")
            
            if filtros['requerir_porcentaje'] and porcentaje <= 0:
                razones_rechazo.append("sin porcentaje")
            
            if porcentaje < filtros['umbral_minimo']:
                razones_rechazo.append(f"porcentaje {porcentaje}% < {filtros['umbral_minimo']}%")
            
            if expertos < filtros['expertos_minimos']:
                razones_rechazo.append(f"expertos {expertos} < {filtros['expertos_minimos']}")
            
            if not razones_rechazo:
                consensos_filtrados.append(consenso)
            else:
                rechazados.append({
                    'consenso': consenso,
                    'razones': razones_rechazo
                })
        
        print(f"✅ Filtros aplicados:")
        print(f"   • Aprobados: {len(consensos_filtrados)}")
        print(f"   • Rechazados: {len(rechazados)}")
        
        # Mostrar algunos rechazos
        if rechazados:
            print(f"\n❌ Ejemplos de rechazos:")
            for i, item in enumerate(rechazados[:3]):
                consenso = item['consenso']
                partido = f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}"
                razones = ', '.join(item['razones'])
                print(f"   {i+1}. {partido} - {razones}")
        
        # PASO 4: GENERAR ALERTAS
        print(f"\n📢 PASO 4: Generando alertas...")
        
        alertas_finales = []
        
        for consenso in consensos_filtrados:
            partido = f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}"
            direccion = consenso.get('direccion_consenso', '?')
            porcentaje = consenso.get('porcentaje_consenso', 0)
            expertos = consenso.get('num_experts', 0)
            hora = consenso.get('hora_juego', 'N/A')
            total_line = consenso.get('total_line', 'N/A')
            
            # Calcular urgencia
            if porcentaje >= 90:
                urgencia = "🔴 CRÍTICA"
            elif porcentaje >= 80:
                urgencia = "🟡 ALTA"
            else:
                urgencia = "🟢 MEDIA"
            
            alerta = {
                'partido': partido,
                'consenso': f"{direccion} {porcentaje}%",
                'expertos': expertos,
                'hora': hora,
                'total_line': total_line,
                'urgencia': urgencia,
                'timestamp': datetime.now().isoformat()
            }
            
            alertas_finales.append(alerta)
        
        print(f"✅ {len(alertas_finales)} alertas generadas")
        
        # PASO 5: MOSTRAR ALERTAS FINALES
        if alertas_finales:
            print(f"\n🚨 ALERTAS REALES PARA ENVIAR:")
            print("=" * 60)
            
            for i, alerta in enumerate(alertas_finales, 1):
                print(f"\n{i}. {alerta['urgencia']} {alerta['partido']}")
                print(f"   📊 Consenso: {alerta['consenso']}")
                print(f"   👥 Expertos: {alerta['expertos']}")
                print(f"   🕐 Hora: {alerta['hora']}")
                print(f"   📈 Total Line: {alerta['total_line']}")
        else:
            print(f"\n📝 No hay alertas para enviar con los filtros actuales")
            print(f"💡 Intentando con filtros más permisivos...")
            
            # Probar filtros más permisivos
            filtros_permisivos = []
            for consenso in datos_reales:
                porcentaje = consenso.get('porcentaje_consenso', 0)
                expertos = consenso.get('num_experts', 0)
                equipo_visitante = consenso.get('equipo_visitante')
                equipo_local = consenso.get('equipo_local')
                
                if (porcentaje >= 60 and expertos >= 10 and 
                    equipo_visitante and equipo_local):
                    filtros_permisivos.append(consenso)
            
            print(f"   Con filtros permisivos (≥60%, ≥10 exp): {len(filtros_permisivos)} consensos")
        
        # PASO 6: GUARDAR RESULTADOS
        resultado_completo = {
            'timestamp': datetime.now().isoformat(),
            'datos_extraidos': datos_reales,
            'consensos_filtrados': consensos_filtrados,
            'alertas_generadas': alertas_finales,
            'estadisticas': {
                'total_extraidos': len(datos_reales),
                'datos_completos': len(datos_completos),
                'datos_parciales': len(datos_parciales),
                'consensos_filtrados': len(consensos_filtrados),
                'alertas_generadas': len(alertas_finales),
                'tasa_aprobacion': len(consensos_filtrados) / len(datos_reales) * 100 if datos_reales else 0,
                'tasa_alertas': len(alertas_finales) / len(datos_reales) * 100 if datos_reales else 0
            },
            'configuracion_filtros': filtros
        }
        
        with open('resultado_datos_reales.json', 'w', encoding='utf-8') as f:
            json.dump(resultado_completo, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Resultados guardados: resultado_datos_reales.json")
        
        # PASO 7: RESUMEN FINAL
        print(f"\n" + "="*60)
        print(f"🎯 RESUMEN FINAL - DATOS REALES")
        print(f"=" * 60)
        
        stats = resultado_completo['estadisticas']
        
        print(f"📡 SCRAPER: {stats['total_extraidos']} consensos extraídos de covers.com")
        print(f"   • Completos: {stats['datos_completos']}")
        print(f"   • Parciales: {stats['datos_parciales']}")
        
        print(f"\n🔍 FILTROS: {stats['consensos_filtrados']} consensos aprobados")
        print(f"   • Tasa aprobación: {stats['tasa_aprobacion']:.1f}%")
        
        print(f"\n📢 ALERTAS: {stats['alertas_generadas']} alertas generadas")
        print(f"   • Tasa alertas: {stats['tasa_alertas']:.1f}%")
        
        if stats['alertas_generadas'] > 0:
            print(f"\n🚨 SISTEMA OPERATIVO - LISTO PARA ENVIAR ALERTAS REALES")
            print(f"   ✅ {stats['alertas_generadas']} alertas esperando envío")
        else:
            print(f"\n📝 Sistema funcionando - No hay consensos que cumplan criterios hoy")
            print(f"   ✅ Scraper extrae datos correctamente")
            print(f"   ✅ Filtros funcionan correctamente")
        
        print(f"\n🔄 PRÓXIMOS PASOS:")
        print(f"   1. ✅ Scraper extrae datos reales de covers.com")
        print(f"   2. ✅ Sistema de filtros funciona")
        print(f"   3. ✅ Generación de alertas operativa")
        print(f"   4. 🔄 Integrar con Telegram (módulo separado)")
        print(f"   5. 📅 Automatizar con scheduler diario")
        
        return resultado_completo
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    resultado = main()
    
    if resultado:
        stats = resultado['estadisticas']
        print(f"\n🎉 PRUEBA CON DATOS REALES COMPLETADA")
        print(f"   📊 Extraídos: {stats['total_extraidos']}")
        print(f"   🔍 Filtrados: {stats['consensos_filtrados']}")
        print(f"   📢 Alertas: {stats['alertas_generadas']}")
        
        if stats['alertas_generadas'] > 0:
            print(f"   🚨 ¡SISTEMA LISTO PARA ALERTAS REALES!")
        else:
            print(f"   📝 Sistema operativo - esperando consensos válidos")
    else:
        print(f"\n❌ Prueba fallida - revisar configuración")
    
    input(f"\n⏸️ Presiona Enter para continuar...")
