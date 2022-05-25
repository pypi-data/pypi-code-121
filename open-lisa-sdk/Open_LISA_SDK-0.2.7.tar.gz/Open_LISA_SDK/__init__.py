from .domain.exceptions.instrument_not_found import InstrumentNotFoundException
from .logging import log
from .api_client.api_client import ApiClient


class SDK:
    def __init__(self, host, port, log_level="WARNING", default_string_response_conversion="double", default_bytearray_response_conversion="bytes"):
        log.set_level(log_level)
        log.info("Initializating SDK")
        self._client = ApiClient(host, int(port), str(default_string_response_conversion), str(default_bytearray_response_conversion))

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
