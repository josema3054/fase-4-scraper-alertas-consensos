"""
Test simple de alerta de Telegram
"""
import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_alerta_simple():
    print("🚨 ALERTA DE PRUEBA SIMPLE")
    print("=" * 30)
    
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
        
        # Mensaje simple
        mensaje = """
🚨 ALERTA CONSENSO MLB 🚨

🏟️ Yankees @ Red Sox
⏰ EN 15 MINUTOS

📊 Over 8.5: 78%
👥 24 expertos
🔥 ¡ENTRADA AHORA!
        """
        
        print("📱 Enviando...")
        
        # Usar el método directo
        import asyncio
        result = asyncio.run(notifier.send_message(mensaje))
        
        if result:
            print("✅ ¡ALERTA ENVIADA!")
        else:
            print("❌ Error")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_alerta_simple()
