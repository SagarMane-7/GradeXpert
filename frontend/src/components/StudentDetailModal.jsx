import React from 'react';

export default function StudentDetailModal({ showStudentModal, setShowStudentModal, selectedStudent, studentMarks }) {
  if (!showStudentModal || !selectedStudent) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)',
      zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '20px'
    }} onClick={() => setShowStudentModal(false)}>
      <div className="glass-card" style={{
        maxWidth: '700px', width: '100%', maxHeight: '80vh', overflowY: 'auto',
        background: 'white', borderRadius: '16px', padding: '30px',
        boxShadow: '0 25px 60px rgba(0,0,0,0.15)'
      }} onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ margin: 0 }}>
            <i className="fa-solid fa-user-graduate" style={{ marginRight: '10px', color: 'var(--primary-color)' }}></i>
            Student Details
          </h3>
          <button onClick={() => setShowStudentModal(false)} style={{
            background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer',
            color: '#94a3b8', padding: '5px'
          }}>
            <i className="fa-solid fa-xmark"></i>
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px', background: '#f8fafc', padding: '16px', borderRadius: '12px' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Name</div>
            <div style={{ fontWeight: 600, marginTop: '4px' }}>{selectedStudent.name}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Seat No</div>
            <div style={{ fontWeight: 600, marginTop: '4px' }}>{selectedStudent.seat_no}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Branch</div>
            <div style={{ fontWeight: 600, marginTop: '4px' }}>{selectedStudent.branch}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>SGPA</div>
            <div style={{ fontWeight: 600, marginTop: '4px', color: 'var(--danger-color)' }}>{selectedStudent.sgpa || '0.00'}</div>
          </div>
        </div>

        <h4 style={{ marginBottom: '12px', fontSize: '0.95rem', color: '#475569' }}>
          <i className="fa-solid fa-book-open" style={{ marginRight: '8px' }}></i>
          Subject-wise Marks
        </h4>

        {studentMarks.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Marks</th>
                  <th>Max</th>
                  <th>Grade</th>
                </tr>
              </thead>
              <tbody>
                {studentMarks.map((m, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 500 }}>{m.subject_name}</td>
                    <td style={{ fontWeight: 600, color: m.grade === 'F' ? 'var(--danger-color)' : 'var(--success-color)' }}>{m.marks_obtained}</td>
                    <td>{m.max_marks}</td>
                    <td>
                      <span className={`badge ${m.grade === 'F' ? 'badge-danger' : 'badge-success'}`}>
                        {m.grade}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ textAlign: 'center', color: '#94a3b8', padding: '20px' }}>Loading marks data...</p>
        )}
      </div>
    </div>
  );
}
