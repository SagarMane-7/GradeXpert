import React from 'react';

export default function Login({ 
  isRegister, setIsRegister, 
  handleLogin, handleRegister, 
  username, setUsername, 
  password, setPassword, 
  name, setName, 
  institute, setInstitute, 
  department, setDepartment, 
  errorMessage, successMessage 
}) {
  return (
    <>
      <div className="ambient-bg">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>

      {errorMessage && (
        <div className="toast show" style={{ zIndex: 100 }}>
          <i className="fa-solid fa-triangle-exclamation toast-icon"></i>
          <span>{errorMessage}</span>
        </div>
      )}

      {successMessage && (
        <div className="toast show" style={{ background: '#d1fae5', color: '#065f46', borderColor: '#34d399', zIndex: 100 }}>
          <i className="fa-solid fa-check-circle toast-icon"></i>
          <span>{successMessage}</span>
        </div>
      )}

      <div className="auth-container" style={{ margin: 'auto', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '24px' }}>
        <div className="glass-card" style={{ width: '100%', maxWidth: '440px' }}>
          <div className="brand-header">
            <div className="brand-icon-wrapper">
              <i className="fa-solid fa-graduation-cap brand-icon"></i>
            </div>
            <h1 className="brand-title">Academic Portal</h1>
            <p className="brand-subtitle">{isRegister ? "Create a new account" : "Enter your credentials to access the ledger."}</p>
          </div>

          {isRegister ? (
            <form onSubmit={handleRegister}>
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 500, color: 'var(--text-muted)' }}>Full Name</label>
                <div style={{ position: 'relative' }}>
                  <input type="text" className="form-control" placeholder="Enter your full name" required value={name} onChange={e => setName(e.target.value)} />
                  <i className="fa-regular fa-user input-icon"></i>
                </div>
              </div>
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 500, color: 'var(--text-muted)' }}>Registration ID</label>
                <div style={{ position: 'relative' }}>
                  <input type="text" className="form-control" placeholder="e.g., TECH12345" required value={username} onChange={e => setUsername(e.target.value)} />
                  <i className="fa-solid fa-id-card input-icon"></i>
                </div>
              </div>
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 500, color: 'var(--text-muted)' }}>Institute Name</label>
                <div style={{ position: 'relative' }}>
                  <input type="text" className="form-control" value={institute} readOnly style={{ backgroundColor: '#f1f5f9', color: '#64748b', cursor: 'not-allowed' }} />
                  <i className="fa-solid fa-university input-icon"></i>
                </div>
              </div>
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 500, color: 'var(--text-muted)' }}>Department</label>
                <div style={{ position: 'relative' }}>
                  <select className="form-control" required style={{ appearance: 'none', cursor: 'pointer' }} value={department} onChange={e => setDepartment(e.target.value)}>
                    <option value="Computer Engineering">Computer Engineering</option>
                    <option value="Information Technology">Information Technology</option>
                    <option value="Electronics and Telecommunication">Electronics and Telecommunication</option>
                    <option value="Artificial Intelligence and Data Science">Artificial Intelligence and Data Science</option>
                    <option value="Electronics and Computer Engineering">Electronics and Computer Engineering</option>
                  </select>
                  <i className="fa-solid fa-building input-icon"></i>
                  <i className="fa-solid fa-chevron-down" style={{ position: 'absolute', right: '16px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8', pointerEvents: 'none' }}></i>
                </div>
              </div>
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 500, color: 'var(--text-muted)' }}>Password</label>
                <div style={{ position: 'relative' }}>
                  <input type="password" className="form-control" placeholder="Create a password" required value={password} onChange={e => setPassword(e.target.value)} />
                  <i className="fa-solid fa-lock input-icon"></i>
                </div>
              </div>
              <button type="submit" className="btn-login">
                <span>Create Account</span>
                <i className="fa-solid fa-user-plus" style={{ fontSize: '14px', marginLeft: '4px' }}></i>
              </button>
              <p style={{ textAlign: 'center', marginTop: '25px', fontSize: '14px', color: 'var(--text-muted)' }}>
                Already have an account? <a href="#" onClick={(e) => { e.preventDefault(); setIsRegister(false); }} style={{ color: 'var(--primary-color)', textDecoration: 'none', fontWeight: 600 }}>Sign In</a>
              </p>
            </form>
          ) : (
            <form onSubmit={handleLogin}>
              <div className="input-group">
                <input type="text" className="form-control" placeholder="Username" required value={username} onChange={e => setUsername(e.target.value)} />
                <i className="fa-solid fa-user input-icon"></i>
              </div>
              <div className="input-group">
                <input type="password" className="form-control" placeholder="Password" required value={password} onChange={e => setPassword(e.target.value)} />
                <i className="fa-solid fa-lock input-icon"></i>
              </div>
              <button type="submit" className="btn-login">
                <span>Sign In</span>
                <i className="fa-solid fa-arrow-right-to-bracket" style={{ fontSize: '14px', marginLeft: '4px' }}></i>
              </button>
              <p style={{ textAlign: 'center', marginTop: '25px', fontSize: '14px', color: 'var(--text-muted)' }}>
                Don't have an account? <a href="#" onClick={(e) => { e.preventDefault(); setIsRegister(true); }} style={{ color: 'var(--primary-color)', textDecoration: 'none', fontWeight: 600 }}>Register Here</a>
              </p>
            </form>
          )}
        </div>
      </div>
    </>
  );
}
