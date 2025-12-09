import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error

class ForexPredictor:
    def __init__(self):
        # Improved model with better hyperparameters
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        # Enhanced feature set with momentum, volume, and rolling statistics
        self.feature_cols = [
            # Original indicators
            'rsi', 'macd', 'macd_signal', 'macd_diff', 'bb_high', 'bb_low', 'bb_mid', 'atr', 'sma_50', 'ema_20',
            # New momentum features
            'price_momentum_3', 'price_momentum_5', 'price_momentum_10',
            # Rolling statistics
            'rolling_std_5', 'rolling_std_10',
            # Volume features
            'volume_sma_10', 'volume_ratio',
            # Volatility-adjusted returns
            'volatility_adj_return',
            # Trend strength
            'ema_distance', 'sma_distance'
        ]

    def prepare_data(self, df: pd.DataFrame):
        """
        Prepare data for training/prediction with enhanced features.
        Create target: 1 if next close > current close, else 0.
        """
        data = df.copy()
        
        # Add momentum features (% change over different periods)
        data['price_momentum_3'] = data['close'].pct_change(3) * 100
        data['price_momentum_5'] = data['close'].pct_change(5) * 100
        data['price_momentum_10'] = data['close'].pct_change(10) * 100
        
        # Add rolling volatility
        data['rolling_std_5'] = data['close'].rolling(window=5).std()
        data['rolling_std_10'] = data['close'].rolling(window=10).std()
        
        # Add volume features
        data['volume_sma_10'] = data['volume'].rolling(window=10).mean()
        data['volume_ratio'] = data['volume'] / (data['volume_sma_10'] + 1e-10)
        
        # Volatility-adjusted returns
        returns = data['close'].pct_change()
        volatility = returns.rolling(window=10).std()
        data['volatility_adj_return'] = returns / (volatility + 1e-10)
        
        # Distance from moving averages (trend strength)
        data['ema_distance'] = (data['close'] - data['ema_20']) / data['ema_20'] * 100
        data['sma_distance'] = (data['close'] - data['sma_50']) / data['sma_50'] * 100
        
        # Clean up data
        data.dropna(inplace=True)
        
        # Create target
        data['target'] = (data['close'].shift(-1) > data['close']).astype(int)
        
        # Drop last row as it has no target
        data = data[:-1]
        
        return data

    def train(self, df: pd.DataFrame):
        """
        Train the model with enhanced validation and recent data weighting.
        """
        data = self.prepare_data(df)
        
        if len(data) < 50:
            print("Not enough data for training after processing.")
            return 0.5 # Return dummy accuracy
            
        X = data[self.feature_cols].values
        y = data['target'].astype(int).values
        
        # Create sample weights - recent data is more important
        # Use exponential decay: more recent samples get higher weight
        n_samples = len(X)
        decay_rate = 0.01
        weights = np.exp(decay_rate * np.arange(n_samples))
        weights = weights / weights.sum() * n_samples  # Normalize
        
        # Time-based split (no shuffle) - train on older, test on recent
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        sample_weights = weights[:split_idx]
        
        # Train with sample weights
        self.model.fit(X_train, y_train, sample_weight=sample_weights)
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        # print(f"Model Accuracy: {accuracy:.4f}")
        
        return accuracy

    def predict_next_movement(self, df: pd.DataFrame):
        """
        Predict the movement for the next candle based on the latest data.
        Returns: (prediction (0 or 1), probability)
        """
        # Prepare the full dataset to get engineered features
        prepared_data = self.prepare_data(df)
        
        # Add back the last row with a dummy target (we'll remove it)
        last_row_original = df.iloc[[-1]].copy()
        
        # Recalculate features for the very last row
        # Use the prepared data's feature engineering approach
        if len(prepared_data) > 0:
            # Get the last row with all features computed
            last_row = prepared_data.iloc[[-1]][self.feature_cols]
        else:
            # Fallback if preparation fails
            last_row = df.iloc[[-1]][self.feature_cols]
        
        # Handle NaNs if any
        last_row = last_row.ffill().bfill()
        
        # If still has NaNs, fill with 0
        last_row = last_row.fillna(0)
        
        prediction = self.model.predict(last_row)[0]
        probability = self.model.predict_proba(last_row)[0][prediction]
        
        return prediction, probability

class ForexRegressor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.feature_cols = ['open', 'high', 'low', 'close', 'volume', 'rsi', 'macd', 'atr']
        
    def prepare_data(self, df: pd.DataFrame):
        data = df.copy()
        data.dropna(inplace=True)
        # Target is next close price
        data['target_close'] = data['close'].shift(-1)
        data = data[:-1]
        return data

    def train(self, df: pd.DataFrame):
        data = self.prepare_data(df)
        if len(data) < 10: return
        
        X = data[self.feature_cols].values
        y = data['target_close'].values
        
        self.model.fit(X, y)
        
    def predict_next_price(self, df: pd.DataFrame) -> float:
        last_row = df.iloc[[-1]][self.feature_cols].ffill()
        return self.model.predict(last_row)[0]
        
    def predict_future_path(self, df: pd.DataFrame, steps: int = 10, interval: str = "15m") -> list:
        """
        Predict the next 'steps' candles recursively.
        Returns a list of dicts: [{'time': ..., 'open': ..., 'high': ..., 'low': ..., 'close': ...}]
        """
        future_path = []
        current_df = df.copy()
        
        # Get last known time
        last_time = current_df.iloc[-1]['datetime'] if 'datetime' in current_df.columns else pd.Timestamp.now()
        
        for i in range(steps):
            # Predict next close
            next_close = self.predict_next_price(current_df)
            
            # Estimate other OHLC values based on ATR (simplified)
            last_close = current_df.iloc[-1]['close']
            atr = current_df.iloc[-1].get('atr', last_close * 0.001)
            
            # Simple logic for candle shape
            if next_close > last_close:
                next_open = last_close
                next_high = next_close + (atr * 0.2)
                next_low = next_open - (atr * 0.1)
            else:
                next_open = last_close
                next_high = next_open + (atr * 0.1)
                next_low = next_close - (atr * 0.2)
                
            # Create next candle dict
            # Parse interval string for Timedelta (e.g. "15m", "1h", "1d")
            # Simple mapping for common intervals
            delta = pd.Timedelta(interval)
            next_time = last_time + (delta * (i+1))
            
            next_candle = {
                'datetime': next_time,
                'open': next_open,
                'high': next_high,
                'low': next_low,
                'close': next_close,
                'volume': 0,
                'rsi': current_df.iloc[-1]['rsi'], # Carry forward for simplicity
                'macd': current_df.iloc[-1]['macd'],
                'atr': atr
            }
            
            future_path.append({
                'time': int(next_time.timestamp()), # For lightweight-charts (int seconds)
                'open': next_open,
                'high': next_high,
                'low': next_low,
                'close': next_close
            })
            
            # Append to df for next recursion (simplified, normally need to re-calc indicators)
            # For true recursion we'd need to re-calc indicators, but that's heavy.
            # We'll just append the row with carried-over indicators for the Regressor to have input.
            new_row = pd.DataFrame([next_candle])
            current_df = pd.concat([current_df, new_row], ignore_index=True)
            
        return future_path
