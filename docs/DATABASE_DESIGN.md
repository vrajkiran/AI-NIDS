# AI-NIDS Database Design Document

## 1. Database Overview

The system uses an **SQLite 3** relational database engine stored locally at `database/nids.db`. SQLite was selected because it is serverless, self-contained, zero-configuration, and ideal for an MCA mini project.

---

## 2. Entity-Relationship & Schema Diagram

```text
+---------------------------------------+       +---------------------------------------+
|            network_traffic            |       |                alerts                 |
+---------------------------------------+       +---------------------------------------+
| id               INTEGER PK AUTO      |       | id               INTEGER PK AUTO      |
| timestamp        TEXT NOT NULL        |       | timestamp        TEXT NOT NULL        |
| source_ip        TEXT                 |       | source_ip        TEXT                 |
| destination_ip   TEXT                 |       | destination_ip   TEXT                 |
| source_port      INTEGER              |       | attack_type      TEXT                 |
| destination_port INTEGER              |       | confidence       REAL                 |
| protocol         TEXT                 |       | severity         TEXT                 |
| packet_count     INTEGER              |       | status           TEXT                 |
| byte_count       INTEGER              |       | data_source      TEXT DEFAULT 'REAL'  |
| prediction       TEXT                 |       +---------------------------------------+
| confidence       REAL                 |
| data_source      TEXT DEFAULT 'REAL'  |
+---------------------------------------+
```

---

## 3. Table Specifications

### 3.1 `network_traffic` Table

| Column Name | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | INTEGER | No | Auto Increment | Primary key identifier |
| `timestamp` | TEXT | No | None | ISO formatted timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `source_ip` | TEXT | Yes | NULL | IPv4 address of origin host |
| `destination_ip` | TEXT | Yes | NULL | IPv4 address of target host |
| `source_port` | INTEGER | Yes | NULL | Source TCP/UDP port |
| `destination_port` | INTEGER | Yes | NULL | Destination TCP/UDP port |
| `protocol` | TEXT | Yes | NULL | Protocol name (`TCP`, `UDP`, `ICMP`) |
| `packet_count` | INTEGER | Yes | NULL | Total packets in flow session |
| `byte_count` | INTEGER | Yes | NULL | Total bytes transferred in flow session |
| `prediction` | TEXT | Yes | NULL | Machine Learning decision (`BENIGN` or `ATTACK`) |
| `confidence` | REAL | Yes | NULL | Prediction probability float ($0.0 - 1.0$) |
| `data_source` | TEXT | Yes | `'REAL'` | Data origin tag (`'REAL'` or `'DEMO'`) |

---

### 3.2 `alerts` Table

| Column Name | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | INTEGER | No | Auto Increment | Primary key identifier |
| `timestamp` | TEXT | No | None | ISO formatted alert timestamp |
| `source_ip` | TEXT | Yes | NULL | Originating source IP of the attack |
| `destination_ip` | TEXT | Yes | NULL | Target IP of the attack |
| `attack_type` | TEXT | Yes | NULL | Threat category (`ATTACK`) |
| `confidence` | REAL | Yes | NULL | Model prediction confidence probability |
| `severity` | TEXT | Yes | NULL | Assigned threat level (`HIGH` or `MEDIUM`) |
| `status` | TEXT | Yes | NULL | Alert state (`OPEN`, `REVIEWED`, `CLOSED`) |
| `data_source` | TEXT | Yes | `'REAL'` | Data origin tag (`'REAL'` or `'DEMO'`) |

---

## 4. Key Database Queries

### 4.1 Fetch Summary Metrics
```sql
SELECT
    COALESCE(SUM(packet_count), 0) AS total_packets,
    COUNT(DISTINCT source_ip || ':' || source_port || '>' || destination_ip || ':' || destination_port || '/' || protocol) AS total_flows,
    SUM(CASE WHEN prediction = 'BENIGN' THEN 1 ELSE 0 END) AS normal_traffic,
    SUM(CASE WHEN prediction = 'ATTACK' THEN 1 ELSE 0 END) AS detected_attacks
FROM network_traffic;
```

### 4.2 Clear Demo Data Only
```sql
DELETE FROM network_traffic WHERE data_source = 'DEMO';
DELETE FROM alerts WHERE data_source = 'DEMO';
```

---

## 5. Schema Auto-Migration Logic

When `create_database()` is invoked on startup, `PRAGMA table_info` checks whether the `data_source` column exists. If absent, `ALTER TABLE ... ADD COLUMN data_source TEXT DEFAULT 'REAL'` is executed seamlessly without dropping tables or losing historical records.
