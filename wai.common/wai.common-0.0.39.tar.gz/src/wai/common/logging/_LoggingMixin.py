import logging


class LoggingMixin:
    """
    Mixin class for adding logging to objects.
    """
    @property
    def logger(self) -> logging.Logger:
        cls = type(self)
        return logging.getLogger(cls.__module__ + "." + cls.__name__)
