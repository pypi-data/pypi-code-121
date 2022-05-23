import logging
from datetime import datetime
from typing import List
from typing import Optional

from rx import Observable
from rx.subjects import Subject
from sqlalchemy.orm.exc import NoResultFound
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import noMainThread

from peek_core_device._private.server.controller.MainController import MainController
from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.storage.GpsLocationTable import GpsLocationTable
from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_device.tuples.DeviceDetailTuple import DeviceDetailTuple
from peek_core_device.tuples.DeviceGpsLocationTuple import DeviceGpsLocationTuple
from peek_core_device.tuples.DeviceStatusTuple import DeviceStatusTuple

logger = logging.getLogger(__name__)


class DeviceApi(DeviceApiABC):
    def __init__(self, mainController: MainController, ormSessionCreator):
        self._mainController = mainController
        self._ormSessionCreator = ormSessionCreator

        self._deviceOnlineSubject = Subject()
        self._deviceGpsLocationSubject = Subject()

    def shutdown(self):
        pass

    @deferToThreadWrapWithLogger(logger)
    def deviceDetails(self, deviceTokens: List[str]) -> Deferred:
        ormSession = self._ormSessionCreator()
        try:
            all = (
                ormSession.query(DeviceInfoTable)
                .filter(DeviceInfoTable.deviceToken.in_(deviceTokens))
                .all()
            )

            tuples = [
                DeviceDetailTuple(
                    deviceToken=d.deviceToken,
                    deviceType=d.deviceType,
                    description=d.description,
                    lastOnline=d.lastOnline,
                    deviceStatus=d.deviceStatus,
                )
                for d in all
            ]

            return tuples

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def deviceDescription(self, deviceToken: str) -> Deferred:
        return self.deviceDescriptionBlocking(deviceToken)

    def deviceDescriptionBlocking(self, deviceToken: str) -> Optional[str]:
        noMainThread()

        ormSession = self._ormSessionCreator()
        try:
            all = (
                ormSession.query(DeviceInfoTable)
                .filter(DeviceInfoTable.deviceToken == deviceToken)
                .all()
            )

            if not all:
                return None

            return all[0].description

        finally:
            ormSession.close()

    def deviceOnlineStatus(self) -> Observable:
        return self._deviceOnlineSubject

    def notifyOfOnlineStatus(self, deviceId: str, deviceToken: str, status: bool):
        self._deviceOnlineSubject.on_next(
            DeviceStatusTuple(
                deviceToken=deviceToken, deviceId=deviceId, deviceStatus=status
            )
        )

    def deviceCurrentGpsLocation(self) -> Observable:
        return self._deviceGpsLocationSubject

    def notifyCurrentGpsLocation(
        self,
        deviceToken: str,
        latitude: float,
        longitude: float,
        datetime: datetime,
    ):
        self._deviceGpsLocationSubject.on_next(
            DeviceGpsLocationTuple(
                deviceToken=deviceToken,
                latitude=latitude,
                longitude=longitude,
                datetime=datetime,
            )
        )

    @deferToThreadWrapWithLogger(logger)
    def deviceCurrentGpsLocations(
        self, deviceTokens: List[str]
    ) -> List[DeviceGpsLocationTuple]:
        session = self._ormSessionCreator()
        try:
            query = session.query(GpsLocationTable).filter(
                GpsLocationTable.deviceToken.in_(deviceTokens)
            )
            return [d.toTuple() for d in query.all()]
        except NoResultFound:
            return []
        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def deviceTokens(self):
        ormSession = self._ormSessionCreator()
        query = ormSession.query(DeviceInfoTable)
        return [device.deviceToken for device in query.all()]
