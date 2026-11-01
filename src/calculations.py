"""
Module: calculations.py
Provides core mathematical and engineering calculations for battery packs.

Includes:
- Maximum, minimum, and mean cell voltages
- Voltage spread (delta V) in Volts and millivolts
- Maximum, minimum, and spread temperatures
- Rate of voltage change over time (dV/dt)
- Data quality and sensor sanity validation
"""

import math
from typing import List, Dict, Any, Optional, Tuple


def calculate_voltage_metrics(cell_voltages: List[float]) -> Dict[str, Any]:
    """
    Calculate voltage spread and aggregate statistics for a pack's cell voltages.

    Requirements:
      V_max = max(cell_voltages)
      V_min = min(cell_voltages)
      delta_V = V_max - V_min
      delta_V_mV = delta_V * 1000
      mean_V = sum(cell_voltages) / count

    Handles invalid inputs (empty lists, non-numeric or non-finite values) safely.
    """
    if not cell_voltages:
        return {
            "v_max": None,
            "v_min": None,
            "delta_v": None,
            "delta_v_mv": None,
            "mean_v": None,
            "cell_count": 0,
            "is_valid": False,
            "error": "No cell voltage readings provided."
        }

    # Filter and validate finite numbers
    valid_voltages = []
    for idx, v in enumerate(cell_voltages):
        if v is None:
            continue
        try:
            val = float(v)
            if math.isnan(val) or math.isinf(val):
                continue
            valid_voltages.append((idx, val))
        except (ValueError, TypeError):
            continue

    if not valid_voltages or len(valid_voltages) < len(cell_voltages):
        # Missing or non-finite cells detected
        if not valid_voltages:
            return {
                "v_max": None,
                "v_min": None,
                "delta_v": None,
                "delta_v_mv": None,
                "mean_v": None,
                "cell_count": 0,
                "is_valid": False,
                "error": "All cell voltage readings are invalid or missing."
            }

    raw_values = [v for _, v in valid_voltages]
    v_max = max(raw_values)
    v_min = min(raw_values)
    delta_v = v_max - v_min
    delta_v_mv = delta_v * 1000.0
    mean_v = sum(raw_values) / len(raw_values)

    is_complete = (len(valid_voltages) == len(cell_voltages))

    return {
        "v_max": round(v_max, 4),
        "v_min": round(v_min, 4),
        "delta_v": round(delta_v, 4),
        "delta_v_mv": round(delta_v_mv, 2),
        "mean_v": round(mean_v, 4),
        "cell_count": len(cell_voltages),
        "valid_count": len(valid_voltages),
        "is_valid": is_complete,
        "error": None if is_complete else "Some cell voltage values are missing or invalid."
    }


def calculate_temperature_metrics(cell_temperatures: List[float]) -> Dict[str, Any]:
    """
    Calculate temperature spread and aggregate statistics for cell temperatures.

    Returns:
      t_max: Maximum temperature in deg C
      t_min: Minimum temperature in deg C
      delta_t: Temperature spread across cells (t_max - t_min)
      mean_t: Average cell temperature in deg C
    """
    if not cell_temperatures:
        return {
            "t_max": None,
            "t_min": None,
            "delta_t": None,
            "mean_t": None,
            "sensor_count": 0,
            "is_valid": False,
            "error": "No temperature readings provided."
        }

    valid_temps = []
    for t in cell_temperatures:
        if t is None:
            continue
        try:
            val = float(t)
            if math.isnan(val) or math.isinf(val):
                continue
            valid_temps.append(val)
        except (ValueError, TypeError):
            continue

    if not valid_temps:
        return {
            "t_max": None,
            "t_min": None,
            "delta_t": None,
            "mean_t": None,
            "sensor_count": 0,
            "is_valid": False,
            "error": "All temperature readings are non-finite or invalid."
        }

    t_max = max(valid_temps)
    t_min = min(valid_temps)
    delta_t = t_max - t_min
    mean_t = sum(valid_temps) / len(valid_temps)
    is_complete = (len(valid_temps) == len(cell_temperatures))

    return {
        "t_max": round(t_max, 2),
        "t_min": round(t_min, 2),
        "delta_t": round(delta_t, 2),
        "mean_t": round(mean_t, 2),
        "sensor_count": len(cell_temperatures),
        "valid_count": len(valid_temps),
        "is_valid": is_complete,
        "error": None if is_complete else "Some temperature readings are missing or invalid."
    }


def calculate_rate_of_change(
    current_val: float,
    previous_val: float,
    current_time_epoch: float,
    previous_time_epoch: float
) -> Optional[float]:
    """
    Calculate rate of change dV/dt or dT/dt in units per second.
    Returns None if time difference is zero or negative.
    """
    if current_val is None or previous_val is None:
        return None
    dt = current_time_epoch - previous_time_epoch
    if dt <= 0:
        return None
    return round((current_val - previous_val) / dt, 5)


def assess_sensor_quality(
    cell_voltages: List[float],
    cell_temperatures: List[float],
    min_physical_v: float = 0.5,
    max_physical_v: float = 5.0,
    min_physical_t: float = -40.0,
    max_physical_t: float = 120.0
) -> Tuple[bool, List[str]]:
    """
    Assess raw sensor health against physical bounds.
    Detects disconnected ADC channels, open thermocouples, short circuits, or NaNs.
    """
    issues = []

    if not cell_voltages:
        issues.append("Missing voltage telemetry.")
    else:
        for i, v in enumerate(cell_voltages):
            if v is None:
                issues.append(f"Cell {i+1} voltage is null.")
                continue
            try:
                v_f = float(v)
                if math.isnan(v_f) or math.isinf(v_f):
                    issues.append(f"Cell {i+1} voltage is non-finite (NaN/Inf).")
                elif v_f < min_physical_v:
                    issues.append(f"Cell {i+1} voltage {v_f:.3f}V below physical limit {min_physical_v}V.")
                elif v_f > max_physical_v:
                    issues.append(f"Cell {i+1} voltage {v_f:.3f}V exceeds physical limit {max_physical_v}V.")
            except (ValueError, TypeError):
                issues.append(f"Cell {i+1} voltage could not be parsed as float.")

    if not cell_temperatures:
        issues.append("Missing temperature telemetry.")
    else:
        for i, t in enumerate(cell_temperatures):
            if t is None:
                issues.append(f"Temp sensor {i+1} is null.")
                continue
            try:
                t_f = float(t)
                if math.isnan(t_f) or math.isinf(t_f):
                    issues.append(f"Temp sensor {i+1} is non-finite (NaN/Inf).")
                elif t_f < min_physical_t or t_f > max_physical_t:
                    issues.append(f"Temp sensor {i+1} value {t_f:.1f}C out of physical range.")
            except (ValueError, TypeError):
                issues.append(f"Temp sensor {i+1} could not be parsed as float.")

    is_healthy = len(issues) == 0
    return is_healthy, issues
