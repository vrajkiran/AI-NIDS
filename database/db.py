import sqlite3
from pathlib import Path


def get_connection(database_path: Path):
    """Open a SQLite connection and return rows like dictionaries."""
    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def create_database(database_path: Path) -> None:
    """Create SQLite tables used by the web dashboard and perform auto-migration."""
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection(database_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS network_traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT,
            destination_ip TEXT,
            source_port INTEGER,
            destination_port INTEGER,
            protocol TEXT,
            packet_count INTEGER,
            byte_count INTEGER,
            prediction TEXT,
            confidence REAL,
            data_source TEXT DEFAULT 'REAL'
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT,
            destination_ip TEXT,
            attack_type TEXT,
            confidence REAL,
            severity TEXT,
            status TEXT,
            data_source TEXT DEFAULT 'REAL'
        )
        """
    )

    # Perform safe schema auto-migration for existing databases
    for table in ["network_traffic", "alerts"]:
        columns = [row["name"] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
        if "data_source" not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN data_source TEXT DEFAULT 'REAL'")

    connection.commit()

    # Seed initial realistic demonstration records if tables are empty
    count = cursor.execute("SELECT COUNT(*) FROM network_traffic").fetchone()[0]
    if count == 0:
        seed_demo_data_connection(cursor)
        connection.commit()

    connection.close()


def seed_demo_data_connection(cursor) -> None:
    """Insert initial realistic demonstration records tagged as DEMO."""
    demo_traffic = [
        ("2026-08-30 20:50:12", "192.168.1.105", "104.21.52.12", 52410, 443, "TCP", 148, 124500, "BENIGN", 0.9850, "DEMO"),
        ("2026-08-30 20:50:15", "192.168.1.105", "8.8.8.8", 53120, 53, "UDP", 12, 840, "BENIGN", 0.9920, "DEMO"),
        ("2026-08-30 20:51:02", "192.168.1.105", "142.250.190.46", 52414, 443, "TCP", 210, 185200, "BENIGN", 0.9780, "DEMO"),
        ("2026-08-30 20:51:30", "45.33.32.156", "192.168.1.105", 49152, 80, "TCP", 1250, 1420000, "ATTACK", 0.9940, "DEMO"),
        ("2026-08-30 20:52:01", "185.220.101.5", "192.168.1.105", 60124, 22, "TCP", 45, 3200, "ATTACK", 0.8850, "DEMO"),
        ("2026-08-30 20:52:45", "192.168.1.105", "13.107.42.14", 52420, 443, "TCP", 84, 45200, "BENIGN", 0.9910, "DEMO"),
        ("2026-08-30 20:53:10", "192.168.1.120", "192.168.1.1", 54100, 53, "UDP", 6, 420, "BENIGN", 0.9960, "DEMO"),
        ("2026-08-30 20:53:50", "198.51.100.44", "192.168.1.105", 58210, 8080, "TCP", 2150, 2840000, "ATTACK", 0.9980, "DEMO"),
        ("2026-08-30 20:54:15", "192.168.1.105", "172.217.16.206", 52432, 443, "TCP", 92, 78400, "BENIGN", 0.9890, "DEMO"),
        ("2026-08-30 20:54:55", "103.21.244.0", "192.168.1.105", 61002, 445, "TCP", 32, 2100, "ATTACK", 0.8720, "DEMO"),
    ]
    cursor.executemany(
        """
        INSERT INTO network_traffic (
            timestamp, source_ip, destination_ip, source_port, destination_port,
            protocol, packet_count, byte_count, prediction, confidence, data_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        demo_traffic,
    )

    demo_alerts = [
        ("2026-08-30 20:51:30", "45.33.32.156", "192.168.1.105", "DDoS / Flow Anomaly", 0.9940, "HIGH", "OPEN", "DEMO"),
        ("2026-08-30 20:52:01", "185.220.101.5", "192.168.1.105", "DDoS / Flow Anomaly", 0.8850, "MEDIUM", "OPEN", "DEMO"),
        ("2026-08-30 20:53:50", "198.51.100.44", "192.168.1.105", "DDoS / Flow Anomaly", 0.9980, "HIGH", "OPEN", "DEMO"),
        ("2026-08-30 20:54:55", "103.21.244.0", "192.168.1.105", "DDoS / Flow Anomaly", 0.8720, "MEDIUM", "OPEN", "DEMO"),
    ]
    cursor.executemany(
        """
        INSERT INTO alerts (
            timestamp, source_ip, destination_ip, attack_type, confidence, severity, status, data_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        demo_alerts,
    )


def seed_demo_data(database_path: Path) -> None:
    """Explicit public function to populate demonstration data."""
    with get_connection(database_path) as connection:
        cursor = connection.cursor()
        seed_demo_data_connection(cursor)
        connection.commit()


def clear_demo_data(database_path: Path) -> None:
    """Delete ONLY demonstration data (data_source = 'DEMO'), leaving REAL traffic intact."""
    with get_connection(database_path) as connection:
        connection.execute("DELETE FROM network_traffic WHERE data_source = 'DEMO'")
        connection.execute("DELETE FROM alerts WHERE data_source = 'DEMO'")
        connection.commit()


def has_demo_data(database_path: Path) -> bool:
    """Return True if any records with data_source = 'DEMO' exist."""
    with get_connection(database_path) as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS count FROM network_traffic WHERE data_source = 'DEMO'"
        ).fetchone()
        return bool(row and row["count"] > 0)


def insert_network_traffic(database_path: Path, record: dict, data_source: str = "REAL") -> None:
    """Save one monitored flow result."""
    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO network_traffic (
                timestamp, source_ip, destination_ip, source_port, destination_port,
                protocol, packet_count, byte_count, prediction, confidence, data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["timestamp"],
                record["source_ip"],
                record["destination_ip"],
                record["source_port"],
                record["destination_port"],
                record["protocol"],
                record["packet_count"],
                record["byte_count"],
                record["prediction"],
                record["confidence"],
                data_source,
            ),
        )


def insert_alert(database_path: Path, record: dict, data_source: str = "REAL") -> None:
    """Save an alert when the model predicts ATTACK."""
    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO alerts (
                timestamp, source_ip, destination_ip, attack_type, confidence, severity, status, data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["timestamp"],
                record["source_ip"],
                record["destination_ip"],
                record["attack_type"],
                record["confidence"],
                record["severity"],
                record["status"],
                data_source,
            ),
        )


def fetch_latest_traffic(database_path: Path, limit: int = 100) -> list[dict]:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            "SELECT * FROM network_traffic ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_latest_alerts(database_path: Path, limit: int = 100) -> list[dict]:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_dashboard_summary(database_path: Path) -> dict:
    with get_connection(database_path) as connection:
        row = connection.execute(
            """
            SELECT
                COALESCE(SUM(packet_count), 0) AS total_packets,
                COUNT(DISTINCT
                    CASE
                        WHEN (COALESCE(source_ip, '') || '|' || printf('%05d', COALESCE(source_port, 0))) < (COALESCE(destination_ip, '') || '|' || printf('%05d', COALESCE(destination_port, 0)))
                        THEN COALESCE(source_ip, '') || ':' || COALESCE(source_port, 0) || '<->' || COALESCE(destination_ip, '') || ':' || COALESCE(destination_port, 0) || '|' || COALESCE(protocol, '')
                        ELSE COALESCE(destination_ip, '') || ':' || COALESCE(destination_port, 0) || '<->' || COALESCE(source_ip, '') || ':' || COALESCE(source_port, 0) || '|' || COALESCE(protocol, '')
                    END
                ) AS total_flows,
                SUM(CASE WHEN prediction = 'BENIGN' THEN 1 ELSE 0 END) AS normal_traffic,
                SUM(CASE WHEN prediction = 'ATTACK' THEN 1 ELSE 0 END) AS detected_attacks
            FROM network_traffic
            """
        ).fetchone()
        alert_row = connection.execute(
            "SELECT COUNT(*) AS active_alerts FROM alerts WHERE status = 'OPEN'"
        ).fetchone()

    return {
        "total_packets": int(row["total_packets"] or 0),
        "total_flows": int(row["total_flows"] or 0),
        "normal_traffic": int(row["normal_traffic"] or 0),
        "detected_attacks": int(row["detected_attacks"] or 0),
        "active_alerts": int(alert_row["active_alerts"] or 0),
        "has_demo_data": has_demo_data(database_path),
    }


def get_chart_data(database_path: Path) -> dict:
    with get_connection(database_path) as connection:
        labels = connection.execute(
            "SELECT prediction, COUNT(*) AS count FROM network_traffic GROUP BY prediction"
        ).fetchall()
        timeline = connection.execute(
            """
            SELECT substr(timestamp, 1, 16) AS minute, COUNT(*) AS count
            FROM network_traffic
            GROUP BY substr(timestamp, 1, 16)
            ORDER BY minute DESC
            LIMIT 10
            """
        ).fetchall()
        attacks = connection.execute(
            "SELECT severity, COUNT(*) AS count FROM alerts GROUP BY severity"
        ).fetchall()

    label_counts = {row["prediction"]: row["count"] for row in labels}
    return {
        "benign_attack": {
            "BENIGN": label_counts.get("BENIGN", 0),
            "ATTACK": label_counts.get("ATTACK", 0),
        },
        "traffic_over_time": list(reversed([dict(row) for row in timeline])),
        "attack_count": [dict(row) for row in attacks],
    }
