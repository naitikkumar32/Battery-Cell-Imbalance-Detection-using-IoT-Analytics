"""
Module: mqtt_client.py
Base MQTT connection manager with TLS support, automatic reconnects, and status reporting.

Supports:
- Local plaintext brokers (e.g., Mosquitto on port 1883)
- Cloud TLS-encrypted brokers (e.g., HiveMQ Cloud on port 8883)
- Graceful offline fallback when broker is unreachable
"""

import ssl
import time
import logging
from typing import Optional, Callable, Dict, Any
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MQTTManager:
    def __init__(
        self,
        broker_host: str,
        port: int = 1883,
        use_tls: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        keepalive: int = 60
    ):
        self.broker_host = broker_host.strip() if broker_host else ""
        self.port = port
        self.use_tls = use_tls
        self.username = username.strip() if username else None
        self.password = password if password else None
        self.client_id = client_id or f"battery_client_{int(time.time())}"
        self.keepalive = keepalive

        self.is_connected = False
        self.last_error: Optional[str] = None
        self.on_message_callback: Optional[Callable[[str, bytes], None]] = None

        # Paho MQTT Client setup
        self.client = mqtt.Client(
            client_id=self.client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        self._configure_client()

    def _configure_client(self):
        """Sets credentials, TLS contexts, and internal callbacks."""
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        if self.use_tls or self.port == 8883:
            # Configure default TLS context with system CA certificates
            context = ssl.create_default_context()
            self.client.tls_set_context(context)

        self.client.on_connect = self._handle_connect
        self.client.on_disconnect = self._handle_disconnect
        self.client.on_message = self._handle_message

    def _handle_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.is_connected = True
            self.last_error = None
            logger.info(f"Connected to MQTT broker {self.broker_host}:{self.port}")
        else:
            self.is_connected = False
            self.last_error = f"Connection failed with return code {rc}"
            logger.warning(self.last_error)

    def _handle_disconnect(self, client, userdata, flags, rc, properties=None):
        self.is_connected = False
        if rc != 0:
            self.last_error = f"Unexpected disconnection (code {rc})"
            logger.warning(self.last_error)
        else:
            logger.info("Disconnected from MQTT broker cleanly.")

    def _handle_message(self, client, userdata, message):
        if self.on_message_callback:
            try:
                self.on_message_callback(message.topic, message.payload)
            except Exception as e:
                logger.error(f"Error executing message callback: {str(e)}")

    def connect(self) -> bool:
        """Attempts connection to broker synchronously, starting background network loop."""
        if not self.broker_host:
            self.last_error = "Broker hostname is empty. Operating in offline mode."
            return False

        try:
            self.client.connect(self.broker_host, self.port, self.keepalive)
            self.client.loop_start()
            # Wait up to 3 seconds for connection confirmation
            t_end = time.time() + 3.0
            while time.time() < t_end and not self.is_connected:
                time.sleep(0.1)
            return self.is_connected
        except Exception as e:
            self.is_connected = False
            self.last_error = str(e)
            logger.warning(f"Could not connect to MQTT broker {self.broker_host}:{self.port}: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect and stop background loop."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
        except Exception:
            pass

    def get_status(self) -> Dict[str, Any]:
        return {
            "broker_host": self.broker_host or "None (Offline)",
            "port": self.port,
            "is_connected": self.is_connected,
            "use_tls": self.use_tls or (self.port == 8883),
            "last_error": self.last_error
        }
