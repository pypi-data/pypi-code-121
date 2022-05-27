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
Devices module connector entities module
"""

# Python base dependencies
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Library dependencies
from fastybird_metadata.devices_module import PropertyType
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from sqlalchemy import (
    BINARY,
    BOOLEAN,
    JSON,
    TEXT,
    VARCHAR,
    Column,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

# Library libs
import fastybird_devices_module.entities  # pylint: disable=unused-import
from fastybird_devices_module.entities.base import (
    Base,
    EntityCreatedMixin,
    EntityUpdatedMixin,
)
from fastybird_devices_module.entities.property import PropertyMixin


class ConnectorEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Connector entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_module_connectors"

    __table_args__ = (
        Index("connector_identifier_idx", "connector_identifier"),
        Index("connector_name_idx", "connector_name"),
        Index("connector_enabled_idx", "connector_enabled"),
        UniqueConstraint("connector_identifier", name="connector_identifier_connector_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Connectors",
        },
    )

    col_type: str = Column(VARCHAR(40), name="connector_type", nullable=False)  # type: ignore[assignment]

    col_connector_id: bytes = Column(BINARY(16), primary_key=True, name="connector_id")  # type: ignore[assignment]
    col_identifier: str = Column(VARCHAR(50), name="connector_identifier", nullable=False)  # type: ignore[assignment]
    col_name: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="connector_name", nullable=True, default=None
    )
    col_comment: Optional[str] = Column(  # type: ignore[assignment]
        TEXT, name="connector_comment", nullable=True, default=None
    )
    col_enabled: bool = Column(  # type: ignore[assignment]
        BOOLEAN, name="connector_enabled", nullable=False, default=True
    )

    col_owner: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(50), name="owner", nullable=True, default=None
    )

    col_params: Optional[Dict] = Column(JSON, name="params", nullable=True)  # type: ignore[assignment]

    properties: List["ConnectorPropertyEntity"] = relationship(  # type: ignore[assignment]
        "ConnectorPropertyEntity",
        back_populates="connector",
        cascade="delete, delete-orphan",
    )
    controls: List["ConnectorControlEntity"] = relationship(  # type: ignore[assignment]
        "ConnectorControlEntity",
        back_populates="connector",
        cascade="delete, delete-orphan",
    )
    devices: List["entities.device.DeviceEntity"] = relationship(  # type: ignore[assignment,name-defined]
        "entities.device.DeviceEntity",
        back_populates="connector",
    )

    __mapper_args__ = {
        "polymorphic_identity": "connector",
        "polymorphic_on": col_type,
    }

    # -----------------------------------------------------------------------------

    def __init__(self, identifier: str, name: Optional[str] = None, connector_id: Optional[uuid.UUID] = None) -> None:
        super().__init__()

        self.col_connector_id = connector_id.bytes if connector_id is not None else uuid.uuid4().bytes

        self.col_identifier = identifier
        self.col_name = name

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> str:
        """Connector type"""

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Connector unique identifier"""
        return uuid.UUID(bytes=self.col_connector_id)

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Device unique key"""
        return self.col_identifier

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Device name"""
        return self.col_name

    # -----------------------------------------------------------------------------

    @name.setter
    def name(self, name: Optional[str]) -> None:
        """Device name setter"""
        self.col_name = name

    # -----------------------------------------------------------------------------

    @property
    def comment(self) -> Optional[str]:
        """Device comment"""
        return self.col_comment

    # -----------------------------------------------------------------------------

    @comment.setter
    def comment(self, comment: Optional[str]) -> None:
        """Device comment setter"""
        self.col_comment = comment

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Connector enabled status"""
        return self.col_enabled

    # -----------------------------------------------------------------------------

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Connector enabled setter"""
        self.col_enabled = enabled

    # -----------------------------------------------------------------------------

    @property
    def owner(self) -> Optional[str]:
        """Connector owner identifier"""
        return self.col_owner

    # -----------------------------------------------------------------------------

    @owner.setter
    def owner(self, owner: Optional[str]) -> None:
        """Connector owner identifier setter"""
        self.col_owner = owner

    # -----------------------------------------------------------------------------

    @property
    def params(self) -> Dict:
        """Connector params"""
        return self.col_params if self.col_params is not None else {}

    # -----------------------------------------------------------------------------

    @params.setter
    def params(self, params: Optional[Dict]) -> None:
        """Connector params"""
        self.col_params = params

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, bool, List[str], None]]:
        """Transform entity to dictionary"""
        return {
            "id": self.id.__str__(),
            "type": self.type,
            "identifier": self.identifier,
            "name": self.name,
            "comment": self.comment,
            "enabled": self.enabled,
            "owner": self.owner,
        }


class BlankConnectorEntity(ConnectorEntity):
    """
    Blank connector entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "blank"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Connector type"""
        return "blank"


class ConnectorPropertyEntity(EntityCreatedMixin, EntityUpdatedMixin, PropertyMixin, Base):
    """
    Connector property entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_module_connectors_properties"

    __table_args__ = (
        Index("property_identifier_idx", "property_identifier"),
        Index("property_settable_idx", "property_settable"),
        Index("property_queryable_idx", "property_queryable"),
        UniqueConstraint("property_identifier", "connector_id", name="property_identifier_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Connectors properties",
        },
    )

    col_type: str = Column(VARCHAR(20), name="property_type", nullable=False)  # type: ignore[assignment]

    col_property_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="property_id", default=uuid.uuid4
    )

    connector_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_devices_module_connectors.connector_id"), name="connector_id", nullable=False
    )

    connector: ConnectorEntity = relationship(ConnectorEntity, back_populates="properties")  # type: ignore[assignment]

    __mapper_args__ = {
        "polymorphic_identity": "connector_property",
        "polymorphic_on": col_type,
    }

    # -----------------------------------------------------------------------------

    def __init__(self, connector: ConnectorEntity, identifier: str, property_id: Optional[uuid.UUID] = None) -> None:
        super().__init__(identifier, property_id)

        self.connector = connector

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> PropertyType:
        """Property type"""

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
                "connector": uuid.UUID(bytes=self.connector_id).__str__(),
                "owner": self.connector.owner,
            },
        }


class ConnectorDynamicPropertyEntity(ConnectorPropertyEntity):
    """
    Connector property entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "dynamic"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.DYNAMIC


class ConnectorStaticPropertyEntity(ConnectorPropertyEntity):
    """
    Connector property entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "static"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.STATIC


class ConnectorControlEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Connector control entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_module_connectors_controls"

    __table_args__ = (
        Index("control_name_idx", "control_name"),
        UniqueConstraint("control_name", "connector_id", name="control_name_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Connectors controls",
        },
    )

    col_control_id: bytes = Column(BINARY(16), primary_key=True, name="control_id")  # type: ignore[assignment]
    col_name: str = Column(VARCHAR(100), name="control_name", nullable=False)  # type: ignore[assignment]

    connector_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16),
        ForeignKey("fb_devices_module_connectors.connector_id", ondelete="CASCADE"),
        name="connector_id",
        nullable=False,
    )

    connector: ConnectorEntity = relationship(ConnectorEntity, back_populates="controls")  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, name: str, connector: ConnectorEntity, control_id: Optional[uuid.UUID] = None) -> None:
        super().__init__()

        self.col_control_id = control_id.bytes if control_id is not None else uuid.uuid4().bytes

        self.col_name = name.lower()
        self.connector = connector

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

    def to_dict(self) -> Dict[str, Union[str, None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "id": self.id.__str__(),
                "name": self.name,
                "connector": uuid.UUID(bytes=self.connector_id).__str__(),
                "owner": self.connector.owner,
            },
        }
