import React, { useState } from 'react';

export default function BatchUpload({ onBatchComplete }) {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [summary, setSummary] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setSummary(null);
    }
  };

  const processCSV = async () => {
    if (!file) return;
    setProcessing(true);
    setSummary(null);

    const reader = new FileReader();
    reader.onload = async (e) => {
      const text = e.target.result;
      const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
      
      if (lines.length <= 1) {
        alert("The selected CSV file appears to be empty or missing data rows.");
        setProcessing(false);
        return;
      }

      // Extract indices from header mapping
      const headers = lines[0].split(',');
      const idIdx = headers.indexOf('customerID');
      const seniorIdx = headers.indexOf('SeniorCitizen');
      const tenureIdx = headers.indexOf('tenure');
      const monthlyIdx = headers.indexOf('MonthlyCharges');
      const totalIdx = headers.indexOf('TotalCharges');

      const dataRows = lines.slice(1);
      setProgress({ current: 0, total: dataRows.length });

      let highRiskCount = 0;
      let totalProb = 0;
      let processedCount = 0;

      // Stream requests sequentially to keep systems balanced
      for (let i = 0; i < dataRows.length; i++) {
        const columns = dataRows[i].split(',');
        if (columns.length < headers.length) continue;

        const payload = {
          customerID: idIdx !== -1 ? columns[idIdx] : `BATCH-${i}`,
          SeniorCitizen: seniorIdx !== -1 ? parseInt(columns[seniorIdx]) || 0 : 0,
          tenure: tenureIdx !== -1 ? parseInt(columns[tenureIdx]) || 0 : 0,
          MonthlyCharges: monthlyIdx !== -1 ? parseFloat(columns[monthlyIdx]) || 0.0 : 0.0,
          TotalCharges: totalIdx !== -1 ? parseFloat(columns[totalIdx]) || 0.0 : 0.0,
          customer_notes: "Batch operational validation evaluation stream run."
        };

        try {
          const response = await fetch('http://localhost:8000/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const resData = await response.json();
          
          totalProb += resData.churn_probability;
          if (resData.risk_level === 'high') highRiskCount++;
          processedCount++;
        } catch (err) {
          console.error(`Error processing batch record at index ${i}:`, err);
        }

        setProgress({ current: i + 1, total: dataRows.length });
      }

      setSummary({
        total: processedCount,
        highRisk: highRiskCount,
        avgProbability: processedCount > 0 ? (totalProb / processedCount) : 0
      });
      setProcessing(false);
      setFile(null);
      
      if (onBatchComplete) onBatchComplete();
    };

    reader.readAsText(file);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
      <h2 className="text-xl font-bold text-gray-800 mb-4">📊 Bulk Data Pipeline Upload</h2>
      
      <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
        <input 
          type="file" 
          accept=".csv" 
          id="csv-upload-input"
          className="hidden" 
          onChange={handleFileChange}
          disabled={processing}
        />
        <label htmlFor="csv-upload-input" className="cursor-pointer block">
          <span className="text-3xl block mb-2">📁</span>
          <span className="text-sm font-semibold text-blue-600 block mb-1">
            {file ? file.name : "Click to select data file"}
          </span>
          <span className="text-xs text-gray-400">Accepts standard structured telecom_churn.csv formats</span>
        </label>
      </div>

      {file && !processing && (
        <button
          onClick={processCSV}
          className="w-full mt-4 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium p-2.5 rounded-lg transition-colors"
        >
          Initialize Bulk Scoring Run
        </button>
      )}

      {processing && (
        <div className="mt-4 space-y-2">
          <div className="flex justify-between text-xs font-semibold text-gray-500">
            <span>Evaluating File Submissions...</span>
            <span>{progress.current} / {progress.total} Rows</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-blue-600 h-2 transition-all duration-150" 
              style={{ width: `${(progress.current / progress.total) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {summary && (
        <div className="mt-5 p-4 rounded-lg bg-emerald-50 border border-emerald-100 space-y-2 text-sm text-emerald-800">
          <h3 className="font-bold">✅ Bulk Run Execution Successful</h3>
          <p>Total Records Analyzed: <strong className="font-mono text-gray-900">{summary.total}</strong></p>
          <p>High Attrition Risk Alarms triggered: <strong className="font-mono text-red-600">{summary.highRisk}</strong></p>
          <p>Average Dataset Churn Likelihood: <strong className="font-mono text-gray-900">{(summary.avgProbability * 100).toFixed(1)}%</strong></p>
        </div>
      )}
    </div>
  );
}