"""
Tests: test_detection.py
Validates rule-based status hierarchy and safety threshold evaluation.
"""

import pytest
from src.calculations import calculate_voltage_metrics, calculate_temperature_metrics
from src.detection import evaluate_pack_status

THRESHOLDS = {
    "voltage_spread": {
        "critical_v": 0.050,
        "warning_v": 0.020
    },
    "cell_voltage_limits": {
        "critical_high_v": 4.25,
        "warning_high_v": 4.22,
        "warning_low_v": 3.20,
        "critical_low_v": 3.00
    },
    "temperature": {
        "critical_high_c": 60.0,
        "warning_high_c": 45.0,
        "spread_critical_c": 10.0,
        "spread_warning_c": 5.0
    }
}


def test_normal_status():
    # Tightly balanced: 3.80, 3.81, 3.805, 3.81 (spread = 0.010V < 0.020V)
    cells = [3.800, 3.810, 3.805, 3.810]
    temps = [28.0, 28.5, 28.2, 28.4]
    v_m = calculate_voltage_metrics(cells)
    t_m = calculate_temperature_metrics(temps)

    res = evaluate_pack_status(v_m, t_m, cells, temps, thresholds=THRESHOLDS)
    assert res["status"] == "NORMAL"
    assert len(res["affected_cells"]) == 0


def test_warning_status():
    # Warning spread: 3.800 and 3.825 -> spread = 0.025V (>= 0.020V and < 0.050V)
    cells = [3.800, 3.825, 3.810, 3.815]
    temps = [28.0, 28.5, 28.2, 28.4]
    v_m = calculate_voltage_metrics(cells)
    t_m = calculate_temperature_metrics(temps)

    res = evaluate_pack_status(v_m, t_m, cells, temps, thresholds=THRESHOLDS)
    assert res["status"] == "WARNING"
    assert any("spread is 0.0250V" in r for r in res["reasons"])


def test_critical_status():
    # Critical spread: 3.750 and 3.810 -> spread = 0.060V (>= 0.050V)
    cells = [3.750, 3.810, 3.800, 3.805]
    temps = [28.0, 28.5, 28.2, 28.4]
    v_m = calculate_voltage_metrics(cells)
    t_m = calculate_temperature_metrics(temps)

    res = evaluate_pack_status(v_m, t_m, cells, temps, thresholds=THRESHOLDS)
    assert res["status"] == "CRITICAL"
    assert any("Critical voltage imbalance" in r for r in res["reasons"])


def test_critical_takes_precedence_over_warning():
    # Condition: warning spread (0.030V), BUT critical cell over-voltage (4.26V)
    cells = [4.260, 4.230, 4.240, 4.235]
    temps = [28.0, 28.0, 28.0, 28.0]
    v_m = calculate_voltage_metrics(cells)
    t_m = calculate_temperature_metrics(temps)

    res = evaluate_pack_status(v_m, t_m, cells, temps, thresholds=THRESHOLDS)
    # Must be CRITICAL, NOT WARNING
    assert res["status"] == "CRITICAL"
    assert any("critical over-voltage" in r for r in res["reasons"])


def test_missing_data_not_healthy():
    # Telemetry has missing cells
    cells = [3.8, None, 3.8]
    temps = [28.0, 28.0, 28.0]
    v_m = calculate_voltage_metrics(cells)
    t_m = calculate_temperature_metrics(temps)

    res = evaluate_pack_status(v_m, t_m, cells, temps, thresholds=THRESHOLDS)
    # Must never be NORMAL
    assert res["status"] == "SENSOR_FAULT"
