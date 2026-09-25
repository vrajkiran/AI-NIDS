"""Prediction service for the saved Random Forest intrusion model.

The Flask app and packet capture code should use this module to load the saved
model. The model is not retrained here; it is loaded from ml/model/.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import FEATURE_LIST_PATH, HIGH_CONFIDENCE_THRESHOLD, MODEL_PATH, PREPROCESSOR_PATH


class PredictionService:
    """Load the trained model once and predict BENIGN or ATTACK for flows."""

    def __init__(self):
        self._check_model_files()
        self.model = joblib.load(MODEL_PATH)
        self.feature_list = joblib.load(FEATURE_LIST_PATH)
        preprocessing_info = joblib.load(PREPROCESSOR_PATH)
        self.imputer = preprocessing_info.get("imputer")
        self.label_mapping = preprocessing_info.get("label_mapping", {"BENIGN": 0, "ATTACK": 1})
        self.inverse_label_mapping = preprocessing_info.get("inverse_label_mapping")
        if not self.inverse_label_mapping:
            self.inverse_label_mapping = {v: k for k, v in self.label_mapping.items()}

    def _check_model_files(self) -> None:
        """Give a clear message if training has not been completed yet."""
        missing_files = [
            path for path in [MODEL_PATH, FEATURE_LIST_PATH, PREPROCESSOR_PATH] if not path.exists()
        ]
        if missing_files:
            names = ", ".join(path.name for path in missing_files)
            raise FileNotFoundError(
                "Trained ML files are missing: "
                + names
                + ". Place the CICIDS2017 CSV files in data/ and run: python ml/train.py"
            )

    def validate_features(self, feature_values: dict[str, Any]) -> None:
        """Check that all required features are present and numeric."""
        missing = [feature for feature in self.feature_list if feature not in feature_values]
        if missing:
            raise ValueError("Missing required ML features: " + ", ".join(missing))

        invalid = []
        for feature in self.feature_list:
            value = feature_values[feature]
            try:
                number = float(value)
            except (TypeError, ValueError):
                invalid.append(feature)
                continue
            if math.isnan(number) or math.isinf(number):
                invalid.append(feature)

        if invalid:
            raise ValueError("Invalid numeric values for ML features: " + ", ".join(invalid))

    def arrange_features(self, feature_values: dict[str, Any]) -> pd.DataFrame:
        """Build one-row DataFrame in the exact feature order used in training."""
        self.validate_features(feature_values)
        ordered_row = {feature: float(feature_values[feature]) for feature in self.feature_list}
        dataframe = pd.DataFrame([ordered_row], columns=self.feature_list)

        if self.imputer is not None:
            dataframe = self.imputer.transform(dataframe)
            dataframe = pd.DataFrame(dataframe, columns=self.feature_list)

        return dataframe

    def predict(self, feature_values: dict[str, Any]) -> dict[str, Any]:
        """Predict BENIGN or ATTACK and return confidence when available."""
        dataframe = self.arrange_features(feature_values)
        prediction_number = int(self.model.predict(dataframe)[0])
        predicted_label = self.inverse_label_mapping.get(prediction_number, "ATTACK")
        confidence = self._confidence(dataframe, prediction_number)

        is_attack = str(predicted_label).upper() != "BENIGN"
        prediction_status = "ATTACK" if is_attack else "BENIGN"
        attack_type = predicted_label if is_attack else "BENIGN"

        return {
            "prediction": prediction_status,
            "confidence": confidence,
            "severity": calculate_severity(prediction_status, confidence),
            "attack_type": attack_type,
        }

    def _confidence(self, dataframe: pd.DataFrame, prediction_number: int) -> float | None:
        """Return prediction probability if the model supports predict_proba()."""
        if not hasattr(self.model, "predict_proba"):
            return None

        probabilities = np.asarray(self.model.predict_proba(dataframe)[0])
        class_list = list(self.model.classes_)
        if prediction_number in class_list:
            probability_index = class_list.index(prediction_number)
        else:
            probability_index = int(probabilities.argmax())
        return round(float(probabilities[probability_index]), 4)


def calculate_severity(prediction: str, confidence: float | None) -> str:
    """Simple project-specific severity rule, not a cybersecurity standard."""
    if prediction == "BENIGN":
        return "No alert"
    if confidence is not None and confidence >= HIGH_CONFIDENCE_THRESHOLD:
        return "HIGH"
    return "MEDIUM"


def predict_traffic(feature_values: dict[str, Any]) -> dict[str, Any]:
    """Beginner-friendly function wrapper."""
    service = PredictionService()
    return service.predict(feature_values)

