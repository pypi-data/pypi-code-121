"""MQTT Sensor entity module."""
import json
import logging
from typing import Any, Dict, Optional, Union

from mqtt_hass_base.const import SENSOR_DEVICE_CLASSES
from mqtt_hass_base.entity.common import EntitySettingsType, MqttEntity
from mqtt_hass_base.error import MQTTHassBaseError


class SensorSettingsType(EntitySettingsType, total=False):
    """Sensor entity settings dict format."""

    device_class: Optional[str]
    expire_after: Optional[int]
    force_update: Optional[bool]
    off_delay: Optional[int]
    icon: str
    unit: str
    state_class: Optional[str]


class MqttSensor(MqttEntity):
    """MQTT Sensor entity class."""

    _component = "sensor"

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        unique_id: str,
        mqtt_discovery_root_topic: str,
        mqtt_data_root_topic: str,
        logger: logging.Logger,
        device_payload: Dict[str, str],
        subscriptions: Dict[str, str],
        device_class: Optional[str] = None,
        expire_after: int = 0,
        force_update: bool = False,
        icon: str = "",
        unit: str = "",
        state_class: Optional[str] = None,
        object_id: Optional[str] = None,
    ):
        """Create a new MQTT sensor entity object."""
        MqttEntity.__init__(
            self,
            name,
            unique_id,
            mqtt_discovery_root_topic,
            mqtt_data_root_topic,
            logger,
            device_payload,
            object_id=object_id,
        )
        if device_class is not None and device_class not in SENSOR_DEVICE_CLASSES:
            msg = (
                f"Bad device class {device_class}. Should be in {SENSOR_DEVICE_CLASSES}"
            )
            self.logger.error(msg)
            raise MQTTHassBaseError(msg)
        self._device_class = device_class
        self._expire_after = expire_after
        self._force_update = force_update
        self._state_class = state_class
        self._icon = icon
        self._unit = unit

    def register(self) -> None:
        """Register the current entity to Home Assistant.

        Using the MQTT discovery feature of Home Assistant.
        """
        config_payload = {
            "availability_topic": self.availability_topic,
            "device": self.device_payload,
            "expire_after": self._expire_after,
            "force_update": self._force_update,
            # "json_attributes_template": "",
            "json_attributes_topic": self.json_attributes_topic,
            "name": self.name,
            "payload_available": "online",
            "payload_not_available": "offline",
            "qos": 0,
            "state_topic": self.state_topic,
            "unique_id": self._unique_id,
        }
        if self._device_class:
            config_payload["device_class"] = self._device_class
        if self._icon:
            config_payload["icon"] = self._icon
        if self._unit:
            config_payload["unit_of_measurement"] = self._unit
        if self._object_id:
            config_payload["object_id"] = self._object_id

        self.logger.debug("%s: %s", self.config_topic, json.dumps(config_payload))
        self._mqtt_client.publish(
            topic=self.config_topic, retain=True, payload=json.dumps(config_payload)
        )

    def send_state(
        self,
        state: Union[str, bytes, float, int],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send the current state of the sensor to Home Assistant."""
        if isinstance(state, (bytes, str)):
            state = state[:255]
        self._mqtt_client.publish(topic=self.state_topic, retain=True, payload=state)
        if attributes is not None:
            self.send_attributes(attributes)
