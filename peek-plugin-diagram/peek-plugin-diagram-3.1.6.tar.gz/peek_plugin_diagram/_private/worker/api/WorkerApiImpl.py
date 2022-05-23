import logging
from datetime import datetime
from typing import List

import pytz
from sqlalchemy import select, and_

from peek_plugin_diagram._private.storage.DispIndex import DispIndexerQueue
from peek_plugin_diagram._private.storage.LiveDbDispLink import LiveDbDispLink
from peek_plugin_diagram._private.storage.ModelSet import ModelSet, ModelCoordSet
from peek_plugin_diagram._private.worker.tasks.LiveDbDisplayValueConverter import (
    LiveDbDisplayValueConverter,
)
from peek_plugin_livedb.tuples.LiveDbDisplayValueTuple import LiveDbDisplayValueTuple

logger = logging.getLogger(__name__)


class WorkerApiImpl:
    """Worker Api

    This class allows other classes to work with the Diagram plugin on the
    worker service.

    """

    _FETCH_SIZE = 5000

    @classmethod
    def updateLiveDbDisplayValues(
        cls,
        ormSession,
        modelSetKey: str,
        liveDbRawValues: List[LiveDbDisplayValueTuple],
    ) -> None:
        if not liveDbRawValues:
            return

        startTime = datetime.now(pytz.utc)

        modelSetId = (
            ormSession.query(ModelSet.id).filter(ModelSet.key == modelSetKey).one().id
        )

        translater = LiveDbDisplayValueConverter.create(ormSession, modelSetId)

        for item in liveDbRawValues:
            if item.dataType is None:
                logger.warning("LiveDB key %s is missing dataType", item.key)
                continue

            item.displayValue = translater.translate(item.dataType, item.rawValue)

        logger.debug(
            "Converted %s LiveDB Raw Values in %s",
            len(liveDbRawValues),
            (datetime.now(pytz.utc) - startTime),
        )

    @classmethod
    def liveDbDisplayValueUpdateNotify(
        cls, ormSession, modelSetKey: str, updatedKeys: List[str]
    ):

        logger.debug("TODO TODO - liveDbDisplayValueUpdateNotify coordSetId")
        linkTable = LiveDbDispLink.__table__
        coordSetTable = ModelCoordSet.__table__
        queueTable = DispIndexerQueue.__table__

        modelSetId = (
            ormSession.query(ModelSet.id).filter(ModelSet.key == modelSetKey).one().id
        )

        stmt = (
            select([linkTable.c.dispId])
            .select_from(
                linkTable.join(
                    coordSetTable, linkTable.c.coordSetId == coordSetTable.c.id
                )
            )
            .where(
                and_(
                    linkTable.c.liveDbKey.in_(updatedKeys),
                    coordSetTable.c.modelSetId == modelSetId,
                )
            )
        )

        ins = queueTable.insert().from_select(["dispId"], stmt)
        ormSession.execute(ins)
