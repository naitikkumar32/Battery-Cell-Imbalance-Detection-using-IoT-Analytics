"""
Module: dashboard_helpers.py
Provides UI components, Plotly visualizations, status badges, and formatting helpers
for the Streamlit Battery Monitoring Dashboard.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone


def apply_custom_css():
    """Returns CSS string for styling the dashboard."""
    return """
    <style>
        /* Modern engineering dashboard theme */
        .main-header {
            font-size: 1.85rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
        }
        .sub-header {
            font-size: 0.95rem;
            color: #64748B;
            margin-bottom: 1.2rem;
        }
        .metric-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .metric-title {
            font-size: 0.80rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #0F172A;
            margin: 4px 0;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            font-size: 0.85rem;
            font-weight: 700;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .status-normal { background-color: #DEF7EC; color: #03543F; border: 1px solid #84E1BC; }
        .status-warning { background-color: #FEF08A; color: #713F12; border: 1px solid #FDE047; }
        .status-critical { background-color: #FDE8E8; color: #9B1C1C; border: 1px solid #F8B4B4; }
        .status-fault { background-color: #EDEBFE; color: #5521B5; border: 1px solid #CABFFD; }
        .mode-sim { background-color: #E1EFFE; color: #1E429F; border: 1px solid #A4CAFE; }
        .mode-hw { background-color: #D1FAE5; color: #065F46; border: 1px solid #6EE7B7; }
        .stale-warning {
            background-color: #FFFBEB;
            border-left: 4px solid #F59E0B;
            padding: 10px 14px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-size: 0.9rem;
            color: #92400E;
        }
    </style>
    """


def render_status_pill(status: str) -> str:
    """Returns HTML for color-coded status badge."""
    status_clean = (status or "UNKNOWN").upper()
    css_class = "status-normal"
    if "CRITICAL" in status_clean:
        css_class = "status-critical"
    elif "WARN" in status_clean:
        css_class = "status-warning"
    elif "FAULT" in status_clean or "ISSUE" in status_clean:
        css_class = "status-fault"

    return f'<span class="status-badge {css_class}">{status_clean}</span>'


def render_mode_pill(mode: str) -> str:
    """Returns HTML for operating mode badge."""
    mode_clean = (mode or "SIMULATION").upper()
    css_class = "mode-hw" if "HARDWARE" in mode_clean else "mode-sim"
    return f'<span class="status-badge {css_class}">MODE: {mode_clean}</span>'


def check_is_stale(timestamp_utc_str: Optional[str], timeout_seconds: float = 10.0) -> Tuple[bool, float]:
    """Check if the latest reading is older than timeout."""
    if not timestamp_utc_str:
        return True, 999.0
    try:
        clean_ts = timestamp_utc_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        diff_seconds = (datetime.now(timezone.utc) - dt).total_seconds()
        return (diff_seconds > timeout_seconds), round(diff_seconds, 1)
    except Exception:
        return True, 999.0


def create_cell_voltage_chart(cell_voltages: List[float], v_min: float, v_max: float) -> go.Figure:
    """Generates an interactive bar chart of cell voltages."""
    cells = [f"Cell {i+1}" for i in range(len(cell_voltages))]
    colors = []
    for v in cell_voltages:
        if v == v_max and (v_max - v_min) >= 0.020:
            colors.append("#EF4444") # Red for max diverging cell
        elif v == v_min and (v_max - v_min) >= 0.020:
            colors.append("#F59E0B") # Amber for min diverging cell
        else:
            colors.append("#3B82F6") # Nominal blue

    fig = go.Figure(
        data=[
            go.Bar(
                x=cells,
                y=cell_voltages,
                marker_color=colors,
                text=[f"{v:.4f} V" for v in cell_voltages],
                textposition="auto"
            )
        ]
    )

    y_lower = max(0.0, (min(cell_voltages) - 0.05)) if cell_voltages else 3.0
    y_upper = (max(cell_voltages) + 0.05) if cell_voltages else 4.25

    fig.update_layout(
        title="Live Cell Voltages (V)",
        yaxis_title="Voltage (V)",
        yaxis=dict(range=[y_lower, y_upper]),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        template="plotly_white"
    )
    return fig


def create_temperature_chart(cell_temperatures: List[float]) -> go.Figure:
    """Generates an interactive bar chart of cell temperatures."""
    cells = [f"Sensor {i+1}" for i in range(len(cell_temperatures))]
    colors = ["#EF4444" if t >= 45.0 else "#10B981" for t in cell_temperatures]

    fig = go.Figure(
        data=[
            go.Bar(
                x=cells,
                y=cell_temperatures,
                marker_color=colors,
                text=[f"{t:.1f} °C" for t in cell_temperatures],
                textposition="auto"
            )
        ]
    )
    fig.update_layout(
        title="Cell Temperature Profile (°C)",
        yaxis_title="Temperature (°C)",
        yaxis=dict(range=[0, max(65.0, (max(cell_temperatures) + 5.0) if cell_temperatures else 50.0)]),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        template="plotly_white"
    )
    return fig


def create_voltage_spread_history_chart(
    history_df: pd.DataFrame,
    warn_thresh_mv: float = 20.0,
    crit_thresh_mv: float = 50.0
) -> go.Figure:
    """Plots historical voltage spread in mV with threshold reference lines."""
    fig = go.Figure()

    if not history_df.empty and "delta_v_mv" in history_df.columns:
        fig.add_trace(
            go.Scatter(
                x=history_df["timestamp_utc"],
                y=history_df["delta_v_mv"],
                mode="lines+markers",
                name="Voltage Spread (mV)",
                line=dict(color="#2563EB", width=2),
                marker=dict(size=4)
            )
        )

        # Warning threshold line
        fig.add_hline(
            y=warn_thresh_mv,
            line_dash="dash",
            line_color="#F59E0B",
            annotation_text=f"Warning ({warn_thresh_mv} mV)",
            annotation_position="bottom right"
        )
        # Critical threshold line
        fig.add_hline(
            y=crit_thresh_mv,
            line_dash="dot",
            line_color="#DC2626",
            annotation_text=f"Critical ({crit_thresh_mv} mV)",
            annotation_position="top right"
        )

    fig.update_layout(
        title="Voltage Spread History (delta V in mV)",
        xaxis_title="UTC Timestamp",
        yaxis_title="Spread (mV)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        template="plotly_white"
    )
    return fig


def create_multi_cell_history_chart(history_records: List[Dict[str, Any]]) -> go.Figure:
    """Plots each cell voltage as an individual line over time."""
    fig = go.Figure()
    if not history_records:
        fig.update_layout(title="Multi-Cell Voltage Trend (No data yet)")
        return fig

    # Determine cell count
    first_voltages = history_records[0].get("cell_voltages", [])
    cell_count = len(first_voltages)
    timestamps = [r["timestamp_utc"] for r in history_records]

    colors = ["#2563EB", "#7C3AED", "#059669", "#D97706", "#DC2626", "#0891B2"]

    for c_idx in range(cell_count):
        cell_vals = []
        for r in history_records:
            v_list = r.get("cell_voltages", [])
            val = v_list[c_idx] if c_idx < len(v_list) else None
            cell_vals.append(val)

        color = colors[c_idx % len(colors)]
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=cell_vals,
                mode="lines",
                name=f"Cell {c_idx+1}",
                line=dict(color=color, width=2)
            )
        )

    fig.update_layout(
        title="Multi-Cell Voltage Trends Over Time",
        xaxis_title="UTC Timestamp",
        yaxis_title="Voltage (V)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        template="plotly_white"
    )
    return fig
