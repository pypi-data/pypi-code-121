"""MQTT Hass Base."""
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import paho.mqtt.client as mqtt

from mqtt_hass_base import entity as mqtt_entity
from mqtt_hass_base.error import MQTTHassBaseError

ENTITY_TYPES = (
    "switch",
    "lock",
    "light",
    "binarysensor",
    "sensor",
    "vacuum",
)


class MqttDevice:
    """Mqtt device base class."""

    _entities: List[mqtt_entity.MqttEntity] = []

    def __init__(
        self,
        name: str,
        logger: logging.Logger,
        mqtt_discovery_root_topic: str,
        mqtt_data_root_topic: str,
    ):
        """Create a new device."""
        # Get logger
        self.logger = logger.getChild(name)
        self._name = name
        self.mqtt_discovery_root_topic = mqtt_discovery_root_topic
        self.mqtt_data_root_topic = mqtt_data_root_topic
        self._entities: List[mqtt_entity.MqttEntity] = []
        self._model: Optional[str] = None
        self._manufacturer: Optional[str] = None
        self._sw_version: Optional[str] = None
        self._via_device: Optional[str] = None
        self._identifiers: List[str] = []
        self._connections: Dict[str, str] = {}

    def __repr__(self) -> str:
        """Get repr of the current device."""
        return f"<{self.__class__.__name__} '{self.name}'>"

    @property
    def entities(self) -> List[mqtt_entity.MqttEntity]:
        """Get the list of the entities of the devices."""
        return self._entities

    def add_entity(
        self,
        entity_type: "str",
        name: str,
        unique_id: str,
        entity_settings: Union[
            mqtt_entity.BinarySensorSettingsType,
            mqtt_entity.SensorSettingsType,
            mqtt_entity.LightSettingsType,
            mqtt_entity.LockSettingsType,
            mqtt_entity.SwitchSettingsType,
            mqtt_entity.VacuumSettingsType,
        ],
        subscriptions: Optional[dict[str, str]] = None,
        sub_mqtt_topic: Optional[str] = None,
    ) -> mqtt_entity.MqttEntity:
        """Add a new entity in the device."""
        if entity_type.lower() not in ENTITY_TYPES:
            msg = (
                f"Entity type '{entity_type}' is not supported. "
                f"Supported types are: {ENTITY_TYPES}"
            )
            self.logger.error(msg)
            raise MQTTHassBaseError(msg)

        if sub_mqtt_topic:
            mqtt_data_root_topic = "/".join(
                (self.mqtt_data_root_topic, sub_mqtt_topic.strip("/"))
            )
        else:
            mqtt_data_root_topic = self.mqtt_data_root_topic

        self.logger.info("Adding entity %s - %s", entity_type, name)
        ent = getattr(mqtt_entity, "Mqtt" + entity_type.capitalize())(
            name=name,
            unique_id=unique_id,
            mqtt_discovery_root_topic=self.mqtt_discovery_root_topic,
            mqtt_data_root_topic=mqtt_data_root_topic,
            logger=self.logger,
            device_payload=self.config_device_payload,
            subscriptions=subscriptions,
            **entity_settings,
        )
        self._entities.append(ent)
        return ent

    def set_mqtt_client(self, mqtt_client: mqtt.Client) -> None:
        """Set the mqtt client to each entity."""
        for entity in self.entities:
            entity.set_mqtt_client(mqtt_client)

    def register(self) -> None:
        """Register all entities in MQTT."""
        self.logger.info("Registering entities for device %s", self.name)
        for entity in self.entities:
            entity.register()

    def subscribe(self) -> None:
        """Subscribe to the MQTT topic needed for each entity."""
        self.logger.info("Subscribing to input mqtt topics")
        for entity in self.entities:
            entity.subscribe()

    def unregister(self) -> None:
        """Unregister all entities from MQTT."""
        self.logger.info("Unregistering entities for device %s", self.name)
        for entity in self.entities:
            entity.unregister()

    @property
    def name(self) -> Optional[str]:
        """Return the name of the device."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if name != self._name:
            self.logger = self.logger.getChild("device").getChild(name)
        self._name = name

    @property
    def model(self) -> Optional[str]:
        """Return the module of the device."""
        return self._model

    @model.setter
    def model(self, model: str) -> None:
        self._model = model

    @property
    def manufacturer(self) -> Optional[str]:
        """Return the manufacturer of the device."""
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, manufacturer: str) -> None:
        self._manufacturer = manufacturer

    @property
    def sw_version(self) -> Optional[str]:
        """Return the software version of the device."""
        return self._sw_version

    @sw_version.setter
    def sw_version(self, sw_version: str) -> None:
        self._sw_version = sw_version

    @property
    def via_device(self) -> Optional[str]:
        """Return the intermediate device name of the current device."""
        return self._via_device

    @via_device.setter
    def via_device(self, via_device: str) -> None:
        self._via_device = via_device

    @property
    def identifiers(self) -> List[str]:
        """Return the identifiers of the device."""
        return self._identifiers

    @identifiers.setter
    def identifiers(self, id_: str) -> None:
        if id_ not in self._identifiers:
            self._identifiers.append(id_)

    @property
    def mac(self) -> Optional[str]:
        """Return the mac address of the device."""
        return self.connections.get("mac")

    @mac.setter
    def mac(self, value: str) -> None:
        self.add_connections({"mac": value})

    @property
    def connections(self) -> Dict[str, str]:
        """Return the connection list of the device."""
        return self._connections

    def add_connections(self, raw_item: Union[Dict[str, str], Tuple[str, str]]) -> None:
        """Add new connection(s) to the device config."""
        if isinstance(raw_item, dict):
            self._connections.update(raw_item)
        elif isinstance(raw_item, tuple):
            if len(raw_item) != 2:
                raise MQTTHassBaseError(
                    f"A connection needs 2 elements but it's: {raw_item}"
                )
            self._connections[raw_item[0]] = raw_item[1]
        else:
            raise MQTTHassBaseError(
                f"Bad connection value: {raw_item} - Shoube dict or tuple"
            )

    @property
    def config_device_payload(self) -> dict[str, Any]:
        """Return the configuration device payload.

        This is the payload needed to register an entity of the current
        device in Home Assistant (using MQTT discovery).
        """
        payload: Dict[str, Union[Optional[str], List[str], Dict[str, str]]] = {
            "name": self.name
        }
        if self.connections:
            payload["connections"] = self.connections
        if self.identifiers:
            payload["identifiers"] = self.identifiers
        if self.manufacturer:
            payload["manufacturer"] = self.manufacturer
        if self.model:
            payload["model"] = self.model
        if self.sw_version:
            payload["sw_version"] = self.sw_version
        if self.via_device:
            payload["via_device"] = self.via_device
        if "connections" not in payload and "identifiers" not in payload:
            msg = "You need to define identifiers or connections in the device attributes."
            self.logger.error(msg)
            raise MQTTHassBaseError(msg)
        return payload
