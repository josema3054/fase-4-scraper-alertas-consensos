"""
Test del bot de Telegram
"""
import os
import sys

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_telegram_bot():
    print("🤖 PROBANDO BOT DE TELEGRAM")
    print("=" * 40)
    
    try:
        # Cargar configuración
        from config.settings import Settings
        settings = Settings()
        
        print(f"✅ Token configurado: {settings.TELEGRAM_BOT_TOKEN[:20]}...")
        print(f"✅ Chat ID: {settings.TELEGRAM_CHAT_ID}")
        
        # Probar el bot
        from src.notifications.telegram_bot import TelegramNotifier
        notifier = TelegramNotifier(
            token=settings.TELEGRAM_BOT_TOKEN,
            chat_ids=[settings.TELEGRAM_CHAT_ID]
        )
        
        print("📱 Enviando mensaje de prueba...")
        
        message = """
🎯 **PRUEBA DEL BOT DE CONSENSOS MLB**

✅ El bot está funcionando correctamente
🤖 Sistema configurado y listo
📊 Recibirás alertas cuando:
   • Hay partidos próximos (15 min antes)
   • Se encuentran consensos altos
   • Hay errores en el sistema

¡Sistema de alertas activo! 🚀
        """
        
        result = notifier.send_message(message)
        
        if result:
            print("✅ ¡Mensaje enviado exitosamente!")
            print("📱 Revisa tu Telegram - deberías haber recibido un mensaje")
        else:
            print("❌ Error enviando mensaje")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_telegram_bot()
