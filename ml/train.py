"""Train the Random Forest model using local CICIDS2017 CSV files.

Run from the project root:
    python ml/train.py

By default, the script reads CSV files from the data/ folder. You can also pass
one CSV file or another folder:
    python ml/train.py --data data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import joblib


def safe_text(value) -> str:
    """Return text that can be printed on Windows consoles."""
    return str(value).encode("ascii", "backslashreplace").decode("ascii")

# Allow this file to run directly with: python ml/train.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DATA_DIR, EVALUATION_PATH, FEATURE_LIST_PATH, MODEL_PATH, PREPROCESSOR_PATH
from ml.preprocess import (
    FEATURE_COMPATIBILITY,
    SELECTED_FEATURES,
    apply_imputer,
    clean_dataset,
    fit_imputer,
    load_csv_files,
    split_features_and_label,
)


def build_evaluation_text(y_test, y_pred, class_names: list[str]) -> str:
    """Create readable evaluation output from real test data predictions."""
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
    )

    labels = list(range(len(class_names)))
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    matrix = confusion_matrix(y_test, y_pred, labels=labels)
    report = classification_report(
        y_test,
        y_pred,
        labels=labels,
        target_names=class_names,
        zero_division=0,
    )

    col_headers = "".join(f"{('Pred ' + name):>16}" for name in class_names)
    matrix_lines = [f"{'':20}{col_headers}"]
    for idx, name in enumerate(class_names):
        row_values = "".join(f"{matrix[idx][c]:16d}" for c in range(len(class_names)))
        matrix_lines.append(f"{('Actual ' + name):20}{row_values}")
    matrix_text = "\n".join(matrix_lines)

    return f"""Model Evaluation Results
========================

Accuracy:  {accuracy:.4f}
Precision: {precision:.4f}
Recall:    {recall:.4f}
F1-score:  {f1:.4f}

Confusion Matrix
Rows = Actual, Columns = Predicted

{matrix_text}

Classification Report
{report}
"""


def save_feature_compatibility(model_dir: Path) -> None:
    """Save a simple feature compatibility list for viva explanation."""
    lines = [
        "# Feature Compatibility List",
        "",
        "| Feature | Meaning | CICIDS2017 availability | Live Scapy calculation possibility |",
        "|---|---|---|---|",
    ]
    for item in FEATURE_COMPATIBILITY:
        lines.append(
            f"| {item['feature']} | {item['meaning']} | {item['cicids2017']} | {item['live_scapy']} |"
        )
    lines.append("")
    (model_dir / "feature_compatibility.md").write_text("\n".join(lines), encoding="utf-8")


def train(data_path: Path) -> None:
    """Load CICIDS2017 data, clean it, train Random Forest, and save outputs."""
    raw_data = load_csv_files(data_path)
    cleaned_data, label_to_id, id_to_label = clean_dataset(raw_data)
    class_names = [id_to_label[i] for i in range(len(id_to_label))]
    x, y = split_features_and_label(cleaned_data)

    # scikit-learn is imported after CSV loading so missing local data gives a
    # clear beginner-friendly message before any ML dependency is needed.
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
    import json

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    imputer = fit_imputer(x_train)
    x_train_clean = apply_imputer(imputer, x_train)
    x_test_clean = apply_imputer(imputer, x_test)

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
        n_jobs=1,
    )
    model.fit(x_train_clean, y_train)

    y_pred = model.predict(x_test_clean)
    evaluation_text = build_evaluation_text(y_test, y_pred, class_names)
    print(evaluation_text)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(SELECTED_FEATURES, FEATURE_LIST_PATH)
    joblib.dump(
        {
            "imputer": imputer,
            "missing_value_strategy": "median",
            "label_mapping": label_to_id,
            "inverse_label_mapping": id_to_label,
            "selected_features": SELECTED_FEATURES,
            "classes": class_names,
        },
        PREPROCESSOR_PATH,
    )
    EVALUATION_PATH.write_text(evaluation_text, encoding="utf-8")

    # Also save structured JSON for web UI rendering
    labels = list(range(len(class_names)))
    matrix = confusion_matrix(y_test, y_pred, labels=labels)
    eval_json = {
        "accuracy": f"{accuracy_score(y_test, y_pred):.4f}",
        "precision": f"{precision_score(y_test, y_pred, average='weighted', zero_division=0):.4f}",
        "recall": f"{recall_score(y_test, y_pred, average='weighted', zero_division=0):.4f}",
        "f1_score": f"{f1_score(y_test, y_pred, average='weighted', zero_division=0):.4f}",
        "classes": class_names,
        "matrix": matrix.tolist(),
    }
    (MODEL_PATH.parent / "evaluation_results.json").write_text(json.dumps(eval_json, indent=2), encoding="utf-8")
    save_feature_compatibility(MODEL_PATH.parent)

    print("Saved model: " + safe_text(MODEL_PATH))
    print("Saved feature list: " + safe_text(FEATURE_LIST_PATH))
    print("Saved preprocessing info: " + safe_text(PREPROCESSOR_PATH))
    print("Saved evaluation results: " + safe_text(EVALUATION_PATH))


def parse_args():
    parser = argparse.ArgumentParser(description="Train AI-NIDS binary Random Forest model.")
    parser.add_argument(
        "--data",
        type=Path,
        default=DATA_DIR,
        help="Path to a CICIDS2017 CSV file or folder containing CSV files. Default: data/",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        train(args.data)
    except FileNotFoundError as error:
        print(safe_text(error))
        print("No model was trained because no local CICIDS2017 CSV file was provided.")
        raise SystemExit(1)
    except Exception as error:
        print("Training failed: " + safe_text(error))
        raise SystemExit(1)

