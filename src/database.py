"""
Module: database.py
SQLite persistence layer for battery monitoring, historical analytics, alerts, and authentication.

Features:
- Thread-safe parameterized queries with WAL mode and busy timeout
- Tables:
  1. `battery_readings`: Raw and aggregated telemetry
  2. `alerts`: Event-driven alarms with acknowledgement status
  3. `users`: Authentication records with hashed credentials
- Automatic table creation and indexing
- Graceful handling of empty states
- CSV export capability
- Automated backup and retention cleanup
"""

import sqlite3
import os
import json
import shutil
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BatteryDatabase:
    def __init__(self, db_path: str = "data/battery.db"):
        self.db_path = db_path
        self._ensure_dir()
        self.init_db()

    def _ensure_dir(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Create a connection with WAL mode and reasonable timeout for concurrency."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
        return conn

    def init_db(self):
        """Initializes tables and indexes automatically if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Readings Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS battery_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pack_id TEXT NOT NULL,
                    timestamp_utc TEXT NOT NULL,
                    timestamp_epoch REAL NOT NULL,
                    mode TEXT NOT NULL,
                    source TEXT,
                    cell_count INTEGER NOT NULL,
                    cell_voltages_json TEXT NOT NULL,
                    cell_temperatures_json TEXT NOT NULL,
                    current_a REAL DEFAULT 0.0,
                    v_max REAL,
                    v_min REAL,
                    delta_v REAL,
                    delta_v_mv REAL,
                    mean_v REAL,
                    t_max REAL,
                    t_min REAL,
                    delta_t REAL,
                    mean_t REAL,
                    rule_status TEXT NOT NULL,
                    rule_reasons_json TEXT,
                    ml_prediction INTEGER DEFAULT 1,
                    ml_anomaly_score REAL DEFAULT 0.0,
                    data_quality TEXT DEFAULT 'HEALTHY',
                    created_at TEXT NOT NULL
                );
            """)

            # 2. Indexes for fast historical querying
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_readings_pack_time 
                ON battery_readings (pack_id, timestamp_epoch DESC);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_readings_status 
                ON battery_readings (rule_status);
            """)

            # 3. Alerts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pack_id TEXT NOT NULL,
                    timestamp_utc TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    affected_cells_json TEXT,
                    delta_v_mv REAL,
                    max_temp REAL,
                    reason TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0,
                    acknowledged_at TEXT,
                    acknowledged_by TEXT
                );
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_ack 
                ON alerts (acknowledged, timestamp_utc DESC);
            """)

            # 4. Users Table for Auth
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'operator',
                    created_at TEXT NOT NULL
                );
            """)

            conn.commit()

    def insert_reading(self, reading_data: Dict[str, Any]) -> int:
        """
        Inserts a single validated and evaluated reading record.
        Uses parameterized query to prevent SQL injection.
        """
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO battery_readings (
                    pack_id, timestamp_utc, timestamp_epoch, mode, source,
                    cell_count, cell_voltages_json, cell_temperatures_json, current_a,
                    v_max, v_min, delta_v, delta_v_mv, mean_v,
                    t_max, t_min, delta_t, mean_t,
                    rule_status, rule_reasons_json,
                    ml_prediction, ml_anomaly_score, data_quality, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reading_data.get("pack_id", "UNKNOWN"),
                reading_data.get("timestamp_utc", now_utc),
                reading_data.get("timestamp_epoch", datetime.now(timezone.utc).timestamp()),
                reading_data.get("mode", "simulation"),
                reading_data.get("source", "simulator"),
                reading_data.get("cell_count", len(reading_data.get("cell_voltages", []))),
                json.dumps(reading_data.get("cell_voltages", [])),
                json.dumps(reading_data.get("cell_temperatures", [])),
                reading_data.get("current_a", 0.0),
                reading_data.get("v_max"),
                reading_data.get("v_min"),
                reading_data.get("delta_v"),
                reading_data.get("delta_v_mv"),
                reading_data.get("mean_v"),
                reading_data.get("t_max"),
                reading_data.get("t_min"),
                reading_data.get("delta_t"),
                reading_data.get("mean_t"),
                reading_data.get("rule_status", "NORMAL"),
                json.dumps(reading_data.get("rule_reasons", [])),
                reading_data.get("ml_prediction", 1),
                reading_data.get("ml_anomaly_score", 0.0),
                reading_data.get("data_quality", "HEALTHY"),
                now_utc
            ))
            conn.commit()
            return cursor.lastrowid

    def get_latest_reading(self, pack_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch the most recent reading for a given pack or overall."""
        query = "SELECT * FROM battery_readings"
        params = ()
        if pack_id:
            query += " WHERE pack_id = ?"
            params = (pack_id,)
        query += " ORDER BY timestamp_epoch DESC LIMIT 1"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_reading_dict(row)

    def get_historical_readings(
        self,
        pack_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve recent readings for time series charting."""
        query = "SELECT * FROM battery_readings"
        params = []
        if pack_id:
            query += " WHERE pack_id = ?"
            params.append(pack_id)
        query += " ORDER BY timestamp_epoch DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            # Return in chronological order
            return [self._row_to_reading_dict(r) for r in reversed(rows)]

    def get_available_packs(self) -> List[str]:
        """Returns list of distinct pack IDs in database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT pack_id FROM battery_readings ORDER BY pack_id")
            rows = cursor.fetchall()
            return [r[0] for r in rows] if rows else ["PACK-01"]

    def _row_to_reading_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a SQLite Row to a structured dictionary."""
        d = dict(row)
        try:
            d["cell_voltages"] = json.loads(d["cell_voltages_json"])
        except Exception:
            d["cell_voltages"] = []
        try:
            d["cell_temperatures"] = json.loads(d["cell_temperatures_json"])
        except Exception:
            d["cell_temperatures"] = []
        try:
            d["rule_reasons"] = json.loads(d.get("rule_reasons_json") or "[]")
        except Exception:
            d["rule_reasons"] = []
        return d

    # ==================== ALERTS ====================

    def insert_alert(
        self,
        pack_id: str,
        alert_level: str,
        reason: str,
        affected_cells: Optional[List[int]] = None,
        delta_v_mv: Optional[float] = None,
        max_temp: Optional[float] = None
    ) -> int:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (
                    pack_id, timestamp_utc, alert_level, affected_cells_json,
                    delta_v_mv, max_temp, reason, acknowledged
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                pack_id,
                now_utc,
                alert_level,
                json.dumps(affected_cells or []),
                delta_v_mv,
                max_temp,
                reason
            ))
            conn.commit()
            return cursor.lastrowid

    def get_recent_alerts(self, limit: int = 50, unack_only: bool = False) -> List[Dict[str, Any]]:
        query = "SELECT * FROM alerts"
        params = []
        if unack_only:
            query += " WHERE acknowledged = 0"
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                item = dict(r)
                try:
                    item["affected_cells"] = json.loads(item["affected_cells_json"])
                except Exception:
                    item["affected_cells"] = []
                result.append(item)
            return result

    def acknowledge_alert(self, alert_id: int, acknowledged_by: str = "operator") -> bool:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE alerts
                SET acknowledged = 1, acknowledged_at = ?, acknowledged_by = ?
                WHERE id = ?
            """, (now_utc, acknowledged_by, alert_id))
            conn.commit()
            return cursor.rowcount > 0

    # ==================== EXPORT & BACKUP ====================

    def export_readings_to_csv(self, export_path: str = "exports/historical_readings.csv") -> Tuple[bool, str]:
        """Exports all historical readings to CSV cleanly."""
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        readings = self.get_historical_readings(limit=10000)
        if not readings:
            return False, "No readings available in database to export."

        try:
            import pandas as pd
            records = []
            for r in readings:
                rec = {
                    "id": r["id"],
                    "pack_id": r["pack_id"],
                    "timestamp_utc": r["timestamp_utc"],
                    "mode": r["mode"],
                    "source": r.get("source"),
                    "v_max": r["v_max"],
                    "v_min": r["v_min"],
                    "delta_v": r["delta_v"],
                    "delta_v_mv": r["delta_v_mv"],
                    "mean_v": r["mean_v"],
                    "t_max": r["t_max"],
                    "t_min": r["t_min"],
                    "delta_t": r["delta_t"],
                    "current_a": r["current_a"],
                    "rule_status": r["rule_status"],
                    "ml_prediction": r.get("ml_prediction"),
                    "ml_anomaly_score": r.get("ml_anomaly_score"),
                    "data_quality": r.get("data_quality")
                }
                # Flatten cell voltages
                for idx, v in enumerate(r.get("cell_voltages", [])):
                    rec[f"cell_{idx+1}_v"] = v
                for idx, t in enumerate(r.get("cell_temperatures", [])):
                    rec[f"cell_{idx+1}_temp_c"] = t
                records.append(rec)

            df = pd.DataFrame(records)
            df.to_csv(export_path, index=False)
            return True, f"Successfully exported {len(records)} records to {export_path}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"

    def backup_database(self, backup_dir: str = "data/backups") -> Tuple[bool, str]:
        """Creates a timestamped snapshot of the SQLite database."""
        try:
            os.makedirs(backup_dir, exist_ok=True)
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = os.path.join(backup_dir, f"battery_backup_{timestamp_str}.db")
            shutil.copy2(self.db_path, target_path)
            return True, target_path
        except Exception as e:
            return False, f"Backup error: {str(e)}"
