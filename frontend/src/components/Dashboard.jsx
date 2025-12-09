import React, { useState, useEffect } from 'react';
import Chart from './Chart';
import TradePanel from './TradePanel';
import axios from 'axios';
import { Play, Square, Scan, TrendingUp, TrendingDown, DollarSign, Activity, RotateCcw } from 'lucide-react';
import { motion } from 'framer-motion';

const API_URL = '/api';

const Dashboard = () => {
    const [symbol, setSymbol] = useState('EURUSD');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isRunning, setIsRunning] = useState(false);
    const [activeTrades, setActiveTrades] = useState([]);
    const [stats, setStats] = useState(null);
    const [runningBot, setRunningBot] = useState(false);

    const handleScan = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/scan`, {
                symbol: symbol,
                period: '1mo',
                interval: '15m'
            });

            // Check if opportunity was filtered
            if (response.data.status === 'filtered') {
                alert(`⚠️ ${symbol} Quality Check Failed\n\n${response.data.message}\n\nThe bot uses strict filters to ensure only high-quality trades:\n- Minimum 65% ML confidence\n- Minimum 60/100 opportunity score\n\nTry scanning other currency pairs to find better opportunities!`);
            }

            setData(response.data);
        } catch (error) {
            console.error('Error scanning market:', error);
            alert(`Failed to scan market. Error: ${error.message}\n\nEnsure backend is running on port 8000.`);
        } finally {
            setLoading(false);
        }
    };

    const handleRunBot = async () => {
        setRunningBot(true);
        try {
            const response = await axios.post(`${API_URL}/run_bot`);
            if (response.data.status === 'success') {
                alert(`Bot executed trade on ${response.data.trade.symbol}!\n\nScanned ${response.data.total_scanned} pairs.`);
                fetchTrades(); // Refresh trade data

                // Scan the symbol that was traded
                setSymbol(response.data.trade.symbol);
                await handleScan();
            }
        } catch (error) {
            console.error("Error running bot:", error);
            alert(`Failed to run bot: ${error.message}`);
        } finally {
            setRunningBot(false);
        }
    };

    const fetchTrades = async () => {
        try {
            const response = await axios.get(`${API_URL}/trades`);
            setActiveTrades(response.data.active_trades);
            setStats(response.data.stats);
        } catch (error) {
            console.error("Error fetching trades:", error);
        }
    };

    const handleCloseTrade = async (tradeId) => {
        try {
            await axios.post(`${API_URL}/close_trade/${tradeId}`);
            fetchTrades(); // Refresh
        } catch (error) {
            console.error("Error closing trade:", error);
            alert(`Failed to close trade: ${error.message}`);
        }
    };

    const handleReset = async () => {
        if (!confirm("Are you sure you want to reset your account balance to $10,000? This will clear all trade history.")) return;

        try {
            const response = await axios.post(`${API_URL}/reset`);
            if (response.data.status === 'success') {
                alert(response.data.message);
                // Immediately refresh all data
                await fetchTrades();
                await handleScan();
            }
        } catch (error) {
            console.error("Error resetting account:", error);
            alert(`Failed to reset account: ${error.message}`);
        }
    };

    useEffect(() => {
        handleScan();
        fetchTrades();

        // Poll for trade updates every 5 seconds
        const interval = setInterval(fetchTrades, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Top Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard
                    title="Balance"
                    value="$10,000.00"
                    icon={<DollarSign className="w-5 h-5 text-green-400" />}
                    trend="+0.0%"
                />
                <StatCard
                    title="Active Trades"
                    value="0"
                    icon={<Activity className="w-5 h-5 text-blue-400" />}
                    subtext="Waiting for signal"
                />
                <StatCard
                    title="Market Sentiment"
                    value={data ? (data.sentiment > 0 ? "Bullish" : data.sentiment < 0 ? "Bearish" : "Neutral") : "Loading..."}
                    icon={data?.sentiment > 0 ? <TrendingUp className="w-5 h-5 text-green-400" /> : <TrendingDown className="w-5 h-5 text-red-400" />}
                    trend={data?.sentiment !== undefined ? `${(data.sentiment * 100).toFixed(0)}%` : "0%"}
                />
                <StatCard
                    title="AI Prediction"
                    value={data ? data.prediction : "N/A"}
                    icon={<Scan className="w-5 h-5 text-purple-400" />}
                    subtext={data?.confidence !== undefined ? `Conf: ${(data.confidence * 100).toFixed(1)}%` : ""}
                />
            </div>

            {/* Main Chart Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
                {/* Chart Area */}
                <div className="lg:col-span-2 bg-gray-800 rounded-2xl p-4 border border-gray-700 shadow-xl flex flex-col">
                    <div className="flex justify-between items-center mb-4">
                        <div className="flex space-x-2">
                            <select
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value)}
                                className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                            >
                                <option value="EURUSD">EUR/USD</option>
                                <option value="GBPUSD">GBP/USD</option>
                                <option value="NZDJPY">NZD/JPY</option>
                                <option value="AUDJPY">AUD/JPY</option>
                                <option value="CADJPY">CAD/JPY</option>
                                <option value="EURJPY">EUR/JPY</option>
                                <option value="GBPCAD">GBP/CAD</option>
                                <option value="NZDCAD">NZD/CAD</option>
                                <option value="USDCHF">USD/CHF</option>
                                <option value="AUDUSD">AUD/USD</option>
                                <option value="EURGBP">EUR/GBP</option>
                                <option value="NZDUSD">NZD/USD</option>
                                <option value="GBPJPY">GBP/JPY</option>
                            </select>
                            <button
                                onClick={handleScan}
                                disabled={loading}
                                className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
                            >
                                <Scan className="w-4 h-4 mr-2" />
                                {loading ? "Scanning..." : "Scan"}
                            </button>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                onClick={handleReset}
                                className="flex items-center px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 rounded-lg transition-colors"
                                title="Reset Account Balance"
                            >
                                <RotateCcw className="w-4 h-4 mr-2" />
                                Reset
                            </button>
                            <button
                                onClick={handleRunBot}
                                disabled={runningBot}
                                className={`flex items-center px-4 py-2 rounded-lg transition-colors ${runningBot ? 'bg-gray-600 cursor-not-allowed' : 'bg-green-500/20 text-green-400 border border-green-500/50 hover:bg-green-500/30'}`}
                            >
                                <Play className="w-4 h-4 mr-2" />
                                {runningBot ? 'Running...' : 'Run Bot'}
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 bg-gray-900/50 rounded-xl overflow-hidden relative">
                        {loading ? (
                            <div className="h-full flex items-center justify-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                            </div>
                        ) : (
                            <Chart
                                data={data?.chart_data || []}
                                prediction={data?.prediction}
                                tradeLevels={data?.trade_levels}
                                predictedCandle={data?.predicted_candle}
                                futurePath={data?.future_path}
                                council={data?.council}
                            />
                        )}
                    </div>
                </div>

                {/* Right Panel: Analysis & Signals */}
                <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-xl flex flex-col space-y-6">
                    <h3 className="text-lg font-semibold text-gray-200">Market Analysis</h3>

                    {/* Technical Indicators */}
                    <div className="space-y-4">
                        <div className="p-4 bg-gray-700/30 rounded-xl border border-gray-700">
                            <h4 className="text-sm font-medium text-gray-400 mb-3">Technical Indicators</h4>
                            <div className="grid grid-cols-2 gap-4">
                                <IndicatorItem label="RSI (14)" value={data?.indicators?.rsi?.toFixed(2)} status={data?.indicators?.rsi > 70 ? 'Overbought' : data?.indicators?.rsi < 30 ? 'Oversold' : 'Neutral'} />
                                <IndicatorItem label="MACD" value={data?.indicators?.macd?.toFixed(4)} status={data?.indicators?.macd > 0 ? 'Bullish' : 'Bearish'} />
                                <IndicatorItem label="ATR" value={data?.indicators?.atr?.toFixed(4)} />
                            </div>
                        </div>

                        {/* Patterns */}
                        <div className="p-4 bg-gray-700/30 rounded-xl border border-gray-700">
                            <h4 className="text-sm font-medium text-gray-400 mb-3">Detected Patterns</h4>
                            <div className="space-y-2">
                                {data && Object.entries(data.patterns).map(([key, value]) => (
                                    value && (
                                        <div key={key} className="flex items-center justify-between text-sm">
                                            <span className="capitalize text-gray-300">{key.replace('_', ' ')}</span>
                                            <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded text-xs border border-yellow-500/30">Detected</span>
                                        </div>
                                    )
                                ))}
                                {data && !Object.values(data.patterns).some(Boolean) && (
                                    <div className="text-sm text-gray-500 italic">No significant patterns detected</div>
                                )}
                            </div>
                        </div>

                        {/* AI Insight */}
                        <div className="p-4 bg-gradient-to-br from-purple-900/20 to-blue-900/20 rounded-xl border border-purple-500/30">
                            <h4 className="text-sm font-medium text-purple-300 mb-2 flex items-center">
                                <Scan className="w-4 h-4 mr-2" />
                                AI Insight
                            </h4>
                            <p className="text-sm text-gray-300 leading-relaxed">
                                {data ? (
                                    data.prediction === 'UP'
                                        ? "Model predicts upward movement with " + (data.confidence !== undefined ? (data.confidence * 100).toFixed(0) : "0") + "% confidence. Consider LONG positions if price breaks resistance."
                                        : "Model predicts downward movement with " + (data.confidence !== undefined ? (data.confidence * 100).toFixed(0) : "0") + "% confidence. Consider SHORT positions if price breaks support."
                                ) : (
                                    "Waiting for market data..."
                                )}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Trade Panel Section */}
            <div className="mt-6">
                <TradePanel
                    activeTrades={activeTrades}
                    stats={stats}
                    onCloseTrade={handleCloseTrade}
                />
            </div>
        </div>
    );
};

const StatCard = ({ title, value, icon, trend, subtext }) => (
    <motion.div
        whileHover={{ y: -2 }}
        className="bg-gray-800 p-5 rounded-2xl border border-gray-700 shadow-lg"
    >
        <div className="flex justify-between items-start mb-2">
            <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
            <div className="p-2 bg-gray-700/50 rounded-lg">{icon}</div>
        </div>
        <div className="flex items-end justify-between">
            <div>
                <div className="text-2xl font-bold text-white">{value}</div>
                {subtext && <div className="text-xs text-gray-500 mt-1">{subtext}</div>}
            </div>
            {trend && (
                <div className={`text-sm font-medium ${trend.includes('+') ? 'text-green-400' : 'text-red-400'}`}>
                    {trend}
                </div>
            )}
        </div>
    </motion.div>
);

const IndicatorItem = ({ label, value, status }) => (
    <div>
        <div className="text-xs text-gray-500">{label}</div>
        <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-white">{value || '-'}</span>
            {status && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${status === 'Overbought' || status === 'Bearish' ? 'bg-red-500/20 text-red-400' :
                    status === 'Oversold' || status === 'Bullish' ? 'bg-green-500/20 text-green-400' :
                        'bg-gray-600/30 text-gray-400'
                    }`}>
                    {status}
                </span>
            )}
        </div>
    </div>
);

export default Dashboard;
