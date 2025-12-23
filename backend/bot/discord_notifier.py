import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_discord_message(message: str):
    """
    Send a message to the configured Discord channel via webhook.
    
    Args:
        message (str): The message content to send.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("[Discord] ⚠️  Webhook URL not found. Skipping notification.")
        return

    payload = {
        "content": message
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        # print("[Discord] ✅ Notification sent successfully")
    except Exception as e:
        print(f"[Discord] ❌ Failed to send notification: {e}")

def format_trade_message(trade_data: dict, event_type: str) -> str:
    """
    Format a trade event into a readable Discord message.
    
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
            f"{emoji} **NEW TRADE OPENED**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**Direction:** {direction}\n"
            f"**Entry:** {trade_data.get('entry_price')}\n"
            f"**Stop Loss:** {trade_data.get('stop_loss')}\n"
            f"**Target:** {trade_data.get('target_price')}\n"
            f"**Size:** {trade_data.get('lot_size')} lots\n"
            f"**Score:** {trade_data.get('score', 0)}\n\n" 
            f"*Time to make some pips!* 🚀"
        )
    elif event_type == "CLOSE":
        pnl = trade_data.get('pnl', 0.0)
        pnl_emoji = "💰" if pnl >= 0 else "🔻"
        outcome = "PROFIT" if pnl >= 0 else "LOSS"
        return (
            f"{pnl_emoji} **TRADE CLOSED ({outcome})**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**Direction:** {direction}\n"
            f"**Entry:** {trade_data.get('entry_price')}\n"
            f"**Exit:** {trade_data.get('exit_price')}\n"
            f"**P&L:** ${pnl:.2f}\n"
            f"**Reason:** {trade_data.get('status', 'MANUAL')}\n\n"
            f"*Balance updated.* 📊"
        )
    return ""
