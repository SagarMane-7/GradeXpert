import React from 'react';

export default function Header({ 
  activeTab, 
  uploads, 
  activeUploadId, 
  setActiveUploadId, 
  API_BASE, 
  handleLogout, 
  exportFailedStudents 
}) {
  return (
    <div className="top-bar">
      <div>
        <h1>
          {activeTab === 'dashboard' && 'Overview'}
          {activeTab === 'upload' && 'Import Ledger'}
          {activeTab === 'history' && 'Ledger History'}
          {activeTab === 'analysis' && 'Analytical Deep-Dive'}
          {activeTab === 'failed' && 'Failed / ATKT List'}
          {activeTab === 'subject' && 'Subject Wise Analysis'}
          {activeTab === 'reports' && 'Download Reports'}
        </h1>
        {activeTab === 'upload' && <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Upload the PDF ledger from PICT to process results.</p>}
      </div>
      <div style={{ display: 'flex', gap: '10px' }}>
        {activeTab !== 'history' && activeTab !== 'reports' && (
          <select
            className="form-control"
            style={{ width: '200px' }}
            value={activeUploadId}
            onChange={e => setActiveUploadId(e.target.value)}
          >
            <option value="">Select Ledger Batch</option>
            {uploads.map(u => (
              <option key={u.id} value={u.id}>
                {u.filename} ({new Date(u.upload_date).toLocaleDateString()})
              </option>
            ))}
          </select>
        )}
        {activeTab === 'failed' && (
          <button className="btn btn-warning hover-glow" onClick={() => exportFailedStudents()} style={{ background: '#f59e0b', color: 'white', border: 'none' }}>
            <i className="fa-solid fa-file-export"></i> Export to Excel
          </button>
        )}
        {activeUploadId && activeTab === 'dashboard' && (
          <a
            href={`${API_BASE}/download/report/${activeUploadId}`}
            className="btn btn-primary"
            target="_blank"
            rel="noreferrer"
          >
            <i className="fa-solid fa-download" style={{ marginRight: '8px' }}></i> Download Report
          </a>
        )}
        <button className="btn btn-danger hover-glow" onClick={handleLogout} style={{ background: 'transparent', color: '#ef4444', border: '1px solid #ef4444' }}>
          <i className="fa-solid fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>
  );
}
