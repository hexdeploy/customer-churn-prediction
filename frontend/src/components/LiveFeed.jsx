import React, { useState, useEffect } from 'react';

export default function LiveFeed() {
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState('Connecting...');

  useEffect(() => {
    // Connect to the FastAPI WebSocket server gateway defined in your blueprint
    const ws = new WebSocket('ws://localhost:8000/ws/predictions');

    ws.onopen = () => {
      setStatus('Connected');
      console.log('🔌 WebSocket stream connection established successfully.');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Append new real-time prediction events to the top of our feed list
      setLogs((prevLogs) => [data, ...prevLogs].slice(0, 50)); 
    };

    ws.onerror = (err) => {
      console.error('WebSocket encountered an execution error:', err);
      setStatus('Error');
    };

    ws.onclose = () => {
      setStatus('Disconnected');
      console.log('🔌 WebSocket stream connection closed.');
    };

    // Clean up connection gracefully on component dismount
    return () => ws.close();
  }, []);

  return (
    <div className="bg-slate-900 text-slate-100 p-6 rounded-xl shadow-md border border-slate-800 flex flex-col h-[480px]">
      <div className="flex justify-between items-center mb-4 border-b border-slate-800 pb-3">
        <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${status === 'Connected' ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-3 w-3 ${status === 'Connected' ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
          </span>
          Live Stream Engine Feed
        </h2>
        <span className={`text-xs font-mono px-2.5 py-1 rounded-full uppercase tracking-wider font-semibold ${status === 'Connected' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
          {status}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1 scrollbar-thin scrollbar-thumb-slate-700">
        {logs.length === 0 ? (
          <div className="text-center text-slate-500 text-sm mt-12 italic">
            Waiting for real-time model evaluation instances to process...
          </div>
        ) : (
          logs.map((log, index) => (
            <div 
              key={index} 
              className={`p-3.5 rounded-lg border text-sm transition-all duration-300 animate-fadeIn ${
                log.risk_level === 'high' 
                  ? 'bg-rose-950/40 border-rose-800/60 text-rose-200' 
                  : log.risk_level === 'medium'
                  ? 'bg-amber-950/30 border-amber-800/40 text-amber-200'
                  : 'bg-slate-800/50 border-slate-700/60 text-slate-300'
              }`}
            >
              <div className="flex justify-between font-mono mb-1">
                <span className="font-bold tracking-wide">ID: {log.customer_id}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${
                  log.risk_level === 'high' ? 'bg-rose-500/20 text-rose-400' : log.risk_level === 'medium' ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-700 text-slate-400'
                }`}>
                  {log.risk_level} RISK
                </span>
              </div>
              <div className="flex justify-between items-center text-xs mt-2 text-slate-400">
                <span>Probability: <strong className="font-mono text-slate-200">{(log.churn_probability * 100).toFixed(1)}%</strong></span>
                {log.cached && <span className="text-cyan-400 font-semibold text-[10px] uppercase tracking-wider border border-cyan-500/30 px-1 rounded bg-cyan-950/40">Cached Hit</span>}
                <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}