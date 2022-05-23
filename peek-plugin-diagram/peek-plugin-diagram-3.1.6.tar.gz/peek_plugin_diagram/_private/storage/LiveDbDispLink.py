import logging
from sqlalchemy import Column, orm, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index, Sequence
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_livedb.tuples.LiveDbDisplayValueTuple import LiveDbDisplayValueTuple
from .DeclarativeBase import DeclarativeBase
from .Display import DispBase
from .ModelSet import ModelCoordSet

logger = logging.getLogger(__name__)

LIVE_DB_KEY_DATA_TYPE_BY_DISP_ATTR = {
    "colorId": LiveDbDisplayValueTuple.DATA_TYPE_COLOR,
    "fillColorId": LiveDbDisplayValueTuple.DATA_TYPE_COLOR,
    "lineColorId": LiveDbDisplayValueTuple.DATA_TYPE_COLOR,
    "fillPercent": LiveDbDisplayValueTuple.DATA_TYPE_NUMBER_VALUE,
    "lineStyleId": LiveDbDisplayValueTuple.DATA_TYPE_LINE_STYLE,
    "lineWidth": LiveDbDisplayValueTuple.DATA_TYPE_LINE_WIDTH,
    "text": LiveDbDisplayValueTuple.DATA_TYPE_STRING_VALUE,
    "targetDispGroupId": LiveDbDisplayValueTuple.DATA_TYPE_GROUP_PTR,
}


@addTupleType
class LiveDbDispLink(Tuple, DeclarativeBase):
    __tupleTypeShort__ = "LDL"
    __tablename__ = "LiveDbDispLink"
    __tupleType__ = diagramTuplePrefix + __tablename__

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    coordSetId = Column(
        Integer, ForeignKey("ModelCoordSet.id", ondelete="CASCADE"), nullable=False
    )
    coordSet = relationship(ModelCoordSet)

    dispId = Column(
        BigInteger, ForeignKey("DispBase.id", ondelete="CASCADE"), nullable=False
    )
    disp = relationship(DispBase, backref="liveDbLinks")

    # # comment="The attribute of the disp item to update"
    # dispTableName = Column(String, nullable=False)

    # comment="The attribute of the disp item to update"
    dispAttrName = Column(String, nullable=False)

    liveDbKey = Column(String, nullable=False)

    importKeyHash = Column(String)

    importGroupHash = Column(String)

    importDispHash = Column(String)

    # Store custom props for this link
    propsJson = Column(String)

    __table_args__ = (
        Index(
            "idx_LiveDbDLink_DispKeyHash",
            importKeyHash,
            importDispHash,
            dispAttrName,
            unique=False,
        ),
        Index("idx_LiveDbDLink_importGroupHash", importGroupHash, unique=False),
        Index("idx_LiveDbDLink_coordSetId", coordSetId, unique=False),
        Index("idx_LiveDbDLink_dispId", dispId, unique=False),
        Index("idx_LiveDbDLink_dispId_attr", dispId, dispAttrName, unique=True),
        Index("idx_LiveDbDLink_liveKeyId", liveDbKey, unique=False),
        # Designed for faster querying, it only needs to hit the index
        Index("idx_LiveDbDLink_liveDbUpdate", dispId, liveDbKey, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self, **kwargs):

        for name in self.__fieldNames__:
            if name in kwargs:
                setattr(self, name, kwargs.pop(name))

        assert not kwargs, "LiveDbDispLink.__init__, %s remains" % kwargs
