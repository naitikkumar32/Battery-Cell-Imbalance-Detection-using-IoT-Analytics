"""
Tests: test_database.py
Validates SQLite database initialization, insertion, querying, export, and backup.
"""

import os
import gc
import tempfile
import pytest
from src.database import BatteryDatabase


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = BatteryDatabase(db_path=path)
    yield db
    del db
    gc.collect()
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def test_db_initialization(temp_db):
    # Verify tables created
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        assert "battery_readings" in tables
        assert "alerts" in tables
        assert "users" in tables


def test_insert_and_retrieve_reading(temp_db):
    record = {
        "pack_id": "TEST-PACK",
        "timestamp_utc": "2026-10-29T15:00:00+00:00",
        "timestamp_epoch": 1793286000.0,
        "mode": "simulation",
        "source": "unit_test",
        "cell_count": 4,
        "cell_voltages": [3.80, 3.82, 3.81, 3.83],
        "cell_temperatures": [28.0, 28.5, 28.2, 28.1],
        "current_a": 1.5,
        "v_max": 3.83,
        "v_min": 3.80,
        "delta_v": 0.03,
        "delta_v_mv": 30.0,
        "mean_v": 3.815,
        "t_max": 28.5,
        "t_min": 28.0,
        "delta_t": 0.5,
        "mean_t": 28.2,
        "rule_status": "WARNING",
        "rule_reasons": ["Spread exceeds 0.020V"],
        "ml_prediction": 1,
        "ml_anomaly_score": 0.12,
        "data_quality": "HEALTHY"
    }

    row_id = temp_db.insert_reading(record)
    assert row_id > 0

    latest = temp_db.get_latest_reading(pack_id="TEST-PACK")
    assert latest is not None
    assert latest["pack_id"] == "TEST-PACK"
    assert latest["delta_v_mv"] == 30.0
    assert len(latest["cell_voltages"]) == 4


def test_empty_database_safety(temp_db):
    latest = temp_db.get_latest_reading(pack_id="NON_EXISTENT")
    assert latest is None

    history = temp_db.get_historical_readings(pack_id="NON_EXISTENT")
    assert history == []


def test_csv_export(temp_db, tmp_path):
    record = {
        "pack_id": "TEST-PACK",
        "cell_voltages": [3.8, 3.81],
        "cell_temperatures": [28.0, 28.0],
        "delta_v_mv": 10.0,
        "rule_status": "NORMAL"
    }
    temp_db.insert_reading(record)

    export_file = str(tmp_path / "test_export.csv")
    success, msg = temp_db.export_readings_to_csv(export_file)
    assert success is True
    assert os.path.exists(export_file)


def test_database_backup(temp_db, tmp_path):
    backup_folder = str(tmp_path / "backups")
    success, path = temp_db.backup_database(backup_folder)
    assert success is True
    assert os.path.exists(path)
