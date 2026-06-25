import React from 'react';
import { Line, Doughnut } from 'react-chartjs-2';

export default function Dashboard({ stats, meritList }) {
  const trendData = {
    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5', 'Sem 6 (Current)'],
    datasets: [{
      label: 'Pass Percentage (%)',
      data: [65, 72, 68, 76, 80, stats.passPercentage || 85],
      borderColor: '#4F46E5',
      backgroundColor: 'rgba(79, 70, 229, 0.1)',
      tension: 0.4,
      fill: true
    }]
  };
  const trendOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 40, max: 100 } } };

  const distData = {
    labels: ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F'],
    datasets: [{
      data: [15, 25, 30, 10, 5, 3, 2, stats.failedStudents || 10],
      backgroundColor: ['#eab308', '#10b981', '#0ea5e9', '#6366f1', '#8b5cf6', '#d946ef', '#f97316', '#ef4444'],
      borderWidth: 0
    }]
  };
  const distOptions = { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } } } };

  return (
    <>
      <div className="glass-card insights-gradient" style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
          <div className="ai-pulse" style={{ width: '12px', height: '12px', background: 'var(--primary-color)', borderRadius: '50%' }}></div>
          <h3 style={{ color: 'var(--primary-dark)', fontWeight: 800, letterSpacing: '0.5px' }}>
            <i className="fa-solid fa-bolt" style={{ marginRight: '5px' }}></i> Smart Insights
          </h3>
        </div>
        <ul style={{ listStyle: 'none', display: 'grid', gap: '12px', fontWeight: 500, fontSize: '0.95rem', color: '#334155' }}>
          {stats.totalStudents > 0 ? (
            <>
              <li><i className="fa-solid fa-check text-success" style={{ marginRight: '10px' }}></i> Overall pass percentage is {stats.passPercentage}%.</li>
              {stats.collegeTopper && (
                <li><i className="fa-solid fa-star text-warning" style={{ marginRight: '10px' }}></i> College topper is {stats.collegeTopper.name} from {stats.collegeTopper.branch} with {stats.collegeTopper.percentage} SGPA.</li>
              )}
            </>
          ) : (
            <li><i className="fa-solid fa-info-circle" style={{ marginRight: '10px', color: 'var(--primary-color)' }}></i> Generating AI-driven analysis... (No ledger data found)</li>
          )}
        </ul>
      </div>

      <div className="stats-grid">
        <div className="card stat-card">
          <div className="stat-label">TOTAL STUDENTS</div>
          <div className="stat-value">{stats.totalStudents}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">PASS STUDENTS</div>
          <div className="stat-value" style={{ color: 'var(--success-color)' }}>{stats.passedStudents}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">FAIL STUDENTS</div>
          <div className="stat-value" style={{ color: 'var(--danger-color)' }}>{stats.failedStudents}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">OVERALL PASS PERCENTAGE</div>
          <div className="stat-value">{stats.passPercentage}%</div>
        </div>
      </div>

      <div className="card glass-card hover-glow" style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>Top Performers</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Student Name</th>
                <th>Branch</th>
                <th>PRN Number</th>
                <th>Seat No</th>
                <th>Percentage/SGPA</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {meritList.slice(0, 5).map((m, i) => (
                <tr key={i}>
                  <td><span className="badge" style={{ background: '#1e293b', color: 'white' }}>#{i + 1}</span></td>
                  <td style={{ fontWeight: 600 }}>{m.name}</td>
                  <td>{m.branch}</td>
                  <td>{m.prn || 'F24ET000'}</td>
                  <td>{m.seat_no}</td>
                  <td style={{ color: 'var(--success-color)', fontWeight: 600 }}>{m.sgpa}</td>
                  <td><span className="badge badge-success">Pass</span></td>
                </tr>
              ))}
              {meritList.length === 0 && (
                <tr><td colSpan="7" style={{ textAlign: 'center', padding: '20px' }}>No performers found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="charts-grid">
        <div className="card glass-card hover-glow">
          <h3 style={{ marginBottom: '20px' }}>Performance Trend Analytics</h3>
          <div className="chart-container">
            <Line data={trendData} options={trendOptions} />
          </div>
        </div>
        <div className="card glass-card hover-glow">
          <h3 style={{ marginBottom: '20px' }}>Overall Result Distribution</h3>
          <div className="chart-container">
            <Doughnut data={distData} options={distOptions} />
          </div>
        </div>
      </div>
    </>
  );
}
