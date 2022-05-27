from ctypes import CDLL

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device


class DeviceOsLibrary(Device):
    def __init__(self, os_library, device_id=None, config=None):
        if not hasattr(self, "os_library"):
            self.os_library = os_library
        if not hasattr(self, "library"):
            self.library = None
        super().__init__(device_id, config)
        self.connect()

    # Is abstract in Device and must be overridden
    def handle_configuration(self) -> None:
        pass

    def _init_attributes(self):
        Device._init_attributes(self)
        self.create_attribute(
            ATTR_LIBRARY, default_value=self.os_library, readonly=True
        )

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...

        :param args: connect attributes
        """
        self.connecting = True
        self.handle_configuration_event()
        if self.library is None:
            try:
                self.library = CDLL(self.os_library)
            except OSError as e:
                raise DeviceError(
                    "Error loading library {}. {}".format(self.os_library, e)
                )
        self.connected = True
        self.connecting = False
        self.set_status(STATUS_IDLE)
