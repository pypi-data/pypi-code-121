import time

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device


class DeviceDummy(Device):
    """Here comes some description of the class DeviceDummy."""

    def __init__(self, device_id=None, config=None):
        Device.__init__(self, device_id, config)
        self.connect()

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library /...

        :param args: connect attributes
        """
        self.connecting = True
        self.connected = True
        self.handle_configuration_event()
        self.connecting = False
        self.set_status(STATUS_IDLE)

    def handle_configuration(self):
        start_at = time.time()
        self._config_attributes()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def command(self, command, callback=None, with_token=False, returning=True):
        raise DeviceError("Dummy device does not accept any commands.")

    def handshake(self):
        return True

    def start_polling(self):
        return

    def close(self):
        Device.close(self)
