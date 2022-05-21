"""MQTT Lock entity module."""
import json
import logging
from typing import Any, Dict, Optional, Union

from mqtt_hass_base.entity.common import EntitySettingsType, MqttEntity
from mqtt_hass_base.error import MQTTHassBaseError

LOCK_STATES = {
    "unlocked": "UNLOCKED",
    "UNLOCKED": "UNLOCKED",
    "unlock": "UNLOCKED",
    "UNLOCK": "UNLOCKED",
    "locked": "LOCKED",
    "LOCKED": "LOCKED",
    "lock": "LOCKED",
    "LOCK": "LOCKED",
}


class LockSettingsType(EntitySettingsType, total=False):
    """Lock entity settings dict format."""

    icon: str
    optimistic: bool


class MqttLock(MqttEntity):
    """MQTT Lock entity class."""

    _component = "lock"

    def __init__(
        self,
        name: str,
        unique_id: str,
        mqtt_discovery_root_topic: str,
        mqtt_data_root_topic: str,
        logger: logging.Logger,
        device_payload: Dict[str, str],
        subscriptions: Dict[str, str],
        icon: str,
        optimistic: bool,
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
            subscriptions,
            object_id=object_id,
        )
        self._icon = icon
        self._optimistic = optimistic

    def register(self) -> None:
        """Register the current entity to Hass.

        Using the MQTT discovery feature of Home Assistant.
        """
        config_payload = {
            "availability": {
                "payload_available": "online",
                "payload_not_available": "offline",
                "topic": self.availability_topic,  # required
            },
            "command_topic": self.command_topic,
            "device": self.device_payload,
            # "enabled_by_default": self._enabled_by_default,
            "icon": self._icon,
            # "json_attributes_template": "",
            "json_attributes_topic": self.json_attributes_topic,
            "name": self.name,
            "optimistic": self._optimistic,
            # "payload_lock": "LOCK",
            # "payload_unlock": "UNLOCK",
            "qos": 0,
            "retain": False,
            "state_locked": "LOCKED",
            "state_topic": self.state_topic,
            "state_unlocked": "UNLOCKED",
            "unique_id": self._unique_id,
        }

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
        """Send the current state of the switch to Home Assistant."""
        if state not in LOCK_STATES:
            msg = f"Bad lock state {state!s}. Should be in {LOCK_STATES}"
            self.logger.error(msg)
            raise MQTTHassBaseError(msg)
        payload = LOCK_STATES.get(str(state))
        self._mqtt_client.publish(topic=self.state_topic, retain=True, payload=payload)
        if attributes is not None:
            self.send_attributes(attributes)

    def send_locked(self, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Send the LOCKED state of the switch to Home Assistant."""
        self.send_state("LOCKED", attributes=attributes)

    def send_unlocked(self, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Send the UNLOCKED state of the switch to Home Assistant."""
        self.send_state("UNLOCKED", attributes=attributes)
