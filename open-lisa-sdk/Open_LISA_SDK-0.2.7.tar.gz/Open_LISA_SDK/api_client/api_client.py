import socket
from ..domain.exceptions.could_not_connect_to_server import CouldNotConnectToServerException
from ..domain.instruments.instrument import Instrument
from ..domain.protocol.client_protocol import ClientProtocol
from ..logging import log

class ApiClient:
  def __init__(self, host, port, default_string_response_conversion, default_bytearray_response_conversion):
    try:
      server_address = (host, port)
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect(server_address)
      self._client_protocol = ClientProtocol(sock)
      self._connection = sock
      self._default_string_response_conversion = default_string_response_conversion
      self._default_bytearray_response_conversion = default_bytearray_response_conversion
    except Exception as e:
      log.error(e)
      raise CouldNotConnectToServerException("could not connect with server at {}".format(server_address))

  def disconnect(self):
    try:
      self._connection.shutdown(socket.SHUT_RDWR)
    except (socket.error, OSError, ValueError):
      pass
    self._connection.close()


  def get_instruments(self):
    d = self._client_protocol.get_instruments()
    return [Instrument.from_dict(i, self._client_protocol, self._default_string_response_conversion, self._default_bytearray_response_conversion) for i in d]