from sqlalchemy import Column, ForeignKey, Boolean, Index
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from vortex.Tuple import addTupleType, Tuple, TupleField

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix
from .DeclarativeBase import DeclarativeBase
from .EventDBModelSetTable import EventDBModelSetTable
from ...tuples.EventDBPropertyTuple import EventDBPropertyTuple


@addTupleType
class EventDBPropertyTable(Tuple, DeclarativeBase):
    __tablename__ = "EventDBProperty"
    __tupleType__ = eventdbTuplePrefix + "EventDBPropertyTable"

    SHOW_FILTER_AS_FREE_TEXT = 1
    SHOW_FILTER_SELECT_MANY = 2
    SHOW_FILTER_SELECT_ONE = 3

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(
        Integer, ForeignKey("EventDBModelSet.id", ondelete="CASCADE"), nullable=False
    )
    modelSet = relationship(EventDBModelSetTable)

    key = Column(String, nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    comment = Column(String)

    useForFilter = Column(Boolean)
    useForDisplay = Column(Boolean)
    useForPopup = Column(Boolean)
    showFilterAs = Column(Integer)

    displayByDefaultOnSummaryView = Column(Boolean)
    displayByDefaultOnDetailView = Column(Boolean)

    valuesFromAdminUi = TupleField()

    __table_args__ = (
        Index("idx_EventDBProp_name", modelSetId, key, unique=True),
        Index("idx_EventDBProp_value", modelSetId, name, unique=True),
    )

    def toTuple(self) -> EventDBPropertyTuple:
        return EventDBPropertyTuple(
            modelSetKey=self.modelSet.key,
            key=self.key,
            name=self.name,
            order=self.order,
            comment=self.comment,
            useForFilter=self.useForFilter,
            useForDisplay=self.useForDisplay,
            useForPopup=self.useForPopup,
            displayByDefaultOnSummaryView=self.displayByDefaultOnSummaryView,
            displayByDefaultOnDetailView=self.displayByDefaultOnDetailView,
            showFilterAs=self.showFilterAs,
            values=[v.toTuple() for v in self.values],
        )
