# User Manual & Operator Guide

## 1. Quick Launch
To start the platform immediately:
Double-click **`run_project.bat`** in the project root, or execute:
```powershell
.\.venv\Scripts\streamlit.exe run app.py
```
Open your browser and navigate to:
**`http://localhost:8501`**

---

## 2. Authentication
- Enter the default administrative credentials:
  - **Username:** `admin`
  - **Password:** `admin_demo_password`
- Click **Log In**. The secure session will be established and the Overview page will load.

---

## 3. Dashboard Features & Controls

### A. Top Telemetry Tiles
- **Voltage Spread ($\Delta V$):** Real-time difference between the highest and lowest cell voltage in millivolts ($mV$) and Volts ($V$).
- **Min / Max / Mean Cell Voltages:** Key pack-level diagnostic statistics.
- **Peak Temperature:** Highest cell casing surface temperature with thermal gradient indicator.
- **Badges:** Shows operating mode (`SIMULATION` or `HARDWARE`) and rule status (`NORMAL`, `WARNING`, `CRITICAL`).

### B. Live Charts
- **Live Cell Voltages Bar Chart:** Color-coded bars showing individual cell voltages. Diverging cells that trigger imbalance are highlighted in amber/red.
- **Cell Temperature Profile:** Bar chart of contact temperature sensors.
- **Voltage Spread History:** Time-series tracking $\Delta V_{mV}$ against the **20 mV Warning** and **50 mV Critical** reference limits.
- **Multi-Cell Voltage Trends:** Individual trendlines for each cell over time.

### C. Cell Sanity Matrix
A comparison table showing:
- Exact measured voltage and surface temperature for each cell.
- Calculated millivolt deviation from the pack mean voltage:
  $$\text{Deviation} = (V_{cell} - V_{mean}) \times 1000$$
- Diagnostic condition label (`Nominal`, `Warning Imbalance`, `Critical Deviation`, `Sensor Missing`).

---

## 4. Demonstrating Scenarios from the Dashboard
In the sidebar, locate **Simulation Controls**:
1. Select **`imbalance`** from the dropdown and click **Apply Scenario**.
   - Observe Cell 2 discharge faster than others.
   - Watch the Voltage Spread rise past 20 mV (triggering **WARNING** status).
   - Once spread exceeds 50 mV, watch the badge change to **CRITICAL** and a high-priority alarm logged.
2. Select **`overheating`** and click **Apply Scenario**:
   - Cell 3 temperature will rise rapidly past 45°C (warning) and 60°C (critical).
3. Select **`sensor_failure`**:
   - Simulates a disconnected ADC line (0.0 V reading), triggering **SENSOR_FAULT**.
4. Select **`normal`**:
   - Resets all cells to balanced, healthy nominal conditions (spread < 15 mV).

---

## 5. Alert Acknowledgement & CSV Export
- **Acknowledge Alerts:** Navigate to **Alert Management** in the sidebar. Click **Acknowledge Alert #ID** to register operator review with timestamp.
- **Export Data:** Navigate to **Historical Records & Export** in the sidebar. Click **Generate & Export Full Historical CSV** to create a snapshot file, then click **Download Historical CSV File**.
