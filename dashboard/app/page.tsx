"use client";

import { useEffect, useState } from 'react';

interface Trade {
  id: number;
  token_address: string;
  type: string;
  amount: number;
  price: number;
  pnl: number;
  pnl_percent: number;
  timestamp: string;
  reasoning: string;
}

interface Portfolio {
  total_value_sol: number;
  active_positions: string; // JSON string
}

export default function Home() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [data, setData] = useState<any>({});
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const res = await fetch('/api/data');
      const json = await res.json();
      setTrades(json.trades);
      setPortfolio(json.portfolio);
      setData(json);
      setLoading(false);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="min-h-screen bg-black text-white p-10 font-bold">Loading...</div>;

  const activePositions = portfolio?.active_positions ? JSON.parse(portfolio.active_positions) : [];

  // Calculate status
  let isOnline = false;
  let lastSeenText = "Never";

  if (data?.status_data) {
    isOnline = data.status_data.is_online;
    if (data.heartbeat?.timestamp) {
      // Display Local Time for the user
      lastSeenText = new Date(data.heartbeat.timestamp).toLocaleTimeString();
    }
  } else if (data?.heartbeat?.timestamp) {
    // Fallback if API hasn't updated yet (for old cache)
    isOnline = false;
  }

  return (
    <div className="min-h-screen bg-black text-zinc-100 p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Header */}
        <header className="flex justify-between items-center border-b border-zinc-800 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              SOL/Nansen Bot
            </h1>
            <div className="flex items-center gap-2 mt-2">
              <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
              <span className={`text-sm ${isOnline ? 'text-green-500' : 'text-red-500'}`}>
                {isOnline ? "OPERATIONAL" : "OFFLINE"}
              </span>
              <span className="text-xs text-zinc-600 ml-1">Last heartbeat: {lastSeenText}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-zinc-400">Total Equity (Paper)</div>
            <div className="text-4xl font-mono font-bold text-white">
              {portfolio?.total_value_sol?.toFixed(3) ?? "---"} <span className="text-purple-400 text-lg">SOL</span>
            </div>
          </div>
        </header>

        {/* Active Positions */}
        <section>
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Active Positions
          </h2>
          {activePositions.length === 0 ? (
            <div className="p-8 border border-zinc-800 rounded-xl bg-zinc-900/50 text-center text-zinc-500">
              No active trades. Scanning for buy waves...
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activePositions.map((pos: any, idx: number) => (
                <div key={idx} className="p-6 border border-zinc-800 rounded-xl bg-zinc-900/50 hover:border-purple-500/50 transition-colors">
                  <div className="flex justify-between mb-2">
                    <span className="font-mono text-blue-400">{pos.token.substring(0, 8)}...</span>
                    <span className="text-zinc-400 text-sm">Target Exit: {new Date(pos.target_exit).toLocaleTimeString()}</span>
                  </div>
                  <div className="flex justify-between items-end">
                    <div>
                      <div className="text-xs text-zinc-500">Entry</div>
                      <div>{pos.entry_price} SOL</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-zinc-500">Value</div>
                      <div className="font-bold">{pos.current_val?.toFixed(4)} SOL</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Trade History */}
        <section>
          <h2 className="text-xl font-bold mb-4">Trade Journal</h2>
          <div className="overflow-hidden border border-zinc-800 rounded-xl bg-zinc-900/30">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-900/80 text-zinc-400 uppercase text-xs">
                <tr>
                  <th className="p-4">Time</th>
                  <th className="p-4">Type</th>
                  <th className="p-4">Token</th>
                  <th className="p-4">Price</th>
                  <th className="p-4">PnL</th>
                  <th className="p-4">Reasoning</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {trades.map((trade) => (
                  <tr key={trade.id} className="hover:bg-zinc-900/50 transition-colors">
                    <td className="p-4 text-zinc-500">{new Date(trade.timestamp).toLocaleTimeString()}</td>
                    <td className={`p-4 font-bold ${trade.type === 'BUY' ? 'text-green-500' : 'text-red-500'}`}>
                      {trade.type}
                    </td>
                    <td className="p-4 font-mono text-zinc-300">{trade.token_address.substring(0, 8)}...</td>
                    <td className="p-4 text-zinc-300">{trade.price}</td>
                    <td className={`p-4 font-bold ${trade.pnl > 0 ? 'text-green-400' : trade.pnl < 0 ? 'text-red-400' : 'text-zinc-500'}`}>
                      {trade.pnl ? `${trade.pnl_percent.toFixed(2)}%` : '-'}
                    </td>
                    <td className="p-4 text-zinc-400 italic">
                      {trade.reasoning}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Activity Feed */}
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 backdrop-blur-sm">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span className="text-yellow-400">⚡</span> Live Activity
          </h2>
          <div className="bg-black border border-zinc-800 rounded-lg p-4 font-mono text-sm h-64 overflow-y-auto space-y-2">
            {data.logs && data.logs.length > 0 ? (
              data.logs.map((log: any, i: number) => (
                <div key={i} className="flex gap-3">
                  <span className="text-zinc-500 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className={`${log.level === 'SUCCESS' ? 'text-green-400' :
                    log.level === 'ERROR' ? 'text-red-400' :
                      'text-blue-300'
                    }`}>
                    [{log.level}]
                  </span>
                  <span className="text-zinc-300">{log.message}</span>
                </div>
              ))
            ) : (
              <div className="text-zinc-600 italic">Waiting for activity...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
