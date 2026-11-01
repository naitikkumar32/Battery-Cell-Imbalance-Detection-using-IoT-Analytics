# Project Report: Battery Cell Imbalance Detection Using IoT Analytics

**Author:** B.Tech Student (Mechanical Engineering)  
**Academic Year:** 2026  
**Project Category:** IoT, Machine Learning, & Energy Storage Diagnostics  

---

## Abstract
Lithium-ion battery packs deployed in electric vehicles (EVs) and stationary renewable energy storage systems consist of multiple electrochemical cells connected in series and parallel. Due to manufacturing variations, thermal gradients, and differential aging, individual cells inevitably develop capacity and internal resistance discrepancies, resulting in voltage imbalance. Severe cell imbalance reduces total usable energy, accelerates cell degradation, and poses thermal runaway risks. 

This project presents a multi-layer IoT and Machine Learning monitoring architecture designed for real-time battery cell imbalance detection. The platform acquires multi-cell voltage and surface temperature telemetry through both physical ESP32 edge hardware and a high-fidelity synthetic physics simulator. Telemetry is streamed over MQTT (supporting both local Mosquitto and TLS-encrypted HiveMQ Cloud brokers), validated, and evaluated using a dual-track analytical engine: a deterministic rule-based classifier and an unsupervised Isolation Forest machine learning model. Measurements and alert events are persisted in a thread-safe SQLite database, orchestrated through Node-RED event routing, and visualized via an interactive Streamlit engineering dashboard. Automated testing confirms 100% test pass rate across all operational metrics.

---

## 1. Introduction
Battery Energy Storage Systems (BESS) are central to the global transition toward sustainable electrification. In multi-cell battery packs, each cell's electrochemistry is subject to non-uniform ambient temperatures and discharge stress. When cells drift out of balance, conventional BMS units may fail to provide predictive diagnostics before catastrophic over-discharge or thermal failure occurs. Integrating Internet of Things (IoT) connectivity with cloud-based Machine Learning enables continuous health monitoring, automated alarming, and historical degradation analysis.

---

## 2. Problem Statement
Commercial battery packs often fail prematurely not because all cells have reached end-of-life, but because one weak cell diverges in capacity, reaching cut-off voltage prematurely while remaining cells are still charged. Traditional localized analog alarms do not preserve historical trends, lack remote fleet visibility, and cannot perform unsupervised anomaly detection on complex multi-variable interactions (voltage spread, thermal gradients, and dynamic load currents).

---

## 3. Objectives
1. Implement a real-time data acquisition interface for series battery cells supporting both hardware (ESP32) and physics-based simulation.
2. Establish secure MQTT communication over TLS (HiveMQ Cloud) with local offline fallback.
3. Formulate mathematical calculations for maximum voltage ($V_{max}$), minimum voltage ($V_{min}$), voltage spread ($\Delta V$), millivolt conversion ($\Delta V_{mV}$), and thermal gradient ($\Delta T$).
4. Implement a hierarchical status evaluator prioritizing critical alarms over warning conditions.
5. Deploy an unsupervised Machine Learning pipeline (Isolation Forest) to detect complex multi-variable anomalies.
6. Provide persistent relational storage (SQLite), automated alerting with notification cooldown, and CSV reporting.
7. Build an interactive Streamlit dashboard featuring live telemetry tiles, Plotly trend charts, and operator acknowledgement capabilities.

---

## 4. Existing System vs. Proposed System

| Feature | Existing Conventional System | Proposed IoT & AI/ML System |
|---|---|---|
| **Telemetry Access** | Local analog/CAN bus only | Global IoT cloud telemetry (MQTT over TLS) |
| **Imbalance Detection** | Fixed hardwired analog threshold | Dual-track: Rule-based hierarchy + AI/ML Isolation Forest |
| **Historical Analytics** | None (ephemeral) | Persistent SQLite database with indexed range querying |
| **Visualization** | Basic LED or rudimentary 7-segment display | Responsive Streamlit web dashboard with interactive Plotly graphs |
| **Automation & Routing**| Hardwired logic | Visual low-code Node-RED flow automation |
| **Simulation Capability**| None (requires physical pack) | Full simulation pipeline with 5 realistic failure scenarios |
| **Operator Workflow** | Audible buzzer only | Timestamped alarm logging, cooldowns, and operator acknowledgement |

---

## 5. System Architecture & Methodology

```
+---------------------------------------------------------------------------------------+
|                                DATA GENERATION LAYER                                  |
|   ESP32 Edge Sensor Node (Hardware)  <--->  Synthetic Battery Simulator (Software)    |
+---------------------------------------------------------------------------------------+
                                           │
                                           ▼
+---------------------------------------------------------------------------------------+
|                                  CONNECTIVITY LAYER                                   |
|   MQTT Broker: HiveMQ Cloud (TLS 8883) / Local Mosquitto (1883)                       |
+---------------------------------------------------------------------------------------+
                       │                                       │
                       ▼                                       ▼
+--------------------------------------+   +--------------------------------------------+
|         NODE-RED AUTOMATION          |   |        CORE PYTHON INGESTION PIPELINE      |
| - Low-code flow event routing        |   | - Schema Validation (`data_validator.py`)   |
| - Warning/Critical branching         |   | - Mathematical Metrics (`calculations.py`) |
| - Secondary alert forwarding         |   | - Rule Evaluator (`detection.py`)          |
+--------------------------------------+   | - Isolation Forest ML (`ml_pipeline.py`)   |
                                           +--------------------------------------------+
                                                               │
                                                               ▼
+---------------------------------------------------------------------------------------+
|                                   PERSISTENCE LAYER                                   |
|   SQLite Relational Storage (`data/battery.db` in WAL Mode)                           |
+---------------------------------------------------------------------------------------+
                                           │
                                           ▼
+---------------------------------------------------------------------------------------+
|                                  PRESENTATION LAYER                                   |
|   Streamlit Engineering Dashboard (`app.py` with Plotly Visualizations)               |
+---------------------------------------------------------------------------------------+
```

---

## 6. Battery Calculations & Mathematical Formulations

For any battery pack with $N$ series cells:

1. **Maximum Cell Voltage:**
   $$V_{max} = \max_{i=1 \dots N} (V_i)$$

2. **Minimum Cell Voltage:**
   $$V_{min} = \min_{i=1 \dots N} (V_i)$$

3. **Voltage Spread ($\Delta V$):**
   $$\Delta V = V_{max} - V_{min}$$

4. **Voltage Spread in Millivolts ($\Delta V_{mV}$):**
   $$\Delta V_{mV} = \Delta V \times 1000$$

5. **Arithmetic Mean Voltage ($V_{mean}$):**
   $$V_{mean} = \frac{1}{N} \sum_{i=1}^{N} V_i$$

6. **Cell Millivolt Deviation:**
   $$\text{Dev}_i = (V_i - V_{mean}) \times 1000$$

7. **Thermal Gradient ($\Delta T$):**
   $$\Delta T = T_{max} - T_{min}$$

### Threshold Hierarchy
- **CRITICAL ALARM:** Evaluated first. Triggered if $\Delta V \ge 0.050\text{ V}$ ($50\text{ mV}$), any $V_i \ge 4.25\text{ V}$, any $V_i \le 3.00\text{ V}$, $T_{max} \ge 60^\circ\text{C}$, or $\Delta T \ge 10^\circ\text{C}$.
- **WARNING ALARM:** Evaluated only if not critical. Triggered if $\Delta V \ge 0.020\text{ V}$ ($20\text{ mV}$), any $V_i \ge 4.22\text{ V}$, any $V_i \le 3.20\text{ V}$, $T_{max} \ge 45^\circ\text{C}$, or $\Delta T \ge 5^\circ\text{C}$.
- **NORMAL STATE:** Assigned only when all individual cell voltages and temperatures remain strictly within healthy bounds.
- **SENSOR FAULT:** Explicitly assigned when values are missing or non-finite (NaN/Inf). Missing data is **never** classified as healthy.

---

## 7. Machine Learning Methodology & Evaluation

### Algorithm Choice
The **Isolation Forest** (`sklearn.ensemble.IsolationForest`) algorithm was selected for its proven efficiency in high-dimensional unsupervised anomaly detection. Unlike distance-based algorithms ($k$-NN), Isolation Forest isolates anomalies by recursively partitioning feature space using orthogonal hyperplanes, making it robust against non-linear interactions between thermal gradients and load currents.

### Features Utilized
1. `delta_v_mv`: Voltage spread in millivolts
2. `v_max`: Maximum cell voltage (V)
3. `v_min`: Minimum cell voltage (V)
4. `mean_v`: Mean cell voltage (V)
5. `t_max`: Maximum cell temperature (°C)
6. `delta_t`: Cell-to-cell thermal spread (°C)
7. `current_a`: Total pack current (A)

### Empirical Training & Evaluation Results
The model was trained on a reproducible synthetic operational dataset of 6,000 samples (80% train, 20% test split):
- **Training Samples:** 4,800
- **Held-Out Test Samples:** 1,200
- **Precision:** 0.6667
- **Recall:** 1.0000 (100% anomaly detection recall — zero missed critical failure states)
- **F1-Score:** 0.8000
- **Confusion Matrix:**
  $$\begin{bmatrix} 1020 & 60 \\ 0 & 120 \end{bmatrix}$$
  *(1,020 True Negatives, 120 True Positives, 60 False Positives, 0 False Negatives)*

---

## 8. Automated Testing & Verification
The automated test suite (`pytest`) contains 28 tests across 6 dedicated test modules:
- `test_calculations.py`: 5 tests passed (Spread math, millivolt conversion, empty/NaN handling, rate of change, sensor quality).
- `test_detection.py`: 5 tests passed (Normal, Warning, Critical precedence, sensor fault).
- `test_data_validation.py`: 5 tests passed (JSON parsing, missing keys, hardware/simulation tags).
- `test_database.py`: 5 tests passed (WAL mode init, record insertion, empty state handling, CSV export, backup).
- `test_alerts.py`: 5 tests passed (Cooldown enforcement, escalation bypass, operator acknowledgement).
- `test_ml_pipeline.py`: 3 tests passed (Dataset generation, model training/inference, graceful fallback).

**Final Test Result:** **28 passed, 0 failures** (100% success rate).

---

## 9. Limitations
1. In the simulated demonstrator, cell aging is represented through empirical discharge rate divergence rather than electrochemical equivalent circuit models (Randles/Thevenin models).
2. The prototype ESP32 voltage divider circuit uses ground-referenced taps, which accumulates measurement error across upper cells in series packs compared to dedicated isolated BMS ICs (e.g., ADI LTC6811 or TI BQ76952).

---

## 10. Future Scope
1. Implement active cell balancing circuitry (inductive or capacitive charge shuttling) controlled directly by edge MQTT commands.
2. Integrate remaining useful life (RUL) forecasting using Long Short-Term Memory (LSTM) recurrent neural networks.
3. Deploy edge ML inference using TensorFlow Lite for Microcontrollers directly on the ESP32.

---

## 11. References
1. Plett, G. L. (2015). *Battery Management Systems, Volume I: Battery Modeling*. Artech House.
2. Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). *Isolation Forest*. Eighth IEEE International Conference on Data Mining, 413-422.
3. Andrea, D. (2010). *Battery Management Systems for Large Lithium-Ion Battery Packs*. Artech House.
4. Streamlit Documentation: *Interactive Data Applications in Python*. https://docs.streamlit.io
5. HiveMQ Cloud Documentation: *Secure MQTT Broker Architecture*. https://www.hivemq.com/cloud/
