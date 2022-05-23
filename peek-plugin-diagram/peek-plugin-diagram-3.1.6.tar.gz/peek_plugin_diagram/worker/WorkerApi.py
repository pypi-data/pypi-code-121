from typing import List

from peek_plugin_livedb.tuples.LiveDbDisplayValueTuple import LiveDbDisplayValueTuple


class WorkerApi:
    """Worker Api

    This class allows other classes to work with the LiveDB plugin on the
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
        """Convert Live DB Display Values

        Return an array of items representing the display values from the LiveDB.

        :param liveDbRawValues:
        :param ormSession: The SQLAlchemy orm session from the calling code.
        :param modelSetKey: The name of the model set to get the keys for

        :returns: The input list with populated display values.
        """
        from peek_plugin_diagram._private.worker.api.WorkerApiImpl import WorkerApiImpl

        WorkerApiImpl.updateLiveDbDisplayValues(
            ormSession, modelSetKey, liveDbRawValues
        )

    @classmethod
    def liveDbDisplayValueUpdateNotify(
        cls, ormSession, modelSetKey: str, updatedKeys: List[str]
    ) -> None:
        """LiveDB Display Value Update Notify

        This method is called by the LiveDB when the LiveDB display values update.
        This API support is the worker because the LiveDB updates are applied
        in the worker as well.

        THIS METHOD DOES NOT COMMIT THE TRANSACTION.

        :param ormSession: The SQLAlchemy orm session from the calling code.
        :param modelSetKey: The name of the model set to get the keys for
        :param updatedKeys: An array of LiveDb item keys that have been updated

        :returns: None
        """
        from peek_plugin_diagram._private.worker.api.WorkerApiImpl import WorkerApiImpl

        return WorkerApiImpl.liveDbDisplayValueUpdateNotify(
            ormSession, modelSetKey, updatedKeys
        )
