"""MQTT Binary sensor entity module."""
import json
import logging
from typing import Any, Dict, Optional, Union

from mqtt_hass_base.const import BINARY_SENSOR_DEVICE_CLASSES
from mqtt_hass_base.entity.common import EntitySettingsType, MqttEntity
from mqtt_hass_base.error import MQTTHassBaseError


class BinarySensorSettingsType(EntitySettingsType, total=False):
    """Binary sensor entity settings dict format."""

    device_class: Optional[str]
    expire_after: Optional[int]
    force_update: Optional[bool]
    off_delay: Optional[int]
    icon: str
    state_class: Optional[str]


class MqttBinarysensor(MqttEntity):
    """MQTT Binary sensor entity class.

    See: https://www.home-assistant.io/integrations/binary_sensor.mqtt/
    """

    _component = "binary_sensor"

    def __init__(
        self,
        name: str,
        unique_id: str,
        mqtt_discovery_root_topic: str,
        mqtt_data_root_topic: str,
        logger: logging.Logger,
        device_payload: Optional[Dict[str, str]] = None,
        subscriptions: Optional[Dict[str, str]] = None,
        device_class: Optional[str] = None,
        expire_after: Optional[int] = 0,
        force_update: Optional[bool] = False,
        off_delay: Optional[int] = None,
        icon: str = "",
        state_class: Optional[str] = None,
        object_id: Optional[str] = None,
    ):
        """Create a new MQTT binary sensor entity object."""
        # MqttEntity.__init__(self, name, mqtt_discovery_root_topic, logger, device_payload)
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
        self._device_class = device_class
        if (
            device_class is not None
            and device_class not in BINARY_SENSOR_DEVICE_CLASSES
        ):
            msg = f"Bad device class {device_class}. Should be in {BINARY_SENSOR_DEVICE_CLASSES}"
            self.logger.error(msg)
            raise MQTTHassBaseError(msg)
        self._expire_after = expire_after
        self._force_update = force_update
        self._off_delay = off_delay
        self._state_class = state_class
        self._icon = icon

    def register(self) -> None:
        """Register the current entity to Hass.

        Using the MQTT discovery feature of Home Assistant.
        """
        config_payload = {
            "availability": {
                "payload_available": "online",
                "payload_not_available": "offline",
                "topic": self.availability_topic,
            },
            "device": self.device_payload,
            "expire_after": self._expire_after,
            "force_update": self._force_update,
            "json_attributes_template": "",
            "json_attributes_topic": self.json_attributes_topic,
            "name": self.name,
            "payload_available": "online",
            "payload_not_available": "offline",
            "payload_off": "OFF",
            "payload_on": "ON",
            "qos": 0,
            "state_topic": self.state_topic,
            "unique_id": self.unique_id,
        }
        if self._device_class:
            config_payload["device_class"] = self._device_class
        if self._off_delay:
            config_payload["off_delay"] = self._off_delay
        if self._icon:
            config_payload["icon"] = self._icon
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

    def send_on(self, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Send the ON state of the sensor to Home Assistant."""
        self.send_state("ON", attributes=attributes)

    def send_off(self, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Send the OFF state of the sensor to Home Assistant."""
        self.send_state("OFF", attributes=attributes)
