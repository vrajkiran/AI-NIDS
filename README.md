# AI-Based Real-Time Network Intrusion Detection System Using Machine Learning

## 1. Project Title

AI-Based Real-Time Network Intrusion Detection System Using Machine Learning

## 2. Introduction

This MCA mini project is a Network Intrusion Detection System (NIDS). It monitors real network traffic metadata captured from an authorized network interface using Scapy, aggregates packets into bidirectional traffic flows, extracts numeric flow features, classifies traffic using a Random Forest machine learning classifier, logs detection records into an SQLite database, and presents real-time statistics in a Flask web dashboard.

The project is structured to remain simple, understandable, and demonstration-ready for academic presentation.

## 3. Problem Statement

Modern network environments encounter both legitimate (BENIGN) and malicious (ATTACK) traffic. Manual packet inspection is impractical for high-volume network streams, and fixed signature rules often fail against evolving traffic patterns. This project delivers an automated machine-learning-based intrusion detection pipeline that classifies real-time network flow metadata without inspecting or storing packet payloads.

## 4. Objectives

- Capture real packet metadata from authorized network interfaces using Scapy.
- Enforce strict metadata-only collection (no payload capture or raw packet storage).
- Group packets into bidirectional 5-tuple network flows.
- Compute flow-level statistical features aligned with training dataset parameters.
- Train a Random Forest binary classifier (`BENIGN` vs `ATTACK`) using CICIDS2017 flow data.
- Store real flow detections and high-confidence alerts in an SQLite database.
- Provide a Flask dashboard with live counters, alert tables, and Chart.js visualizations.
- Provide a one-click launcher (`run_ai_nids.bat`) for easy startup and browser integration.

## 5. Existing System

Traditional intrusion detection systems often depend on signature matching or manual inspection. Signature-based systems require constant manual rule updates and cannot effectively detect novel attack patterns or dynamic flow anomalies. Manual log inspection is labor-intensive and error-prone.

## 6. Proposed System

The proposed system applies a supervised Random Forest classifier trained on CICIDS2017 network flow data. During passive monitoring:
1. Scapy captures IP packet headers from an authorized network adapter.
2. Packets are aggregated into active flows.
3. Feature vectors matching the model schema are computed.
4. The Random Forest model outputs a binary prediction (`BENIGN` or `ATTACK`) with confidence scores.
5. Detections and alerts are stored in SQLite and streamed to the Flask web dashboard via JSON REST APIs.

## 7. System Architecture

```text
Real Network Packets
        ↓
Scapy Packet Capture
        ↓
Flow Aggregation
        ↓
Feature Extraction
        ↓
Random Forest ML Model
        ↓
BENIGN / ATTACK
        ↓
SQLite Database
        ↓
Flask Backend
        ↓
Web Dashboard
```

Pipeline Flow:
`Real Packet` → `Scapy` → `Flow Aggregation` → `Features` → `Random Forest` → `Prediction` → `SQLite` → `Flask` → `Dashboard`

## 8. Technologies

- **Language**: Python 3.10+
- **Backend Framework**: Flask
- **Packet Capture**: Scapy
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn, Random Forest
- **Model Serialization**: Joblib
- **Database**: SQLite 3
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (ES6), Chart.js

## 9. Dataset

The classifier is trained on the benchmark CICIDS2017 machine learning dataset derived from network traffic flows.
The dataset file used for model training:
`data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv.parquet`

Dataset Summary:
- Total rows loaded: 225,745
- Duplicate rows removed: 9,358
- Cleaned dataset rows: 216,387
- Class Distribution: `BENIGN`: 89,199 | `ATTACK`: 127,188

## 10. Data Preprocessing

Implemented in `ml/preprocess.py`:
- Column name standardization (whitespace stripping).
- Feature selection: retaining 10 live-calculable flow metrics.
- Type conversion to numeric values.
- Handling missing/infinite values via training data median imputation (`MedianImputer`).
- Deduplication of identical traffic vectors.
- Target encoding (`BENIGN` = 0, `ATTACK` = 1).

## 11. Random Forest Methodology

Implemented in `ml/train.py`:
- Dataset split: 75% Training, 25% Testing (stratified).
- Model: `RandomForestClassifier` with 100 decision trees and balanced class weights.
- Metrics evaluation on test split saved to `ml/model/evaluation_results.txt`.
- Artifacts saved to `ml/model/`: `random_forest_model.joblib`, `feature_list.joblib`, `preprocessing_info.joblib`.

## 12. Packet Monitoring

Implemented in `network/packet_capture.py`:
- Passive packet capture via Scapy (`sniff`).
- Captures metadata only: Timestamp, Source IP, Destination IP, Source Port, Destination Port, Protocol, Packet Length.
- Payload storage is strictly disabled for security and privacy.

## 13. Feature Extraction

Implemented in `network/flow.py` and `network/features.py`:

| Feature Name | Description | Calculation |
|---|---|---|
| Destination Port | Target port | TCP/UDP destination port |
| Protocol | IP Protocol number | ICMP (1), TCP (6), UDP (17) |
| Flow Duration | Microseconds elapsed | `(last_timestamp - first_timestamp) * 1e6` |
| Total Fwd Packets | Forward packet count | Packets from source to destination |
| Total Backward Packets | Reverse packet count | Packets from destination to source |
| Total Length of Fwd Packets | Forward bytes total | Sum of forward packet lengths |
| Total Length of Bwd Packets | Reverse bytes total | Sum of reverse packet lengths |
| Fwd Packet Length Mean | Average forward packet size | `Fwd Bytes / Fwd Packets` |
| Bwd Packet Length Mean | Average reverse packet size | `Bwd Bytes / Bwd Packets` |
| Flow Bytes/s | Transfer rate (bytes/sec) | `Total Bytes / Duration` |
| Flow Packets/s | Transfer rate (packets/sec) | `Total Packets / Duration` |

## 14. Project Modules

- `app.py`: Flask application routes, monitoring thread controller, REST API endpoints.
- `config.py`: Centralized configuration paths, server parameters (`HOST = "127.0.0.1"`, `PORT = 5000`), log settings.
- `run.py`: Python launcher that initializes DB, starts Flask, and launches the default web browser.
- `run_ai_nids.bat`: Windows batch script for one-click startup.
- `ml/preprocess.py`: Dataset loading, cleaning, and feature selection.
- `ml/train.py`: Random Forest training script.
- `ml/predict.py`: Real-time prediction service wrapper.
- `network/packet_capture.py`: Scapy packet sniffer thread with Layer 2/3 fallback.
- `network/flow.py`: Bidirectional flow state tracking.
- `network/features.py`: Scapy packet header metadata extraction.
- `database/db.py`: SQLite connection management, schema initialization, query functions.
- `templates/`: Jinja2 templates (`base.html`, `dashboard.html`, `live_traffic.html`, `alerts.html`, `model.html`).
- `static/`: Modern dashboard styles (`css/style.css`) and dynamic polling logic (`js/main.js`).

## 15. Database

SQLite file location: `database/nids.db`

Schema Details:
- **`network_traffic` table**: Stores flow records (`timestamp`, `source_ip`, `destination_ip`, `source_port`, `destination_port`, `protocol`, `packet_count`, `byte_count`, `prediction`, `confidence`).
- **`alerts` table**: Stores detected attack events (`timestamp`, `source_ip`, `destination_ip`, `attack_type`, `confidence`, `severity`, `status`).

Severity Classification:
- `BENIGN` → No alert created.
- `ATTACK` (Confidence >= 0.90) → `HIGH` severity.
- `ATTACK` (Confidence < 0.90) → `MEDIUM` severity.

## 16. Results

Model evaluation metrics read from `ml/model/evaluation_results.txt`:
- **Accuracy**: 99.97%
- **Precision**: 99.98%
- **Recall**: 99.96%
- **F1-Score**: 99.97%

Confusion Matrix (Test set):
- True BENIGN: 22,295 | False ATTACK: 5
- False BENIGN: 12 | True ATTACK: 31,785

## 17. Limitations

- Binary classification (`BENIGN` vs `ATTACK`) trained primarily on DDoS flow patterns.
- Real packet capture on Windows requires Npcap or Administrator privileges for raw socket access.
- Passive monitoring only; no automated IP blocking or packet filtering.

## 18. Future Scope

- Multiclass attack taxonomy (DDoS, PortScan, Brute Force, Web Attack).
- WebSocket integration for lower latency UI updates.
- Interactive alert management (Mark as Reviewed / Resolved).
- Automated reporting in PDF/CSV formats.

## 19. Installation

1. Clone or open the project folder in your terminal:
   ```cmd
   cd c:\Users\Intel\OneDrive\문서\AI-NIDS
   ```
2. Create and activate a Python virtual environment:
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install project dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

## 20. Model Training

To retrain the Random Forest model using the dataset in `data/`:
```cmd
python ml/train.py
```
This updates model artifacts in `ml/model/`.

## 21. Running the Application

To run the Flask application directly:
```cmd
python app.py
```
Access the web dashboard in your browser at:
`http://127.0.0.1:5000`

## 22. Using the Launcher

To launch the system with automatic browser opening and status banner:

**On Windows (Double Click or Terminal)**:
```cmd
run_ai_nids.bat
```

**Using Python directly**:
```cmd
python run.py
```

The launcher will:
1. Initialize the SQLite database.
2. Load the trained Random Forest model.
3. Start the Flask web server on `http://127.0.0.1:5000`.
4. Open your default web browser automatically.

## 23. Starting and Stopping Monitoring

1. Launch AI-NIDS using `run_ai_nids.bat`.
2. Open the web dashboard.
3. Select an authorized network interface (e.g., `Wi-Fi` or `Ethernet`) from the dropdown.
4. Set capture duration (default: 10 seconds).
5. Click **Start Monitoring**.
6. Real traffic flows will be captured, processed by Scapy, evaluated by Random Forest, logged to SQLite, and displayed in real time on the dashboard.
7. Click **Stop Monitoring** at any time to halt active capture.

---

### Security and Ethics Disclaimer
This tool is built strictly for educational monitoring on authorized networks. It contains no packet injection, exploit code, password logging, or automated blocking features.
