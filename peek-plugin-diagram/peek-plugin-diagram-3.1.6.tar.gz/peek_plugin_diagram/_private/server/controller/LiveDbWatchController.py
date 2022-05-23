import logging
from typing import List

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_base.storage.StorageUtil import makeOrmValuesSubqueryCondition
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndex
from peek_plugin_diagram._private.storage.LiveDbDispLink import LiveDbDispLink
from peek_plugin_livedb.server.LiveDBReadApiABC import LiveDBReadApiABC
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC

logger = logging.getLogger(__name__)


class LiveDbWatchController:
    """Watch Grid Controller

    This controller handles most of the interactions with the LiveDB plugin..

    That is :

    1) Informing the LiveDB that the keys are being watched

    2) Sending updates for these watched grids to the clients (???? is this the right spot?)

    3) Computing display values for the live db

    4) Queueing display updates to be compiled, based on events from the livedb.

    """

    def __init__(
        self,
        liveDbWriteApi: LiveDBWriteApiABC,
        liveDbReadApi: LiveDBReadApiABC,
        dbSessionCreator,
    ):
        self._liveDbWriteApi = liveDbWriteApi
        self._liveDbReadApi = liveDbReadApi
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass

    @inlineCallbacks
    def updateClientWatchedGrids(self, clientId: str, gridKeys: List[str]) -> Deferred:
        """Update Client Watched Grids

        Tell the server that these grids are currently being watched by users.

        :param clientId: A unique identifier of the client (Maybe it's vortex uuid)
        :param gridKeys: A list of grid keys that this client is observing.
        :returns: Nothing
        """

        try:
            liveDbKeys = yield self.getLiveDbKeys(gridKeys)
            self._liveDbWriteApi.prioritiseLiveDbValueAcquisition(
                "pofDiagram", liveDbKeys
            )

        except Exception as e:
            logger.exception(e)

    @deferToThreadWrapWithLogger(logger)
    def getLiveDbKeys(self, gridKeys) -> List[str]:

        session = self._dbSessionCreator()
        try:
            return [
                t[0]
                for t in session.query(LiveDbDispLink.liveDbKey)
                .join(GridKeyIndex, GridKeyIndex.dispId == LiveDbDispLink.dispId)
                .filter(
                    makeOrmValuesSubqueryCondition(
                        session, GridKeyIndex.gridKey, gridKeys
                    )
                )
                .yield_per(1000)
                .distinct()
            ]
        finally:
            session.close()
