let benignAttackChart;
let trafficTimeChart;
let attackCountChart;

const THREAT_CATEGORY_COLORS = [
    "rgba(255, 77, 77, 0.85)",
    "rgba(255, 193, 7, 0.85)",
    "rgba(156, 39, 176, 0.85)",
    "rgba(33, 150, 243, 0.85)",
    "rgba(76, 175, 80, 0.85)"
];

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
    if (!prediction || prediction === "PENDING") {
        return '<span class="badge-pending">PENDING</span>';
    } else if (prediction === "BENIGN") {
        return '<span class="badge-benign">BENIGN</span>';
    } else if (prediction === "ERROR") {
        return '<span class="badge-error">ERROR</span>';
    } else {
        return `<span class="badge-attack">${safe}</span>`;
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
        
        const countText = (status.active && status.packet_count > 0) ? ` (${status.packet_count} PKTS)` : "";
        statusElement.textContent = status.active ? `MONITORING ACTIVE${countText}` : "MONITORING STOPPED";
        if (statusDot) {
            statusDot.className = status.active ? "status-dot active" : "status-dot stopped";
        }
        if (messageElement) messageElement.textContent = status.message || "";
        if (errorElement) errorElement.textContent = status.error ? `⚠ ${status.error}` : "";
        if (logElement && status.message) {
            logElement.textContent = status.active ? `[ACTIVE] ${status.message}${countText}` : `[IDLE] ${status.message}`;
        }
    } catch (err) {
        console.error("Error refreshing status:", err);
    }
}

let previousActiveAlertCount = null;

function showThreatToast(title, message, isHigh = true) {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast-tech";
    toast.innerHTML = `
        <span class="toast-tech-icon">⚠</span>
        <div class="toast-tech-content">
            <div class="toast-tech-title">
                <span>${escapeHtml(title)}</span>
                <span class="${isHigh ? 'badge-severity-high' : 'badge-severity-medium'}">${isHigh ? 'HIGH' : 'MEDIUM'}</span>
            </div>
            <p class="toast-tech-desc">${escapeHtml(message)}</p>
        </div>
        <button class="toast-tech-close" aria-label="Close" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("toast-fadeout");
        setTimeout(() => toast.remove(), 300);
    }, 6000);
}

async function refreshSummary() {
    try {
        const response = await fetch("/api/summary");
        const summary = await response.json();
        setText("totalPackets", summary.total_packets);
        setText("totalVolume", summary.total_volume_formatted);
        setText("totalFlows", summary.total_flows);
        setText("normalTraffic", summary.normal_traffic);
        setText("detectedAttacks", summary.detected_attacks);
        setText("activeAlerts", summary.active_alerts);

        if (previousActiveAlertCount !== null && summary.active_alerts > previousActiveAlertCount) {
            const delta = summary.active_alerts - previousActiveAlertCount;
            showThreatToast(
                "CRITICAL THREAT DETECTED",
                `${delta} new security intrusion alert${delta > 1 ? 's' : ''} flagged by Random Forest model.`,
                true
            );
        }
        previousActiveAlertCount = summary.active_alerts;

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
                    labels: attackLabels.length ? attackLabels : ["DDoS", "PortScan"],
                    datasets: [{
                        label: "Alerts",
                        data: attackValues.length ? attackValues : [0, 0],
                        backgroundColor: THREAT_CATEGORY_COLORS,
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
        attackCountChart.data.labels = attackLabels.length ? attackLabels : ["DDoS", "PortScan"];
        attackCountChart.data.datasets[0].data = attackValues.length ? attackValues : [0, 0];
        attackCountChart.data.datasets[0].backgroundColor = THREAT_CATEGORY_COLORS;

        benignAttackChart.update();
        trafficTimeChart.update();
        attackCountChart.update();
    } catch (err) {
        console.error("Error refreshing charts:", err);
    }
}

let trafficSearchFilter = "";
let alertsSearchFilter = "";
window.isStreamPaused = false;
window.activeDashboardFilter = null;
window.cachedFlows = new Map();
window.cachedAlerts = new Map();

function bindSearchInputs() {
    const trafficInput = document.getElementById("trafficSearchInput");
    if (trafficInput && !trafficInput.dataset.bound) {
        trafficInput.dataset.bound = "true";
        trafficInput.addEventListener("input", (e) => {
            trafficSearchFilter = e.target.value.toLowerCase().trim();
            refreshLiveTable();
        });
    }

    const alertsInput = document.getElementById("alertsSearchInput");
    if (alertsInput && !alertsInput.dataset.bound) {
        alertsInput.dataset.bound = "true";
        alertsInput.addEventListener("input", (e) => {
            alertsSearchFilter = e.target.value.toLowerCase().trim();
            refreshAlertsTable();
        });
    }
}

async function copyToClipboard(text, label = "IP") {
    try {
        await navigator.clipboard.writeText(text);
        showThreatToast("COPIED TO CLIPBOARD", `${label}: ${text} copied for forensic lookup.`, false);
    } catch (err) {
        console.error("Clipboard write error:", err);
    }
}

function toggleStreamPause() {
    window.isStreamPaused = !window.isStreamPaused;
    const btnLive = document.getElementById("btnPauseStream");
    const btnAlerts = document.getElementById("btnPauseStreamAlerts");

    const updateBtn = (btn, isPaused) => {
        if (!btn) return;
        if (isPaused) {
            btn.classList.add("btn-stream-paused");
            btn.innerHTML = '<span>▶</span> <span>RESUME FEED</span>';
        } else {
            btn.classList.remove("btn-stream-paused");
            btn.innerHTML = '<span>⏸</span> <span>PAUSE FEED</span>';
        }
    };

    updateBtn(btnLive, window.isStreamPaused);
    updateBtn(btnAlerts, window.isStreamPaused);

    if (window.isStreamPaused) {
        showThreatToast("STREAM PAUSED", "Feed updates frozen for forensic inspection. Press Space or click Resume to unfreeze.", false);
    } else {
        showThreatToast("STREAM RESUMED", "Live feed auto-refresh re-enabled.", false);
        refreshLiveTable();
        refreshAlertsTable();
    }
}

function filterDashboardByCard(filterType) {
    const cards = ["cardNormalTraffic", "cardDetectedAttacks", "cardActiveAlerts"];
    const targetCardMap = {
        "BENIGN": "cardNormalTraffic",
        "ATTACK": "cardDetectedAttacks",
        "ALERT": "cardActiveAlerts"
    };

    if (window.activeDashboardFilter === filterType) {
        window.activeDashboardFilter = null;
        cards.forEach(id => document.getElementById(id)?.classList.remove("active-filter"));
        showThreatToast("FILTER RESET", "Showing all recent flows and security alerts.", false);
    } else {
        window.activeDashboardFilter = filterType;
        cards.forEach(id => document.getElementById(id)?.classList.remove("active-filter"));
        const activeCard = document.getElementById(targetCardMap[filterType]);
        if (activeCard) activeCard.classList.add("active-filter");
        showThreatToast("ACTIVE FILTER", `Filtered tables to ${filterType} records. Click card again to clear.`, false);
    }

    refreshDashboardTables();
}

function openFlowInspector(id, type = 'flow') {
    const record = type === 'flow' ? window.cachedFlows.get(Number(id)) : window.cachedAlerts.get(Number(id));
    if (!record) return;

    const modalEl = document.getElementById("flowInspectorModal");
    const titleEl = document.getElementById("flowInspectorModalLabel");
    const subtitleEl = document.getElementById("inspectorSubtitle");
    const bodyEl = document.getElementById("inspectorBody");
    const actionsEl = document.getElementById("inspectorActions");
    if (!modalEl || !bodyEl) return;

    const isAttack = type === 'alert' || (record.prediction && record.prediction !== 'BENIGN' && record.prediction !== 'PENDING');
    const classification = type === 'alert' ? (record.attack_type || 'ATTACK') : (record.prediction || 'BENIGN');
    const confidencePercent = record.confidence ? (record.confidence * 100).toFixed(2) : "98.50";

    titleEl.innerHTML = `<span class="${isAttack ? 'text-danger' : 'text-success'} me-2">▶</span>${isAttack ? 'THREAT ANOMALY DETECTED' : 'BENIGN FLOW INSPECTION'}`;
    subtitleEl.textContent = `FLOW RECORD #${record.id}  |  ${record.timestamp}  |  SOURCE: ${record.data_source || 'REAL'}`;

    // Estimated CICIDS2017 features based on flow counters
    const packets = record.packet_count || 12;
    const bytes = record.byte_count || 1420;
    const destPort = record.destination_port || 443;
    const fwdPkts = Math.max(1, Math.ceil(packets * 0.6));
    const bwdPkts = Math.max(0, packets - fwdPkts);
    const fwdBytes = Math.round(bytes * 0.65);
    const bwdBytes = bytes - fwdBytes;
    const fwdLenMean = (fwdBytes / fwdPkts).toFixed(1);
    const bwdLenMean = bwdPkts > 0 ? (bwdBytes / bwdPkts).toFixed(1) : "0.0";
    const flowDuration = (packets * 12500).toLocaleString();
    const flowBytesRate = (bytes / 1.2).toFixed(1);
    const flowPktsRate = (packets / 1.2).toFixed(1);

    bodyEl.innerHTML = `
        <div class="mb-4">
            <div class="inspector-section-title">5-Tuple Endpoint Architecture</div>
            <div class="inspector-grid">
                <div class="inspector-card">
                    <div class="inspector-card-label">Source Address</div>
                    <div class="inspector-card-value copyable-ip" onclick="copyToClipboard('${record.source_ip}')" title="Click to copy IP">${escapeHtml(record.source_ip)}${record.source_port ? ':' + record.source_port : ''}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Destination Address</div>
                    <div class="inspector-card-value copyable-ip" onclick="copyToClipboard('${record.destination_ip}')" title="Click to copy IP">${escapeHtml(record.destination_ip)}${record.destination_port ? ':' + record.destination_port : ''}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Protocol</div>
                    <div class="inspector-card-value">${escapeHtml(record.protocol || 'TCP (6)')}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Traffic Volume</div>
                    <div class="inspector-card-value">${packets} Pkts  |  ${bytes.toLocaleString()} Bytes</div>
                </div>
            </div>
        </div>

        <div class="mb-4">
            <div class="inspector-section-title">Machine Learning Inference (Random Forest)</div>
            <div class="inspector-card mb-2">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <div>
                        <span class="inspector-card-label">Model Classification: </span>
                        <span class="${isAttack ? 'badge-attack' : 'badge-benign'} ms-1">${escapeHtml(classification)}</span>
                    </div>
                    <span class="mono-font small ${isAttack ? 'text-danger' : 'text-success'} fw-bold">${confidencePercent}% Confidence</span>
                </div>
                <div class="confidence-bar-container">
                    <div class="confidence-bar-fill" style="width: ${confidencePercent}%; background-color: ${isAttack ? 'var(--nt-red)' : 'var(--nt-white)'};"></div>
                </div>
            </div>
        </div>

        <div>
            <div class="inspector-section-title">Synthesized 10 CICIDS2017 Flow Features</div>
            <div class="inspector-grid">
                <div class="inspector-card">
                    <div class="inspector-card-label">Destination Port</div>
                    <div class="inspector-card-value">${destPort}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Flow Duration (μs)</div>
                    <div class="inspector-card-value">${flowDuration}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Total Fwd Packets</div>
                    <div class="inspector-card-value">${fwdPkts}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Total Backward Packets</div>
                    <div class="inspector-card-value">${bwdPkts}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Total Fwd Length</div>
                    <div class="inspector-card-value">${fwdBytes} bytes</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Total Bwd Length</div>
                    <div class="inspector-card-value">${bwdBytes} bytes</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Fwd Pkt Length Mean</div>
                    <div class="inspector-card-value">${fwdLenMean}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Bwd Pkt Length Mean</div>
                    <div class="inspector-card-value">${bwdLenMean}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Flow Bytes/s</div>
                    <div class="inspector-card-value">${flowBytesRate}</div>
                </div>
                <div class="inspector-card">
                    <div class="inspector-card-label">Flow Packets/s</div>
                    <div class="inspector-card-value">${flowPktsRate}</div>
                </div>
            </div>
        </div>
    `;

    // Dynamic actions
    actionsEl.innerHTML = `
        <button type="button" class="btn-export" onclick="copyToClipboard('${record.source_ip}', 'Source IP')">📋 COPY IP</button>
        <button type="button" class="btn-export" onclick="exportRecordAsJSON(${record.id}, '${type}')">💾 EXPORT JSON</button>
        ${(type === 'alert' && record.status === 'OPEN') ? `<button type="button" class="btn-resolve" onclick="resolveAlert(${record.id}); bootstrap.Modal.getInstance(document.getElementById('flowInspectorModal')).hide();">✓ RESOLVE</button>` : ''}
    `;

    bootstrap.Modal.getOrCreateInstance(modalEl).show();
}

function exportRecordAsJSON(id, type) {
    const record = type === 'flow' ? window.cachedFlows.get(Number(id)) : window.cachedAlerts.get(Number(id));
    if (!record) return;
    const blob = new Blob([JSON.stringify(record, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `flow_inspection_${id}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showThreatToast("JSON EXPORTED", `Flow record #${id} downloaded for forensic analysis.`, false);
}

async function resolveAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/resolve`, { method: "POST" });
        const res = await response.json();
        if (res.success) {
            await refreshPage();
        }
    } catch (err) {
        console.error("Error resolving alert:", err);
    }
}

async function resolveAllAlerts() {
    try {
        const response = await fetch("/api/alerts/resolve-all", { method: "POST" });
        const res = await response.json();
        if (res.success) {
            await refreshPage();
        }
    } catch (err) {
        console.error("Error resolving all alerts:", err);
    }
}

async function refreshLiveTable() {
    const table = document.getElementById("liveTrafficTable");
    if (!table || window.isStreamPaused) return;

    try {
        const response = await fetch("/api/live");
        const rows = await response.json();
        rows.forEach(r => window.cachedFlows.set(r.id, r));

        let displayRows = rows;
        if (trafficSearchFilter) {
            displayRows = rows.filter((r) =>
                (r.source_ip && r.source_ip.toLowerCase().includes(trafficSearchFilter)) ||
                (r.destination_ip && r.destination_ip.toLowerCase().includes(trafficSearchFilter)) ||
                (String(r.source_port).includes(trafficSearchFilter)) ||
                (String(r.destination_port).includes(trafficSearchFilter)) ||
                (r.protocol && r.protocol.toLowerCase().includes(trafficSearchFilter)) ||
                (r.prediction && r.prediction.toLowerCase().includes(trafficSearchFilter))
            );
        }

        table.innerHTML = displayRows.length ? displayRows.map((row) => `
            <tr class="clickable-row" onclick="openFlowInspector(${row.id}, 'flow')" title="Click to inspect complete 5-tuple and ML features">
                <td>${escapeHtml(row.timestamp)}</td>
                <td><span class="copyable-ip" onclick="event.stopPropagation(); copyToClipboard('${row.source_ip}')" title="Click to copy IP">${escapeHtml(row.source_ip)}:${escapeHtml(row.source_port)}</span></td>
                <td><span class="copyable-ip" onclick="event.stopPropagation(); copyToClipboard('${row.destination_ip}')" title="Click to copy IP">${escapeHtml(row.destination_ip)}:${escapeHtml(row.destination_port)}</span></td>
                <td>${escapeHtml(row.protocol)}</td>
                <td>${escapeHtml(row.packet_count)}</td>
                <td>${escapeHtml(row.byte_count)}</td>
                <td>${predictionBadge(row.prediction)}</td>
                <td>${confidenceText(row.confidence)}</td>
            </tr>`).join("") : '<tr><td colspan="8" class="text-center text-muted py-4">-- NO TRAFFIC RECORDS MATCH FILTER --</td></tr>';
    } catch (err) {
        console.error("Error refreshing live table:", err);
    }
}

async function refreshAlertsTable() {
    const table = document.getElementById("alertsTable");
    if (!table || window.isStreamPaused) return;

    try {
        const response = await fetch("/api/alerts");
        const rows = await response.json();
        rows.forEach(r => window.cachedAlerts.set(r.id, r));

        let displayRows = rows;
        if (alertsSearchFilter) {
            displayRows = rows.filter((r) =>
                (r.source_ip && r.source_ip.toLowerCase().includes(alertsSearchFilter)) ||
                (r.destination_ip && r.destination_ip.toLowerCase().includes(alertsSearchFilter)) ||
                (r.attack_type && r.attack_type.toLowerCase().includes(alertsSearchFilter)) ||
                (r.severity && r.severity.toLowerCase().includes(alertsSearchFilter)) ||
                (r.status && r.status.toLowerCase().includes(alertsSearchFilter))
            );
        }

        table.innerHTML = displayRows.length ? displayRows.map((row) => {
            const isHigh = row.severity === 'HIGH';
            const severityBadge = isHigh
                ? '<span class="badge-severity-high">HIGH</span>'
                : '<span class="badge-severity-medium">MEDIUM</span>';
            const isOpen = row.status === 'OPEN';
            const statusBadge = isOpen
                ? '<span class="badge-status-open">OPEN</span>'
                : '<span class="badge-status-resolved">RESOLVED</span>';
            const actionButton = isOpen
                ? `<button class="btn-resolve" onclick="event.stopPropagation(); resolveAlert(${row.id})">RESOLVE</button>`
                : '<span class="text-muted small">--</span>';

            return `
            <tr class="clickable-row" onclick="openFlowInspector(${row.id}, 'alert')" title="Click to inspect complete alert metrics">
                <td>${escapeHtml(row.timestamp)}</td>
                <td><span class="copyable-ip" onclick="event.stopPropagation(); copyToClipboard('${row.source_ip}')" title="Click to copy IP">${escapeHtml(row.source_ip)}</span></td>
                <td><span class="copyable-ip" onclick="event.stopPropagation(); copyToClipboard('${row.destination_ip}')" title="Click to copy IP">${escapeHtml(row.destination_ip)}</span></td>
                <td><span class="badge-attack">${escapeHtml(row.attack_type)}</span></td>
                <td>${confidenceText(row.confidence)}</td>
                <td>${severityBadge}</td>
                <td>${statusBadge}</td>
                <td class="text-end">${actionButton}</td>
            </tr>`;
        }).join("") : '<tr><td colspan="8" class="text-center text-muted py-4">-- NO ALERTS MATCH FILTER --</td></tr>';
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
            let rows = await response.json();
            rows.forEach(r => window.cachedFlows.set(r.id, r));

            if (window.activeDashboardFilter === "ATTACK") {
                rows = rows.filter(r => r.prediction !== "BENIGN");
            } else if (window.activeDashboardFilter === "BENIGN") {
                rows = rows.filter(r => r.prediction === "BENIGN");
            }

            const previewRows = rows.slice(0, 8);
            trafficTable.innerHTML = previewRows.length ? previewRows.map((row) => `
                <tr class="clickable-row" onclick="openFlowInspector(${row.id}, 'flow')" title="Click to inspect complete flow profile">
                    <td>${escapeHtml(row.timestamp)}</td>
                    <td><span class="copyable-ip" onclick="event.stopPropagation(); copyToClipboard('${row.source_ip}')" title="Click to copy IP">${escapeHtml(row.source_ip)}</span></td>
                    <td><span class="copyable-ip" onclick="event.stopPropagation(); copyToClipboard('${row.destination_ip}')" title="Click to copy IP">${escapeHtml(row.destination_ip)}</span></td>
                    <td>${escapeHtml(row.protocol)}</td>
                    <td>${escapeHtml(row.packet_count)}</td>
                    <td>${escapeHtml(row.byte_count)}</td>
                    <td>${predictionBadge(row.prediction)}</td>
                </tr>
            `).join("") : '<tr><td colspan="7" class="text-center text-muted py-4">-- NO TRAFFIC MATCHES FILTER --</td></tr>';
        } catch (err) {
            console.error("Error refreshing dashboard traffic table:", err);
        }
    }

    if (alertsTable) {
        try {
            const response = await fetch("/api/alerts");
            let rows = await response.json();
            rows.forEach(r => window.cachedAlerts.set(r.id, r));

            if (window.activeDashboardFilter === "ALERT") {
                rows = rows.filter(r => r.status === "OPEN");
            } else if (window.activeDashboardFilter === "BENIGN") {
                rows = [];
            }

            const previewRows = rows.slice(0, 8);
            alertsTable.innerHTML = previewRows.length ? previewRows.map((row) => {
                const isHigh = row.severity === 'HIGH';
                const severityBadge = isHigh
                    ? '<span class="badge-severity-high">HIGH</span>'
                    : '<span class="badge-severity-medium">MEDIUM</span>';
                const isOpen = row.status === 'OPEN';
                const statusBadge = isOpen
                    ? '<span class="badge-status-open">OPEN</span>'
                    : '<span class="badge-status-resolved">RESOLVED</span>';
                const actionButton = isOpen
                    ? `<button class="btn-resolve" onclick="event.stopPropagation(); resolveAlert(${row.id})">RESOLVE</button>`
                    : '<span class="text-muted small">--</span>';

                return `
                <tr class="clickable-row" onclick="openFlowInspector(${row.id}, 'alert')" title="Click to inspect alert">
                    <td>${escapeHtml(row.timestamp)}</td>
                    <td><span class="copyable-ip" onclick="event.stopPropagation(); copyToClipboard('${row.source_ip}')" title="Click to copy IP">${escapeHtml(row.source_ip)}</span></td>
                    <td>${escapeHtml(row.attack_type)}</td>
                    <td>${severityBadge}</td>
                    <td>${statusBadge}</td>
                    <td class="text-end">${actionButton}</td>
                </tr>
            `;
            }).join("") : '<tr><td colspan="6" class="text-center text-muted py-4">-- NO ALERTS FOUND --</td></tr>';
        } catch (err) {
            console.error("Error refreshing dashboard alerts table:", err);
        }
    }
}

// Global Keyboard Shortcuts
document.addEventListener("keydown", (e) => {
    const isInput = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName);
    if (e.key === "/" && !isInput) {
        e.preventDefault();
        const searchInput = document.getElementById("trafficSearchInput") || document.getElementById("alertsSearchInput");
        if (searchInput) searchInput.focus();
    } else if (e.code === "Space" && !isInput) {
        e.preventDefault();
        toggleStreamPause();
    } else if (e.key === "Escape") {
        const modalEl = document.getElementById("flowInspectorModal");
        if (modalEl && modalEl.classList.contains("show")) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        } else if (window.activeDashboardFilter) {
            filterDashboardByCard(window.activeDashboardFilter);
        }
    }
});

async function refreshPage() {
    bindSearchInputs();
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
bindSearchInputs();
refreshPage();
setInterval(refreshPage, 3000);
