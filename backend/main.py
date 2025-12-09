from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import asyncio
from contextlib import asynccontextmanager
from bot.data_loader import fetch_forex_data, get_live_price
from bot.indicators import add_technical_indicators
from bot.ml_model import ForexPredictor
from bot.pattern_recognition import identify_patterns
from bot.fundamental_analysis import get_news_sentiment
from bot.backtest import Backtester
from bot.opportunity_scanner import scan_all_pairs, get_best_opportunity
from bot.trade_calculator import calculate_trade_levels, predict_next_candle, calculate_position_size
from bot.paper_trader import paper_trader
from bot.chatbot_service import chatbot
from bot.auto_trading_service import auto_trader

# Background task for monitoring trades
async def monitor_trades():
    """Background task to check and close trades when SL/TP is hit."""
    while True:
        try:
            # Get current prices for all active trades
            if paper_trader.active_trades:
                current_prices = {}
                for trade_id, trade in list(paper_trader.active_trades.items()):
                    try:
                        current_prices[trade.symbol] = get_live_price(trade.symbol)
                    except Exception as e:
                        print(f"Error fetching price for {trade.symbol}: {e}")
                
                # Check and update trades
                paper_trader.check_and_update_trades(current_prices)
        except Exception as e:
            print(f"Error in monitor_trades: {e}")
        
        # Wait 5 seconds before next check
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task
    task = asyncio.create_task(monitor_trades())
    yield
    # Cancel task on shutdown
    task.cancel()

app = FastAPI(title="Forex Trading Bot API", lifespan=lifespan)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (simplified for demo)
current_symbol = "EURUSD"
predictor = ForexPredictor()

class ScanRequest(BaseModel):
    symbol: str
    period: str = "1mo"
    interval: str = "15m"

class BacktestRequest(BaseModel):
    symbol: str = "EURUSD"
    initial_balance: float = 10000

@app.get("/")
def read_root():
    return {"status": "online", "message": "Forex Trading Bot API is running. Access endpoints at /api/..."}

@app.get("/api/status")
def get_status():
    return {"status": "online", "message": "Forex Bot is running"}

@app.post("/api/scan")
def scan_market(request: ScanRequest):
    try:
        # Use the unified scanner which includes Council and Regressor
        from bot.opportunity_scanner import scan_single_pair
        
        # Fetch chart data first (always needed for display)
        df = fetch_forex_data(request.symbol, period=request.period, interval=request.interval)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {request.symbol}")
        
        # Ensure data is sorted by time
        df = df.sort_values('datetime')
        
        # Convert dataframe to chart data format
        # Using Unix timestamps (seconds) for intraday data
        chart_data = []
        for _, row in df.tail(200).iterrows():  # Last 200 candles
            chart_data.append({
                "time": int(row['datetime'].timestamp()),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row.get('volume', 0))
            })
        
        # Now scan for opportunity
        
        result = scan_single_pair(request.symbol)
        
        if not result:
            # Opportunity was filtered out due to low quality
            # Return a helpful message instead of 404
            return {
                "status": "filtered",
                "message": f"Opportunity filtered out - does not meet quality thresholds (min 65% confidence, min 60 score)",
                "symbol": request.symbol,
                "current_price": float(df.iloc[-1]['close']) if not df.empty else 0,
                "prediction": "N/A",
                "confidence": 0,
                "sentiment": 0,
                "score": 0,
                "council": {"consensus": "NEUTRAL", "strength": 0, "votes": {}},
                "future_path": [],
                "trade_levels": {
                    "entry_price": 0,
                    "stop_loss": 0,
                    "target_price": 0,
                    "direction": "NONE",
                    "risk_reward": 0,
                    "atr": 0
                },
                "indicators": {"rsi": 50, "macd": 0, "atr": 0},
                "patterns": {},
                "chart_data": chart_data  # Include chart data even when filtered
            }
            
        # Opportunity found - use chart data we fetched
        response = {
            "symbol": result['symbol'],
            "current_price": result['current_price'],
            "prediction": result['prediction'],
            "confidence": result['confidence'] / 100.0, # Frontend expects 0-1
            "sentiment": (result['score'] - 50) / 50.0, # Approx mapping 0-100 to -1 to 1
            "score": result['score'],
            "council": result['council'],
            "future_path": result['future_path'],
            "trade_levels": result['trade_levels'],
            "indicators": result['indicators'],
            "patterns": result.get('patterns', {}),
            "chart_data": chart_data  # Use chart data we fetched
        }
        
        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest")
def run_backtest(request: BacktestRequest):
    try:
        df = fetch_forex_data(request.symbol, period="1y", interval="1d")
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
            
        backtester = Backtester(initial_balance=request.initial_balance)
        report = backtester.run(df)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/live_price/{symbol}")
def live_price(symbol: str):
    try:
        price = get_live_price(symbol)
        return {"symbol": symbol, "price": price}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run_bot")
def run_bot():
    """Scan all pairs, find best opportunity, and execute paper trade."""
    try:
        print("Running bot - scanning all pairs...")
        
        # Scan all pairs and get top 3 opportunities
        opportunities = scan_all_pairs(max_workers=5)
        top_3 = opportunities[:3] if len(opportunities) >= 3 else opportunities
        
        if not opportunities:
            return {"status": "no_opportunities", "message": "No valid opportunities found"}
        
        # Get active trade symbols
        active_symbols = [trade.symbol for trade in paper_trader.active_trades.values()]
        
        # Find best opportunity that isn't already active
        best = None
        for opp in opportunities:
            if opp['symbol'] not in active_symbols:
                best = opp
                break
        
        if not best:
            return {"status": "no_new_opportunities", "message": "All good opportunities already traded"}
        
        # Calculate position size (risk 2% of balance)
        trade_levels = best['trade_levels']
        lot_size = calculate_position_size(
            balance=paper_trader.balance,
            risk_per_trade=0.02,
            entry=trade_levels['entry_price'],
            stop=trade_levels['stop_loss']
        )
        
        # Execute paper trade
        trade = paper_trader.open_trade(
            symbol=best['symbol'],
            direction=trade_levels['direction'],
            entry_price=trade_levels['entry_price'],
            stop_loss=trade_levels['stop_loss'],
            target_price=trade_levels['target_price'],
            lot_size=lot_size,
            score=best.get('score', 0.0) # Pass the score
        )
        
        return {
            "status": "success",
            "trade": trade.to_dict(),
            "top_opportunities": top_3,
            "all_opportunities": opportunities,
            "total_scanned": len(opportunities)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades")
def get_trades():
    """Get active trades and trading statistics."""
    try:
        return {
            "active_trades": paper_trader.get_active_trades(),
            "recent_history": paper_trader.get_trade_history(limit=20),
            "stats": paper_trader.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/close_trade/{trade_id}")
def close_trade_manual(trade_id: str):
    """Manually close a trade."""
    try:
        # Get current price for the symbol
        if trade_id not in paper_trader.active_trades:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        trade = paper_trader.active_trades[trade_id]
        current_price = get_live_price(trade.symbol)
        
        paper_trader.close_trade(trade_id, current_price, "CLOSED_MANUAL")
        
        return {"status": "success", "trade_id": trade_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
def reset_account():
    """Reset the paper trading account."""
    try:
        paper_trader.reset_account()
        return {"status": "success", "message": "Account reset to $10,000"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chatbot endpoints
class ChatMessage(BaseModel):
    message: str

class FeedbackRequest(BaseModel):
    message_id: str
    rating: str  # 'positive' or 'negative'
    comment: Optional[str] = None

@app.post("/api/chat")
def chat(request: ChatMessage):
    """Send message to chatbot and get response with trading context."""
    try:
        # Gather trading data for context
        trading_data = {
            'stats': paper_trader.get_stats(),
            'active_trades': paper_trader.get_active_trades(),
            'history': paper_trader.get_trade_history(limit=10)
        }
        
        response = chatbot.get_response(request.message, trading_data=trading_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/feedback")
def add_feedback(request: FeedbackRequest):
    """Add feedback for a chatbot response."""
    try:
        success = chatbot.add_feedback(request.message_id, request.rating, request.comment)
        if success:
            return {"status": "success", "message": "Feedback recorded"}
        else:
            raise HTTPException(status_code=404, detail="Message not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/train")
def train_chatbot():
    """Train chatbot on collected feedback."""
    try:
        result = chatbot.train_on_feedback()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history")
def get_chat_history():
    """Get conversation history."""
    try:
        history = chatbot.get_conversation_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/history")
def clear_chat_history():
    """Clear conversation history."""
    try:
        chatbot.clear_history()
        return {"status": "success", "message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Auto-trading endpoints
@app.post("/api/auto-trade/start")
async def start_auto_trading():
    """Start continuous auto-trading."""
    try:
        result = await auto_trader.start()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auto-trade/stop")
async def stop_auto_trading():
    """Stop continuous auto-trading."""
    try:
        result = await auto_trader.stop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auto-trade/status")
def get_auto_trade_status():
    """Get auto-trading status."""
    try:
        status = auto_trader.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
