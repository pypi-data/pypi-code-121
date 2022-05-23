import logging
from datetime import datetime

from vortex.DeferUtil import callMethodLater
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.storage.DeviceUpdateTuple import \
    DeviceUpdateTuple
from peek_core_device.tuples.DeviceInfoTuple import DeviceInfoTuple

logger = logging.getLogger(__name__)


class NotifierController:
    def __init__(self, tupleObservable: TupleDataObservableHandler):
        self._tupleObservable = tupleObservable

        from peek_core_device._private.server.DeviceApi import DeviceApi

        self._api: DeviceApi = None

    def setApi(self, api):
        self._api = api

    def shutdown(self):
        self._tupleObservable = None
        self._api = None

    @callMethodLater
    def notifyDeviceInfo(self, deviceId: str):
        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceInfoTuple.tupleName(), dict(deviceId=deviceId))
        )

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceInfoTuple.tupleName(), dict())
        )

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceInfoTable.tupleName(), dict())
        )

    @callMethodLater
    def notifyDeviceUpdate(self, deviceType: str):
        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceUpdateTuple.tupleName(),
                dict(deviceType=deviceType))
        )

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceUpdateTuple.tupleName(), dict())
        )

    @callMethodLater
    def notifyDeviceOnline(self, deviceId: str, deviceToken: str, online: bool):
        """Notify Device Online

        Notify that the device has changed it's online status

        """
        self._api.notifyOfOnlineStatus(deviceId, deviceToken, online)

    @callMethodLater
    def notifyDeviceGpsLocation(
        self,
        deviceToken: str,
        latitude: float,
        longitude: float,
        updatedDate: datetime,
    ):
        self._api.notifyCurrentGpsLocation(
            deviceToken,
            latitude,
            longitude,
            updatedDate,
        )
