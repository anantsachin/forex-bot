import pandas as pd
import numpy as np
from bot.indicators import add_technical_indicators
from bot.ml_model import ForexPredictor

class Backtester:
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades = []
        self.predictor = ForexPredictor()
        
    def run(self, df: pd.DataFrame):
        """
        Run the backtest on the provided DataFrame.
        """
        # Prepare data
        df = add_technical_indicators(df)
        df.dropna(inplace=True)
        
        # Train model on first 70% of data (simulated) or use pre-trained
        # For backtesting, we should ideally walk-forward, but for simplicity:
        split_idx = int(len(df) * 0.7)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        print("Training model for backtest...")
        self.predictor.train(train_df)
        
        position = None # 'long', 'short', None
        entry_price = 0
        stop_loss = 0
        take_profit = 0
        
        print("Running simulation...")
        for i in range(len(test_df) - 1):
            # Use .iloc for integer indexing
            current_row = test_df.iloc[[i]]
            next_row = test_df.iloc[[i+1]] # To check result (simulating next step)
            
            current_price = current_row['close'].values[0]
            current_time = current_row['datetime'].values[0]
            
            # Check exit conditions if in position
            if position == 'long':
                if current_price <= stop_loss:
                    self._close_trade(current_time, stop_loss, 'loss', 'long')
                    position = None
                elif current_price >= take_profit:
                    self._close_trade(current_time, take_profit, 'win', 'long')
                    position = None
            
            # Check entry conditions if no position
            if position is None:
                prediction, prob = self.predictor.predict_next_movement(current_row)
                atr = current_row['atr'].values[0]
                
                # Breathing space stop loss (1.5 * ATR)
                sl_dist = 1.5 * atr
                tp_dist = 2.0 * sl_dist # 1:2 Risk Reward
                
                if prediction == 1 and prob > 0.5: # Bullish (relaxed for testing)
                    position = 'long'
                    entry_price = current_price
                    stop_loss = entry_price - sl_dist
                    take_profit = entry_price + tp_dist
                    self.trades.append({
                        'type': 'entry',
                        'side': 'long',
                        'price': entry_price,
                        'time': current_time,
                        'sl': stop_loss,
                        'tp': take_profit
                    })
        
        return self._generate_report()
    
    def _close_trade(self, time, price, result, side):
        last_trade = self.trades[-1]
        profit = 0
        if side == 'long':
            profit = price - last_trade['price']
        
        # Assuming 1 lot (100,000 units) for simplicity, or just pips
        # Let's calculate % return
        pct_return = (profit / last_trade['price']) * 100
        
        self.balance *= (1 + (pct_return / 100)) # Compounding
        
        self.trades.append({
            'type': 'exit',
            'side': side,
            'price': price,
            'time': time,
            'result': result,
            'profit_pct': pct_return,
            'balance': self.balance
        })

    def _generate_report(self):
        if not self.trades:
            return {"message": "No trades executed."}
            
        exits = [t for t in self.trades if t['type'] == 'exit']
        wins = [t for t in exits if t['result'] == 'win']
        losses = [t for t in exits if t['result'] == 'loss']
        
        total_trades = len(exits)
        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        
        total_return = ((self.balance - self.initial_balance) / self.initial_balance) * 100
        
        # Calculate Max Drawdown
        balances = [t['balance'] for t in exits]
        if not balances:
            max_drawdown = 0
        else:
            peak = self.initial_balance
            max_drawdown = 0
            for b in balances:
                if b > peak:
                    peak = b
                dd = (peak - b) / peak * 100
                if dd > max_drawdown:
                    max_drawdown = dd
                    
        return {
            "initial_balance": self.initial_balance,
            "final_balance": self.balance,
            "total_return_pct": total_return,
            "total_trades": total_trades,
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
            "trades": self.trades
        }
