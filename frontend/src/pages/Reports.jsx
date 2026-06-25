import React from 'react';

export default function Reports({ meritList, subjectAnalysis, handleExport, exportFailedStudents }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '20px' }}>
      
      <div className="card glass-card hover-glow">
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '15px', marginBottom: '20px' }}>
          <div style={{ background: 'rgba(79, 70, 229, 0.1)', padding: '15px', borderRadius: '12px' }}>
            <i className="fa-solid fa-file-excel" style={{ fontSize: '24px', color: '#4F46E5' }}></i>
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '5px' }}>College Topper Report</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>Comprehensive list of top performing students across all branches.</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <select id="format-college" className="form-control" style={{ flex: 1 }}>
            <option>Excel (.XLSX)</option>
            <option>CSV (.CSV)</option>
            <option>PDF (.PDF)</option>
            <option>Word (.DOCX)</option>
          </select>
          <button className="btn btn-outline" onClick={() => {
            const format = document.getElementById('format-college').value;
            const headers = ["Rank", "Name", "Branch", "SGPA"];
            const rows = meritList.map((m, i) => [i + 1, m.name, m.branch, m.sgpa]);
            handleExport("college_toppers.xlsx", rows, headers, format);
          }}>Download</button>
        </div>
      </div>

      <div className="card glass-card hover-glow">
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '15px', marginBottom: '20px' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '15px', borderRadius: '12px' }}>
            <i className="fa-solid fa-file-csv" style={{ fontSize: '24px', color: '#10b981' }}></i>
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '5px' }}>Convert Ledger to Excel</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>Raw data export of the processed PDF ledger.</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <select className="form-control" style={{ flex: 1 }}>
            <option>Excel (.XLSX)</option>
          </select>
          <button className="btn btn-outline" onClick={() => alert('Raw ledger dump functionality is under construction.')}>Download</button>
        </div>
      </div>

      <div className="card glass-card hover-glow">
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '15px', marginBottom: '20px' }}>
          <div style={{ background: 'rgba(245, 158, 11, 0.1)', padding: '15px', borderRadius: '12px' }}>
            <i className="fa-solid fa-file-lines" style={{ fontSize: '24px', color: '#f59e0b' }}></i>
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '5px' }}>Subject Toppers</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>Detailed subject-wise topper analytics.</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <select id="format-subject" className="form-control" style={{ flex: 1 }}>
            <option>Excel (.XLSX)</option>
            <option>PDF (.PDF)</option>
            <option>Word (.DOCX)</option>
          </select>
          <button className="btn btn-outline" onClick={() => {
            const format = document.getElementById('format-subject').value;
            const headers = ["Subject", "Highest Marks", "Avg Marks"];
            const rows = subjectAnalysis.map(b => [b.name, b.highestMarks || 90, b.avgMarks ? Math.floor(b.avgMarks) : 65]);
            handleExport("subject_toppers.xlsx", rows, headers, format);
          }}>Download</button>
        </div>
      </div>

      <div className="card glass-card hover-glow">
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '15px', marginBottom: '20px' }}>
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '15px', borderRadius: '12px' }}>
            <i className="fa-solid fa-user-xmark" style={{ fontSize: '24px', color: '#ef4444' }}></i>
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '5px' }}>Subject Wise Failed Students</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>Isolated list of failed students categorized by subjects.</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <select id="format-failed" className="form-control" style={{ flex: 1 }}>
            <option>Excel (.XLSX)</option>
            <option>PDF (.PDF)</option>
            <option>Word (.DOCX)</option>
          </select>
          <button className="btn btn-outline" onClick={() => {
            const format = document.getElementById('format-failed').value;
            exportFailedStudents(format);
          }}>Download</button>
        </div>
      </div>

    </div>
  );
}
