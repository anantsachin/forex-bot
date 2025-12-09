#!/usr/bin/env python3
"""Test new position sizing with updated parameters."""
import sys
sys.path.append('/Users/apple/Desktop/Personal Projects/trade bots/forexbotgemini/backend')

from bot.trade_calculator import calculate_position_size

# Current balance
balance = 10000.00
risk_pct = 0.05  # 5% risk

# EUR/GBP trade example from user
entry = 0.87526
stop = 0.87443

lot_size = calculate_position_size(balance, risk_pct, entry, stop)

print(f"Balance: ${balance:,.2f}")
print(f"Risk %: {risk_pct * 100}%")
print(f"Risk Amount: ${balance * risk_pct:,.2f}")
print(f"\nTrade: EUR/GBP")
print(f"Entry: {entry}")
print(f"Stop: {stop}")
print(f"Stop Distance: {abs(entry - stop):.5f} ({abs(entry - stop) * 10000:.1f} pips)")
print(f"\n{'='*50}")
print(f"CALCULATED LOT SIZE: {lot_size}")
print(f"{'='*50}")

# Calculate expected P&L
units = lot_size * 100000
risk_per_unit = abs(entry - stop)
expected_risk = units * risk_per_unit

print(f"\nExpected risk at stop: ${expected_risk:.2f}")
print(f"Expected P&L at target (2:1 R/R): ${expected_risk * 2:.2f}")
