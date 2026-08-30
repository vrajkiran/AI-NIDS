"""Controlled tests for the prediction service.

These tests do not create a trained project model and do not invent evaluation
metrics. They only verify feature validation, feature ordering, and severity.
"""

import unittest
from ml.predict import PredictionService, calculate_severity


class DemoModel:
    classes_ = [0, 1]

    def predict(self, dataframe):
        return [0]

    def predict_proba(self, dataframe):
        return [[0.96, 0.04]]


class TestPredictionService(unittest.TestCase):
    def test_prediction_service_orders_features(self):
        service = object.__new__(PredictionService)
        service.model = DemoModel()
        service.feature_list = ["b", "a"]
        service.imputer = None

        dataframe = service.arrange_features({"a": 1, "b": 2})

        self.assertEqual(list(dataframe.columns), ["b", "a"])
        self.assertEqual(dataframe.iloc[0].tolist(), [2.0, 1.0])

    def test_prediction_service_reports_missing_features(self):
        service = object.__new__(PredictionService)
        service.model = DemoModel()
        service.feature_list = ["required_feature"]
        service.imputer = None

        with self.assertRaises(ValueError) as context:
            service.arrange_features({})
        self.assertIn("Missing required ML features", str(context.exception))

    def test_severity_rules(self):
        self.assertEqual(calculate_severity("BENIGN", 0.99), "No alert")
        self.assertEqual(calculate_severity("ATTACK", 0.91), "HIGH")
        self.assertEqual(calculate_severity("ATTACK", 0.75), "MEDIUM")


if __name__ == "__main__":
    unittest.main()

