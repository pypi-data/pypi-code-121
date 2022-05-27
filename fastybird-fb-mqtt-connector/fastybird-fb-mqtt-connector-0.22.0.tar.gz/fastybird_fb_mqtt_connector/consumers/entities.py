#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
FastyBird MQTT connector consumers module entities
"""

# Python base dependencies
import re
from abc import ABC
from typing import List, Optional, Set, Tuple, Union

# Library dependencies
from fastnumbers import fast_real
from fastybird_metadata.types import DataType

# Library libs
from fastybird_fb_mqtt_connector.exceptions import ParsePayloadException
from fastybird_fb_mqtt_connector.types import ExtensionType


def clean_name(name: str) -> str:
    """Clean name value"""
    return re.sub(r"[^A-Za-z0-9.,_ -]", "", name)


def clean_payload(payload: str) -> str:
    """Clean payload value"""
    return re.sub(r"[^A-Za-z0-9.:_°, %µ³/\"-]", "", payload)


class BaseEntity(ABC):
    """
    Base entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device: str
    __retained: bool = False

    # -----------------------------------------------------------------------------

    def __init__(self, device: str) -> None:
        self.__device = device

    # -----------------------------------------------------------------------------

    @property
    def device(self) -> str:
        """Entity device identifier"""
        return self.__device

    # -----------------------------------------------------------------------------

    @property
    def retained(self) -> bool:
        """Entity retained flag"""
        return self.__retained

    # -----------------------------------------------------------------------------

    @retained.setter
    def retained(self, retained: bool) -> None:
        """Entity retained flag setter"""
        self.__retained = retained


class AttributeEntity(BaseEntity):
    """
    Base attribute message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    NAME = "name"
    STATE = "state"
    PROPERTIES = "properties"
    CHANNELS = "channels"
    EXTENSIONS = "extensions"
    CONTROLS = "controls"

    __attribute: str
    __value: Union[str, List[str]]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device: str,
        attribute: str,
        value: str,
    ) -> None:
        if attribute not in self.allowed_attributes:
            raise AttributeError(f"Attribute '{attribute}' is not valid")

        super().__init__(device=device)

        self.__attribute = attribute
        self.__parse_value(value)

    # -----------------------------------------------------------------------------

    @property
    def attribute(self) -> str:
        """Entity attribute"""
        return self.__attribute

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[str, List[str]]:
        """Entity value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @property
    def allowed_attributes(self) -> List[str]:
        """List of entity allowed attributes"""
        return []

    # -----------------------------------------------------------------------------

    def __parse_value(self, value: str) -> None:
        """Parse value against entity attribute type"""
        if self.attribute == self.NAME:
            self.__value = clean_name(value)

        elif self.attribute in (
            self.PROPERTIES,
            self.CHANNELS,
            self.EXTENSIONS,
            self.CONTROLS,
        ):
            cleaned_value = clean_payload(value)

            cleaned_value_parts = cleaned_value.strip().split(",")
            cleaned_value_parts = [item.strip() for item in cleaned_value_parts if item.strip()]

            self.__value = list(set(cleaned_value_parts))

        else:
            self.__value = clean_payload(value)


class DeviceAttributeEntity(AttributeEntity):
    """
    Device attribute message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @property
    def allowed_attributes(self) -> List[str]:
        """List of entity allowed attributes"""
        return [
            self.NAME,
            self.PROPERTIES,
            self.STATE,
            self.CHANNELS,
            self.EXTENSIONS,
            self.CONTROLS,
        ]


class ChannelAttributeEntity(AttributeEntity):
    """
    Channel attribute message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __channel: str

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device: str,
        channel: str,
        attribute: str,
        value: str,
    ) -> None:
        super().__init__(device=device, attribute=attribute, value=value)

        self.__channel = channel

    # -----------------------------------------------------------------------------

    @property
    def channel(self) -> str:
        """Entity channel identifier"""
        return self.__channel

    # -----------------------------------------------------------------------------

    @property
    def allowed_attributes(self) -> List[str]:
        """List of entity allowed attributes"""
        return [
            self.NAME,
            self.PROPERTIES,
            self.CONTROLS,
        ]


class ExtensionAttributeEntity(BaseEntity):
    """
    Device extension message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    MAC_ADDRESS = "mac-address"
    MANUFACTURER = "manufacturer"
    MODEL = "model"
    VERSION = "version"
    NAME = "name"

    __extension: ExtensionType
    __parameter: str
    __value: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device: str,
        extension: ExtensionType,
        parameter: str,
        value: str,
    ) -> None:
        if parameter not in self.allowed_parameters:
            raise AttributeError(f"Hardware attribute '{parameter}' is not valid")

        super().__init__(device=device)

        self.__extension = extension
        self.__parameter = parameter
        self.__value = clean_payload(value)

    # -----------------------------------------------------------------------------

    @property
    def extension(self) -> ExtensionType:
        """Entity extension"""
        return self.__extension

    # -----------------------------------------------------------------------------

    @property
    def parameter(self) -> str:
        """Entity parameter"""
        return self.__parameter

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> str:
        """Entity parameter value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @property
    def allowed_parameters(self) -> List[str]:
        """List of entity allowed parameters"""
        return [
            self.MAC_ADDRESS,
            self.MANUFACTURER,
            self.MODEL,
            self.VERSION,
            self.NAME,
        ]


class HardwareEntity(BaseEntity):
    """
    Device hardware message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    MAC_ADDRESS = "mac-address"
    MANUFACTURER = "manufacturer"
    MODEL = "model"
    VERSION = "version"

    __parameter: str
    __value: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device: str,
        parameter: str,
        value: str,
    ) -> None:
        if parameter not in self.allowed_parameters:
            raise AttributeError(f"Hardware attribute '{parameter}' is not valid")

        super().__init__(device=device)

        self.__parameter = parameter
        self.__value = clean_payload(value)

    # -----------------------------------------------------------------------------

    @property
    def parameter(self) -> str:
        """Entity parameter"""
        return self.__parameter

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> str:
        """Entity parameter value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @property
    def allowed_parameters(self) -> List[str]:
        """List of entity allowed parameters"""
        return [
            self.MAC_ADDRESS,
            self.MANUFACTURER,
            self.MODEL,
            self.VERSION,
        ]


class FirmwareEntity(BaseEntity):
    """
    Device firmware message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    MANUFACTURER = "manufacturer"
    VERSION = "version"

    __parameter: str
    __value: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device: str,
        parameter: str,
        value: str,
    ) -> None:
        if parameter not in self.allowed_parameters:
            raise AttributeError(f"Firmware attribute '{parameter}' is not valid")

        super().__init__(device=device)

        self.__parameter = parameter
        self.__value = clean_payload(value)

    # -----------------------------------------------------------------------------

    @property
    def parameter(self) -> str:
        """Entity parameter"""
        return self.__parameter

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> str:
        """Entity parameter value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @property
    def allowed_parameters(self) -> List[str]:
        """List of entity allowed parameters"""
        return [
            self.MANUFACTURER,
            self.VERSION,
        ]


class PropertyEntity(BaseEntity):
    """
    Base property message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __name: str
    __value: Optional[str] = None
    __attributes: Set["PropertyAttributeEntity"] = set()

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device: str,
        name: str,
    ) -> None:
        super().__init__(device=device)

        self.__name = name
        self.__attributes = set()

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Entity name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Optional[str]:
        """Entity value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @value.setter
    def value(self, value: str) -> None:
        """Entity value setter"""
        self.__value = value

    # -----------------------------------------------------------------------------

    @property
    def attributes(self) -> Set["PropertyAttributeEntity"]:
        """List of entity attributes"""
        return self.__attributes

    # -----------------------------------------------------------------------------

    def add_attribute(self, attribute: "PropertyAttributeEntity") -> None:
        """Validate and create property attribute"""
        self.__attributes.add(attribute)


class DevicePropertyEntity(PropertyEntity):
    """
    Device property message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class ChannelPropertyEntity(PropertyEntity):
    """
    Channel property message entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __channel: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device: str,
        channel: str,
        name: str,
    ) -> None:
        super().__init__(device=device, name=name)

        self.__channel = channel

    # -----------------------------------------------------------------------------

    @property
    def channel(self) -> str:
        """Entity channel identifier"""
        return self.__channel


class PropertyAttributeEntity(ABC):
    """
    Property attribute entity

    @package        FastyBird:FbMqttConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    NAME = "name"
    SETTABLE = "settable"
    QUERYABLE = "queryable"
    DATA_TYPE = "data-type"
    FORMAT = "format"
    UNIT = "unit"

    FORMAT_ALLOWED_PAYLOADS = [
        "rgb",
        "hsv",
    ]

    __attribute: str
    __value: Union[
        str, bool, Tuple[float, float], List[Union[str, Tuple[str, Optional[str], Optional[str]]]], DataType, None
    ] = None

    # -----------------------------------------------------------------------------

    def __init__(self, attribute: str, value: str) -> None:
        if attribute not in self.allowed_attributes:
            raise AttributeError(f"Property attribute: '{attribute}' is not valid")

        self.__attribute = attribute
        self.__parse_value(value=value)

    # -----------------------------------------------------------------------------

    @property
    def attribute(self) -> str:
        """Entity attribute"""
        return self.__attribute

    # -----------------------------------------------------------------------------

    @property
    def value(
        self,
    ) -> Union[
        str, bool, DataType, Tuple[float, float], List[Union[str, Tuple[str, Optional[str], Optional[str]]]], None
    ]:
        """Entity value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @property
    def allowed_attributes(self) -> List[str]:
        """List of entity allowed attributes"""
        return [
            self.NAME,
            self.SETTABLE,
            self.QUERYABLE,
            self.DATA_TYPE,
            self.FORMAT,
            self.UNIT,
        ]

    # -----------------------------------------------------------------------------

    def __parse_value(self, value: str) -> None:  # pylint: disable=too-many-branches
        cleaned_value = clean_payload(value)

        if self.attribute in (PropertyAttributeEntity.NAME, PropertyAttributeEntity.UNIT):
            if self.attribute == PropertyAttributeEntity.NAME:
                self.__value = clean_name(cleaned_value)

            else:
                self.__value = cleaned_value

            if cleaned_value == "":
                self.__value = None

        elif self.attribute in (
            PropertyAttributeEntity.SETTABLE,
            PropertyAttributeEntity.QUERYABLE,
        ):
            self.__value = cleaned_value.lower() == "true"

        elif self.attribute == PropertyAttributeEntity.DATA_TYPE:
            if not DataType.has_value(cleaned_value):
                raise ParsePayloadException("Provided payload is not valid")

            self.__value = DataType(cleaned_value)

        elif self.attribute == PropertyAttributeEntity.FORMAT:
            if len(re.findall(r"([a-zA-Z0-9]+)?:([a-zA-Z0-9]+)?", cleaned_value)) == 1:
                start, end = re.findall(r"([a-zA-Z0-9]+)?:([a-zA-Z0-9]+)?", cleaned_value).pop()

                if start and start.isnumeric() is False:
                    raise ParsePayloadException("Provided payload is not valid")

                if end and end.isnumeric() is False:
                    raise ParsePayloadException("Provided payload is not valid")

                start = fast_real(start) if start else None
                end = fast_real(end) if end else None

                if start and end and start > end:
                    raise ParsePayloadException("Provided payload is not valid")

                self.__value = start, end

            elif "," in cleaned_value:
                cleaned_value_parts = cleaned_value.strip().split(",")
                cleaned_value_parts = [item.strip() for item in cleaned_value_parts if item.strip()]

                self.__value = list(set(cleaned_value_parts))

            elif cleaned_value in ("none", ""):
                self.__value = None

            elif cleaned_value not in PropertyAttributeEntity.FORMAT_ALLOWED_PAYLOADS:
                raise ParsePayloadException("Provided payload is not valid")

            else:
                self.__value = cleaned_value

        else:
            self.__value = None if cleaned_value == "none" or cleaned_value is False else cleaned_value
