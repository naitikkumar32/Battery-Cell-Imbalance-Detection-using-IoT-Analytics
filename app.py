"""
Main Application: app.py
Streamlit Web Dashboard for Battery Cell Imbalance Detection Using IoT Analytics.

Features:
- Authentication & Session State Management
- Real-time Telemetry Dashboard (Voltage Cards, Spread in mV, Temperature Cards)
- Rule-based Status Classification & AI/ML Anomaly Detection
- Interactive Plotly Visualizations (Cell comparisons, Historical spreads, Multi-cell trends)
- Simulation Controls (Normal, Imbalance, Overheating, Sensor Fault, Missing Data)
- MQTT HiveMQ / Local Broker Integration Status
- Alert Acknowledgement System & CSV Data Export
- Comprehensive Settings & Threshold Customization
"""

import os
import time
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.database import BatteryDatabase
from src.calculations import calculate_voltage_metrics, calculate_temperature_metrics
from src.detection import evaluate_pack_status, load_thresholds
from src.alerts import AlertManager
from src.auth import AuthManager
from src.ml_pipeline import AnomalyDetector
from src.simulator import BatterySimulator
from src.mqtt_subscriber import BatteryMQTTSubscriber
from src.dashboard_helpers import (
    apply_custom_css,
    render_status_pill,
    render_mode_pill,
    check_is_stale,
    create_cell_voltage_chart,
    create_temperature_chart,
    create_voltage_spread_history_chart,
    create_multi_cell_history_chart
)

# Page configuration
st.set_page_config(
    page_title="Battery Imbalance Detection | IoT Analytics",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(apply_custom_css(), unsafe_allow_html=True)

# Initialize Core Services (cached across reruns)
@st.cache_resource
def get_database():
    db_path = os.getenv("DATABASE_PATH", "data/battery.db")
    return BatteryDatabase(db_path=db_path)

@st.cache_resource
def get_auth_manager():
    return AuthManager(get_database())

@st.cache_resource
def get_ml_detector():
    detector = AnomalyDetector()
    if not detector.is_loaded:
        try:
            detector.train()
        except Exception:
            pass
    return detector

@st.cache_resource
def get_alert_manager():
    cooldown = float(os.getenv("ALERT_COOLDOWN_SECONDS", 60))
    return AlertManager(get_database(), cooldown_seconds=cooldown)

@st.cache_resource
def get_pipeline_subscriber():
    host = os.getenv("MQTT_BROKER_HOST", "")
    port = int(os.getenv("MQTT_PORT", 8883 if os.getenv("MQTT_USE_TLS", "false").lower() == "true" else 1883))
    use_tls = os.getenv("MQTT_USE_TLS", "false").lower() == "true"
    user = os.getenv("MQTT_USERNAME")
    pw = os.getenv("MQTT_PASSWORD")
    topic = os.getenv("MQTT_TOPIC", "battery/cells/data")

    sub = BatteryMQTTSubscriber(
        broker_host=host,
        port=port,
        use_tls=use_tls,
        username=user,
        password=pw,
        topic=topic,
        db=get_database(),
        alert_manager=get_alert_manager(),
        ml_detector=get_ml_detector()
    )
    if host:
        try:
            sub.start()
        except Exception:
            pass
    return sub

@st.cache_resource
def get_simulator():
    sim = BatterySimulator(pack_id="PACK-01", cell_count=4, interval_seconds=2.0)
    sub = get_pipeline_subscriber()
    sim.start(callback=sub.process_raw_message)
    return sim


# ==============================================================================
# AUTHENTICATION HANDLING
# ==============================================================================
db = get_database()
auth_mgr = get_auth_manager()
ml_detector = get_ml_detector()
pipeline_sub = get_pipeline_subscriber()
simulator = get_simulator()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

def render_login_page():
    st.markdown('<div class="main-header">🔋 Battery Cell Imbalance Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">IoT Analytics & Machine Learning Battery Management Platform</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.info("🔐 Please log in to access the battery monitoring telemetry.")
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="admin_demo_password")
            submit_btn = st.form_submit_button("Log In", use_container_width=True)

            if submit_btn:
                success, user_info = auth_mgr.authenticate(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.success("Authentication successful! Loading dashboard...")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Check .env or defaults.")

        st.caption("Default local credentials configured in `.env` (admin / admin_demo_password).")


def render_dashboard():
    user_info = st.session_state.user_info or {"username": "Guest", "role": "operator"}

    with st.sidebar:
        st.title("🔋 Battery Monitor")
        st.caption(f"Logged in as: **{user_info.get('username')}** ({user_info.get('role')})")

        page = st.radio(
            "Navigation",
            ["Overview & Live Analytics", "Historical Records & Export", "Alert Management", "AI/ML Diagnostics", "System Configuration"],
            index=0
        )

        st.markdown("---")
        st.subheader("Simulation Controls")
        active_scenario = st.selectbox(
            "Inject Scenario",
            ["normal", "imbalance", "overheating", "sensor_failure", "missing_data"],
            index=0
        )
        if st.button("Apply Scenario", use_container_width=True):
            simulator.set_scenario(active_scenario)
            st.success(f"Simulation scenario set to: **{active_scenario.upper()}**")

        col_sim_1, col_sim_2 = st.columns(2)
        with col_sim_1:
            if st.button("Pause Sim", use_container_width=True):
                simulator.pause()
                st.info("Simulation paused.")
        with col_sim_2:
            if st.button("Resume Sim", use_container_width=True):
                simulator.resume()
                st.success("Simulation resumed.")

        st.markdown("---")
        if st.button("Log Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.rerun()

    # 1. OVERVIEW & LIVE ANALYTICS
    if page == "Overview & Live Analytics":
        st.markdown('<div class="main-header">Battery Cell Imbalance Detection Using IoT Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Live Telemetry, Cell Balancing Metrics & Health Diagnostics</div>', unsafe_allow_html=True)

        bar_col1, bar_col2, bar_col3, bar_col4 = st.columns([1.5, 1.5, 1.5, 1.5])

        available_packs = db.get_available_packs()
        with bar_col1:
            selected_pack = st.selectbox("Battery Pack", available_packs, index=0)

        latest_reading = db.get_latest_reading(pack_id=selected_pack)

        with bar_col2:
            mode_val = latest_reading.get("mode", "simulation") if latest_reading else "simulation"
            st.markdown(f"<div style='margin-top: 1.8rem;'>{render_mode_pill(mode_val)}</div>", unsafe_allow_html=True)

        with bar_col3:
            status_val = latest_reading.get("rule_status", "NORMAL") if latest_reading else "NO_DATA"
            st.markdown(f"<div style='margin-top: 1.8rem;'>{render_status_pill(status_val)}</div>", unsafe_allow_html=True)

        with bar_col4:
            mqtt_status = pipeline_sub.manager.get_status()
            conn_text = "🟢 Connected" if mqtt_status["is_connected"] else "⚪ Offline / Sim"
            st.markdown(f"<div style='margin-top: 1.8rem; font-size: 0.85rem;'><b>MQTT Broker:</b> {conn_text}</div>", unsafe_allow_html=True)

        if latest_reading:
            is_stale, age_s = check_is_stale(latest_reading.get("timestamp_utc"), timeout_seconds=10.0)
            if is_stale:
                st.markdown(
                    f'<div class="stale-warning">⚠️ <b>Telemetry Stale Warning:</b> No new reading received in the last {age_s:.1f}s. Check MQTT connection or simulation worker.</div>',
                    unsafe_allow_html=True
                )

        if not latest_reading:
            st.info("ℹ️ No battery readings recorded yet in SQLite database. The simulator is generating readings...")
            if st.button("Generate Immediate Sample"):
                sample = simulator.generate_reading()
                pipeline_sub.process_raw_message(sample)
                st.rerun()
        else:
            st.markdown("---")

            # High-Level Metric Tiles
            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
            with m_col1:
                st.metric(
                    label="Voltage Spread (ΔV)",
                    value=f"{latest_reading.get('delta_v_mv', 0.0):.1f} mV",
                    delta=f"{latest_reading.get('delta_v', 0.0):.4f} V"
                )
            with m_col2:
                st.metric(
                    label="Min Cell Voltage",
                    value=f"{latest_reading.get('v_min', 0.0):.3f} V"
                )
            with m_col3:
                st.metric(
                    label="Max Cell Voltage",
                    value=f"{latest_reading.get('v_max', 0.0):.3f} V"
                )
            with m_col4:
                st.metric(
                    label="Pack Mean Voltage",
                    value=f"{latest_reading.get('mean_v', 0.0):.3f} V"
                )
            with m_col5:
                st.metric(
                    label="Peak Temperature",
                    value=f"{latest_reading.get('t_max', 0.0):.1f} °C",
                    delta=f"Spread: {latest_reading.get('delta_t', 0.0):.1f} °C"
                )

            # Live Charts Section
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                v_fig = create_cell_voltage_chart(
                    latest_reading.get("cell_voltages", []),
                    latest_reading.get("v_min", 3.7),
                    latest_reading.get("v_max", 3.7)
                )
                st.plotly_chart(v_fig, use_container_width=True)

            with chart_col2:
                t_fig = create_temperature_chart(latest_reading.get("cell_temperatures", []))
                st.plotly_chart(t_fig, use_container_width=True)

            # Historical Spread Chart & Trend
            historical = db.get_historical_readings(pack_id=selected_pack, limit=50)
            if historical:
                hist_df = pd.DataFrame(historical)
                spread_fig = create_voltage_spread_history_chart(hist_df, warn_thresh_mv=20.0, crit_thresh_mv=50.0)
                st.plotly_chart(spread_fig, use_container_width=True)

                trend_fig = create_multi_cell_history_chart(historical)
                st.plotly_chart(trend_fig, use_container_width=True)

            # Cell Comparison Table
            st.subheader("Cell Comparison & Sanity Matrix")
            c_voltages = latest_reading.get("cell_voltages", [])
            c_temps = latest_reading.get("cell_temperatures", [])
            v_mean = latest_reading.get("mean_v", 3.7)

            matrix_data = []
            for idx in range(len(c_voltages)):
                v_val = c_voltages[idx]
                t_val = c_temps[idx] if idx < len(c_temps) else None
                deviation_mv = round((v_val - v_mean) * 1000.0, 2) if v_val is not None else 0.0

                health = "Nominal"
                if v_val is None:
                    health = "Sensor Missing"
                elif abs(deviation_mv) >= 50.0:
                    health = "Critical Deviation"
                elif abs(deviation_mv) >= 20.0:
                    health = "Warning Imbalance"

                matrix_data.append({
                    "Cell": f"Cell {idx+1}",
                    "Voltage (V)": v_val,
                    "Deviation from Mean (mV)": deviation_mv,
                    "Temperature (°C)": t_val,
                    "Condition": health
                })

            st.dataframe(pd.DataFrame(matrix_data), use_container_width=True)

            if st.button("🔄 Refresh Live Telemetry"):
                st.rerun()

    # 2. HISTORICAL RECORDS & EXPORT
    elif page == "Historical Records & Export":
        st.markdown('<div class="main-header">Historical Battery Telemetry</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Query SQLite persistent records and export CSV reports</div>', unsafe_allow_html=True)

        history = db.get_historical_readings(limit=200)
        if not history:
            st.info("No historical readings found in SQLite database.")
        else:
            st.write(f"Showing last **{len(history)}** telemetry cycles.")

            if st.button("💾 Generate & Export Full Historical CSV"):
                success, msg = db.export_readings_to_csv()
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

            csv_file_path = "exports/historical_readings.csv"
            if os.path.exists(csv_file_path):
                with open(csv_file_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Historical CSV File",
                        data=f,
                        file_name="battery_historical_telemetry.csv",
                        mime="text/csv"
                    )

            table_rows = []
            for r in history:
                table_rows.append({
                    "ID": r["id"],
                    "Timestamp (UTC)": r["timestamp_utc"],
                    "Pack": r["pack_id"],
                    "Mode": r["mode"],
                    "ΔV (mV)": r["delta_v_mv"],
                    "V_min (V)": r["v_min"],
                    "V_max (V)": r["v_max"],
                    "T_max (°C)": r["t_max"],
                    "Rule Status": r["rule_status"],
                    "ML Status": "Outlier" if r.get("ml_prediction") == -1 else "Inlier"
                })
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

    # 3. ALERT MANAGEMENT
    elif page == "Alert Management":
        st.markdown('<div class="main-header">Battery Alarm & Event Management</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Active warnings, critical events, and operator acknowledgements</div>', unsafe_allow_html=True)

        unack_only = st.checkbox("Show Unacknowledged Alerts Only", value=False)
        alerts = db.get_recent_alerts(limit=50, unack_only=unack_only)

        if not alerts:
            st.success("✅ No active alert events logged.")
        else:
            st.write(f"Displaying **{len(alerts)}** alert records:")
            for a in alerts:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <b>{render_status_pill(a['alert_level'])}</b> &nbsp; 
                                <b>Pack:</b> {a['pack_id']} &nbsp;|&nbsp; 
                                <b>Time:</b> {a['timestamp_utc']}
                            </div>
                            <div>
                                <b>Status:</b> {'✅ Acknowledged' if a['acknowledged'] else '⚠️ Unacknowledged'}
                            </div>
                        </div>
                        <div style="margin-top: 8px; color: #334155;">
                            <b>Reason:</b> {a['reason']} <br/>
                            <b>Voltage Spread:</b> {a.get('delta_v_mv', 'N/A')} mV &nbsp;|&nbsp; 
                            <b>Max Temp:</b> {a.get('max_temp', 'N/A')} °C &nbsp;|&nbsp; 
                            <b>Affected Cells:</b> {a.get('affected_cells', [])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if not a["acknowledged"]:
                        if st.button(f"Acknowledge Alert #{a['id']}", key=f"ack_{a['id']}"):
                            db.acknowledge_alert(a["id"], acknowledged_by=user_info.get("username", "operator"))
                            st.success(f"Alert #{a['id']} acknowledged.")
                            st.rerun()

    # 4. AI/ML DIAGNOSTICS
    elif page == "AI/ML Diagnostics":
        st.markdown('<div class="main-header">AI/ML Anomaly Detection Pipeline</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Unsupervised Isolation Forest model training, inference, and metrics</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.subheader("Model Status")
            if ml_detector.is_loaded:
                st.success("🟢 Isolation Forest Model is loaded and active for real-time inference.")
            else:
                st.warning("⚠️ ML Model is not yet trained or loaded. Rule-based detection is active as fallback.")

            st.markdown(r"""
            **Pipeline Specification:**
            - **Algorithm:** Isolation Forest (`sklearn.ensemble.IsolationForest`)
            - **Key Features:** Voltage Spread ($\Delta V_{mV}$), $V_{max}$, $V_{min}$, $V_{mean}$, Peak Temp ($T_{max}$), Thermal Gradient ($\Delta T$), Pack Current ($I$)
            - **Contamination Factor:** 0.05
            - **Preprocessing:** Standard Normalization (`StandardScaler`)
            """)

        with col2:
            st.subheader("Model Retraining")
            n_samples = st.slider("Dataset Samples", min_value=1000, max_value=10000, value=4000, step=500)
            anomaly_ratio = st.slider("Synthetic Anomaly Ratio", min_value=0.02, max_value=0.20, value=0.08, step=0.01)

            if st.button("🚀 Train & Evaluate New Model"):
                with st.spinner("Generating dataset and training Isolation Forest..."):
                    metrics = ml_detector.train()
                    st.success("Model trained successfully!")
                    st.json(metrics)

        st.markdown("---")
        st.subheader("Live Inference Sample")
        latest = db.get_latest_reading()
        if latest:
            feat = {
                "delta_v_mv": latest.get("delta_v_mv", 0.0),
                "v_max": latest.get("v_max", 3.7),
                "v_min": latest.get("v_min", 3.7),
                "mean_v": latest.get("mean_v", 3.7),
                "t_max": latest.get("t_max", 28.0),
                "delta_t": latest.get("delta_t", 0.0),
                "current_a": latest.get("current_a", 0.0)
            }
            res = ml_detector.predict(feat)
            st.write("**Extracted Features from Latest Telemetry:**", feat)
            st.write("**Inference Output:**", res)

    # 5. SYSTEM CONFIGURATION
    elif page == "System Configuration":
        st.markdown('<div class="main-header">System Configuration & Thresholds</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Tune battery safety thresholds, MQTT settings, and operational limits</div>', unsafe_allow_html=True)

        thresholds = load_thresholds()

        with st.form("thresholds_form"):
            st.subheader("Voltage Imbalance Thresholds")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                warn_v = st.number_input(
                    "Warning Spread (V)",
                    min_value=0.005,
                    max_value=0.100,
                    value=float(thresholds.get("voltage_spread", {}).get("warning_v", 0.020)),
                    step=0.005,
                    format="%.3f"
                )
            with col_t2:
                crit_v = st.number_input(
                    "Critical Spread (V)",
                    min_value=0.010,
                    max_value=0.200,
                    value=float(thresholds.get("voltage_spread", {}).get("critical_v", 0.050)),
                    step=0.005,
                    format="%.3f"
                )

            st.subheader("Thermal Thresholds (°C)")
            col_t3, col_t4 = st.columns(2)
            with col_t3:
                warn_t = st.number_input(
                    "Warning Temp (°C)",
                    min_value=30.0,
                    max_value=80.0,
                    value=float(thresholds.get("temperature", {}).get("warning_high_c", 45.0)),
                    step=1.0
                )
            with col_t4:
                crit_t = st.number_input(
                    "Critical Temp (°C)",
                    min_value=40.0,
                    max_value=100.0,
                    value=float(thresholds.get("temperature", {}).get("critical_high_c", 60.0)),
                    step=1.0
                )

            save_btn = st.form_submit_button("Save Thresholds to YAML", use_container_width=True)
            if save_btn:
                import yaml
                thresholds["voltage_spread"]["warning_v"] = warn_v
                thresholds["voltage_spread"]["critical_v"] = crit_v
                thresholds["temperature"]["warning_high_c"] = warn_t
                thresholds["temperature"]["critical_high_c"] = crit_t

                with open("config/thresholds.yaml", "w", encoding="utf-8") as f:
                    yaml.dump(thresholds, f, default_flow_style=False)
                st.success("✅ Threshold configuration saved to `config/thresholds.yaml`!")


# ==============================================================================
# MAIN APPLICATION CONTROLLER
# ==============================================================================
if not st.session_state.authenticated:
    render_login_page()
else:
    render_dashboard()
