import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Pause, Bot, TrendingUp, Target, Shield, Clock, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';
import TradePanel from './TradePanel';
import Chart from './Chart';

const API_URL = '/api';

const AutoTrade = () => {
    const [autoMode, setAutoMode] = useState(false);
    const [scanning, setScanning] = useState(false);
    const [selectedOpportunity, setSelectedOpportunity] = useState(null);
    const [opportunities, setOpportunities] = useState([]);
    const [lastScan, setLastScan] = useState(null);
    const [activeTrades, setActiveTrades] = useState([]);
    const [stats, setStats] = useState(null);

    const startAutoTrade = async () => {
        setScanning(true);
        try {
            const response = await axios.post(`${API_URL}/run_bot`);
            if (response.data.status === 'success') {
                const opps = response.data.all_opportunities || [];
                setOpportunities(opps);
                if (opps.length > 0) {
                    setSelectedOpportunity(opps[0]);
                }
                setLastScan(new Date());
                fetchTrades();
            }
        } catch (error) {
            console.error("Auto-trade error:", error);
        } finally {
            setScanning(false);
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
            fetchTrades();
        } catch (error) {
            console.error("Error closing trade:", error);
        }
    };

    useEffect(() => {
        fetchTrades();
        const interval = setInterval(fetchTrades, 5000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        let interval;
        if (autoMode) {
            startAutoTrade(); // Initial run
            interval = setInterval(startAutoTrade, 60000); // Run every minute
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [autoMode]);

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 rounded-2xl p-6 border border-purple-500/30">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-purple-600 rounded-xl">
                            <Bot className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">AutoTrade System</h1>
                            <p className="text-gray-300 text-sm mt-1">
                                AI-powered automatic trading using patterns, indicators & machine learning
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setAutoMode(!autoMode)}
                            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${autoMode
                                ? 'bg-red-600 hover:bg-red-700 text-white'
                                : 'bg-green-600 hover:bg-green-700 text-white'
                                }`}
                        >
                            {autoMode ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                            {autoMode ? 'Stop Auto Mode' : 'Start Auto Mode'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Opportunities List */}
                <div className="lg:col-span-1 space-y-6">
                    {opportunities.length > 0 ? (
                        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 h-[600px] overflow-y-auto">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 sticky top-0 bg-gray-800 z-10 pb-2 border-b border-gray-700">
                                <TrendingUp className="w-5 h-5 text-green-400" />
                                Top Opportunities
                            </h3>
                            <div className="space-y-3">
                                {opportunities.map((opp, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        onClick={() => setSelectedOpportunity(opp)}
                                        className={`p-4 rounded-lg border cursor-pointer transition-all ${selectedOpportunity?.symbol === opp.symbol
                                            ? 'bg-blue-900/30 border-blue-500 ring-1 ring-blue-500'
                                            : 'bg-gray-700/50 border-gray-600 hover:bg-gray-700'
                                            }`}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-bold">{opp.symbol}</span>
                                            <span className={`font-bold ${opp.score >= 70 ? 'text-green-400' : 'text-yellow-400'}`}>
                                                {opp.score}
                                            </span>
                                        </div>
                                        <div className="flex justify-between text-sm text-gray-400">
                                            <span>{opp.prediction} ({opp.confidence}%)</span>
                                            <span>${opp.current_price?.toFixed(4)}</span>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 h-[200px] flex items-center justify-center text-gray-500">
                            <p>No opportunities found. Start scanning.</p>
                        </div>
                    )}
                </div>

                {/* Right Column: Chart & Analysis */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Chart Section */}
                    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 shadow-xl h-[600px]">
                        {selectedOpportunity ? (
                            <div className="h-full flex flex-col">
                                <div className="flex justify-between items-center mb-4 px-2">
                                    <div>
                                        <h3 className="text-xl font-bold flex items-center gap-2">
                                            {selectedOpportunity.symbol} Analysis
                                            <span className={`text-sm px-2 py-0.5 rounded ${selectedOpportunity.prediction === 'UP' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                                {selectedOpportunity.prediction}
                                            </span>
                                        </h3>
                                    </div>
                                    <div className="text-sm text-gray-400">
                                        Confidence: <span className="text-white font-bold">{selectedOpportunity.confidence}%</span>
                                    </div>
                                </div>
                                <div className="flex-1 min-h-0">
                                    <Chart
                                        data={selectedOpportunity.chart_data || []}
                                        prediction={selectedOpportunity.prediction}
                                        tradeLevels={selectedOpportunity.trade_levels}
                                        futurePath={selectedOpportunity.future_path}
                                        council={selectedOpportunity.council}
                                    />
                                </div>
                            </div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-gray-500">
                                <TrendingUp className="w-16 h-16 mb-4 opacity-20" />
                                <p>Select an opportunity to view detailed analysis</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* All Scan Results Table */}
            {opportunities.length > 0 && (
                <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                    <div className="p-4 border-b border-gray-700 bg-gray-700/30">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <RefreshCw className="w-5 h-5 text-blue-400" />
                            Full Market Scan Results
                        </h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-gray-700/50 text-gray-400">
                                <tr>
                                    <th className="p-4">Symbol</th>
                                    <th className="p-4">Score</th>
                                    <th className="p-4">Prediction</th>
                                    <th className="p-4">Confidence</th>
                                    <th className="p-4">Price</th>
                                    <th className="p-4">RSI</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {opportunities.map((opp, idx) => (
                                    <tr key={idx} className="hover:bg-gray-700/30 transition-colors">
                                        <td className="p-4 font-medium">{opp.symbol}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs font-semibold ${opp.score >= 70 ? 'bg-green-500/20 text-green-400' :
                                                opp.score >= 50 ? 'bg-yellow-500/20 text-yellow-400' :
                                                    'bg-red-500/20 text-red-400'
                                                }`}>
                                                {opp.score}
                                            </span>
                                        </td>
                                        <td className={`p-4 ${opp.prediction === 'UP' ? 'text-green-400' : 'text-red-400'}`}>
                                            {opp.prediction}
                                        </td>
                                        <td className="p-4">{opp.confidence}%</td>
                                        <td className="p-4 text-gray-300">{opp.current_price?.toFixed(5)}</td>
                                        <td className="p-4 text-gray-400">{opp.indicators?.rsi?.toFixed(1)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )
            }

            {/* Trade Panel */}
            <TradePanel
                activeTrades={activeTrades}
                stats={stats}
                onCloseTrade={handleCloseTrade}
            />

            {/* Strategy Info */}
            <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
                <h3 className="text-lg font-semibold mb-4">Strategy Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <h4 className="text-sm font-semibold text-purple-400 mb-2">Pattern Recognition</h4>
                        <p className="text-sm text-gray-400">
                            Identifies Doji, Hammer, Engulfing patterns for entry signals
                        </p>
                    </div>
                    <div>
                        <h4 className="text-sm font-semibold text-blue-400 mb-2">Technical Indicators</h4>
                        <p className="text-sm text-gray-400">
                            RSI, MACD, Bollinger Bands alignment for trend confirmation
                        </p>
                    </div>
                    <div>
                        <h4 className="text-sm font-semibold text-green-400 mb-2">Machine Learning</h4>
                        <p className="text-sm text-gray-400">
                            Random Forest model predicts next movement with confidence score
                        </p>
                    </div>
                </div>
            </div>
        </div >
    );
};

export default AutoTrade;
