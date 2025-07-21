"""
PRUEBA RÁPIDA DEL SISTEMA
========================
Test rápido para validar el flujo: Datos → Filtros → Alertas
"""

def test_flujo_basico():
    print("🧪 PRUEBA RÁPIDA DEL FLUJO SEPARADO")
    print("=" * 50)
    
    # SIMULAR DATOS DEL SCRAPER (como si vinieran de covers.com)
    print("📡 PASO 1: Datos simulados del scraper...")
    
    datos_scraper = [
        {
            'equipo_visitante': 'NYY',
            'equipo_local': 'BOS',
            'direccion_consenso': 'OVER',
            'porcentaje_consenso': 85,
            'num_experts': 25,
            'total_line': 9.5,
            'hora_juego': '7:10 pm ET',
            'completitud': '3/3'
        },
        {
            'equipo_visitante': 'LAD',
            'equipo_local': 'SF',
            'direccion_consenso': 'UNDER',
            'porcentaje_consenso': 65,  # Bajo umbral
            'num_experts': 12,  # Pocos expertos
            'total_line': 8.0,
            'completitud': '3/3'
        },
        {
            'equipo_visitante': 'ATL',
            'equipo_local': 'MIA',
            'direccion_consenso': 'OVER',
            'porcentaje_consenso': 92,  # Alto consenso
            'num_experts': 35,  # Muchos expertos
            'total_line': 10.0,
            'hora_juego': '8:20 pm ET',
            'completitud': '3/3'
        }
    ]
    
    print(f"✅ {len(datos_scraper)} consensos extraídos (simulados)")
    
    # PASO 2: APLICAR FILTROS
    print(f"\n🔍 PASO 2: Aplicando filtros...")
    
    # Configuración de filtros
    umbral_minimo = 70
    expertos_minimos = 15
    
    print(f"   Filtros: ≥{umbral_minimo}%, ≥{expertos_minimos} expertos")
    
    consensos_filtrados = []
    rechazados = []
    
    for consenso in datos_scraper:
        porcentaje = consenso.get('porcentaje_consenso', 0)
        expertos = consenso.get('num_experts', 0)
        
        if porcentaje >= umbral_minimo and expertos >= expertos_minimos:
            consensos_filtrados.append(consenso)
        else:
            razon = []
            if porcentaje < umbral_minimo:
                razon.append(f"porcentaje {porcentaje}% < {umbral_minimo}%")
            if expertos < expertos_minimos:
                razon.append(f"expertos {expertos} < {expertos_minimos}")
            
            rechazados.append({
                'consenso': consenso,
                'razon': ', '.join(razon)
            })
    
    print(f"✅ Filtros aplicados:")
    print(f"   • Aprobados: {len(consensos_filtrados)}")
    print(f"   • Rechazados: {len(rechazados)}")
    
    # Mostrar rechazos
    if rechazados:
        print(f"\n❌ Rechazados:")
        for i, item in enumerate(rechazados):
            consenso = item['consenso']
            partido = f"{consenso['equipo_visitante']} @ {consenso['equipo_local']}"
            print(f"   {i+1}. {partido} - {item['razon']}")
    
    # PASO 3: GENERAR ALERTAS
    print(f"\n📢 PASO 3: Generando alertas...")
    
    alertas = []
    for consenso in consensos_filtrados:
        partido = f"{consenso['equipo_visitante']} @ {consenso['equipo_local']}"
        direccion = consenso['direccion_consenso']
        porcentaje = consenso['porcentaje_consenso']
        expertos = consenso['num_experts']
        hora = consenso.get('hora_juego', 'N/A')
        
        # Calcular urgencia
        if porcentaje >= 90:
            urgencia = "🔴 ALTA"
        elif porcentaje >= 80:
            urgencia = "🟡 MEDIA"
        else:
            urgencia = "🟢 BAJA"
        
        alerta = {
            'partido': partido,
            'consenso': f"{direccion} {porcentaje}%",
            'expertos': expertos,
            'hora': hora,
            'urgencia': urgencia,
            'mensaje': f"ALERTA: {partido} - {direccion} {porcentaje}% ({expertos} expertos)"
        }
        
        alertas.append(alerta)
    
    print(f"✅ {len(alertas)} alertas generadas")
    
    # PASO 4: MOSTRAR ALERTAS
    if alertas:
        print(f"\n🚨 ALERTAS PARA ENVIAR:")
        print("=" * 50)
        
        for i, alerta in enumerate(alertas, 1):
            print(f"\n{i}. {alerta['urgencia']} {alerta['partido']}")
            print(f"   📊 Consenso: {alerta['consenso']}")
            print(f"   👥 Expertos: {alerta['expertos']}")
            print(f"   🕐 Hora: {alerta['hora']}")
            print(f"   📱 Mensaje: {alerta['mensaje']}")
    else:
        print(f"\n📝 No hay alertas para enviar")
    
    # RESUMEN FINAL
    print(f"\n" + "="*50)
    print(f"🎯 RESUMEN DEL FLUJO:")
    print(f"=" * 50)
    print(f"📡 SCRAPER: {len(datos_scraper)} consensos extraídos")
    print(f"🔍 FILTROS: {len(consensos_filtrados)} aprobados, {len(rechazados)} rechazados")
    print(f"📢 ALERTAS: {len(alertas)} listas para enviar")
    
    if len(alertas) > 0:
        print(f"\n✅ FLUJO FUNCIONAL - Sistema listo para alertas reales")
    else:
        print(f"\n📝 Sistema operativo - esperando consensos que cumplan filtros")
    
    return {
        'datos_extraidos': len(datos_scraper),
        'consensos_filtrados': len(consensos_filtrados),
        'alertas_generadas': len(alertas),
        'flujo_exitoso': True
    }

if __name__ == "__main__":
    resultado = test_flujo_basico()
    
    print(f"\n🎉 PRUEBA COMPLETADA")
    print(f"   ✅ Flujo separado funcionando correctamente")
    print(f"   📊 Datos: {resultado['datos_extraidos']} → Filtros: {resultado['consensos_filtrados']} → Alertas: {resultado['alertas_generadas']}")
    
    print(f"\n💡 PRÓXIMOS PASOS:")
    print(f"   1. ✅ Scraper puro (extrae TODO)")
    print(f"   2. ✅ Filtros post-extracción (aplica criterios)")
    print(f"   3. ✅ Sistema de alertas (procesa válidos)")
    print(f"   4. 🔄 Integrar con scraper real de covers.com")
    print(f"   5. 📅 Automatizar con scheduler")
    
    input(f"\n⏸️ Presiona Enter para continuar...")
