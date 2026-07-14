import React, { useState, useEffect } from 'react';

export default function MetricsPanel({ refreshTrigger }) {
  const [metrics, setMetrics] = useState({
    total_predictions: 0,
    avg_churn_probability: 0.0,
    high_risk_count: 0
  });

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/benchmark');
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      console.error("Failed to fetch running metrics aggregate:", err);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [refreshTrigger]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
      {/* Metric Card 1 */}
      <div className="bg-white p-5 rounded-xl shadow-md border border-gray-100 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Scored Inferences</p>
          <h3 className="text-2xl font-black text-slate-800 mt-1 font-mono">{metrics.total_predictions}</h3>
        </div>
        <div className="text-2xl bg-blue-50 p-2.5 rounded-lg text-blue-600">🖥️</div>
      </div>

      {/* Metric Card 2 */}
      <div className="bg-white p-5 rounded-xl shadow-md border border-gray-100 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Avg Attrition Probability</p>
          <h3 className="text-2xl font-black text-slate-800 mt-1 font-mono">
            {(metrics.avg_churn_probability * 100).toFixed(1)}%
          </h3>
        </div>
        <div className="text-2xl bg-purple-50 p-2.5 rounded-lg text-purple-600">📉</div>
      </div>

      {/* Metric Card 3 */}
      <div className="bg-white p-5 rounded-xl shadow-md border border-gray-100 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">High Risk Violations</p>
          <h3 className="text-2xl font-black text-red-600 mt-1 font-mono">{metrics.high_risk_count}</h3>
        </div>
        <div className="text-2xl bg-red-50 p-2.5 rounded-lg text-red-500">🚨</div>
      </div>
    </div>
  );
}