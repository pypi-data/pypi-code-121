from time import time
from .domain.exceptions.instrument_not_found import InstrumentNotFoundException
from .logging import log
from .api_client.api_client import ApiClient

DEFAULT_RS232_BAUDRATE = 460800
class SDK:
    def __init__(self, log_level="WARNING", default_string_response_conversion="double", default_bytearray_response_conversion="bytes"):
        log.set_level(log_level)
        log.info("Initializating SDK")
        self._client = ApiClient(str(default_string_response_conversion), str(default_bytearray_response_conversion))

    def connect_through_TCP(self, host, port):
        self._client.connect_through_TCP(host, int(port))

    def connect_through_RS232(self, baudrate=DEFAULT_RS232_BAUDRATE):
        self._client.connect_through_RS232(baudrate)

    def disconnect(self):
        self._client.disconnect()

    def list_instruments(self):
        """
        Returns the list of Instrument objects that are connected and identified by the server
        """
        return self._client.get_instruments()

    def get_instrument(self, id):
        """
        Returns a Instrument object that are connected and identified by the server
        """
        instruments = self.list_instruments()
        for i in instruments:
            if i.ID == id:
                return i

        raise InstrumentNotFoundException
