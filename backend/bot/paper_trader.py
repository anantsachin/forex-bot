import time
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Callable
import random
from bot.data_loader import get_live_price

# Global callback for loss notifications
_loss_callback: Optional[Callable] = None

def set_loss_callback(callback: Callable):
    """Set a callback function to be called when a losing trade closes."""
    global _loss_callback
    _loss_callback = callback

class PaperTrade:
    def __init__(self, trade_id: str, symbol: str, direction: str, entry_price: float, 
                 stop_loss: float, target_price: float, lot_size: float,
                 entry_time: Optional[str] = None, exit_time: Optional[str] = None,
                 exit_price: Optional[float] = None, pnl: float = 0.0, status: str = "OPEN",
                 score: float = 0.0):
        self.trade_id = trade_id
        self.symbol = symbol
        self.direction = direction  # "BUY" or "SELL"
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.target_price = target_price
        self.lot_size = lot_size
        self.score = score  # Opportunity quality score
        self.entry_time = datetime.fromisoformat(entry_time) if entry_time else datetime.now()
        self.exit_time = datetime.fromisoformat(exit_time) if exit_time else None
        self.exit_price = exit_price
        self.pnl = pnl
        self.status = status  # OPEN, CLOSED_WIN, CLOSED_LOSS, CLOSED_MANUAL
        
    def calculate_floating_pnl(self, current_price: float) -> tuple:
        """Calculate unrealized P&L based on current market price.
        
        Returns:
            tuple: (floating_pnl, pnl_percentage)
        """
        # Standard Lot = 100,000 units
        units = self.lot_size * 100000
        
        # Calculate raw profit in Quote Currency
        if self.direction == "BUY":
            price_diff = current_price - self.entry_price
        else:  # SELL
            price_diff = self.entry_price - current_price
            
        raw_pnl = price_diff * units
        
        # Convert to USD (Account Currency)
        symbol = self.symbol
        
        if symbol.endswith("USD"):
            # XXX/USD pairs (e.g., EURUSD) -> Quote is USD
            floating_pnl = raw_pnl
            
        elif symbol.startswith("USD"):
            # USD/XXX pairs (e.g., USDJPY) -> Quote is XXX
            # Convert XXX to USD: Divide by current USD/XXX rate (current_price)
            if current_price > 0:
                floating_pnl = raw_pnl / current_price
            else:
                floating_pnl = 0
                
        else:
            # Cross pairs (e.g., EURGBP) -> Quote is GBP
            # Need to convert GBP to USD. Find GBPUSD rate.
            quote_currency = symbol[3:]  # e.g., GBP
            usd_pair = f"{quote_currency}USD"
            
            try:
                # Try to get conversion rate
                conversion_rate = get_live_price(usd_pair)
                floating_pnl = raw_pnl * conversion_rate
            except Exception as e:
                print(f"Could not fetch conversion rate for {usd_pair}, using 1.0: {e}")
                # Fallback or try inverse USD{Quote}
                try:
                    inverse_pair = f"USD{quote_currency}"
                    inverse_rate = get_live_price(inverse_pair)
                    floating_pnl = raw_pnl / inverse_rate
                except:
                    floating_pnl = raw_pnl  # Fallback to 1:1 if fails
        
        # Calculate percentage
        # For percentage, we need to know how much capital was risked
        # Simple approach: P&L as % of notional value at entry
        notional_value = self.entry_price * units
        if symbol.startswith("USD") and current_price > 0:
            notional_value = notional_value / self.entry_price  # Already in USD
        
        pnl_percentage = (floating_pnl / abs(notional_value)) * 100 if notional_value != 0 else 0
        
        return (round(floating_pnl, 2), round(pnl_percentage, 4))
    
    def calculate_max_risk(self) -> float:
        """Calculate maximum risk (potential loss if stop loss is hit).
        
        Returns:
            float: Maximum risk in USD
        """
        # Standard Lot = 100,000 units
        units = self.lot_size * 100000
        
        # Calculate price difference to stop loss
        if self.direction == "BUY":
            price_diff = self.stop_loss - self.entry_price  # Negative for BUY
        else:  # SELL
            price_diff = self.entry_price - self.stop_loss  # Negative for SELL
            
        raw_risk = abs(price_diff * units)
        
        # Convert to USD (Account Currency)
        symbol = self.symbol
        
        if symbol.endswith("USD"):
            # XXX/USD pairs (e.g., EURUSD) -> Quote is USD
            max_risk = raw_risk
            
        elif symbol.startswith("USD"):
            # USD/XXX pairs (e.g., USDJPY) -> Quote is XXX
            # Convert XXX to USD: Divide by current USD/XXX rate
            if self.entry_price > 0:
                max_risk = raw_risk / self.entry_price
            else:
                max_risk = 0
                
        else:
            # Cross pairs (e.g., EURGBP) -> Quote is GBP
            # Need to convert to USD
            quote_currency = symbol[3:]  # e.g., GBP
            usd_pair = f"{quote_currency}USD"
            
            try:
                conversion_rate = get_live_price(usd_pair)
                max_risk = raw_risk * conversion_rate
            except Exception as e:
                print(f"Could not fetch conversion rate for {usd_pair}, using 1.0: {e}")
                try:
                    inverse_pair = f"USD{quote_currency}"
                    inverse_rate = get_live_price(inverse_pair)
                    max_risk = raw_risk / inverse_rate
                except:
                    max_risk = raw_risk  # Fallback to 1:1 if fails
        
        return round(max_risk, 2)
    
    def to_dict(self):
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "target_price": self.target_price,
            "lot_size": self.lot_size,
            "score": round(self.score, 2),
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "exit_price": self.exit_price,
            "pnl": round(self.pnl, 2),
            "status": self.status
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'PaperTrade':
        """Create a PaperTrade instance from a dictionary."""
        return PaperTrade(
            trade_id=data['trade_id'],
            symbol=data['symbol'],
            direction=data['direction'],
            entry_price=data['entry_price'],
            stop_loss=data['stop_loss'],
            target_price=data['target_price'],
            lot_size=data['lot_size'],
            entry_time=data['entry_time'],
            exit_time=data.get('exit_time'),
            exit_price=data.get('exit_price'),
            pnl=data.get('pnl', 0.0),
            status=data.get('status', 'OPEN'),
            score=data.get('score', 0.0)
        )

class PaperTradingEngine:
    def __init__(self, initial_balance: float = 10000, data_file: str = "paper_trades.json"):
        self.data_file = data_file
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades: List[PaperTrade] = []
        self.active_trades: Dict[str, PaperTrade] = {}
        
        # Load existing data if available
        self._load_data()
    
    def _save_data(self):
        """Save all trades and balance to JSON file."""
        try:
            data = {
                "initial_balance": self.initial_balance,
                "balance": self.balance,
                "trades": [trade.to_dict() for trade in self.trades],
                "active_trade_ids": list(self.active_trades.keys())
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving paper trading data: {e}")
    
    def _load_data(self):
        """Load trades and balance from JSON file if it exists."""
        if not os.path.exists(self.data_file):
            print("No previous trading data found, starting fresh.")
            return
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            self.initial_balance = data.get('initial_balance', self.initial_balance)
            self.balance = data.get('balance', self.balance)
            
            # Restore all trades
            for trade_data in data.get('trades', []):
                trade = PaperTrade.from_dict(trade_data)
                self.trades.append(trade)
                
                # Restore active trades
                if trade.trade_id in data.get('active_trade_ids', []):
                    self.active_trades[trade.trade_id] = trade
            
            print(f"Loaded {len(self.trades)} trades from history. Balance: ${self.balance:.2f}")
        except Exception as e:
            print(f"Error loading paper trading data: {e}")
        
    def open_trade(self, symbol: str, direction: str, entry_price: float, 
                   stop_loss: float, target_price: float, lot_size: float, score: float = 0.0) -> PaperTrade:
        """Open a new paper trade."""
        trade_id = f"{symbol}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        trade = PaperTrade(
            trade_id=trade_id,
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            lot_size=lot_size,
            score=score
        )
        
        self.trades.append(trade)
        self.active_trades[trade_id] = trade
        
        print(f"Opened {direction} trade for {symbol} at {entry_price} (Score: {score})")
        self._save_data()  # Save after opening trade
        return trade
    
    def check_and_update_trades(self, current_prices: Dict[str, float]):
        """Check all active trades and close if stop/target hit."""
        for trade_id, trade in list(self.active_trades.items()):
            if trade.symbol not in current_prices:
                continue
                
            current_price = current_prices[trade.symbol]
            
            # Check if stop loss or target hit
            should_close = False
            exit_reason = None
            
            if trade.direction == "BUY":
                if current_price <= trade.stop_loss:
                    should_close = True
                    exit_reason = "CLOSED_LOSS"
                elif current_price >= trade.target_price:
                    should_close = True
                    exit_reason = "CLOSED_WIN"
            else:  # SELL
                if current_price >= trade.stop_loss:
                    should_close = True
                    exit_reason = "CLOSED_LOSS"
                elif current_price <= trade.target_price:
                    should_close = True
                    exit_reason = "CLOSED_WIN"
            
            if should_close:
                self.close_trade(trade_id, current_price, exit_reason)
    


    def reset_account(self, initial_balance: float = 10000):
        """Reset the account to initial state."""
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades = []
        self.active_trades = {}
        self._save_data()
        print(f"Account reset to ${initial_balance}")

    def close_trade(self, trade_id: str, exit_price: float, reason: str = "CLOSED_MANUAL"):
        """Close a trade and calculate P&L."""
        if trade_id not in self.active_trades:
            return
        
        trade = self.active_trades[trade_id]
        trade.exit_time = datetime.now()
        trade.exit_price = exit_price
        trade.status = reason
        
        # Calculate P&L
        # Standard Lot = 100,000 units
        units = trade.lot_size * 100000
        
        # Calculate raw profit in Quote Currency
        if trade.direction == "BUY":
            price_diff = exit_price - trade.entry_price
        else:  # SELL
            price_diff = trade.entry_price - exit_price
            
        raw_pnl = price_diff * units
        
        # Convert to USD (Account Currency)
        symbol = trade.symbol
        
        if symbol.endswith("USD"):
            # XXX/USD pairs (e.g., EURUSD) -> Quote is USD
            trade.pnl = raw_pnl
            
        elif symbol.startswith("USD"):
            # USD/XXX pairs (e.g., USDJPY) -> Quote is XXX
            # Convert XXX to USD: Divide by current USD/XXX rate (exit_price)
            if exit_price > 0:
                trade.pnl = raw_pnl / exit_price
            else:
                trade.pnl = 0
                
        else:
            # Cross pairs (e.g., EURGBP) -> Quote is GBP
            # Need to convert GBP to USD. Find GBPUSD rate.
            quote_currency = symbol[3:] # e.g., GBP
            usd_pair = f"{quote_currency}USD"
            
            try:
                # Try to get conversion rate
                # Note: This is a blocking call, might slow down. 
                # In production, use a cached rate or pass it in.
                conversion_rate = get_live_price(usd_pair)
                trade.pnl = raw_pnl * conversion_rate
            except Exception as e:
                print(f"Could not fetch conversion rate for {usd_pair}, using 1.0: {e}")
                # Fallback or try inverse USD{Quote}
                try:
                    inverse_pair = f"USD{quote_currency}"
                    inverse_rate = get_live_price(inverse_pair)
                    trade.pnl = raw_pnl / inverse_rate
                except:
                    trade.pnl = raw_pnl # Fallback to 1:1 if fails
        
        self.balance += trade.pnl
        del self.active_trades[trade_id]
        
        print(f"Closed {trade.symbol} trade: {reason}, P&L: ${trade.pnl:.2f}")
        
        # Notify auto-trader if this was a losing trade
        global _loss_callback
        if _loss_callback and "LOSS" in reason and trade.pnl < 0:
            _loss_callback()
        
        self._save_data()  # Save after closing trade
    
    def get_active_trades(self) -> List[Dict]:
        """Get all active trades with current prices, floating P&L, and risk metrics."""
        active_trades_data = []
        
        for trade in self.active_trades.values():
            trade_dict = trade.to_dict()
            
            # Calculate risk amount
            try:
                risk_amount = trade.calculate_max_risk()
                risk_percentage = (risk_amount / self.balance) * 100 if self.balance > 0 else 0
                
                trade_dict['risk_amount'] = round(risk_amount, 2)
                trade_dict['risk_percentage'] = round(risk_percentage, 2)
            except Exception as e:
                print(f"Error calculating risk for {trade.symbol}: {e}")
                trade_dict['risk_amount'] = 0.0
                trade_dict['risk_percentage'] = 0.0
            
            # Fetch current price and calculate floating P&L
            try:
                current_price = get_live_price(trade.symbol)
                floating_pnl, pnl_percentage = trade.calculate_floating_pnl(current_price)
                
                trade_dict['current_price'] = round(current_price, 5)
                trade_dict['floating_pnl'] = floating_pnl
                trade_dict['pnl_percentage'] = pnl_percentage
            except Exception as e:
                print(f"Error calculating floating P&L for {trade.symbol}: {e}")
                trade_dict['current_price'] = trade.entry_price
                trade_dict['floating_pnl'] = 0.0
                trade_dict['pnl_percentage'] = 0.0
            
            active_trades_data.append(trade_dict)
        
        return active_trades_data
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get recent closed trades."""
        closed_trades = [t for t in self.trades if t.status != "OPEN"]
        return [trade.to_dict() for trade in closed_trades[-limit:]]
    
    def get_stats(self) -> Dict:
        """Calculate trading statistics including risk metrics."""
        closed_trades = [t for t in self.trades if t.status != "OPEN"]
        
        # Calculate total floating P&L from active trades
        total_floating_pnl = 0.0
        max_risk_per_trade = 0.0
        total_daily_risk = 0.0
        
        for trade in self.active_trades.values():
            try:
                current_price = get_live_price(trade.symbol)
                floating_pnl, _ = trade.calculate_floating_pnl(current_price)
                total_floating_pnl += floating_pnl
                
                # Calculate risk for this trade
                trade_risk = trade.calculate_max_risk()
                total_daily_risk += trade_risk
                
                # Track maximum risk per trade
                if trade_risk > max_risk_per_trade:
                    max_risk_per_trade = trade_risk
                    
            except Exception as e:
                print(f"Error calculating floating P&L for {trade.symbol} in stats: {e}")
        
        if not closed_trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "total_floating_pnl": round(total_floating_pnl, 2),
                "max_risk_per_trade": round(max_risk_per_trade, 2),
                "total_daily_risk": round(total_daily_risk, 2),
                "balance": self.balance,
                "initial_balance": self.initial_balance,
                "return_pct": 0
            }
        
        wins = sum(1 for t in closed_trades if t.pnl > 0)
        total_pnl = sum(t.pnl for t in closed_trades)
        
        return {
            "total_trades": len(closed_trades),
            "win_rate": round((wins / len(closed_trades)) * 100, 2) if closed_trades else 0,
            "total_pnl": round(total_pnl, 2),
            "total_floating_pnl": round(total_floating_pnl, 2),
            "max_risk_per_trade": round(max_risk_per_trade, 2),
            "total_daily_risk": round(total_daily_risk, 2),
            "balance": round(self.balance, 2),
            "initial_balance": self.initial_balance,
            "return_pct": round(((self.balance - self.initial_balance) / self.initial_balance) * 100, 2)
        }

# Global paper trading engine instance
paper_trader = PaperTradingEngine(initial_balance=10000)
