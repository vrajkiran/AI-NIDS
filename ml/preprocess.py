"""Preprocessing helpers for the CICIDS2017 binary classifier.

This file keeps the data cleaning steps separate from model training so the
same feature order and missing-value rules can be reused later for live traffic.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# These features are available in CICIDS2017 and can also be calculated from
# live packets/flows using Scapy by counting packets, bytes, ports, and time.
SELECTED_FEATURES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Mean",
    "Flow Bytes/s",
    "Flow Packets/s",
]

LABEL_COLUMN = "Label"

FEATURE_COMPATIBILITY = [
    {
        "feature": "Destination Port",
        "meaning": "Destination service port used by the flow.",
        "cicids2017": "Available",
        "live_scapy": "Yes, from TCP/UDP destination port.",
    },
    {
        "feature": "Flow Duration",
        "meaning": "Time between the first and latest packet in a flow.",
        "cicids2017": "Available",
        "live_scapy": "Yes, by saving first and last packet timestamps.",
    },
    {
        "feature": "Total Fwd Packets",
        "meaning": "Number of packets in the forward direction.",
        "cicids2017": "Available",
        "live_scapy": "Yes, by counting packets from source to destination.",
    },
    {
        "feature": "Total Backward Packets",
        "meaning": "Number of packets in the reverse direction.",
        "cicids2017": "Available",
        "live_scapy": "Yes, by counting packets from destination to source.",
    },
    {
        "feature": "Total Length of Fwd Packets",
        "meaning": "Total bytes in forward packets.",
        "cicids2017": "Available",
        "live_scapy": "Yes, by summing forward packet lengths.",
    },
    {
        "feature": "Total Length of Bwd Packets",
        "meaning": "Total bytes in backward packets.",
        "cicids2017": "Available",
        "live_scapy": "Yes, by summing backward packet lengths.",
    },
    {
        "feature": "Fwd Packet Length Mean",
        "meaning": "Average size of forward packets.",
        "cicids2017": "Available",
        "live_scapy": "Yes, total forward bytes divided by forward packet count.",
    },
    {
        "feature": "Bwd Packet Length Mean",
        "meaning": "Average size of backward packets.",
        "cicids2017": "Available",
        "live_scapy": "Yes, total backward bytes divided by backward packet count.",
    },
    {
        "feature": "Flow Bytes/s",
        "meaning": "Average bytes transferred per second in a flow.",
        "cicids2017": "Available",
        "live_scapy": "Yes, total flow bytes divided by flow duration.",
    },
    {
        "feature": "Flow Packets/s",
        "meaning": "Average packets transferred per second in a flow.",
        "cicids2017": "Available",
        "live_scapy": "Yes, total flow packets divided by flow duration.",
    },
]


class MedianImputer:
    """Small median imputer so preprocessing remains easy to understand."""

    def __init__(self):
        self.medians = None

    def fit(self, dataframe: pd.DataFrame) -> "MedianImputer":
        self.medians = dataframe.median(numeric_only=True).fillna(0)
        return self

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self.medians is None:
            raise ValueError("MedianImputer must be fitted before transform().")
        return dataframe.fillna(self.medians)


def normalize_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remove extra spaces from CICIDS2017 column names."""
    dataframe = dataframe.copy()
    dataframe.columns = dataframe.columns.str.strip()
    return dataframe


def load_csv_files(data_path: Path) -> pd.DataFrame:
    """Load one CICIDS2017 CSV/Parquet file or all supported files inside a folder."""
    data_path = Path(data_path)

    supported_suffixes = {".csv", ".parquet"}

    if data_path.is_file() and data_path.suffix.lower() in supported_suffixes:
        dataset_files = [data_path]
    elif data_path.is_dir():
        dataset_files = sorted(
            file for file in data_path.iterdir() if file.suffix.lower() in supported_suffixes
        )
    else:
        raise FileNotFoundError("Dataset path not found. Please check the --data value.")

    if not dataset_files:
        raise FileNotFoundError(
            "No CSV or Parquet files found. Place CICIDS2017 files in data/ or pass --data."
        )

    frames = []
    for dataset_file in dataset_files:
        print(f"Loading: {dataset_file.name}")
        if dataset_file.suffix.lower() == ".csv":
            frame = pd.read_csv(dataset_file, low_memory=False)
        else:
            frame = pd.read_parquet(dataset_file)
        frames.append(normalize_column_names(frame))

    return pd.concat(frames, ignore_index=True)


def check_required_columns(dataframe: pd.DataFrame) -> None:
    """Stop early if a selected feature is missing from the dataset."""
    missing_columns = [column for column in SELECTED_FEATURES + [LABEL_COLUMN] if column not in dataframe.columns]
    if missing_columns:
        available = ", ".join(dataframe.columns[:20])
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
            + f". First available columns are: {available}"
        )


def standardize_label(raw_label: str) -> str:
    """Map raw CICIDS2017 label string to a clean, standardized category."""
    label_upper = str(raw_label).strip().upper()
    if "BENIGN" in label_upper:
        return "BENIGN"
    elif "DDOS" in label_upper:
        return "DDoS"
    elif "DOS" in label_upper:
        return "DoS"
    elif "PORTSCAN" in label_upper or "PORT SCAN" in label_upper:
        return "PortScan"
    elif "PATATOR" in label_upper or "BRUTE" in label_upper:
        return "Brute Force"
    elif "WEB" in label_upper or "SQL" in label_upper or "XSS" in label_upper:
        return "Web Attack"
    elif "BOT" in label_upper:
        return "Botnet"
    elif "INFILTRATION" in label_upper:
        return "Infiltration"
    elif "HEARTBLEED" in label_upper:
        return "Heartbleed"
    else:
        return str(raw_label).strip()


def convert_labels(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int], dict[int, str]]:
    """Convert CICIDS2017 labels into standardized multi-class integer targets."""
    dataframe = dataframe.copy()
    cleaned_labels = dataframe[LABEL_COLUMN].astype(str).map(standardize_label)

    unique_labels = sorted(cleaned_labels.unique())
    if "BENIGN" in unique_labels:
        unique_labels.remove("BENIGN")
        unique_labels = ["BENIGN"] + unique_labels

    label_to_id = {label: idx for idx, label in enumerate(unique_labels)}
    id_to_label = {idx: label for label, idx in label_to_id.items()}

    dataframe["target"] = cleaned_labels.map(label_to_id)
    dataframe["target_name"] = cleaned_labels
    return dataframe, label_to_id, id_to_label


def clean_dataset(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int], dict[int, str]]:
    """Clean missing, infinite, duplicate, and non-numeric values."""
    dataframe = normalize_column_names(dataframe)
    check_required_columns(dataframe)

    needed_columns = SELECTED_FEATURES + [LABEL_COLUMN]
    dataframe = dataframe[needed_columns].copy()

    before_duplicates = len(dataframe)
    dataframe = dataframe.drop_duplicates()
    removed_duplicates = before_duplicates - len(dataframe)

    for column in SELECTED_FEATURES:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    dataframe = dataframe.replace([np.inf, -np.inf], np.nan)
    dataframe, label_to_id, id_to_label = convert_labels(dataframe)

    print(f"Rows after loading selected columns: {before_duplicates}")
    print(f"Duplicate rows removed: {removed_duplicates}")
    print(f"Rows after duplicate removal: {len(dataframe)}")
    print("Multi-class distribution:")
    print(dataframe["target_name"].value_counts())

    return dataframe[SELECTED_FEATURES + ["target"]], label_to_id, id_to_label


def split_features_and_label(dataframe: pd.DataFrame):
    """Separate input features from the output target label."""
    x = dataframe[SELECTED_FEATURES]
    y = dataframe["target"]
    return x, y


def fit_imputer(x_train: pd.DataFrame) -> MedianImputer:
    """Learn median values from training data for missing-value handling."""
    return MedianImputer().fit(x_train)


def apply_imputer(imputer: MedianImputer, dataframe: pd.DataFrame) -> pd.DataFrame:
    """Apply saved missing-value handling and keep column names."""
    return imputer.transform(dataframe)



