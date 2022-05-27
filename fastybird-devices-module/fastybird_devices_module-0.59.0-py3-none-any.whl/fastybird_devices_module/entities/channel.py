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
Devices module channel entities module
"""

# Python base dependencies
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Library dependencies
from fastybird_metadata.devices_module import PropertyType
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload
from sqlalchemy import (
    BINARY,
    JSON,
    TEXT,
    VARCHAR,
    Column,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship

# Library libs
import fastybird_devices_module.entities  # pylint: disable=unused-import
from fastybird_devices_module.entities.base import (
    Base,
    EntityCreatedMixin,
    EntityUpdatedMixin,
)
from fastybird_devices_module.entities.property import PropertyMixin


class ChannelEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Channel entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_module_channels"

    __table_args__ = (
        Index("channel_identifier_idx", "channel_identifier"),
        UniqueConstraint("channel_identifier", "device_id", name="channel_identifier_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Device channels",
        },
    )

    col_channel_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="channel_id", default=uuid.uuid4
    )
    col_identifier: str = Column(VARCHAR(50), name="channel_identifier", nullable=False)  # type: ignore[assignment]
    col_name: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="channel_name", nullable=True, default=None
    )
    col_comment: Optional[str] = Column(  # type: ignore[assignment]
        TEXT, name="channel_comment", nullable=True, default=None
    )

    col_params: Optional[Dict] = Column(JSON, name="params", nullable=True)  # type: ignore[assignment]

    device_id: Optional[bytes] = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16),
        ForeignKey("fb_devices_module_devices.device_id", ondelete="CASCADE"),
        name="device_id",
        nullable=False,
    )

    properties: List["ChannelPropertyEntity"] = relationship(  # type: ignore[assignment]
        "ChannelPropertyEntity",
        back_populates="channel",
        cascade="delete, delete-orphan",
    )
    controls: List["ChannelControlEntity"] = relationship(  # type: ignore[assignment]
        "ChannelControlEntity",
        back_populates="channel",
        cascade="delete, delete-orphan",
    )

    device: "entities.device.DeviceEntity" = relationship(  # type: ignore[name-defined]
        "entities.device.DeviceEntity",
        back_populates="channels",
    )

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device: "entities.device.DeviceEntity",  # type: ignore[name-defined]
        identifier: str,
        name: Optional[str] = None,
        channel_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__()

        self.col_channel_id = channel_id.bytes if channel_id is not None else uuid.uuid4().bytes

        self.col_identifier = identifier
        self.col_name = name

        self.device = device

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Channel unique identifier"""
        return uuid.UUID(bytes=self.col_channel_id)

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Channel unique key"""
        return self.col_identifier

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Channel name"""
        return self.col_name

    # -----------------------------------------------------------------------------

    @name.setter
    def name(self, name: Optional[str]) -> None:
        """Channel name setter"""
        self.col_name = name

    # -----------------------------------------------------------------------------

    @property
    def comment(self) -> Optional[str]:
        """Channel comment"""
        return self.col_comment

    # -----------------------------------------------------------------------------

    @comment.setter
    def comment(self, comment: Optional[str]) -> None:
        """Channel comment setter"""
        self.col_comment = comment

    # -----------------------------------------------------------------------------

    @property
    def params(self) -> Dict:
        """Channel params"""
        return self.col_params if self.col_params is not None else {}

    # -----------------------------------------------------------------------------

    @params.setter
    def params(self, params: Optional[Dict]) -> None:
        """Channel params"""
        self.col_params = params

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List[str], Dict, None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "id": self.id.__str__(),
                "identifier": self.identifier,
                "name": self.name,
                "comment": self.comment,
                "device": uuid.UUID(bytes=self.device_id).__str__(),
                "owner": self.device.owner,
            },
        }


class ChannelPropertyEntity(EntityCreatedMixin, EntityUpdatedMixin, PropertyMixin, Base):
    """
    Channel property entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_module_channels_properties"

    __table_args__ = (
        Index("property_identifier_idx", "property_identifier"),
        Index("property_settable_idx", "property_settable"),
        Index("property_queryable_idx", "property_queryable"),
        UniqueConstraint("property_identifier", "channel_id", name="property_identifier_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Device channels properties",
        },
    )

    col_type: str = Column(VARCHAR(20), name="property_type", nullable=False)  # type: ignore[assignment]

    col_property_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="property_id", default=uuid.uuid4
    )

    channel_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_devices_module_channels.channel_id"), name="channel_id", nullable=False
    )

    parent_id: Optional[bytes] = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16),
        ForeignKey("fb_devices_module_channels_properties.property_id", ondelete="SET NULL"),
        name="parent_id",
        nullable=True,
    )

    channel: ChannelEntity = relationship(ChannelEntity, back_populates="properties")  # type: ignore[assignment]

    children: List["ChannelPropertyEntity"] = relationship(  # type: ignore[assignment]
        "ChannelPropertyEntity", backref=backref("parent", remote_side=[col_property_id])
    )

    __mapper_args__ = {
        "polymorphic_identity": "channel_property",
        "polymorphic_on": col_type,
    }

    # -----------------------------------------------------------------------------

    def __init__(self, channel: ChannelEntity, identifier: str, property_id: Optional[uuid.UUID] = None) -> None:
        super().__init__(identifier, property_id)

        self.channel = channel

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> PropertyType:
        """Property type"""

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Property settable status"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            return self.parent.settable  # type: ignore[no-any-return]

        return super().settable

    # -----------------------------------------------------------------------------

    @settable.setter
    def settable(self, settable: bool) -> None:
        """Property settable setter"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            raise AttributeError("Settable setter is allowed only for parent")

        super(ChannelPropertyEntity, type(self)).settable.fset(self, settable)  # type: ignore[attr-defined]

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Property queryable status"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            return self.parent.queryable  # type: ignore[no-any-return]

        return super().queryable

    # -----------------------------------------------------------------------------

    @queryable.setter
    def queryable(self, queryable: bool) -> None:
        """Property queryable setter"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            raise AttributeError("Queryable setter is allowed only for parent")

        super(ChannelPropertyEntity, type(self)).queryable.fset(self, queryable)  # type: ignore[attr-defined]

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Transform data type to enum value"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            return self.parent.data_type  # type: ignore[no-any-return]

        return super().data_type

    # -----------------------------------------------------------------------------

    @data_type.setter
    def data_type(self, data_type: DataType) -> None:
        """Data type setter"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            raise AttributeError("Data type setter is allowed only for parent")

        super(ChannelPropertyEntity, type(self)).data_type.fset(self, data_type)  # type: ignore[attr-defined]

    # -----------------------------------------------------------------------------

    @property
    def unit(self) -> Optional[str]:
        """Property unit"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            return self.parent.unit  # type: ignore[no-any-return]

        return super().unit

    # -----------------------------------------------------------------------------

    @unit.setter
    def unit(self, unit: Optional[str]) -> None:
        """Property unit setter"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            raise AttributeError("Unit setter is allowed only for parent")

        super(ChannelPropertyEntity, type(self)).unit.fset(self, unit)  # type: ignore[attr-defined]

    # -----------------------------------------------------------------------------

    @property
    def format(
        self,
    ) -> Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ]:
        """Property format"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            return self.parent.format  # type: ignore[no-any-return]

        return super().format

    # -----------------------------------------------------------------------------

    @format.setter
    def format(
        self,
        value_format: Union[
            str,
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ],
    ) -> None:
        """Property format setter"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            raise AttributeError("Value format setter is allowed only for parent")

        super(ChannelPropertyEntity, type(self)).format.fset(self, value_format)  # type: ignore[attr-defined]

    # -----------------------------------------------------------------------------

    @property
    def invalid(self) -> Union[str, int, float, None]:
        """Property invalid value"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            return self.parent.invalid  # type: ignore[no-any-return]

        return super().invalid

    # -----------------------------------------------------------------------------

    @invalid.setter
    def invalid(self, invalid: str) -> None:
        """Property invalid value setter"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            raise AttributeError("Invalid value setter is allowed only for parent")

        super(ChannelPropertyEntity, type(self)).invalid.fset(self, invalid)  # type: ignore[attr-defined]

    # -----------------------------------------------------------------------------

    @property
    def number_of_decimals(self) -> Optional[int]:
        """Property value number of decimals"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            return self.parent.number_of_decimals  # type: ignore[no-any-return]

        return super().number_of_decimals

    # -----------------------------------------------------------------------------

    @number_of_decimals.setter
    def number_of_decimals(self, number_of_decimals: Optional[int]) -> None:
        """Property value number of decimals setter"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            raise AttributeError("Number of decimals setter is allowed only for parent")

        super(ChannelPropertyEntity, type(self)).number_of_decimals.fset(  # type: ignore[attr-defined]
            self, number_of_decimals
        )

    # -----------------------------------------------------------------------------

    @property
    def default(self) -> Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property default"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            return self.parent.default  # type: ignore[no-any-return]

        return super().default

    # -----------------------------------------------------------------------------

    @default.setter
    def default(self, default: Optional[str]) -> None:
        """Property default value setter"""
        if self.parent is not None and not self.type.__eq__(PropertyType.MAPPED):
            raise AttributeError("Default value setter is allowed only for parent")

        super(ChannelPropertyEntity, type(self)).default.fset(self, default)  # type: ignore[attr-defined]

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[
        str,
        Union[
            int,
            float,
            str,
            bool,
            datetime,
            ButtonPayload,
            SwitchPayload,
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            List[str],
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            None,
        ],
    ]:
        """Transform entity to dictionary"""
        children: List[str] = []

        for child in self.children:
            children.append(child.id.__str__())

        return {
            **super().to_dict(),
            **{
                "channel": uuid.UUID(bytes=self.channel_id).__str__(),
                "parent": uuid.UUID(bytes=self.parent_id).__str__() if self.parent_id is not None else None,
                "children": children,
                "owner": self.channel.device.owner,
            },
        }


class ChannelDynamicPropertyEntity(ChannelPropertyEntity):
    """
    Channel property entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "dynamic"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.DYNAMIC


class ChannelStaticPropertyEntity(ChannelPropertyEntity):
    """
    Channel property entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "static"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.STATIC

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property value"""
        if self.parent is not None:
            return self.parent.value  # type: ignore[no-any-return]

        return super().value

    # -----------------------------------------------------------------------------

    @value.setter
    def value(self, value: Optional[str]) -> None:
        """Property value number of decimals setter"""
        if self.parent is not None:
            raise AttributeError("Value setter is allowed only for parent")

        super(ChannelStaticPropertyEntity, type(self)).value.fset(self, value)  # type: ignore[attr-defined]

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[
        str,
        Union[
            int,
            float,
            str,
            bool,
            datetime,
            ButtonPayload,
            SwitchPayload,
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            List[str],
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            None,
        ],
    ]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "value": self.value,
                "default": self.default,
            },
        }


class ChannelMappedPropertyEntity(ChannelPropertyEntity):
    """
    Channel property entity

    @package        FastyBird:DevicesModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "mapped"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.MAPPED

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[
        str,
        Union[
            int,
            float,
            str,
            bool,
            datetime,
            ButtonPayload,
            SwitchPayload,
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            List[str],
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            None,
        ],
    ]:
        """Transform entity to dictionary"""
        if isinstance(self.parent, ChannelStaticPropertyEntity):
            return {
                **super().to_dict(),
                **{
                    "value": self.value,
                    "default": self.default,
                },
            }

        return super().to_dict()


class ChannelControlEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Channel control entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_module_channels_controls"

    __table_args__ = (
        Index("control_name_idx", "control_name"),
        UniqueConstraint("control_name", "channel_id", name="control_name_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Device channels controls",
        },
    )

    col_control_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="control_id", default=uuid.uuid4
    )
    col_name: str = Column(VARCHAR(100), name="control_name", nullable=False)  # type: ignore[assignment]

    channel_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16),
        ForeignKey("fb_devices_module_channels.channel_id", ondelete="CASCADE"),
        name="channel_id",
        nullable=False,
    )

    channel: ChannelEntity = relationship(ChannelEntity, back_populates="controls")  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, name: str, channel: ChannelEntity, control_id: Optional[uuid.UUID] = None) -> None:
        super().__init__()

        self.col_control_id = control_id.bytes if control_id is not None else uuid.uuid4().bytes

        self.col_name = name

        self.channel = channel

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Control unique identifier"""
        return uuid.UUID(bytes=self.col_control_id)

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Control name"""
        return self.col_name

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, str]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "id": self.id.__str__(),
                "name": self.name,
                "channel": uuid.UUID(bytes=self.channel_id).__str__(),
                "owner": self.channel.device.owner,
            },
        }
