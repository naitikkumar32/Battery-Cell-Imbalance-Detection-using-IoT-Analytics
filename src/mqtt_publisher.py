"""
Module: mqtt_publisher.py
Publishes battery cell telemetry packets to local or cloud MQTT brokers.
"""

import json
import logging
from typing import Dict, Any, Optional
from src.mqtt_client import MQTTManager

logger = logging.getLogger(__name__)


class BatteryMQTTPublisher:
    def __init__(
        self,
        broker_host: str,
        port: int = 1883,
        use_tls: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        topic: str = "battery/cells/data"
    ):
        self.topic = topic
        self.manager = MQTTManager(
            broker_host=broker_host,
            port=port,
            use_tls=use_tls,
            username=username,
            password=password,
            client_id=f"battery_pub_{port}"
        )

    def start(self) -> bool:
        return self.manager.connect()

    def stop(self):
        self.manager.disconnect()

    def publish_payload(self, payload: Dict[str, Any]) -> bool:
        """Serializes and publishes battery telemetry payload to designated topic."""
        if not self.manager.is_connected:
            return False

        try:
            json_str = json.dumps(payload)
            info = self.manager.client.publish(self.topic, json_str, qos=1)
            info.wait_for_publish(timeout=2.0)
            return info.is_published()
        except Exception as e:
            logger.error(f"Failed to publish MQTT message: {str(e)}")
            return False
