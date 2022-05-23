import logging

from sqlalchemy import Column, DateTime, BigInteger, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.schema import Index, ForeignKey
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class EventDBEventTable(Tuple, DeclarativeBase):
    __tablename__ = "EventDBEvent"
    __tupleType__ = eventdbTuplePrefix + "EventDBEventTable"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    dateTime = Column(DateTime(True), primary_key=True, nullable=False)

    value = Column(JSONB, nullable=False)

    key = Column(String)

    isAlarm = Column(Boolean)

    modelSetId = Column(
        Integer, ForeignKey("EventDBModelSet.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        Index("idx_EventDBEvent_modelSetId_key", modelSetId, key, unique=False),
    )
