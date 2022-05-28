import serial
import struct
from .message_protocol import MessageProtocol
from ...logging import log
from ...domain.exceptions.could_not_connect_to_server import CouldNotConnectToServerException

# TODO: Duplicado en server y SDK, ver de usar uno en comun
class MessageProtocolRS232(MessageProtocol):
    # Constructor with RS232 connection for server side
    def __init__(self, rs232_connection):
        self._connection = rs232_connection
        if not self._connection.isOpen():
            self._connection.open()

    # Constructor with discover for client side
    def __init__(self, baudrate):
        MAX_COM_TO_TRY = 10
        TIMEOUT_TO_WAIT_HANDSHAKE_RESPONSE = 3
        RS232_HANDSHAKE_CLIENT_REQUEST = 'OPEN'
        RS232_HANDSHAKE_SERVER_RESPONSE = 'LISA'

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
                    log.debug('Detect Open LISA server at {}'.format(endpoint))
                    self._connection = connection
                    return
                else:
                    log.debug("no answer detected from {}".format(endpoint))
            except serial.SerialException:
                log.debug("could not connect to {}".format(endpoint))

        raise CouldNotConnectToServerException("could not detect Open LISA server listening through RS232")

    def __del__(self):
        self._connection.close()

    def send_msg(self, msg, encode=True):
        if encode:
            msg = msg.encode()
        # Prefix each message with a 4-byte length
        msg = struct.pack('>I', len(msg)) + msg
        self._connection.write(msg)

    def receive_msg(self, decode=True):
        # Read message length and unpack it into an integer
        raw_msglen = self.__recvall(4)
        if not raw_msglen:
            raise ConnectionResetError
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        data = self.__recvall(msglen)
        if decode:
            data = data.decode()
        return data

    def __recvall(self, n):
        # Helper function to recv n bytes or raise ConnectionResetError if EOF is hit
        data = bytearray()
        while len(data) < n:
            bytes_to_read = max(1, min(2048, self._connection.in_waiting, n))
            packet = self._connection.read(bytes_to_read)
            if not packet:
                raise ConnectionResetError
            data.extend(packet)
        return data