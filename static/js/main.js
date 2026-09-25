let benignAttackChart;
let trafficTimeChart;
let attackCountChart;

function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function predictionBadge(prediction) {
    const safe = escapeHtml(prediction);
    if (prediction === "ATTACK") {
        return '<span class="badge-attack">ATTACK</span>';
    } else if (prediction === "BENIGN") {
        return '<span class="badge-benign">BENIGN</span>';
    } else if (prediction === "PENDING") {
        return '<span class="badge-pending">PENDING</span>';
    } else {
        return `<span class="badge-error">${safe}</span>`;
    }
}

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

        // Nothing OS Monochrome + Signature Red Palette
        const ntWhite = "#ffffff";
        const ntRed = "#d71920";
        const ntDarkGray = "#333333";
        const ntSurfaceBorder = "#0a0a0a";
        const ntTickColor = "#8e8e93";
        const ntGridColor = "rgba(255, 255, 255, 0.05)";

        if (!benignAttackChart) {
            benignAttackChart = new Chart(benignCanvas, {
                type: "doughnut",
                data: {
                    labels: ["BENIGN", "ATTACK"],
                    datasets: [{
                        data: benignAttackValues,
                        backgroundColor: [ntWhite, ntRed],
                        borderWidth: 2,
                        borderColor: ntSurfaceBorder
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: {
                                font: { family: 'JetBrains Mono', size: 10 },
                                color: ntTickColor,
                                boxWidth: 10,
                                padding: 12
                            }
                        }
                    },
                    cutout: '72%'
                }
            });

            trafficTimeChart = new Chart(document.getElementById("trafficTimeChart"), {
                type: "line",
                data: {
                    labels: timeLabels.length ? timeLabels : ["NOW"],
                    datasets: [{
                        label: "Flows",
                        data: timeValues.length ? timeValues : [0],
                        borderColor: ntWhite,
                        borderWidth: 1.8,
                        backgroundColor: "rgba(255, 255, 255, 0.04)",
                        tension: 0.2,
                        fill: true,
                        pointBackgroundColor: ntWhite,
                        pointRadius: 2.5,
                        pointHoverRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: {
                            ticks: { font: { family: 'JetBrains Mono', size: 9 }, color: ntTickColor },
                            grid: { color: ntGridColor }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { font: { family: 'JetBrains Mono', size: 9 }, color: ntTickColor },
                            grid: { color: ntGridColor }
                        }
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
                        backgroundColor: [ntRed, ntDarkGray],
                        borderWidth: 1,
                        borderColor: ntSurfaceBorder,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: {
                            ticks: { font: { family: 'JetBrains Mono', size: 9 }, color: ntTickColor },
                            grid: { color: ntGridColor }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { font: { family: 'JetBrains Mono', size: 9 }, color: ntTickColor },
                            grid: { color: ntGridColor }
                        }
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
                <td>${escapeHtml(row.timestamp)}</td>
                <td>${escapeHtml(row.source_ip)}:${escapeHtml(row.source_port)}</td>
                <td>${escapeHtml(row.destination_ip)}:${escapeHtml(row.destination_port)}</td>
                <td>${escapeHtml(row.protocol)}</td>
                <td>${escapeHtml(row.packet_count)}</td>
                <td>${escapeHtml(row.byte_count)}</td>
                <td>${predictionBadge(row.prediction)}</td>
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
        table.innerHTML = rows.length ? rows.map((row) => {
            const isHigh = row.severity === 'HIGH';
            const severityBadge = isHigh
                ? '<span class="badge-severity-high">HIGH</span>'
                : '<span class="badge-severity-medium">MEDIUM</span>';
            return `
            <tr>
                <td>${escapeHtml(row.timestamp)}</td>
                <td>${escapeHtml(row.source_ip)}</td>
                <td>${escapeHtml(row.destination_ip)}</td>
                <td><span class="badge-attack">${escapeHtml(row.attack_type)}</span></td>
                <td>${confidenceText(row.confidence)}</td>
                <td>${severityBadge}</td>
                <td><span class="mono-font text-uppercase">${escapeHtml(row.status)}</span></td>
            </tr>`;
        }).join("") : '<tr><td colspan="7" class="text-center text-muted py-4">-- NO ALERTS FOUND --</td></tr>';
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
                    <td>${escapeHtml(row.timestamp)}</td>
                    <td>${escapeHtml(row.source_ip)}</td>
                    <td>${escapeHtml(row.destination_ip)}</td>
                    <td>${escapeHtml(row.protocol)}</td>
                    <td>${escapeHtml(row.packet_count)}</td>
                    <td>${escapeHtml(row.byte_count)}</td>
                    <td>${predictionBadge(row.prediction)}</td>
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
            alertsTable.innerHTML = rows.length ? rows.map((row) => {
                const isHigh = row.severity === 'HIGH';
                const severityBadge = isHigh
                    ? '<span class="badge-severity-high">HIGH</span>'
                    : '<span class="badge-severity-medium">MEDIUM</span>';
                return `
                <tr>
                    <td>${escapeHtml(row.timestamp)}</td>
                    <td>${escapeHtml(row.source_ip)}</td>
                    <td>${escapeHtml(row.attack_type)}</td>
                    <td>${severityBadge}</td>
                    <td><span class="mono-font text-uppercase">${escapeHtml(row.status)}</span></td>
                </tr>
            `;
            }).join("") : '<tr><td colspan="5" class="text-center text-muted py-4">-- NO ALERTS FOUND --</td></tr>';
        } catch (err) {
            console.error("Error refreshing dashboard alerts table:", err);
        }
    }
}

async function refreshPage() {
    const tasks = [refreshStatus()];

    // Summary & Charts only exist on Dashboard
    if (document.getElementById("totalPackets")) {
        tasks.push(refreshSummary());
    }
    if (document.getElementById("benignAttackChart")) {
        tasks.push(refreshCharts());
    }

    // Live traffic table only exists on /live
    if (document.getElementById("liveTrafficTable")) {
        tasks.push(refreshLiveTable());
    }

    // Alerts table only exists on /alerts
    if (document.getElementById("alertsTable")) {
        tasks.push(refreshAlertsTable());
    }

    // Dashboard preview tables only exist on Dashboard
    if (document.getElementById("recentTrafficTable") || document.getElementById("recentAlertsTable")) {
        tasks.push(refreshDashboardTables());
    }

    await Promise.all(tasks);
}

// Initial calls
updateLiveClock();
setInterval(updateLiveClock, 1000);
refreshPage();
setInterval(refreshPage, 3000);
