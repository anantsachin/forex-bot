import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, XCircle, Activity } from 'lucide-react';

const TradePanel = ({ activeTrades, stats, onCloseTrade }) => {
    return (
        <div className="space-y-4">
            {/* Trading Stats */}
            <div className="grid grid-cols-7 gap-4">
                <div className="bg-gray-800 p-4 rounded-lg">
                    <div className="text-gray-400 text-sm">Balance</div>
                    <div className="text-2xl font-bold text-green-400">${stats?.balance?.toLocaleString() || '10,000'}</div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                    <div className="text-gray-400 text-sm">Total P&L</div>
                    <div className={`text-2xl font-bold ${(stats?.total_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        ${stats?.total_pnl?.toFixed(2) || '0.00'}
                    </div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg border-2 border-blue-500/30">
                    <div className="text-gray-400 text-sm flex items-center gap-1">
                        Floating P&L
                        <span className="text-xs text-blue-400">(Unrealized)</span>
                    </div>
                    <div className={`text-2xl font-bold ${(stats?.total_floating_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {(stats?.total_floating_pnl || 0) >= 0 ? '+' : ''}${(stats?.total_floating_pnl || 0).toFixed(2)}
                    </div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg border-2 border-orange-500/30">
                    <div className="text-gray-400 text-sm">Max Risk/Trade</div>
                    <div className="text-2xl font-bold text-orange-400">
                        ${stats?.max_risk_per_trade?.toFixed(2) || '0.00'}
                    </div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg border-2 border-red-500/30">
                    <div className="text-gray-400 text-sm">Total Daily Risk</div>
                    <div className="text-2xl font-bold text-red-400">
                        ${stats?.total_daily_risk?.toFixed(2) || '0.00'}
                    </div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                    <div className="text-gray-400 text-sm">Win Rate</div>
                    <div className="text-2xl font-bold text-blue-400">{stats?.win_rate || 0}%</div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                    <div className="text-gray-400 text-sm">Total Trades</div>
                    <div className="text-2xl font-bold text-purple-400">{stats?.total_trades || 0}</div>
                </div>
            </div>

            {/* Active Trades */}
            {activeTrades && activeTrades.length > 0 && (
                <div className="bg-gray-800 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-green-400" />
                        Active Trades
                    </h3>
                    <div className="space-y-3">
                        {activeTrades.map((trade) => (
                            <div key={trade.trade_id} className="bg-gray-700 p-4 rounded-lg">
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className="text-xl font-bold">{trade.symbol}</span>
                                            <span className={`px-2 py-1 rounded text-xs font-semibold ${trade.direction === 'BUY' ? 'bg-green-600' : 'bg-red-600'
                                                }`}>
                                                {trade.direction}
                                            </span>
                                        </div>

                                        <div className="grid grid-cols-5 gap-4 text-sm mb-3">
                                            <div>
                                                <div className="text-gray-400">Entry</div>
                                                <div className="font-semibold text-yellow-400">{trade.entry_price}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400">Current</div>
                                                <div className="font-semibold text-blue-400">{trade.current_price || trade.entry_price}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400">Stop Loss</div>
                                                <div className="font-semibold text-red-400">{trade.stop_loss}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400">Target</div>
                                                <div className="font-semibold text-green-400">{trade.target_price}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400">Score</div>
                                                <div className="font-semibold text-purple-400 flex items-center gap-1">
                                                    ⭐ {(trade.score || 0).toFixed(1)}
                                                </div>
                                            </div>
                                        </div>

                                        {/* Floating P&L Display */}
                                        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg border border-gray-600">
                                            <div className="flex items-center gap-4">
                                                <div>
                                                    <div className="text-xs text-gray-400">Floating P&L</div>
                                                    <div className={`text-lg font-bold ${(trade.floating_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                        {(trade.floating_pnl || 0) >= 0 ? '+' : ''}${(trade.floating_pnl || 0).toFixed(2)}
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="text-xs text-gray-400">P&L %</div>
                                                    <div className={`text-lg font-bold ${(trade.pnl_percentage || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                        {(trade.pnl_percentage || 0) >= 0 ? '+' : ''}{(trade.pnl_percentage || 0).toFixed(2)}%
                                                    </div>
                                                </div>
                                                <div className="border-l border-gray-600 pl-4">
                                                    <div className="text-xs text-gray-400">Risk Amount</div>
                                                    <div className="text-lg font-bold text-orange-400">
                                                        ${(trade.risk_amount || 0).toFixed(2)}
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="text-xs text-gray-400">Risk %</div>
                                                    <div className="text-lg font-bold text-orange-400">
                                                        {(trade.risk_percentage || 0).toFixed(2)}%
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="text-xs text-gray-500">
                                                Size: {trade.lot_size} Lots
                                            </div>
                                        </div>
                                    </div>

                                    <button
                                        onClick={() => onCloseTrade(trade.trade_id)}
                                        className="ml-4 p-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                                        title="Close Trade"
                                    >
                                        <XCircle className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* No Active Trades Message */}
            {(!activeTrades || activeTrades.length === 0) && (
                <div className="bg-gray-800 p-8 rounded-lg text-center">
                    <DollarSign className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                    <div className="text-gray-400">No active trades</div>
                    <div className="text-sm text-gray-500 mt-1">Click "Run Bot" to find opportunities</div>
                </div>
            )}
        </div>
    );
};

export default TradePanel;
