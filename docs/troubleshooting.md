# Troubleshooting & Common Issues Guide

## 1. Port 8501 Already in Use
**Symptom:** Streamlit displays `Port 8501 is already in use` or fails to bind.  
**Resolution:**
Run the following in PowerShell to terminate existing Python processes:
```powershell
Stop-Process -Name python -Force
```
Or start Streamlit on an alternate port:
```powershell
.\.venv\Scripts\streamlit.exe run app.py --server.port 8502
```

---

## 2. Telemetry Stale Warning on Dashboard
**Symptom:** Yellow banner appears: `⚠️ Telemetry Stale Warning: No new reading received in the last Xs`.  
**Causes & Resolutions:**
1. **Simulation was paused:** Click **Resume Sim** in the sidebar.
2. **Database write failure:** Verify that `data/battery.db` is not locked by an external database browser (like DB Browser for SQLite). Close external locks.
3. **No broker connection in Hardware Mode:** If configured for `hardware` mode, ensure the ESP32 is powered on and publishing to the designated MQTT topic.

---

## 3. HiveMQ Cloud Connection Fails (`[FAILED] rc=5` or SSL Handshake Error)
**Symptom:** MQTT client cannot connect to broker.  
**Causes & Resolutions:**
1. **Port mismatch:** HiveMQ Cloud requires port **8883** with TLS enabled (`MQTT_USE_TLS=true`). Plaintext port 1883 will be rejected.
2. **Invalid credentials:** Verify your HiveMQ Cloud username and password in `.env` (note: this is distinct from your HiveMQ website login).
3. **Cluster Hostname:** Ensure the hostname ends in `.hivemq.cloud` and contains no leading `http://` or `mqtt://`.

---

## 4. SQLite "Database is Locked" Error (`OperationalError`)
**Symptom:** `sqlite3.OperationalError: database is locked`.  
**Resolution:**
The system uses WAL mode (`PRAGMA journal_mode=WAL`) and a 10-second busy timeout. If a lock occurs during heavy concurrent access:
1. Ensure no external SQLite inspection GUI is holding an open uncommitted write transaction.
2. Restart the application using `run_project.bat`.

---

## 5. Machine Learning "Model Not Loaded" Status
**Symptom:** Diagnostics page shows rule-based fallback active.  
**Resolution:**
Generate the training dataset and train the Isolation Forest model using the provided script:
```powershell
.\.venv\Scripts\python.exe scripts/train_model.py
```
This saves `models/isolation_forest_model.joblib` and `models/scaler.joblib`.
