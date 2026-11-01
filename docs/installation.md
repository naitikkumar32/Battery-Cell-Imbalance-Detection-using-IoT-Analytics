# Installation & Setup Guide

## 1. System Requirements
- **Operating System:** Windows 10/11 (or Linux/macOS)
- **Python Version:** Python 3.10 to Python 3.14 (Verified and fully functional on Python 3.14.7)
- **Disk Space:** ~500 MB free space
- **Optional Tools:** Arduino IDE 2.x (for ESP32 flashing), Node.js & Node-RED (for Flow automation)

---

## 2. Step-by-Step Installation

### Step 1: Open PowerShell or Command Prompt
Navigate to the project root directory:
```powershell
cd "C:\Users\jatin\OneDrive\Documents\Desktop\HCL Battery cell imbalence detection"
```

### Step 2: Create Python Virtual Environment (`.venv`)
```powershell
py -m venv .venv
```

### Step 3: Activate Virtual Environment
On Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell restricts execution scripts, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

Or on Windows CMD:
```cmd
.\.venv\Scripts\activate.bat
```

### Step 4: Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables
Copy the template configuration file:
```powershell
copy .env.example .env
```
Open `.env` in any text editor and adjust variables as required. (The defaults work immediately out-of-the-box for simulation mode without needing any external cloud credentials).

### Step 6: Initialize Database and Pre-train ML Model
Run the setup helper scripts:
```powershell
python scripts/init_database.py
python scripts/generate_dataset.py
python scripts/train_model.py
```

### Step 7: Verify Everything
```powershell
python scripts/verify_setup.py
```
Ensure all items report `[PASS]`.

---

## 3. Running Automated Tests
To run the automated test suite:
```powershell
pytest -v
```
All 28 unit and integration tests should pass cleanly.

---

## 4. HiveMQ Cloud Configuration (Optional)
To connect real hardware or cloud simulation to HiveMQ Cloud:
1. Sign up for a free serverless cluster at [https://www.hivemq.com/cloud/](https://www.hivemq.com/cloud/).
2. Under **Overview**, copy your Cluster URL (e.g., `xxxx.s1.eu.hivemq.cloud`).
3. Under **Access Management**, create MQTT credentials (Username and Password).
4. Update your local `.env` file:
   ```env
   MQTT_BROKER_HOST=xxxx.s1.eu.hivemq.cloud
   MQTT_PORT=8883
   MQTT_USE_TLS=true
   MQTT_USERNAME=your_username
   MQTT_PASSWORD=your_password
   MQTT_TOPIC=battery/cells/data
   ```
5. Restart the dashboard or publisher. The connection indicator will turn green: `🟢 Connected`.
