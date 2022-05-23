from unittest.mock import Mock

__author__ = "Sebastian Stigler"
__copyright__ = "Copyright 2022, Sebastian Stigler"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.4"
__maintainer__ = "Sebastian Stigler"
__email__ = "sebastian.stigler@hs-aalen.de"
__status__ = "Production"

disable_irq = Mock(return_value="disable_irq")
enable_irq = Mock()
idle = Mock()


class Pin(Mock):
    IN = 0
    OUT = 1
    OPEN_DRAIN = 2
    PULL_NONE = 0
    PULL_UP = 1

    def __init__(self, id, mode=-1, pull=-1):
        super().__init__()
        self.id = id
        self._mode = mode
        self._pull = pull
        self._value = 1

    def init(self, mode=-1, pull=-1):
        self._mode = mode
        self._pull = pull

    def value(self, x=None):
        if x is None:
            return self._value
        self._value = x

    def on(self):
        self._value = 1

    def off(self):
        self.value = 0

    def irq(self, *args, **kwargs):
        pass


I2C = Mock()


class Timer(Mock):
    ONE_SHOT = 0
    PERIODIC = 1

    def __init__(self, id):
        super().__init__()
        self.id = id
        self._mode = -1
        self._period = -2
        self._callback = None

    def init(self, *, mode=1, period=-1, callback=None):
        self._mode = mode
        self._period = period
        self._callback = callback

    def deinit():
        pass
