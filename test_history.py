
import sys
import os

# Add backend to path
sys.path.append(os.getcwd() + "/backend")

# Mock data_loader before importing paper_trader to avoid yfinance/API calls if needed
# But paper_trader imports get_live_price from data_loader.
# If we just want to test logic, we can try to proceed. 
# get_live_price might hit network, but we are just instantiating and checking valid history.

try:
    from bot.paper_trader import PaperTradingEngine, PaperTrade
    
    # Create engine (will load from file if exists, but we can also mock it)
    engine = PaperTradingEngine()
    
    # Artificial inject trades if empty (for testing)
    # But current file has trades.
    
    # Test getting history
    history = engine.get_trade_history(limit=0)
    print(f"Total history length with limit=0: {len(history)}")
    
    history_limit = engine.get_trade_history(limit=5)
    print(f"History length with limit=5: {len(history_limit)}")
    
    assert len(history) >= len(history_limit)
    print("Verification successful: limit=0 returns full or larger set.")
    
except Exception as e:
    print(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()
