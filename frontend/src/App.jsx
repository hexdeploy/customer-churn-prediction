import React, { useState, useEffect } from 'react';

// Automatically shifts to your production domain or falls back to localhost during local dev
const API_BASE_URL ="https://customer-churn-prediction-kappa-eight.vercel.app";

export default function App() {
  // Authentication State
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authMode, setAuthMode] = useState('login'); 

  // Form Inputs State 
  const [customerId, setCustomerId] = useState('');
  const [tenure, setTenure] = useState('');
  const [monthlyCharges, setMonthlyCharges] = useState('');
  const [seniorCitizen, setSeniorCitizen] = useState('No');
  const [nlpNotes, setNlpNotes] = useState('');

  // Dynamic Backend Response States
  const [riskVerdict, setRiskVerdict] = useState('N/A');
  const [churnProbability, setChurnProbability] = useState('0.00%');
  const [sentimentScore, setSentimentScore] = useState('0.0');
  
  // Independent Loading States
  const [isSingleProcessing, setIsSingleProcessing] = useState(false);
  const [isBulkProcessing, setIsBulkProcessing] = useState(false);

  // Live Aggregated State Data
  const [totalEvaluates, setTotalEvaluates] = useState(0);
  const [highRiskPercent, setHighRiskPercent] = useState(0.0);
  const [systemStatus, setSystemStatus] = useState('Offline');
  const [historyLogs, setHistoryLogs] = useState([]);
  const [bulkFile, setBulkFile] = useState(null);

  // 🔍 UI Live Log Searching & Filtering States
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('All');

  // --- 📊 LOCAL EDA CALCULATIONS FROM MONGO LOGS ---
  const totalLogs = historyLogs.length;
  const highRiskCount = historyLogs.filter(log => log.risk_verdict === 'High Risk').length;
  const modRiskCount = historyLogs.filter(log => log.risk_verdict === 'Moderate Risk').length;
  const lowRiskCount = historyLogs.filter(log => log.risk_verdict === 'Low Risk').length;

  const highPct = totalLogs ? Math.round((highRiskCount / totalLogs) * 100) : 0;
  const modPct = totalLogs ? Math.round((modRiskCount / totalLogs) * 100) : 0;
  const lowPct = totalLogs ? Math.round((lowRiskCount / totalLogs) * 100) : 0;

  const avgTenure = totalLogs ? (historyLogs.reduce((acc, curr) => acc + curr.tenure, 0) / totalLogs).toFixed(1) : 0;
  const avgCharges = totalLogs ? (historyLogs.reduce((acc, curr) => acc + (parseFloat(curr.monthly_charges) || 0), 0) / totalLogs).toFixed(2) : "0.00";

  // 🔍 Filtered History Logs Logic Computation
  const filteredLogs = historyLogs.filter(log => {
    const matchesSearch = log.customer_id ? log.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) : false;
    const matchesRiskDropdown = filterRisk === 'All' ? true : log.risk_verdict === filterRisk;
    return matchesSearch && matchesRiskDropdown;
  });

  const syncDashboardData = async () => {
    try {
      const metricsResponse = await fetch(`${API_BASE_URL}/metrics`);
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setTotalEvaluates(metricsData.total_evals);
        setHighRiskPercent(metricsData.high_risk_percentage);
        setSystemStatus(metricsData.status);
      } else {
        setSystemStatus('Offline');
      }
      
      const historyResponse = await fetch(`${API_BASE_URL}/history`);
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setHistoryLogs(historyData);
      }
    } catch (err) {
      console.error("Pipeline sync failed:", err);
      setSystemStatus('Offline');
    }
  };

  useEffect(() => {
    if (isLoggedIn) {
      syncDashboardData();
    }
  }, [isLoggedIn]);

  const handleAuth = (e) => {
    e.preventDefault();
    setIsLoggedIn(true);
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setIsSingleProcessing(true);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: customerId,
          tenure: parseInt(tenure) || 0,
          monthly_charges: parseFloat(monthlyCharges.replace('$', '')) || 0.0,
          senior_citizen: seniorCitizen === 'Yes' ? 1 : 0,
          notes: nlpNotes
        })
      });

      if (!response.ok) throw new Error('Prediction execution failure.');
      const data = await response.json();

      setRiskVerdict(data.risk_verdict || 'Low Risk');
      setChurnProbability(`${(data.churn_probability * 100).toFixed(2)}%`);
      setSentimentScore(data.sentiment_score !== undefined ? data.sentiment_score.toFixed(1) : '0.5');
      
      setCustomerId('');
      setTenure('');
      setMonthlyCharges('');
      setNlpNotes('');
      syncDashboardData();
    } catch (err) {
      console.error(err);
      alert('Error talking to backend server.');
    } finally {
      setIsSingleProcessing(false);
    }
  };

  const handleDeleteItem = async (targetId) => {
    if (!confirm(`Are you sure you want to delete prediction logs for client: ${targetId}?`)) return;
    try {
      const response = await fetch(`${API_BASE_URL}/history/${targetId}`, { method: 'DELETE' });
      if (response.ok) syncDashboardData();
    } catch (err) {
      console.error(err);
    }
  };

  if (!isLoggedIn) {
    return (
      <div style={{ backgroundColor: '#fdf2f8', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'sans-serif', color: '#1e293b', padding: '20px' }}>
        <div style={{ backgroundColor: '#ffffff', padding: '40px', borderRadius: '16px', width: '100%', maxWidth: '400px', boxShadow: '0 10px 30px rgba(219, 39, 119, 0.1)', border: '1px solid #fbcfe8' }}>
          <h2 style={{ textAlign: 'center', margin: '0 0 10px 0', color: '#db2777', fontWeight: '800' }}>{authMode === 'login' ? 'Account Login' : 'Create Account'}</h2>
          <p style={{ textAlign: 'center', color: '#64748b', fontSize: '14px', margin: '0 0 30px 0' }}>Sign in to access Your Churn Dashboard Engine</p>
          <form onSubmit={handleAuth} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {authMode === 'signup' && (
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: '#475569', marginBottom: '5px', fontWeight: 'bold' }}>Full Name</label>
                <input type="text" required style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #fbcfe8', boxSizing: 'border-box' }} />
              </div>
            )}
            <div>
              <label style={{ display: 'block', fontSize: '12px', color: '#475569', marginBottom: '5px', fontWeight: 'bold' }}>Email Address</label>
              <input type="email" required style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', boxSizing: 'border-box' }} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '12px', color: '#475569', marginBottom: '5px', fontWeight: 'bold' }}>Password</label>
              <input type="password" required style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', boxSizing: 'border-box' }} />
            </div>
            <button type="submit" style={{ width: '100%', padding: '12px', borderRadius: '8px', border: 'none', backgroundColor: '#db2777', color: '#fff', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px', boxShadow: '0 4px 12px rgba(219, 39, 119, 0.2)' }}>
              {authMode === 'login' ? 'Login' : 'Sign Up'}
            </button>
          </form>
          <div style={{ textAlign: 'center', marginTop: '20px', borderTop: '1px solid #f1f5f9', paddingTop: '15px' }}>
            <button onClick={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')} style={{ background: 'none', border: 'none', color: '#be185d', cursor: 'pointer', fontSize: '14px', fontWeight: '600' }}>
              {authMode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#fff5f7', minHeight: '100vh', fontFamily: 'sans-serif', color: '#334155', paddingBottom: '40px' }}>
      
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px 30px', backgroundColor: '#ffffff', borderBottom: '1px solid #fbcfe8', boxShadow: '0 2px 10px rgba(219,39,119,0.04)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '22px', fontWeight: '900', color: '#db2777', letterSpacing: '0.5px' }}>CHURN.AI</span>
          <span style={{ fontSize: '10px', backgroundColor: '#fce7f3', color: '#db2777', padding: '3px 8px', borderRadius: '20px', fontWeight: 'bold' }}>v2.0-Engine</span>
        </div>
        <button onClick={() => setIsLoggedIn(false)} style={{ padding: '8px 18px', borderRadius: '8px', border: '1px solid #f43f5e', backgroundColor: 'transparent', color: '#f43f5e', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}>Sign Out</button>
      </nav>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '30px 20px', display: 'flex', flexDirection: 'column', gap: '30px' }}>
        
        {/* KPI Row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div style={{ backgroundColor: '#ffffff', padding: '24px', borderRadius: '16px', border: '1px solid #fbcfe8' }}>
            <div style={{ color: '#64748b', fontSize: '12px', textTransform: 'uppercase', fontWeight: '800' }}>Processed Evaluates</div>
            <div style={{ fontSize: '32px', fontWeight: '900', color: '#db2777', marginTop: '5px' }}>{totalEvaluates}</div>
          </div>
          <div style={{ backgroundColor: '#ffffff', padding: '24px', borderRadius: '16px', border: '1px solid #fbcfe8' }}>
            <div style={{ color: '#64748b', fontSize: '12px', textTransform: 'uppercase', fontWeight: '800' }}>High Risk Segments</div>
            <div style={{ fontSize: '32px', fontWeight: '900', color: '#f59e0b', marginTop: '5px' }}>{highRiskPercent}%</div>
          </div>
          <div style={{ backgroundColor: '#ffffff', padding: '24px', borderRadius: '16px', border: '1px solid #fbcfe8' }}>
            <div style={{ color: '#64748b', fontSize: '12px', textTransform: 'uppercase', fontWeight: '800' }}>System Pipeline Status</div>
            <div style={{ fontSize: '32px', fontWeight: '900', color: systemStatus === 'Active' ? '#10b981' : '#f43f5e', marginTop: '5px' }}>{systemStatus}</div>
          </div>
        </div>

        {/* Dynamic Controls Grid Side-by-Side */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
          <div style={{ backgroundColor: '#ffffff', padding: '30px', borderRadius: '16px', border: '1px solid #fbcfe8' }}>
            <h3 style={{ margin: '0 0 25px 0', color: '#1e293b', fontWeight: '800' }}>🔮 Single Churn Evaluator</h3>
            <form onSubmit={handlePredict} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', color: '#475569', marginBottom: '6px', fontWeight: 'bold' }}>Customer ID</label>
                <input type="text" required value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="e.g. 4242-ANUP" style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', boxSizing: 'border-box' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', color: '#475569', marginBottom: '6px', fontWeight: 'bold' }}>Tenure (Months)</label>
                  <input type="number" required value={tenure} onChange={(e) => setTenure(e.target.value)} placeholder="e.g. 12" style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', boxSizing: 'border-box' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', color: '#475569', marginBottom: '6px', fontWeight: 'bold' }}>Monthly Charges</label>
                  <div style={{ position: 'relative' }}>
                    <span style={{ position: 'absolute', left: '12px', top: '12px', color: '#94a3b8', fontWeight: 'bold' }}>$</span>
                    <input type="text" required value={monthlyCharges} onChange={(e) => setMonthlyCharges(e.target.value)} placeholder="45.50" style={{ width: '100%', padding: '12px 12px 12px 28px', borderRadius: '8px', border: '1px solid #e2e8f0', boxSizing: 'border-box' }} />
                  </div>
                </div>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '13px', color: '#475569', marginBottom: '6px', fontWeight: 'bold' }}>Senior Citizen Status</label>
                <select value={seniorCitizen} onChange={(e) => setSeniorCitizen(e.target.value)} style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', boxSizing: 'border-box' }}>
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '13px', color: '#475569', marginBottom: '6px', fontWeight: 'bold' }}>Customer Support Notes (NLP Signal)</label>
                <textarea rows="3" required value={nlpNotes} onChange={(e) => setNlpNotes(e.target.value)} placeholder="Type recent customer feedback transcripts here..." style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', boxSizing: 'border-box', resize: 'none' }}></textarea>
              </div>
              <button type="submit" disabled={isSingleProcessing} style={{ width: '100%', padding: '14px', borderRadius: '8px', border: 'none', backgroundColor: isSingleProcessing ? '#cbd5e1' : '#db2777', color: '#fff', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' }}>
                {isSingleProcessing ? 'Analyzing Core Pipeline...' : 'Compute Churn Probability'}
              </button>
            </form>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ backgroundColor: '#ffffff', padding: '25px', borderRadius: '16px', border: '2px solid #db2777', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <h4 style={{ margin: '0', color: '#db2777', textTransform: 'uppercase', fontSize: '12px', fontWeight: '800' }}>INFERENCE COMPLETE</h4>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '10px' }}>
                <span style={{ color: '#64748b' }}>Risk Verdict:</span>
                <span style={{ color: riskVerdict === 'High Risk' ? '#f43f5e' : riskVerdict === 'Moderate Risk' ? '#f59e0b' : '#10b981', fontWeight: '900' }}>{riskVerdict}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '10px' }}>
                <span style={{ color: '#64748b' }}>Churn Probability:</span>
                <span style={{ color: '#1e293b', fontSize: '20px', fontWeight: '900' }}>{churnProbability}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '10px' }}>
                <span style={{ color: '#64748b' }}>Sentiment Score:</span>
                <span style={{ color: '#db2777', fontFamily: 'monospace', fontWeight: 'bold' }}>{sentimentScore}</span>
              </div>
              {riskVerdict !== 'N/A' && (
                <div style={{ backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginTop: '5px' }}>
                  <span style={{ fontSize: '11px', fontWeight: '800', color: '#475569', display: 'block', marginBottom: '4px' }}>💡 Model Risk Drivers:</span>
                  <p style={{ fontSize: '12px', margin: '0', color: '#64748b', lineHeight: '1.4' }}>
                    {riskVerdict === 'High Risk' && "⚠️ Critical trigger detected via support text analysis (keywords match structural cancellation or device outages). High billing rate risks quick attrition."}
                    {riskVerdict === 'Moderate Risk' && "⏳ Price sensitivity warning active. Client notes reference competitor match research or ongoing pricing inquiries."}
                    {riskVerdict === 'Low Risk' && "✨ Positive user health. Support interaction text indicates normal operational feedback loops or long-term loyalty inquiry structures."}
                  </p>
                </div>
              )}
            </div>

            <div style={{ backgroundColor: '#ffffff', padding: '25px', borderRadius: '16px', border: '1px solid #fbcfe8' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: '#1e293b', fontWeight: '800' }}>📊 Bulk Data Pipeline Upload</h3>
              <p style={{ fontSize: '12px', color: '#64748b', margin: '0 0 15px 0' }}>Accepts telecom_churn.csv format. Don't have one? <a href={`${API_BASE_URL}/download-template`} download style={{ color: '#db2777', fontWeight: 'bold' }}>Download CSV Template</a></p>
              <input type="file" accept=".csv" onChange={(e) => setBulkFile(e.target.files[0])} style={{ color: '#64748b', fontSize: '14px', width: '100%', marginBottom: '15px' }} />
              <button onClick={async () => {
                if (!bulkFile) return alert("Please select a valid file first.");
                const formData = new FormData(); formData.append("file", bulkFile);
                try {
                  setIsBulkProcessing(true);
                  const res = await fetch(`${API_BASE_URL}/predict/bulk`, { method: "POST", body: formData });
                  if (res.ok) { alert("Bulk Pipeline Execution Successful!"); setBulkFile(null); syncDashboardData(); }
                } catch (err) { console.error(err); } finally { setIsBulkProcessing(false); }
              }} disabled={isBulkProcessing} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: 'none', backgroundColor: isBulkProcessing ? '#94a3b8' : '#1e293b', color: '#fff', fontWeight: 'bold', cursor: 'pointer' }}>
                {isBulkProcessing ? "Processing Rows..." : "🚀 Run Bulk Pipeline Engine"}
              </button>
            </div>
          </div>
        </div>

        {/* Live EDA Subsection */}
        <div style={{ backgroundColor: '#ffffff', padding: '30px', borderRadius: '16px', border: '1px solid #fbcfe8' }}>
          <h3 style={{ margin: '0 0 8px 0', color: '#1e293b', fontWeight: '800' }}>📊 Real-Time Exploratory Data Analysis (EDA)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '30px', marginTop: '20px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 'bold' }}><span>High Risk</span><span>{highRiskCount} ({highPct}%)</span></div>
                <div style={{ height: '14px', backgroundColor: '#f1f5f9', borderRadius: '10px', overflow: 'hidden' }}><div style={{ width: `${highPct}%`, height: '100%', backgroundColor: '#f43f5e' }}></div></div>
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 'bold' }}><span>Moderate Risk</span><span>{modRiskCount} ({modPct}%)</span></div>
                <div style={{ height: '14px', backgroundColor: '#f1f5f9', borderRadius: '10px', overflow: 'hidden' }}><div style={{ width: `${modPct}%`, height: '100%', backgroundColor: '#f59e0b' }}></div></div>
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 'bold' }}><span>Low Risk</span><span>{lowRiskCount} ({lowPct}%)</span></div>
                <div style={{ height: '14px', backgroundColor: '#f1f5f9', borderRadius: '10px', overflow: 'hidden' }}><div style={{ width: `${lowPct}%`, height: '100%', backgroundColor: '#10b981' }}></div></div>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', alignItems: 'center' }}>
              <div style={{ backgroundColor: '#fff5f7', padding: '15px', borderRadius: '12px', textAlign: 'center', border: '1px solid #fbcfe8' }}>
                <span style={{ fontSize: '11px', color: '#be185d', fontWeight: 'bold' }}>AVG TENURE</span>
                <div style={{ fontSize: '24px', fontWeight: '900', color: '#db2777' }}>{avgTenure} mo</div>
              </div>
              <div style={{ backgroundColor: '#fff5f7', padding: '15px', borderRadius: '12px', textAlign: 'center', border: '1px solid #fbcfe8' }}>
                <span style={{ fontSize: '11px', color: '#be185d', fontWeight: 'bold' }}>AVG MONTHLY BILL</span>
                <div style={{ fontSize: '24px', fontWeight: '900', color: '#db2777' }}>${avgCharges}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Prediction Data Log Grid with Filter Controls */}
        <div style={{ backgroundColor: '#ffffff', borderRadius: '16px', border: '1px solid #fbcfe8', overflow: 'hidden' }}>
          
          {/* Action Header Interface */}
          <div style={{ padding: '20px 25px', borderBottom: '1px solid #fbcfe8', backgroundColor: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '15px' }}>
            <div>
              <h3 style={{ margin: '0', color: '#1e293b', fontWeight: '800' }}>🗄️ Live MongoDB Cloud Cluster Logs</h3>
              <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: '#64748b' }}>Showing {filteredLogs.length} of {historyLogs.length} logged pipeline analytics rows.</p>
            </div>
            
            {/* Live Interactive Query Filters Action Bar */}
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <input 
                type="text" 
                placeholder="🔍 Search client ID..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', width: '160px' }}
              />
              <select
                value={filterRisk}
                onChange={(e) => setFilterRisk(e.target.value)}
                style={{ padding: '8px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', backgroundColor: '#fff' }}
              >
                <option value="All">All Risk Levels</option>
                <option value="High Risk">High Risk Only</option>
                <option value="Moderate Risk">Moderate Risk</option>
                <option value="Low Risk">Low Risk</option>
              </select>

              {/* Management CSV Downloader Hook */}
              <a 
                href={`${API_BASE_URL}/export-results`}
                style={{ backgroundColor: '#1e293b', color: '#fff', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold', textDecoration: 'none', display: 'inline-block' }}
              >
                📥 Export CSV Report
              </a>
              <button onClick={syncDashboardData} style={{ backgroundColor: '#fdf2f8', border: '1px solid #fbcfe8', color: '#db2777', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}>Refresh</button>
            </div>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
              <thead>
                <tr style={{ backgroundColor: '#fff5f7', color: '#64748b', borderBottom: '1px solid #fbcfe8', fontWeight: '800' }}>
                  <th style={{ padding: '14px 20px' }}>Customer ID</th>
                  <th style={{ padding: '14px 20px' }}>Tenure</th>
                  <th style={{ padding: '14px 20px' }}>Monthly Charges</th>
                  <th style={{ padding: '14px 20px' }}>Churn Prob.</th>
                  <th style={{ padding: '14px 20px' }}>Risk Verdict</th>
                  <th style={{ padding: '14px 20px' }}>Timestamp</th>
                  <th style={{ padding: '14px 20px', textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{ padding: '30px', textAlign: 'center', color: '#94a3b8', fontStyle: 'italic' }}>No active inference pipeline evaluations found matching current filter query parameters.</td>
                  </tr>
                ) : (
                  filteredLogs.map((log) => (
                    <tr key={log.customer_id} style={{ borderBottom: '1px solid #f1f5f9', color: '#334155' }}>
                      <td style={{ padding: '14px 20px', fontFamily: 'monospace', color: '#db2777', fontWeight: 'bold' }}>{log.customer_id}</td>
                      <td style={{ padding: '14px 20px' }}>{log.tenure} mo</td>
                      <td style={{ padding: '14px 20px', fontWeight: '600' }}>${(log.monthly_charges || 0).toFixed(2)}</td>
                      <td style={{ padding: '14px 20px', fontWeight: 'bold' }}>{((log.churn_probability || 0) * 100).toFixed(1)}%</td>
                      <td style={{ padding: '14px 20px' }}>
                        <span style={{ fontSize: '12px', padding: '3px 8px', borderRadius: '12px', fontWeight: 'bold', backgroundColor: log.risk_verdict === 'High Risk' ? '#ffe4e6' : log.risk_verdict === 'Moderate Risk' ? '#fef3c7' : '#d1fae5', color: log.risk_verdict === 'High Risk' ? '#f43f5e' : log.risk_verdict === 'Moderate Risk' ? '#d97706' : '#10b981' }}>
                          {log.risk_verdict}
                        </span>
                      </td>
                      <td style={{ padding: '14px 20px', fontSize: '12px', color: '#64748b' }}>{log.timestamp}</td>
                      <td style={{ padding: '14px 20px', textAlign: 'center' }}>
                        <button onClick={() => handleDeleteItem(log.customer_id)} style={{ backgroundColor: 'transparent', border: 'none', color: '#f43f5e', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' }}>✕ Delete</button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}