from abc import ABCMeta, abstractmethod
import sys
from codefast.logger import Logger
import signal
import atexit
import traceback


class ProcessFramework(metaclass=ABCMeta):
    """ A framework for processing tasks. Capable of handling signal 
    interrupts in a safe manner.
    """

    def __init__(self):
        self._continue = True

    @abstractmethod
    def process(self):
        pass

    def safe_kill_handler(self, signum, frame):
        self._continue = False

    def run(self):
        @atexit.register
        def atexit_fun():
            exc_type, exc_value, exc_tb = sys.exc_info()
            s = traceback.format_exception(exc_type, exc_value, exc_tb)
            log = Logger()
            if exc_type:
                log.error(__name__ + ' exit:' + str(s))
            else:
                log.info(__name__ + ' exit:' + str(s))

        signal.signal(signal.SIGTERM, self.safe_kill_handler)
        signal.signal(signal.SIGINT, self.safe_kill_handler)
        signal.signal(signal.SIGHUP, self.safe_kill_handler)

        while self._continue:
            self.process()
