import socket
import serial
from ..domain.exceptions.could_not_connect_to_server import CouldNotConnectToServerException
from ..domain.instruments.instrument import Instrument
from ..domain.protocol.client_protocol import ClientProtocol
from ..logging import log
from ..common.protocol.message_protocol_tcp import MessageProtocolTCP
from ..common.protocol.message_protocol_rs232 import MessageProtocolRS232

class ApiClient:
  def __init__(self, default_string_response_conversion, default_bytearray_response_conversion):
    self._default_string_response_conversion = default_string_response_conversion
    self._default_bytearray_response_conversion = default_bytearray_response_conversion

  def connect_through_TCP(self, host, port):
    try:
      server_address = (host, port)
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect(server_address)
      self._client_protocol = ClientProtocol(MessageProtocolTCP(sock))
      self._socket_connection = sock
    except Exception as e:
      log.error(e)
      raise CouldNotConnectToServerException("could not connect with server at {} through TCP".format(server_address))

  def connect_through_RS232(self, baudrate):
    self._client_protocol = ClientProtocol(MessageProtocolRS232(baudrate=baudrate))

  def disconnect(self):
    if (self._socket_connection):
      try:
        self._socket_connection.shutdown(socket.SHUT_RDWR)
      except (socket.error, OSError, ValueError):
        pass
      self._socket_connection.close()


  def get_instruments(self):
    d = self._client_protocol.get_instruments()
    return [Instrument.from_dict(i, self._client_protocol, self._default_string_response_conversion, self._default_bytearray_response_conversion) for i in d]