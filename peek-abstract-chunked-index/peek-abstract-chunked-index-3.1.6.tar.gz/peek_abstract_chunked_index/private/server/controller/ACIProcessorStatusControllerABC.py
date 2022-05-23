from abc import ABCMeta
from datetime import datetime

import pytz
from twisted.internet import reactor
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


class ACIProcessorStatusControllerABC(metaclass=ABCMeta):
    _StateTuple = None
    NOTIFY_PERIOD = 2.0

    def __init__(self):
        self.status = self._StateTuple()
        self._tupleObservable = None
        self._notifyPending = False
        self._lastNotifyDatetime = datetime.now(pytz.utc)

    def setTupleObservable(self, tupleObservable: TupleDataObservableHandler):
        self._tupleObservable = tupleObservable

    def shutdown(self):
        self._tupleObservable = None

    # ---------------
    # Search Object Processor Methods

    # ---------------
    # Notify Methods

    def notify(self):
        if self._notifyPending:
            return

        self._notifyPending = True

        deltaSeconds = (datetime.now(pytz.utc) - self._lastNotifyDatetime).seconds
        if deltaSeconds >= self.NOTIFY_PERIOD:
            self._sendNotify()
        else:
            reactor.callLater(self.NOTIFY_PERIOD - deltaSeconds, self._sendNotify)

    def _sendNotify(self):
        self._notifyPending = False
        self._lastNotifyDatetime = datetime.now(pytz.utc)
        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(self._StateTuple.tupleType(), {})
        )
