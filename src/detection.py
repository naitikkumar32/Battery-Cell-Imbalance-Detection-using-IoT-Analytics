"""
Module: detection.py
Implements rule-based operational status classification and battery fault detection.

Strict rule hierarchy:
1. Critical conditions take precedence over warning conditions.
2. Missing or invalid sensor data NEVER reports as healthy (returns SENSOR_FAULT).
3. Evaluates:
   - Voltage spread (delta V) against Warning (e.g. 0.020V) and Critical (e.g. 0.050V)
   - Cell over-voltage and under-voltage limits
   - Over-temperature and temperature gradient (spread)
"""

from typing import Dict, Any, List, Optional
import yaml
import os


def load_thresholds(config_path: str = "config/thresholds.yaml") -> Dict[str, Any]:
    """Load thresholds from YAML configuration with robust fallbacks."""
    defaults = {
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

    if not os.path.exists(config_path):
        return defaults

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                return {**defaults, **data}
    except Exception:
        pass

    return defaults


def evaluate_pack_status(
    v_metrics: Dict[str, Any],
    t_metrics: Dict[str, Any],
    cell_voltages: List[float],
    cell_temperatures: List[float],
    thresholds: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates rule-based status for a battery pack.

    Returns:
      {
        "status": "NORMAL" | "WARNING" | "CRITICAL" | "SENSOR_FAULT",
        "reasons": List[str],
        "affected_cells": List[int],
        "delta_v": float,
        "delta_v_mv": float,
        "max_temp": float
      }

    Guarantees:
      - Critical checks take precedence over warning checks.
      - SENSOR_FAULT is raised if metrics are invalid or sensors are incomplete.
    """
    if thresholds is None:
        thresholds = load_thresholds()

    v_crit = thresholds.get("voltage_spread", {}).get("critical_v", 0.050)
    v_warn = thresholds.get("voltage_spread", {}).get("warning_v", 0.020)

    cell_crit_high = thresholds.get("cell_voltage_limits", {}).get("critical_high_v", 4.25)
    cell_warn_high = thresholds.get("cell_voltage_limits", {}).get("warning_high_v", 4.22)
    cell_warn_low = thresholds.get("cell_voltage_limits", {}).get("warning_low_v", 3.20)
    cell_crit_low = thresholds.get("cell_voltage_limits", {}).get("critical_low_v", 3.00)

    t_crit_high = thresholds.get("temperature", {}).get("critical_high_c", 60.0)
    t_warn_high = thresholds.get("temperature", {}).get("warning_high_c", 45.0)
    t_crit_spread = thresholds.get("temperature", {}).get("spread_critical_c", 10.0)
    t_warn_spread = thresholds.get("temperature", {}).get("spread_warning_c", 5.0)

    critical_reasons: List[str] = []
    warning_reasons: List[str] = []
    affected_cells: List[int] = []

    # 1. Sanity & Data Completeness Check
    if not v_metrics.get("is_valid", False) or not t_metrics.get("is_valid", False):
        fault_reasons = []
        if not v_metrics.get("is_valid", False):
            fault_reasons.append(v_metrics.get("error") or "Invalid voltage telemetry.")
        if not t_metrics.get("is_valid", False):
            fault_reasons.append(t_metrics.get("error") or "Invalid temperature telemetry.")
        return {
            "status": "SENSOR_FAULT",
            "reasons": fault_reasons,
            "affected_cells": [],
            "delta_v": v_metrics.get("delta_v"),
            "delta_v_mv": v_metrics.get("delta_v_mv"),
            "max_temp": t_metrics.get("t_max")
        }

    delta_v = v_metrics["delta_v"]
    delta_v_mv = v_metrics["delta_v_mv"]
    v_max = v_metrics["v_max"]
    v_min = v_metrics["v_min"]

    t_max = t_metrics["t_max"]
    delta_t = t_metrics["delta_t"]

    # Identify candidate affected cells (min and max cells)
    for idx, v in enumerate(cell_voltages):
        if v == v_max or v == v_min:
            if (idx + 1) not in affected_cells:
                affected_cells.append(idx + 1)

    # 2. Check CRITICAL conditions first
    # 2a. Critical Voltage Spread
    if delta_v >= v_crit:
        critical_reasons.append(
            f"Critical voltage imbalance: spread is {delta_v:.4f}V ({delta_v_mv:.1f}mV) >= {v_crit:.4f}V threshold."
        )

    # 2b. Critical Cell Over/Under Voltage
    for idx, v in enumerate(cell_voltages):
        if v >= cell_crit_high:
            critical_reasons.append(f"Cell {idx+1} critical over-voltage: {v:.3f}V >= {cell_crit_high:.3f}V.")
            if (idx + 1) not in affected_cells:
                affected_cells.append(idx + 1)
        elif v <= cell_crit_low:
            critical_reasons.append(f"Cell {idx+1} critical under-voltage: {v:.3f}V <= {cell_crit_low:.3f}V.")
            if (idx + 1) not in affected_cells:
                affected_cells.append(idx + 1)

    # 2c. Critical Temperature
    if t_max >= t_crit_high:
        critical_reasons.append(f"Critical high temperature: {t_max:.1f}C >= {t_crit_high:.1f}C threshold.")
    if delta_t >= t_crit_spread:
        critical_reasons.append(f"Critical thermal gradient: spread is {delta_t:.1f}C >= {t_crit_spread:.1f}C threshold.")

    if critical_reasons:
        return {
            "status": "CRITICAL",
            "reasons": critical_reasons,
            "affected_cells": affected_cells,
            "delta_v": delta_v,
            "delta_v_mv": delta_v_mv,
            "max_temp": t_max
        }

    # 3. Check WARNING conditions (only if not critical)
    # 3a. Warning Voltage Spread
    if delta_v >= v_warn:
        warning_reasons.append(
            f"Warning voltage imbalance: spread is {delta_v:.4f}V ({delta_v_mv:.1f}mV) >= {v_warn:.4f}V threshold."
        )

    # 3b. Warning Cell Limits
    for idx, v in enumerate(cell_voltages):
        if v >= cell_warn_high:
            warning_reasons.append(f"Cell {idx+1} elevated voltage: {v:.3f}V >= {cell_warn_high:.3f}V.")
            if (idx + 1) not in affected_cells:
                affected_cells.append(idx + 1)
        elif v <= cell_warn_low:
            warning_reasons.append(f"Cell {idx+1} low voltage: {v:.3f}V <= {cell_warn_low:.3f}V.")
            if (idx + 1) not in affected_cells:
                affected_cells.append(idx + 1)

    # 3c. Warning Temperature
    if t_max >= t_warn_high:
        warning_reasons.append(f"Warning elevated temperature: {t_max:.1f}C >= {t_warn_high:.1f}C threshold.")
    if delta_t >= t_warn_spread:
        warning_reasons.append(f"Warning thermal gradient: spread is {delta_t:.1f}C >= {t_warn_spread:.1f}C threshold.")

    if warning_reasons:
        return {
            "status": "WARNING",
            "reasons": warning_reasons,
            "affected_cells": affected_cells,
            "delta_v": delta_v,
            "delta_v_mv": delta_v_mv,
            "max_temp": t_max
        }

    # 4. If neither critical nor warning, status is NORMAL
    return {
        "status": "NORMAL",
        "reasons": ["All cell voltages and pack temperatures are within nominal operating limits."],
        "affected_cells": [],
        "delta_v": delta_v,
        "delta_v_mv": delta_v_mv,
        "max_temp": t_max
    }
