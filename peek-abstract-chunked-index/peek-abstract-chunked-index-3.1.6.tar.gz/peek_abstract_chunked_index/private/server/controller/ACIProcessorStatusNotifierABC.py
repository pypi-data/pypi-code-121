from abc import ABCMeta, abstractmethod


class ACIProcessorStatusNotifierABC(metaclass=ABCMeta):
    @abstractmethod
    def setProcessorStatus(self, state: bool, queueSize: int):
        """Set Processor Status

        Example Code:

            self._status.chunkedIndexProcessorProcessorStatus = state
            self._status.chunkedIndexProcessorQueueSize = queueSize
            self.notify()

        """

    @abstractmethod
    def addToProcessorTotal(self, delta: int):
        """Add To Processor Total

        Example Code:

            self._status.chunkedIndexProcessorQueueProcessedTotal += delta
            self.notify()

        """

    @abstractmethod
    def setProcessorError(self, error: str):
        """Set Processor Error

        Example Code:

            self._status.chunkedIndexProcessorQueueLastError = error
            self.notify()

        """


'''
class ACIProcessorStatusNotifier(ProcessorStatusNotifierABC):
    """ Queue Status Notifier

    This is an example class

    """

    def __init__(self, statusController: ChunkedIndexStatusControllerABC,
                 statusTuple: ChunkedIndexServerStatusTupleABC):
        self._statusController = statusController
        self._state = statusTuple

    @abstractmethod
    def setProcessorStatus(self, state: bool, queueSize: int):
        """ Set Processor Status

        """

        self._state.processorStatus = state
        self._state.queueSize = queueSize
        self._statusController.notify()

    @abstractmethod
    def addToProcessorTotal(self, delta: int):
        """ Add To Processor Total

        """

        self._state.queueProcessedTotal += delta
        self._statusController.notify()

    @abstractmethod
    def setProcessorError(self, error: str):
        """ Set Processor Error

        """

        self._state.queueLastError = error
        self._statusController.notify()
'''
