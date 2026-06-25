import React from 'react';

export default function History({ uploads, setActiveUploadId, setActiveTab, handleDeleteHistory }) {
  return (
    <div className="card glass-card hover-glow">
      <h3 style={{ marginBottom: '20px' }}>Previous Uploads</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>UPLOAD DATE</th>
              <th>FILENAME</th>
              <th>ACADEMIC YEAR</th>
              <th>SEMESTER</th>
              <th>TOTAL STUDENTS</th>
              <th>PASS / FAIL</th>
              <th>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {uploads.length === 0 ? (
              <tr><td colSpan="7" style={{ textAlign: 'center', padding: '20px' }}>No upload history found</td></tr>
            ) : (
              uploads.map(u => (
                <tr key={u.id}>
                  <td style={{ color: 'var(--text-secondary)' }}>{new Date(u.upload_date).toLocaleString()}</td>
                  <td style={{ fontWeight: 600, color: '#dc2626' }}><i className="fa-solid fa-file-pdf" style={{ marginRight: '8px' }}></i>{u.filename}</td>
                  <td>{u.academic_year || '2023-2024'}</td>
                  <td>{u.semester || '2'}</td>
                  <td>{u.total_students}</td>
                  <td>
                    <span style={{ color: 'var(--success-color)', fontWeight: 600 }}>{u.pass_percentage ? Math.round(u.total_students * (u.pass_percentage / 100)) : 0} Pass</span>
                    <span style={{ margin: '0 5px' }}>/</span>
                    <span style={{ color: 'var(--danger-color)', fontWeight: 600 }}>{u.pass_percentage ? u.total_students - Math.round(u.total_students * (u.pass_percentage / 100)) : 0} Fail</span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => { setActiveUploadId(u.id); setActiveTab('analysis'); }}
                        className="btn btn-primary"
                        style={{ padding: '8px 16px', fontSize: '0.8rem', borderRadius: '6px' }}
                      >
                        <i className="fa-solid fa-chart-line" style={{ marginRight: '5px' }}></i> View Analysis
                      </button>
                      <button
                        onClick={() => handleDeleteHistory(u.id)}
                        className="btn btn-danger"
                        style={{ padding: '8px 12px', fontSize: '0.8rem', borderRadius: '6px', background: '#ef4444', color: 'white', border: 'none' }}
                      >
                        <i className="fa-solid fa-trash"></i>
                      </button>
                    </div>
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
