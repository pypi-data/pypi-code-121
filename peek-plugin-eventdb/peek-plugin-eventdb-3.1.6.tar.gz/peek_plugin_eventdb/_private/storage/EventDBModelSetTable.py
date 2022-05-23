from sqlalchemy import Column
from sqlalchemy import Integer, String
from vortex.Tuple import addTupleType, Tuple

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix
from .DeclarativeBase import DeclarativeBase


@addTupleType
class EventDBModelSetTable(Tuple, DeclarativeBase):
    __tablename__ = "EventDBModelSet"
    __tupleType__ = eventdbTuplePrefix + "EventDBModelSetTable"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    comment = Column(String)

    propsJson = Column(String)


def getOrCreateEventDBModelSet(session, modelSetKey: str) -> EventDBModelSetTable:
    qry = session.query(EventDBModelSetTable).filter(
        EventDBModelSetTable.key == modelSetKey
    )
    if not qry.count():
        session.add(EventDBModelSetTable(key=modelSetKey, name=modelSetKey))
        session.commit()

    return qry.one()
