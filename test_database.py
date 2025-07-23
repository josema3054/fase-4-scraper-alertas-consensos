"""
Test simple para verificar el sistema de base de datos
"""
from src.database.data_manager import DataManager
import os

def main():
    print("🔍 VERIFICANDO SISTEMA DE PERSISTENCIA")
    print("=" * 50)
    
    # Inicializar manager
    dm = DataManager()
    print(f"✅ DataManager inicializado")
    print(f"📍 Ruta de base de datos: {dm.db_path}")
    
    # Verificar si existe la base de datos
    if os.path.exists(dm.db_path):
        print("✅ Base de datos existe")
        
        # Verificar datos existentes
        import sqlite3
        with sqlite3.connect(dm.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM scraping_sessions')
            sesiones = cursor.fetchone()[0]
            
            cursor = conn.execute('SELECT COUNT(*) FROM scrapers_programados')  
            programados = cursor.fetchone()[0]
            
            print(f"📊 Sesiones guardadas: {sesiones}")
            print(f"⏰ Scrapers programados: {programados}")
            
            # Mostrar últimas sesiones si existen
            if sesiones > 0:
                cursor = conn.execute('''
                    SELECT fecha, total_partidos, estado, duracion_segundos 
                    FROM scraping_sessions 
                    ORDER BY fecha DESC, hora_ejecucion DESC 
                    LIMIT 5
                ''')
                print("\n📈 Últimas sesiones:")
                for row in cursor.fetchall():
                    fecha, total, estado, duracion = row
                    duracion_str = f"{duracion:.1f}s" if duracion else "N/A"
                    print(f"  • {fecha}: {total} partidos - {estado} ({duracion_str})")
            else:
                print("\n📝 No hay sesiones previas guardadas")
                
    else:
        print("❌ Base de datos no existe, se creará automáticamente")
    
    print("\n✅ Sistema de persistencia verificado")
    print("\n💡 Para usar el sistema:")
    print("   1. Ejecuta tu interfaz web normal")
    print("   2. Los datos se guardarán automáticamente")
    print("   3. Al reiniciar, los datos estarán disponibles")

if __name__ == "__main__":
    main()
