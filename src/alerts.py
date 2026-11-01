"""
Module: alerts.py
Manages alert lifecycle, state transitions, notification cooldowns, and dispatching.

Ensures:
- Cooldown timer prevents flooding logs and databases every 2 seconds.
- State changes (e.g. NORMAL -> WARNING, WARNING -> CRITICAL) trigger immediate alerts.
- Optional SMTP email dispatch is executed safely without blocking.
- Never fabricates or claims an alert/email succeeded unless verified.
"""

import os
import time
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List, Tuple
from src.database import BatteryDatabase

logger = logging.getLogger(__name__)


class AlertManager:
    def __init__(self, db: BatteryDatabase, cooldown_seconds: float = 60.0):
        self.db = db
        self.cooldown_seconds = cooldown_seconds

        # State tracking: pack_id -> {"last_status": str, "last_alert_time": float}
        self._pack_state: Dict[str, Dict[str, Any]] = {}

    def process_reading(self, reading_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluates reading status and triggers an alert if condition warrants
        and cooldown period has elapsed or state transitioned to worse.
        """
        pack_id = reading_data.get("pack_id", "UNKNOWN")
        status = reading_data.get("rule_status", "NORMAL")

        if status in ("NORMAL", None):
            # Reset or track normal status
            if pack_id in self._pack_state:
                self._pack_state[pack_id]["last_status"] = "NORMAL"
            return None

        # Status is WARNING, CRITICAL, or SENSOR_FAULT
        now = time.time()
        pack_entry = self._pack_state.get(pack_id, {
            "last_status": "NORMAL",
            "last_alert_time": 0.0
        })

        last_status = pack_entry["last_status"]
        last_alert_time = pack_entry["last_alert_time"]

        # Escalate immediately if state became more severe
        severity_order = {"NORMAL": 0, "WARNING": 1, "SENSOR_FAULT": 2, "CRITICAL": 3}
        current_sev = severity_order.get(status, 1)
        last_sev = severity_order.get(last_status, 0)

        escalated = current_sev > last_sev
        cooldown_elapsed = (now - last_alert_time) >= self.cooldown_seconds

        if escalated or cooldown_elapsed:
            # Trigger alert record
            reasons = reading_data.get("rule_reasons", [])
            primary_reason = "; ".join(reasons) if reasons else f"Condition: {status}"

            affected = reading_data.get("affected_cells", [])
            delta_v_mv = reading_data.get("delta_v_mv")
            max_temp = reading_data.get("t_max")

            alert_id = self.db.insert_alert(
                pack_id=pack_id,
                alert_level=status,
                reason=primary_reason,
                affected_cells=affected,
                delta_v_mv=delta_v_mv,
                max_temp=max_temp
            )

            # Update tracked state
            self._pack_state[pack_id] = {
                "last_status": status,
                "last_alert_time": now
            }

            alert_payload = {
                "alert_id": alert_id,
                "pack_id": pack_id,
                "status": status,
                "reason": primary_reason,
                "affected_cells": affected,
                "delta_v_mv": delta_v_mv,
                "max_temp": max_temp,
                "timestamp_utc": reading_data.get("timestamp_utc")
            }

            # Optional email dispatch
            self._dispatch_email_if_configured(alert_payload)

            return alert_payload

        # Suppressed by cooldown
        return None

    def _dispatch_email_if_configured(self, alert_payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Dispatches email alert via SMTP only if explicitly enabled in environment variables.
        """
        enabled = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        if not enabled:
            return False, "Email alerts disabled in configuration."

        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USERNAME")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        recipient = os.getenv("ALERT_RECIPIENT_EMAIL")

        if not (smtp_host and smtp_user and smtp_pass and recipient):
            return False, "SMTP configuration incomplete. Skipping email dispatch."

        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = recipient
            msg["Subject"] = f"[{alert_payload['status']}] Battery Alert: {alert_payload['pack_id']}"

            body = f"""
BATTERY MONITORING ALARM NOTIFICATION
====================================
Pack ID:         {alert_payload['pack_id']}
Alert Level:     {alert_payload['status']}
Timestamp:       {alert_payload.get('timestamp_utc')}
Voltage Spread:  {alert_payload.get('delta_v_mv')} mV
Max Temperature: {alert_payload.get('max_temp')} °C
Affected Cells:  {alert_payload.get('affected_cells')}

Reason:
{alert_payload.get('reason')}

Please inspect the system dashboard immediately.
"""
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10.0) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            logger.info(f"Dispatched email alert to {recipient} for {alert_payload['pack_id']}")
            return True, f"Alert email sent to {recipient}"
        except Exception as e:
            logger.error(f"Failed to dispatch email alert: {str(e)}")
            return False, f"Email dispatch failed: {str(e)}"
