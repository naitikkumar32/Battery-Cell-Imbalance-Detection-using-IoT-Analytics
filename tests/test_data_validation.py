"""
Tests: test_data_validation.py
Validates telemetry JSON schema decoding, validation, and error trapping.
"""

import json
from src.data_validator import validate_battery_payload


def test_valid_json_payload():
    payload = {
        "pack_id": "PACK-01",
        "timestamp": "2026-10-29T15:00:00Z",
        "mode": "simulation",
        "cell_voltages": [3.81, 3.82, 3.80, 3.81],
        "cell_temperatures": [28.0, 28.2, 28.1, 28.0],
        "current_a": 2.1
    }
    is_valid, sanitized, errors = validate_battery_payload(json.dumps(payload))
    assert is_valid is True
    assert sanitized["pack_id"] == "PACK-01"
    assert len(sanitized["cell_voltages"]) == 4
    assert sanitized["current_a"] == 2.1
    assert len(errors) == 0


def test_missing_pack_id():
    payload = {
        "cell_voltages": [3.81, 3.82],
        "cell_temperatures": [28.0, 28.2]
    }
    is_valid, sanitized, errors = validate_battery_payload(payload)
    assert is_valid is False
    assert any("pack_id" in err for err in errors)


def test_malformed_json_string():
    raw_str = '{"pack_id": "PACK-01", cell_voltages: invalid json'
    is_valid, sanitized, errors = validate_battery_payload(raw_str)
    assert is_valid is False
    assert any("JSON decoding error" in err for err in errors)


def test_empty_cell_list():
    payload = {
        "pack_id": "PACK-01",
        "cell_voltages": [],
        "cell_temperatures": []
    }
    is_valid, sanitized, errors = validate_battery_payload(payload)
    assert is_valid is False
    assert any("cannot be empty" in err for err in errors)


def test_hardware_mode_parsing():
    payload = {
        "pack_id": "ESP32-PACK-01",
        "mode": "hardware",
        "cell_voltages": [3.79, 3.80, 3.81, 3.80],
        "cell_temperatures": [29.1, 29.0, 29.2, 29.0]
    }
    is_valid, sanitized, errors = validate_battery_payload(payload)
    assert is_valid is True
    assert sanitized["mode"] == "hardware"
    assert sanitized["source"] == "esp32"
