
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_telegram_message(message: str):
    """
    Send a message to the configured Telegram group, either directly or via Vercel relay.
    
    Args:
        message (str): The message content to send.
    """
    # 1. Try Vercel Relay
    relay_url = os.getenv("VERCEL_RELAY_URL")
    relay_secret = os.getenv("RELAY_SECRET")
    
    if relay_url:
        try:
            headers = {"Content-Type": "application/json"}
            if relay_secret:
                headers["X-Relay-Secret"] = relay_secret
                
            response = requests.post(
                relay_url, 
                json={"message": message}, 
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            # print("[Telegram Relay] ✅ Notification sent successfully")
            return
        except Exception as e:
            print(f"[Telegram Relay] ⚠️ Failed to send via relay (falling back to direct): {e}")
            # Fall through to direct method if relay fails
            pass

    # 2. Direct Telegram API (Fallback or Primary)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        if not relay_url:
            print("[Telegram] ⚠️  Credentials not found and no relay configured. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        # print("[Telegram] ✅ Notification sent successfully")
    except Exception as e:
        print(f"[Telegram] ❌ Failed to send notification: {e}")

def format_trade_message(trade_data: dict, event_type: str) -> str:
    """
    Format a trade event into a readable message.
    
    Args:
        trade_data (dict): Dictionary containing trade details.
        event_type (str): 'OPEN' or 'CLOSE'
        
    Returns:
        str: Formatted message string.
    """
    symbol = trade_data.get('symbol', 'UNKNOWN')
    direction = trade_data.get('direction', 'UNKNOWN')
    
    if event_type == "OPEN":
        emoji = "🟢" if direction == "BUY" else "🔴"
        return (
            f"{emoji} <b>NEW TRADE OPENED</b>\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction}\n"
            f"<b>Entry:</b> {trade_data.get('entry_price')}\n"
            f"<b>Stop Loss:</b> {trade_data.get('stop_loss')}\n"
            f"<b>Target:</b> {trade_data.get('target_price')}\n"
            f"<b>Size:</b> {trade_data.get('lot_size')} lots\n"
            f"<b>Score:</b> {trade_data.get('score', 0)}\n\n" 
            f"<i>Time to make some pips!</i> 🚀"
        )
    elif event_type == "CLOSE":
        pnl = trade_data.get('pnl', 0.0)
        pnl_emoji = "💰" if pnl >= 0 else "🔻"
        outcome = "PROFIT" if pnl >= 0 else "LOSS"
        return (
            f"{pnl_emoji} <b>TRADE CLOSED ({outcome})</b>\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction}\n"
            f"<b>Entry:</b> {trade_data.get('entry_price')}\n"
            f"<b>Exit:</b> {trade_data.get('exit_price')}\n"
            f"<b>P&L:</b> ${pnl:.2f}\n"
            f"<b>Reason:</b> {trade_data.get('status', 'MANUAL')}\n\n"
            f"<i>Balance updated.</i> 📊"
        )
    return ""
