import pandas as pd
import ta

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame with 'open', 'high', 'low', 'close' columns.
        
    Returns:
        pd.DataFrame: DataFrame with added indicators.
    """
    if df.empty:
        return df
    
    # Ensure close is numeric
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    
    # RSI (Relative Strength Index)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    
    # MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
    df['bb_high'] = bollinger.bollinger_hband()
    df['bb_low'] = bollinger.bollinger_lband()
    df['bb_mid'] = bollinger.bollinger_mavg()
    
    # ATR (Average True Range) for Stop Loss
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    
    # SMA/EMA
    df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
    df['ema_20'] = ta.trend.ema_indicator(df['close'], window=20)
    
    # Drop NaN values created by indicators (optional, or handle later)
    # df.dropna(inplace=True)
    
    return df
