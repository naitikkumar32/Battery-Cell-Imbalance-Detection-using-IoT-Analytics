# System Shutdown and Process Termination Instructions

## 1. Stopping the Streamlit Dashboard
If you started the application via `run_project.bat` or the terminal command:
1. Navigate to the terminal or command prompt window running the server.
2. Press **`Ctrl + C`** on your keyboard.
3. When prompted `Terminate batch job (Y/N)?`, type **`Y`** and press **Enter**.
4. The Streamlit web server and internal simulation threads will terminate gracefully.

---

## 2. Stopping Background / Orphaned Processes (PowerShell / Windows CMD)
If a process remains active in the background or port 8501 is busy:

### Option A: Check and kill via PowerShell
```powershell
# Find Python processes running Streamlit
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, MainWindowTitle

# Terminate running Python processes associated with the project
Stop-Process -Name python -Force
```

### Option B: Check by Port (Port 8501)
```powershell
# Identify process listening on Streamlit port 8501
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | Select-Object OwningProcess

# Terminate that specific PID (replace <PID> with the number)
Stop-Process -Id <PID> -Force
```

---

## 3. Stopping Node-RED (If Running)
In the command window where `node-red` was executed, press **`Ctrl + C`**.

---

## 4. Resetting Database or Clearing Telemetry
If you wish to reset historical data for a clean demonstration:
1. Stop the application.
2. Delete or archive `data/battery.db`.
3. Run `.\.venv\Scripts\python.exe scripts/init_database.py` to recreate a fresh database schema.
