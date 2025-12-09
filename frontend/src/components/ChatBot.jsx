import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, ThumbsUp, ThumbsDown, Brain, Trash2 } from 'lucide-react';
import axios from 'axios';

const API_URL = '/api';

const ChatBot = () => {
    const [messages, setMessages] = useState([
        { id: 'welcome', text: "Hello! I'm your Forex AI Assistant powered by Gemini. How can I help you today?", sender: 'bot', rating: null }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [trainingStatus, setTrainingStatus] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMsg = { id: `user_${Date.now()}`, text: input, sender: 'user' };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post(`${API_URL}/chat`, { message: input });
            const botMsg = {
                id: response.data.id,
                text: response.data.response,
                sender: 'bot',
                rating: null,
                timestamp: response.data.timestamp
            };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMsg = {
                id: `error_${Date.now()}`,
                text: "Sorry, I encountered an error. Please try again.",
                sender: 'bot',
                rating: null
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    const handleFeedback = async (messageId, rating) => {
        try {
            await axios.post(`${API_URL}/chat/feedback`, {
                message_id: messageId,
                rating: rating
            });

            // Update message rating in UI
            setMessages(prev => prev.map(msg =>
                msg.id === messageId ? { ...msg, rating } : msg
            ));
        } catch (error) {
            console.error('Error submitting feedback:', error);
        }
    };

    const handleTrain = async () => {
        try {
            setTrainingStatus('training');
            const response = await axios.post(`${API_URL}/chat/train`);
            setTrainingStatus('success');
            alert(`Training completed!\n\n${response.data.message}\nPositive: ${response.data.positive}\nNegative: ${response.data.negative}`);
            setTimeout(() => setTrainingStatus(null), 3000);
        } catch (error) {
            console.error('Error training chatbot:', error);
            setTrainingStatus('error');
            setTimeout(() => setTrainingStatus(null), 3000);
        }
    };

    const handleClearHistory = async () => {
        if (!confirm('Are you sure you want to clear the chat history?')) return;

        try {
            await axios.delete(`${API_URL}/chat/history`);
            setMessages([
                { id: 'welcome', text: "Hello! I'm your Forex AI Assistant powered by Gemini. How can I help you today?", sender: 'bot', rating: null }
            ]);
        } catch (error) {
            console.error('Error clearing history:', error);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-800 rounded-2xl border border-gray-700 shadow-xl overflow-hidden">
            <div className="p-4 bg-gray-700/50 border-b border-gray-700 flex items-center justify-between">
                <div className="flex items-center">
                    <Bot className="w-6 h-6 text-blue-400 mr-2" />
                    <h3 className="font-semibold text-white">Gemini AI Assistant</h3>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={handleTrain}
                        disabled={trainingStatus === 'training'}
                        className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm font-medium transition-colors ${trainingStatus === 'training' ? 'bg-yellow-600/50 cursor-not-allowed' :
                                trainingStatus === 'success' ? 'bg-green-600 text-white' :
                                    trainingStatus === 'error' ? 'bg-red-600 text-white' :
                                        'bg-purple-600 hover:bg-purple-700 text-white'
                            }`}
                    >
                        <Brain className="w-4 h-4" />
                        {trainingStatus === 'training' ? 'Training...' :
                            trainingStatus === 'success' ? 'Trained!' :
                                trainingStatus === 'error' ? 'Error' : 'Train'}
                    </button>
                    <button
                        onClick={handleClearHistory}
                        className="p-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-colors"
                        title="Clear chat history"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className="flex flex-col max-w-[80%]">
                            <div className={`p-3 rounded-xl ${msg.sender === 'user'
                                ? 'bg-blue-600 text-white rounded-tr-none'
                                : 'bg-gray-700 text-gray-200 rounded-tl-none'
                                }`}>
                                {msg.text}
                            </div>
                            {msg.sender === 'bot' && msg.id !== 'welcome' && (
                                <div className="flex gap-2 mt-2 ml-2">
                                    <button
                                        onClick={() => handleFeedback(msg.id, 'positive')}
                                        className={`p-1 rounded transition-colors ${msg.rating === 'positive'
                                                ? 'bg-green-600 text-white'
                                                : 'bg-gray-600/50 text-gray-400 hover:bg-green-600/20 hover:text-green-400'
                                            }`}
                                        title="Good response"
                                    >
                                        <ThumbsUp className="w-3 h-3" />
                                    </button>
                                    <button
                                        onClick={() => handleFeedback(msg.id, 'negative')}
                                        className={`p-1 rounded transition-colors ${msg.rating === 'negative'
                                                ? 'bg-red-600 text-white'
                                                : 'bg-gray-600/50 text-gray-400 hover:bg-red-600/20 hover:text-red-400'
                                            }`}
                                        title="Bad response"
                                    >
                                        <ThumbsDown className="w-3 h-3" />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700 text-gray-200 p-3 rounded-xl rounded-tl-none">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t border-gray-700 bg-gray-800">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask about trading strategies, market analysis..."
                        className="flex-1 bg-gray-700 border border-gray-600 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className={`p-2 rounded-lg transition-colors ${loading || !input.trim()
                                ? 'bg-gray-600 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700'
                            } text-white`}
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatBot;
