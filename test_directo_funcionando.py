"""
TEST DIRECTO CON SCRAPER SELENIUM FUNCIONANDO
============================================
Usar el scraper que ya sabemos que funciona y aplicarle filtros después
"""

import sys
import os
import json
from datetime import datetime

# Agregar rutas
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    print("🚀 TEST DIRECTO - SCRAPER + FILTROS")
    print("=" * 60)
    
    try:
        # 1. USAR SCRAPER SELENIUM QUE YA FUNCIONA
        print("📡 PASO 1: Extrayendo datos con Selenium...")
        
        from src.scraper.mlb_selenium_scraper import MLBSeleniumScraper
        
        scraper = MLBSeleniumScraper()
        datos_extraidos = scraper.scrape_mlb_consensus()
        
        print(f"✅ Datos extraídos: {len(datos_extraidos)} consensos")
        
        if not datos_extraidos:
            print("❌ No se obtuvieron datos")
            return
        
        # 2. MOSTRAR DATOS SIN FILTRAR
        print(f"\n📋 DATOS SIN FILTRAR:")
        for i, consenso in enumerate(datos_extraidos[:5]):
            partido = f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}"
            direccion = consenso.get('direccion_consenso', '?')
            porcentaje = consenso.get('porcentaje_consenso', 0)
            expertos = consenso.get('num_experts', 0)
            
            print(f"   {i+1}. {partido} - {direccion} {porcentaje}% ({expertos} expertos)")
        
        # 3. APLICAR FILTROS MANUALMENTE
        print(f"\n🔍 PASO 2: Aplicando filtros...")
        
        # Filtros simples
        umbral_minimo = 70
        expertos_minimos = 15
        
        consensos_filtrados = []
        for consenso in datos_extraidos:
            porcentaje = consenso.get('porcentaje_consenso', 0)
            expertos = consenso.get('num_experts', 0)
            
            # Verificar equipos válidos
            equipo_visitante = consenso.get('equipo_visitante')
            equipo_local = consenso.get('equipo_local')
            
            if (porcentaje >= umbral_minimo and 
                expertos >= expertos_minimos and
                equipo_visitante and equipo_local):
                consensos_filtrados.append(consenso)
        
        print(f"✅ Consensos filtrados: {len(consensos_filtrados)}")
        
        # 4. MOSTRAR RESULTADOS FILTRADOS
        if consensos_filtrados:
            print(f"\n🎯 CONSENSOS QUE CUMPLEN FILTROS:")
            print(f"   (≥{umbral_minimo}%, ≥{expertos_minimos} expertos)")
            
            for i, consenso in enumerate(consensos_filtrados):
                partido = f"{consenso.get('equipo_visitante', '?')} @ {consenso.get('equipo_local', '?')}"
                direccion = consenso.get('direccion_consenso', '?')
                porcentaje = consenso.get('porcentaje_consenso', 0)
                expertos = consenso.get('num_experts', 0)
                hora = consenso.get('hora_juego', 'N/A')
                total_line = consenso.get('total_line', 'N/A')
                
                print(f"\n   {i+1}. 🚨 ALERTA: {partido}")
                print(f"      📊 Consenso: {direccion} {porcentaje}%")
                print(f"      👥 Expertos: {expertos}")
                print(f"      🕐 Hora: {hora}")
                print(f"      📈 Total Line: {total_line}")
        
        else:
            print(f"\n📝 No hay consensos que cumplan los filtros")
            print(f"💡 Intenta filtros más permisivos:")
            
            # Probar filtros más permisivos
            filtros_permisivos = []
            for consenso in datos_extraidos:
                porcentaje = consenso.get('porcentaje_consenso', 0)
                expertos = consenso.get('num_experts', 0)
                
                if porcentaje >= 60 and expertos >= 10:
                    filtros_permisivos.append(consenso)
            
            print(f"   Con umbral 60% y 10 expertos: {len(filtros_permisivos)} consensos")
        
        # 5. GUARDAR RESULTADOS
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'datos_extraidos': datos_extraidos,
            'consensos_filtrados': consensos_filtrados,
            'estadisticas': {
                'total_extraidos': len(datos_extraidos),
                'total_filtrados': len(consensos_filtrados),
                'tasa_aprobacion': len(consensos_filtrados) / len(datos_extraidos) * 100 if datos_extraidos else 0
            },
            'configuracion_filtros': {
                'umbral_minimo': umbral_minimo,
                'expertos_minimos': expertos_minimos
            }
        }
        
        with open('test_directo_resultado.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados: test_directo_resultado.json")
        
        # 6. RESUMEN FINAL
        print(f"\n" + "="*60)
        print(f"🎯 RESUMEN DEL FLUJO SEPARADO:")
        print(f"=" * 60)
        print(f"✅ SCRAPER: Extrajo {len(datos_extraidos)} consensos SIN filtrar")
        print(f"✅ FILTROS: Aprobó {len(consensos_filtrados)} consensos")
        
        if len(consensos_filtrados) > 0:
            print(f"🚨 ALERTAS: {len(consensos_filtrados)} listas para enviar")
            print(f"✅ Sistema funcionando correctamente")
        else:
            print(f"📝 Sin alertas para enviar (normal si no hay consensos fuertes)")
            print(f"✅ Sistema operativo - esperando consensos válidos")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    resultado = main()
    
    if resultado:
        print(f"\n🎉 TEST COMPLETADO EXITOSAMENTE")
        print(f"   Datos extraídos: {resultado['estadisticas']['total_extraidos']}")
        print(f"   Alertas generadas: {resultado['estadisticas']['total_filtrados']}")
        print(f"   Tasa aprobación: {resultado['estadisticas']['tasa_aprobacion']:.1f}%")
    
    input(f"\n⏸️ Presiona Enter para continuar...")
