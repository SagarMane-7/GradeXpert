import React from 'react';

export default function Sidebar({ activeTab, setActiveTab, user }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <i className="fa-solid fa-graduation-cap"></i>
        <span>GradeXpert</span>
      </div>

      <nav className="nav-links">
        <a href="#" className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); setActiveTab('dashboard'); }}>
          <i className="fa-solid fa-chart-pie"></i>
          <span>Dashboard</span>
        </a>
        <a href="#" className={`nav-item ${activeTab === 'upload' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); setActiveTab('upload'); }}>
          <i className="fa-solid fa-upload"></i>
          <span>Upload Ledger</span>
        </a>
        <a href="#" className={`nav-item ${activeTab === 'history' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); setActiveTab('history'); }}>
          <i className="fa-solid fa-clock-rotate-left"></i>
          <span>History</span>
        </a>
        <a href="#" className={`nav-item ${activeTab === 'analysis' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); setActiveTab('analysis'); }}>
          <i className="fa-solid fa-chart-line"></i>
          <span>Analysis</span>
        </a>
        <a href="#" className={`nav-item ${activeTab === 'failed' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); setActiveTab('failed'); }}>
          <i className="fa-solid fa-triangle-exclamation"></i>
          <span>Failed Students</span>
        </a>
        <a href="#" className={`nav-item ${activeTab === 'subject' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); setActiveTab('subject'); }}>
          <i className="fa-solid fa-book-open"></i>
          <span>Subject Wise Analysis</span>
        </a>
        <a href="#" className={`nav-item ${activeTab === 'reports' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); setActiveTab('reports'); }}>
          <i className="fa-solid fa-file-contract"></i>
          <span>Reports</span>
        </a>
      </nav>

      <div className="user-profile">
        <div className="avatar">{user?.name ? user.name[0].toUpperCase() : 'U'}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{user?.name || 'User'}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{user?.role === 'ADMIN' ? 'Administrator' : 'Faculty'}</div>
        </div>
        <i className="fa-solid fa-chevron-right" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}></i>
      </div>
    </aside>
  );
}
