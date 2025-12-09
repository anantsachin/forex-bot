import pandas as pd
import numpy as np

def calculate_trade_levels(df: pd.DataFrame, prediction: int, confidence: float):
    """
    Calculate entry, stop loss, and target price based on ATR and prediction.
    
    Args:
        df: DataFrame with price data and ATR indicator
        prediction: 1 for bullish (buy), 0 for bearish (sell)
        confidence: ML prediction confidence (0-1)
        
    Returns:
        dict with entry_price, stop_loss, target_price, risk_reward
    """
    latest = df.iloc[-1]
    
    entry_price = float(latest['close'])
    atr = float(latest['atr']) if not pd.isna(latest['atr']) else 0.001
    
    # Dynamic ATR multipliers based on confidence
    # Higher confidence = tighter stops, larger targets
    if confidence >= 0.75:
        stop_multiplier = 2.0  # Widened from 1.8
        target_multiplier = 3.0  # Reduced from 4.0
    elif confidence >= 0.65:
        stop_multiplier = 2.5  # Widened from 2.0
        target_multiplier = 3.5  # Reduced from 4.0
    else:
        stop_multiplier = 3.0  # Widened from 2.2
        target_multiplier = 4.0  # Reduced from 4.4
    
    if prediction == 1:  # Bullish - Buy
        stop_loss = entry_price - (stop_multiplier * atr)
        target_price = entry_price + (target_multiplier * atr)
    else:  # Bearish - Sell
        stop_loss = entry_price + (stop_multiplier * atr)
        target_price = entry_price - (target_multiplier * atr)
    
    risk = abs(entry_price - stop_loss)
    reward = abs(target_price - entry_price)
    risk_reward = reward / risk if risk > 0 else 0
    
    return {
        "entry_price": round(entry_price, 5),
        "stop_loss": round(stop_loss, 5),
        "target_price": round(target_price, 5),
        "atr": round(atr, 5),
        "risk_reward": round(risk_reward, 2),
        "direction": "BUY" if prediction == 1 else "SELL"
    }

def calculate_position_size(balance: float, risk_per_trade: float, entry: float, stop: float):
    """
    Calculate position size based on risk management with minimum trade value.
    
    Args:
        balance: Account balance
        risk_per_trade: Percentage of balance to risk (e.g., 0.015 for 1.5%)
        entry: Entry price
        stop: Stop loss price
        
    Returns:
        Position size (number of lots)
    """
    # Calculate risk amount in dollars
    risk_amount = balance * risk_per_trade
    risk_per_unit = abs(entry - stop)
    
    # Calculate risk per unit in USD
    # For JPY pairs (price > 50), risk is in JPY, need to convert to USD
    if entry > 50:
        # Approximate conversion for USD/JPY and Cross-JPY
        # Risk (USD) = Risk (JPY) / Price
        risk_per_unit_usd = risk_per_unit / entry
    else:
        # For USD quote pairs (EURUSD, GBPUSD), risk is already in USD
        risk_per_unit_usd = risk_per_unit
        
    if risk_per_unit_usd == 0:
        return 0.01

    # Calculate raw units needed
    raw_units = risk_amount / risk_per_unit_usd
    
    # Convert to lots (1 Standard Lot = 100,000 units)
    lot_size = raw_units / 100000
    
    # Round to 2 decimal places (allows micro lots)
    lot_size = round(lot_size, 2)
    
    # Minimum 0.01 lot
    if lot_size < 0.01:
        lot_size = 0.01
    
    # Cap maximum position at 20000% of account balance (200x leverage)
    # Forex uses high leverage - actual risk controlled by stop loss
    max_notional = balance * 200.0
    
    # For JPY pairs, notional in USD is different
    if entry > 50:
        # For USD/JPY, Notional (USD) = Units
        # For EUR/JPY, Notional (USD) = Units * EURUSD_Price (approx 1.1)
        # Simplified: assume Notional (USD) ~= Units for JPY pairs
        max_units = max_notional
    else:
        # For EUR/USD, Notional (USD) = Units * Price
        max_units = max_notional / entry
        
    max_lot_size = max_units / 100000
    
    if lot_size > max_lot_size:
        lot_size = max(0.01, round(max_lot_size, 2))
    
    return round(lot_size, 2)

def predict_next_candle(df: pd.DataFrame, prediction: int, confidence: float):
    """
    Generate predicted next candle based on ML prediction and confidence.
    
    Args:
        df: Historical price data
        prediction: 1 for up, 0 for down
        confidence: Prediction confidence (0-1)
        
    Returns:
        dict with predicted OHLC
    """
    latest = df.iloc[-1]
    close = float(latest['close'])
    atr = float(latest['atr']) if not pd.isna(latest['atr']) else 0.001
    
    # Movement magnitude based on confidence and ATR
    movement = atr * confidence * 0.5
    
    if prediction == 1:  # Bullish
        predicted_close = close + movement
        predicted_high = predicted_close + (atr * 0.3)
        predicted_low = close - (atr * 0.2)
        predicted_open = close
    else:  # Bearish
        predicted_close = close - movement
        predicted_high = close + (atr * 0.2)
        predicted_low = predicted_close - (atr * 0.3)
        predicted_open = close
    
    return {
        "open": round(predicted_open, 5),
        "high": round(predicted_high, 5),
        "low": round(predicted_low, 5),
        "close": round(predicted_close, 5),
        "is_prediction": True
    }
