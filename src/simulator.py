"""
Module: simulator.py
Synthetic battery data generator with realistic physics, noise, and configurable operational scenarios.

Supported Scenarios:
- 'normal': Tightly balanced cells, low noise, steady discharge
- 'imbalance': Progressive divergence of one cell causing warning/critical spread
- 'overheating': Gradual temperature rise beyond safe operational thresholds
- 'sensor_failure': Erratic / shorted ADC reading (e.g. 0V or 5V or infinite spike)
- 'missing_data': Dropped cell readings or incomplete telemetry
"""

import time
import math
import random
import json
import os
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable


class BatterySimulator:
    def __init__(
        self,
        pack_id: str = "PACK-01",
        cell_count: int = 4,
        interval_seconds: float = 2.0,
        csv_export_path: str = "exports/simulation_data.csv"
    ):
        self.pack_id = pack_id
        self.cell_count = cell_count
        self.interval_seconds = interval_seconds
        self.csv_export_path = csv_export_path

        self.scenario = "normal"
        self.is_running = False
        self.is_paused = False
        self._thread: Optional[threading.Thread] = None

        # Base physical state
        self.nominal_cell_v = 3.85
        self.nominal_temp_c = 28.0
        self.pack_current_a = 2.5 # Discharging at 2.5 A

        # Dynamic state vectors
        self.cell_voltages: List[float] = [self.nominal_cell_v for _ in range(cell_count)]
        self.cell_temperatures: List[float] = [self.nominal_temp_c for _ in range(cell_count)]
        self.step_counter = 0

        # Ensure directory for CSV export exists
        csv_dir = os.path.dirname(self.csv_export_path)
        if csv_dir and not os.path.exists(csv_dir):
            os.makedirs(csv_dir, exist_ok=True)

        self._init_csv_file()

    def _init_csv_file(self):
        """Creates the CSV file with header if it doesn't exist."""
        if not os.path.exists(self.csv_export_path):
            headers = [
                "timestamp_utc", "pack_id", "mode", "scenario", "current_a"
            ]
            for i in range(1, self.cell_count + 1):
                headers.append(f"cell_{i}_v")
            for i in range(1, self.cell_count + 1):
                headers.append(f"cell_{i}_temp_c")
            try:
                with open(self.csv_export_path, "w", encoding="utf-8") as f:
                    f.write(",".join(headers) + "\n")
            except Exception:
                pass

    def set_scenario(self, scenario: str):
        """Update simulation scenario dynamically."""
        valid_scenarios = ["normal", "imbalance", "overheating", "sensor_failure", "missing_data"]
        if scenario in valid_scenarios:
            self.scenario = scenario
            if scenario == "normal":
                # Reset cells to balanced state
                self.cell_voltages = [3.85 + random.uniform(-0.003, 0.003) for _ in range(self.cell_count)]
                self.cell_temperatures = [28.0 + random.uniform(-0.5, 0.5) for _ in range(self.cell_count)]
                self.step_counter = 0

    def generate_reading(self) -> Dict[str, Any]:
        """
        Computes one synthetic reading frame based on the active scenario.
        Returns a standardized telemetry dictionary.
        """
        self.step_counter += 1
        now = datetime.now(timezone.utc)
        timestamp_iso = now.isoformat()

        # Base discharge slope
        discharge_decay = 0.0002
        noise_sigma = 0.0015

        voltages: List[Optional[float]] = []
        temps: List[Optional[float]] = []

        # Apply scenario behaviors
        if self.scenario == "normal":
            for i in range(self.cell_count):
                self.cell_voltages[i] = max(3.0, self.cell_voltages[i] - discharge_decay)
                v_reading = self.cell_voltages[i] + random.gauss(0, noise_sigma)
                t_reading = self.cell_temperatures[i] + random.gauss(0, 0.1)
                voltages.append(round(v_reading, 4))
                temps.append(round(t_reading, 2))

        elif self.scenario == "imbalance":
            # Cell 2 degrades significantly faster or suffers internal resistance loss
            for i in range(self.cell_count):
                rate = discharge_decay * 4.0 if i == 1 else discharge_decay
                self.cell_voltages[i] = max(2.95, self.cell_voltages[i] - rate)
                v_reading = self.cell_voltages[i] + random.gauss(0, noise_sigma)
                t_reading = self.cell_temperatures[i] + (0.05 if i == 1 else 0.0)
                voltages.append(round(v_reading, 4))
                temps.append(round(t_reading, 2))

        elif self.scenario == "overheating":
            for i in range(self.cell_count):
                self.cell_voltages[i] = max(3.0, self.cell_voltages[i] - discharge_decay)
                # Cell 3 exhibits severe localized thermal runaway / heating
                if i == 2:
                    self.cell_temperatures[i] += 1.8
                else:
                    self.cell_temperatures[i] += 0.4
                voltages.append(round(self.cell_voltages[i] + random.gauss(0, noise_sigma), 4))
                temps.append(round(self.cell_temperatures[i], 2))

        elif self.scenario == "sensor_failure":
            for i in range(self.cell_count):
                if i == 0:
                    # Cell 1 sensor ADC disconnects / shorts to ground
                    voltages.append(0.0)
                    temps.append(-40.0)
                else:
                    voltages.append(round(self.cell_voltages[i] + random.gauss(0, noise_sigma), 4))
                    temps.append(round(self.cell_temperatures[i], 2))

        elif self.scenario == "missing_data":
            for i in range(self.cell_count):
                if i == (self.cell_count - 1):
                    # Last cell dropped in packet
                    voltages.append(None)
                    temps.append(None)
                else:
                    voltages.append(round(self.cell_voltages[i] + random.gauss(0, noise_sigma), 4))
                    temps.append(round(self.cell_temperatures[i], 2))
        else:
            # Fallback normal
            voltages = [round(v, 4) for v in self.cell_voltages]
            temps = [round(t, 2) for t in self.cell_temperatures]

        # Pack current with small load fluctuation
        current_reading = round(self.pack_current_a + random.gauss(0, 0.05), 3)

        payload = {
            "pack_id": self.pack_id,
            "timestamp": timestamp_iso,
            "mode": "simulation",
            "source": "synthetic_generator",
            "scenario": self.scenario,
            "cell_voltages": voltages,
            "cell_temperatures": temps,
            "current_a": current_reading,
            "cell_count": self.cell_count
        }

        self._log_to_csv(payload)
        return payload

    def _log_to_csv(self, payload: Dict[str, Any]):
        """Appends reading to local CSV export."""
        try:
            row = [
                payload["timestamp"],
                payload["pack_id"],
                payload["mode"],
                payload.get("scenario", ""),
                str(payload.get("current_a", 0.0))
            ]
            for v in payload["cell_voltages"]:
                row.append("" if v is None else str(v))
            for t in payload["cell_temperatures"]:
                row.append("" if t is None else str(t))

            with open(self.csv_export_path, "a", encoding="utf-8") as f:
                f.write(",".join(row) + "\n")
        except Exception:
            pass

    def start(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """Starts asynchronous simulation thread with optional callback."""
        if self.is_running:
            return

        self.is_running = True
        self.is_paused = False

        def _run():
            while self.is_running:
                if not self.is_paused:
                    reading = self.generate_reading()
                    if callback:
                        try:
                            callback(reading)
                        except Exception:
                            pass
                time.sleep(self.interval_seconds)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
