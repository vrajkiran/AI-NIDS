# AI-Based Real-Time Network Intrusion Detection System Using Machine Learning

## 1. Project Title

AI-Based Real-Time Network Intrusion Detection System Using Machine Learning

---

## 2. Abstract

With the exponential growth of high-speed network traffic, modern computer networks are subjected to sophisticated cyber threats, unauthorized network intrusions, and Distributed Denial of Service (DDoS) attacks. Traditional network security mechanisms—such as static packet-filtering firewalls and signature-based Intrusion Detection Systems (IDS)—suffer from inherent vulnerabilities: they cannot easily detect novel attack patterns, require continuous manual rule updates, and struggle under heavy traffic volume.

This MCA mini project presents **AI-NIDS**, an automated, real-time Network Intrusion Detection System powered by Machine Learning. The system passively monitors authorized network traffic using Scapy, aggregates packets into stateful 5-tuple network flows, calculates statistical traffic metrics, and classifies each conversation as `BENIGN` or `ATTACK` using a Random Forest binary classifier trained on the benchmark CICIDS2017 dataset. Results are saved in an SQLite database and presented live in an intuitive Flask-driven web dashboard.

---

## 3. Introduction

Network Intrusion Detection Systems (NIDS) act as digital security sentinels that inspect network communication channels for malicious activity or policy violations. A NIDS monitors traffic across network segments, analyzes protocol behaviors, and alerts system administrators when potential security incidents occur.

This project implements a lightweight, stateful NIDS tailored for academic evaluation. By combining Python packet sniffing (Scapy), structured machine learning (Random Forest), local database persistence (SQLite), and web UI streaming (Flask + Chart.js), AI-NIDS delivers an end-to-end security analysis pipeline suitable for real-time monitoring and presentation.

---

## 4. Problem Statement

Modern enterprise and local networks face continuous threat vectors ranging from port scanning to volumetric denial-of-service attacks. The central problems addressed by this project include:
1. **Manual Inspection Limitation**: Human security analysts cannot inspect millions of daily raw network packets manually.
2. **Signature Static Failure**: Fixed signature rules fail against dynamic, obfuscated, or zero-day attack patterns.
3. **Payload Inspection Overhead & Privacy Risks**: Inspecting raw packet payloads consumes high CPU/memory and introduces privacy/credential leakage risks.

---

## 5. Aim

To design, implement, and evaluate an automated, stateful Network Intrusion Detection System that classifies real-time network flow metadata into `BENIGN` or `ATTACK` using a Random Forest machine learning model without inspecting or storing packet payloads.

---

## 6. Objectives

- Passively capture IP network packet headers from an authorized network interface using Scapy.
- Enforce strict metadata-only collection (no payload storage or credential harvesting).
- Aggregate raw packets into bidirectional 5-tuple network conversations (flows).
- Compute live statistical features (duration, packet counts, byte rates, mean packet sizes) compatible with dataset features.
- Train and evaluate a Random Forest binary classifier using CICIDS2017 flow data.
- Store flow records and high-confidence alerts in an SQLite database with clear `REAL` vs `DEMO` data source tagging.
- Render live metrics, alert logs, and Chart.js graphs on a retro-futuristic technical web dashboard.
- Provide a one-click Windows batch launcher (`run_ai_nids.bat`) for easy application startup.

---

## 7. Existing System

Traditional Network Intrusion Detection Systems rely primarily on two paradigms:
1. **Signature-Based Inspection**: Matches packet bytes against a database of known threat signatures (e.g., Snort rules).
   - *Limitation*: Blind to unknown zero-day attacks and dynamic traffic alterations.
2. **Stateless Packet Filtering**: Inspects individual packets in isolation without context.
   - *Limitation*: Fails to recognize multi-packet attack patterns (such as slow port scans or flow volumetric floods).

---

## 8. Proposed System

The proposed **AI-NIDS** system replaces static rule matching with supervised machine learning:
- **Stateful Flow Aggregation**: Grouping forward and backward packets into bidirectional conversations.
- **Statistical Feature Extraction**: Computing 10 mathematical metrics per flow.
- **Random Forest Classification**: Evaluating flow metrics against trained decision trees.
- **Privacy Preservation**: Analyzing header metadata only; payloads are ignored and never written to disk.
- **Separation of Real & Demo Modes**: Clear visual indicators (`DEMO MODE ACTIVE`) and independent data management.

---

## 9. Why This Project Is Needed

As network speeds increase, security tools must operate efficiently without introducing latency or violating user privacy. AI-NIDS demonstrates how lightweight flow-based feature extraction combined with ensemble decision trees can detect attacks with high accuracy (>99.9%) using minimal computational resources.

---

## 10. Scope

### In Scope:
- Passive sniffing on authorized local adapters (Wi-Fi, Ethernet, Loopback).
- Bidirectional IP/TCP/UDP flow aggregation.
- Random Forest binary classification (`BENIGN` vs `ATTACK`).
- SQLite persistence, Flask REST endpoints, and web dashboard visualization.
- Dual-mode operation (`REAL` live capture vs `DEMO` presentation mode).

### Out of Scope:
- Raw packet payload decryption or deep packet inspection (DPI).
- Automatic firewall blocking or TCP packet resets (prevention features).
- Multi-node distributed sensor deployment.

---

## 11. System Architecture

```text
Real Network Packets
        ↓
Scapy Packet Capture (Metadata Only)
        ↓
Flow Aggregation Engine (5-Tuple Grouping)
        ↓
Feature Extraction (10 Flow Metrics)
        ↓
Random Forest Classifier (Joblib Model)
        ↓
Prediction & Confidence Calculation
        ↓
SQLite Database (nids.db)
        ↓
Flask REST APIs & Web Dashboard
```

---

## 12. Complete Working Mechanism

1. **Initialization**: The user starts the system using `run_ai_nids.bat`. Flask launches on `127.0.0.1:5000`, initializes `nids.db`, loads `random_forest_model.joblib`, and opens the browser.
2. **Interface Selection**: The user selects an authorized network adapter (e.g., `Wi-Fi`) and sets capture duration.
3. **Packet Capture**: Scapy sniffs IP packets in a background thread.
4. **Header Dissection**: Packet timestamp, source IP, destination IP, ports, protocol, and length are extracted.
5. **Flow Tracking**: Packets matching `(Source IP, Dest IP, Source Port, Dest Port, Protocol)` or its reverse are added to a `Flow` instance.
6. **Feature Computation**: Flow statistics (`Flow Duration`, `Total Fwd Packets`, `Flow Bytes/s`, etc.) are computed.
7. **ML Inference**: `PredictionService.predict()` passes features to the Random Forest model, returning `BENIGN` or `ATTACK` plus confidence.
8. **Persistence**: Flow records and generated alerts are written to SQLite with `data_source="REAL"`.
9. **Dashboard Update**: JavaScript polls `/api/summary`, `/api/live`, `/api/alerts`, and `/api/charts` every 3 seconds to update UI cards and Chart.js graphs.

---

## 13. Packet Capture

Scapy handles passive network sniffing via `sniff(iface=..., prn=handle_packet, store=False)`.

### Captured Header Fields:
- **Timestamp**: High-precision Unix epoch time (`packet.time`).
- **Source IP & Destination IP**: Protocol addresses from the IPv4 header (`packet[IP].src`, `packet[IP].dst`).
- **Source Port & Destination Port**: Service ports from TCP (`packet[TCP].sport`) or UDP (`packet[UDP].dport`).
- **Protocol Number**: IP protocol integer (ICMP=1, TCP=6, UDP=17).
- **Packet Length**: Total byte length of the frame (`len(packet)`).

*Payload bytes are explicitly discarded.*

---

## 14. Network Flow

A **flow** is defined as a sequence of packets transferred between two endpoints during a network session. Bidirectional flow matching checks both forward `(A→B)` and reverse `(B→A)` traffic directions using a 5-tuple hash key:
$$\text{Flow Key} = (\text{IP}_A, \text{IP}_B, \text{Port}_A, \text{Port}_B, \text{Protocol})$$

---

## 15. Feature Extraction

| Feature Name | Meaning | Calculation Formula | Live Scapy Calculation |
|---|---|---|---|
| Destination Port | Target service port | `packet[TCP/UDP].dport` | Extracted directly from layer |
| Protocol | IP Protocol number | `packet[IP].proto` | Extracted directly from layer |
| Flow Duration | Microseconds elapsed | $(\text{Time}_{\text{last}} - \text{Time}_{\text{first}}) \times 10^6$ | Calculated from packet timestamps |
| Total Fwd Packets | Forward packet count | Count of packets from $A \to B$ | Counter incremented on match |
| Total Backward Packets | Reverse packet count | Count of packets from $B \to A$ | Counter incremented on reverse match |
| Total Length of Fwd Packets | Total forward bytes | Sum of packet lengths from $A \to B$ | Byte accumulator |
| Total Length of Bwd Packets | Total reverse bytes | Sum of packet lengths from $B \to A$ | Byte accumulator |
| Fwd Packet Length Mean | Average forward packet size | $\frac{\text{Total Fwd Bytes}}{\text{Total Fwd Packets}}$ | Calculated ratio |
| Bwd Packet Length Mean | Average reverse packet size | $\frac{\text{Total Bwd Bytes}}{\text{Total Bwd Packets}}$ | Calculated ratio |
| Flow Bytes/s | Transfer throughput (B/s) | $\frac{\text{Total Bytes}}{\text{Duration in Seconds}}$ | Calculated rate |
| Flow Packets/s | Transfer throughput (Pkt/s) | $\frac{\text{Total Packets}}{\text{Duration in Seconds}}$ | Calculated rate |

---

## 16. Dataset

The model is trained on the **CICIDS2017** benchmark dataset (Canadian Institute for Cybersecurity).
- **File Used**: `data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv.parquet`
- **Total Samples Loaded**: 225,745
- **Duplicates Removed**: 9,358
- **Cleaned Dataset**: 216,387 samples (`BENIGN`: 89,199 | `ATTACK`: 127,188)

---

## 17. Data Preprocessing

Implemented in `ml/preprocess.py`:
1. **Column Normalization**: Stripping whitespace from CSV/Parquet column headers.
2. **Feature Filtering**: Selecting the 10 live-compatible features.
3. **Numeric Conversion**: Coercing strings to float values.
4. **Infinite/Missing Handling**: Replacing $\pm \infty$ with NaN, then filling NaNs using median values learned from training data (`MedianImputer`).
5. **Label Binarization**: Mapping `"BENIGN"` $\to 0$ and `"ATTACK"` $\to 1$.

---

## 18. Machine Learning

Supervised binary classification is employed to separate normal network behavior from attack signatures based on tabular flow statistics.

---

## 19. Random Forest

Random Forest is an ensemble learning method that constructs a multitude of decision trees during training. It outputs the mode of the classes predicted by individual trees.
- **Why Random Forest?**:
  - Handles non-linear feature relationships effectively.
  - Robust against feature scale variances (no scaling required).
  - Provides prediction probabilities used as confidence scores.
  - Highly explainable for academic mini projects.

---

## 20. Training Process

Implemented in `ml/train.py`:
- 75% Training / 25% Testing stratified split.
- `RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)`.
- Evaluated on test set and saved to Joblib binaries in `ml/model/`.

---

## 21. Prediction Process

Implemented in `ml/predict.py`:
1. `PredictionService` loads `random_forest_model.joblib`, `feature_list.joblib`, and `preprocessing_info.joblib`.
2. Input flow features are validated and formatted into a single-row DataFrame.
3. `model.predict()` predicts class (0 or 1).
4. `model.predict_proba()` calculates prediction confidence probability.
5. Severity is assigned (`BENIGN` $\to$ No Alert; `ATTACK` with confidence $\ge 0.90$ $\to$ HIGH, else MEDIUM).

---

## 22. Evaluation Metrics

Evaluated on the test split ($N = 54,097$):
- **Accuracy**: $99.97\%$
- **Precision**: $99.98\%$
- **Recall**: $99.96\%$
- **F1-Score**: $99.97\%$

### Confusion Matrix:
- True BENIGN: 22,295 | False ATTACK (FP): 5
- False BENIGN (FN): 12 | True ATTACK: 31,785

---

## 23. False Positives & False Negatives

- **False Positive (FP)**: Legitimate high-volume traffic (e.g., large file download) misclassified as ATTACK. (Only 5 cases in test set).
- **False Negative (FN)**: Malicious traffic stealthy enough to mimic normal flow misclassified as BENIGN. (12 cases in test set).

---

## 24. Backend

Built with **Flask** (`app.py`).

| Route | Method | Purpose | Response |
|---|---|---|---|
| `/` | GET | Render main dashboard view | HTML |
| `/live` | GET | Render live traffic view | HTML |
| `/alerts` | GET | Render alerts view | HTML |
| `/model` | GET | Render model performance view | HTML |
| `/start-monitoring` | POST | Start background packet capture | Redirect `/` |
| `/stop-monitoring` | POST | Stop active packet capture | Redirect `/` |
| `/load-demo` | POST | Seed presentation demo records | Redirect `/` |
| `/clear-demo` | POST | Clear demo records (`data_source='DEMO'`) | Redirect `/` |
| `/api/status` | GET | Monitoring thread status | JSON |
| `/api/summary` | GET | Dashboard KPI counts & demo flag | JSON |
| `/api/live` | GET | Latest 50 traffic flows | JSON |
| `/api/alerts` | GET | Latest 50 security alerts | JSON |
| `/api/charts` | GET | Aggregated chart datasets | JSON |

---

## 25. Database

SQLite 3 database located at `database/nids.db`.

### `network_traffic` Table
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (TEXT)
- `source_ip` (TEXT)
- `destination_ip` (TEXT)
- `source_port` (INTEGER)
- `destination_port` (INTEGER)
- `protocol` (TEXT)
- `packet_count` (INTEGER)
- `byte_count` (INTEGER)
- `prediction` (TEXT)
- `confidence` (REAL)
- `data_source` (TEXT DEFAULT 'REAL')

### `alerts` Table
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (TEXT)
- `source_ip` (TEXT)
- `destination_ip` (TEXT)
- `attack_type` (TEXT)
- `confidence` (REAL)
- `severity` (TEXT)
- `status` (TEXT)
- `data_source` (TEXT DEFAULT 'REAL')

---

## 26. Frontend

- Styled using custom CSS (`static/css/style.css`) implementing a **Retro-Futuristic Technical Security Aesthetic** (Sand background `#F4EFE6`, Parchment cards `#EFE7D8`, Dark Teal `#1B4D4F`, Terracotta Rust `#B84A2A`).
- Dynamic polling implemented in vanilla JavaScript (`static/js/main.js`).
- Visual charts rendered with Chart.js.

---

## 27. UI Design

- **70% Cybersecurity Professional / 30% Retro Instrumentation**.
- Topbar navigation with glowing status indicator dot and live timestamp clock.
- Clean technical monospace metrics and alert badges.

---

## 28. Demo Mode

- Allows instant presentation and testing without requiring live network traffic generation.
- Demo records are tagged with `data_source = 'DEMO'`.
- The dashboard displays a `⚡ DEMO MODE ACTIVE` badge when demo data is present.
- Demo data can be cleared at any time via `🗑 CLEAR DEMO`, leaving real records untouched.

---

## 29. Real Monitoring Mode

- Initiated via `▶ START MONITORING`.
- Scapy captures real network frames.
- Detections are saved with `data_source = 'REAL'`.

---

## 30. Launcher

- `run_ai_nids.bat` (Windows batch script) and `run.py` (Python launcher).
- Auto-detects virtual environment, initializes SQLite, launches Flask, and opens the default browser automatically.

---

## 31. Complete Installation

```cmd
git clone <repository_url>
cd AI-NIDS
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 32. How to Train the Model

```cmd
python ml/train.py
```

---

## 33. How to Run the Application

```cmd
run_ai_nids.bat
```
or
```cmd
python run.py
```

---

## 34. How to Use the Dashboard

1. Open `http://127.0.0.1:5000`.
2. Select network interface and duration.
3. Click `▶ START MONITORING` for live capture, or `⚡ DEMO DATA` for presentation testing.
4. Click `🗑 CLEAR DEMO` to wipe test records.

---

## 35. Example Workflow

`Packet Received` $\to$ `Flow Updated (192.168.1.105:52410 → 104.21.52.12:443)` $\to$ `10 Features Computed` $\to$ `Random Forest Predicts BENIGN (0.985)` $\to$ `Saved to SQLite` $\to$ `Dashboard Table & Charts Refresh`.

---

## 36. Advantages

- Lightweight, non-intrusive metadata analysis.
- Privacy-preserving (no payload storage).
- High detection accuracy (>99.9%).
- One-click launcher and dual-mode demonstration support.

---

## 37. Limitations

- Trained on binary DDoS patterns (multiclass taxonomy is future work).
- WinPcap/Npcap required for raw Layer-2 capture on Windows.
- Passive detection only (no automated IP blocking).

---

## 38. Future Scope

- Multiclass attack breakdown (PortScan, Brute Force, Web Attacks).
- WebSocket push updates.
- Automated PDF report generation.

---

## 39. Security Considerations

Monitoring should strictly be conducted on authorized networks and personal devices. The software contains no exploit modules, credential harvesters, or packet injection capabilities.

---

## 40. Project Folder Structure

```text
AI-NIDS/
├── app.py
├── config.py
├── run.py
├── run_ai_nids.bat
├── requirements.txt
├── README.md
├── database/
│   ├── db.py
│   └── nids.db
├── ml/
│   ├── preprocess.py
│   ├── train.py
│   ├── predict.py
│   └── model/
│       ├── random_forest_model.joblib
│       ├── feature_list.joblib
│       ├── preprocessing_info.joblib
│       └── evaluation_results.txt
├── network/
│   ├── packet_capture.py
│   ├── flow.py
│   └── features.py
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── live_traffic.html
│   ├── alerts.html
│   └── model.html
├── tests/
│   ├── test_pipeline.py
│   └── test_prediction_service.py
└── docs/
    ├── PROJECT_DOCUMENTATION.md
    ├── SYSTEM_ARCHITECTURE.md
    ├── DATABASE_DESIGN.md
    ├── ML_PIPELINE.md
    ├── USER_GUIDE.md
    └── DEVELOPMENT_HISTORY.md
```

---

## 41. Troubleshooting

- **No Scapy Layer 2 Driver**: Install Npcap in WinPcap API-compatible mode or run as Administrator.
- **Port 5000 Occupied**: `run.py` handles port configuration; kill orphan python processes if port conflict occurs.
- **Missing ML Files**: Run `python ml/train.py`.

---

## 42. Final System Summary

AI-NIDS delivers an efficient, reliable, stateful Network Intrusion Detection System built specifically for MCA academic evaluation. It cleanly bridges low-level network packet analysis with machine learning and web UI visualization.
