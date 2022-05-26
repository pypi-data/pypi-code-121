import logging
import weakref
from enum import IntEnum
from functools import partial

try:
    from pythonfmu import Fmi2Status
except ImportError:

    class Fmi2Status(IntEnum):
        ok = 0
        warning = 1
        discard = 2
        error = 3
        fatal = 4


class FMUForwardHandler(logging.Handler):
    """Logging handler to forward Python log message to FMU logger.
    
    Attributes
    ----------
    _fmu : ReferenceType[pythonfmu.Fmi2Slave]
        FMU

    Parameters
    ----------
    fmu : pythonfmu.Fmi2Slave
        FMU to redirect log messages to
    """

    def __init__(self, fmu: "pythonfmu.Fmi2Slave", *args, **kwargs):
        super().__init__(*args, **kwargs)
        callback = partial(FMUForwardHandler.remove_handler, weakref.ref(self))
        self._fmu = weakref.ref(fmu, callback)

    @classmethod
    def add_handler(cls, fmu: "pythonfmu.Fmi2Slave", level: int) -> "FMUForwardHandler":
        """Add a new instance of this handler to the root logger.
        
        Parameters
        ----------
        fmu : pythonfmu.Fmi2Slave
            FMU

        Returns
        -------
        FMUForwardHandler
            The added handler
        """
        root_logger = logging.getLogger()
        if root_logger.level > level:
            root_logger.setLevel(level)
        handler = cls(fmu, level=level)
        root_logger.addHandler(handler)
        return handler

    @classmethod
    def remove_handler(
        cls, 
        handler: "ReferenceType[FMUForwardHandler]", 
        fmu: "Optional[ReferenceType[pythonfmu.Fmi2Slave]]" = None
    ) -> None:
        """Remove the instance of the provided handler on the
        root logger.
        
        Parameters
        ----------
        handler : weakref.ReferenceType[FMUForwardHandler]
            Weakreference object to the handler to be removed
        fmu : weakref.ReferenceType[pythonfmu.Fmi2Slave] or None
            Weakreference object to the FMU; default None
        """
        if handler() is not None:
            root_logger = logging.getLogger()
            root_logger.removeHandler(handler())

    @staticmethod
    def logging2FmiLevel(levelno: int) -> "pythonfmu.Fmi2Status":
        """Convert a Python log level to FMI 2 status.
        
        Parameters
        ----------
        levelno : int
            Python log level

        Returns
        -------
        pythonfmu.Fmi2Status
            FMI 2 status
        """
        if levelno >= logging.CRITICAL:
            return Fmi2Status.fatal
        elif levelno >= logging.ERROR:
            return Fmi2Status.error
        elif levelno >= logging.WARNING:
            return Fmi2Status.warning
        else:
            return Fmi2Status.ok

    def emit(self, record: "logging.LogRecord") -> None:
        """Forward a record to the FMU logger.
        
        Parameters
        ----------
        record : logging.LogRecord
            A log record
        """
        if self._fmu() is not None:
            self._fmu().log(
                record.getMessage(),
                FMUForwardHandler.logging2FmiLevel(record.levelno),
                debug=(record.levelno <= logging.DEBUG),
            )
