# Layer 4 — Node-RED Automation Flow Guide

## 1. Overview
Node-RED provides visual low-code event-driven orchestration and external alerting for the battery monitoring architecture.

The provided flow (`battery_monitoring_flow.json`) subscribes to the MQTT telemetry topic (`battery/cells/data`), validates inbound payloads, calculates cell voltage spread ($\Delta V_{mV}$) and peak temperature, evaluates thresholds, and branches execution across 4 distinct streams:
1. **NORMAL** ($< 20\text{ mV}$, $< 45^\circ\text{C}$): Routed to monitoring logs.
2. **WARNING** ($\ge 20\text{ mV}$ and $< 50\text{ mV}$, or $\ge 45^\circ\text{C}$): Emits warning telemetry and routes to alert formatter.
3. **CRITICAL** ($\ge 50\text{ mV}$, or $\ge 60^\circ\text{C}$): Emits critical alarm and publishes event to `battery/alerts/events`.
4. **SENSOR FAULT**: Catches missing cell readings, NaN values, or malformed packets.

---

## 2. Architecture & Data Integrity Safeguard
> [!IMPORTANT]
> **Single Source of Truth Principle:**
> The Python backend (`src/database.py`, `src/detection.py`, and `src/ml_pipeline.py`) remains the authoritative processor for SQLite persistence and machine learning inference. 
> Node-RED acts as a **parallel supervisory alert orchestrator**. This prevents duplicate database inserts, race conditions, or conflicting alarm states between Node-RED and Python.

---

## 3. Node-RED Installation on Windows

If Node-RED is not already installed on your system, install it using Node.js:

1. **Install Node.js (LTS version)**:
   - Download the Windows installer from [https://nodejs.org/](https://nodejs.org/)
   - Run the installer and verify installation:
     ```powershell
     node -v
     npm -v
     ```

2. **Install Node-RED globally**:
   ```powershell
   npm install -g --unsafe-perm node-red
   ```

3. **Start Node-RED**:
   ```powershell
   node-red
   ```
   Open your browser and navigate to: `http://localhost:1880`

---

## 4. How to Import the Flow

1. Open Node-RED editor at `http://localhost:1880`.
2. Click the top-right hamburger menu (`☰`) and select **Import**.
3. Click **Select a file to import** and browse to:
   `node_red/battery_monitoring_flow.json`
4. Select **Import to new flow** and click **Import**.
5. Configure the MQTT Broker node:
   - Double click the **Local/Cloud MQTT Broker** node in the config panel.
   - For Local Mosquitto: set Server to `localhost`, Port `1883`.
   - For HiveMQ Cloud: set Server to your cluster URL (e.g. `xxxx.s1.eu.hivemq.cloud`), Port `8883`, check **Enable TLS**, and enter your HiveMQ username and password in the **Security** tab.
6. Click the red **Deploy** button in the top right.

---

## 5. Flow Nodes Breakdown
- **MQTT In (`battery/cells/data`)**: Subscribes to telemetry from simulator or ESP32.
- **Parse JSON**: Automatically deserializes UTF-8 JSON payloads into JavaScript objects.
- **Calculate Imbalance & Classify**: JavaScript function executing exact $\Delta V = V_{max} - V_{min}$ and temperature bounds. Checks CRITICAL conditions before WARNING.
- **Debug Nodes**: Inspect messages directly inside the Node-RED debug panel.
- **MQTT Out (`battery/alerts/events`)**: Re-publishes formatted JSON alarm events for secondary SCADA or industrial gateways.
