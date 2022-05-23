import logging
from typing import List

from sqlalchemy.orm.exc import NoResultFound
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Tuple import Tuple
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.server.controller.NotifierController import (
    NotifierController,
)
from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.tuples.DeviceBackgroundStateTupleAction import (
    DeviceBackgroundStateTupleAction,
)
from peek_core_device._private.tuples.UpdateDeviceOnlineAction import (
    UpdateDeviceOnlineAction,
)
from peek_core_device.tuples.DeviceInfoTuple import DeviceInfoTuple

logger = logging.getLogger(__name__)


class DeviceStatusController:
    def __init__(self, dbSessionCreator, notifierController: NotifierController):
        self._dbSessionCreator = dbSessionCreator
        self._notifierController = notifierController

        self._setAllDevicesOfflineBlocking()

    def shutdown(self):
        pass

    def processTupleAction(self, tupleAction: TupleActionABC) -> List[Tuple]:
        if isinstance(tupleAction, UpdateDeviceOnlineAction):
            return self._processUpdateOnline(tupleAction)

        if isinstance(tupleAction, DeviceBackgroundStateTupleAction):
            return self._processUpdateBackgrounded(tupleAction)

    @deferToThreadWrapWithLogger(logger)
    def _processUpdateBackgrounded(
        self, action: DeviceBackgroundStateTupleAction
    ) -> List[Tuple]:
        """Process Device Backgrounded Update

        :rtype: Deferred
        """
        session = self._dbSessionCreator()

        try:
            deviceInfo = (
                session.query(DeviceInfoTable)
                .filter(DeviceInfoTable.deviceId == action.deviceId)
                .one()
            )

            deviceId = deviceInfo.deviceId
            deviceInfo.lastOnline = action.dateTime

            if deviceInfo.deviceStatus & DeviceInfoTuple.DEVICE_ONLINE:
                deviceInfo.deviceStatus = DeviceInfoTuple.DEVICE_ONLINE
            else:
                deviceInfo.deviceStatus = DeviceInfoTuple.DEVICE_OFFLINE

            if action.deviceBackgrounded:
                deviceInfo.deviceStatus |= DeviceInfoTuple.DEVICE_BACKGROUND

            session.commit()

            self._notifierController.notifyDeviceInfo(deviceId=deviceId)
            self._notifierController.notifyDeviceOnline(
                deviceInfo.deviceId, deviceInfo.deviceToken, deviceInfo.deviceStatus
            )

            return []

        except NoResultFound:
            return []

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def _processUpdateOnline(self, action: UpdateDeviceOnlineAction) -> List[Tuple]:
        """Process Online Status Update

        :rtype: Deferred
        """
        session = self._dbSessionCreator()
        try:
            deviceInfo = (
                session.query(DeviceInfoTable)
                .filter(DeviceInfoTable.deviceId == action.deviceId)
                .one()
            )

            deviceId = deviceInfo.deviceId

            deviceInfo.lastOnline = action.dateTime
            deviceInfo.deviceStatus = action.deviceStatus

            session.commit()

            self._notifierController.notifyDeviceInfo(deviceId=deviceId)
            self._notifierController.notifyDeviceOnline(
                deviceInfo.deviceId, deviceInfo.deviceToken, deviceInfo.deviceStatus
            )

            return []

        except NoResultFound:
            return []

        finally:
            session.close()

    def _setAllDevicesOfflineBlocking(self):
        """Set All Devices to Offline"""
        session = self._dbSessionCreator()
        try:
            session.execute(
                DeviceInfoTable.__table__.update().values(
                    deviceStatus=DeviceInfoTuple.DEVICE_OFFLINE
                )
            )
            session.commit()

        finally:
            session.close()
