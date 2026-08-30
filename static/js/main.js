let benignAttackChart;
let trafficTimeChart;
let attackCountChart;

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

function confidenceText(value) {
    return value === null || value === undefined ? "N/A" : Number(value).toFixed(4);
}

function updateLiveClock() {
    const clockElement = document.getElementById("liveClock");
    if (!clockElement) return;

    const now = new Date();
    const dateStr = now.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '-');
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
    clockElement.textContent = `📅 ${dateStr} 🕒 ${timeStr}`;
}

function clearSystemLog() {
    const logElement = document.getElementById("systemLogText");
    if (logElement) {
        logElement.textContent = "System log cleared. Monitoring active.";
    }
}

async function refreshStatus() {
    const statusElement = document.getElementById("monitorStatus");
    const statusDot = document.getElementById("statusDot");
    const messageElement = document.getElementById("statusMessage");
    const errorElement = document.getElementById("errorMessage");
    const logElement = document.getElementById("systemLogText");

    if (!statusElement) return;

    try {
        const response = await fetch("/api/status");
        const status = await response.json();
        
        statusElement.textContent = status.active ? "MONITORING ACTIVE" : "MONITORING STOPPED";
        if (statusDot) {
            statusDot.className = status.active ? "status-dot active" : "status-dot stopped";
        }
        if (messageElement) messageElement.textContent = status.message || "";
        if (errorElement) errorElement.textContent = status.error ? `⚠ ${status.error}` : "";
        if (logElement && status.message) {
            logElement.textContent = status.active ? `[ACTIVE] ${status.message}` : `[IDLE] ${status.message}`;
        }
    } catch (err) {
        console.error("Error refreshing status:", err);
    }
}

async function refreshSummary() {
    try {
        const response = await fetch("/api/summary");
        const summary = await response.json();
        setText("totalPackets", summary.total_packets);
        setText("totalFlows", summary.total_flows);
        setText("normalTraffic", summary.normal_traffic);
        setText("detectedAttacks", summary.detected_attacks);
        setText("activeAlerts", summary.active_alerts);

        const demoBadge = document.getElementById("demoBannerBadge");
        if (demoBadge) {
            if (summary.has_demo_data) {
                demoBadge.classList.remove("d-none");
            } else {
                demoBadge.classList.add("d-none");
            }
        }
    } catch (err) {
        console.error("Error refreshing summary:", err);
    }
}

async function refreshCharts() {
    const benignCanvas = document.getElementById("benignAttackChart");
    if (!benignCanvas) return;

    try {
        const response = await fetch("/api/charts");
        const data = await response.json();

        const benignCount = data.benign_attack.BENIGN || 0;
        const attackCount = data.benign_attack.ATTACK || 0;
        const benignAttackValues = [benignCount, attackCount];
        
        const timeLabels = (data.traffic_over_time || []).map((item) => item.minute);
        const timeValues = (data.traffic_over_time || []).map((item) => item.count);
        const attackLabels = (data.attack_count || []).map((item) => item.severity);
        const attackValues = (data.attack_count || []).map((item) => item.count);

        const tealColor = "#1b4d4f";
        const rustColor = "#b84a2a";
        const amberColor = "#c28829";

        if (!benignAttackChart) {
            benignAttackChart = new Chart(benignCanvas, {
                type: "doughnut",
                data: {
                    labels: ["BENIGN", "ATTACK"],
                    datasets: [{
                        data: benignAttackValues,
                        backgroundColor: [tealColor, rustColor],
                        borderWidth: 2,
                        borderColor: "#efe7d8"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "bottom", labels: { font: { family: 'JetBrains Mono', size: 11 }, color: '#2b2520' } }
                    }
                }
            });

            trafficTimeChart = new Chart(document.getElementById("trafficTimeChart"), {
                type: "line",
                data: {
                    labels: timeLabels.length ? timeLabels : ["NOW"],
                    datasets: [{
                        label: "Flows",
                        data: timeValues.length ? timeValues : [0],
                        borderColor: tealColor,
                        backgroundColor: "rgba(27, 77, 79, 0.15)",
                        tension: 0.25,
                        fill: true,
                        pointBackgroundColor: tealColor
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { font: { family: 'JetBrains Mono', size: 10 }, color: '#6e6456' }, grid: { color: 'rgba(184, 172, 148, 0.3)' } },
                        y: { beginAtZero: true, ticks: { font: { family: 'JetBrains Mono', size: 10 }, color: '#6e6456' }, grid: { color: 'rgba(184, 172, 148, 0.3)' } }
                    }
                }
            });

            attackCountChart = new Chart(document.getElementById("attackCountChart"), {
                type: "bar",
                data: {
                    labels: attackLabels.length ? attackLabels : ["HIGH", "MEDIUM"],
                    datasets: [{
                        label: "Alerts",
                        data: attackValues.length ? attackValues : [0, 0],
                        backgroundColor: [rustColor, amberColor],
                        borderWidth: 1,
                        borderColor: "#efe7d8"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { font: { family: 'JetBrains Mono', size: 10 }, color: '#6e6456' }, grid: { color: 'rgba(184, 172, 148, 0.3)' } },
                        y: { beginAtZero: true, ticks: { font: { family: 'JetBrains Mono', size: 10 }, color: '#6e6456' }, grid: { color: 'rgba(184, 172, 148, 0.3)' } }
                    }
                }
            });
            return;
        }

        benignAttackChart.data.datasets[0].data = benignAttackValues;
        trafficTimeChart.data.labels = timeLabels.length ? timeLabels : ["NOW"];
        trafficTimeChart.data.datasets[0].data = timeValues.length ? timeValues : [0];
        attackCountChart.data.labels = attackLabels.length ? attackLabels : ["HIGH", "MEDIUM"];
        attackCountChart.data.datasets[0].data = attackValues.length ? attackValues : [0, 0];

        benignAttackChart.update();
        trafficTimeChart.update();
        attackCountChart.update();
    } catch (err) {
        console.error("Error refreshing charts:", err);
    }
}

async function refreshLiveTable() {
    const table = document.getElementById("liveTrafficTable");
    if (!table) return;

    try {
        const response = await fetch("/api/live");
        const rows = await response.json();
        table.innerHTML = rows.length ? rows.map((row) => `
            <tr>
                <td>${row.timestamp}</td>
                <td>${row.source_ip}:${row.source_port}</td>
                <td>${row.destination_ip}:${row.destination_port}</td>
                <td>${row.protocol}</td>
                <td>${row.packet_count}</td>
                <td>${row.byte_count}</td>
                <td>
                    ${row.prediction === 'ATTACK' ? '<span class="badge-attack">ATTACK</span>' : '<span class="badge-benign">BENIGN</span>'}
                </td>
                <td>${confidenceText(row.confidence)}</td>
            </tr>`).join("") : '<tr><td colspan="8" class="text-center text-muted py-4">-- NO TRAFFIC RECORDS AVAILABLE --</td></tr>';
    } catch (err) {
        console.error("Error refreshing live table:", err);
    }
}

async function refreshAlertsTable() {
    const table = document.getElementById("alertsTable");
    if (!table) return;

    try {
        const response = await fetch("/api/alerts");
        const rows = await response.json();
        table.innerHTML = rows.length ? rows.map((row) => `
            <tr>
                <td>${row.timestamp}</td>
                <td>${row.source_ip}</td>
                <td>${row.destination_ip}</td>
                <td><span class="badge-attack">${row.attack_type}</span></td>
                <td>${confidenceText(row.confidence)}</td>
                <td>
                    ${row.severity === 'HIGH' ? '<span class="badge-severity-high">HIGH</span>' : '<span class="badge-severity-medium">MEDIUM</span>'}
                </td>
                <td><span class="mono-font text-uppercase">${row.status}</span></td>
            </tr>`).join("") : '<tr><td colspan="7" class="text-center text-muted py-4">-- NO ALERTS FOUND --</td></tr>';
    } catch (err) {
        console.error("Error refreshing alerts table:", err);
    }
}

async function refreshDashboardTables() {
    const trafficTable = document.getElementById("recentTrafficTable");
    const alertsTable = document.getElementById("recentAlertsTable");

    if (trafficTable) {
        try {
            const response = await fetch("/api/live");
            const rows = (await response.json()).slice(0, 8);
            trafficTable.innerHTML = rows.length ? rows.map((row) => `
                <tr>
                    <td>${row.timestamp}</td>
                    <td>${row.source_ip}</td>
                    <td>${row.destination_ip}</td>
                    <td>${row.protocol}</td>
                    <td>${row.packet_count}</td>
                    <td>${row.byte_count}</td>
                    <td>
                        ${row.prediction === 'ATTACK' ? '<span class="badge-attack">ATTACK</span>' : '<span class="badge-benign">BENIGN</span>'}
                    </td>
                </tr>
            `).join("") : '<tr><td colspan="7" class="text-center text-muted py-4">-- NO TRAFFIC DATA AVAILABLE --</td></tr>';
        } catch (err) {
            console.error("Error refreshing dashboard traffic table:", err);
        }
    }

    if (alertsTable) {
        try {
            const response = await fetch("/api/alerts");
            const rows = (await response.json()).slice(0, 8);
            alertsTable.innerHTML = rows.length ? rows.map((row) => `
                <tr>
                    <td>${row.timestamp}</td>
                    <td>${row.source_ip}</td>
                    <td>${row.attack_type}</td>
                    <td>
                        ${row.severity === 'HIGH' ? '<span class="badge-severity-high">HIGH</span>' : '<span class="badge-severity-medium">MEDIUM</span>'}
                    </td>
                    <td><span class="mono-font text-uppercase">${row.status}</span></td>
                </tr>
            `).join("") : '<tr><td colspan="5" class="text-center text-muted py-4">-- NO ALERTS FOUND --</td></tr>';
        } catch (err) {
            console.error("Error refreshing dashboard alerts table:", err);
        }
    }
}

async function refreshPage() {
    await Promise.all([
        refreshStatus(),
        refreshSummary(),
        refreshCharts(),
        refreshLiveTable(),
        refreshAlertsTable(),
        refreshDashboardTables()
    ]);
}

// Initial calls
updateLiveClock();
setInterval(updateLiveClock, 1000);
refreshPage();
setInterval(refreshPage, 3000);
