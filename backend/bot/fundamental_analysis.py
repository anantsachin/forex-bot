import yfinance as yf
import pandas as pd
# from textblob import TextBlob # Uncomment if using TextBlob

def get_news_sentiment(symbol: str):
    """
    Fetch news for a symbol and calculate average sentiment.
    Returns a score between -1 (Negative) and 1 (Positive).
    """
    if not symbol.endswith("=X"):
        symbol = f"{symbol}=X"
        
    ticker = yf.Ticker(symbol)
    news = ticker.news
    
    if not news:
        return 0.0
        
    total_sentiment = 0
    count = 0
    
    for item in news:
        title = item.get('title', '')
        # Simple keyword based sentiment for now to avoid extra deps
        # In production, use an LLM or NLTK/TextBlob
        sentiment = 0
        lower_title = title.lower()
        
        if any(w in lower_title for w in ['surge', 'jump', 'gain', 'bull', 'rise', 'high', 'positive']):
            sentiment += 1
        elif any(w in lower_title for w in ['drop', 'fall', 'loss', 'bear', 'decline', 'low', 'negative']):
            sentiment -= 1
            
        total_sentiment += sentiment
        count += 1
        
    if count == 0:
        return 0.0
        
    # Normalize to -1 to 1
    avg_sentiment = total_sentiment / count
    return max(min(avg_sentiment, 1.0), -1.0)
