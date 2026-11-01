"""
Tests: test_calculations.py
Validates battery metric mathematics, mV conversion, and edge case safety.
"""

import math
import pytest
from src.calculations import (
    calculate_voltage_metrics,
    calculate_temperature_metrics,
    calculate_rate_of_change,
    assess_sensor_quality
)


def test_voltage_spread_calculation():
    # Test 4S pack: 3.80V, 3.82V, 3.85V, 3.81V
    voltages = [3.80, 3.82, 3.85, 3.81]
    res = calculate_voltage_metrics(voltages)

    assert res["is_valid"] is True
    assert res["v_max"] == 3.85
    assert res["v_min"] == 3.80
    assert pytest.approx(res["delta_v"], 0.0001) == 0.05
    # Millivolt conversion check: 0.05 V = 50.0 mV
    assert pytest.approx(res["delta_v_mv"], 0.01) == 50.0
    assert pytest.approx(res["mean_v"], 0.001) == 3.82


def test_empty_and_null_voltages():
    # Empty list
    res_empty = calculate_voltage_metrics([])
    assert res_empty["is_valid"] is False
    assert res_empty["delta_v"] is None

    # List with None
    res_null = calculate_voltage_metrics([3.8, None, 3.9])
    assert res_null["is_valid"] is False

    # List with NaN
    res_nan = calculate_voltage_metrics([3.8, float("nan"), 3.9])
    assert res_nan["is_valid"] is False


def test_temperature_metrics():
    temps = [28.5, 29.0, 32.1, 28.8]
    res = calculate_temperature_metrics(temps)

    assert res["is_valid"] is True
    assert res["t_max"] == 32.1
    assert res["t_min"] == 28.5
    assert pytest.approx(res["delta_t"], 0.01) == 3.6
    assert pytest.approx(res["mean_t"], 0.01) == 29.6


def test_rate_of_change():
    v1, t1 = 3.85, 100.0
    v2, t2 = 3.81, 102.0
    # dv/dt = (3.81 - 3.85) / 2.0 = -0.02 V/s
    roc = calculate_rate_of_change(v2, v1, t2, t1)
    assert pytest.approx(roc, 0.0001) == -0.02


def test_sensor_quality_assessment():
    # Healthy sensors
    healthy, issues = assess_sensor_quality([3.8, 3.82, 3.81, 3.83], [28.0, 29.0, 28.5, 29.2])
    assert healthy is True
    assert len(issues) == 0

    # Unrealistic ADC voltage (0.1V - below physical 0.5V)
    faulty, issues = assess_sensor_quality([0.1, 3.82, 3.81, 3.83], [28.0, 29.0, 28.5, 29.2])
    assert faulty is False
    assert any("below physical limit" in i for i in issues)
