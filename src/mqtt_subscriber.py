"""
Module: mqtt_subscriber.py
Subscribes to MQTT telemetry topics, validates inbound messages, executes calculations,
evaluates rule and ML anomaly status, stores records in SQLite, and dispatches alerts.
"""

import json
import logging
from typing import Optional, Dict, Any, Callable
from src.mqtt_client import MQTTManager
from src.data_validator import validate_battery_payload
from src.calculations import calculate_voltage_metrics, calculate_temperature_metrics, assess_sensor_quality
from src.detection import evaluate_pack_status
from src.database import BatteryDatabase
from src.alerts import AlertManager
from src.ml_pipeline import AnomalyDetector

logger = logging.getLogger(__name__)


class BatteryMQTTSubscriber:
    def __init__(
        self,
        broker_host: str,
        port: int = 1883,
        use_tls: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        topic: str = "battery/cells/data",
        db: Optional[BatteryDatabase] = None,
        alert_manager: Optional[AlertManager] = None,
        ml_detector: Optional[AnomalyDetector] = None
    ):
        self.topic = topic
        self.db = db or BatteryDatabase()
        self.alert_manager = alert_manager or AlertManager(self.db)
        self.ml_detector = ml_detector or AnomalyDetector()

        self.latest_reading: Optional[Dict[str, Any]] = None
        self.on_processed_callback: Optional[Callable[[Dict[str, Any]], None]] = None

        self.manager = MQTTManager(
            broker_host=broker_host,
            port=port,
            use_tls=use_tls,
            username=username,
            password=password,
            client_id=f"battery_sub_{port}"
        )
        self.manager.on_message_callback = self._on_message_received

    def start(self) -> bool:
        connected = self.manager.connect()
        if connected:
            self.manager.client.subscribe(self.topic, qos=1)
            logger.info(f"Subscribed to MQTT topic: {self.topic}")
        return connected

    def stop(self):
        self.manager.disconnect()

    def process_raw_message(self, raw_data: Any) -> Optional[Dict[str, Any]]:
        """
        Unified processing pipeline:
        1. Validation
        2. Calculations
        3. Sensor Quality Assessment
        4. Rule-based Status Classification
        5. AI/ML Anomaly Prediction
        6. SQLite Persistence
        7. Alert Handling
        """
        is_valid, validated_data, errors = validate_battery_payload(raw_data)
        if not is_valid or not validated_data:
            logger.warning(f"Rejected invalid battery payload: {errors}")
            return None

        cell_voltages = validated_data["cell_voltages"]
        cell_temps = validated_data["cell_temperatures"]

        # Calculations
        v_metrics = calculate_voltage_metrics(cell_voltages)
        t_metrics = calculate_temperature_metrics(cell_temps)
        is_sensor_healthy, sensor_issues = assess_sensor_quality(cell_voltages, cell_temps)

        # Rule-based Detection
        status_eval = evaluate_pack_status(
            v_metrics=v_metrics,
            t_metrics=t_metrics,
            cell_voltages=cell_voltages,
            cell_temperatures=cell_temps
        )

        # ML Inference
        features = {
            "delta_v_mv": v_metrics.get("delta_v_mv", 0.0),
            "v_max": v_metrics.get("v_max", 3.7),
            "v_min": v_metrics.get("v_min", 3.7),
            "mean_v": v_metrics.get("mean_v", 3.7),
            "t_max": t_metrics.get("t_max", 25.0),
            "delta_t": t_metrics.get("delta_t", 0.0),
            "current_a": validated_data.get("current_a", 0.0)
        }
        ml_result = self.ml_detector.predict(features)

        # Build evaluated reading payload
        reading_record = {
            "pack_id": validated_data["pack_id"],
            "timestamp_utc": validated_data["timestamp_utc"],
            "timestamp_epoch": validated_data["timestamp_epoch"],
            "mode": validated_data["mode"],
            "source": validated_data["source"],
            "cell_count": validated_data["cell_count"],
            "cell_voltages": cell_voltages,
            "cell_temperatures": cell_temps,
            "current_a": validated_data["current_a"],
            "v_max": v_metrics["v_max"],
            "v_min": v_metrics["v_min"],
            "delta_v": v_metrics["delta_v"],
            "delta_v_mv": v_metrics["delta_v_mv"],
            "mean_v": v_metrics["mean_v"],
            "t_max": t_metrics["t_max"],
            "t_min": t_metrics["t_min"],
            "delta_t": t_metrics["delta_t"],
            "mean_t": t_metrics["mean_t"],
            "rule_status": status_eval["status"],
            "rule_reasons": status_eval["reasons"],
            "affected_cells": status_eval["affected_cells"],
            "ml_prediction": -1 if ml_result.get("is_anomaly") else 1,
            "ml_anomaly_score": ml_result.get("anomaly_score", 0.0),
            "ml_status": ml_result.get("status", "NORMAL"),
            "data_quality": "HEALTHY" if is_sensor_healthy else "SENSOR_ISSUE",
            "sensor_issues": sensor_issues
        }

        # Persist to SQLite
        try:
            self.db.insert_reading(reading_record)
        except Exception as e:
            logger.error(f"Database insert error: {str(e)}")

        # Evaluate alerts
        self.alert_manager.process_reading(reading_record)

        self.latest_reading = reading_record

        if self.on_processed_callback:
            try:
                self.on_processed_callback(reading_record)
            except Exception:
                pass

        return reading_record

    def _on_message_received(self, topic: str, payload_bytes: bytes):
        try:
            payload_str = payload_bytes.decode("utf-8")
            self.process_raw_message(payload_str)
        except Exception as e:
            logger.error(f"Error handling message on {topic}: {str(e)}")
