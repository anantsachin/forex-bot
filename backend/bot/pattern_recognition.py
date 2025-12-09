import pandas as pd

def identify_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify candlestick patterns in the DataFrame.
    Adds boolean columns for patterns.
    """
    if df.empty:
        return df
        
    df = df.copy()
    
    # Ensure columns are numeric
    open_price = df['open']
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Calculate candle body and range
    body = close - open_price
    abs_body = body.abs()
    candle_range = high - low
    
    # Doji: Body is very small relative to range
    df['pattern_doji'] = abs_body <= (candle_range * 0.1)
    
    # Hammer: Small body near top, long lower shadow
    lower_shadow = pd.concat([open_price, close], axis=1).min(axis=1) - low
    upper_shadow = high - pd.concat([open_price, close], axis=1).max(axis=1)
    df['pattern_hammer'] = (lower_shadow >= (abs_body * 2)) & (upper_shadow <= (abs_body * 0.5))
    
    # Bullish Engulfing: Previous candle red, current candle green and engulfs previous
    prev_open = open_price.shift(1)
    prev_close = close.shift(1)
    prev_body = prev_close - prev_open
    
    df['pattern_bullish_engulfing'] = (
        (prev_body < 0) & # Previous red
        (body > 0) &      # Current green
        (open_price <= prev_close) & # Open below prev close
        (close >= prev_open)         # Close above prev open
    )
    
    # Bearish Engulfing
    df['pattern_bearish_engulfing'] = (
        (prev_body > 0) & # Previous green
        (body < 0) &      # Current red
        (open_price >= prev_close) & # Open above prev close
        (close <= prev_open)         # Close below prev open
    )
    
    return df
