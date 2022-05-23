import logging
from pathlib import Path

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_core_device._private.server.controller.EnrollmentController import (
    EnrollmentController,
)
from peek_core_device._private.server.controller.GpsController import GpsController
from peek_core_device._private.server.controller.NotifierController import (
    NotifierController,
)
from peek_core_device._private.server.controller.DeviceStatusController import (
    DeviceStatusController,
)
from peek_core_device._private.server.controller.UpdateController import (
    UpdateController,
)

logger = logging.getLogger(__name__)


class MainController(TupleActionProcessorDelegateABC):
    def __init__(
        self,
        dbSessionCreator,
        notifierController: NotifierController,
        deviceUpdateFilePath: Path,
        tupleObservable: TupleDataObservableHandler,
    ):
        self._dbSessionCreator = dbSessionCreator
        self._notifierController = notifierController

        self._enrollmentController = EnrollmentController(
            dbSessionCreator, notifierController
        )

        self._onlineController = DeviceStatusController(
            dbSessionCreator, notifierController
        )

        self._updateController = UpdateController(
            dbSessionCreator, notifierController, deviceUpdateFilePath
        )

        self._gpsController = GpsController(
            dbSessionCreator=dbSessionCreator,
            tupleObservable=tupleObservable,
            notifierController=notifierController,
        )

    @property
    def deviceUpdateController(self):
        return self._updateController

    def shutdown(self):
        self._enrollmentController.shutdown()
        self._onlineController.shutdown()
        self._updateController.shutdown()
        self._gpsController.shutdown()

    @inlineCallbacks
    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        result = yield self._enrollmentController.processTupleAction(tupleAction)
        if result is not None:
            return result

        result = yield self._onlineController.processTupleAction(tupleAction)
        if result is not None:
            return result

        result = yield self._updateController.processTupleAction(tupleAction)
        if result is not None:
            return result

        result = yield self._gpsController.processTupleAction(tupleAction)
        if result is not None:
            return result

        raise NotImplementedError(tupleAction.tupleName())
