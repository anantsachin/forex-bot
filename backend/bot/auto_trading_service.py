import asyncio
import time
from datetime import datetime
from typing import Optional
from bot.opportunity_scanner import get_best_opportunity
from bot.trade_calculator import calculate_trade_levels, calculate_position_size
from bot.paper_trader import paper_trader, set_loss_callback

class AutoTradingService:
    def __init__(self):
        self.is_running = False
        self.last_trade_time: Optional[str] = None
        self.last_loss_time: Optional[float] = None  # Timestamp of last losing trade
        self.trade_count = 0
        self.task: Optional[asyncio.Task] = None
        self.scan_interval = 300  # 5 minutes between scans
        self.daily_start_balance: Optional[float] = None  # Track daily starting balance
        self.cooldown_after_loss = 900  # 15 minutes cooldown after a loss
        
        # Register callback for loss notifications
        set_loss_callback(self._on_trade_loss)
        
    def check_risk_limits(self) -> tuple[bool, str]:
        """
        Check if trading should be allowed based on risk management rules.
        Returns: (can_trade, reason_if_not)
        """
        stats = paper_trader.get_stats()
        
        # 1. Daily loss limit - stop if down 3% for the day
        if self.daily_start_balance is None:
            self.daily_start_balance = stats['balance']
        
        daily_pnl = stats['balance'] - self.daily_start_balance
        daily_pnl_pct = (daily_pnl / self.daily_start_balance) * 100
        
        if daily_pnl_pct < -3.0:
            return False, f"Daily loss limit hit ({daily_pnl_pct:.2f}%). Stopping trading for today."
        
        # 2. Maximum concurrent trades - max 3 at once
        active_count = len(paper_trader.active_trades)
        if active_count >= 3:
            return False, f"Maximum concurrent trades reached ({active_count}/3)"
        
        # 3. Cooldown after loss - wait 15 minutes after a losing trade
        if self.last_loss_time:
            time_since_loss = time.time() - self.last_loss_time
            if time_since_loss < self.cooldown_after_loss:
                remaining = int((self.cooldown_after_loss - time_since_loss) / 60)
                return False, f"Cooldown active - {remaining} min remaining after loss"
        
        # 4. Win rate check - stop if below 40% with at least 10 trades
        if stats['total_trades'] >= 10 and stats['win_rate'] < 40:
            return False, f"Win rate too low ({stats['win_rate']:.1f}%). Review strategy before continuing."
        
        return True, ""
    
    def _on_trade_loss(self):
        """Callback invoked when a losing trade closes."""
        self.last_loss_time = time.time()
        print(f"[Auto-Trade] \u26a0\ufe0f  Loss detected - Cooldown activated (15 min)")
        
    async def trading_loop(self):
        """Main auto-trading loop that runs continuously with risk management."""
        print("Auto-trading started with enhanced risk management!")
        print("Risk limits: Max 3% daily loss, Max 3 concurrent trades, 15min cooldown after losses")
        
        while self.is_running:
            try:
                # Check risk limits before scanning
                can_trade, reason = self.check_risk_limits()
                if not can_trade:
                    print(f"[Auto-Trade] ⚠️  {reason}")
                    await asyncio.sleep(60)  # Check again in 1 minute
                    continue
                
                print(f"[Auto-Trade] Scanning for opportunities... (Trade #{self.trade_count + 1})")
                
                # Get best opportunity
                best = get_best_opportunity()
                
                # Score threshold set to 45 to allow trading
                if best and best.get('score', 0) >= 45.0:
                    print(f"[Auto-Trade] ✅ Found opportunity: {best['symbol']} (Score: {best['score']:.1f}/100)")
                    
                    # Calculate trade levels with improved risk-reward
                    trade_levels = best['trade_levels']  # Already calculated in scanner
                    
                    # Calculate position size with 10% risk for $100-200 P&L
                    stats = paper_trader.get_stats()
                    lot_size = calculate_position_size(
                        balance=stats['balance'],
                        risk_per_trade=0.01,  # 1% risk
                        entry=trade_levels['entry_price'],
                        stop=trade_levels['stop_loss']
                    )
                    
                    # Execute trade
                    trade = paper_trader.open_trade(
                        symbol=best['symbol'],
                        direction=trade_levels['direction'],
                        entry_price=trade_levels['entry_price'],
                        stop_loss=trade_levels['stop_loss'],
                        target_price=trade_levels['target_price'],
                        lot_size=lot_size,
                        score=best.get('score', 0.0)
                    )
                    
                    self.trade_count += 1
                    self.last_trade_time = datetime.now().isoformat()
                    print(f"[Auto-Trade] ✅ Executed {trade_levels['direction']} on {best['symbol']} | Lot: {lot_size} | Score: {best['score']:.1f}")
                else:
                    if best:
                        print(f"[Auto-Trade] ⚠️  Opportunity below threshold: {best['symbol']} (Score: {best['score']:.1f}/100, need 70+)")
                    else:
                        print(f"[Auto-Trade] No opportunities found in current scan")
                
            except Exception as e:
                print(f"[Auto-Trade] Error in trading loop: {e}")
            
            # Wait before next scan
            print(f"[Auto-Trade] Waiting {self.scan_interval} seconds until next scan...")
            await asyncio.sleep(self.scan_interval)
    
    async def start(self):
        """Start auto-trading."""
        if self.is_running:
            return {"status": "already_running", "message": "Auto-trading is already running"}
        
        self.is_running = True
        self.task = asyncio.create_task(self.trading_loop())
        return {
            "status": "started",
            "message": "Auto-trading started successfully",
            "scan_interval": self.scan_interval
        }
    
    async def stop(self):
        """Stop auto-trading."""
        if not self.is_running:
            return {"status": "not_running", "message": "Auto-trading is not running"}
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        return {
            "status": "stopped",
            "message": "Auto-trading stopped successfully",
            "total_trades": self.trade_count
        }
    
    def get_status(self):
        """Get current auto-trading status."""
        return {
            "is_running": self.is_running,
            "last_trade_time": self.last_trade_time,
            "trade_count": self.trade_count,
            "scan_interval": self.scan_interval
        }

# Global auto-trading service instance
auto_trader = AutoTradingService()
