"""
Script: verify_setup.py
Verifies complete project environment, dependencies, configuration files,
database connectivity, and ML model status.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def check_module(name: str):
    try:
        __import__(name)
        print(f"  [PASS] Library: {name}")
        return True
    except ImportError as e:
        print(f"  [FAIL] Library: {name} ({str(e)})")
        return False


def main():
    print("=" * 60)
    print("Verifying Project Environment & Components...")
    print("=" * 60)

    # 1. Check Python Version
    print(f"Python Version: {sys.version.split()[0]}")

    # 2. Check Core Dependencies
    deps = [
        "numpy", "pandas", "scipy", "sklearn", "streamlit",
        "paho.mqtt", "yaml", "pytest", "bcrypt", "dotenv", "plotly"
    ]
    print("\nChecking Dependencies:")
    all_deps_ok = all([check_module(d) for d in deps])

    # 3. Check Configurations
    print("\nChecking Configurations:")
    configs = [
        "config/settings.yaml",
        "config/thresholds.yaml",
        ".env.example"
    ]
    for c in configs:
        if os.path.exists(c):
            print(f"  [PASS] Config file: {c}")
        else:
            print(f"  [FAIL] Missing config file: {c}")

    # 4. Check Database
    print("\nChecking SQLite Database:")
    try:
        from src.database import BatteryDatabase
        db = BatteryDatabase()
        packs = db.get_available_packs()
        print(f"  [PASS] SQLite initialized successfully. Available packs: {packs}")
    except Exception as e:
        print(f"  [FAIL] Database initialization failed: {e}")

    # 5. Check ML Model
    print("\nChecking AI/ML Model:")
    try:
        from src.ml_pipeline import AnomalyDetector
        det = AnomalyDetector()
        if det.is_loaded:
            print(f"  [PASS] Pre-trained Isolation Forest model loaded.")
        else:
            print(f"  [INFO] Pre-trained model not found. Can be generated via scripts/train_model.py.")
    except Exception as e:
        print(f"  [FAIL] ML loader error: {e}")

    print("=" * 60)
    if all_deps_ok:
        print("Verification complete: System is READY.\n")
    else:
        print("Verification failed: Please install missing dependencies.\n")


if __name__ == "__main__":
    main()
