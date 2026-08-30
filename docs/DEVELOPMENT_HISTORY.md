# AI-NIDS Phased Development History

This document details how the **AI-NIDS** project was architected and built through ten systematic development phases.

---

## Phase 1: Environment & Project Architecture Setup
- **Objective**: Establish project directory structure, dependencies, and core configuration settings.
- **Implementation**: Created `config.py` defining system paths (`BASE_DIR`, `DATABASE_PATH`, `MODEL_PATH`) and runtime parameters. Created `requirements.txt` specifying Flask, Scapy, Pandas, NumPy, Scikit-learn, and Joblib.

---

## Phase 2: Dataset Acquisition & ML Cleaning Pipeline
- **Objective**: Load and clean the CICIDS2017 dataset for binary classification.
- **Implementation**: Created `ml/preprocess.py`. Implemented column normalization, feature selection (10 live-calculable metrics), numeric conversion, median missing-value imputation (`MedianImputer`), and label binarization (`BENIGN` $\to 0$, `ATTACK` $\to 1$).

---

## Phase 3: Model Training & Evaluation Serialization
- **Objective**: Train a Random Forest model and serialize binary model artifacts.
- **Implementation**: Created `ml/train.py`. Implemented a 75/25 stratified split and trained a 100-tree `RandomForestClassifier`. Saved `random_forest_model.joblib`, `feature_list.joblib`, `preprocessing_info.joblib`, and `evaluation_results.txt`.

---

## Phase 4: Scapy Packet Capture Engine
- **Objective**: Capture real network packets passively without storing raw payloads.
- **Implementation**: Created `network/packet_capture.py`. Implemented Scapy `sniff()` in a background thread with Layer-2 and Layer-3 fallback handling. Extracted safe header metadata only.

---

## Phase 5: Stateful Flow Aggregation & Feature Extraction
- **Objective**: Group packets into bidirectional conversations and compute ML features.
- **Implementation**: Created `network/features.py` and `network/flow.py`. Implemented 5-tuple hash matching for forward/reverse packets and computed 10 flow statistics matching training features.

---

## Phase 6: Prediction Service Integration
- **Objective**: Connect flow features to the pre-trained Random Forest model.
- **Implementation**: Created `ml/predict.py`. Implemented `PredictionService` to load model binaries once, validate feature vectors, compute prediction probabilities, and assign alert severity levels (`HIGH` / `MEDIUM`).

---

## Phase 7: SQLite Database Layer & Flask Application
- **Objective**: Persist detection records and expose REST API endpoints.
- **Implementation**: Created `database/db.py` and `app.py`. Built tables `network_traffic` and `alerts`. Implemented Flask routes for dashboard rendering and API endpoints (`/api/status`, `/api/summary`, `/api/live`, `/api/alerts`, `/api/charts`).

---

## Phase 8: Retro-Futuristic Technical Security UI/UX
- **Objective**: Build a responsive web interface inspired by technical cybersecurity dashboards.
- **Implementation**: Created `static/css/style.css`, `static/js/main.js`, and Jinja templates (`base.html`, `dashboard.html`, `live_traffic.html`, `alerts.html`, `model.html`). Applied warm sand background (`#F4EFE6`), parchment cards (`#EFE7D8`), dark technical teal (`#1B4D4F`), and terracotta rust (`#B84A2A`).

---

## Phase 9: Real vs Demo Data Separation & Launcher
- **Objective**: Implement dual-mode presentation support and one-click execution.
- **Implementation**: Updated database schema to include `data_source TEXT DEFAULT 'REAL'`. Implemented `seed_demo_data()` and `clear_demo_data()`. Added `run_ai_nids.bat` and `run.py` for one-click startup and browser auto-launch.

---

## Phase 10: Final Auditing, Verification & Documentation
- **Objective**: Conduct comprehensive testing and author complete MCA documentation.
- **Implementation**: Verified all routes and API endpoints, ran automated unit tests (`unittest`), and authored 6 technical documentation files inside `docs/`.
