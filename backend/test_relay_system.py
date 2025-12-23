
import os
import sys
import time
from dotenv import load_dotenv
from bot.telegram_notifier import send_telegram_message

# Load environment variables
load_dotenv()

def test_system():
    print("🔍 Testing Telegram Notification System...")
    print("-" * 50)
    
    # 1. Check Configuration
    relay_url = os.getenv("VERCEL_RELAY_URL")
    relay_secret = os.getenv("RELAY_SECRET")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print(f"Configurations found:")
    print(f"  • VERCEL_RELAY_URL: {'✅ Configured (' + relay_url + ')' if relay_url else '❌ Not Set'}")
    print(f"  • RELAY_SECRET:     {'✅ Configured' if relay_secret else '⚠️  Not Set (Optional)'}")
    print(f"  • TELEGRAM_TOKEN:   {'✅ Configured' if bot_token else '❌ Not Set'}")
    print(f"  • CHAT_ID:          {'✅ Configured' if chat_id else '❌ Not Set'}")
    print("-" * 50)
    
    if not relay_url and not bot_token:
        print("❌ Error: No notification method configured.")
        print("   Please set VERCEL_RELAY_URL in backend/.env to test the relay.")
        return

    # 2. Send Test Message
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    test_message = (
        f"🧪 <b>TEST NOTIFICATION</b>\n\n"
        f"Verifying system functionality at {timestamp}.\n"
        f"Mode: {'Relay' if relay_url else 'Direct'}\n\n"
        f"<i>If you see this, the system is working!</i> 🚀"
    )

    print(f"\n📨 Attempting to send message via {'Relay' if relay_url else 'Direct API'}...")
    send_telegram_message(test_message)
    print("\n✅ Check your Telegram group for the message.")

if __name__ == "__main__":
    test_system()
