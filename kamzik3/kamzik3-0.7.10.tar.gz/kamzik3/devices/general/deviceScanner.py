import time
from typing import Optional, List

from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceScanner(Device):
    last_scan_count = None
    class_filter = None
    attribute_filter: Optional[List[str]] = None
    method_filter = None

    def __init__(self, device_id=None, config=None):
        Device.__init__(self, device_id, config)
        self.connect()

    def handle_configuration(self):
        start_at = time.time()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    @expose_method()
    def get_scanner_attributes(self):
        raise NotImplementedError

    @expose_method()
    def get_scanner_macro(self, scanner_input, scanner_attributes, parent_macro=None):
        raise NotImplementedError
