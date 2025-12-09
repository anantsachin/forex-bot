from bot.data_loader import fetch_forex_data
import pandas as pd

def test_fetch():
    symbols = ["EURUSD", "GBPUSD", "GC=F", "BTC-USD"]
    for symbol in symbols:
        print(f"Testing {symbol}...")
        try:
            df = fetch_forex_data(symbol, period="1y", interval="1d")
            print(f"Result for {symbol}: {len(df)} rows")
            if not df.empty:
                print(df.tail())
            else:
                print("Empty DataFrame")
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

if __name__ == "__main__":
    test_fetch()
