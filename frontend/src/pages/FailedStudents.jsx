import React, { useState } from 'react';

export default function FailedStudents({ failedStudents, handleViewStudent }) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFailedStudents = failedStudents.filter(s =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.seat_no.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="card glass-card hover-glow">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0 }}>Failed Students</h3>
        <div style={{ position: 'relative' }}>
          <i className="fa-solid fa-search" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}></i>
          <input
            type="text"
            placeholder="Search name or roll no..."
            className="form-control"
            style={{ width: '250px', padding: '10px 12px 10px 35px', borderRadius: '6px', fontSize: '0.9rem' }}
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>PRN NUMBER</th>
              <th>SEAT NO</th>
              <th>STUDENT NAME</th>
              <th>BRANCH</th>
              <th>FAILED SUBJECTS</th>
              <th>STATUS</th>
              <th>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {filteredFailedStudents.length === 0 ? (
              <tr><td colSpan="7" style={{ textAlign: 'center', padding: '20px' }}>No failed students found</td></tr>
            ) : (
              filteredFailedStudents.map((s, i) => (
                <tr key={i}>
                  <td style={{ color: 'var(--text-secondary)' }}>{s.prn || `F24ET${100 + i}`}</td>
                  <td>{s.seat_no}</td>
                  <td style={{ fontWeight: 600 }}>{s.name}</td>
                  <td>{s.branch}</td>
                  <td><span className="badge" style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', border: '1px solid #f59e0b' }}>Low SGPA</span></td>
                  <td style={{ fontWeight: 600, color: 'var(--danger-color)' }}>{s.sgpa || "0.00"}</td>
                  <td>
                    <button className="btn btn-outline" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => handleViewStudent(s)}>
                      <i className="fa-solid fa-eye" style={{ marginRight: '4px' }}></i> View
                    </button>
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
