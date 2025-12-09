from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
    
    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        """
        Analyze the market data and return a vote (BUY/SELL/NEUTRAL) and confidence (0-1).
        """
        raise NotImplementedError

class TrendAgent(BaseAgent):
    def __init__(self):
        super().__init__("Trend Agent")
        
    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        latest = df.iloc[-1]
        
        # EMA Trend
        ema_20 = latest.get('ema_20', 0)
        sma_50 = latest.get('sma_50', 0)
        close = latest['close']
        
        # MACD Trend
        macd = latest.get('macd', 0)
        macd_signal = latest.get('macd_signal', 0)
        
        score = 0
        
        # Price above EMAs
        if close > ema_20: score += 1
        if ema_20 > sma_50: score += 1
        
        # MACD Bullish
        if macd > macd_signal: score += 1
        if macd > 0: score += 1
        
        if score >= 3:
            return "BUY", 0.8
        elif score <= 1:
            return "SELL", 0.8
        else:
            return "NEUTRAL", 0.5

class VolatilityAgent(BaseAgent):
    def __init__(self):
        super().__init__("Volatility Agent")
        
    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        latest = df.iloc[-1]
        close = latest['close']
        
        bb_high = latest.get('bb_high', close)
        bb_low = latest.get('bb_low', close)
        bb_mid = latest.get('bb_mid', close)
        atr = latest.get('atr', 0)
        
        # Band squeeze or breakout logic could go here
        # Simple mean reversion for now
        
        if close < bb_low:
            return "BUY", 0.7  # Oversold / Reversion
        elif close > bb_high:
            return "SELL", 0.7 # Overbought / Reversion
        
        return "NEUTRAL", 0.5

class PatternAgent(BaseAgent):
    def __init__(self):
        super().__init__("Pattern Agent")
        
    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        latest = df.iloc[-1]
        
        if latest.get('pattern_bullish_engulfing', False):
            return "BUY", 0.9
        if latest.get('pattern_hammer', False):
            return "BUY", 0.85
            
        if latest.get('pattern_bearish_engulfing', False):
            return "SELL", 0.9
        if latest.get('pattern_doji', False):
            return "NEUTRAL", 0.6
            
        return "NEUTRAL", 0.5

class MomentumAgent(BaseAgent):
    def __init__(self):
        super().__init__("Momentum Agent")
        
    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        latest = df.iloc[-1]
        rsi = latest.get('rsi', 50)
        
        if rsi < 30:
            return "BUY", 0.85 # Oversold
        elif rsi > 70:
            return "SELL", 0.85 # Overbought
        elif 50 < rsi < 70:
            return "BUY", 0.6 # Bullish momentum
        elif 30 < rsi < 50:
            return "SELL", 0.6 # Bearish momentum
            
        return "NEUTRAL", 0.5

class CouncilOfAgents:
    def __init__(self):
        self.agents = [
            TrendAgent(),
            VolatilityAgent(),
            PatternAgent(),
            MomentumAgent()
        ]
        
    def deliberate(self, df: pd.DataFrame) -> Dict:
        """
        Collect votes from all agents and form a consensus.
        """
        votes = {}
        buy_score = 0
        sell_score = 0
        total_confidence = 0
        
        for agent in self.agents:
            vote, confidence = agent.analyze(df)
            votes[agent.name] = {
                "vote": vote,
                "confidence": confidence
            }
            
            if vote == "BUY":
                buy_score += confidence
            elif vote == "SELL":
                sell_score += confidence
                
            total_confidence += confidence
            
        # Determine Consensus
        if buy_score > sell_score and buy_score > 1.5: # Threshold
            consensus = "BUY"
            strength = buy_score / len(self.agents)
        elif sell_score > buy_score and sell_score > 1.5:
            consensus = "SELL"
            strength = sell_score / len(self.agents)
        else:
            consensus = "NEUTRAL"
            strength = 0.5
            
        return {
            "consensus": consensus,
            "strength": round(strength, 2),
            "votes": votes
        }
