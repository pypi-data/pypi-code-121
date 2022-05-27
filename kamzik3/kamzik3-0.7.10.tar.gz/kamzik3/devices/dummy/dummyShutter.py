from kamzik3.constants import *
from kamzik3.devices.general.deviceShutter import DeviceShutter
from kamzik3.snippets.snippetsDecorators import expose_method


class DummyShutter(DeviceShutter):
    """
    Implementation of Dummy Shutter, used for testing.
    """

    def _open_shutter(self):
        self.set_status(STATUS_IDLE)
        self.clear_open_delay()
        self.set_value(ATTR_OPENED, True)
        self.set_value(ATTR_OPENED_AT, 100)

    def _close_shutter(self):
        self.clear_close_delay()
        self.set_status(STATUS_IDLE)
        self.set_value(ATTR_OPENED, False)
        self.set_value(ATTR_OPENED_AT, 0)

    @expose_method()
    def is_opened(self):
        return self.get_value(ATTR_OPENED)
