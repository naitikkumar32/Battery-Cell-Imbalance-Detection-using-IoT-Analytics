# Battery Cell Imbalance Detection Using IoT Analytics

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Isolation%20Forest-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-28%20Passed-brightgreen.svg)]()

> A production-ready, full-stack IoT and Machine Learning platform engineered to monitor multi-cell lithium battery packs, calculate real-time voltage and temperature imbalance, detect anomalies via an Isolation Forest pipeline, persist telemetry to SQLite, orchestrate alarms through Node-RED, and provide an interactive web dashboard for battery safety diagnostics.

---

## 1. Project Overview & The Six Layers

This platform spans all six layers of modern industrial IoT and energy storage analytics:

1. **Layer 1 — Synthetic Data → Local Pipeline → CSV → Dashboard:**
   - Multi-scenario physics simulation engine (`normal`, `imbalance`, `overheating`, `sensor_fault`, `missing_data`).
   - Generates telemetry every 2 seconds with realistic noise and drift.
   - Fully functional offline without cloud credentials.
2. **Layer 2 — Synthetic Data → MQTT → HiveMQ Cloud → Dashboard:**
   - Secure TLS-encrypted MQTT (Port 8883) with HiveMQ Cloud integration.
   - Automatic reconnection with exponential backoff and schema validation.
   - Graceful offline fallback.
3. **Layer 3 — MQTT → SQLite Database → Dashboard:**
   - Thread-safe SQLite persistence in `data/battery.db` using WAL mode.
   - Parameterized queries, automatic schema initialization, and B-tree indexes.
   - CSV export and automatic database backup routines.
4. **Layer 4 — Node-RED Automation Flow:**
   - Pre-built flow (`node_red/battery_monitoring_flow.json`) for event-driven stream routing.
   - Multi-branching for `NORMAL`, `WARNING`, `CRITICAL`, and `SENSOR_FAULT`.
5. **Layer 5 — AI/ML Anomaly Detection → Auth → Dashboard → Alerts:**
   - Unsupervised Isolation Forest model detecting multi-variable anomalies.
   - Secure Bcrypt/PBKDF2 login authentication with session controls.
   - Event-driven alert lifecycle with state escalation and notification cooldowns.
6. **Layer 6 — Real Sensors → ESP32 Microcontroller → Physical Alerts:**
   - Complete ESP32 Arduino C++ firmware (`esp32_battery_monitor.ino`).
   - Precision voltage divider taps and 10k NTC thermistor interfaces.
   - Onboard physical LED and active buzzer alarms.

---

## 2. System Architecture

```
+-----------------------------------------------------------------------------------+
|                              DATA GENERATION SOURCES                              |
|   [ Physical ESP32 Hardware Node ]           [ Python Synthetic Simulator ]       |
|     - Voltage Dividers (4S Pack)               - Scenarios: Imbalance, Heat, etc. |
|     - 10k NTC Surface Thermistors              - Realistic Noise & Discharge      |
+-----------------------------------------------------------------------------------+
                                       │
                                       ▼
+-----------------------------------------------------------------------------------+
|                                TRANSPORT LAYER                                    |
|   MQTT Broker: HiveMQ Cloud (TLS 8883) or Local Mosquitto (1883)                  |
|   Topic: `battery/cells/data`                                                     |
+-----------------------------------------------------------------------------------+
                     │                                         │
                     ▼                                         ▼
+---------------------------------------+   +---------------------------------------+
|          LAYER 4: NODE-RED            |   |          INGESTION & ANALYTICS        |
| - Low-code event flow                 |   | - Schema Validation & Quality Check   |
| - Warning & Critical branching        |   | - Mathematical Imbalance Engine       |
| - Secondary alerts (`battery/alerts`) |   | - Rule-based Severity Evaluator       |
+---------------------------------------+   | - Isolation Forest Anomaly Inference  |
                                            +---------------------------------------+
                                                               │
                                                               ▼
+-----------------------------------------------------------------------------------+
|                            STORAGE LAYER (SQLITE WAL)                             |
|   `data/battery.db` - Tables: `battery_readings`, `alerts`, `users`               |
+-----------------------------------------------------------------------------------+
                                       │
                                       ▼
+-----------------------------------------------------------------------------------+
|                           PRESENTATION LAYER (STREAMLIT)                          |
|   URL: http://localhost:8501                                                      |
|   - Real-time Cell Voltage & Temp Cards   - Multi-Cell Plotly Time Series         |
|   - Interactive Scenario Injection        - Alert History & Acknowledgement       |
|   - CSV Historical Telemetry Export       - Settings & Threshold Configuration    |
+-----------------------------------------------------------------------------------+
```

---

## 3. Battery Calculations & Mathematical Formulas

For each battery pack consisting of $N$ series cells:

- **Maximum Cell Voltage:** $V_{max} = \max(V_1, V_2, \dots, V_N)$
- **Minimum Cell Voltage:** $V_{min} = \min(V_1, V_2, \dots, V_N)$
- **Voltage Spread ($\Delta V$):** $\Delta V = V_{max} - V_{min}$
- **Voltage Spread in Millivolts:** $\Delta V_{mV} = \Delta V \times 1000$
- **Pack Mean Voltage:** $V_{mean} = \frac{1}{N} \sum_{i=1}^N V_i$
- **Thermal Gradient ($\Delta T$):** $\Delta T = T_{max} - T_{min}$

### Demonstration Threshold Hierarchy (Configurable in `config/thresholds.yaml`):
1. **CRITICAL (Evaluated First):** $\Delta V \ge 0.050\text{ V}$ ($50\text{ mV}$), $V_{cell} \ge 4.25\text{ V}$, $V_{cell} \le 3.00\text{ V}$, $T_{max} \ge 60^\circ\text{C}$, or $\Delta T \ge 10^\circ\text{C}$.
2. **WARNING (Evaluated Second):** $\Delta V \ge 0.020\text{ V}$ ($20\text{ mV}$), $V_{cell} \ge 4.22\text{ V}$, $V_{cell} \le 3.20\text{ V}$, $T_{max} \ge 45^\circ\text{C}$, or $\Delta T \ge 5^\circ\text{C}$.
3. **NORMAL:** All cell voltages and temperatures remain within nominal boundaries.
4. **SENSOR FAULT:** Raised when readings are missing, non-finite (NaN/Inf), or physically impossible. Missing data is never classified as healthy.

---

## 4. Quick Start & Execution

### 1-Click Launch (Windows)
Double-click **`run_project.bat`** or run:
```powershell
.\run_project.bat
```
This batch script automatically verifies `.venv`, initializes SQLite tables, verifies the ML model, and launches the Streamlit web dashboard.

### Manual Launch via Terminal
```powershell
# 1. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

# 2. Start Dashboard
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

- **Default Username:** `admin`
- **Default Password:** `admin_demo_password`

---

## 5. Machine Learning Pipeline & Empirical Metrics

The anomaly detection engine utilizes **Isolation Forest** trained on multi-variable telemetry:
- **Features Used:** `delta_v_mv`, `v_max`, `v_min`, `mean_v`, `t_max`, `delta_t`, `current_a`
- **Trained Samples:** 4,800
- **Held-Out Test Samples:** 1,200
- **Precision:** 0.6667
- **Recall:** 1.0000 (100% anomaly recall — zero missed critical failure states)
- **F1-Score:** 0.8000
- **Confusion Matrix:** `[[1020, 60], [0, 120]]`

To retrain the model at any time:
```powershell
python scripts/generate_dataset.py
python scripts/train_model.py
```

---

## 6. Automated Testing

Run the automated test suite:
```powershell
pytest -v
```

### Test Results Summary:
```
tests/test_alerts.py::test_normal_reading_no_alert PASSED                [  3%]
tests/test_alerts.py::test_warning_reading_triggers_alert PASSED         [  7%]
tests/test_alerts.py::test_cooldown_suppresses_repeat_alerts PASSED      [ 10%]
tests/test_alerts.py::test_escalation_bypasses_cooldown PASSED           [ 14%]
tests/test_alerts.py::test_alert_acknowledgement PASSED                  [ 17%]
tests/test_calculations.py::test_voltage_spread_calculation PASSED       [ 21%]
tests/test_calculations.py::test_empty_and_null_voltages PASSED          [ 25%]
tests/test_calculations.py::test_temperature_metrics PASSED              [ 28%]
tests/test_calculations.py::test_rate_of_change PASSED                   [ 32%]
tests/test_calculations.py::test_sensor_quality_assessment PASSED        [ 35%]
tests/test_data_validation.py::test_valid_json_payload PASSED            [ 39%]
tests/test_data_validation.py::test_missing_pack_id PASSED               [ 42%]
tests/test_data_validation.py::test_malformed_json_string PASSED         [ 46%]
tests/test_data_validation.py::test_empty_cell_list PASSED               [ 50%]
tests/test_data_validation.py::test_hardware_mode_parsing PASSED         [ 53%]
tests/test_database.py::test_db_initialization PASSED                    [ 57%]
tests/test_database.py::test_insert_and_retrieve_reading PASSED          [ 60%]
tests/test_database.py::test_empty_database_safety PASSED                [ 64%]
tests/test_database.py::test_csv_export PASSED                           [ 67%]
tests/test_database.py::test_database_backup PASSED                      [ 71%]
tests/test_detection.py::test_normal_status PASSED                       [ 75%]
tests/test_detection.py::test_warning_status PASSED                      [ 78%]
tests/test_detection.py::test_critical_status PASSED                     [ 82%]
tests/test_detection.py::test_critical_takes_precedence_over_warning PASSED [ 85%]
tests/test_detection.py::test_missing_data_not_healthy PASSED            [ 89%]
tests/test_ml_pipeline.py::test_dataset_generation PASSED                [ 92%]
tests/test_ml_pipeline.py::test_training_and_inference PASSED            [ 96%]
tests/test_ml_pipeline.py::test_fallback_when_model_missing PASSED       [100%]

======================= 28 passed, 0 failures in 5.92s ========================
```

---

## 7. Folder Structure

```
HCL Battery cell imbalence detection/
│
├── app.py                      # Main Streamlit Dashboard
├── requirements.txt            # Python dependencies (pinned)
├── pytest.ini                  # Pytest configuration
├── run_project.bat             # 1-Click Windows execution script
├── stop_instructions.md        # Process termination guide
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete system documentation
│
├── config/
│   ├── settings.yaml           # Global system and MQTT configuration
│   └── thresholds.yaml         # Configurable battery safety thresholds
│
├── src/
│   ├── __init__.py             # Core package init
│   ├── calculations.py         # Imbalance math, delta V, dV/dt, metrics
│   ├── data_validator.py       # JSON telemetry schema validation
│   ├── detection.py            # Hierarchical rule-based status detector
│   ├── simulator.py            # Multi-scenario synthetic generator
│   ├── database.py             # SQLite WAL persistence layer
│   ├── alerts.py               # Alert engine with cooldown & notifications
│   ├── auth.py                 # Bcrypt/PBKDF2 login authentication
│   ├── ml_pipeline.py          # Isolation Forest anomaly detection pipeline
│   ├── mqtt_client.py          # Base MQTT manager with TLS support
│   ├── mqtt_publisher.py       # MQTT publisher utility
│   ├── mqtt_subscriber.py      # MQTT ingestion & pipeline worker
│   └── dashboard_helpers.py    # Plotly charts, UI pills & CSS
│
├── data/                       # SQLite storage (data/battery.db)
├── datasets/                   # Generated training datasets
├── models/                     # Saved ML models (.joblib)
├── exports/                    # CSV telemetry exports
├── logs/                       # Application logs
│
├── node_red/
│   ├── battery_monitoring_flow.json  # Node-RED routing flow
│   └── README.md               # Node-RED installation & setup guide
│
├── firmware/
│   └── esp32_battery_monitor/
│       ├── esp32_battery_monitor.ino # ESP32 C++ firmware
│       └── README.md           # Wiring diagram, BOM & calibration
│
├── tests/                      # Automated Pytest Suite (28 tests)
│   ├── test_calculations.py
│   ├── test_data_validation.py
│   ├── test_database.py
│   ├── test_detection.py
│   ├── test_alerts.py
│   └── test_ml_pipeline.py
│
├── scripts/                    # Automation and utility scripts
│   ├── init_database.py        # Database schema initialization
│   ├── generate_dataset.py     # Training data generation
│   ├── train_model.py          # Isolation Forest model training
│   └── verify_setup.py         # Environment verification
│
└── docs/                       # Comprehensive documentation
    ├── architecture.md         # Detailed architectural specifications
    ├── installation.md         # Windows installation guide
    ├── user_manual.md          # Dashboard operator guide
    ├── troubleshooting.md      # Common errors and resolutions
    ├── hardware_setup.md       # Electrical wiring & bench safety
    └── project_report.md       # Mini-project college submission report
```

---

## 8. HiveMQ Cloud Configuration Guide

To stream telemetry to or from HiveMQ Cloud:
1. Create a free serverless cluster at [https://www.hivemq.com/cloud/](https://www.hivemq.com/cloud/).
2. In HiveMQ console, obtain your **Cluster URL** (e.g. `your-cluster.s1.eu.hivemq.cloud`) and configure credentials under **Access Management**.
3. Create a local `.env` file from `.env.example`:
   ```env
   APP_MODE=hardware
   MQTT_BROKER_HOST=your-cluster.s1.eu.hivemq.cloud
   MQTT_PORT=8883
   MQTT_USE_TLS=true
   MQTT_USERNAME=your_username
   MQTT_PASSWORD=your_password
   MQTT_TOPIC=battery/cells/data
   ```
4. Start the dashboard. The MQTT status indicator will display `🟢 Connected`.

---

## 9. Hardware Wiring & Safety
For physical ESP32 implementation:
- Consult [`docs/hardware_setup.md`](file:///c:/Users/jatin/OneDrive/Documents/Desktop/HCL%20Battery%20cell%20imbalence%20detection/docs/hardware_setup.md) and [`firmware/esp32_battery_monitor/README.md`](file:///c:/Users/jatin/OneDrive/Documents/Desktop/HCL%20Battery%20cell%20imbalence%20detection/firmware/esp32_battery_monitor/README.md).
- **Never** connect cells directly to ESP32 pins. Use the documented 1% precision resistor divider network.
- Test with a 50mA current-limited bench power supply prior to real battery connection.
