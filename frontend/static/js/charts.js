// charts.js - Production Charts

async function initCharts() {
    console.log("Initializing Charts...");

    const ctxSub = document.getElementById('subjectChart');
    const ctxPF = document.getElementById('passFailChart');
    const ctxDiff = document.getElementById('subjectDifficultyChart');
    const ctxTrend = document.getElementById('performanceTrendChart');

    function setChartReady(id) {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        const wrapper = canvas.closest('.chart-container') || canvas.parentElement;
        if (wrapper) wrapper.classList.add('ready');
    }

    const subjectsRequest = fetchWithAuth('/analysis/subjects');
    const gradesRequest = fetchWithAuth('/analysis/grades');
    const atRiskPromise = initAtRiskTable();

    const [subjectsResult, gradesResult] = await Promise.allSettled([subjectsRequest, gradesRequest]);

    let subjectData = null;
    if (subjectsResult.status === 'fulfilled' && subjectsResult.value && subjectsResult.value.ok) {
        subjectData = await subjectsResult.value.json();
    } else if (ctxSub || ctxDiff) {
        console.error('Error loading subject analysis data', subjectsResult.status === 'rejected' ? subjectsResult.reason : subjectsResult.value);
    }

    if (ctxPF && gradesResult.status === 'fulfilled' && gradesResult.value && gradesResult.value.ok) {
        try {
            const gradeData = await gradesResult.value.json();
            const desiredOrder = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F'];
            const colorMap = {
                'O':  '#F59E0B',
                'A+': '#10B981',
                'A':  '#0EA5E9',
                'B+': '#6366F1',
                'B':  '#8B5CF6',
                'C':  '#D946EF',
                'P':  '#F97316',
                'F':  '#EF4444'
            };
            const orderedLabels = [];
            const orderedValues = [];
            const orderedColors = [];

            desiredOrder.forEach(grade => {
                if (gradeData[grade] !== undefined) {
                    orderedLabels.push(grade);
                    orderedValues.push(gradeData[grade]);
                    orderedColors.push(colorMap[grade]);
                }
            });

            new Chart(ctxPF, {
                type: 'doughnut',
                data: {
                    labels: orderedLabels,
                    datasets: [{
                        data: orderedValues,
                        backgroundColor: orderedColors,
                        borderWidth: 0,
                        hoverOffset: 12
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    layout: { padding: 20 },
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                pointStyle: 'circle',
                                font: { family: "'Inter', sans-serif", size: 13, weight: '600' },
                                color: '#475569'
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            titleFont: { size: 14, family: "'Inter', sans-serif" },
                            bodyFont: { size: 15, family: "'Inter', sans-serif", weight: 'bold' },
                            padding: 15,
                            cornerRadius: 10,
                            displayColors: true,
                            usePointStyle: true,
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    const total = context.chart._metasets[context.datasetIndex].total;
                                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                    return ` ${value} Students (${percentage}%)`;
                                }
                            }
                        }
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true,
                        duration: 0,
                        easing: 'easeOutBounce'
                    }
                }
            });
            setChartReady('passFailChart');
        } catch (e) {
            console.error('Error rendering pass/fail chart:', e);
        }
    }

    if ((ctxSub || ctxDiff) && subjectData) {
        if (ctxSub) {
            const labels = subjectData.map(d => d.name);
            const passRates = subjectData.map(d => d.pass);
            const gradientPass = ctxSub.getContext('2d').createLinearGradient(0, 0, 0, 400);
            gradientPass.addColorStop(0, 'rgba(54, 162, 235, 0.85)');
            gradientPass.addColorStop(1, 'rgba(54, 162, 235, 0.1)');

            new Chart(ctxSub, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'Pass Percentage',
                        data: passRates,
                        backgroundColor: gradientPass,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        borderRadius: 6,
                        barPercentage: 0.6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            titleFont: { size: 14, family: "'Inter', sans-serif" },
                            bodyFont: { size: 13, family: "'Inter', sans-serif" },
                            padding: 12,
                            cornerRadius: 8,
                            displayColors: false
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { display: false },
                            title: { display: true, text: 'SUBJECTS', color: '#64748b', font: { family: "'Inter', sans-serif", size: 12, weight: 600, letterSpacing: 1 }, padding: { top: 10 } }
                        },
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
                            ticks: { font: { family: "'Inter', sans-serif" }, color: '#64748b' }
                        }
                    },
                    animation: { duration: 0 },
                    easing: 'easeOutQuart'
                }
            });
            setChartReady('subjectChart');
        }

        if (ctxDiff) {
            if (subjectData.length > 0) {
                let minAvg = Infinity;
                let hardest = null;
                let maxFailRate = -1;
                let mostFailed = null;

                subjectData.forEach(sub => {
                    if (sub.avgMarks > 0 && sub.avgMarks < minAvg) {
                        minAvg = sub.avgMarks;
                        hardest = sub;
                    }
                    const totalSub = sub.total;
                    const subFailRate = totalSub > 0 ? (sub.fail / totalSub) * 100 : 0;
                    if (subFailRate > maxFailRate) {
                        maxFailRate = subFailRate;
                        mostFailed = sub;
                    }
                });

                if (hardest) {
                    const hTitle = document.getElementById('hardestSubjectName');
                    if (hTitle) hTitle.innerText = hardest.name.length > 30 ? hardest.name.substring(0, 30) + '...' : hardest.name;
                    const hMarks = document.getElementById('hardestSubjectMarks');
                    if (hMarks) hMarks.innerText = `Avg Marks: ${hardest.avgMarks} (Out of ${hardest.outof})`;
                }
                if (mostFailed) {
                    const fTitle = document.getElementById('highestFailureName');
                    if (fTitle) fTitle.innerText = mostFailed.name.length > 30 ? mostFailed.name.substring(0, 30) + '...' : mostFailed.name;
                    const fRate = document.getElementById('highestFailureRate');
                    if (fRate) fRate.innerText = `Failed: ${mostFailed.fail} Students (${maxFailRate.toFixed(1)}%)`;
                }
            }

            const labels = subjectData.map(d => d.name.length > 25 ? d.name.substring(0,25) + '...' : d.name);
            const avgMarks = subjectData.map(d => d.avgMarks);
            const passPerc = subjectData.map(d => d.pass);
            const failCounts = subjectData.map(d => d.fail);
            const barColors = avgMarks.map(m => m < 50 ? 'rgba(239, 68, 68, 0.85)' : 'rgba(14, 165, 233, 0.85)');
            const borderColors = avgMarks.map(m => m < 50 ? 'rgba(220, 38, 38, 1)' : 'rgba(2, 132, 199, 1)');

            new Chart(ctxDiff, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        {
                            type: 'line',
                            label: 'Pass %',
                            data: passPerc,
                            borderColor: 'rgba(16, 185, 129, 1)',
                            backgroundColor: 'rgba(16, 185, 129, 0.2)',
                            borderWidth: 3,
                            fill: false,
                            tension: 0.4,
                            yAxisID: 'y1'
                        },
                        {
                            type: 'bar',
                            label: 'Avg Marks',
                            data: avgMarks,
                            backgroundColor: barColors,
                            borderColor: borderColors,
                            borderWidth: 1,
                            borderRadius: 6,
                            yAxisID: 'y'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { position: 'top', labels: { font: { family: "'Inter', sans-serif" } } },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            titleFont: { size: 13, family: "'Inter', sans-serif" },
                            bodyFont: { size: 13, family: "'Inter', sans-serif" },
                            callbacks: {
                                afterBody: function(ctx) {
                                    const i = ctx[0].dataIndex;
                                    return `\nTotal Failed: ${failCounts[i]} Students`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: { grid: { display: false }, ticks: { maxRotation: 45, minRotation: 45, font: { size: 10 } } },
                        y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'Average Marks', color: '#64748b' } },
                        y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'Pass Percentage (%)', color: '#64748b' }, grid: { drawOnChartArea: false }, min: 0, max: 100 }
                    },
                    animation: { duration: 0, easing: 'easeOutQuart' }
                }
            });
            setChartReady('subjectDifficultyChart');
        }
    }

    if (ctxTrend) {
        new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5', 'Sem 6 (Current)'],
                datasets: [{
                    label: 'Pass % Trend',
                    data: [65, 72, 68, 76, 80, 85],
                    borderColor: 'rgba(79, 70, 229, 1)',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: 'rgba(79, 70, 229, 1)',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { grid: { display: false } }, y: { beginAtZero: false, min: 40, max: 100, title: { display: true, text: 'Pass Percentage (%)' } } },
                animation: { duration: 0, easing: 'easeOutQuart' }
            }
        });
        setChartReady('performanceTrendChart');
    }

    await atRiskPromise;
    window.initSmartInsights(subjectData);
}

let globalAtRiskData = [];

function getFilterQuery() {
    let q = [];
    const b = document.getElementById('globalBranchFilter');
    if (b && b.value !== 'all') q.push('branch=' + encodeURIComponent(b.value));
    return q.length ? '?' + q.join('&') : '';
}

window.triggerDashboardUpdate = function() {
    Chart.instances.forEach(i => i.destroy());
    initCharts();
};

window.resetGlobalFilters = function() {
    const b = document.getElementById('globalBranchFilter');
    if (b) b.value = 'all';
    window.triggerDashboardUpdate();
};

async function initAtRiskTable() {
    const tbody = document.getElementById('atRiskTableBody');
    if (!tbody) return;
    try {
        const response = await fetchWithAuth('/analytics/at-risk' + getFilterQuery());
        if (response && response.ok) {
            globalAtRiskData = await response.json();
            window.renderAtRiskTable(globalAtRiskData);
        } else {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Error loading data</td></tr>';
        }
    } catch(e) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Error connecting to server</td></tr>';
    }
}

window.filterAtRiskTable = function() {
    const term = document.getElementById('atRiskSearch').value.toLowerCase();
    const filtered = globalAtRiskData.filter(d => 
        (d.name && d.name.toLowerCase().includes(term)) || 
        (d.seat_no && d.seat_no.toLowerCase().includes(term))
    );
    window.renderAtRiskTable(filtered);
};

window.renderAtRiskTable = function(data) {
    const tbody = document.getElementById('atRiskTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    data.sort((a,b) => b.failed_count - a.failed_count || a.percentage - b.percentage);
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">No at-risk students found!</td></tr>';
        return;
    }
    data.forEach(s => {
        const tr = document.createElement('tr');
        if (s.risk_status === 'Critical') tr.style.backgroundColor = 'rgba(239, 68, 68, 0.04)';
        let badgeColor = s.risk_status === 'Critical' ? 'badge-danger' : 'badge-warning';
        let failColor = s.failed_count > 3 ? 'color: var(--danger-color); font-weight: bold;' : 'font-weight: 500;';
        tr.innerHTML = `
            <td style="font-weight: 600;">${s.name || '-'}</td>
            <td class="text-secondary">${s.prn || '-'}</td>
            <td class="text-secondary">${s.seat_no}</td>
            <td style="font-weight: 500; color: ${s.percentage < 40 ? 'var(--danger-color)' : 'inherit'};">${s.percentage}%</td>
            <td style="${failColor}">${s.failed_count} Subject(s)</td>
            <td><span class="badge ${badgeColor}">${s.risk_status}</span></td>
        `;
        tbody.appendChild(tr);
    });
};

window.exportAtRiskCSV = function() {
    if(!globalAtRiskData || globalAtRiskData.length === 0) return;
    let csvContent = "Student Name,PRN Number,Roll Number,Percentage,Failed Subjects,Status\n";
    globalAtRiskData.forEach(s => {
        const name = s.name ? s.name.replace(/"/g, '""') : '';
        csvContent += `"${name}","${s.prn || ''}","${s.seat_no}","${s.percentage}","${s.failed_count}","${s.risk_status}"\n`;
    });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "At_Risk_Students.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

window.showToast = function(msg, type='success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;
    let icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
    let iconColor = type === 'success' ? 'var(--success-color)' : 'var(--warning-color)';
    toast.innerHTML = `<i class="fa-solid ${icon}" style="color: ${iconColor};"></i> <span>${msg}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 1200);
};

window.initSmartInsights = async function(subjectData = null) {
    const list = document.getElementById('smartInsightsList');
    if (!list) return;
    list.innerHTML = '';

    // Insight 1: Calculate Critical students
    const criticalCount = globalAtRiskData.filter(d => d.risk_status === 'Critical').length;
    const li1 = document.createElement('li');
    li1.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: var(--danger-color); margin-right: 8px;"></i> <b>${criticalCount}</b> students are in <span style="color: var(--danger-color); font-weight: 700;">Critical State</span> and require immediate attention.`;
    list.appendChild(li1);

    // Insight 2 & 3: Hardest subject
    let data = subjectData;
    if (!data) {
        try {
            const response = await fetchWithAuth('/analysis/subjects' + getFilterQuery());
            if (response && response.ok) {
                data = await response.json();
            }
        } catch (e) {
            console.error('Error loading subjects for insights:', e);
            data = [];
        }
    }

    if (data && data.length > 0) {
        const hardSubjectsCount = data.filter(s => s.pass < 60).length;
        const li2 = document.createElement('li');
        li2.innerHTML = `<i class="fa-solid fa-book-open" style="color: var(--warning-color); margin-right: 8px;"></i> <b>${hardSubjectsCount}</b> subjects currently have a pass rate below 60%.`;
        list.appendChild(li2);

        let minAvg = Infinity;
        let hardest = null;

        data.forEach(sub => {
            if (sub.avgMarks > 0 && sub.avgMarks < minAvg) {
                minAvg = sub.avgMarks;
                hardest = sub;
            }
        });

        if (hardest) {
            const li3 = document.createElement('li');
            li3.innerHTML = `<i class="fa-solid fa-chart-line" style="color: var(--primary-color); margin-right: 8px;"></i> <b>${hardest.name}</b> is historically the most difficult subject. A remedial session action is recommended.`;
            list.appendChild(li3);
        }
    }
};

