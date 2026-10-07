"""Integration and route tests for AI-NIDS web application and database queries."""

import unittest
from app import app
from config import DATABASE_PATH
from database.db import (
    clear_demo_data,
    get_chart_data,
    get_connection,
    get_dashboard_summary,
    seed_demo_data,
)


class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_page_routes_status_200(self):
        for route in ["/", "/live", "/alerts", "/model"]:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_api_endpoints_return_json(self):
        for api_route in ["/api/status", "/api/summary", "/api/live", "/api/alerts", "/api/charts"]:
            with self.subTest(api_route=api_route):
                response = self.client.get(api_route)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.is_json)

    def test_start_monitoring_handles_missing_or_invalid_duration_safely(self):
        # Missing duration must not crash with TypeError
        response = self.client.post("/start-monitoring", data={"interface": "", "duration": ""})
        self.assertEqual(response.status_code, 302)

        # Invalid duration string must not crash
        response_invalid = self.client.post("/start-monitoring", data={"interface": "", "duration": "abc"})
        self.assertEqual(response_invalid.status_code, 302)

    def test_database_summary_and_chart_data(self):
        summary = get_dashboard_summary(DATABASE_PATH)
        self.assertIn("total_packets", summary)
        self.assertIn("total_flows", summary)
        self.assertIn("normal_traffic", summary)
        self.assertIn("detected_attacks", summary)

        chart_data = get_chart_data(DATABASE_PATH)
        self.assertIn("benign_attack", chart_data)
        self.assertIn("traffic_over_time", chart_data)
        self.assertIn("attack_count", chart_data)

    def test_demo_data_lifecycle(self):
        clear_demo_data(DATABASE_PATH)
        summary_cleared = get_dashboard_summary(DATABASE_PATH)
        self.assertFalse(summary_cleared["has_demo_data"])

        seed_demo_data(DATABASE_PATH)
        summary_seeded = get_dashboard_summary(DATABASE_PATH)
        self.assertTrue(summary_seeded["has_demo_data"])

    def test_csv_export_endpoints(self):
        traffic_resp = self.client.get("/export/traffic")
        self.assertEqual(traffic_resp.status_code, 200)
        self.assertEqual(traffic_resp.mimetype, "text/csv")
        self.assertIn("Timestamp", traffic_resp.get_data(as_text=True))

        alerts_resp = self.client.get("/export/alerts")
        self.assertEqual(alerts_resp.status_code, 200)
        self.assertEqual(alerts_resp.mimetype, "text/csv")
        self.assertIn("Attack Type", alerts_resp.get_data(as_text=True))

    def test_alert_resolution_endpoints(self):
        seed_demo_data(DATABASE_PATH)
        # Test resolve single alert
        resp = self.client.post("/api/alerts/1/resolve")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("success", data)

        # Test resolve all alerts
        resp_all = self.client.post("/api/alerts/resolve-all")
        self.assertEqual(resp_all.status_code, 200)
        data_all = resp_all.get_json()
        self.assertTrue(data_all["success"])
        self.assertIn("resolved_count", data_all)


if __name__ == "__main__":
    unittest.main()
