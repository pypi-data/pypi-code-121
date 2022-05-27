from functools import partial
import time
from typing import Dict, List, Optional

from kamzik3.constants import STATUS_CONFIGURED
from kamzik3.devices.dummy.deviceDummy import DeviceDummy


def dummy_func(logger, method_name, *args):
    """Placeholder for Device methods."""
    logger.info(f"Dummy '{method_name}', received arguments: {args}")


class DummyTangoDevice(DeviceDummy):
    """
    Implementation of a dummy Tango device.

    :param attributes: dictionary of attribute_name: (default_value, unit) key-value
     pairs
    :param methods: list of methods, to be mocked using dummy_func
    :param device_id: str, the device name
    :param config: dict, the optional configuration of the device
    """

    def __init__(
        self,
        attributes: Optional[Dict[str, List]] = None,
        methods: Optional[List] = None,
        device_id: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        if attributes is not None and not isinstance(attributes, dict):
            raise TypeError(
                f"attributes should be a dictionary, got {type(attributes)}"
            )
        self._attributes = attributes
        if methods is not None and not isinstance(methods, list):
            raise TypeError(f"methods should be a list, got {type(methods)}")
        self._methods = methods
        DeviceDummy.__init__(self, device_id=device_id, config=config)

    def _config_methods(self):
        """Create the dummy methods."""
        if self._methods is not None:
            for method_name in self._methods:
                setattr(
                    self, method_name, partial(dummy_func, self.logger, method_name)
                )

    def _init_attributes(self):
        DeviceDummy._init_attributes(self)
        if self._attributes is not None:
            for attr_name, (value, unit) in self._attributes.items():
                self.create_attribute(attr_name, default_value=value, unit=unit)

    def handle_configuration(self):
        start_at = time.time()
        self._config_attributes()
        self._config_methods()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )
