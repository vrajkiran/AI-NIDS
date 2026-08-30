from pathlib import Path

# Base folder of this project. All project paths are built from here.
BASE_DIR = Path(__file__).resolve().parent

# SQLite database file for future detection records.
DATABASE_PATH = BASE_DIR / "database" / "nids.db"

# ML files. The Flask app will load this saved model later instead of retraining.
MODEL_DIR = BASE_DIR / "ml" / "model"
MODEL_PATH = MODEL_DIR / "random_forest_model.joblib"
FEATURE_LIST_PATH = MODEL_DIR / "feature_list.joblib"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessing_info.joblib"
EVALUATION_PATH = MODEL_DIR / "evaluation_results.txt"

# Put your local CICIDS2017 CSV files inside this folder, or pass --data manually.
DATA_DIR = BASE_DIR / "data"

# Packet capture is disabled by default for safety.
# Change these values or pass command-line options when testing authorized traffic.
PACKET_CAPTURE_ENABLED = False
NETWORK_INTERFACE = ""
CAPTURE_DURATION = 10

# Server Configuration
HOST = "127.0.0.1"
PORT = 5000

# Prediction is optional and requires a trained model from: python ml/train.py
PREDICTION_ENABLED = False
HIGH_CONFIDENCE_THRESHOLD = 0.90
LOG_PATH = BASE_DIR / "network_monitor.log"

