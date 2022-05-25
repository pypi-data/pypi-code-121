from .sdk_exception import OpenLISAException

DEFAULT_MESSAGE = "could not connect with server"

class CouldNotConnectToServerException(OpenLISAException):
  """
    Raised when the SDK is initiated and connection with server could not be established
  """
  def __init__(self, message=DEFAULT_MESSAGE):
    self.message = message
    super().__init__(self.message)