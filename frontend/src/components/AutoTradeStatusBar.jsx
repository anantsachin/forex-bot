import React, { useState, useEffect } from 'react';
import { Play, Square, Activity, Clock, TrendingUp } from 'lucide-react';
import axios from 'axios';

import { API_URL } from '../config';

const AutoTradeStatusBar = () => {
    const [status, setStatus] = useState({
        is_running: false,
        last_trade_time: null,
        trade_count: 0,
        scan_interval: 300
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Fetch status on mount
        fetchStatus();

        // Poll status every 5 seconds
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchStatus = async () => {
        try {
            const response = await axios.get(`${API_URL}/auto-trade/status`);
            setStatus(response.data);
        } catch (error) {
            console.error('Error fetching auto-trade status:', error);
        }
    };

    const handleStart = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/auto-trade/start`);
            if (response.data.status === 'started' || response.data.status === 'already_running') {
                await fetchStatus();
                alert('Auto-trading started! The bot will scan for opportunities every 5 minutes.');
            }
        } catch (error) {
            console.error('Error starting auto-trade:', error);
            alert(`Failed to start auto-trading: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleStop = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/auto-trade/stop`);
            if (response.data.status === 'stopped') {
                await fetchStatus();
                alert(`Auto-trading stopped. Total trades executed: ${response.data.total_trades}`);
            }
        } catch (error) {
            console.error('Error stopping auto-trade:', error);
            alert(`Failed to stop auto-trading: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const formatTime = (isoString) => {
        if (!isoString) return 'Never';
        const date = new Date(isoString);
        return date.toLocaleTimeString();
    };

    return (
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-3">
            <div className="flex items-center justify-between max-w-7xl mx-auto">
                <div className="flex items-center gap-6">
                    {/* Status Indicator */}
                    <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${status.is_running ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                        <span className="text-sm font-medium text-white">
                            {status.is_running ? 'Auto-Trading Active' : 'Auto-Trading Stopped'}
                        </span>
                    </div>

                    {/* Trade Count */}
                    <div className="flex items-center gap-2 text-gray-400">
                        <TrendingUp className="w-4 h-4" />
                        <span className="text-sm">{status.trade_count} trades</span>
                    </div>

                    {/* Last Trade Time */}
                    <div className="flex items-center gap-2 text-gray-400">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm">Last: {formatTime(status.last_trade_time)}</span>
                    </div>

                    {/* Scan Interval */}
                    {status.is_running && (
                        <div className="flex items-center gap-2 text-gray-400">
                            <Activity className="w-4 h-4" />
                            <span className="text-sm">Scanning every {status.scan_interval / 60} min</span>
                        </div>
                    )}
                </div>

                {/* Control Button */}
                <button
                    onClick={status.is_running ? handleStop : handleStart}
                    disabled={loading}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${status.is_running
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                    {status.is_running ? (
                        <>
                            <Square className="w-4 h-4" />
                            Stop Auto-Trading
                        </>
                    ) : (
                        <>
                            <Play className="w-4 h-4" />
                            Start Auto-Trading
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

export default AutoTradeStatusBar;
