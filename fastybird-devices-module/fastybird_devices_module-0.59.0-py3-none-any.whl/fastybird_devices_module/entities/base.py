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
Devices module base entities module
"""

# Python base dependencies
import datetime
from typing import Dict, Optional, Union

# Library dependencies
from fastybird_metadata.types import ConnectorSource, ModuleSource, PluginSource
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base

OrmBase = declarative_base()


class Base(OrmBase):  # type: ignore[misc,valid-type]  # pylint: disable=too-few-public-methods
    """
    Base entity

    @package        FastyBird:DevicesModule!
    @module         entities/base

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __abstract__ = True

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict:  # pylint: disable=no-self-use
        """Transform entity to dictionary"""
        return {}

    # -----------------------------------------------------------------------------

    @property
    def source(self) -> Union[ModuleSource, ConnectorSource, PluginSource]:
        """Entity source type"""
        return ModuleSource.DEVICES_MODULE


class EntityCreatedMixin:  # pylint: disable=too-few-public-methods
    """
    Timestamp creating entity

    @package        FastyBird:DevicesModule!
    @module         entities/base

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    col_created_at: Optional[datetime.datetime] = Column(  # type: ignore[assignment]
        DateTime, name="created_at", nullable=True, default=None
    )

    # -----------------------------------------------------------------------------

    @property
    def created_at(self) -> Optional[datetime.datetime]:
        """Entity created timestamp"""
        return self.col_created_at

    # -----------------------------------------------------------------------------

    @created_at.setter
    def created_at(self, created_at: Optional[datetime.datetime]) -> None:
        """Entity created timestamp setter"""
        self.col_created_at = created_at


class EntityUpdatedMixin:  # pylint: disable=too-few-public-methods
    """
    Timestamp updating entity

    @package        FastyBird:DevicesModule!
    @module         entities/base

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    col_updated_at: Optional[datetime.datetime] = Column(  # type: ignore[assignment]
        DateTime, name="updated_at", nullable=True, default=None
    )

    # -----------------------------------------------------------------------------

    @property
    def updated_at(self) -> Optional[datetime.datetime]:
        """Entity updated timestamp"""
        return self.col_updated_at

    # -----------------------------------------------------------------------------

    @updated_at.setter
    def updated_at(self, updated_at: Optional[datetime.datetime]) -> None:
        """Entity updated timestamp setter"""
        self.col_updated_at = updated_at
