from sqlalchemy import Column
from sqlalchemy import Integer, String
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_docdb_generic_menu._private.PluginNames import (
    docDbGenericMenuTuplePrefix,
)
from peek_plugin_docdb_generic_menu._private.storage.DeclarativeBase import (
    DeclarativeBase,
)


@addTupleType
class DocDbGenericMenuTuple(Tuple, DeclarativeBase):
    __tupleType__ = docDbGenericMenuTuplePrefix + "DocDbGenericMenuTuple"
    __tablename__ = "Menu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    modelSetKey = Column(String)
    coordSetKey = Column(String)
    faIcon = Column(String)
    title = Column(String)
    tooltip = Column(String)
    url = Column(String, nullable=False)
    showCondition = Column(String, nullable=True)
