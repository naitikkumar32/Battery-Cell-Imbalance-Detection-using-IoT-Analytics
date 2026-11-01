@echo off
setlocal enabledelayedexpansion

title Battery Cell Imbalance Detection - IoT Analytics Platform

echo ===============================================================================
echo   BATTERY CELL IMBALANCE DETECTION USING IOT ANALYTICS
echo   Full-Stack IoT ^& Machine Learning Battery Management System
echo ===============================================================================
echo.

REM 1. Set directory to script root
cd /d "%~dp0"
echo [*] Working Directory: %CD%

REM 2. Check for .venv virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .venv\
    echo Please create the virtual environment using:
    echo     py -m venv .venv
    echo     .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM 3. Verify Python version in .venv
echo [*] Checking Python runtime in .venv...
.\.venv\Scripts\python.exe -c "import sys; print('    Python version:', sys.version.split()[0])"
if %errorlevel% neq 0 (
    echo [ERROR] Virtual environment python.exe failed to execute.
    pause
    exit /b 1
)

REM 4. Ensure .env file exists (copy template if absent)
if not exist ".env" (
    echo [*] .env not found. Creating default .env from .env.example...
    copy .env.example .env >nul
    echo [OK] Default .env created.
)

REM 5. Initialize SQLite Database & Tables if not present
if not exist "data\battery.db" (
    echo [*] Database not detected. Initializing SQLite tables and default admin...
    .\.venv\Scripts\python.exe scripts\init_database.py
    if %errorlevel% neq 0 (
        echo [ERROR] Database initialization failed.
        pause
        exit /b 1
    )
) else (
    echo [OK] SQLite database verified (data\battery.db).
)

REM 6. Verify pre-trained ML model exists
if not exist "models\isolation_forest_model.joblib" (
    echo [*] Machine learning model not found. Training initial Isolation Forest...
    .\.venv\Scripts\python.exe scripts\train_model.py
    if %errorlevel% neq 0 (
        echo [WARNING] Model auto-training encountered an issue. Rule-based fallback active.
    )
) else (
    echo [OK] AI/ML Isolation Forest model verified.
)

REM 7. Launch Streamlit Application
echo.
echo ===============================================================================
echo   STARTING STREAMLIT DASHBOARD...
echo   URL: http://localhost:8501
echo   Default Credentials: admin / admin_demo_password
echo   Press Ctrl+C in this console to stop the server safely.
echo ===============================================================================
echo.

.\.venv\Scripts\streamlit.exe run app.py --server.port 8501 --server.headless false

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Streamlit exited with an error code: %errorlevel%
    pause
)

endlocal
