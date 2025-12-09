import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import AutoTrade from './components/AutoTrade';
import ChatBot from './components/ChatBot';
import TradeHistory from './components/TradeHistory';
import AutoTradeStatusBar from './components/AutoTradeStatusBar';
import { Activity, BarChart2, MessageSquare, Settings, Bot, History } from 'lucide-react';

import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="flex h-screen bg-gray-900 text-white font-sans overflow-hidden">
      {/* Sidebar */}
      <div className="w-20 bg-gray-800 flex flex-col items-center py-8 space-y-8 border-r border-gray-700">
        <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20">
          <Activity className="w-8 h-8 text-white" />
        </div>

        <nav className="flex-1 flex flex-col space-y-4 w-full items-center">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`p-3 rounded-xl transition-all duration-200 ${activeTab === 'dashboard' ? 'bg-gray-700 text-blue-400' : 'text-gray-400 hover:text-white hover:bg-gray-700/50'}`}
          >
            <BarChart2 className="w-6 h-6" />
          </button>
          <button
            onClick={() => setActiveTab('autotrade')}
            className={`p-3 rounded-xl transition-all duration-200 ${activeTab === 'autotrade' ? 'bg-gray-700 text-purple-400' : 'text-gray-400 hover:text-white hover:bg-gray-700/50'}`}
          >
            <Bot className="w-6 h-6" />
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`p-3 rounded-xl transition-all duration-200 ${activeTab === 'history' ? 'bg-gray-700 text-green-400' : 'text-gray-400 hover:text-white hover:bg-gray-700/50'}`}
          >
            <History className="w-6 h-6" />
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`p-3 rounded-xl transition-all duration-200 ${activeTab === 'chat' ? 'bg-gray-700 text-blue-400' : 'text-gray-400 hover:text-white hover:bg-gray-700/50'}`}
          >
            <MessageSquare className="w-6 h-6" />
          </button>
          <button
            className="p-3 rounded-xl text-gray-400 hover:text-white hover:bg-gray-700/50 transition-all duration-200"
          >
            <Settings className="w-6 h-6" />
          </button>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Header */}
        <header className="h-16 bg-gray-800/50 backdrop-blur-md border-b border-gray-700 flex items-center justify-between px-8">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Forex AI Trader
          </h1>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-3 py-1 bg-green-500/10 rounded-full border border-green-500/20">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs font-medium text-green-400">System Online</span>
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-600 border-2 border-gray-700"></div>
          </div>
        </header>

        {/* Auto-Trade Status Bar */}
        <AutoTradeStatusBar />

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          {activeTab === 'dashboard' && (
            <ErrorBoundary>
              <Dashboard />
            </ErrorBoundary>
          )}
          {activeTab === 'autotrade' && (
            <ErrorBoundary>
              <AutoTrade />
            </ErrorBoundary>
          )}
          {activeTab === 'history' && (
            <ErrorBoundary>
              <TradeHistory />
            </ErrorBoundary>
          )}
          {activeTab === 'chat' && <div className="h-full max-w-3xl mx-auto"><ChatBot /></div>}
        </main>
      </div>
    </div>
  );
}

export default App;
