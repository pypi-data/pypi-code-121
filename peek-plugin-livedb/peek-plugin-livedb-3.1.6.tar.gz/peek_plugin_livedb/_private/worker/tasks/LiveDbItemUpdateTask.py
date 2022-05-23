import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

import pytz
from sqlalchemy.sql.expression import bindparam, and_, select
from txcelery.defer import DeferrableTask
from vortex.Payload import Payload

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_base.worker.CeleryApp import celeryApp
from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from peek_plugin_livedb._private.storage.LiveDbModelSet import LiveDbModelSet
from peek_plugin_livedb._private.storage.LiveDbRawValueQueue import LiveDbRawValueQueue
from peek_plugin_livedb.tuples.LiveDbDisplayValueTuple import LiveDbDisplayValueTuple

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def updateValues(self, payloadEncodedArgs: bytes) -> None:
    """Compile Grids Task

    :param self: A celery reference to this task
    :param payloadEncodedArgs: The updates from the queue controller
    :returns: None
    """
    startTime = datetime.now(pytz.utc)

    argData = Payload().fromEncodedPayload(payloadEncodedArgs).tuples
    allModelUpdates: List[LiveDbRawValueQueue] = argData[0]
    queueItemIds = argData[1]

    # Group the data by model set
    updatesByModelSetId = defaultdict(list)
    for update in allModelUpdates:
        updatesByModelSetId[update.modelSetId].append(update)

    ormSession = CeleryDbConn.getDbSession()
    try:

        for modelSetId, modelUpdates in updatesByModelSetId.items():
            _updateValuesForModelSet(modelSetId, modelUpdates, ormSession)

        # ---------------
        # delete the queue items
        dispQueueTable = LiveDbRawValueQueue.__table__
        ormSession.execute(dispQueueTable.delete(dispQueueTable.c.id.in_(queueItemIds)))

        ormSession.commit()

        # ---------------
        # Finally, tell log some statistics
        logger.info(
            "Updated %s raw values in %s",
            len(allModelUpdates),
            (datetime.now(pytz.utc) - startTime),
        )

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e, countdown=2)

    finally:
        ormSession.close()


def _updateValuesForModelSet(modelSetId, modelUpdates, ormSession):
    # Try to load the Diagram plugins API
    try:
        from peek_plugin_diagram.worker.WorkerApi import WorkerApi as DiagramWorkerApi
    except ImportError:
        logger.warning("Failed to load the diagram WorkerAPI")
        DiagramWorkerApi = None

    table = LiveDbItem.__table__

    # Load the Model Set
    liveDbModelSet = (
        ormSession.query(LiveDbModelSet).filter(LiveDbModelSet.id == modelSetId).one()
    )

    # Create a list of keys
    updatedKeys = [i.key for i in modelUpdates]

    # ---------------
    # Make a list of display items from the provided data
    displayItems = _makeDisplayValueTuples(
        liveDbModelSet, modelUpdates, ormSession, updatedKeys
    )

    # ---------------
    # Get the Diagram plugin to convert the live db values
    if DiagramWorkerApi:
        DiagramWorkerApi.updateLiveDbDisplayValues(
            ormSession, modelSetKey=liveDbModelSet.name, liveDbRawValues=displayItems
        )

    # ---------------
    # Update the the values in the tables
    sql = (
        table.update()
        .where(
            and_(
                table.c.key == bindparam("b_key"),
                table.c.modelSetId == liveDbModelSet.id,
            )
        )
        .values(
            {
                "rawValue": bindparam("b_rawValue"),
                "displayValue": bindparam("b_displayValue"),
            }
        )
    )

    ormSession.execute(
        sql,
        [
            dict(b_key=o.key, b_rawValue=o.rawValue, b_displayValue=o.displayValue)
            for o in displayItems
        ],
    )

    # ---------------
    # Tell the diagram plugin that livedb values have been updated
    if DiagramWorkerApi:
        DiagramWorkerApi.liveDbDisplayValueUpdateNotify(
            ormSession, modelSetKey=liveDbModelSet.key, updatedKeys=updatedKeys
        )


def _makeDisplayValueTuples(liveDbModelSet, modelUpdates, ormSession, updatedKeys):
    # Load the key typ lookups
    dataTypeLookup = _getLiveDbKeyDatatypeDict(
        ormSession, liveDbModelSet, liveDbKeys=updatedKeys
    )

    displayItems = []
    for update in modelUpdates:
        displayItems.append(
            LiveDbDisplayValueTuple(
                key=update.key,
                dataType=dataTypeLookup.get(update.key),
                rawValue=update.rawValue,
            )
        )

    return displayItems


def _getLiveDbKeyDatatypeDict(
    ormSession, liveDbModelSet: LiveDbModelSet, liveDbKeys: List[str]
) -> Dict[str, int]:
    """Get Live DB DataTypes

    Return an array of items representing the display values from the LiveDB.

    :param ormSession: The SQLAlchemy orm session from the calling code.
    :param liveDbModelSet: The name of the model set to get the keys for
    :param liveDbKeys: An array of LiveDb Keys.

    :returns: An array of tuples.
    """
    liveDbTable = LiveDbItem.__table__
    modelTable = LiveDbModelSet.__table__

    if not liveDbKeys:
        return {}

    liveDbKeys = list(set(liveDbKeys))  # Remove duplicates if any exist.
    stmt = (
        select([liveDbTable.c.key, liveDbTable.c.dataType])
        .select_from(
            liveDbTable.join(modelTable, liveDbTable.c.modelSetId == modelTable.c.id)
        )
        .where(modelTable.c.name == liveDbModelSet.name)
        .where(liveDbTable.c.key.in_(liveDbKeys))
    )

    resultSet = ormSession.execute(stmt)
    return dict(resultSet.fetchall())
