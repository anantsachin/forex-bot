import sys
import os
# Add current directory to path so we can resolve 'bot' package
sys.path.append(os.getcwd())

import time
from bot.paper_trader import PaperTradingEngine, PaperTrade

# Setup
TEST_FILE = "test_trades.json"
# Ensure we clean up previous runs
# paper_trader saves to backend/data_file based on absolute path logic we added.
# We need to be careful where we look for it.
# Our new logic: status_file_path = os.path.join(project_root, "backend", data_file)
# project_root is derived from __file__ in paper_trader.py.

print(">>> Testing Persistence...")
# 1. Create engine and open trade
print("Initializing Engine 1...")
engine1 = PaperTradingEngine(data_file=TEST_FILE)
# Clean previous test file if exists
if os.path.exists(engine1.data_file):
    os.remove(engine1.data_file)
    engine1 = PaperTradingEngine(data_file=TEST_FILE) # Re-init

engine1.reset_account() # Ensure fresh
trade = engine1.open_trade("EURUSD", "BUY", 1.0500, 1.0400, 1.0600, 0.1, score=85)
trade_id = trade.trade_id
print(f"Opened trade {trade_id}")

# 2. Create new engine instance (simulating restart)
print("Initializing Engine 2 (Simulated Restart)...")
engine2 = PaperTradingEngine(data_file=TEST_FILE)
if len(engine2.trades) >= 1 and engine2.trades[-1].trade_id == trade_id:
    print("PASS: Trade persisted across instances.")
else:
    print(f"FAIL: Expected trade not found. Trades: {len(engine2.trades)}")

print("\n>>> Testing Cooldown...")
# 3. Test Cooldown
# Trade is currently OPEN. Cooldown should be active.
is_cooldown = engine2.is_trade_cooldown("EURUSD", "BUY", minutes=10)
if is_cooldown:
    print("PASS: Cooldown active for open trade.")
else:
    print("FAIL: Cooldown NOT active for open trade.")

# Close the trade
print("Closing trade...")
engine2.close_trade(trade_id, 1.0550, "CLOSED_WIN")

# Check cooldown after close
is_cooldown_after = engine2.is_trade_cooldown("EURUSD", "BUY", minutes=10)
if is_cooldown_after:
    print("PASS: Cooldown active after close.")
else:
    print(f"FAIL: Cooldown NOT active after close.")

# Check different symbol
is_cooldown_mod = engine2.is_trade_cooldown("GBPUSD", "BUY", minutes=10)
if not is_cooldown_mod:
    print("PASS: Cooldown NOT active for different symbol.")
else:
    print("FAIL: Cooldown active for different symbol!")

# Cleanup
if os.path.exists(engine1.data_file):
    os.remove(engine1.data_file)
print("\nDone.")
