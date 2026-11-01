# System Architecture & Technical Specifications

## 1. High-Level Architectural Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                      DATA ACQUISITION LAYER                                       |
|                                                                                                   |
|   [ Physical ESP32 Hardware Node ]                  [ Python Synthetic Generator ]                |
|     - 4S Cell Voltage Dividers                        - Drift & Gaussian Noise Engine             |
|     - 10k NTC Contact Thermistors                     - Scenarios: Normal, Imbalance, Heat, Fault |
|     - Local LEDs & Buzzer Alarm                       - Configurable sampling interval (2.0s)     |
+---------------------------------------------------------------------------------------------------+
                                         │                              │
                                         ▼                              ▼
+---------------------------------------------------------------------------------------------------+
|                                     TRANSPORT / BROKER LAYER                                      |
|                                                                                                   |
|   [ HiveMQ Cloud (TLS 8883) ]          OR          [ Local Mosquitto Broker (1883) ]              |
|   Topic: `battery/cells/data`                      Topic: `battery/cells/data`                    |
+---------------------------------------------------------------------------------------------------+
                    │                                                   │
                    ▼                                                   ▼
+---------------------------------------+       +---------------------------------------------------+
|          LAYER 4: NODE-RED            |       |         ANALYTICS & INGESTION PIPELINE            |
|                                       |       |                                                   |
| - JSON Payload Validation             |       | 1. Data Validator (Schema & Bounds Sanitizer)     |
| - Voltage Spread Calculation          |       | 2. Math Calculations (V_max, V_min, ΔV, ΔV_mV)    |
| - Multi-stream Threshold Routing      |       | 3. Sensor Quality Assessor (NaN/Fault Trap)       |
| - Secondary Alert Publication         |       | 4. Rule-Based Detector (Critical > Warning Check) |
|   (`battery/alerts/events`)           |       | 5. Isolation Forest ML Inference (Anomaly Score)  |
+---------------------------------------+       +---------------------------------------------------+
                                                                        │
                                                                        ▼
+---------------------------------------------------------------------------------------------------+
|                                     PERSISTENCE LAYER (SQLITE)                                    |
|                                                                                                   |
|   `data/battery.db` (WAL Mode enabled, Parameterized Queries, Fast B-Tree Indexes)                |
|   - `battery_readings`: Historical telemetry, aggregated metrics, ML anomaly scores               |
|   - `alerts`: Event-driven threshold breaches, state escalations, operator acknowledgements       |
|   - `users`: Hashed user credentials and role-based permissions                                   |
+---------------------------------------------------------------------------------------------------+
                                                                        │
                                                                        ▼
+---------------------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER (STREAMLIT)                                 |
|                                                                                                   |
|   - Authentication & Role Session Controller                                                      |
|   - Live Cell Voltage & Temperature Profile Cards                                                 |
|   - Interactive Plotly Time-Series Visualizations & Spread Threshold Annotations                  |
|   - Operator Alert Acknowledgment Matrix                                                          |
|   - Simulation Scenario Injection & CSV Historical Export Facility                                |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Inbound Telemetry Payload Schema
Both the ESP32 hardware firmware and Python synthetic generator transmit standardized JSON payloads:

```json
{
  "pack_id": "PACK-01",
  "timestamp": "2026-10-29T15:20:00.000Z",
  "mode": "simulation",
  "source": "synthetic_generator",
  "scenario": "normal",
  "cell_count": 4,
  "cell_voltages": [3.8124, 3.8189, 3.8105, 3.8142],
  "cell_temperatures": [28.2, 28.5, 28.3, 28.4],
  "current_a": 2.500
}
```

---

## 3. Database Entity-Relationship Model (SQLite)

### Table: `battery_readings`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing record ID |
| `pack_id` | TEXT | Battery pack identifier (Indexed) |
| `timestamp_utc` | TEXT | Standardized ISO 8601 UTC timestamp |
| `timestamp_epoch` | REAL | Epoch time in seconds for high-speed chronological range queries (Indexed) |
| `mode` | TEXT | Operating mode (`simulation` or `hardware`) |
| `source` | TEXT | Originating source (`synthetic_generator` or `esp32_sensor_array`) |
| `cell_count` | INTEGER | Number of series-connected cells |
| `cell_voltages_json`| TEXT | JSON array containing individual cell voltages |
| `cell_temperatures_json`| TEXT | JSON array containing individual cell surface temperatures |
| `current_a` | REAL | Battery discharge/charge current in Amperes |
| `v_max` | REAL | Highest individual cell voltage |
| `v_min` | REAL | Lowest individual cell voltage |
| `delta_v` | REAL | Maximum voltage divergence ($V_{max} - V_{min}$) in Volts |
| `delta_v_mv` | REAL | Voltage spread scaled to millivolts ($\Delta V \times 1000$) |
| `mean_v` | REAL | Arithmetic average cell voltage |
| `t_max` | REAL | Peak cell surface temperature in °C |
| `t_min` | REAL | Lowest cell surface temperature in °C |
| `delta_t` | REAL | Temperature gradient across pack ($T_{max} - T_{min}$) |
| `mean_t` | REAL | Pack average temperature |
| `rule_status` | TEXT | Operational state (`NORMAL`, `WARNING`, `CRITICAL`, `SENSOR_FAULT`) |
| `rule_reasons_json`| TEXT | Serialized array of detected threshold violation causes |
| `ml_prediction` | INTEGER | Anomaly prediction ($1 = \text{Inlier/Normal}$, $-1 = \text{Outlier/Anomaly}$) |
| `ml_anomaly_score`| REAL | Normalized anomaly score from Isolation Forest |
| `data_quality` | TEXT | Sensor health status (`HEALTHY` or `SENSOR_ISSUE`) |
| `created_at` | TEXT | Record insertion timestamp |

### Table: `alerts`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Alert ID |
| `pack_id` | TEXT | Battery pack identifier |
| `timestamp_utc` | TEXT | Time alarm condition triggered |
| `alert_level` | TEXT | Severity (`WARNING`, `CRITICAL`, `SENSOR_FAULT`) |
| `affected_cells_json`| TEXT | Array of cell indices contributing to divergence |
| `delta_v_mv` | REAL | Voltage spread in mV at time of alert |
| `max_temp` | REAL | Maximum cell temperature at time of alert |
| `reason` | TEXT | Detailed alarm message |
| `acknowledged` | INTEGER | 0 = Unacknowledged, 1 = Acknowledged by operator |
| `acknowledged_at` | TEXT | Operator acknowledgement timestamp |
| `acknowledged_by` | TEXT | Username of operator acknowledging alert |

### Table: `users`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | User ID |
| `username` | TEXT UNIQUE | Unique login handle |
| `password_hash` | TEXT | Salted Bcrypt or PBKDF2 hash |
| `role` | TEXT | Role (`administrator` or `operator`) |
| `created_at` | TEXT | User creation timestamp |
