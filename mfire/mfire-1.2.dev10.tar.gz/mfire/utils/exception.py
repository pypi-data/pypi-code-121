"""
@package utils.exception

Module with custom excpetion and for handling exception in multiprocessing
"""

from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_processor")


class PrometheeError(Exception):
    """Base class promethee's custom exception"""

    def __init__(self, err, **kwargs):
        self.err = err
        for key, value in kwargs.items():
            if value is None:
                continue
            try:
                self.err += " {}={}.".format(key, value)
            except Exception:
                LOGGER.exception(
                    "Exception caught in PrometheeError execution", exc_info=True,
                )
        super().__init__(self.err)


class ConfigurationError(PrometheeError):
    """Raised when a wrong configuration has been given"""

    def __init__(self, err, **kwargs):
        super().__init__(err, **kwargs)
