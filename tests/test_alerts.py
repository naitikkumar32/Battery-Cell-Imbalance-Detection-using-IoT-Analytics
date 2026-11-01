"""
Tests: test_alerts.py
Validates alert generation, cooldown mechanics, escalation, and acknowledgement.
"""

import os
import gc
import tempfile
import pytest
from src.database import BatteryDatabase
from src.alerts import AlertManager


@pytest.fixture
def alert_setup():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = BatteryDatabase(db_path=path)
    mgr = AlertManager(db=db, cooldown_seconds=5.0)
    yield db, mgr
    del mgr
    del db
    gc.collect()
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def test_normal_reading_no_alert(alert_setup):
    db, mgr = alert_setup
    reading = {
        "pack_id": "PACK-01",
        "rule_status": "NORMAL",
        "delta_v_mv": 12.0
    }
    alert = mgr.process_reading(reading)
    assert alert is None
    assert len(db.get_recent_alerts()) == 0


def test_warning_reading_triggers_alert(alert_setup):
    db, mgr = alert_setup
    reading = {
        "pack_id": "PACK-01",
        "rule_status": "WARNING",
        "rule_reasons": ["Voltage spread 25mV exceeds warning threshold."],
        "delta_v_mv": 25.0,
        "t_max": 29.0,
        "affected_cells": [1, 2]
    }
    alert = mgr.process_reading(reading)
    assert alert is not None
    assert alert["status"] == "WARNING"

    alerts_in_db = db.get_recent_alerts()
    assert len(alerts_in_db) == 1
    assert alerts_in_db[0]["pack_id"] == "PACK-01"


def test_cooldown_suppresses_repeat_alerts(alert_setup):
    db, mgr = alert_setup
    reading = {
        "pack_id": "PACK-01",
        "rule_status": "WARNING",
        "rule_reasons": ["Imbalance"],
        "delta_v_mv": 25.0
    }

    # First alert succeeds
    first = mgr.process_reading(reading)
    assert first is not None

    # Immediate second reading with same status should be suppressed by cooldown
    second = mgr.process_reading(reading)
    assert second is None
    assert len(db.get_recent_alerts()) == 1


def test_escalation_bypasses_cooldown(alert_setup):
    db, mgr = alert_setup
    warn_reading = {
        "pack_id": "PACK-01",
        "rule_status": "WARNING",
        "rule_reasons": ["Developing imbalance"],
        "delta_v_mv": 25.0
    }
    mgr.process_reading(warn_reading)

    # Escalation to CRITICAL immediately bypasses cooldown
    crit_reading = {
        "pack_id": "PACK-01",
        "rule_status": "CRITICAL",
        "rule_reasons": ["Critical cell divergence 65mV"],
        "delta_v_mv": 65.0
    }
    escalated = mgr.process_reading(crit_reading)
    assert escalated is not None
    assert escalated["status"] == "CRITICAL"
    assert len(db.get_recent_alerts()) == 2


def test_alert_acknowledgement(alert_setup):
    db, mgr = alert_setup
    reading = {
        "pack_id": "PACK-01",
        "rule_status": "WARNING",
        "rule_reasons": ["Alert"],
        "delta_v_mv": 25.0
    }
    alert = mgr.process_reading(reading)
    alert_id = alert["alert_id"]

    # Verify unacknowledged
    unack = db.get_recent_alerts(unack_only=True)
    assert len(unack) == 1

    # Acknowledge
    success = db.acknowledge_alert(alert_id, acknowledged_by="test_engineer")
    assert success is True

    # Verify no unacknowledged remain
    unack_after = db.get_recent_alerts(unack_only=True)
    assert len(unack_after) == 0
