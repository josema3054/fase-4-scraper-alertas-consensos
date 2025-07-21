import requests
from datetime import datetime

# URL con fecha actual
today = datetime.now().strftime('%Y-%m-%d')
url = f"https://contests.covers.com/consensus/topoverunderconsensus/all/expert/{today}"

print(f"Fecha hoy: {today}")
print(f"URL a probar: {url}")
print()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    print("Conectando...")
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Código de respuesta: {response.status_code}")
    print(f"Tamaño de respuesta: {len(response.text)} caracteres")
    
    if response.status_code == 200:
        print("✅ ¡CONEXIÓN EXITOSA!")
        
        # Buscar indicadores de consenso
        content = response.text.lower()
        indicators = {
            'over': content.count('over'),
            'under': content.count('under'),
            'consensus': content.count('consensus'),
            'total': content.count('total'),
            '%': content.count('%')
        }
        
        print("\n📊 Indicadores encontrados:")
        for key, count in indicators.items():
            print(f"   {key}: {count} veces")
        
    else:
        print(f"❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")

input("\nPresiona Enter para continuar...")
