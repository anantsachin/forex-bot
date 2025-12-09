import google.generativeai as genai
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBx2kQCcRQYe0y8E1CogoV8FAYxyq2aDp8"
genai.configure(api_key=GEMINI_API_KEY)

class ChatBot:
    def __init__(self, feedback_file: str = "chatbot_feedback.json"):
        self.feedback_file = feedback_file
        
        # Try different model names in order of preference
        model_names = [
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'models/gemini-2.0-flash-exp',
            'models/gemini-1.5-flash'
        ]
        
        self.model = None
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"Successfully initialized model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to initialize {model_name}: {e}")
                continue
        
        if self.model is None:
            # List available models
            try:
                print("Available models:")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        print(f"  - {m.name}")
                # Use the first available model
                available_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                if available_models:
                    self.model = genai.GenerativeModel(available_models[0].name)
                    print(f"Using model: {available_models[0].name}")
            except Exception as e:
                print(f"Error listing models: {e}")
                raise Exception("Could not initialize any Gemini model")
        
        self.conversation_history: List[Dict] = []
        self.feedback_data: List[Dict] = []
        self.system_context = """You are an AI trading assistant for a Forex trading bot. 
You help users understand trading strategies, market analysis, and bot performance.
Be concise, accurate, and helpful. Focus on forex trading, technical analysis, and risk management."""
        
        # Load existing feedback
        self._load_feedback()
    
    def _load_feedback(self):
        """Load feedback data from file."""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    self.feedback_data = json.load(f)
            except Exception as e:
                print(f"Error loading feedback: {e}")
                self.feedback_data = []
    
    def _save_feedback(self):
        """Save feedback data to file."""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            print(f"Error saving feedback: {e}")
    
    def get_response(self, user_message: str, trading_data: Optional[Dict] = None) -> Dict:
        """Get response from Gemini AI with trading context."""
        try:
            # Build context from feedback
            context = self.system_context
            
            # Add trading data to context if available
            if trading_data:
                context += "\n\n=== CURRENT TRADING DATA ===\n"
                
                # Add stats
                if 'stats' in trading_data:
                    stats = trading_data['stats']
                    context += f"\nAccount Balance: ${stats.get('balance', 0):,.2f}"
                    context += f"\nTotal P&L: ${stats.get('total_pnl', 0):,.2f}"
                    context += f"\nFloating P&L: ${stats.get('total_floating_pnl', 0):,.2f}"
                    context += f"\nWin Rate: {stats.get('win_rate', 0)}%"
                    context += f"\nTotal Trades: {stats.get('total_trades', 0)}"
                    context += f"\nMax Risk/Trade: ${stats.get('max_risk_per_trade', 0):,.2f}"
                    context += f"\nTotal Daily Risk: ${stats.get('total_daily_risk', 0):,.2f}\n"
                
                # Add active trades
                if 'active_trades' in trading_data and trading_data['active_trades']:
                    context += f"\nActive Trades ({len(trading_data['active_trades'])}):\n"
                    for trade in trading_data['active_trades']:
                        context += f"  - {trade['symbol']} {trade['direction']}: "
                        context += f"Entry {trade['entry_price']}, Current {trade.get('current_price', 'N/A')}, "
                        context += f"SL {trade['stop_loss']}, TP {trade['target_price']}, "
                        context += f"P&L: ${trade.get('floating_pnl', 0):.2f} ({trade.get('pnl_percentage', 0):.2f}%), "
                        context += f"Risk: ${trade.get('risk_amount', 0):.2f}, Score: {trade.get('score', 0)}\n"
                else:
                    context += "\nNo active trades currently.\n"
                
                # Add recent trade history
                if 'history' in trading_data and trading_data['history']:
                    context += f"\nRecent Trade History (last {min(5, len(trading_data['history']))}):\n"
                    for trade in trading_data['history'][:5]:
                        context += f"  - {trade['symbol']} {trade['direction']}: "
                        context += f"P&L ${trade.get('pnl', 0):.2f}, Status: {trade['status']}, "
                        context += f"Score: {trade.get('score', 0)}\n"
            
            # Add positive feedback examples
            if self.feedback_data:
                positive_examples = [f for f in self.feedback_data if f.get('rating') == 'positive']
                if positive_examples:
                    context += "\n\nLearn from these good responses:\n"
                    for example in positive_examples[-3:]:  # Last 3 positive examples
                        context += f"Q: {example['user_message']}\nA: {example['bot_response']}\n"
            
            # Create prompt with context
            full_prompt = f"{context}\n\nUser: {user_message}\nAssistant:"
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            bot_response = response.text
            
            # Store in conversation history
            message_id = f"msg_{int(datetime.now().timestamp() * 1000)}"
            conversation_entry = {
                "id": message_id,
                "user_message": user_message,
                "bot_response": bot_response,
                "timestamp": datetime.now().isoformat(),
                "rating": None
            }
            self.conversation_history.append(conversation_entry)
            
            return {
                "id": message_id,
                "response": bot_response,
                "timestamp": conversation_entry["timestamp"]
            }
        except Exception as e:
            print(f"Error getting response: {e}")
            return {
                "id": "error",
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "timestamp": datetime.now().isoformat()
            }
    
    def add_feedback(self, message_id: str, rating: str, comment: Optional[str] = None):
        """Add feedback for a specific message."""
        # Find the message in history
        for msg in self.conversation_history:
            if msg['id'] == message_id:
                msg['rating'] = rating
                msg['comment'] = comment
                
                # Add to feedback data
                feedback_entry = {
                    "message_id": message_id,
                    "user_message": msg['user_message'],
                    "bot_response": msg['bot_response'],
                    "rating": rating,
                    "comment": comment,
                    "timestamp": datetime.now().isoformat()
                }
                self.feedback_data.append(feedback_entry)
                self._save_feedback()
                return True
        return False
    
    def train_on_feedback(self) -> Dict:
        """Process feedback to improve responses."""
        positive_count = sum(1 for f in self.feedback_data if f.get('rating') == 'positive')
        negative_count = sum(1 for f in self.feedback_data if f.get('rating') == 'negative')
        
        # Update system context based on feedback
        if positive_count > 0:
            self.system_context += f"\n\nNote: Users have provided {positive_count} positive feedback on similar responses."
        
        return {
            "status": "success",
            "total_feedback": len(self.feedback_data),
            "positive": positive_count,
            "negative": negative_count,
            "message": f"Training completed. Processed {len(self.feedback_data)} feedback entries."
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

# Global chatbot instance
chatbot = ChatBot()
