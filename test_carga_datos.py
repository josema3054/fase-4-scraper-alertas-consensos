"""
Test para verificar que los datos se cargan correctamente sin hacer scraping
"""
from src.database.data_manager import DataManager
import json

def main():
    print("🔍 VERIFICANDO CARGA DE DATOS EXISTENTES")
    print("=" * 50)
    
    # Inicializar manager
    dm = DataManager()
    
    # Obtener sesión de hoy
    sesion_hoy = dm.obtener_sesion_del_dia()
    
    if sesion_hoy:
        print(f"✅ Sesión encontrada:")
        print(f"   📅 Fecha: {sesion_hoy.fecha}")
        print(f"   ⏰ Hora: {sesion_hoy.hora_ejecucion}")
        print(f"   🎯 Partidos: {sesion_hoy.total_partidos}")
        print(f"   📊 Estado: {sesion_hoy.estado}")
        
        if sesion_hoy.datos_raw:
            print(f"\n📈 DATOS DISPONIBLES:")
            print(f"   • Total de partidos: {len(sesion_hoy.datos_raw)}")
            
            # Mostrar algunos ejemplos
            for i, partido in enumerate(sesion_hoy.datos_raw[:3]):
                equipos = partido.get('teams', 'N/A')
                consenso = partido.get('porcentaje_consenso', 'N/A')
                print(f"   {i+1}. {equipos} - {consenso}%")
                
            if len(sesion_hoy.datos_raw) > 3:
                print(f"   ... y {len(sesion_hoy.datos_raw) - 3} partidos más")
                
        print(f"\n✅ Conclusión: El botón 'ACTUALIZAR DATOS' debería cargar estos {sesion_hoy.total_partidos} partidos")
        print("   sin hacer scraping nuevo")
        
    else:
        print("❌ No hay sesión del día actual")
        print("   Se necesita hacer scraping primero")

if __name__ == "__main__":
    main()
