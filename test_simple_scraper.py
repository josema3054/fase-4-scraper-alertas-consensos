"""
TEST SIMPLE DEL SCRAPER PURO
============================
Test básico para verificar que funciona la extracción
"""

import sys
import os

# Agregar rutas
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')

sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

print("🧪 TEST SIMPLE DEL SCRAPER PURO")
print("=" * 50)

try:
    # Importar scraper
    print("📦 Importando scraper...")
    from src.scraper.mlb_scraper_puro import MLBScraperPuro
    print("✅ Scraper importado correctamente")
    
    # Crear instancia
    print("🔧 Creando instancia...")
    scraper = MLBScraperPuro()
    print("✅ Instancia creada")
    
    # Ejecutar extracción
    print("🚀 Ejecutando extracción de datos...")
    print("   (Esto puede tomar varios minutos)")
    
    consensos = scraper.extraer_todos_los_consensos()
    
    print(f"\n📊 RESULTADO:")
    print(f"   Consensos extraídos: {len(consensos)}")
    
    if consensos:
        print(f"\n📋 PRIMEROS CONSENSOS:")
        for i, consenso in enumerate(consensos[:3]):
            partido = consenso.get('partido_completo', 'N/A')
            completitud = consenso.get('completitud', '?/?')
            porcentaje = consenso.get('porcentaje_consenso', 0)
            direccion = consenso.get('direccion_consenso', '?')
            
            print(f"   {i+1}. [{completitud}] {partido}")
            print(f"      {direccion} {porcentaje}%")
        
        # Estadísticas
        completos = [c for c in consensos if c.get('completitud') == '3/3']
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   Total: {len(consensos)}")
        print(f"   Completos (3/3): {len(completos)}")
        print(f"   Parciales: {len(consensos) - len(completos)}")
        
        # Guardar datos
        import json
        with open('test_simple_resultado.json', 'w', encoding='utf-8') as f:
            json.dump(consensos, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Datos guardados: test_simple_resultado.json")
        
        print(f"\n✅ TEST EXITOSO")
        
    else:
        print(f"\n❌ No se extrajeron consensos")
        print("💡 Posibles causas:")
        print("   - No hay partidos MLB para hoy")
        print("   - Problema de conectividad")
        print("   - Cambio en la estructura de la página")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print(f"💡 Verifica que los archivos estén en la ubicación correcta")

except Exception as e:
    print(f"❌ Error durante la ejecución: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎯 Test completado")
input("Presiona Enter para continuar...")
