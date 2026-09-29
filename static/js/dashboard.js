document.addEventListener('DOMContentLoaded', function () {
    if (!window.dashboardStats) return;

    const stats = window.dashboardStats;

    // 1. Risk Level Distribution (Doughnut)
    const ctxRisk = document.getElementById('riskDistributionChart');
    if (ctxRisk) {
        new Chart(ctxRisk, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                datasets: [{
                    data: [
                        stats.risk_distribution.LOW || 0,
                        stats.risk_distribution.MEDIUM || 0,
                        stats.risk_distribution.HIGH || 0
                    ],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 3,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 15, font: { family: 'Inter', size: 12 } } }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Cases by Acquisition Stage (Bar)
    const ctxStage = document.getElementById('stageChart');
    if (ctxStage) {
        const stageLabels = Object.keys(stats.cases_by_stage || {});
        const stageValues = Object.values(stats.cases_by_stage || {});

        new Chart(ctxStage, {
            type: 'bar',
            data: {
                labels: stageLabels,
                datasets: [{
                    label: 'Active Cases',
                    data: stageValues,
                    backgroundColor: '#2563eb',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { font: { family: 'Inter', size: 10 }, maxRotation: 45, minRotation: 45 } },
                    y: { beginAtZero: true, ticks: { stepSize: 1, font: { family: 'Inter' } } }
                }
            }
        });
    }

    // 3. Average Pending Days by Stage (Horizontal Bar Bottleneck Chart)
    const ctxAvg = document.getElementById('avgPendingChart');
    if (ctxAvg) {
        const avgLabels = Object.keys(stats.avg_pending_by_stage || {});
        const avgValues = Object.values(stats.avg_pending_by_stage || {});

        new Chart(ctxAvg, {
            type: 'bar',
            data: {
                labels: avgLabels,
                datasets: [{
                    label: 'Avg Pending Days',
                    data: avgValues,
                    backgroundColor: '#d97706',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, title: { display: true, text: 'Days Pending', font: { family: 'Inter' } } },
                    y: { ticks: { font: { family: 'Inter', size: 11 } } }
                }
            }
        });
    }

    // 4. District-wise Risk Overview (Stacked Bar)
    const ctxDistrict = document.getElementById('districtRiskChart');
    if (ctxDistrict && window.districtAnalytics) {
        const distData = window.districtAnalytics;
        const labels = distData.map(d => d.district);
        const highRisk = distData.map(d => d.high_risk);
        const medRisk = distData.map(d => d.medium_risk);
        const lowRisk = distData.map(d => d.low_risk);

        new Chart(ctxDistrict, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'High Risk', data: highRisk, backgroundColor: '#ef4444' },
                    { label: 'Medium Risk', data: medRisk, backgroundColor: '#f59e0b' },
                    { label: 'Low Risk', data: lowRisk, backgroundColor: '#10b981' }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top', labels: { font: { family: 'Inter' } } } },
                scales: {
                    x: { stacked: true, ticks: { font: { family: 'Inter', size: 10 } } },
                    y: { stacked: true, beginAtZero: true }
                }
            }
        });
    }

    // 5. Case Status Distribution (Doughnut)
    const ctxStatus = document.getElementById('statusDistributionChart');
    if (ctxStatus && stats.cases_by_status) {
        const labels = Object.keys(stats.cases_by_status);
        const values = Object.values(stats.cases_by_status);

        new Chart(ctxStatus, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#64748b'],
                    borderWidth: 3,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: 'Inter', size: 12 } } } },
                cutout: '65%'
            }
        });
    }
});
