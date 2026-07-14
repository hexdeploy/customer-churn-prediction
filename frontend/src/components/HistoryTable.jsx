import React, { useState, useEffect } from 'react';

export default function HistoryTable({ refreshTrigger }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/history');
      const data = await response.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to query MongoDB prediction logs:", err);
    } finally {
      setLoading(false);
    }
  };

  // Re-fetch whenever the parent component triggers a refresh (e.g., after a new prediction)
  useEffect(() => {
    fetchHistory();
  }, [refreshTrigger]);

  if (loading) {
    return <div className="text-gray-500 text-sm italic py-4">Querying database collection...</div>;
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 overflow-hidden">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">🗄️ MongoDB Prediction History</h2>
        <button 
          onClick={fetchHistory}
          className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium px-3 py-1.5 rounded-lg transition-colors"
        >
          🔄 Refresh Logs
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-200 bg-slate-50 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              <th className="p-3">Customer ID</th>
              <th className="p-3">Tenure</th>
              <th className="p-3">Monthly Charges</th>
              <th className="p-3">Churn Prob.</th>
              <th className="p-3">Model Version</th>
              <th className="p-3 text-right">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-sm text-gray-700">
            {history.length === 0 ? (
              <tr>
                <td colSpan="6" className="p-4 text-center text-gray-400 italic">No historical data found in this collection.</td>
              </tr>
            ) : (
              history.map((row) => (
                <tr key={row._id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-3 font-mono font-bold text-gray-900">{row.customer_id}</td>
                  <td className="p-3">{row.input_features?.tenure} mo</td>
                  <td className="p-3">${row.input_features?.MonthlyCharges?.toFixed(2)}</td>
                  <td className="p-3">
                    <span className={`font-mono font-bold ${row.churn_probability >= 0.5 ? 'text-red-600' : 'text-emerald-600'}`}>
                      {(row.churn_probability * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="p-3 text-xs text-gray-500"><span className="bg-gray-100 px-2 py-0.5 rounded-md">{row.model_version}</span></td>
                  <td className="p-3 text-xs text-gray-400 text-right">
                    {new Date(row.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}