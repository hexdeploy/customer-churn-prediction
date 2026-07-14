import React, { useState } from 'react';

export default function PredictForm({ onPredictionComplete }) {
  const [formData, setFormData] = useState({
    customerID: '4242-ANUP',
    SeniorCitizen: 0,
    tenure: 12,
    MonthlyCharges: 45.50,
    TotalCharges: 546.00,
    customer_notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setResult(data);
      
      // Bubble up to trigger summary dashboard refresh if hook provided
      if (onPredictionComplete) onPredictionComplete();
    } catch (err) {
      console.error("Error evaluating customer prediction:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
      <h2 className="text-xl font-bold text-gray-800 mb-4">🔮 Single Churn Evaluator</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-600 mb-1">Customer ID</label>
            <input 
              type="text" 
              className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={formData.customerID}
              onChange={(e) => setFormData({...formData, customerID: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-600 mb-1">Tenure (Months)</label>
            <input 
              type="number" 
              className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={formData.tenure}
              onChange={(e) => setFormData({...formData, tenure: parseInt(e.target.value) || 0})}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-600 mb-1">Monthly Charges ($)</label>
            <input 
              type="number" step="0.01"
              className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={formData.MonthlyCharges}
              onChange={(e) => setFormData({...formData, MonthlyCharges: parseFloat(e.target.value) || 0.0})}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-600 mb-1">Total Charges ($)</label>
            <input 
              type="number" step="0.01"
              className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={formData.TotalCharges}
              onChange={(e) => setFormData({...formData, TotalCharges: parseFloat(e.target.value) || 0.0})}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-600 mb-1">Senior Citizen STATUS</label>
          <select 
            className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            value={formData.SeniorCitizen}
            onChange={(e) => setFormData({...formData, SeniorCitizen: parseInt(e.target.value)})}
          >
            <option value={0}>No (0)</option>
            <option value={1}>Yes (1)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-600 mb-1">Customer Support Interaction Notes (NLP Signal)</label>
          <textarea 
            rows="3"
            placeholder="Type recent customer feedback tags or chat transcripts here..."
            className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            value={formData.customer_notes}
            onChange={(e) => setFormData({...formData, customer_notes: e.target.value})}
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium p-2.5 rounded-lg transition-colors disabled:bg-gray-400"
        >
          {loading ? "Processing Pipelines..." : "Compute Churn Probability"}
        </button>
      </form>

      {result && (
        <div className="mt-6 p-4 rounded-lg border bg-slate-50 space-y-2">
          <h3 className="font-bold text-gray-700">Inference Complete:</h3>
          <div className="flex justify-between text-sm">
            <span>Risk Verdict:</span>
            <span className={`font-bold uppercase ${result.risk_level === 'high' ? 'text-red-500' : result.risk_level === 'medium' ? 'text-amber-500' : 'text-green-500'}`}>
              {result.risk_level}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Churn Probability:</span>
            <span className="font-mono font-bold text-blue-600">{(result.churn_probability * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Injected Sentiment Score:</span>
            <span className="font-mono text-gray-600">{result.sentiment_score_injected}</span>
          </div>
          <div className="text-xs text-gray-400 italic mt-1 text-right">Served via: {result.source}</div>
        </div>
      )}
    </div>
  );
}