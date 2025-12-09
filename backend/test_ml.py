from bot.data_loader import fetch_forex_data
from bot.indicators import add_technical_indicators
from bot.ml_model import ForexPredictor
from bot.pattern_recognition import identify_patterns

def test_ml_system():
    symbol = "EURUSD"
    print(f"Testing ML System for {symbol}...")
    
    # 1. Fetch Data
    df = fetch_forex_data(symbol, period="2y", interval="1d") # More data for training
    if df.empty:
        print("Error: No data.")
        return
        
    # 2. Add Indicators
    df = add_technical_indicators(df)
    df.dropna(inplace=True)
    
    # 3. Identify Patterns
    df = identify_patterns(df)
    print("Patterns identified.")
    print(df[['datetime', 'pattern_doji', 'pattern_hammer']].tail())
    
    # 4. Train Model
    predictor = ForexPredictor()
    print("Training model...")
    accuracy = predictor.train(df)
    
    # 5. Predict Next Movement
    prediction, prob = predictor.predict_next_movement(df)
    direction = "UP" if prediction == 1 else "DOWN"
    print(f"Prediction for next day: {direction} (Probability: {prob:.2f})")

if __name__ == "__main__":
    test_ml_system()
