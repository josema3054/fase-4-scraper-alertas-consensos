"""
Test de alerta de prueba para partido próximo
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def enviar_alerta_prueba():
    print("🚨 ENVIANDO ALERTA DE PRUEBA")
    print("=" * 40)
    
    try:
        # Cargar configuración
        from config.settings import Settings
        settings = Settings()
        
        # Inicializar notificador
        from src.notifications.telegram_bot import TelegramNotifier
        notifier = TelegramNotifier(
            token=settings.TELEGRAM_BOT_TOKEN,
            chat_ids=[settings.TELEGRAM_CHAT_ID]
        )
        
        # Simular datos de partido próximo
        partido_ejemplo = {
            "visitante": "New York Yankees",
            "local": "Boston Red Sox", 
            "hora_partido": "18:00",
            "fecha_partido": "2025-07-22",
            "porcentaje_consenso": 78,
            "tipo_apuesta": "Over 8.5",
            "num_experts": 24,
            "minutos_restantes": 15
        }
        
        # Crear mensaje de alerta
        mensaje_alerta = f"""
🚨 **ALERTA DE CONSENSO MLB** 🚨

⏰ **PARTIDO EN {partido_ejemplo['minutos_restantes']} MINUTOS**
🏟️ {partido_ejemplo['visitante']} @ {partido_ejemplo['local']}
🕐 Hora: {partido_ejemplo['hora_partido']} 

📊 **CONSENSO DETECTADO:**
🎯 {partido_ejemplo['tipo_apuesta']}: **{partido_ejemplo['porcentaje_consenso']}%**
👥 Expertos: {partido_ejemplo['num_experts']}
🔥 Umbral: {settings.MLB_CONSENSUS_THRESHOLD}% (SUPERADO)

⚡ **ACCIÓN RECOMENDADA:**
✅ Revisar líneas en tu sportsbook
✅ Considerar entrada: {partido_ejemplo['tipo_apuesta']}
⏱️ Tiempo restante: {partido_ejemplo['minutos_restantes']} minutos

🤖 Alerta automática del sistema
        """
        
        print("📱 Enviando alerta...")
        print(f"📊 Consenso: {partido_ejemplo['porcentaje_consenso']}%")
        print(f"🏟️ Partido: {partido_ejemplo['visitante']} vs {partido_ejemplo['local']}")
        
        # Enviar mensaje
        resultado = await notifier.send_message(mensaje_alerta)
        
        if resultado:
            print("✅ ¡Alerta enviada exitosamente!")
            print("📱 Revisa tu Telegram")
            
            # Simular alerta de seguimiento
            print("\n⏳ Enviando alerta de seguimiento...")
            await asyncio.sleep(2)
            
            mensaje_seguimiento = f"""
📈 **ACTUALIZACIÓN DE CONSENSO**

🏟️ {partido_ejemplo['visitante']} @ {partido_ejemplo['local']}
⏰ Quedan {partido_ejemplo['minutos_restantes'] - 2} minutos

🔄 **Consenso actualizado:** {partido_ejemplo['porcentaje_consenso'] + 2}%
📈 Tendencia: ⬆️ SUBIENDO
⚡ **¡ENTRADA RECOMENDADA YA!**

🎯 {partido_ejemplo['tipo_apuesta']}
            """
            
            await notifier.send_message(mensaje_seguimiento)
            print("✅ Alerta de seguimiento enviada")
            
        else:
            print("❌ Error enviando alerta")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_alerta():
    """Wrapper para ejecutar la función async"""
    asyncio.run(enviar_alerta_prueba())

if __name__ == "__main__":
    test_alerta()
