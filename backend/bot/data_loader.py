import yfinance as yf
import pandas as pd
import time
from typing import Dict, Tuple

# Price cache: {symbol: (price, timestamp)}
_price_cache: Dict[str, Tuple[float, float]] = {}
_CACHE_TTL = 10  # Cache prices for 10 seconds

def fetch_forex_data(symbol: str, period: str = "1y", interval: str = "1h") -> pd.DataFrame:
    """
    Fetch historical Forex data from yfinance.
    
    Args:
        symbol (str): The forex pair symbol (e.g., 'EURUSD=X').
        period (str): Data period to download (e.g., '1d', '5d', '1mo', '1y').
        interval (str): Data interval (e.g., '1m', '5m', '1h', '1d').
        
    Returns:
        pd.DataFrame: DataFrame containing the historical data.
    """
    # Ensure the symbol has the correct suffix for yfinance if not present
    if not symbol.endswith("=X") and not symbol.endswith("-USD") and not symbol.startswith("^") and not symbol.endswith("=F"):
        symbol = f"{symbol}=X"
        
    print(f"Fetching data for {symbol}...")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    
    if df.empty:
        print(f"No data found for {symbol}.")
        return df
        
    # Reset index to make Date/Datetime a column
    df.reset_index(inplace=True)
    
    # Rename columns to standard lowercase
    df.columns = [c.lower() for c in df.columns]
    
    # Ensure datetime is timezone-naive or consistent
    if 'date' in df.columns:
        df['datetime'] = pd.to_datetime(df['date'])
        df.drop(columns=['date'], inplace=True)
    elif 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        
    # Keep only necessary columns
    required_cols = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df = df[[c for c in required_cols if c in df.columns]]
    
    return df

def get_live_price(symbol: str) -> float:
    """Get current live price for a forex pair with caching."""
    global _price_cache
    
    # Check cache first
    cache_key = symbol
    current_time = time.time()
    
    if cache_key in _price_cache:
        cached_price, cached_time = _price_cache[cache_key]
        # Use cache if less than 60 seconds old (increased from 10)
        if current_time - cached_time < 60:
            return cached_price
    
    # Fetch new price
    ticker = yf.Ticker(f"{symbol}=X")
    price = ticker.fast_info.last_price
    
    # Update cache
    _price_cache[cache_key] = (price, current_time)
    
    return price
