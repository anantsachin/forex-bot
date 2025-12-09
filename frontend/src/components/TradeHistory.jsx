import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { History, ArrowUpRight, ArrowDownRight, Search, Filter } from 'lucide-react';

import { API_URL } from '../config';

const TradeHistory = () => {
    const [trades, setTrades] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL'); // ALL, WIN, LOSS

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await axios.get(`${API_URL}/trades`);
            // Combine active and recent history if needed, or just use history
            // The backend /trades endpoint returns { active_trades, recent_history, stats }
            // We'll use recent_history for this page
            setTrades(response.data.recent_history || []);
        } catch (error) {
            console.error("Error fetching trade history:", error);
        } finally {
            setLoading(false);
        }
    };

    const filteredTrades = trades.filter(trade => {
        if (filter === 'ALL') return true;
        if (filter === 'WIN') return trade.pnl > 0;
        if (filter === 'LOSS') return trade.pnl <= 0;
        return true;
    });

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto p-6">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-blue-600/20 rounded-xl">
                            <History className="w-6 h-6 text-blue-400" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white">Trade History</h2>
                            <p className="text-gray-400 text-sm">Performance log of all executed trades</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 bg-gray-700/50 p-1 rounded-lg">
                        <button
                            onClick={() => setFilter('ALL')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${filter === 'ALL' ? 'bg-gray-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
                        >
                            All
                        </button>
                        <button
                            onClick={() => setFilter('WIN')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${filter === 'WIN' ? 'bg-green-600/20 text-green-400 shadow' : 'text-gray-400 hover:text-green-400'}`}
                        >
                            Wins
                        </button>
                        <button
                            onClick={() => setFilter('LOSS')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${filter === 'LOSS' ? 'bg-red-600/20 text-red-400 shadow' : 'text-gray-400 hover:text-red-400'}`}
                        >
                            Losses
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-gray-700 text-gray-400 text-sm">
                                <th className="p-4 font-medium">Time</th>
                                <th className="p-4 font-medium">Symbol</th>
                                <th className="p-4 font-medium">Type</th>
                                <th className="p-4 font-medium">Lots</th>
                                <th className="p-4 font-medium">Entry</th>
                                <th className="p-4 font-medium">Exit</th>
                                <th className="p-4 font-medium">Stop Loss</th>
                                <th className="p-4 font-medium">Score</th>
                                <th className="p-4 font-medium">P&L</th>
                                <th className="p-4 font-medium">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700/50">
                            {loading ? (
                                <tr>
                                    <td colSpan="10" className="p-8 text-center text-gray-500">Loading history...</td>
                                </tr>
                            ) : filteredTrades.length === 0 ? (
                                <tr>
                                    <td colSpan="10" className="p-8 text-center text-gray-500">No trades found in history</td>
                                </tr>
                            ) : (
                                filteredTrades.map((trade) => (
                                    <tr key={trade.trade_id} className="hover:bg-gray-700/20 transition-colors text-sm">
                                        <td className="p-4 text-gray-400">
                                            <div className="flex flex-col">
                                                <div className="text-xs text-gray-500 mb-1">Exit:</div>
                                                <span>{formatDate(trade.exit_time).split(',')[0]}</span>
                                                <span className="text-xs text-gray-500">{formatDate(trade.exit_time).split(',')[1]}</span>
                                                <div className="text-xs text-gray-500 mt-2 mb-1">Entry:</div>
                                                <span>{formatDate(trade.entry_time).split(',')[0]}</span>
                                                <span className="text-xs text-gray-500">{formatDate(trade.entry_time).split(',')[1]}</span>
                                            </div>
                                        </td>
                                        <td className="p-4 font-bold text-white">{trade.symbol}</td>
                                        <td className="p-4">
                                            <span className={`flex items-center gap-1 font-medium ${trade.direction === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                                                {trade.direction === 'BUY' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                                {trade.direction}
                                            </span>
                                        </td>
                                        <td className="p-4 text-gray-300">{trade.lot_size}</td>
                                        <td className="p-4 text-gray-400">{trade.entry_price?.toFixed(5)}</td>
                                        <td className="p-4 text-gray-400">{trade.exit_price?.toFixed(5)}</td>
                                        <td className="p-4 text-gray-500">{trade.stop_loss?.toFixed(5)}</td>
                                        <td className="p-4 text-purple-400 font-semibold">
                                            ⭐ {(trade.score || 0).toFixed(1)}
                                        </td>
                                        <td className={`p-4 font-bold ${trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            {trade.pnl >= 0 ? '+' : ''}${trade.pnl?.toFixed(2)}
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${trade.status === 'CLOSED_WIN' ? 'bg-green-500/10 text-green-400' :
                                                trade.status === 'CLOSED_LOSS' ? 'bg-red-500/10 text-red-400' :
                                                    'bg-gray-500/10 text-gray-400'
                                                }`}>
                                                {trade.status.replace('CLOSED_', '')}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default TradeHistory;
