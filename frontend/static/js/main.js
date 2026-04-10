// main.js - Production Grade Frontend Logic

const BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" ? "http://127.0.0.1:5000" : "";
const API_BASE = `${BASE_URL}/api`;

const urlParams = new URLSearchParams(window.location.search);
let currentUploadId = urlParams.get('upload_id');

if (currentUploadId) {
    localStorage.setItem('currentUploadId', currentUploadId);
} else {
    currentUploadId = localStorage.getItem('currentUploadId');
}

// Helper to append upload_id if present
function buildUrl(endpoint) {
    let url = `${API_BASE}${endpoint}`;
    if (currentUploadId) {
        url += (url.includes('?') ? '&' : '?') + `upload_id=${currentUploadId}`;
    }
    return url;
}

// Helper for Authenticated Requests
async function fetchWithAuth(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
    };

    const response = await fetch(buildUrl(endpoint), {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('token');
        window.location.href = 'index.html';
        return;
    }

    return response;
}

// Dashboard Initialization
async function initDashboard() {
    console.log("Initializing Dashboard...");

    // 1. Fetch Dashboard Stats
    try {
        const resStats = await fetchWithAuth('/dashboard/stats');
        if (resStats && resStats.ok) {
            const stats = await resStats.json();
            const elTotal = document.getElementById('stat-total');
            const elPassCount = document.getElementById('stat-pass-count');
            const elFailed = document.getElementById('stat-failed');
            const elPassPerc = document.getElementById('stat-pass');
            
            if(elTotal) elTotal.innerText = stats.totalStudents;
            if(elPassCount) elPassCount.innerText = stats.passedStudents;
            if(elFailed) elFailed.innerText = stats.failedStudents;
            if(elPassPerc) elPassPerc.innerText = stats.passPercentage + '% ';
        }
    } catch(err) {
        console.error('Error fetching dashboard stats:', err);
    }

    // 2. Fetch Top Performers
    try {
        const resMeta = await fetchWithAuth('/analysis/merit');
        if (resMeta && resMeta.ok) {
            const meritList = await resMeta.json();
            const tbody = document.getElementById('topStudentsTable');
            tbody.innerHTML = '';

            meritList.slice(0, 10).forEach(student => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="badge" style="background:#333; color:white;">#${student.rank}</span></td>
                    <td style="font-weight: 500;">${student.name}</td>
                    <td>${student.branch ? student.branch : 'Unknown'}</td>
                    <td class="text-secondary">${student.prn || '-'}</td>
                    <td class="text-secondary">${student.seat_no}</td>
                    <td style="color: green; font-weight: 600;">${student.sgpa}</td>
                    <td><span class="badge badge-success">Pass</span></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error("Error fetching merit list:", err);
    }
}


// Init Reports UI
function initReports() {
    const attachDownload = (btnId, selId, endpoint) => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener('click', () => {
                let url = buildUrl(endpoint);
                if (selId) {
                    const sel = document.getElementById(selId);
                    if (sel) {
                        url += (url.includes('?') ? '&' : '?') + `format=${sel.value}`;
                    }
                }
                const token = localStorage.getItem('token');
                if (token) {
                    url += (url.includes('?') ? '&' : '?') + `jwt=${token}`;
                }
                window.open(url, '_blank');
            });
        }
    };

    attachDownload('btn-report-remedial', 'sel-report-remedial', '/reports/remedial');
    attachDownload('btn-report-subject-weak', 'sel-report-subject-weak', '/reports/subject-weak');
    attachDownload('btn-report-class-summary', 'sel-report-class-summary', '/reports/class-summary');
    attachDownload('btn-report-progress', 'sel-report-progress', '/reports/progress');
    attachDownload('btn-report-action', 'sel-report-action', '/reports/action-recommendation');
}


// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
    // Check Auth
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
    } else {
        // If we're not on index.html, initialize profile sidebar clickability
        if (!window.location.pathname.endsWith('index.html')) {
            // Make profile sidebar clickable
            const profileSidebar = document.querySelector('.user-profile');
            if (profileSidebar) {
                profileSidebar.style.cursor = 'pointer';
                profileSidebar.title = "View Profile Info";
                profileSidebar.addEventListener('click', () => {
                    window.location.href = 'profile.html';
                });
                // Hover effect inject
                profileSidebar.onmouseover = function() { this.style.backgroundColor = '#f1f1fc'; };
                profileSidebar.onmouseout = function() { this.style.backgroundColor = 'transparent'; };
            }
        }

        // Init Dashboard if on dashboard page
        if (document.getElementById('stat-total')) {
            initDashboard();
        }
        // Init Reports Page if present
        if (document.getElementById('btn-report-remedial')) {
            initReports();
        }
        // Init Charts if present
        if (typeof initCharts === 'function') {
            initCharts();
        }
    }
});

// --- Scheduling Modal Logic ---
function openScheduleModal() {
    const modal = document.getElementById('scheduleModal');
    if (modal) {
        modal.style.display = 'flex';
        // Auto-fill date with today's date if empty
        if (!document.getElementById('scheduleDate').value) {
            document.getElementById('scheduleDate').valueAsDate = new Date();
        }
    }
}

function closeScheduleModal() {
    const modal = document.getElementById('scheduleModal');
    if (modal) modal.style.display = 'none';
}

async function submitClassSchedule() {
    const dateStr = document.getElementById('scheduleDate').value;
    const timeStr = document.getElementById('scheduleTime').value;
    const venueStr = document.getElementById('scheduleVenue').value || 'TBD';
    const topicStr = document.getElementById('scheduleTopic').value || 'Remedial Session';

    if (!dateStr || !timeStr) {
        if (window.showToast) window.showToast('Please select a Date and Time.', 'warning');
        else alert('Please select a Date and Time.');
        return;
    }

    // Format date nicely
    const dateObj = new Date(dateStr);
    const niceDate = dateObj.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });

    // Format time (12-hour AM/PM)
    let [hours, minutes] = timeStr.split(':');
    let niceTime = 'TBD';
    if (hours && minutes) {
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12;
        niceTime = `${hours}:${minutes} ${ampm}`;
    }

    const btnElement = document.getElementById('btnSubmitSchedule');
    const originalText = btnElement.innerHTML;
    
    // Set UI to loading state
    btnElement.innerHTML = '<i class="fa-solid fa-spinner fa-spin" style="margin-right: 8px;"></i> Sending Invitations...';
    btnElement.disabled = true;
    btnElement.style.opacity = '0.7';

    try {
        const response = await fetchWithAuth('/notify-remedial', {
            method: 'POST',
            body: JSON.stringify({
                date: niceDate,
                time: niceTime,
                venue: venueStr,
                topic: topicStr
            })
        });

        if (response && response.ok) {
            const data = await response.json();
            if (window.showToast) {
                window.showToast(data.message || 'Remedial session emails sent successfully!', 'success');
            } else {
                alert(data.message || 'Remedial session emails sent successfully!');
            }
            closeScheduleModal();
        } else {
            let errorMsg = 'Failed to send emails. Please check the server logs.';
            if (response) {
                try {
                    const data = await response.json();
                    if (data.error) errorMsg = data.error;
                } catch(e) {}
            }
            if (window.showToast) window.showToast(errorMsg, 'error');
            else alert(errorMsg);
        }
    } catch (error) {
        console.error('Error sending remedial notifications:', error);
        if (window.showToast) window.showToast('Network error while attempting to send emails.', 'error');
        else alert('Network error while attempting to send emails.');
    } finally {
        // Restore UI
        btnElement.innerHTML = originalText;
        btnElement.disabled = false;
        btnElement.style.opacity = '1';
    }
}
