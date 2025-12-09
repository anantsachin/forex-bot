from bot.data_loader import fetch_forex_data
from bot.backtest import Backtester

def test_backtest():
    symbol = "EURUSD"
    print(f"Running backtest for {symbol}...")
    
    # Fetch data
    df = fetch_forex_data(symbol, period="1y", interval="1d")
    if df.empty:
        print("Error: No data.")
        return
        
    backtester = Backtester(initial_balance=10000)
    report = backtester.run(df)
    
    print("\n--- Backtest Report ---")
    print(f"Final Balance: ${report.get('final_balance', 0):.2f}")
    print(f"Total Return: {report.get('total_return_pct', 0):.2f}%")
    print(f"Win Rate: {report.get('win_rate', 0):.2f}%")
    print(f"Max Drawdown: {report.get('max_drawdown', 0):.2f}%")
    print(f"Total Trades: {report.get('total_trades', 0)}")

if __name__ == "__main__":
    test_backtest()
