import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email_alert(subject: str, body: str):
    """
    Send an email alert using SMTP (e.g., Gmail).
    Requires EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECEIVER in env vars.
    """
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = os.getenv("EMAIL_RECEIVER")
    
    # Optional: Allow custom SMTP server, default to Gmail
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not sender_email or not sender_password or not receiver_email:
        logger.warning("[Email] ⚠️  Credentials missing. Skipping email alert.")
        return

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"Forex Bot <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach body
        msg.attach(MIMEText(body, 'html')) # Use HTML for better formatting

        # Connect to server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Secure the connection
        server.login(sender_email, sender_password)
        
        # Send
        server.send_message(msg)
        server.quit()
        logger.info(f"[Email] ✅ Alert sent to {receiver_email}")
        
    except Exception as e:
        logger.error(f"[Email] ❌ Failed to send email: {e}")

def format_trade_email(trade_data: dict, event_type: str) -> tuple:
    """
    Format trade data into an Email Subject and HTML Body.
    Returns: (subject, html_body)
    """
    symbol = trade_data.get('symbol', 'UNKNOWN')
    direction = trade_data.get('direction', 'UNKNOWN')
    
    if event_type == "OPEN":
        subject = f"🚀 NEW TRADE: {direction} {symbol}"
        emoji = "🟢" if direction == "BUY" else "🔴"
        
        body = f"""
        <html>
          <body>
            <h2>{emoji} Trade Opened: {symbol}</h2>
            <p>A new trade has been executed based on market analysis.</p>
            <ul>
                <li><b>Direction:</b> {direction}</li>
                <li><b>Entry Price:</b> {trade_data.get('entry_price')}</li>
                <li><b>Size:</b> {trade_data.get('lot_size')} lots</li>
            </ul>
            <hr>
            <p><i>Stop Loss:</i> {trade_data.get('stop_loss')}<br>
            <i>Take Profit:</i> {trade_data.get('target_price')}</p>
            <p><b>Score:</b> {trade_data.get('score', 0)}</p>
          </body>
        </html>
        """
        return subject, body

    elif event_type == "CLOSE":
        pnl = trade_data.get('pnl', 0.0)
        outcome = "PROFIT" if pnl >= 0 else "LOSS"
        subject = f"{'💰' if pnl >= 0 else '🔻'} TRADE CLOSED: {symbol} ({outcome})"
        
        body = f"""
        <html>
          <body>
            <h2>Trade Closed: {symbol}</h2>
            <p><b>Outcome:</b> <span style="color: {'green' if pnl >= 0 else 'red'};">{outcome}</span></p>
            <ul>
                <li><b>Direction:</b> {direction}</li>
                <li><b>Entry:</b> {trade_data.get('entry_price')}</li>
                <li><b>Exit:</b> {trade_data.get('exit_price')}</li>
                <li><b>P&L:</b> ${pnl:.2f}</li>
            </ul>
            <p><b>Reason:</b> {trade_data.get('status', 'MANUAL')}</p>
          </body>
        </html>
        """
        return subject, body
    
    return "Notification", "Unknown Event"
