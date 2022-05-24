#===============================================================================
# PSCAD Message Handlers
#===============================================================================

"""PSCAD Message Handlers"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging, time


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Abstract Handler
#===============================================================================

class AbstractHandler:
    """
    Base class for subscription event handlers
    """

    def __init__(self):
        self._elapsed_start = time.perf_counter()

    @property
    def elapsed(self) -> float:
        """
        Elapsed time since handler was created
        """
        return time.perf_counter() - self._elapsed_start

    def send(self, _msg) -> bool: # pylint: disable=no-self-use
        """
        Called when a event message is received, to process the message
        """
        return False

    def close(self) -> None:
        """
        Generator close function - for treating instance as a generator
        """


#===============================================================================
# BuildEvent
#===============================================================================

class BuildEvent(AbstractHandler):
    """
    Base class for build-event handlers
    """

    def __init__(self):
        super().__init__()
        self._level = 0

    def send(self, msg) -> bool:
        handled = False

        if msg is not None:
            phase = msg.pop('name')
            status = msg.pop('status')
            project = msg.pop('project', None)
            elapsed = self.elapsed
            handled = self._build_event(phase, status, project, elapsed, **msg)

            if status == 'BEGIN':
                self._level += 1
            elif status == 'END':
                self._level -= 1
                if self._level == 0:
                    raise StopIteration

        return handled

    def _build_event(self, phase: str, status: str, project: str, # pylint: disable=unused-argument, no-self-use
                     elapsed: float, **kwargs) -> bool:

        LOG.debug("BuildEvt: [%s] %s/%s %.3f", project, phase, status, elapsed)
        return False
