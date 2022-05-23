from unittest.mock import Mock

__author__ = "Sebastian Stigler"
__copyright__ = "Copyright 2022, Sebastian Stigler"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.4"
__maintainer__ = "Sebastian Stigler"
__email__ = "sebastian.stigler@hs-aalen.de"
__status__ = "Production"

AP_IF = 0
STA_IF = 1


class WLAN(Mock):
    def __init__(self, inteface_id):
        super().__init__()
        self._interface_id = inteface_id
        self._active = False
        self._ssid = ""
        self._password = ""
        self._bssid = ""
        self._isconnected = False

    def active(self, state):
        self._active = state

    def connect(self, ssid=None, password=None, *, bssid=None):
        self._ssid = ssid
        self._password = password
        self._bssid = bssid

    def isconnected(self):
        if not self._isconnected:
            self._isconnected = True
            return False
        return self._isconnected

    def ifconfig(isgd=None):
        return ("192.168.0.4", "255.255.255.0", "192.168.0.1", "8.8.8.8")
