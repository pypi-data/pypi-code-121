import logging
from typing import Union

from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.storage.GpsLocationTable import GpsLocationTable
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class DeviceInfoTableTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:

        deviceId = tupleSelector.selector.get("deviceId")

        ormSession = self._ormSessionCreator()
        try:
            query = ormSession.query(
                DeviceInfoTable, GpsLocationTable
            ).outerjoin(GpsLocationTable)

            if deviceId is not None:
                query = query.filter(DeviceInfoTable.deviceId == deviceId)

            # Add the current location to each DeviceInfo row
            tuples = []
            for deviceInfoTableRow, gpsLocationTableRow in query.all():
                deviceInfoTableRow.currentLocation = gpsLocationTableRow
                tuples.append(deviceInfoTableRow)

            # Create the vortex message
            return (
                Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()
            )

        finally:
            ormSession.close()
