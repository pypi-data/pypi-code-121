import logging

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class DeviceUpdateTuple(Tuple, DeclarativeBase):
    """DeviceUpdateTuple

    This table stores information about the peek device updates.

    """

    __tablename__ = "DeviceUpdate"
    __tupleType__ = deviceTuplePrefix + "DeviceUpdateTuple"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deviceType = Column(String(20), nullable=False)
    description = Column(String, nullable=False)
    buildDate = Column(DateTime(True), nullable=False)
    appVersion = Column(String(15), nullable=False)
    updateVersion = Column(String(15), nullable=False)
    filePath = Column(String(150), nullable=False)
    urlPath = Column(String(150), nullable=False)
    fileSize = Column(Integer, nullable=False)
    isEnabled = Column(Boolean, nullable=False, server_default="0")

    __table_args__ = (
        Index(
            "idx_DeviceUpdate_Version",
            deviceType,
            appVersion,
            updateVersion,
            unique=True,
        ),
    )
