import pandas as pd
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from bot.data_loader import fetch_forex_data
from bot.indicators import add_technical_indicators
from bot.pattern_recognition import identify_patterns
from bot.agentic_council import CouncilOfAgents
from bot.ml_model import ForexPredictor, ForexRegressor
from bot.trade_calculator import calculate_trade_levels

# Available symbols to scan
AVAILABLE_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
    "USDCHF", "NZDUSD", "EURJPY", "GBPJPY", "AUDJPY",
    "CADJPY", "EURGBP", "EURAUD", "GBPAUD", "EURCAD"
]

def calculate_opportunity_score(df: pd.DataFrame, prediction: int, confidence: float, council_result: Dict) -> float:
    """
    Calculate opportunity score based on ML confidence, Council consensus, and patterns.
    Score range: 0-100, higher is better. Minimum threshold for trading should be 70.
    """
    latest = df.iloc[-1]
    score = 0
    
    # 1. ML Confidence (0-35 points) - INCREASED from 30
    score += confidence * 35
    
    # 2. Council Consensus (0-40 points)
    consensus = council_result['consensus']
    strength = council_result['strength']
    
    if consensus == "BUY" and prediction == 1:
        score += strength * 40
    elif consensus == "SELL" and prediction == 0:
        score += strength * 40
    elif consensus != "NEUTRAL":
        # REDUCED partial credit from 20 to 10 - require better alignment
        score += strength * 10
        
    # 3. Indicator Alignment (0-15 points) - STRICTER RSI requirements
    rsi = latest.get('rsi', 50)
    # For BUY: RSI should be between 35-65 (not overbought, not oversold)
    # For SELL: RSI should be between 35-65 (same range)
    if prediction == 1:  # Bullish
        if 35 < rsi < 65:
            score += 15
        elif 30 < rsi < 70:
            score += 8  # Partial credit if close
    else:  # Bearish
        if 35 < rsi < 65:
            score += 15
        elif 30 < rsi < 70:
            score += 8
            
    # 4. Pattern Strength (0-10 points) - REDUCED from 15, more selective
    pattern_score = 0
    if prediction == 1:
        if latest.get('pattern_hammer', False) or latest.get('pattern_bullish_engulfing', False):
            pattern_score += 10
    else:
        if latest.get('pattern_bearish_engulfing', False):
            pattern_score += 10
            
    score += pattern_score
    
    # NEW 5. Trend Strength Filter (0-10 points)
    # Check if price is aligned with moving averages
    close = latest['close']
    ema_20 = latest.get('ema_20', close)
    sma_50 = latest.get('sma_50', close)
    
    if prediction == 1:  # Bullish - want price above EMAs
        if close > ema_20 and close > sma_50:
            score += 10
        elif close > ema_20 or close > sma_50:
            score += 5
    else:  # Bearish - want price below EMAs
        if close < ema_20 and close < sma_50:
            score += 10
        elif close < ema_20 or close < sma_50:
            score += 5
    
    # NEW 6. Volatility Filter - Penalize overly volatile/choppy markets
    # Check MACD divergence
    macd = latest.get('macd', 0)
    macd_signal = latest.get('macd_signal', 0)
    macd_diff = abs(macd - macd_signal)
    
    # Reward clear MACD signals
    if macd_diff > 0.0001:  # Meaningful divergence
        if (prediction == 1 and macd > macd_signal) or (prediction == 0 and macd < macd_signal):
            score += 5  # Bonus for MACD alignment
    
    return min(100, max(0, score))

def scan_single_pair(symbol: str, period: str = "1mo", interval: str = "15m") -> Dict:
    """
    Scan a single trading pair and return analysis.
    Returns None if pair doesn't meet quality thresholds.
    """
    try:
        # Fetch and analyze data
        df = fetch_forex_data(symbol, period=period, interval=interval)
        if df.empty or len(df) < 50:
            return None
        
        df = add_technical_indicators(df)
        df = identify_patterns(df)
        
        # 1. Council Deliberation
        council = CouncilOfAgents()
        council_result = council.deliberate(df)
        
        # 2. ML Classification (Direction)
        predictor = ForexPredictor()
        predictor.train(df)
        prediction, confidence = predictor.predict_next_movement(df)
        
        # CRITICAL FILTER: Reject low confidence predictions early
        if confidence < 0.65:  # Minimum 65% confidence required
            print(f"  ✗ {symbol}: Rejected - Low confidence ({confidence*100:.1f}%)")
            return None
        
        # 3. ML Regression (Future Path)
        regressor = ForexRegressor()
        regressor.train(df)
        future_path = regressor.predict_future_path(df, steps=10, interval=interval)
        
        # Calculate opportunity score
        score = calculate_opportunity_score(df, prediction, confidence, council_result)
        
        # ADDITIONAL FILTER: Reject low scores early
        if score < 60:  # Preliminary threshold (auto-trader will use 70)
            print(f"  ✗ {symbol}: Rejected - Low score ({score:.1f}/100)")
            return None
        
        # Calculate trade levels
        trade_levels = calculate_trade_levels(df, prediction, confidence)
        
        # Prepare chart data (last 100 candles)
        chart_df = df.tail(100).copy()
        # Ensure datetime is available for chart
        if 'datetime' in chart_df.columns:
            # Use unix timestamp for intraday data
            chart_df['time'] = chart_df['datetime'].astype('int64') // 10**9
        else:
            # Fallback if datetime column missing
            chart_df['time'] = chart_df.index.astype('int64') // 10**9
            
        candles = chart_df[['time', 'open', 'high', 'low', 'close']].to_dict(orient='records')

        return {
            "symbol": symbol,
            "score": round(score, 2),
            "prediction": "UP" if prediction == 1 else "DOWN",
            "confidence": round(confidence * 100, 2),
            "current_price": float(df.iloc[-1]['close']),
            "trade_levels": trade_levels,
            "council": council_result,
            "future_path": future_path,
            "chart_data": candles,
            "patterns": {
                "doji": bool(df.iloc[-1].get('pattern_doji', False)),
                "hammer": bool(df.iloc[-1].get('pattern_hammer', False)),
                "bullish_engulfing": bool(df.iloc[-1].get('pattern_bullish_engulfing', False)),
                "bearish_engulfing": bool(df.iloc[-1].get('pattern_bearish_engulfing', False))
            },
            "indicators": {
                "rsi": float(df.iloc[-1]['rsi']) if not pd.isna(df.iloc[-1]['rsi']) else 50,
                "macd": float(df.iloc[-1]['macd']) if not pd.isna(df.iloc[-1]['macd']) else 0,
                "atr": float(df.iloc[-1]['atr']) if not pd.isna(df.iloc[-1]['atr']) else 0,
            }
        }
    except Exception as e:
        print(f"Error scanning {symbol}: {e}")
        return None

def scan_all_pairs(max_workers: int = 5) -> List[Dict]:
    """
    Scan all available pairs in parallel and return ranked opportunities.
    
    Args:
        max_workers: Number of parallel workers for scanning
        
    Returns:
        List of opportunities sorted by score (highest first)
    """
    opportunities = []
    
    print(f"Starting scan of {len(AVAILABLE_SYMBOLS)} symbols...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {
            executor.submit(scan_single_pair, symbol): symbol 
            for symbol in AVAILABLE_SYMBOLS
        }
        
        for future in as_completed(future_to_symbol):
            result = future.result()
            if result:
                opportunities.append(result)
                print(f"✓ {result['symbol']}: Score {result['score']}")
    
    # Sort by score (highest first)
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Scan complete! Found {len(opportunities)} opportunities")
    return opportunities

def get_best_opportunity() -> Dict:
    """
    Scan all pairs and return the single best trading opportunity.
    """
    opportunities = scan_all_pairs()
    
    if not opportunities:
        return None
    
    best = opportunities[0]
    print(f"Best opportunity: {best['symbol']} with score {best['score']}")
    
    return best
