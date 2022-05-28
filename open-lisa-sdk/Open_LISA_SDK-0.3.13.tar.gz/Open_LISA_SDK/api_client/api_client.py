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
    # Discover server RS232
    MAX_COM_TO_TRY = 10
    TIMEOUT_TO_WAIT_HANDSHAKE_RESPONSE = 3
    RS232_HANDSHAKE_CLIENT_REQUEST = 'OPEN'
    RS232_HANDSHAKE_SERVER_RESPONSE = 'LISA'

    connection = None
    for i in range(1, MAX_COM_TO_TRY):
      try:
        endpoint = "COM{}".format(i)
        connection = serial.Serial(port=endpoint, baudrate=baudrate, timeout=TIMEOUT_TO_WAIT_HANDSHAKE_RESPONSE)
        MAX_UNSIGNED_INT = 4_294_967_295
        connection.set_buffer_size(rx_size = MAX_UNSIGNED_INT, tx_size = MAX_UNSIGNED_INT)
        if not connection.isOpen():
          connection.open()

        # custom handshake
        connection.write(RS232_HANDSHAKE_CLIENT_REQUEST.encode())
        response = connection.read(len(RS232_HANDSHAKE_SERVER_RESPONSE))
        if len(response) > 0 and str(response.decode()) == RS232_HANDSHAKE_SERVER_RESPONSE:
          log.debug('Detect Open LISA server at {} with baudrate {}'.format(endpoint, baudrate))
          break
        else:
          connection = None
          log.debug("no answer detected from {}".format(endpoint))
      except serial.SerialException as ex:
        log.info('serial exception {}'.format(ex))
        log.debug("could not connect to {}".format(endpoint))
        connection = None

    if not connection:
      raise CouldNotConnectToServerException("could not detect Open LISA server listening through RS232")

    self._client_protocol = ClientProtocol(MessageProtocolRS232(rs232_connection=connection))

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