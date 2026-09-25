from __future__ import annotations

import logging
import re
import threading
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for

from config import CAPTURE_DURATION, DATABASE_PATH, EVALUATION_PATH, HOST, NETWORK_INTERFACE, PORT, SECRET_KEY
from database.db import (
    clear_demo_data,
    create_database,
    fetch_latest_alerts,
    fetch_latest_traffic,
    get_chart_data,
    get_dashboard_summary,
    has_demo_data,
    insert_alert,
    insert_network_traffic,
    seed_demo_data,
)
from network.packet_capture import PacketCapture, get_interface_names

app = Flask(__name__)
app.secret_key = SECRET_KEY
create_database(DATABASE_PATH)

monitor_lock = threading.Lock()
monitor_thread = None
monitor_capture = None
monitor_status = {
    "active": False,
    "message": "Monitoring stopped",
    "interface": NETWORK_INTERFACE,
    "error": "",
}


def save_detection(metadata: dict, flow, result: dict) -> None:
    """Save flow prediction to SQLite. Raw packet payloads are never stored."""
    try:
        timestamp = datetime.fromtimestamp(metadata["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        confidence = result.get("confidence")

        traffic_record = {
            "timestamp": timestamp,
            "source_ip": flow.source.ip,
            "destination_ip": flow.destination.ip,
            "source_port": flow.source.port,
            "destination_port": flow.destination.port,
            "protocol": metadata["protocol_name"],
            "packet_count": flow.total_packets,
            "byte_count": flow.total_bytes,
            "prediction": result.get("prediction", "PENDING"),
            "confidence": confidence,
        }
        insert_network_traffic(DATABASE_PATH, traffic_record, data_source="REAL")

        if result.get("prediction") == "ATTACK":
            insert_alert(
                DATABASE_PATH,
                {
                    "timestamp": timestamp,
                    "source_ip": flow.source.ip,
                    "destination_ip": flow.destination.ip,
                    "attack_type": result.get("attack_type", "DDoS / Flow Anomaly"),
                    "confidence": confidence,
                    "severity": result.get("severity", "MEDIUM"),
                    "status": "OPEN",
                },
                data_source="REAL",
            )
    except Exception as error:
        message = f"Database error while saving detection: {error}"
        logging.exception(message)
        with monitor_lock:
            monitor_status["error"] = message


def run_monitor(interface: str, duration: int) -> None:
    """Run packet capture in a background thread."""
    global monitor_capture

    capture = PacketCapture(
        interface=interface,
        duration=duration,
        enabled=True,
        prediction_enabled=True,
        on_detection=save_detection,
    )

    with monitor_lock:
        monitor_capture = capture
        monitor_status.update({"active": True, "message": "Monitoring active", "interface": interface, "error": ""})

    capture.start()

    with monitor_lock:
        monitor_status["active"] = False
        monitor_status["message"] = capture.error_message or "Monitoring stopped"
        monitor_status["error"] = capture.error_message
        monitor_capture = None


def read_model_metrics() -> dict:
    """Read real metrics saved by ml/train.py safely with full fallbacks."""
    default_metrics = {
        "available": False,
        "raw_text": "Model evaluation report not found. Train the model using: python ml/train.py",
        "accuracy": "N/A",
        "precision": "N/A",
        "recall": "N/A",
        "f1_score": "N/A",
        "confusion_matrix": None,
        "matrix_classes": [],
        "matrix_rows": [],
    }
    if not EVALUATION_PATH.exists():
        return default_metrics

    try:
        text = EVALUATION_PATH.read_text(encoding="utf-8")
        metrics = {
            "available": True,
            "raw_text": text,
            "accuracy": "N/A",
            "precision": "N/A",
            "recall": "N/A",
            "f1_score": "N/A",
            "confusion_matrix": None,
            "matrix_classes": [],
            "matrix_rows": [],
        }

        # First, try to load structured JSON evaluation data
        json_path = EVALUATION_PATH.parent / "evaluation_results.json"
        if json_path.exists():
            import json
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                metrics["accuracy"] = data.get("accuracy", "N/A")
                metrics["precision"] = data.get("precision", "N/A")
                metrics["recall"] = data.get("recall", "N/A")
                metrics["f1_score"] = data.get("f1_score", "N/A")

                classes = data.get("classes", [])
                matrix = data.get("matrix", [])
                if classes and matrix:
                    metrics["matrix_classes"] = classes
                    metrics["matrix_rows"] = [
                        {"actual": classes[i], "cell_values": matrix[i]}
                        for i in range(len(classes))
                    ]
            except Exception as json_err:
                logging.warning("Could not parse evaluation_results.json: %s", json_err)

        # Fallback to text regex parsing if JSON metrics were not populated
        if metrics["accuracy"] == "N/A":
            for name in ["Accuracy", "Precision", "Recall", "F1-score"]:
                match = re.search(rf"{re.escape(name)}:\s+([0-9.]+)", text)
                key = name.lower().replace("-", "_")
                metrics[key] = match.group(1) if match else "N/A"

        if not metrics["matrix_rows"]:
            matrix_match = re.search(
                r"Actual BENIGN\s+(\d+)\s+(\d+)[\r\n\s]+Actual ATTACK\s+(\d+)\s+(\d+)",
                text,
            )
            if matrix_match:
                g = matrix_match.groups()
                metrics["matrix_classes"] = ["BENIGN", "ATTACK"]
                metrics["matrix_rows"] = [
                    {"actual": "BENIGN", "cell_values": [int(g[0]), int(g[1])]},
                    {"actual": "ATTACK", "cell_values": [int(g[2]), int(g[3])]},
                ]

        return metrics
    except Exception as error:
        logging.exception("Error reading model metrics: %s", error)
        default_metrics["raw_text"] = f"Error reading evaluation file: {error}"
        return default_metrics



@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        summary=get_dashboard_summary(DATABASE_PATH),
        traffic=fetch_latest_traffic(DATABASE_PATH, 8),
        alerts=fetch_latest_alerts(DATABASE_PATH, 8),
        status=monitor_status,
        interfaces=get_interface_names(),
        default_duration=CAPTURE_DURATION,
    )


@app.route("/live")
def live():
    return render_template("live_traffic.html", traffic=fetch_latest_traffic(DATABASE_PATH, 100), status=monitor_status)


@app.route("/alerts")
def alerts():
    return render_template("alerts.html", alerts=fetch_latest_alerts(DATABASE_PATH, 100), status=monitor_status)


@app.route("/model")
def model():
    return render_template("model.html", metrics=read_model_metrics(), status=monitor_status)


@app.route("/start-monitoring", methods=["POST"])
def start_monitoring():
    global monitor_thread

    interface = request.form.get("interface", NETWORK_INTERFACE).strip()
    duration = request.form.get("duration", str(CAPTURE_DURATION), type=int)
    interfaces = get_interface_names()

    if interface and interface not in interfaces:
        monitor_status.update({"active": False, "message": "Invalid network interface", "error": f"Interface not found: {interface}"})
        return redirect(url_for("dashboard"))

    if duration is None or duration < 5 or duration > 3600:
        monitor_status.update({"active": False, "message": "Invalid capture duration", "error": "Duration must be between 5 and 3600 seconds."})
        return redirect(url_for("dashboard"))

    with monitor_lock:
        if monitor_thread and monitor_thread.is_alive():
            monitor_status["message"] = "Monitoring is already active"
            monitor_status["error"] = "A packet capture session is already running."
            return redirect(url_for("dashboard"))

        monitor_thread = threading.Thread(target=run_monitor, args=(interface, duration), daemon=True)
        monitor_thread.start()

    return redirect(url_for("dashboard"))


@app.route("/stop-monitoring", methods=["POST"])
def stop_monitoring():
    with monitor_lock:
        if monitor_capture is not None:
            monitor_capture.stop()
        monitor_status.update({"active": False, "message": "Monitoring stopped", "error": ""})
    return redirect(url_for("dashboard"))


@app.route("/load-demo", methods=["POST"])
def load_demo():
    seed_demo_data(DATABASE_PATH)
    with monitor_lock:
        monitor_status["message"] = "Demonstration records loaded successfully"
    return redirect(url_for("dashboard"))


@app.route("/clear-demo", methods=["POST"])
def clear_demo():
    clear_demo_data(DATABASE_PATH)
    with monitor_lock:
        monitor_status["message"] = "Demonstration data cleared. Real records preserved."
    return redirect(url_for("dashboard"))



@app.route("/api/status")
def api_status():
    return jsonify(monitor_status)


@app.route("/api/summary")
def api_summary():
    data = get_dashboard_summary(DATABASE_PATH)
    data["monitoring_active"] = monitor_status["active"]
    data["message"] = monitor_status["message"]
    data["error"] = monitor_status["error"]
    return jsonify(data)


@app.route("/api/live")
def api_live():
    return jsonify(fetch_latest_traffic(DATABASE_PATH, 50))


@app.route("/api/alerts")
def api_alerts():
    return jsonify(fetch_latest_alerts(DATABASE_PATH, 50))


@app.route("/api/charts")
def api_charts():
    return jsonify(get_chart_data(DATABASE_PATH))


@app.route("/live-traffic")
def live_traffic():
    return redirect(url_for("live"))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)

