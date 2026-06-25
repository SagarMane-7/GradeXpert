import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement, RadialLinearScale } from 'chart.js';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Document, Packer, Paragraph, Table, TableRow, TableCell, WidthType, HeadingLevel, TextRun } from 'docx';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UploadLedger from './pages/UploadLedger';
import History from './pages/History';
import SubjectAnalysis from './pages/SubjectAnalysis';
import FailedStudents from './pages/FailedStudents';
import Reports from './pages/Reports';

import Sidebar from './components/Sidebar';
import Header from './components/Header';
import StudentDetailModal from './components/StudentDetailModal';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement, RadialLinearScale);

const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = isLocal ? '/api' : '/api';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState(null);

  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [institute, setInstitute] = useState("SCTR'S Pune Institute of Computer Technology");
  const [department, setDepartment] = useState('Computer Engineering');

  const [activeTab, setActiveTab] = useState('dashboard');
  const [uploads, setUploads] = useState([]);
  const [activeUploadId, setActiveUploadId] = useState('');
  const [stats, setStats] = useState({
    totalStudents: 0,
    passedStudents: 0,
    failedStudents: 0,
    passPercentage: 0,
    collegeTopper: null
  });
  const [branchAnalysis, setBranchAnalysis] = useState([]);
  const [subjectAnalysis, setSubjectAnalysis] = useState([]);
  const [meritList, setMeritList] = useState([]);
  const [failedStudents, setFailedStudents] = useState([]);

  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentMarks, setStudentMarks] = useState([]);
  const [showStudentModal, setShowStudentModal] = useState(false);

  const [topperCategory, setTopperCategory] = useState('');
  const [subjectToppers, setSubjectToppers] = useState([]);

  const [academicYear, setAcademicYear] = useState('2025-2026');
  const [semester, setSemester] = useState('Semester 1');
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      fetchMe();
      fetchHistory();
    } else {
      localStorage.removeItem('token');
      setUser(null);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      fetchDashboardData(activeUploadId);
    }
  }, [token, activeUploadId]);

  const fetchMe = async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setUser(await res.json()); else handleLogout();
    } catch (e) { setErrorMessage('Failed to fetch user context'); }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setUploads(data);
        if (data.length > 0 && !activeUploadId) setActiveUploadId(data[0].id);
      }
    } catch (e) { console.error(e); }
  };

  const fetchDashboardData = async (uploadId) => {
    const queryParam = uploadId ? `?upload_id=${uploadId}` : '';
    try {
      const [resStats, resBranch, resSubject, resMerit, resFailed] = await Promise.all([
        fetch(`${API_BASE}/dashboard/stats${queryParam}`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE}/analysis/branch${queryParam}`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE}/analysis/subject${queryParam}`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE}/analysis/merit${queryParam}`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE}/analysis/failed${queryParam}`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      if (resStats.ok) setStats(await resStats.json());
      if (resBranch.ok) setBranchAnalysis(await resBranch.json());
      if (resSubject.ok) setSubjectAnalysis(await resSubject.json());
      if (resMerit.ok) setMeritList(await resMerit.json());
      if (resFailed.ok) setFailedStudents(await resFailed.json());
    } catch (e) { console.error(e); }
  };

  const handleLogin = async (e) => {
    e.preventDefault(); setErrorMessage('');
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.ok) { setToken(data.access_token); setSuccessMessage('Logged in successfully!'); }
      else setErrorMessage(data.error || 'Invalid credentials');
    } catch (err) { setErrorMessage('Network connection error'); }
  };

  const handleRegister = async (e) => {
    e.preventDefault(); setErrorMessage('');
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, registration_id: username, institute, department, password })
      });
      const data = await res.json();
      if (res.ok) { setSuccessMessage('Registration successful! Please login.'); setIsRegister(false); }
      else setErrorMessage(data.error || 'Registration failed');
    } catch (err) { setErrorMessage('Network connection error'); }
  };

  const handleLogout = () => {
    setToken(''); setUser(null); setUploads([]); setActiveUploadId('');
    setStats({ totalStudents: 0, passedStudents: 0, failedStudents: 0, passPercentage: 0, collegeTopper: null });
    setBranchAnalysis([]); setMeritList([]); setFailedStudents([]);
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return setErrorMessage('Please select a file first.');
    setIsUploading(true); setSuccessMessage(''); setErrorMessage('');
    const formData = new FormData(); formData.append('ledger', selectedFile);
    try {
      const res = await fetch(`${API_BASE}/upload`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: formData });
      const data = await res.json();
      if (res.ok) {
        setSuccessMessage(data.message || 'File uploaded successfully!');
        setSelectedFile(null); 
        setActiveUploadId(data.upload_id);
        fetchHistory(); 
        setActiveTab('dashboard');
      } else { setErrorMessage(data.error || 'File processing failed'); }
    } catch (err) { setErrorMessage('Upload request failed'); } finally { setIsUploading(false); }
  };

  const handleDeleteHistory = async (id) => {
    if (!confirm('Are you sure you want to delete this ledger upload?')) return;
    try {
      const res = await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { setSuccessMessage('Ledger deleted successfully'); if (activeUploadId === id) setActiveUploadId(''); fetchHistory(); }
      else { const data = await res.json(); setErrorMessage(data.error || 'Delete failed'); }
    } catch (e) { setErrorMessage('Network error'); }
  };

  const handleExport = (filename, dataRows, headers, format = 'Excel (.XLSX)') => {
    if (!dataRows || dataRows.length === 0) return setErrorMessage('No data to export.');
    if (format.includes('Excel') || format.includes('CSV')) {
      const worksheet = XLSX.utils.aoa_to_sheet([headers, ...dataRows]);
      const workbook = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(workbook, worksheet, "Report");
      XLSX.writeFile(workbook, format.includes('CSV') ? filename.replace('.xlsx', '.csv') : filename.replace('.csv', '.xlsx'));
    } else if (format.includes('PDF')) {
      const doc = new jsPDF('landscape'); doc.text(filename.replace(/_/g, ' ').toUpperCase(), 14, 15);
      autoTable(doc, { head: [headers], body: dataRows, startY: 20 });
      doc.save(filename.replace('.csv', '.pdf').replace('.xlsx', '.pdf'));
    } else if (format.includes('Word')) {
      const tableRows = [
        new TableRow({ tableHeader: true, children: headers.map(h => new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: String(h), bold: true })] })] })) }),
        ...dataRows.map(row => new TableRow({ children: row.map(cell => new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: String(cell ?? '') })] })] })) }))
      ];
      const doc = new Document({ sections: [{ children: [new Paragraph({ text: filename, heading: HeadingLevel.HEADING_1 }), new Table({ rows: tableRows, width: { size: 100, type: WidthType.PERCENTAGE } })] }] });
      Packer.toBlob(doc).then(blob => {
        const url = URL.createObjectURL(blob); const a = document.createElement('a');
        a.href = url; a.download = filename.replace('.xlsx', '.docx'); a.click(); URL.revokeObjectURL(url);
      });
    }
  };

  const exportFailedStudents = (format = 'Excel (.XLSX)') => {
    const headers = ["PRN NUMBER", "SEAT NO", "STUDENT NAME", "BRANCH", "FAILED SUBJECTS", "STATUS"];
    const rows = failedStudents.map(s => [s.prn || 'N/A', s.seat_no, s.name, s.branch || 'N/A', s.failed_count || '1', 'Low SGPA']);
    handleExport("failed_students.xlsx", rows, headers, format);
  };

  const handleViewStudent = async (student) => {
    setSelectedStudent(student); setShowStudentModal(true);
    try {
      const res = await fetch(`${API_BASE}/analysis/student-marks/${student.seat_no}?upload_id=${activeUploadId}`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setStudentMarks(await res.json()); else setStudentMarks([]);
    } catch (e) { setStudentMarks([]); }
  };

  const fetchSubjectToppers = async (category) => {
    if (!category || category === 'Select Category') return setSubjectToppers([]);
    try {
      const queryParam = activeUploadId ? `?upload_id=${activeUploadId}&category=${category}` : `?category=${category}`;
      const res = await fetch(`${API_BASE}/analysis/subject-toppers${queryParam}`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setSubjectToppers(await res.json()); else setSubjectToppers([]);
    } catch (e) { setSubjectToppers([]); }
  };

  if (!token) {
    return (
      <Login 
        isRegister={isRegister} setIsRegister={setIsRegister} handleLogin={handleLogin} handleRegister={handleRegister}
        username={username} setUsername={setUsername} password={password} setPassword={setPassword}
        name={name} setName={setName} institute={institute} setInstitute={setInstitute} department={department} setDepartment={setDepartment}
        errorMessage={errorMessage} successMessage={successMessage}
      />
    );
  }

  return (
    <div className="layout">
      {errorMessage && (
        <div className="custom-toast" style={{ position: 'fixed', bottom: '25px', right: '25px', zIndex: 9999, borderLeftColor: 'var(--danger-color)' }}>
          <i className="fa-solid fa-triangle-exclamation"></i>
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage('')} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', marginLeft: 'auto' }}><i className="fa-solid fa-times"></i></button>
        </div>
      )}
      {successMessage && (
        <div className="custom-toast success" style={{ position: 'fixed', bottom: '25px', right: '25px', zIndex: 9999 }}>
          <i className="fa-solid fa-check-circle"></i>
          <span>{successMessage}</span>
          <button onClick={() => setSuccessMessage('')} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', marginLeft: 'auto' }}><i className="fa-solid fa-times"></i></button>
        </div>
      )}

      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} user={user} />

      <main className="main-content">
        <Header 
          activeTab={activeTab} uploads={uploads} activeUploadId={activeUploadId} setActiveUploadId={setActiveUploadId} 
          API_BASE={API_BASE} handleLogout={handleLogout} exportFailedStudents={exportFailedStudents} 
        />

        {activeTab === 'dashboard' && <Dashboard stats={stats} meritList={meritList} />}
        {activeTab === 'upload' && <UploadLedger handleFileUpload={handleFileUpload} academicYear={academicYear} setAcademicYear={setAcademicYear} semester={semester} setSemester={setSemester} selectedFile={selectedFile} setSelectedFile={setSelectedFile} isUploading={isUploading} />}
        {activeTab === 'history' && <History uploads={uploads} setActiveUploadId={setActiveUploadId} setActiveTab={setActiveTab} handleDeleteHistory={handleDeleteHistory} />}
        {activeTab === 'analysis' && <SubjectAnalysis subjectAnalysis={subjectAnalysis} stats={stats} topperCategory={topperCategory} setTopperCategory={setTopperCategory} subjectToppers={subjectToppers} fetchSubjectToppers={fetchSubjectToppers} handleExport={handleExport} />}
        {activeTab === 'failed' && <FailedStudents failedStudents={failedStudents} handleViewStudent={handleViewStudent} />}
        {activeTab === 'subject' && <SubjectAnalysis subjectAnalysis={subjectAnalysis} stats={stats} topperCategory={topperCategory} setTopperCategory={setTopperCategory} subjectToppers={subjectToppers} fetchSubjectToppers={fetchSubjectToppers} handleExport={handleExport} />}
        {activeTab === 'reports' && <Reports meritList={meritList} subjectAnalysis={subjectAnalysis} handleExport={handleExport} exportFailedStudents={exportFailedStudents} />}

      </main>

      <StudentDetailModal showStudentModal={showStudentModal} setShowStudentModal={setShowStudentModal} selectedStudent={selectedStudent} studentMarks={studentMarks} />
    </div>
  );
}
