"""
Module: data_validator.py
Validates and sanitizes inbound telemetry payloads from both simulation and hardware sources.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List


def parse_iso_timestamp(ts_val: Any) -> Tuple[Optional[str], Optional[float]]:
    """
    Parses a timestamp value (ISO string or unix epoch float) and returns
    a standardized UTC ISO string and epoch seconds.
    """
    if ts_val is None:
        now = datetime.now(timezone.utc)
        return now.isoformat(), now.timestamp()

    if isinstance(ts_val, (int, float)):
        try:
            dt = datetime.fromtimestamp(ts_val, tz=timezone.utc)
            return dt.isoformat(), float(ts_val)
        except Exception:
            pass

    if isinstance(ts_val, str):
        try:
            # Handle ISO formats like 2026-10-29T15:00:00Z
            clean_ts = ts_val.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat(), dt.timestamp()
        except Exception:
            pass

    now = datetime.now(timezone.utc)
    return now.isoformat(), now.timestamp()


def validate_battery_payload(raw_payload: Any) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
    """
    Validates a raw payload (JSON string or dict) received from MQTT or an API.

    Returns:
      (is_valid: bool, validated_dict: Optional[dict], error_messages: List[str])
    """
    errors: List[str] = []

    if isinstance(raw_payload, (bytes, bytearray)):
        try:
            raw_payload = raw_payload.decode("utf-8")
        except UnicodeDecodeError:
            return False, None, ["Payload is not valid UTF-8 string."]

    if isinstance(raw_payload, str):
        try:
            data = json.loads(raw_payload)
        except json.JSONDecodeError as e:
            return False, None, [f"JSON decoding error: {str(e)}"]
    elif isinstance(raw_payload, dict):
        data = raw_payload
    else:
        return False, None, ["Payload must be a JSON string or Python dictionary."]

    # 1. Check pack_id
    pack_id = data.get("pack_id")
    if not pack_id or not isinstance(pack_id, str):
        errors.append("Field 'pack_id' is missing or not a non-empty string.")
    else:
        pack_id = pack_id.strip()

    # 2. Check timestamp
    ts_iso, ts_epoch = parse_iso_timestamp(data.get("timestamp"))

    # 3. Check mode
    mode = data.get("mode", "simulation").lower()
    if mode not in ("simulation", "hardware"):
        mode = "simulation"

    # 4. Check cell_voltages
    raw_voltages = data.get("cell_voltages")
    validated_voltages: List[float] = []
    if raw_voltages is None:
        errors.append("Field 'cell_voltages' is missing.")
    elif not isinstance(raw_voltages, list):
        errors.append("Field 'cell_voltages' must be a list.")
    elif len(raw_voltages) == 0:
        errors.append("Field 'cell_voltages' list cannot be empty.")
    else:
        for idx, val in enumerate(raw_voltages):
            if val is None:
                errors.append(f"Cell voltage at index {idx} is null.")
                continue
            try:
                f_val = float(val)
                validated_voltages.append(round(f_val, 4))
            except (ValueError, TypeError):
                errors.append(f"Cell voltage at index {idx} ({val}) is not a valid number.")

    # 5. Check cell_temperatures
    raw_temps = data.get("cell_temperatures")
    validated_temps: List[float] = []
    if raw_temps is None:
        errors.append("Field 'cell_temperatures' is missing.")
    elif not isinstance(raw_temps, list):
        errors.append("Field 'cell_temperatures' must be a list.")
    elif len(raw_temps) == 0:
        errors.append("Field 'cell_temperatures' list cannot be empty.")
    else:
        for idx, val in enumerate(raw_temps):
            if val is None:
                errors.append(f"Cell temperature at index {idx} is null.")
                continue
            try:
                f_val = float(val)
                validated_temps.append(round(f_val, 2))
            except (ValueError, TypeError):
                errors.append(f"Cell temperature at index {idx} ({val}) is not a valid number.")

    # 6. Current (optional, defaults to 0.0 A)
    current_a = 0.0
    if "current_a" in data and data["current_a"] is not None:
        try:
            current_a = round(float(data["current_a"]), 3)
        except (ValueError, TypeError):
            errors.append("Field 'current_a' must be numeric.")

    is_valid = (len(errors) == 0)

    if not is_valid:
        return False, None, errors

    sanitized = {
        "pack_id": pack_id,
        "timestamp_utc": ts_iso,
        "timestamp_epoch": ts_epoch,
        "mode": mode,
        "cell_voltages": validated_voltages,
        "cell_temperatures": validated_temps,
        "current_a": current_a,
        "cell_count": len(validated_voltages),
        "source": data.get("source", "simulated" if mode == "simulation" else "esp32")
    }

    return True, sanitized, []
