import React from 'react';

export default function UploadLedger({
  handleFileUpload,
  academicYear,
  setAcademicYear,
  semester,
  setSemester,
  selectedFile,
  setSelectedFile,
  isUploading
}) {
  return (
    <div className="glass-card hover-glow" style={{ maxWidth: '800px', margin: '0 auto', background: 'white' }}>
      <h3 style={{ marginBottom: '20px' }}>Upload Configuration</h3>
      <form onSubmit={handleFileUpload}>
        <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '0.9rem' }}>Academic Year</label>
            <select
              className="form-control"
              style={{ appearance: 'none', background: '#fff url("data:image/svg+xml;charset=US-ASCII,%3Csvg width=\'10\' height=\'6\' viewBox=\'0 0 10 6\' fill=\'none\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M1 1L5 5L9 1\' stroke=\'%2364748B\' stroke-width=\'1.5\' stroke-linecap=\'round\' stroke-linejoin=\'round\'/%3E%3C/svg%3E") no-repeat right 12px center' }}
              value={academicYear}
              onChange={e => setAcademicYear(e.target.value)}
            >
              <option value="2023-2024">2023-2024</option>
              <option value="2024-2025">2024-2025</option>
              <option value="2025-2026">2025-2026</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '0.9rem' }}>Semester</label>
            <select
              className="form-control"
              style={{ appearance: 'none', background: '#fff url("data:image/svg+xml;charset=US-ASCII,%3Csvg width=\'10\' height=\'6\' viewBox=\'0 0 10 6\' fill=\'none\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M1 1L5 5L9 1\' stroke=\'%2364748B\' stroke-width=\'1.5\' stroke-linecap=\'round\' stroke-linejoin=\'round\'/%3E%3C/svg%3E") no-repeat right 12px center' }}
              value={semester}
              onChange={e => setSemester(e.target.value)}
            >
              <option value="Semester 1">Semester 1</option>
              <option value="Semester 2">Semester 2</option>
              <option value="Semester 3">Semester 3</option>
              <option value="Semester 4">Semester 4</option>
            </select>
          </div>
        </div>

        <div style={{ border: '2px dashed var(--border-color)', borderRadius: 'var(--radius)', padding: '40px', textAlign: 'center', background: '#f8fafc', marginBottom: '20px' }}>
          <i className="fa-solid fa-cloud-arrow-up" style={{ fontSize: '3rem', color: 'var(--text-secondary)', marginBottom: '15px' }}></i>
          <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '5px', fontSize: '1.2rem' }}>Drag & Drop Ledger PDF</p>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '15px' }}>
            or <span style={{ color: 'var(--primary-color)', cursor: 'pointer', fontWeight: 500 }}>browse files</span> from your computer
          </p>
          <input
            type="file"
            accept=".pdf"
            onChange={e => setSelectedFile(e.target.files[0])}
            style={{ maxWidth: '100%', marginTop: '10px' }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button type="submit" className="btn btn-primary" style={{ padding: '10px 24px', borderRadius: '8px' }} disabled={isUploading || !selectedFile}>
            {isUploading ? (
              <><i className="fa-solid fa-spinner fa-spin" style={{ marginRight: '8px' }}></i> Processing Ledger...</>
            ) : (
              <>Process Ledger</>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
