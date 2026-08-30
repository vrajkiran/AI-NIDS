# AI-NIDS User Guide & Operations Manual

## 1. System Requirements

- **Operating System**: Windows 10 / 11, Linux, or macOS.
- **Python**: Python 3.10 or higher.
- **Network Privileges**: Administrator / root access or Npcap installed for raw packet capture.

---

## 2. Quick Start Guide

### Launching on Windows
Double-click `run_ai_nids.bat` in the root project folder.

### Launching via Terminal
```cmd
.venv\Scripts\python run.py
```

The launcher will automatically start Flask on `http://127.0.0.1:5000` and open your default browser.

---

## 3. Web Dashboard Features

### 3.1 Top Navigation Bar
- **Dashboard**: Main overview containing KPI cards, controls, charts, and recent activity.
- **Live Traffic**: Full view of all monitored network traffic flow records.
- **Alerts**: Dedicated security threat log displaying high and medium severity attack events.
- **Model Performance**: Evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix) read from training results.
- **Live Status Indicator**: Displays `MONITORING ACTIVE` (Green) or `MONITORING STOPPED` (Red).
- **Live Clock Badge**: Real-time system date and clock (`📅 DD-MM-YYYY 🕒 HH:MM:SS`).

---

### 3.2 Dashboard Control Panel
- **Interface Dropdown**: Select the authorized network adapter (e.g., `Wi-Fi`, `Ethernet`, `Scapy Default`).
- **Capture Duration**: Set duration in seconds (Default: 10 seconds).
- **▶ START MONITORING**: Begins passive Scapy packet sniffing and real-time Random Forest classification.
- **■ STOP**: Halts active network capture.
- **⚡ DEMO DATA**: Seeds presentation demo traffic and alerts (`data_source = 'DEMO'`) into SQLite for instant demonstration without live traffic.
- **🗑 CLEAR DEMO**: Deletes demo records from SQLite while keeping real packet detections intact.

---

### 3.3 Dashboard Charts & Visualizations
- **Benign vs Attack (Doughnut Chart)**: Visual breakdown of normal traffic vs detected attacks.
- **Traffic Over Time (Line Chart)**: Flow generation volume over time.
- **Attack Events (Bar Chart)**: Severity distribution (`HIGH` vs `MEDIUM`).

---

## 4. Operational Instructions

### Running a Real Traffic Capture Test:
1. Open `http://127.0.0.1:5000`.
2. Select your active interface (e.g., `Wi-Fi`).
3. Enter duration (e.g., `15` seconds).
4. Click `▶ START MONITORING`.
5. Perform network activities in another tab (e.g., browse web pages).
6. Observe live traffic counters and table rows populating in real time.

---

### Demonstrating Presentation Demo Mode:
1. Click `⚡ DEMO DATA` on the Dashboard.
2. Notice the `⚡ DEMO MODE ACTIVE` indicator badge appear.
3. Show filled KPI cards, tables, and charts to reviewers or evaluators.
4. Click `🗑 CLEAR DEMO` to wipe demo records when presentation is finished.
