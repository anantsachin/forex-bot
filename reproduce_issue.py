#!/usr/bin/env python3
"""Reproduce USD/JPY position sizing issue."""
import sys
sys.path.append('/Users/apple/Desktop/Personal Projects/trade bots/forexbotgemini/backend')

from bot.trade_calculator import calculate_position_size

# Parameters from user report
balance = 10000.00
risk_pct = 0.10  # 10% risk (as set previously)
entry = 155.233
stop = 154.95589

print(f"Testing USD/JPY Position Size Calculation")
print(f"Balance: ${balance}")
print(f"Risk: {risk_pct*100}% (${balance * risk_pct})")
print(f"Entry: {entry}")
print(f"Stop: {stop}")
print(f"Diff: {abs(entry-stop)}")

lot_size = calculate_position_size(balance, risk_pct, entry, stop)

print(f"\nCalculated Lot Size: {lot_size}")

# Manual verification of what this lot size means
units = lot_size * 100000
risk_per_unit_jpy = abs(entry - stop)
total_risk_jpy = units * risk_per_unit_jpy
total_risk_usd = total_risk_jpy / entry # Approx

print(f"\nVerification:")
print(f"Units: {units}")
print(f"Risk (JPY): {total_risk_jpy:.2f}")
print(f"Risk (USD): ${total_risk_usd:.2f}")
