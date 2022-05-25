from .sdk_exception import OpenLISAException

DEFAULT_MESSAGE = "instrument not exists"


class InstrumentNotFoundException(OpenLISAException):
    """
    Raised when the requested instrument not exists
  """

    def __init__(self, message=DEFAULT_MESSAGE):
        self.message = message
        super().__init__(self.message)
